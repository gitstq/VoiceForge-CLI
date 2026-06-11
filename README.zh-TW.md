<div align="center">

# 🎙️ VoiceForge-CLI

**輕量級 AI 語音合成與聲音克隆引擎**

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-orange.svg)](https://github.com/gitstq/VoiceForge-CLI/releases)

[简体中文](README.md) | [English](README.en.md) | [日本語](README.ja.md)

<img src="assets/logo.svg" alt="VoiceForge-CLI Logo" width="200"/>

**零 API 費用 · 多引擎切換 · Web UI · 批次處理 · 隱私優先**

</div>

---

## 🎉 專案介紹

VoiceForge-CLI 是一款輕量級的 AI 語音合成與聲音克隆引擎，支援多種 TTS 引擎切換、Web UI 管理、批次文本轉語音處理。完全本地運行，零 API 費用，隱私優先。

## ✨ 核心特性

- 🎙️ **多引擎 TTS** — 支援 Edge TTS（微軟免費）和離線 TTS（pyttsx3），一鍵切換
- 🌐 **Web UI** — 內建深色主題 Web 管理介面，視覺化操作
- 📦 **批次處理** — 支援從檔案讀取文本，批次合成語音
- 🎵 **音訊處理** — 格式轉換（WAV/MP3/OGG）、音訊合併、音量調節
- 💾 **專案管理** — 儲存/載入/匯出語音合成專案
- 🔒 **隱私優先** — 完全本地運行，無需 API Key
- 💰 **零成本** — 使用免費 TTS 引擎，無任何 API 費用
- 🖥️ **CLI + Web 雙模式** — 命令列和 Web 介面雙入口
- 🌍 **多語言支援** — 支援中文、英文、日文等 40+ 語言音色

## 🚀 快速開始

### 環境需求
- Python 3.9+
- FFmpeg（音訊處理需要）

### 安裝

```bash
git clone https://github.com/gitstq/VoiceForge-CLI.git
cd VoiceForge-CLI
pip install -r requirements.txt
```

### 基本使用

```bash
# 文本轉語音
voiceforge speak --text "你好，歡迎使用VoiceForge" --output hello.mp3

# 查看可用音色
voiceforge voices --lang zh-TW

# 啟動 Web UI
voiceforge web --port 8080
```

## 📖 詳細使用指南

### CLI 命令大全

| 命令 | 說明 | 範例 |
|------|------|------|
| `speak` | 文本轉語音 | `voiceforge speak --text "你好" -o out.mp3` |
| `voices` | 查看可用音色 | `voiceforge voices --lang zh-TW` |
| `preview` | 預覽語音 | `voiceforge preview --text "測試"` |
| `batch` | 批次合成 | `voiceforge batch --file texts.txt --output-dir ./out` |
| `convert` | 格式轉換 | `voiceforge convert --input a.wav --output b.mp3` |
| `merge` | 合併音訊 | `voiceforge merge --files a.mp3 b.mp3 --output merged.mp3` |
| `info` | 音訊資訊 | `voiceforge info --file audio.mp3` |
| `web` | 啟動 Web UI | `voiceforge web --host 0.0.0.0 --port 8080` |
| `project` | 專案管理 | `voiceforge project --save proj --texts "a,b,c"` |
| `version` | 查看版本 | `voiceforge version` |

## 💡 設計思路與迭代規劃

### 設計理念
- **極簡主義** — 最少依賴，最大功能
- **本地優先** — 無需伺服器，隱私安全
- **雙模式** — CLI 高效操作 + Web 視覺化管理

### 迭代規劃
- [ ] v1.1: 聲音克隆功能
- [ ] v1.2: SSML 標記支援
- [ ] v1.3: 插件系統
- [ ] v2.0: 桌面應用

## 🤝 貢獻指南

1. Fork 本倉庫
2. 建立特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 發起 Pull Request

## 📄 開源協議

本專案基於 [MIT License](LICENSE) 開源。

---

<div align="center">

**用 ❤️ 打造 | 由 [gitstq](https://github.com/gitstq) 維護**

</div>
