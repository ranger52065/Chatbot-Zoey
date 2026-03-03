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
from env_utils import DASHSCOPE_API_KEY
from openai import OpenAI

# 初始化OpenAI客户端
client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 可用模型配置
MODELS = {
    "qwen-turbo": {"name": "通义千问-Turbo (快速)", "supports_audio": False},
    "qwen-plus": {"name": "通义千问-Plus (均衡)", "supports_audio": False},
    "qwen-max": {"name": "通义千问-Max (智能)", "supports_audio": False},
    "qwen-omni-turbo": {"name": "通义千问-Omni (多模态)", "supports_audio": True},
}

# 预设问题
PRESET_QUESTIONS = [
    "介绍一下你自己",
    "今天天气怎么样？",
    "给我讲个笑话",
    "推荐一部好看的电影",
    "如何提高编程能力？",
]


def process_image(image_path: str) -> Optional[dict]:
    """
    将图片转换为base64编码格式
    
    Args:
        image_path: 图片文件路径
        
    Returns:
        包含图片数据的字典，用于API请求
    """
    try:
        with Image.open(image_path) as img:
            img_format = img.format if img.format else "JPEG"

            if img.mode == "RGBA":
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
                img_format = "JPEG"
            elif img.mode != "RGB":
                img = img.convert("RGB")

            max_size = 1024
            if max(img.size) > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

            buffered = io.BytesIO()
            img.save(buffered, format=img_format, quality=85)
            img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

            return {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/{img_format.lower()};base64,{img_base64}",
                    "detail": "low",
                },
            }
    except Exception as e:
        print(f"图片处理失败 {image_path}: {e}")
        return None


def process_audio(audio_path: str) -> Optional[dict]:
    """
    将音频文件转换为base64编码格式
    
    Args:
        audio_path: 音频文件路径
        
    Returns:
        包含音频数据的字典，用于API请求
    """
    try:
        file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
        if file_size_mb > 25:
            print(f"警告: 音频文件过大 ({file_size_mb:.2f}MB)，可能影响处理速度")

        with open(audio_path, "rb") as f:
            audio_data = f.read()

        audio_format = os.path.splitext(audio_path)[1].lower().lstrip(".")
        if not audio_format:
            audio_format = "wav"

        audio_base64 = base64.b64encode(audio_data).decode("utf-8")

        return {
            "type": "input_audio",
            "input_audio": {
                "data": audio_base64,
                "format": audio_format,
            },
        }
    except Exception as e:
        print(f"音频处理失败 {audio_path}: {e}")
        return None


def get_last_user_messages(history: list) -> Optional[list]:
    """
    获取最后一次assistant回复后的所有用户消息
    
    Args:
        history: 聊天历史记录
        
    Returns:
        用户消息列表，如果没有则返回None
    """
    if not history:
        return None
    if history[-1]["role"] == "assistant":
        return None

    last_assistant_idx = -1
    for i in range(len(history) - 1, -1, -1):
        if history[i]["role"] == "assistant":
            last_assistant_idx = i
            break

    if last_assistant_idx == -1:
        return history
    return history[last_assistant_idx + 1 :]


def add_message(history: list, messages: dict) -> tuple:
    """
    将用户输入的消息添加到聊天记录
    
    Args:
        history: 当前聊天历史
        messages: 用户输入的消息（包含text和files）
        
    Returns:
        更新后的历史和清空的输入框
    """
    for file_path in messages.get("files", []):
        print(f"上传文件: {file_path}")
        history.append({"role": "user", "content": (file_path,)})

    if messages.get("text") and messages["text"].strip():
        print(f"文字输入: {messages['text']}")
        history.append({"role": "user", "content": messages["text"]})

    return history, gr.MultimodalTextbox(value=None, interactive=True)


def add_preset_question(history: list, question: str) -> tuple:
    """
    添加预设问题到聊天记录
    
    Args:
        history: 当前聊天历史
        question: 预设问题
        
    Returns:
        更新后的历史
    """
    if question:
        history.append({"role": "user", "content": question})
    return history, gr.MultimodalTextbox(value=None, interactive=True)


def build_content(user_messages: list) -> tuple:
    """
    构建API请求的内容列表
    
    Args:
        user_messages: 用户消息列表
        
    Returns:
        (content列表, 输入类型统计)
        输入类型统计: {'images': int, 'audios': int, 'texts': int}
    """
    content = []
    input_types = {'images': 0, 'audios': 0, 'texts': 0}

    for msg in user_messages:
        if isinstance(msg["content"], str):
            content.append({"type": "text", "text": msg["content"]})
            input_types['texts'] += 1

        elif isinstance(msg["content"], tuple):
            file_path = msg["content"][0]
            ext = file_path.lower()

            if ext.endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp")):
                img_dict = process_image(file_path)
                if img_dict:
                    content.append(img_dict)
                    input_types['images'] += 1

            elif ext.endswith((".wav", ".mp3", ".m4a", ".aac", ".ogg", ".flac")):
                audio_dict = process_audio(file_path)
                if audio_dict:
                    content.append(audio_dict)
                    input_types['audios'] += 1

            elif ext.endswith((".mp4", ".avi", ".mov", ".mkv", ".webm")):
                content.append(
                    {"type": "text", "text": f"[上传视频: {os.path.basename(file_path)}]"}
                )
                input_types['texts'] += 1
            else:
                content.append(
                    {"type": "text", "text": f"[上传文件: {os.path.basename(file_path)}]"}
                )
                input_types['texts'] += 1

    return content, input_types


