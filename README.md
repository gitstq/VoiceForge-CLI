<div align="center">

# 🎙️ VoiceForge-CLI

**轻量级 AI 语音合成与声音克隆引擎**

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-orange.svg)](https://github.com/gitstq/VoiceForge-CLI/releases)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)](https://github.com/gitstq/VoiceForge-CLI/pulls)

[English](README.en.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md)

<img src="assets/logo.svg" alt="VoiceForge-CLI Logo" width="200"/>

**零 API 费用 · 多引擎切换 · Web UI · 批量处理 · 隐私优先**

[快速开始](#-快速开始) · [功能特性](#-核心特性) · [使用指南](#-详细使用指南) · [Web UI](#-web-ui)

</div>

---

## 🎉 项目介绍

VoiceForge-CLI 是一款轻量级的 AI 语音合成与声音克隆引擎，支持多种 TTS 引擎切换、Web UI 管理、批量文本转语音处理。完全本地运行，零 API 费用，隐私优先。

灵感来源于 GitHub Trending 上的 voicebox 等语音 AI 项目，VoiceForge-CLI 以纯 Python 实现，极低资源占用，适合低配机器和快速部署场景。

## ✨ 核心特性

- 🎙️ **多引擎 TTS** — 支持 Edge TTS（微软免费）和离线 TTS（pyttsx3），一键切换
- 🌐 **Web UI** — 内置深色主题 Web 管理界面，可视化操作
- 📦 **批量处理** — 支持从文件读取文本，批量合成语音
- 🎵 **音频处理** — 格式转换（WAV/MP3/OGG）、音频合并、音量调节
- 💾 **项目管理** — 保存/加载/导出语音合成项目
- 🔒 **隐私优先** — 完全本地运行，无需 API Key
- 💰 **零成本** — 使用免费 TTS 引擎，无任何 API 费用
- 🖥️ **CLI + Web 双模式** — 命令行和 Web 界面双入口
- 🌍 **多语言支持** — 支持中文、英文、日文等 40+ 语言音色

## 🚀 快速开始

### 环境要求

- Python 3.9+
- FFmpeg（音频处理需要）

### 安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/VoiceForge-CLI.git
cd VoiceForge-CLI

# 安装依赖
pip install -r requirements.txt

# 或者使用 pip 安装
pip install -e .
```

### 基本使用

```bash
# 文本转语音（使用默认引擎）
voiceforge speak --text "你好，欢迎使用VoiceForge" --output hello.mp3

# 查看可用音色
voiceforge voices --lang zh-CN

# 使用指定音色合成
voiceforge speak --text "Hello World" --voice en-US-JennyNeural --output hello.mp3

# 调整语速和音量
voiceforge speak --text "快速朗读测试" --rate +30% --volume +20% --output fast.mp3

# 启动 Web UI
voiceforge web --port 8080
```

## 📖 详细使用指南

### CLI 命令大全

| 命令 | 说明 | 示例 |
|------|------|------|
| `speak` | 文本转语音 | `voiceforge speak --text "你好" -o out.mp3` |
| `voices` | 查看可用音色 | `voiceforge voices --lang zh-CN` |
| `preview` | 预览语音 | `voiceforge preview --text "测试" --voice zh-CN-XiaoxiaoNeural` |
| `batch` | 批量合成 | `voiceforge batch --file texts.txt --output-dir ./out` |
| `convert` | 格式转换 | `voiceforge convert --input a.wav --output b.mp3` |
| `merge` | 合并音频 | `voiceforge merge --files a.mp3 b.mp3 --output merged.mp3` |
| `info` | 音频信息 | `voiceforge info --file audio.mp3` |
| `web` | 启动 Web UI | `voiceforge web --host 0.0.0.0 --port 8080` |
| `project` | 项目管理 | `voiceforge project --save myproj --texts "a,b,c"` |
| `version` | 查看版本 | `voiceforge version` |

### 音色参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--voice` | 音色名称 | `zh-CN-XiaoxiaoNeural` |
| `--rate` | 语速调整 | `-50%` ~ `+100%` |
| `--volume` | 音量调整 | `-50%` ~ `+100%` |
| `--pitch` | 音调调整 | `-20Hz` ~ `+20Hz` |
| `--format` | 输出格式 | `mp3`, `wav`, `ogg` |

### 批量处理

```bash
# 从文本文件批量合成
voiceforge batch --file input.txt --output-dir ./output --format mp3

# input.txt 格式（每行一段文本）
# 你好，这是第一段
# 这是第二段内容
# 第三段文本
```

### 项目管理

```bash
# 保存项目
voiceforge project --save myproject --texts "段落一,段落二,段落三" --output-dir ./audio

# 加载项目
voiceforge project --load ./projects/myproject.json

# 列出所有项目
voiceforge project --list --dir ./projects
```

## 🌐 Web UI

启动 Web 界面后，访问 `http://localhost:8080` 即可使用：

- 📝 文本输入与编辑
- 🎤 音色选择与切换
- 🎚️ 语速/音量/音调实时调节
- ▶️ 语音预览播放
- 📦 批量处理面板
- 💾 项目管理面板

```bash
voiceforge web --host 0.0.0.0 --port 8080
```

## 💡 设计思路与迭代规划

### 设计理念
- **极简主义** — 最少依赖，最大功能
- **本地优先** — 无需服务器，隐私安全
- **双模式** — CLI 高效操作 + Web 可视化管理

### 迭代规划
- [ ] v1.1: 声音克隆功能（参考音频 → 复制音色）
- [ ] v1.2: SSML 标记支持（精细控制停顿、重音）
- [ ] v1.3: 插件系统（自定义 TTS 引擎接入）
- [ ] v2.0: 桌面应用（Electron/Tauri 封装）

## 📦 打包与部署

### 使用 PyInstaller 打包

```bash
make build
# 或手动执行
pip install pyinstaller
pyinstaller --onefile --name voiceforge voiceforge/cli.py
```

### Docker 部署

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["voiceforge", "web", "--host", "0.0.0.0", "--port", "8080"]
```

## 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 发起 Pull Request

提交规范遵循 [Angular Convention](https://github.com/angular/angular/blob/master/CONTRIBUTING.md)。

## 📄 开源协议

本项目基于 [MIT License](LICENSE) 开源。

---

<div align="center">

**用 ❤️ 打造 | 由 [gitstq](https://github.com/gitstq) 维护**

</div>
