"""
TTS引擎核心模块

本模块定义了TTS引擎的抽象基类和具体实现，包括：
- TTSEngine：TTS引擎抽象基类，定义统一接口
- EdgeTTSEngine：基于edge-tts的在线TTS引擎，支持多种音色和参数调节
- OfflineTTSEngine：基于pyttsx3的离线TTS引擎
- EngineFactory：工厂模式，根据配置创建对应的引擎实例

使用示例：
    from voiceforge.engine import EngineFactory

    # 创建Edge TTS引擎
    engine = EngineFactory.create_engine("edge")
    engine.speak("你好世界", "hello.mp3", rate="+20%", volume="+10%")

    # 创建离线TTS引擎
    offline_engine = EngineFactory.create_engine("offline")
    offline_engine.speak("你好世界", "hello.wav")
"""

import asyncio
import os
import tempfile
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import edge_tts
import pyttsx3


class TTSEngine(ABC):
    """TTS引擎抽象基类

    定义了所有TTS引擎必须实现的统一接口，
    包括语音合成、音色获取和预览播放功能。

    属性：
        engine_name: 引擎名称标识
    """

    def __init__(self, engine_name: str) -> None:
        """初始化TTS引擎

        参数：
            engine_name: 引擎名称标识字符串
        """
        self.engine_name: str = engine_name

    @abstractmethod
    async def speak(
        self,
        text: str,
        output_file: str,
        **kwargs: Any,
    ) -> str:
        """将文本合成为语音并保存到文件

        参数：
            text: 要合成的文本内容
            output_file: 输出音频文件的路径
            **kwargs: 额外参数（如语速、音量、音调等）

        返回：
            输出文件的绝对路径

        异常：
            NotImplementedError: 子类必须实现此方法
            TTSError: 语音合成过程中发生错误
        """
        raise NotImplementedError("子类必须实现speak方法")

    @abstractmethod
    async def get_voices(self, lang: Optional[str] = None) -> List[Dict[str, str]]:
        """获取可用的音色列表

        参数：
            lang: 可选的语言代码过滤（如"zh-CN"），为None时返回所有音色

        返回：
            音色信息字典列表，每个字典包含name、locale、gender等字段
        """
        raise NotImplementedError("子类必须实现get_voices方法")

    @abstractmethod
    async def preview(self, text: str, **kwargs: Any) -> None:
        """预览语音合成效果（使用临时文件播放）

        参数：
            text: 要预览的文本内容
            **kwargs: 额外参数（如语速、音量、音调等）
        """
        raise NotImplementedError("子类必须实现preview方法")


