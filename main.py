from dotenv import load_dotenv
from prompts import CAPTION_CHARACTER, CAPTION_STYLE
from transformers import LlavaForConditionalGeneration, AutoProcessor, BitsAndBytesConfig
from PIL import Image
from openai import OpenAI
import torch
import uuid
import os
import re
import base64
import mimetypes

load_dotenv()

MODEL_ID = "fancyfeast/llama-joycaption-beta-one-hf-llava"
GPU_TIER = os.getenv("CUDA_GPU", "").strip().lower()
USE_GEMMA = os.getenv("USE_GEMMA", "").strip().lower()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPEN_ROUTER_API"),
)

cuda_available = torch.cuda.is_available()

if cuda_available:
    device = "cuda"
    dtype = torch.bfloat16
else:
    device = "cpu"
    dtype = torch.float32

processor = AutoProcessor.from_pretrained(MODEL_ID)
use_4bit = cuda_available and GPU_TIER == "poor"

if USE_GEMMA == "yes":
    model = None
elif not cuda_available:
    raise RuntimeError("CUDA GPU required to load the model.")
elif use_4bit:
    try:
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
            bnb_4bit_compute_dtype=dtype,
        )
    except Exception as exc:
        raise RuntimeError(
            "GPU=poor requested 4-bit loading, but bitsandbytes is unavailable."
        ) from exc
    model = LlavaForConditionalGeneration.from_pretrained(
        MODEL_ID,
        quantization_config=quant_config,
        device_map="auto",
    )
elif GPU_TIER == "reach":
    model = LlavaForConditionalGeneration.from_pretrained(
        MODEL_ID,
        torch_dtype=dtype,
    )
    model.to(device)
else:
    raise RuntimeError(
        "Set CUDA_GPU to 'reach' for full precision or 'poor' for 4-bit quantization."
    )
if model is not None:
    model.eval()

def image_to_data_url(path):
    mime, _ = mimetypes.guess_type(path)
    if mime not in {"image/jpeg", "image/png"}:
        raise ValueError(f"Unsupported image type: {mime or 'unknown'}")
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{b64}"

def caption_image(image_path: str, prompt: str) -> str:
    if model is None:
        raise RuntimeError("Model is not loaded. Use caption_image_silicon() instead.")
    image = Image.open(image_path).convert("RGB")

    convo = [
        {"role": "user", "content": prompt.strip()},
    ]
    convo_string = processor.apply_chat_template(
        convo, tokenize=False, add_generation_prompt=True
    )

    inputs = processor(
        text=[convo_string],
        images=[image],
        return_tensors="pt",
    )
    inputs = {k: v.to(device) for k, v in inputs.items()}

    if "pixel_values" in inputs:
        inputs["pixel_values"] = inputs["pixel_values"].to(dtype)

    eos_token_id = processor.tokenizer.eos_token_id
    output_ids = model.generate(
        **inputs,
        max_new_tokens=256,
        do_sample=False,
        eos_token_id=eos_token_id,
        pad_token_id=eos_token_id,
        repetition_penalty=1.1,
        no_repeat_ngram_size=3,
    )
    prompt_len = inputs["input_ids"].shape[1]
    generated_ids = output_ids[0][prompt_len:]
    text = processor.tokenizer.decode(
        generated_ids, skip_special_tokens=True
    ).strip()
    return text.split("###", 1)[0].strip()

def caption_image_silicon(input_data):
    completion_input = client.chat.completions.create(
        extra_body={},
        model="google/gemma-3-4b-it:free",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{CAPTION_CHARACTER}"
                    },
                    
                    {
                        "type": "image_url",
                        "image_url": {
                        "url": input_data
                        }
                    }
                ]
            }
        ]
    )

    caption_input = completion_input.choices[0].message.content

    return caption_input

def _natural_key(text: str):
    return tuple(
        (1, int(part)) if part.isdigit() else (0, part.casefold())
        for part in re.split(r"(\d+)", text)
        if part != ""
    )

