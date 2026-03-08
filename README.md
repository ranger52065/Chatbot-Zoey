

<div align="center">
# 🤖 Zoey - 多模态AI助手
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Gradio](https://img.shields.io/badge/Gradio-5.49.1-orange.svg)](https://gradio.app/)

一个基于通义千问的智能对话助手，支持文字、图片、音频多模态交互

[功能特性](#功能特性) • [快速开始](#快速开始) • [使用指南](#使用指南) • [配置说明](#配置说明)

</div>

---

## 📖 项目简介

Zoey 是一个基于 Alibaba DashScope API（通义千问）构建的多模态AI对话助手。通过 Gradio 提供友好的 Web 界面，支持文字、图片、音频等多种输入方式，实现智能对话、图像理解、语音交互等功能。

<a name="功能特性"></a>
### ✨ 功能特性

- 🎯 **多模型支持** - 支持 qwen-turbo、qwen-plus、qwen-max、qwen-omni-turbo 四种模型
- 🖼️ **图像理解** - 上传图片进行智能分析和对话
- 🎵 **音频处理** - 支持语音输入和语音回复（仅 qwen-omni-turbo）
- 💬 **流式响应** - 实时流式输出，响应更快速流畅
- 🎨 **友好界面** - 基于 Gradio 的现代化 Web 界面
- 💡 **快捷问题** - 预设常用问题，一键发送
- 📥 **对话导出** - 支持导出聊天历史为 JSON 文件
- 🔧 **自定义提示词** - 支持设置系统提示词定制 AI 行为
- 🌐 **局域网访问** - 支持局域网内多设备访问

---
<a name="快速开始"></a>
## 🚀 快速开始

### 前置要求

- Python 3.11 或更高版本
- DashScope API Key（[获取地址](https://dashscope.console.aliyun.com/)）

### 安装步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/ranger52065/Zoey.git
   cd Zoey
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r successful_requirements.txt
   ```

4. **配置环境变量**
   
   创建 `.env` 文件并添加您的 API Key：
   ```env
   DASHSCOPE_API_KEY=your_api_key_here
   ```

5. **启动应用**
   ```bash
   # 方式一：直接运行
   python Zoey/Zoey.py
   
   # 方式二：使用启动脚本（Windows）
   start.bat
   ```

6. **访问界面**
   
   打开浏览器访问：
   - 本地访问：http://127.0.0.1:7860
   - 局域网访问：http://your-local-ip:7860

---
<a name="使用指南"></a>
## 📚 使用指南

### 模型选择

| 模型 | 速度 | 适用场景 | 音频输出 |
|------|------|----------|----------|
| qwen-turbo | ⚡⚡⚡ 最快 | 日常对话、快速问答 | ❌ |
| qwen-plus | ⚡⚡ 均衡 | 通用场景、一般任务 | ❌ |
| qwen-max | ⚡ 深度 | 复杂推理、深度分析 | ❌ |
| qwen-omni-turbo | ⚡⚡ 多模态 | 图像理解、语音交互 | ✅ |

### 多模态输入

支持的文件类型：
- **图片**：`.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`
- **音频**：`.wav`, `.mp3`, `.m4a`, `.aac`, `.ogg`, `.flac`
- **视频**：`.mp4`, `.avi`, `.mov`, `.mkv`, `.webm`（仅显示文件名）

### 注意事项

⚠️ **qwen-omni-turbo 模型限制**：
- 不支持多张图片同时输入
- 不支持多个音频同时输入
- 不支持图片和音频混合输入

---
<a name="配置说明"></a>
## ⚙️ 配置说明

### 环境变量

在 `.env` 文件中配置：

```env
# 必填：DashScope API Key
DASHSCOPE_API_KEY=your_api_key_here

# 可选：自定义 API 地址
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

### 系统提示词

在 Web 界面的"系统提示词"文本框中自定义 AI 的角色和行为：

```
你是一个友好、专业的AI助手，请用简洁清晰的语言回答问题。
```

---

## 🛠️ 技术栈

- **后端框架**：Python + OpenAI SDK
- **前端界面**：Gradio
- **AI 模型**：Alibaba DashScope (通义千问)
- **图像处理**：Pillow
- **环境管理**：python-dotenv

---

## 📁 项目结构

```
Zoey/
├── .env                    # 环境变量配置
├── .venv/                  # 虚拟环境
├── env_utils.py            # 环境变量加载工具
├── successful_requirements.txt  # 依赖列表
├── start.bat               # Windows 启动脚本
├── README.md               # 项目文档
├── AGENTS.md               # AI 编码助手指南
└── Zoey/
    ├── __init__.py
    └── Zoey.py             # 主应用程序
```

---

## 🔧 开发指南

### 代码风格

本项目使用 Ruff 进行代码格式化和检查：

```bash
# 代码检查
ruff check Zoey/

# 自动修复
ruff check --fix Zoey/

# 代码格式化
ruff format Zoey/
```

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行单个测试文件
pytest tests/test_example.py -v

# 运行单个测试函数
pytest tests/test_example.py::test_func -v
```

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📝 更新日志

### v1.0.0 (2026-03-03)
- ✨ 初始版本发布
- ✅ 支持文字、图片、音频多模态输入
- ✅ 支持四种通义千问模型
- ✅ 实现流式响应
- ✅ 添加对话导出功能
- ✅ 支持自定义系统提示词


---

## 🙏 致谢

- [Alibaba DashScope](https://dashscope.aliyun.com/) - 提供强大的 AI 模型服务
- [Gradio](https://gradio.app/) - 优秀的机器学习界面框架
- [OpenAI SDK](https://github.com/openai/openai-python) - 完善的 API 客户端

---

## 📮 联系方式

如有问题或建议，欢迎：
- 提交 [Issue](https://github.com/ranger52065/Zoey/issues)
- 发送邮件至 ranger52065@sina.com

---

<div align="center">

**如果这个项目对你有帮助，请给一个 ⭐️ Star 支持一下！**

Made with ❤️ by [ranger52065]

</div>
