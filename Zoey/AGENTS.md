# AGENTS.md

This document provides guidance for AI coding agents working in this repository.

## Project Overview

Zoey is a multimodal AI chatbot application built with OpenAI SDK and Gradio. It supports text, image, and audio inputs, interfacing with Alibaba's DashScope API (qwen models) for LLM capabilities.

## Build/Lint/Test Commands

### Running the Application
```bash
.venv\Scripts\activate          # Activate virtual environment (Windows)
python Zoey/Zoey.py             # Run the main application
start.bat                       # Or use the batch file
```

### Linting and Formatting
```bash
ruff check Zoey/                # Run ruff linter
ruff check --fix Zoey/          # Run ruff with auto-fix
ruff format Zoey/               # Run ruff formatter
```

### Testing
**Note:** No test directory currently exists. When tests are added, use:
```bash
pytest tests/ -v                              # Run all tests
pytest tests/test_example.py -v               # Run a single test file
pytest tests/test_example.py::test_func -v    # Run a single test function
pytest tests/test_example.py -k "test_name" -v  # Run tests matching name pattern
pytest tests/ --cov=Zoey -v                   # Run with coverage
```

### Dependency Management
```bash
pip install -r successful_requirements.txt
```

## Project Structure

```
Zoey/
├── .env                    # Environment variables (API keys) - DO NOT COMMIT
├── .venv/                  # Virtual environment
├── env_utils.py            # Environment variable loader
├── successful_requirements.txt
├── start.bat               # Windows startup script
└── Zoey/
    ├── __init__.py
    └── Zoey.py             # Main multimodal chatbot application
```

## Code Style Guidelines

### Imports
```python
# Order: path modifications, stdlib, third-party, local modules
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import base64
import io
import json
from datetime import datetime
from typing import Optional

import gradio as gr
from PIL import Image
from openai import OpenAI

from env_utils import DASHSCOPE_API_KEY
```

### Naming Conventions
- **Files**: snake_case (e.g., `env_utils.py`)
- **Functions**: snake_case (e.g., `process_image`, `build_content`)
- **Variables**: snake_case (e.g., `user_messages`, `input_types`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MODELS`, `PRESET_QUESTIONS`)
- **Classes**: PascalCase

### Type Hints
```python
def process_image(image_path: str) -> Optional[dict]:
    """Process image and return API-compatible dict."""
    pass

def build_content(user_messages: list) -> tuple:
    """Build content list and return (content, input_types)."""
    pass
```

### Docstrings
```python
def function_name(param: type) -> return_type:
    """
    Brief description in Chinese.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
    """
    pass
```

### Error Handling
```python
try:
    result = some_operation()
except Exception as e:
    print(f"操作失败: {e}")
    import traceback
    traceback.print_exc()
    return None
```

### Code Formatting
- Maximum line length: ~100 characters
- Use 4 spaces for indentation (no tabs)
- Blank lines between logical sections
- Use f-strings for string formatting
- Use Chinese for user-facing messages and logs

### Generator Functions (Streaming)
```python
def submit_messages(history: list, model: str, enable_audio: bool, system_prompt: str):
    """Submit messages and stream AI response. Yields updated history after each chunk."""
    for chunk in completion:
        if hasattr(chunk, "choices") and chunk.choices:
            delta = chunk.choices[0].delta
            if hasattr(delta, "content") and delta.content:
                response_text += delta.content
                history[-1]["content"] = response_text
                yield history
```

## Gradio Application Pattern

```python
def create_ui():
    """Create Gradio interface."""
    with gr.Blocks(title="Zoey AI助手", theme=gr.themes.Soft()) as block:
        gr.Markdown("# 🤖 Zoey 多模态AI助手")
        
        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(type="messages", height=500)
                chat_input = gr.MultimodalTextbox(
                    interactive=True,
                    file_types=["image", ".wav", ".mp3", ".m4a"],
                    file_count="multiple",
                )
        
        # Event bindings with chained .then()
        chat_input.submit(
            add_message, [chatbot, chat_input], [chatbot, chat_input],
        ).then(
            submit_messages, [chatbot, model_select, audio_output, system_prompt], [chatbot],
        ).then(
            lambda: "就绪", None, status_text
        )
    
    return block
```

## Multimodal Input Handling

### Supported File Types
- **Images**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`
- **Audio**: `.wav`, `.mp3`, `.m4a`, `.aac`, `.ogg`, `.flac`
- **Video**: `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm` (shown as text placeholder)

### Processing Patterns
```python
def process_image(image_path: str) -> Optional[dict]:
    """Convert image to base64-encoded API format."""
    # Handle RGBA to RGB conversion, resize if > 1024px
    return {"type": "image_url", "image_url": {"url": f"data:image/{fmt};base64,{data}"}}

def process_audio(audio_path: str) -> Optional[dict]:
    """Convert audio to base64-encoded API format. Warns if > 25MB."""
    return {"type": "input_audio", "input_audio": {"data": base64_data, "format": fmt}}
```

## API Configuration

Uses Alibaba's DashScope API with OpenAI-compatible interface:
- API Key: `DASHSCOPE_API_KEY` environment variable via `env_utils.py`
- Base URL: `https://dashscope.aliyuncs.com/compatible-mode/v1`

| Model | Speed | Use Case | Audio Output |
|-------|-------|----------|--------------|
| qwen-turbo | Fastest | Daily conversation | No |
| qwen-plus | Medium | General tasks | No |
| qwen-max | Slow | Complex reasoning | No |
| qwen-omni-turbo | Medium | Multimodal (image/audio) | Yes |

### Model Limitations
- `qwen-omni-turbo`: Does NOT support multiple images in one request
- `qwen-omni-turbo`: Does NOT support multiple audio files in one request
- `qwen-omni-turbo`: Does NOT support mixed image + audio input

## Security Notes

- Never commit `.env` file or API keys
- Keep sensitive configuration in environment variables
- Use `env_utils.py` to load environment variables with `python-dotenv`