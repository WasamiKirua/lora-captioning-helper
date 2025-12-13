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
  - the trigger name referenced in the generated captions
  - the prefix for renaming if you use `batch_rename()`
- For each image, the script writes a matching caption file next to it: `image.jpg` → `image.txt`.

## Run

`python main.py`

Then follow the prompts for:
- `directory` (the image folder / trigger token)
- caption length and prompt type

## Note

Prompts are tailored to generate SFW and NSFW captions (if intended)

