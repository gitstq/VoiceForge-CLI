"""
音频处理模块

本模块提供了基于pydub的音频处理功能，包括：
- 格式转换（MP3、WAV、OGG、FLAC等）
- 多个音频文件合并
- 音频时长获取
- 音频详细信息获取
- 音量调节

使用示例：
    from voiceforge.audio import AudioProcessor

    processor = AudioProcessor()
    processor.convert_format("input.wav", "output.mp3", "mp3")
    duration = processor.get_duration("output.mp3")
"""

import os
from typing import Any, Dict, List, Optional

from pydub import AudioSegment
from pydub.utils import mediainfo


class AudioProcessor:
    """音频处理器

    封装了pydub库的常用音频处理功能，提供简洁的接口用于
    音频格式转换、合并、信息获取和音量调节等操作。

    注意：
        - 需要安装FFmpeg才能处理MP3等格式
        - 某些格式转换可能需要额外的编解码器

    使用示例：
        processor = AudioProcessor()
        info = processor.get_info("audio.mp3")
        processor.adjust_volume("audio.mp3", "louder.mp3", db_change=5.0)
    """

    # 支持的音频格式
    SUPPORTED_FORMATS: List[str] = ["mp3", "wav", "ogg", "flac", "aac", "m4a", "wma"]

    def convert_format(
        self,
        input_path: str,
        output_path: str,
        format: str,
        bitrate: Optional[str] = None,
    ) -> str:
        """转换音频文件格式

        将输入音频文件从当前格式转换为目标格式。
        支持MP3、WAV、OGG、FLAC、AAC等常见格式。

        参数：
            input_path: 输入音频文件的路径
            output_path: 输出音频文件的路径
            format: 目标格式（如"mp3"、"wav"、"ogg"等）
            bitrate: 可选的比特率（如"192k"），仅对有损格式有效

        返回：
            输出文件的绝对路径

        异常：
            FileNotFoundError: 输入文件不存在
            ValueError: 不支持的格式或输入文件无效
            RuntimeError: 格式转换失败
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"输入文件不存在: {input_path}")

        format = format.lower().strip().replace(".", "")
        if format not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"不支持的音频格式: '{format}'，"
                f"支持的格式: {', '.join(self.SUPPORTED_FORMATS)}"
            )

        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        try:
            audio = AudioSegment.from_file(input_path)

            export_kwargs: Dict[str, Any] = {"format": format}
            if bitrate and format in ("mp3", "ogg", "aac"):
                export_kwargs["bitrate"] = bitrate

            audio.export(output_path, **export_kwargs)
            return os.path.abspath(output_path)
        except Exception as e:
            raise RuntimeError(f"音频格式转换失败: {e}") from e

    def merge_audio(
        self,
        file_list: List[str],
        output_path: str,
        format: str = "mp3",
    ) -> str:
        """合并多个音频文件为一个文件

        按照列表顺序将多个音频文件拼接合并为一个音频文件。

        参数：
            file_list: 要合并的音频文件路径列表（按合并顺序排列）
            output_path: 输出音频文件的路径
            format: 输出格式（默认"mp3"）

        返回：
            输出文件的绝对路径

        异常：
            FileNotFoundError: 输入文件不存在
            ValueError: 文件列表为空
            RuntimeError: 合并失败
        """
        if not file_list:
            raise ValueError("合并文件列表不能为空")

        for f in file_list:
            if not os.path.exists(f):
                raise FileNotFoundError(f"输入文件不存在: {f}")

        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        try:
            combined = AudioSegment.empty()
            for audio_file in file_list:
                segment = AudioSegment.from_file(audio_file)
                combined += segment

            combined.export(output_path, format=format)
            return os.path.abspath(output_path)
        except Exception as e:
            raise RuntimeError(f"音频合并失败: {e}") from e

    def get_duration(self, file_path: str) -> float:
        """获取音频文件的时长

        参数：
            file_path: 音频文件路径

        返回：
            音频时长（秒）

        异常：
            FileNotFoundError: 文件不存在
            RuntimeError: 获取时长失败
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        try:
            audio = AudioSegment.from_file(file_path)
            return len(audio) / 1000.0
        except Exception as e:
            raise RuntimeError(f"获取音频时长失败: {e}") from e

    def get_info(self, file_path: str) -> Dict[str, Any]:
        """获取音频文件的详细信息

        返回音频的格式、采样率、通道数、时长、比特率等信息。

        参数：
            file_path: 音频文件路径

        返回：
            包含以下字段的字典：
                - format: 音频格式
                - sample_rate: 采样率（Hz）
                - channels: 通道数（1=单声道，2=立体声）
                - duration: 时长（秒）
                - bitrate: 比特率（bps）
                - file_size: 文件大小（字节）

        异常：
            FileNotFoundError: 文件不存在
            RuntimeError: 获取信息失败
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        try:
            info = mediainfo(file_path)
            audio = AudioSegment.from_file(file_path)

            return {
                "format": os.path.splitext(file_path)[1].lstrip("."),
                "sample_rate": audio.frame_rate,
                "channels": audio.channels,
                "duration": len(audio) / 1000.0,
                "bitrate": info.get("bit_rate", "unknown"),
                "file_size": os.path.getsize(file_path),
            }
        except Exception as e:
            raise RuntimeError(f"获取音频信息失败: {e}") from e

    def adjust_volume(
        self,
        file_path: str,
        output_path: str,
        db_change: float = 0.0,
    ) -> str:
        """调整音频文件的音量

        参数：
            file_path: 输入音频文件路径
            output_path: 输出音频文件路径
            db_change: 音量变化量（分贝），正值增大音量，负值减小音量

        返回：
            输出文件的绝对路径

        异常：
            FileNotFoundError: 输入文件不存在
            RuntimeError: 音量调节失败
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"输入文件不存在: {file_path}")

        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        try:
            audio = AudioSegment.from_file(file_path)
            adjusted = audio + db_change  # type: ignore[operator]

            # 根据输出文件扩展名确定格式
            ext = os.path.splitext(output_path)[1].lstrip(".")
            export_format = ext if ext else "mp3"

            adjusted.export(output_path, format=export_format)
            return os.path.abspath(output_path)
        except Exception as e:
            raise RuntimeError(f"音量调节失败: {e}") from e
