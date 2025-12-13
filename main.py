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

def batch_rename(directory: str):
    directory = os.path.normpath(directory)
    prefix = os.path.basename(directory)

    files = [
        filename
        for filename in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, filename))
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

def cleanup_tmp_dirs(root: str, prefix: str = "_tmp_") -> list[str]:
    removed: list[str] = []
    for name in os.listdir(root):
        path = os.path.join(root, name)
        if name.startswith(prefix) and os.path.isdir(path):
            shutil.rmtree(path)
            removed.append(path)
    return removed

def image_clip(directory: str, prompt: str):

    directory = os.path.normpath(directory)
    character_name = os.path.basename(directory)

    test_prompt = f"""Write a medium-length detailed description for this image. If there is a person/character in the image you must refer to them as {character_name}. 
    Do NOT mention the image's resolution. Do NOT mention any text that is in the image. 
    Mention whether the image depicts an extreme close-up, close-up, medium close-up, medium shot, cowboy shot, medium wide shot, wide shot, or extreme wide shot. 
    Do not mention the mood/feeling/etc of the image. Your response will be used by a text-to-image model, so avoid useless meta phrases like “This image shows…”, "You are looking at...", etc."""

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

        response = requests.post(vllm_url, json=data, headers=headers, timeout=300)

        if response.status_code == 200:
            response_data = response.json()
            caption = (
                response_data["choices"][0]["message"]["content"]
                if "choices" in response_data
                else "No caption found"
            )
            with open(caption_path, "w", encoding="utf-8") as caption_text:
                caption_text.write(caption.strip())
            print(f"💾 Saved caption: {caption_path}")
        else:
            if response.status_code == 401 and not api_key:
                print(
                    "Error: 401 Unauthorized. Set VLLM_API_TOKEN (or VLLM_API_KEY / OPENAI_API_KEY) "
                    "to match your vLLM server's API token."
                )
            else:
                print(f"Error: {response.status_code}, {response.text}")

if __name__ == "__main__":
    print("Python Program to caption image Lora dataset")
    directory = input(r"Enter the path of the folder: ")
    
    while True:
        length = input(r'Enter caption length: "short", "medium-length", "long", "very long": ').strip().lower()
        if length in caption_length:
            break
        print('❌ Invalid length. Choose: "short", "medium-length", "long", "very long"')
    
    allowed_prompts = ["descriptive", "descriptive_casual", "sd_prompt"]

    while True:
        prompt = input(r'Enter prompt type: "descriptive", "descriptive_casual", "sd_prompt": ').strip().lower()
        if prompt in allowed_prompts:
            break
        print('❌ Invalid prompt. Choose: "descriptive", "descriptive_casual", "sd_prompt"')

    if prompt == 'descriptive':
        descriptive = descriptive.replace("LENGTH", length)
        descriptive = descriptive.replace("DIRECTORY", directory)
        print(descriptive)
    elif prompt == 'descriptive_casual':
        descriptive_casual = descriptive_casual.replace("LENGTH", length)
        descriptive_casual = descriptive_casual.replace("DIRECTORY", directory)
        print(descriptive_casual)
    elif prompt == 'sd_prompt':
        sd_prompt = sd_prompt.replace("LENGTH", length)
        sd_prompt = sd_prompt.replace("DIRECTORY", directory)
        print(sd_prompt)
    
    batch_rename(directory)
    
    image_clip(directory, prompt)
    
    answer = input("Delete folders here starting with '_tmp_'? (y/N): ").strip().lower()
    
    if answer in {"y", "yes"}:
        removed = cleanup_tmp_dirs(os.getcwd())
        print(f"Removed {len(removed)} folder(s).")
