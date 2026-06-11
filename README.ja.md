<div align="center">

# 🎙️ VoiceForge-CLI

**軽量級 AI 音声合成＆ボイスクローンエンジン**

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-orange.svg)](https://github.com/gitstq/VoiceForge-CLI/releases)

[简体中文](README.md) | [English](README.en.md) | [繁體中文](README.zh-TW.md)

<img src="assets/logo.svg" alt="VoiceForge-CLI Logo" width="200"/>

**ゼロAPIコスト · マルチエンジン · Web UI · バッチ処理 · プライバシー第一**

</div>

---

## 🎉 プロジェクト紹介

VoiceForge-CLIは、軽量級AI音声合成＆ボイスクローンエンジンです。複数のTTSエンジン切り替え、Web UI管理、バッチテキスト音声変換をサポート。完全ローカル実行、ゼロAPIコスト、プライバシー第一。

## ✨ コア機能

- 🎙️ **マルチエンジンTTS** — Edge TTS + オフラインTTS
- 🌐 **Web UI** — ダークテーマWeb管理インターフェース内蔵
- 📦 **バッチ処理** — ファイルからテキストを読み込み一括音声合成
- 🎵 **音声処理** — フォーマット変換（WAV/MP3/OGG）、結合、音量調整
- 💾 **プロジェクト管理** — 保存/読み込み/エクスポート
- 🔒 **プライバシー第一** — 完全ローカル、APIキー不要
- 💰 **ゼロコスト** — 無料TTSエンジン
- 🖥️ **CLI + Web デュアルモード** — コマンドラインとWebインターフェース
- 🌍 **多言語対応** — 40+言語の音声をサポート

## 🚀 クイックスタート

### 動作環境
- Python 3.9+
- FFmpeg（音声処理に必要）

### インストール

```bash
git clone https://github.com/gitstq/VoiceForge-CLI.git
cd VoiceForge-CLI
pip install -r requirements.txt
```

### 基本的な使い方

```bash
# テキストから音声合成
voiceforge speak --text "こんにちは、VoiceForgeへようこそ" --output hello.mp3

# 利用可能な音声を一覧表示
voiceforge voices --lang ja-JP

# Web UIを起動
voiceforge web --port 8080
```

## 📖 詳細ガイド

### CLIコマンド一覧

| コマンド | 説明 | 例 |
|---------|------|-----|
| `speak` | テキスト音声変換 | `voiceforge speak --text "こんにちは" -o out.mp3` |
| `voices` | 音声一覧 | `voiceforge voices --lang ja-JP` |
| `batch` | バッチ合成 | `voiceforge batch --file texts.txt --output-dir ./out` |
| `convert` | フォーマット変換 | `voiceforge convert --input a.wav --output b.mp3` |
| `merge` | 音声結合 | `voiceforge merge --files a.mp3 b.mp3 --output merged.mp3` |
| `web` | Web UI起動 | `voiceforge web --port 8080` |

## 💡 設計思想

- **ミニマリズム** — 最小依存、最大機能
- **ローカルファースト** — サーバー不要、プライバシー安全
- **デュアルモード** — CLI効率 + Web可視化

### ロードマップ
- [ ] v1.1: ボイスクローン機能
- [ ] v1.2: SSMLサポート
- [ ] v1.3: プラグインシステム
- [ ] v2.0: デスクトップアプリ

## 🤝 コントリビュート

1. リポジトリをFork
2. フィーチャーブランチを作成
3. 変更をコミット
4. ブランチにプッシュ
5. Pull Requestを作成

## 📄 ライセンス

[MIT License](LICENSE)に基づいてオープンソース化されています。

---

<div align="center">

**❤️ で作られました | [gitstq](https://github.com/gitstq) によるメンテナンス**

</div>