class EdgeTTSEngine(TTSEngine):
    """基于edge-tts的在线TTS引擎

    使用微软Edge浏览器的在线TTS服务，支持多种语言和音色，
    可调节语速、音量和音调。合成的音频保存为MP3格式。

    支持的参数：
        - rate: 语速调节，格式如"+20%"、"-10%"、"+0%"
        - volume: 音量调节，格式如"+10%"、"-5%"、"+0%"
        - pitch: 音调调节，格式如"+5Hz"、"-5Hz"、"+0Hz"
        - voice: 指定音色名称

    使用示例：
        engine = EdgeTTSEngine()
        await engine.speak("你好", "hello.mp3", rate="+20%", volume="+10%")
        voices = await engine.get_voices("zh-CN")
    """

    # 默认中文音色
    DEFAULT_VOICE: str = "zh-CN-XiaoxiaoNeural"

    def __init__(self) -> None:
        """初始化Edge TTS引擎"""
        super().__init__("edge-tts")
        self._voices_cache: Optional[List[Dict[str, str]]] = None

    async def speak(
        self,
        text: str,
        output_file: str,
        **kwargs: Any,
    ) -> str:
        """使用edge-tts将文本合成为语音

        参数：
            text: 要合成的文本内容
            output_file: 输出MP3文件路径
            **kwargs: 合成参数
                - voice: 音色名称（默认为zh-CN-XiaoxiaoNeural）
                - rate: 语速（如"+20%"）
                - volume: 音量（如"+10%"）
                - pitch: 音调（如"+5Hz"）

        返回：
            输出文件的绝对路径

        异常：
            RuntimeError: 语音合成失败
            ValueError: 文本内容为空
        """
        if not text or not text.strip():
            raise ValueError("合成文本不能为空")

        voice: str = kwargs.get("voice", self.DEFAULT_VOICE)
        rate: str = kwargs.get("rate", "+0%")
        volume: str = kwargs.get("volume", "+0%")
        pitch: str = kwargs.get("pitch", "+0Hz")

        # 确保输出目录存在
        output_dir = os.path.dirname(output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # 如果未指定扩展名，默认添加.mp3
        if not output_file.endswith(".mp3"):
            output_file = output_file + ".mp3"

        try:
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=rate,
                volume=volume,
                pitch=pitch,
            )
            await communicate.save(output_file)
            return os.path.abspath(output_file)
        except Exception as e:
            raise RuntimeError(f"Edge TTS合成失败: {e}") from e

    async def get_voices(self, lang: Optional[str] = None) -> List[Dict[str, str]]:
        """获取edge-tts可用的音色列表

        参数：
            lang: 可选的语言代码过滤（如"zh-CN"），
                  为None时返回所有可用音色

        返回：
            按语言分组的音色信息字典列表，
            每个字典包含name（音色ID）、locale（语言区域）、
            gender（性别）、description（描述）字段

        异常：
            RuntimeError: 获取音色列表失败
        """
        if self._voices_cache is not None and lang is None:
            return self._voices_cache

        try:
            voices_raw = await edge_tts.list_voices()
            voices: List[Dict[str, str]] = []
            for v in voices_raw:
                voice_info: Dict[str, str] = {
                    "name": v.get("ShortName", ""),
                    "locale": v.get("Locale", ""),
                    "gender": v.get("Gender", ""),
                    "description": v.get("FriendlyName", ""),
                }
                voices.append(voice_info)

            self._voices_cache = voices

            if lang:
                voices = [v for v in voices if v["locale"].startswith(lang)]

            return voices
        except Exception as e:
            raise RuntimeError(f"获取音色列表失败: {e}") from e

    async def preview(self, text: str, **kwargs: Any) -> None:
        """使用临时文件预览语音合成效果

        参数：
            text: 要预览的文本内容
            **kwargs: 合成参数（同speak方法）

        异常：
            RuntimeError: 预览失败
        """
        if not text or not text.strip():
            raise ValueError("预览文本不能为空")

        try:
            with tempfile.NamedTemporaryFile(
                suffix=".mp3", delete=False
            ) as tmp_file:
                tmp_path = tmp_file.name

            await self.speak(text, tmp_path, **kwargs)
            print(f"预览音频已生成: {tmp_path}")
            print("请使用系统音频播放器打开该文件进行预览。")
        except Exception as e:
            raise RuntimeError(f"预览失败: {e}") from e


