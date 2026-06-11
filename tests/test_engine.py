"""
TTS引擎测试模块

测试EdgeTTSEngine和EngineFactory的基本功能。
使用mock模拟edge-tts和pyttsx3的外部依赖，确保测试不依赖网络和系统TTS引擎。
"""

import os
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from voiceforge.engine import EdgeTTSEngine, EngineFactory, OfflineTTSEngine, TTSEngine


class TestTTSEngine:
    """TTSEngine抽象基类测试"""

    def test_cannot_instantiate_abstract(self) -> None:
        """验证TTSEngine抽象基类不能直接实例化"""
        with pytest.raises(TypeError):
            TTSEngine("test")  # type: ignore[abstract]

    def test_subclass_must_implement_speak(self) -> None:
        """验证子类必须实现speak方法"""
        class IncompleteEngine(TTSEngine):
            async def get_voices(self, lang=None):
                return []
            async def preview(self, text, **kwargs):
                pass

        with pytest.raises(TypeError):
            IncompleteEngine("test")  # type: ignore[abstract]


class TestEdgeTTSEngine:
    """EdgeTTSEngine测试"""

    def test_init(self) -> None:
        """测试EdgeTTSEngine初始化"""
        engine = EdgeTTSEngine()
        assert engine.engine_name == "edge-tts"
        assert engine._voices_cache is None

    def test_default_voice(self) -> None:
        """测试默认音色设置"""
        assert EdgeTTSEngine.DEFAULT_VOICE == "zh-CN-XiaoxiaoNeural"

    @pytest.mark.asyncio
    async def test_speak_empty_text_raises_error(self) -> None:
        """测试空文本抛出ValueError"""
        engine = EdgeTTSEngine()
        with pytest.raises(ValueError, match="合成文本不能为空"):
            await engine.speak("", "output.mp3")

    @pytest.mark.asyncio
    async def test_speak_whitespace_text_raises_error(self) -> None:
        """测试纯空白文本抛出ValueError"""
        engine = EdgeTTSEngine()
        with pytest.raises(ValueError, match="合成文本不能为空"):
            await engine.speak("   ", "output.mp3")

    @pytest.mark.asyncio
    async def test_speak_success(self) -> None:
        """测试语音合成成功"""
        engine = EdgeTTSEngine()

        mock_communicate = MagicMock()
        mock_communicate.save = AsyncMock()

        with patch("voiceforge.engine.edge_tts.Communicate", return_value=mock_communicate):
            result = await engine.speak("你好世界", "output.mp3")

        assert result.endswith("output.mp3")
        mock_communicate.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_speak_with_parameters(self) -> None:
        """测试带参数的语音合成"""
        engine = EdgeTTSEngine()

        mock_communicate = MagicMock()
        mock_communicate.save = AsyncMock()

        with patch("voiceforge.engine.edge_tts.Communicate", return_value=mock_communicate) as mock_cls:
            await engine.speak(
                "测试",
                "test.mp3",
                voice="zh-CN-YunxiNeural",
                rate="+20%",
                volume="+10%",
                pitch="+5Hz",
            )

        mock_cls.assert_called_once_with(
            text="测试",
            voice="zh-CN-YunxiNeural",
            rate="+20%",
            volume="+10%",
            pitch="+5Hz",
        )

    @pytest.mark.asyncio
    async def test_speak_creates_directory(self) -> None:
        """测试合成时自动创建输出目录"""
        engine = EdgeTTSEngine()

        mock_communicate = MagicMock()
        mock_communicate.save = AsyncMock()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "subdir", "test", "output.mp3")

            with patch("voiceforge.engine.edge_tts.Communicate", return_value=mock_communicate):
                result = await engine.speak("测试", output_path)

            assert os.path.exists(os.path.dirname(output_path))

    @pytest.mark.asyncio
    async def test_speak_auto_append_extension(self) -> None:
        """测试自动添加.mp3扩展名"""
        engine = EdgeTTSEngine()

        mock_communicate = MagicMock()
        mock_communicate.save = AsyncMock()

        with patch("voiceforge.engine.edge_tts.Communicate", return_value=mock_communicate):
            result = await engine.speak("测试", "output")

        assert result.endswith("output.mp3")

    @pytest.mark.asyncio
    async def test_speak_error_handling(self) -> None:
        """测试合成失败时的错误处理"""
        engine = EdgeTTSEngine()

        with patch("voiceforge.engine.edge_tts.Communicate", side_effect=Exception("网络错误")):
            with pytest.raises(RuntimeError, match="Edge TTS合成失败"):
                await engine.speak("测试", "output.mp3")

    @pytest.mark.asyncio
    async def test_get_voices_success(self) -> None:
        """测试获取音色列表成功"""
        engine = EdgeTTSEngine()

        mock_voices = [
            {
                "ShortName": "zh-CN-XiaoxiaoNeural",
                "Locale": "zh-CN",
                "Gender": "Female",
                "FriendlyName": "晓晓",
            },
            {
                "ShortName": "zh-CN-YunxiNeural",
                "Locale": "zh-CN",
                "Gender": "Male",
                "FriendlyName": "云希",
            },
        ]

        with patch("voiceforge.engine.edge_tts.list_voices", new_callable=AsyncMock, return_value=mock_voices):
            voices = await engine.get_voices()

        assert len(voices) == 2
        assert voices[0]["name"] == "zh-CN-XiaoxiaoNeural"
        assert voices[0]["locale"] == "zh-CN"
        assert voices[0]["gender"] == "Female"
        assert voices[1]["name"] == "zh-CN-YunxiNeural"

    @pytest.mark.asyncio
    async def test_get_voices_with_lang_filter(self) -> None:
        """测试按语言过滤音色列表"""
        engine = EdgeTTSEngine()

        mock_voices = [
            {"ShortName": "zh-CN-XiaoxiaoNeural", "Locale": "zh-CN", "Gender": "Female", "FriendlyName": "晓晓"},
            {"ShortName": "en-US-JennyNeural", "Locale": "en-US", "Gender": "Female", "FriendlyName": "Jenny"},
        ]

        with patch("voiceforge.engine.edge_tts.list_voices", new_callable=AsyncMock, return_value=mock_voices):
            voices = await engine.get_voices(lang="zh-CN")

        assert len(voices) == 1
        assert voices[0]["locale"] == "zh-CN"

    @pytest.mark.asyncio
    async def test_get_voices_caching(self) -> None:
        """测试音色列表缓存功能"""
        engine = EdgeTTSEngine()

        mock_voices = [
            {"ShortName": "zh-CN-XiaoxiaoNeural", "Locale": "zh-CN", "Gender": "Female", "FriendlyName": "晓晓"},
        ]

        with patch("voiceforge.engine.edge_tts.list_voices", new_callable=AsyncMock, return_value=mock_voices) as mock_list:
            # 第一次调用
            voices1 = await engine.get_voices()
            # 第二次调用（应该使用缓存）
            voices2 = await engine.get_voices()

        assert len(voices1) == len(voices2)
        # list_voices应该只被调用一次（缓存生效）
        mock_list.assert_called_once()

    @pytest.mark.asyncio
    async def test_preview_empty_text_raises_error(self) -> None:
        """测试预览空文本抛出ValueError"""
        engine = EdgeTTSEngine()
        with pytest.raises(ValueError, match="预览文本不能为空"):
            await engine.preview("")

    @pytest.mark.asyncio
    async def test_preview_success(self) -> None:
        """测试预览功能成功"""
        engine = EdgeTTSEngine()

        mock_communicate = MagicMock()
        mock_communicate.save = AsyncMock()

        with patch("voiceforge.engine.edge_tts.Communicate", return_value=mock_communicate):
            await engine.preview("测试预览")

        mock_communicate.save.assert_called_once()


