# Lora Captioning Helper

## Setup (uv)

1) Create and sync the virtual environment:

```bash
uv sync
```

2) Activate the environment:

```bash
source .venv/bin/activate
```

3) Create a `.env` file with your settings:

```ini
# Required when using the OpenRouter flow
OPEN_ROUTER_API=your_key_here

# CUDA GPU tier: "reach" for full precision, "poor" for 4-bit
CUDA_GPU=reach

# Use Gemma via OpenRouter instead of local JoyCaption, this skip local model loading
USE_GEMMA=no
```

## How It Works

The script loads and runs the JoyCaption model locally when a CUDA GPU is available and `USE_GEMMA` is not `"yes"`. It supports:

- Full precision loading when `CUDA_GPU=reach`
- 4-bit loading when `CUDA_GPU=poor` (CUDA only)

When `USE_GEMMA=yes`, the local model is skipped and the script uses the OpenRouter endpoint instead.

## Directory Preparation

When you run the script, it prompts for `directory`. That value must be the **folder name/path that contains your dataset images**. For example, if your images are in `./my_set`, then enter `my_set` when prompted. The script uses that folder to find images, generate captions, and write `.txt` files next to each image.

## Trigger Words in Captions

If your prompt includes a trigger word (for example, `tok woman`), the model will use it when describing the person/character in the image. This helps ensure captions consistently include your trigger token where a person is present.

### Caption Output Differences

- **JoyCaption (local model):** more verbose, detailed captions.
- **Gemma via OpenRouter:** shorter captions. Enable it by setting `USE_GEMMA=yes`.

## Running

```bash
./.venv/bin/python main.py
```