class OfflineTTSEngine(TTSEngine):
    """基于pyttsx3的离线TTS引擎

    使用系统本地TTS引擎进行语音合成，无需网络连接。
    合成的音频保存为WAV格式。

    注意：
        - 需要系统安装TTS引擎（如Windows SAPI、macOS say、Linux espeak）
        - 音色和参数支持取决于系统TTS引擎的能力
        - preview方法在离线模式下直接通过扬声器播放

    使用示例：
        engine = OfflineTTSEngine()
        await engine.speak("你好", "hello.wav")
    """

    def __init__(self) -> None:
        """初始化离线TTS引擎"""
        super().__init__("pyttsx3")
        self._engine: Optional[pyttsx3.Engine] = None

    def _get_engine(self) -> pyttsx3.Engine:
        """获取或创建pyttsx3引擎实例

        返回：
            pyttsx3引擎实例

        异常：
            RuntimeError: 引擎初始化失败
        """
        if self._engine is None:
            try:
                self._engine = pyttsx3.init()
            except Exception as e:
                raise RuntimeError(f"离线TTS引擎初始化失败: {e}") from e
        return self._engine

    async def speak(
        self,
        text: str,
        output_file: str,
        **kwargs: Any,
    ) -> str:
        """使用pyttsx3将文本合成为语音

        参数：
            text: 要合成的文本内容
            output_file: 输出WAV文件路径
            **kwargs: 合成参数
                - voice_id: 音色ID（可选）
                - rate: 语速整数值（可选）

        返回：
            输出文件的绝对路径

        异常：
            RuntimeError: 语音合成失败
            ValueError: 文本内容为空
        """
        if not text or not text.strip():
            raise ValueError("合成文本不能为空")

        # 确保输出目录存在
        output_dir = os.path.dirname(output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # 如果未指定扩展名，默认添加.wav
        if not output_file.endswith(".wav"):
            output_file = output_file + ".wav"

        try:
            engine = self._get_engine()

            # 设置音色
            voice_id = kwargs.get("voice_id")
            if voice_id:
                voices = engine.getProperty("voices")
                for v in voices:
                    if v.id == voice_id:
                        engine.setProperty("voice", v.id)
                        break

            # 设置语速
            rate = kwargs.get("rate")
            if rate is not None:
                engine.setProperty("rate", int(rate))

            engine.save_to_file(text, output_file)
            engine.runAndWait()
            return os.path.abspath(output_file)
        except Exception as e:
            raise RuntimeError(f"离线TTS合成失败: {e}") from e

    async def get_voices(self, lang: Optional[str] = None) -> List[Dict[str, str]]:
        """获取系统可用的离线音色列表

        参数：
            lang: 可选的语言过滤（离线引擎可能不完全支持语言过滤）

        返回：
            音色信息字典列表
        """
        try:
            engine = self._get_engine()
            voices = engine.getProperty("voices")
            result: List[Dict[str, str]] = []
            for v in voices:
                voice_info: Dict[str, str] = {
                    "name": v.id,
                    "locale": "",
                    "gender": "",
                    "description": v.name,
                }
                result.append(voice_info)
            return result
        except Exception as e:
            raise RuntimeError(f"获取离线音色列表失败: {e}") from e

    async def preview(self, text: str, **kwargs: Any) -> None:
        """直接通过扬声器播放预览

        参数：
            text: 要预览的文本内容
            **kwargs: 合成参数（同speak方法）

        异常：
            RuntimeError: 预览播放失败
        """
        if not text or not text.strip():
            raise ValueError("预览文本不能为空")

        try:
            engine = self._get_engine()

            voice_id = kwargs.get("voice_id")
            if voice_id:
                voices = engine.getProperty("voices")
                for v in voices:
                    if v.id == voice_id:
                        engine.setProperty("voice", v.id)
                        break

            rate = kwargs.get("rate")
            if rate is not None:
                engine.setProperty("rate", int(rate))

            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            raise RuntimeError(f"离线预览播放失败: {e}") from e


class EngineFactory:
    """TTS引擎工厂类

    使用工厂模式根据引擎类型创建对应的TTS引擎实例。
    支持的引擎类型：
        - "edge": EdgeTTSEngine（在线，基于edge-tts）
        - "offline": OfflineTTSEngine（离线，基于pyttsx3）

    使用示例：
        engine = EngineFactory.create_engine("edge")
        engine = EngineFactory.create_engine("offline")
    """

    _registry: Dict[str, type] = {
        "edge": EdgeTTSEngine,
        "offline": OfflineTTSEngine,
    }

    @classmethod
    def create_engine(cls, engine_type: str = "edge") -> TTSEngine:
        """根据引擎类型创建TTS引擎实例

        参数：
            engine_type: 引擎类型标识，支持"edge"和"offline"，
                         默认为"edge"

        返回：
            对应的TTS引擎实例

        异常：
            ValueError: 不支持的引擎类型
        """
        engine_type = engine_type.lower().strip()
        if engine_type not in cls._registry:
            supported = ", ".join(cls._registry.keys())
            raise ValueError(
                f"不支持的引擎类型: '{engine_type}'，"
                f"支持的类型: {supported}"
            )
        return cls._registry[engine_type]()

    @classmethod
    def register_engine(cls, engine_type: str, engine_class: type) -> None:
        """注册自定义TTS引擎

        参数：
            engine_type: 引擎类型标识
            engine_class: 引擎类（必须继承TTSEngine）

        异常：
            TypeError: 引擎类不是TTSEngine的子类
        """
        if not issubclass(engine_class, TTSEngine):
            raise TypeError(
                f"引擎类必须继承TTSEngine，"
                f"但'{engine_class.__name__}'不是TTSEngine的子类"
            )
        cls._registry[engine_type.lower()] = engine_class

    @classmethod
    def get_supported_engines(cls) -> List[str]:
        """获取所有支持的引擎类型列表

        返回：
            引擎类型标识字符串列表
        """
        return list(cls._registry.keys())
