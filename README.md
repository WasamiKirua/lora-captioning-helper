# lora captioning helper

Small utility to (optionally) rename a folder of images and generate `.txt` captions for each image via a vLLM OpenAI-compatible endpoint (JoyCaption / LLaVA).

## Setup

1. Install deps: `pip install -r requirements.txt`
2. Create a `.env` file (see `.env.example`) with:
   - `VLLM_URL=HOST:PORT` (example format: `123.45.67.89:8000`)
   - `MODEL_NAME=YOUR_MODEL_ID` (example format: `fancyfeast/llama-joycaption-beta-one-hf-llava`)
   - `VLLM_API_TOKEN=YOUR_TOKEN` (sent as `Authorization: Bearer ...`; required if your endpoint is protected)

## How it works (important)

- Put your training images inside a folder whose name is your LoRA trigger token (example: `Suz1e/`).
- When you run the script and enter `directory=Suz1e`, the folder name (`Suz1e`) is used as:
  - the prefix for renaming (`Suz1e0.jpg`, `Suz1e1.jpg`, ...)
  - the character/trigger token injected into prompts when you’re not doing style-only training
- Before renaming, the script converts `.avif`, `.png`, `.webp`, and `.jpeg` images to `.jpg` (and deletes the originals) so your dataset ends up with consistent `.jpg` files.
- For each image, the script writes a matching caption file next to it: `image.jpg` → `image.txt`.
- If you select training `type_of="style"`, the script does not treat the directory name as the trigger token; instead it appends your style string to every caption (example: `..., hiroiko araki style`).

## Run

`python main.py`

Then follow the prompts for:
- `directory` (the image folder / trigger token)
- caption length and prompt type

## Note

Prompts are tailored to generate SFW and NSFW captions (if intended)
