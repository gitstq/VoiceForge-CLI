"""
批量处理模块

本模块提供了批量文本转语音的功能，支持：
- 从文本列表批量合成语音
- 从文件读取文本并批量处理（支持按段落或按行分割）
- 进度回调通知

使用示例：
    from voiceforge.batch import BatchProcessor
    from voiceforge.engine import EngineFactory

    engine = EngineFactory.create_engine("edge")
    processor = BatchProcessor()
    results = await processor.process_texts(
        texts=["你好", "世界"],
        engine=engine,
        output_dir="./output"
    )
"""

import os
from typing import Any, Callable, Dict, List, Optional

from voiceforge.engine import TTSEngine


class BatchProcessor:
    """批量语音合成处理器

    支持从文本列表或文件中批量合成语音，并提供进度回调功能。

    命名模式（naming参数）：
        - "index": 使用数字索引命名（如 001.mp3, 002.mp3）
        - "text": 使用文本内容的前20个字符命名
        - "prefix_index": 使用前缀+索引命名（需额外指定prefix参数）

    回调函数签名：
        callback(current_index, total_count, text, output_file) -> None

    使用示例：
        processor = BatchProcessor()

        # 定义进度回调
        def on_progress(index, total, text, output_file):
            print(f"[{index}/{total}] {text[:20]}... -> {output_file}")

        results = await processor.process_texts(
            texts=["第一段", "第二段", "第三段"],
            engine=engine,
            output_dir="./output",
            callback=on_progress
        )
    """

    def __init__(self) -> None:
        """初始化批量处理器"""
        self._results: List[Dict[str, Any]] = []

    async def process_texts(
        self,
        texts: List[str],
        engine: TTSEngine,
        output_dir: str,
        naming: str = "index",
        prefix: str = "speech",
        format: str = "mp3",
        callback: Optional[Callable[[int, int, str, str], None]] = None,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """批量将文本列表合成为语音文件

        参数：
            texts: 要合成的文本列表
            engine: TTS引擎实例
            output_dir: 输出目录路径
            naming: 文件命名模式，支持"index"、"text"、"prefix_index"
            prefix: 前缀命名时的前缀字符串（默认"speech"）
            format: 输出音频格式（默认"mp3"）
            callback: 可选的进度回调函数
            **kwargs: 传递给引擎speak方法的额外参数

        返回：
            合成结果列表，每个元素为包含text、output_file、success、error字段的字典

        异常：
            ValueError: 文本列表为空或引擎实例无效
        """
        if not texts:
            raise ValueError("文本列表不能为空")
        if engine is None:
            raise ValueError("引擎实例不能为None")

        os.makedirs(output_dir, exist_ok=True)
        results: List[Dict[str, Any]] = []
        total = len(texts)

        for i, text in enumerate(texts):
            text = text.strip()
            if not text:
                results.append({
                    "text": "",
                    "output_file": "",
                    "success": False,
                    "error": "文本内容为空，已跳过",
                })
                continue

            # 生成输出文件名
            filename = self._generate_filename(text, i, naming, prefix, format)
            output_file = os.path.join(output_dir, filename)

            try:
                result_path = await engine.speak(text, output_file, **kwargs)
                results.append({
                    "text": text,
                    "output_file": result_path,
                    "success": True,
                    "error": None,
                })
            except Exception as e:
                results.append({
                    "text": text,
                    "output_file": output_file,
                    "success": False,
                    "error": str(e),
                })

            # 触发进度回调
            if callback:
                try:
                    callback(i + 1, total, text, output_file)
                except Exception:
                    # 回调异常不影响主流程
                    pass

        self._results = results
        return results

    async def process_file(
        self,
        input_file: str,
        engine: TTSEngine,
        output_dir: str,
        split_by: str = "paragraph",
        naming: str = "index",
        format: str = "mp3",
        callback: Optional[Callable[[int, int, str, str], None]] = None,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """从文件读取文本并批量合成语音

        支持按段落（空行分隔）或按行分割文本。

        参数：
            input_file: 输入文本文件路径
            engine: TTS引擎实例
            output_dir: 输出目录路径
            split_by: 文本分割方式，"paragraph"（按段落）或"line"（按行）
            naming: 文件命名模式
            format: 输出音频格式
            callback: 可选的进度回调函数
            **kwargs: 传递给引擎speak方法的额外参数

        返回：
            合成结果列表

        异常：
            FileNotFoundError: 输入文件不存在
            ValueError: 不支持的分割方式
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"输入文件不存在: {input_file}")

        try:
            with open(input_file, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            raise RuntimeError(f"读取文件失败: {e}") from e

        # 根据分割方式拆分文本
        if split_by == "paragraph":
            texts = [t.strip() for t in content.split("\n\n") if t.strip()]
        elif split_by == "line":
            texts = [t.strip() for t in content.split("\n") if t.strip()]
        else:
            raise ValueError(
                f"不支持的分割方式: '{split_by}'，"
                f"支持: 'paragraph', 'line'"
            )

        if not texts:
            raise ValueError("文件中没有有效的文本内容")

        return await self.process_texts(
            texts=texts,
            engine=engine,
            output_dir=output_dir,
            naming=naming,
            format=format,
            callback=callback,
            **kwargs,
        )

    def _generate_filename(
        self,
        text: str,
        index: int,
        naming: str,
        prefix: str,
        format: str,
    ) -> str:
        """根据命名模式生成输出文件名

        参数：
            text: 文本内容
            index: 当前索引（从0开始）
            naming: 命名模式
            prefix: 前缀字符串
            format: 文件格式

        返回：
            生成的文件名字符串
        """
        ext = format if format.startswith(".") else f".{format}"

        if naming == "index":
            return f"{index + 1:03d}{ext}"
        elif naming == "text":
            # 使用文本前20个字符，去除不安全字符
            safe_text = "".join(
                c for c in text[:20] if c.isalnum() or c in ("_", "-")
            )
            return f"{safe_text or 'text'}{ext}"
        elif naming == "prefix_index":
            return f"{prefix}_{index + 1:03d}{ext}"
        else:
            return f"{index + 1:03d}{ext}"

    def get_results(self) -> List[Dict[str, Any]]:
        """获取最近一次批量处理的结果

        返回：
            合成结果列表
        """
        return self._results

    def get_summary(self) -> Dict[str, Any]:
        """获取最近一次批量处理的摘要统计

        返回：
            包含total、success、failed、success_rate字段的字典
        """
        if not self._results:
            return {
                "total": 0,
                "success": 0,
                "failed": 0,
                "success_rate": "0.0%",
            }

        total = len(self._results)
        success = sum(1 for r in self._results if r["success"])
        failed = total - success
        rate = f"{(success / total * 100):.1f}%" if total > 0 else "0.0%"

        return {
            "total": total,
            "success": success,
            "failed": failed,
            "success_rate": rate,
        }
