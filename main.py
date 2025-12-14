import os
import re
import shutil
import uuid
import requests
from PIL import Image
import io
import base64
import json
import sys
from dotenv import load_dotenv
from prompts import *


# PORT 8000 VastAI
load_dotenv()
vllm_url = os.getenv("VLLM_URL")
vllm_url = f'http://{vllm_url}/v1/chat/completions'  # or 'v1/responses'
model_name = os.getenv("MODEL_NAME")
api_key = (
    os.getenv("VLLM_API_TOKEN")
    or os.getenv("VLLM_API_KEY")
    or os.getenv("OPENAI_API_KEY")
)

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
        print(f"Current Name: {source}\nNew Name: {temp}\n")
        os.rename(source, temp)
        staged.append((temp, final))

    for temp, final in staged:
        print(f"Current Name: {temp}\nNew Name: {final}\n")
        os.rename(temp, final)

def image_clip(directory: str, prompt: str, type_of: str, style_: str):

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

        image = Image.open(image_path).convert("RGB")

        # Convert the image to a format suitable for transmission (e.g., JPEG)
        image_io = io.BytesIO()
        image.save(image_io, format='JPEG')
        image_io.seek(0)

        # Convert the image to base64
        image_base64 = base64.b64encode(image_io.getvalue()).decode('utf-8')
        image_data_url = f"data:image/jpeg;base64,{image_base64}"

        data = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": "You are a helpful image captioner."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_data_url}},
                    ],
                },
            ],
            "max_tokens": 512,
            "temperature": 0.6,
            "top_p": 0.9,
        }

        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            response = requests.post(vllm_url, json=data, headers=headers, timeout=300)
            response.raise_for_status()
            response_data = response.json()
            caption = (
                response_data["choices"][0]["message"]["content"]
                if "choices" in response_data
                else "No caption found"
            )
            caption_out = caption.strip()
            if type_of == "style" and style_:
                caption_out = caption_out.rstrip()
                if caption_out.endswith("."):
                    caption_out = caption_out[:-1].rstrip()
                caption_out = f"{caption_out}, {style_}"
            with open(caption_path, "w", encoding="utf-8") as caption_text:
                caption_text.write(caption_out)
            print(f"💾 Saved caption: {caption_path}")
            print()
        except requests.exceptions.RequestException as e:
            print("An error occurred:", e)

if __name__ == "__main__":
    
    print("Python Program to caption image Lora dataset")
    directory = input(r"Enter the path of the folder: ")
    directory = os.path.normpath(directory)
    directory_token = os.path.basename(directory)

    allowed_prompts = ["descriptive", "descriptive_casual", "sd_prompt", "style"]

    while True:
        prompt = input(r'Enter prompt type: "descriptive", "descriptive_casual", "sd_prompt", "style": ').strip().lower()
        if prompt in allowed_prompts:
            break
        print('❌ Invalid prompt. Choose: "descriptive", "descriptive_casual", "sd_prompt", "style"')
    
    type_of = ""
    style_ = ""

    if prompt == "style":
        type_of = "style"
        style_ = input(r'Enter the syle description, Ex: "hiroiko araki style": ').strip().lower()
        prompt_text = style_prompt
    else:
        while True:
            length = input(r'Enter caption length: "short", "medium-length", "long", "very long": ').strip().lower()
            if length in caption_length:
                break
            print('❌ Invalid length. Choose: "short", "medium-length", "long", "very long"')
    
        if prompt == 'descriptive':
            prompt_text = descriptive.replace("LENGTH", length).replace("DIRECTORY", directory_token)
        elif prompt == 'descriptive_casual':
            prompt_text = descriptive_casual.replace("LENGTH", length).replace("DIRECTORY", directory_token)
        elif prompt == 'sd_prompt':
            prompt_text = sd_prompt.replace("LENGTH", length).replace("DIRECTORY", directory_token)
        else:
            raise RuntimeError(f"Unknown prompt: {prompt}")
    
    print()
    print("ℹ️ Prompt for this run:")
    print()
    print(prompt_text)
    print()
    
    #convert_images_to_jpg(directory)
    #batch_rename(directory)
    
    image_clip(directory, prompt_text, type_of, style_)