def submit_messages(
    history: list, model: str, enable_audio: bool, system_prompt: str
):
    """
    提交用户消息并生成AI回复
    
    Args:
        history: 聊天历史
        model: 选择的模型名称
        enable_audio: 是否启用音频输出
        system_prompt: 系统提示词
        
    Yields:
        更新后的聊天历史（流式输出）
    """
    user_messages = get_last_user_messages(history)

    if not user_messages:
        yield history
        return

    print(f"[{datetime.now().strftime('%H:%M:%S')}] 处理用户消息，模型: {model}")

    content, input_types = build_content(user_messages)

    if not content:
        yield history
        return

    is_omni_model = model == "qwen-omni-turbo"
    
    if is_omni_model:
        has_multiple_images = input_types['images'] > 1
        has_multiple_audios = input_types['audios'] > 1
        has_mixed_modalities = (input_types['images'] > 0 and input_types['audios'] > 0)
        
        if has_multiple_images:
            history.append({"role": "assistant", "content": "⚠️ qwen-omni-turbo 模型不支持多张图片同时输入，请每次只上传一张图片。"})
            yield history
            return
        
        if has_multiple_audios:
            history.append({"role": "assistant", "content": "⚠️ qwen-omni-turbo 模型不支持多个音频同时输入，请每次只上传一个音频。"})
            yield history
            return
        
        if has_mixed_modalities:
            history.append({"role": "assistant", "content": "⚠️ qwen-omni-turbo 模型不支持图片和音频混合输入，请分开提交。"})
            yield history
            return

    history.append({"role": "assistant", "content": "⏳ 正在思考..."})
    yield history

    try:
        api_params = {
            "model": model,
            "messages": [],
            "stream": True,
            "stream_options": {"include_usage": True},
        }

        if system_prompt.strip():
            api_params["messages"].append(
                {"role": "system", "content": system_prompt.strip()}
            )

        api_params["messages"].append({"role": "user", "content": content})

        supports_audio = MODELS.get(model, {}).get("supports_audio", False)
        if enable_audio and supports_audio:
            api_params["modalities"] = ["text", "audio"]
            api_params["audio"] = {"voice": "Cherry", "format": "wav"}

        completion = client.chat.completions.create(**api_params)

        history.pop()
        history.append({"role": "assistant", "content": ""})

        response_text = ""
        audio_received = False

        for chunk in completion:
            if hasattr(chunk, "usage") and chunk.usage:
                print(f"Token使用: {chunk.usage}")
                continue

            if hasattr(chunk, "choices") and chunk.choices:
                delta = chunk.choices[0].delta

                if hasattr(delta, "content") and delta.content:
                    response_text += delta.content
                    history[-1]["content"] = response_text
                    yield history

                if hasattr(delta, "audio") and delta.audio:
                    audio_received = True
                    if hasattr(delta.audio, "data"):
                        try:
                            audio_bytes = base64.b64decode(delta.audio.data)
                            audio_path = os.path.join(
                                os.path.dirname(__file__), "response_audio.wav"
                            )
                            with open(audio_path, "wb") as f:
                                f.write(audio_bytes)
                            print(f"音频已保存: {audio_path}")
                        except Exception as e:
                            print(f"音频处理错误: {e}")

        if not response_text and audio_received:
            history[-1]["content"] = "🔊 [已生成语音回复，请查看保存的音频文件]"

        print(f"[{datetime.now().strftime('%H:%M:%S')}] 回复完成")

    except Exception as e:
        print(f"调用模型出错: {e}")
        import traceback

        traceback.print_exc()

        if history and history[-1]["role"] == "assistant":
            if "思考" in history[-1].get("content", ""):
                history.pop()
            else:
                history[-1]["content"] = f"❌ 出错了: {str(e)}"
        else:
            history.append({"role": "assistant", "content": f"❌ 出错了: {str(e)}"})

    yield history