class TestOfflineTTSEngine:
    """OfflineTTSEngine测试"""

    def test_init(self) -> None:
        """测试离线引擎初始化"""
        engine = OfflineTTSEngine()
        assert engine.engine_name == "pyttsx3"
        assert engine._engine is None

    @pytest.mark.asyncio
    async def test_speak_empty_text_raises_error(self) -> None:
        """测试空文本抛出ValueError"""
        engine = OfflineTTSEngine()
        with pytest.raises(ValueError, match="合成文本不能为空"):
            await engine.speak("", "output.wav")

    @pytest.mark.asyncio
    async def test_speak_success(self) -> None:
        """测试离线合成成功"""
        engine = OfflineTTSEngine()

        mock_engine = MagicMock()
        mock_engine.save_to_file = MagicMock()
        mock_engine.runAndWait = MagicMock()

        with patch("voiceforge.engine.pyttsx3.init", return_value=mock_engine):
            result = await engine.speak("测试", "output.wav")

        assert result.endswith("output.wav")
        mock_engine.save_to_file.assert_called_once_with("测试", "output.wav")
        mock_engine.runAndWait.assert_called_once()

    @pytest.mark.asyncio
    async def test_speak_auto_append_extension(self) -> None:
        """测试自动添加.wav扩展名"""
        engine = OfflineTTSEngine()

        mock_engine = MagicMock()
        mock_engine.save_to_file = MagicMock()
        mock_engine.runAndWait = MagicMock()

        with patch("voiceforge.engine.pyttsx3.init", return_value=mock_engine):
            result = await engine.speak("测试", "output")

        assert result.endswith("output.wav")

    @pytest.mark.asyncio
    async def test_get_voices(self) -> None:
        """测试获取离线音色列表"""
        engine = OfflineTTSEngine()

        mock_engine = MagicMock()
        mock_voice = MagicMock()
        mock_voice.id = "voice_id_1"
        mock_voice.name = "测试音色"
        mock_engine.getProperty.return_value = [mock_voice]

        with patch("voiceforge.engine.pyttsx3.init", return_value=mock_engine):
            voices = await engine.get_voices()

        assert len(voices) == 1
        assert voices[0]["name"] == "voice_id_1"
        assert voices[0]["description"] == "测试音色"

    @pytest.mark.asyncio
    async def test_preview(self) -> None:
        """测试离线预览功能"""
        engine = OfflineTTSEngine()

        mock_engine = MagicMock()
        mock_engine.say = MagicMock()
        mock_engine.runAndWait = MagicMock()

        with patch("voiceforge.engine.pyttsx3.init", return_value=mock_engine):
            await engine.preview("测试预览")

        mock_engine.say.assert_called_once_with("测试预览")
        mock_engine.runAndWait.assert_called_once()


