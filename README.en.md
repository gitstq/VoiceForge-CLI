<div align="center">

# 🎙️ VoiceForge-CLI

**Lightweight AI Text-to-Speech & Voice Synthesis Engine**

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-orange.svg)](https://github.com/gitstq/VoiceForge-CLI/releases)

[简体中文](README.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md)

<img src="assets/logo.svg" alt="VoiceForge-CLI Logo" width="200"/>

**Zero API Cost · Multi-Engine · Web UI · Batch Processing · Privacy-First**

[Quick Start](#-quick-start) · [Features](#-core-features) · [Guide](#-detailed-usage-guide) · [Web UI](#-web-ui)

</div>

---

## 🎉 About

VoiceForge-CLI is a lightweight AI text-to-speech and voice synthesis engine with multi-engine support, Web UI, and batch processing. Fully local execution, zero API cost, privacy-first.

## ✨ Core Features

- 🎙️ **Multi-Engine TTS** — Edge TTS (free Microsoft) + Offline TTS (pyttsx3)
- 🌐 **Web UI** — Built-in dark theme web management interface
- 📦 **Batch Processing** — Bulk text-to-speech from files
- 🎵 **Audio Processing** — Format conversion (WAV/MP3/OGG), merge, volume adjustment
- 💾 **Project Management** — Save/load/export synthesis projects
- 🔒 **Privacy-First** — Fully local, no API keys required
- 💰 **Zero Cost** — Free TTS engines, no API fees
- 🖥️ **CLI + Web Dual Mode** — Command-line and web interface
- 🌍 **Multi-Language** — 40+ language voices supported

## 🚀 Quick Start

### Requirements
- Python 3.9+
- FFmpeg (for audio processing)

### Installation

```bash
git clone https://github.com/gitstq/VoiceForge-CLI.git
cd VoiceForge-CLI
pip install -r requirements.txt
```

### Basic Usage

```bash
# Text to speech
voiceforge speak --text "Hello, welcome to VoiceForge" --output hello.mp3

# List available voices
voiceforge voices --lang en-US

# With specific voice
voiceforge speak --text "Hello World" --voice en-US-JennyNeural --output hello.mp3

# Adjust rate and volume
voiceforge speak --text "Speed test" --rate +30% --volume +20% --output fast.mp3

# Start Web UI
voiceforge web --port 8080
```

## 📖 Detailed Usage Guide

### CLI Commands

| Command | Description | Example |
|---------|-------------|---------|
| `speak` | Text to speech | `voiceforge speak --text "Hi" -o out.mp3` |
| `voices` | List voices | `voiceforge voices --lang en-US` |
| `preview` | Preview voice | `voiceforge preview --text "test" --voice en-US-JennyNeural` |
| `batch` | Batch synthesis | `voiceforge batch --file texts.txt --output-dir ./out` |
| `convert` | Format conversion | `voiceforge convert --input a.wav --output b.mp3` |
| `merge` | Merge audio | `voiceforge merge --files a.mp3 b.mp3 --output merged.mp3` |
| `info` | Audio info | `voiceforge info --file audio.mp3` |
| `web` | Start Web UI | `voiceforge web --host 0.0.0.0 --port 8080` |
| `project` | Project management | `voiceforge project --save proj --texts "a,b,c"` |
| `version` | Show version | `voiceforge version` |

## 🌐 Web UI

Launch the web interface and visit `http://localhost:8080`:

- 📝 Text input and editing
- 🎤 Voice selection and switching
- 🎚️ Real-time rate/volume/pitch adjustment
- ▶️ Voice preview playback
- 📦 Batch processing panel
- 💾 Project management panel

## 💡 Design & Roadmap

### Design Philosophy
- **Minimalism** — Minimal dependencies, maximum functionality
- **Local-First** — No server needed, privacy secure
- **Dual Mode** — CLI efficiency + Web visualization

### Roadmap
- [ ] v1.1: Voice cloning (reference audio → clone voice)
- [ ] v1.2: SSML support (pause, emphasis control)
- [ ] v1.3: Plugin system (custom TTS engine integration)
- [ ] v2.0: Desktop app (Electron/Tauri)

## 📦 Build & Deploy

### PyInstaller

```bash
make build
```

## 🤝 Contributing

Contributions welcome! Please follow these steps:

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'feat: add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

**Built with ❤️ | Maintained by [gitstq](https://github.com/gitstq)**

</div>