def export_history(history: list) -> Optional[str]:
    """
    导出聊天历史为JSON文件
    
    Args:
        history: 聊天历史
        
    Returns:
        导出文件的路径，失败返回None
    """
    if not history:
        return None

    try:
        export_data = []
        for msg in history:
            if isinstance(msg.get("content"), str):
                export_data.append(
                    {"role": msg["role"], "content": msg["content"]}
                )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_path = os.path.join(
            os.path.dirname(__file__), f"chat_history_{timestamp}.json"
        )

        with open(export_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        print(f"对话已导出: {export_path}")
        return export_path
    except Exception as e:
        print(f"导出失败: {e}")
        return None


def handle_export(history: list) -> tuple:
    """处理导出并返回文件和状态信息"""
    export_path = export_history(history)
    if export_path:
        return export_path, f"导出成功: {export_path}"
    else:
        return None, "导出失败或无对话内容"


def create_ui():
    """创建Gradio界面"""
    with gr.Blocks(
        title="Zoey AI助手",
        theme=gr.themes.Soft(),
        css="""
        .preset-btn { min-width: 120px; }
        .status-bar { background: #f0f0f0; padding: 8px; border-radius: 8px; }
        """,
    ) as block:
        gr.Markdown(
            """
            # 🤖 Zoey 多模态AI助手
            **支持文字、图片、音频输入 | 多模型切换 | 流式响应**
            """
        )

        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(
                    type="messages",
                    height=500,
                    label="对话窗口",
                    show_copy_button=True,
                    avatar_images=(None, "🤖"),
                )

                chat_input = gr.MultimodalTextbox(
                    interactive=True,
                    file_types=[
                        "image",
                        ".wav",
                        ".mp3",
                        ".m4a",
                        ".mp4",
                        ".jpg",
                        ".png",
                        ".gif",
                        ".webp",
                    ],
                    file_count="multiple",
                    placeholder="输入消息或上传文件（支持图片、音频、视频）...",
                    show_label=False,
                    sources=["microphone", "upload"],
                )

                with gr.Row():
                    clear_btn = gr.Button("🗑️ 清除对话", variant="secondary")
                    export_btn = gr.Button("📥 导出对话", variant="secondary")

            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ 设置")

                model_select = gr.Dropdown(
                    choices=list(MODELS.keys()),
                    value="qwen-turbo",
                    label="选择模型",
                    info="不同模型速度和智能程度不同",
                )

                audio_output = gr.Checkbox(
                    label="启用语音回复",
                    value=False,
                    info="仅Omn模型支持，会增加响应时间",
                )

                system_prompt = gr.Textbox(
                    label="系统提示词",
                    placeholder="设置AI的角色和行为...",
                    value="你是一个友好、专业的AI助手，请用简洁清晰的语言回答问题。",
                    lines=3,
                )

                gr.Markdown("### 💡 快捷问题")
                preset_buttons = []
                with gr.Row():
                    for i, q in enumerate(PRESET_QUESTIONS[:3]):
                        btn = gr.Button(q[:10] + "...", elem_classes="preset-btn")
                        preset_buttons.append((btn, q))
                with gr.Row():
                    for i, q in enumerate(PRESET_QUESTIONS[3:]):
                        btn = gr.Button(q[:10] + "...", elem_classes="preset-btn")
                        preset_buttons.append((btn, q))

                gr.Markdown(
                    """
                    ### 📖 使用说明
                    - **qwen-turbo**: 最快，适合日常对话
                    - **qwen-plus**: 均衡，通用场景
                    - **qwen-max**: 最智能，复杂任务
                    - **qwen-omni**: 多模态，支持图片/音频
                    """
                )

        status_text = gr.Textbox(
            label="状态", value="就绪", interactive=False, elem_classes="status-bar"
        )

        # 事件绑定
        chat_input.submit(
            add_message,
            [chatbot, chat_input],
            [chatbot, chat_input],
        ).then(
            submit_messages,
            [chatbot, model_select, audio_output, system_prompt],
            [chatbot],
        ).then(
            lambda: "就绪", None, status_text
        )

        clear_btn.click(
            lambda: ([], gr.MultimodalTextbox(value=None), "对话已清除"),
            None,
            [chatbot, chat_input, status_text],
        )

        export_btn.click(
            handle_export,
            [chatbot],
            [gr.File(label="导出文件"), status_text],
        )

        for btn, question in preset_buttons:
            btn.click(
                add_preset_question,
                [chatbot, gr.State(question)],
                [chatbot, chat_input],
            ).then(
                submit_messages,
                [chatbot, model_select, audio_output, system_prompt],
                [chatbot],
            ).then(
                lambda: "就绪", None, status_text
            )

    return block


def find_available_port(start_port: int = 7860, max_attempts: int = 10) -> int:
    """查找可用端口"""
    import socket
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    return start_port


if __name__ == "__main__":
    print("=" * 50)
    print("Zoey 多模态AI助手 启动中...")
    print("=" * 50)
    
    block = create_ui()
    
    import socket
    local_ip = socket.gethostbyname(socket.gethostname())
    port = find_available_port()
    
    print(f"\n[本地] http://127.0.0.1:{port}")
    print(f"[局域网] http://{local_ip}:{port}")
    print("=" * 50)
    
    block.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False,
        show_error=True,
    )