def convert_images_to_jpg(directory: str) -> list[tuple[str, str]]:
    """
    Convert .avif/.png/.webp/.jpeg images to .jpg in-place (same folder), then delete originals.
    Returns a list of (source, converted) paths.
    """
    directory = os.path.normpath(directory)
    convert_exts = {".avif", ".png", ".webp", ".jpeg"}

    converted: list[tuple[str, str]] = []
    failures: list[tuple[str, str]] = []

    for filename in os.listdir(directory):
        source = os.path.join(directory, filename)
        if not os.path.isfile(source):
            continue

        stem, ext = os.path.splitext(filename)
        ext = ext.casefold()
        if ext not in convert_exts:
            continue

        # Default output: same stem, .jpg. Avoid overwriting an existing file.
        dest = os.path.join(directory, f"{stem}.jpg")
        if os.path.exists(dest):
            dest = os.path.join(directory, f"{stem}__from_{ext.lstrip('.')}.jpg")
            if os.path.exists(dest):
                dest = os.path.join(directory, f"{stem}__from_{ext.lstrip('.')}_{uuid.uuid4().hex}.jpg")

        try:
            with Image.open(source) as img:
                rgb = img.convert("RGB")
                exif = img.info.get("exif")
                save_kwargs = {"format": "JPEG", "quality": 95, "optimize": True}
                if exif:
                    save_kwargs["exif"] = exif
                rgb.save(dest, **save_kwargs)
            os.remove(source)
            converted.append((source, dest))
        except Exception as e:
            failures.append((source, str(e)))

    if failures:
        msg_lines = ["Failed to convert some images to .jpg:"]
        msg_lines.extend([f"- {path}: {err}" for path, err in failures])
        msg_lines.append(
            "If AVIF files fail to open, install an AVIF-capable Pillow build or add `pillow-avif-plugin`."
        )
        raise RuntimeError("\n".join(msg_lines))

    return converted

def batch_rename(directory: str):
    directory = os.path.normpath(directory)
    prefix = os.path.basename(directory)

    allowed_exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".avif"}
    files = [
        filename
        for filename in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, filename))
        and os.path.splitext(filename)[1].casefold() in allowed_exts
    ]

    files.sort(
        key=lambda filename: (
            _natural_key(os.path.splitext(filename)[0]),
            os.path.splitext(filename)[1].casefold(),
            filename.casefold(),
        )
    )

    staged: list[tuple[str, str]] = []
    for i, filename in enumerate(files):
        source = os.path.join(directory, filename)
        _stem, ext = os.path.splitext(filename)
        final = os.path.join(directory, f"{prefix}{i}{ext}")
        temp = os.path.join(directory, f".__tmp_rename__{uuid.uuid4().hex}{ext}")
        #print(f"Current Name: {source}\nNew Name: {temp}\n")
        os.rename(source, temp)
        staged.append((temp, final))

    for temp, final in staged:
        #print(f"Current Name: {temp}\nNew Name: {final}\n")
        print(f"Current Name: {source}\nNew Name: {final}\n")
        os.rename(temp, final)

def image_clip(directory: str, prompt: str):

    directory = os.path.normpath(directory)

    allowed_exts = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}
    
    imgs = [
        filename
        for filename in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, filename))
        and os.path.splitext(filename)[1].casefold() in allowed_exts
    ]

    imgs.sort(key=lambda f: (_natural_key(os.path.splitext(f)[0]), f.casefold()))
    
    for f in imgs:
        image_path = os.path.join(directory, f)
        caption_path = os.path.splitext(image_path)[0] + ".txt"

        print(f"🖼️  Captioning: {image_path}")
        print()
        if os.getenv("ON_SILICON") == "yes":
            try:
                input_data = image_to_data_url(image_path)
                caption_output = caption_image_silicon(input_data)
                try:
                    with open(caption_path, "w", encoding="utf-8") as caption_text:
                        caption_text.write(caption_output)
                except Exception as e:
                    print(f"❌ Could not write {caption_path}")
            except Exception as e:
                print("❌ Something went wrong in 'caption_image_silicon()'")
        else:
            try:
                caption_output = caption_image(image_path, prompt)
                try:
                    with open(caption_path, "w", encoding="utf-8") as caption_text:
                        caption_text.write(caption_output)
                except Exception as e:
                    print(f"❌ Could not write {caption_path}")
            except Exception as e:
                print("An error occurred:", e)

if __name__ == "__main__":
    
    print("🌸 Lora Captioning Helper 🌸")
    print()
    directory = input(r"Enter the path of the folder: ")
    print()
    caption_type = input(r"Enter caption type: (character or style): ")
    print()

    directory = os.path.normpath(directory)
    directory_token = os.path.basename(directory)

    allowed_prompts = ["character", "style"]

    if caption_type in allowed_prompts:
        if caption_type == 'character':
            trigger = input(f"Enter the trigger word(s) Ex: 'tok woman': ")
            prompt = CAPTION_CHARACTER.replace("TRIGGER", trigger)
        elif caption_type == 'style':
            prompt = CAPTION_STYLE
        print('👀 Converting imgs to JPG...')
        convert_images_to_jpg(directory)
        print()
        print('✨ Renaming imgs in batch...')
        batch_rename(directory)
        print()
        print('🧠 Clipping imgs...')
        image_clip(directory, prompt)

    else:
        print('❌ Invalid type. Choose: "character", "style"')