class TestEngineFactory:
    """EngineFactory工厂类测试"""

    def test_create_edge_engine(self) -> None:
        """测试创建Edge TTS引擎"""
        engine = EngineFactory.create_engine("edge")
        assert isinstance(engine, EdgeTTSEngine)
        assert engine.engine_name == "edge-tts"

    def test_create_offline_engine(self) -> None:
        """测试创建离线TTS引擎"""
        engine = EngineFactory.create_engine("offline")
        assert isinstance(engine, OfflineTTSEngine)
        assert engine.engine_name == "pyttsx3"

    def test_create_default_engine(self) -> None:
        """测试默认创建Edge TTS引擎"""
        engine = EngineFactory.create_engine()
        assert isinstance(engine, EdgeTTSEngine)

    def test_create_unsupported_engine_raises_error(self) -> None:
        """测试创建不支持的引擎类型抛出ValueError"""
        with pytest.raises(ValueError, match="不支持的引擎类型"):
            EngineFactory.create_engine("unsupported")

    def test_create_engine_case_insensitive(self) -> None:
        """测试引擎类型大小写不敏感"""
        engine = EngineFactory.create_engine("EDGE")
        assert isinstance(engine, EdgeTTSEngine)

        engine = EngineFactory.create_engine("Offline")
        assert isinstance(engine, OfflineTTSEngine)

    def test_register_custom_engine(self) -> None:
        """测试注册自定义引擎"""
        class CustomEngine(TTSEngine):
            def __init__(self):
                super().__init__("custom-engine")

            async def speak(self, text, output_file, **kwargs):
                return output_file
            async def get_voices(self, lang=None):
                return []
            async def preview(self, text, **kwargs):
                pass

        EngineFactory.register_engine("custom", CustomEngine)
        engine = EngineFactory.create_engine("custom")
        assert isinstance(engine, CustomEngine)

        # 清理：移除自定义注册
        EngineFactory._registry.pop("custom", None)

    def test_register_non_tts_engine_raises_error(self) -> None:
        """测试注册非TTSEngine子类抛出TypeError"""
        class NotAnEngine:
            pass

        with pytest.raises(TypeError, match="引擎类必须继承TTSEngine"):
            EngineFactory.register_engine("bad", NotAnEngine)  # type: ignore[arg-type]

    def test_get_supported_engines(self) -> None:
        """测试获取支持的引擎类型列表"""
        engines = EngineFactory.get_supported_engines()
        assert "edge" in engines
        assert "offline" in engines
