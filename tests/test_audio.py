"""
音频处理模块测试

测试AudioProcessor的各项功能，使用mock模拟pydub的外部依赖。
"""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from voiceforge.audio import AudioProcessor


class TestAudioProcessor:
    """AudioProcessor音频处理器测试"""

    def test_init(self) -> None:
        """测试AudioProcessor初始化"""
        processor = AudioProcessor()
        assert "mp3" in processor.SUPPORTED_FORMATS
        assert "wav" in processor.SUPPORTED_FORMATS
        assert "ogg" in processor.SUPPORTED_FORMATS

    def test_supported_formats(self) -> None:
        """测试支持的格式列表"""
        formats = AudioProcessor.SUPPORTED_FORMATS
        assert "mp3" in formats
        assert "wav" in formats
        assert "flac" in formats
        assert "aac" in formats
        assert "m4a" in formats

    def test_convert_format_file_not_found(self) -> None:
        """测试转换不存在的文件抛出FileNotFoundError"""
        processor = AudioProcessor()
        with pytest.raises(FileNotFoundError, match="输入文件不存在"):
            processor.convert_format("nonexistent.wav", "output.mp3", "mp3")

    def test_convert_format_unsupported_format(self) -> None:
        """测试不支持的格式抛出ValueError"""
        processor = AudioProcessor()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            with pytest.raises(ValueError, match="不支持的音频格式"):
                processor.convert_format(tmp_path, "output.xyz", "xyz")
        finally:
            os.unlink(tmp_path)

    def test_convert_format_success(self) -> None:
        """测试格式转换成功"""
        processor = AudioProcessor()

        mock_audio = MagicMock()
        mock_audio.export = MagicMock()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.mp3")

            with patch("voiceforge.audio.AudioSegment.from_file", return_value=mock_audio):
                result = processor.convert_format(tmp_path, output_path, "mp3")

            assert result.endswith("output.mp3")
            mock_audio.export.assert_called_once()

        os.unlink(tmp_path)

    def test_convert_format_with_bitrate(self) -> None:
        """测试带比特率的格式转换"""
        processor = AudioProcessor()

        mock_audio = MagicMock()
        mock_audio.export = MagicMock()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "output.mp3")

            with patch("voiceforge.audio.AudioSegment.from_file", return_value=mock_audio):
                processor.convert_format(tmp_path, output_path, "mp3", bitrate="192k")

            mock_audio.export.assert_called_once()
            call_kwargs = mock_audio.export.call_args[1]
            assert call_kwargs["bitrate"] == "192k"

        os.unlink(tmp_path)

    def test_convert_format_creates_directory(self) -> None:
        """测试转换时自动创建输出目录"""
        processor = AudioProcessor()

        mock_audio = MagicMock()
        mock_audio.export = MagicMock()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "subdir", "output.mp3")

            with patch("voiceforge.audio.AudioSegment.from_file", return_value=mock_audio):
                processor.convert_format(tmp_path, output_path, "mp3")

            assert os.path.exists(os.path.dirname(output_path))

        os.unlink(tmp_path)

    def test_merge_audio_empty_list_raises_error(self) -> None:
        """测试空文件列表抛出ValueError"""
        processor = AudioProcessor()
        with pytest.raises(ValueError, match="合并文件列表不能为空"):
            processor.merge_audio([], "output.mp3")

    def test_merge_audio_file_not_found(self) -> None:
        """测试合并不存在的文件抛出FileNotFoundError"""
        processor = AudioProcessor()
        with pytest.raises(FileNotFoundError, match="输入文件不存在"):
            processor.merge_audio(["nonexistent.mp3"], "output.mp3")

    def test_merge_audio_success(self) -> None:
        """测试音频合并成功"""
        processor = AudioProcessor()

        mock_segment1 = MagicMock()
        mock_segment2 = MagicMock()
        mock_empty = MagicMock()
        mock_empty.__iadd__ = MagicMock(return_value=mock_empty)
        mock_empty.export = MagicMock()

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp1:
            tmp1_path = tmp1.name
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp2:
            tmp2_path = tmp2.name

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "merged.mp3")

            with patch("voiceforge.audio.AudioSegment.empty", return_value=mock_empty), \
                 patch("voiceforge.audio.AudioSegment.from_file", side_effect=[mock_segment1, mock_segment2]):
                result = processor.merge_audio([tmp1_path, tmp2_path], output_path)

            assert result.endswith("merged.mp3")
            mock_empty.export.assert_called_once()

        os.unlink(tmp1_path)
        os.unlink(tmp2_path)

    def test_get_duration_file_not_found(self) -> None:
        """测试获取不存在文件的时长抛出FileNotFoundError"""
        processor = AudioProcessor()
        with pytest.raises(FileNotFoundError, match="文件不存在"):
            processor.get_duration("nonexistent.mp3")

    def test_get_duration_success(self) -> None:
        """测试获取音频时长成功"""
        processor = AudioProcessor()

        mock_audio = MagicMock()
        mock_audio.__len__ = MagicMock(return_value=5000)  # 5秒

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = tmp.name

        with patch("voiceforge.audio.AudioSegment.from_file", return_value=mock_audio):
            duration = processor.get_duration(tmp_path)

        assert duration == 5.0
        os.unlink(tmp_path)

    def test_get_info_file_not_found(self) -> None:
        """测试获取不存在文件的信息抛出FileNotFoundError"""
        processor = AudioProcessor()
        with pytest.raises(FileNotFoundError, match="文件不存在"):
            processor.get_info("nonexistent.mp3")

    def test_get_info_success(self) -> None:
        """测试获取音频信息成功"""
        processor = AudioProcessor()

        mock_audio = MagicMock()
        mock_audio.frame_rate = 44100
        mock_audio.channels = 2
        mock_audio.__len__ = MagicMock(return_value=3000)

        mock_media_info = {
            "bit_rate": "128000",
        }

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = tmp.name

        with patch("voiceforge.audio.AudioSegment.from_file", return_value=mock_audio), \
             patch("voiceforge.audio.mediainfo", return_value=mock_media_info):
            info = processor.get_info(tmp_path)

        assert info["format"] == "mp3"
        assert info["sample_rate"] == 44100
        assert info["channels"] == 2
        assert info["duration"] == 3.0
        assert info["bitrate"] == "128000"
        assert "file_size" in info
        os.unlink(tmp_path)

    def test_adjust_volume_file_not_found(self) -> None:
        """测试调整不存在文件的音量抛出FileNotFoundError"""
        processor = AudioProcessor()
        with pytest.raises(FileNotFoundError, match="输入文件不存在"):
            processor.adjust_volume("nonexistent.mp3", "output.mp3", 5.0)

    def test_adjust_volume_success(self) -> None:
        """测试音量调节成功"""
        processor = AudioProcessor()

        mock_audio = MagicMock()
        mock_adjusted = MagicMock()
        mock_adjusted.export = MagicMock()
        mock_audio.__add__ = MagicMock(return_value=mock_adjusted)

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = tmp.name

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "louder.mp3")

            with patch("voiceforge.audio.AudioSegment.from_file", return_value=mock_audio):
                result = processor.adjust_volume(tmp_path, output_path, 5.0)

            assert result.endswith("louder.mp3")
            mock_audio.__add__.assert_called_once_with(5.0)
            mock_adjusted.export.assert_called_once()

        os.unlink(tmp_path)

    def test_adjust_volume_negative_db(self) -> None:
        """测试负分贝音量调节"""
        processor = AudioProcessor()

        mock_audio = MagicMock()
        mock_adjusted = MagicMock()
        mock_adjusted.export = MagicMock()
        mock_audio.__add__ = MagicMock(return_value=mock_adjusted)

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = tmp.name

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "quieter.mp3")

            with patch("voiceforge.audio.AudioSegment.from_file", return_value=mock_audio):
                result = processor.adjust_volume(tmp_path, output_path, -10.0)

            mock_audio.__add__.assert_called_once_with(-10.0)

        os.unlink(tmp_path)

    def test_adjust_volume_creates_directory(self) -> None:
        """测试音量调节时自动创建输出目录"""
        processor = AudioProcessor()

        mock_audio = MagicMock()
        mock_adjusted = MagicMock()
        mock_adjusted.export = MagicMock()
        mock_audio.__add__ = MagicMock(return_value=mock_adjusted)

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = tmp.name

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "subdir", "adjusted.mp3")

            with patch("voiceforge.audio.AudioSegment.from_file", return_value=mock_audio):
                processor.adjust_volume(tmp_path, output_path, 3.0)

            assert os.path.exists(os.path.dirname(output_path))

        os.unlink(tmp_path)
