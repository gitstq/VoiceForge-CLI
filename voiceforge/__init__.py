"""
VoiceForge - 轻量级AI语音合成与声音克隆CLI工具

本包提供了基于edge-tts和pyttsx3的文本转语音功能，
支持在线和离线TTS引擎、音频处理、批量合成、项目管理以及Web UI界面。

典型用法：
    from voiceforge.engine import EngineFactory
    engine = EngineFactory.create_engine("edge")
    engine.speak("你好世界", "output.mp3")
"""

__version__ = "1.0.0"
"""VoiceForge的版本号"""

__author__ = "VoiceForge Team"
"""VoiceForge的开发团队"""

__description__ = "轻量级AI语音合成与声音克隆CLI工具"
"""VoiceForge的项目描述"""
