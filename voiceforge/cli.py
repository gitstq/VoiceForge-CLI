"""
CLI入口模块

本模块提供了VoiceForge的命令行接口，支持以下命令：
- speak: 文本转语音合成
- voices: 列出可用音色
- preview: 预览语音合成效果
- batch: 批量文本转语音
- convert: 音频格式转换
- merge: 合并多个音频文件
- info: 获取音频文件信息
- web: 启动Web UI服务
- project: 项目管理（保存/加载/列表/导出）
- version: 显示版本号

使用示例：
    voiceforge speak --text "你好世界" --voice zh-CN-XiaoxiaoNeural --output hello.mp3
    voiceforge voices --lang zh-CN
    voiceforge batch --file input.txt --output-dir ./output
    voiceforge web --host 0.0.0.0 --port 8080
"""

import argparse
import asyncio
import os
import sys
from typing import List, Optional

from voiceforge import __version__
from voiceforge.audio import AudioProcessor
from voiceforge.batch import BatchProcessor
from voiceforge.engine import EngineFactory
from voiceforge.project import ProjectManager


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器

    返回：
        配置完成的ArgumentParser实例
    """
    parser = argparse.ArgumentParser(
        prog="voiceforge",
        description="VoiceForge - 轻量级AI语音合成与声音克隆CLI工具",
        epilog="示例: voiceforge speak --text '你好' --output hello.mp3",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"VoiceForge v{__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # speak 命令
    speak_parser = subparsers.add_parser("speak", help="文本转语音合成")
    speak_parser.add_argument("--text", type=str, required=True, help="要合成的文本")
    speak_parser.add_argument("--voice", type=str, default="", help="音色名称")
    speak_parser.add_argument("--output", type=str, default="output.mp3", help="输出文件路径")
    speak_parser.add_argument("--rate", type=str, default="+0%", help="语速（如'+20%%'）")
    speak_parser.add_argument("--volume", type=str, default="+0%", help="音量（如'+10%%'）")
    speak_parser.add_argument("--pitch", type=str, default="+0Hz", help="音调（如'+5Hz'）")
    speak_parser.add_argument("--engine", type=str, default="edge", help="引擎类型（edge/offline）")

    # voices 命令
    voices_parser = subparsers.add_parser("voices", help="列出可用音色")
    voices_parser.add_argument("--lang", type=str, default=None, help="按语言过滤（如zh-CN）")
    voices_parser.add_argument("--list", action="store_true", help="以列表形式显示")

    # preview 命令
    preview_parser = subparsers.add_parser("preview", help="预览语音合成效果")
    preview_parser.add_argument("--text", type=str, required=True, help="要预览的文本")
    preview_parser.add_argument("--voice", type=str, default="", help="音色名称")
    preview_parser.add_argument("--rate", type=str, default="+0%", help="语速")
    preview_parser.add_argument("--volume", type=str, default="+0%", help="音量")
    preview_parser.add_argument("--pitch", type=str, default="+0Hz", help="音调")

    # batch 命令
    batch_parser = subparsers.add_parser("batch", help="批量文本转语音")
    batch_parser.add_argument("--file", type=str, required=True, help="输入文本文件路径")
    batch_parser.add_argument("--output-dir", type=str, default="./output", help="输出目录")
    batch_parser.add_argument("--format", type=str, default="mp3", help="输出格式")
    batch_parser.add_argument("--voice", type=str, default="", help="音色名称")
    batch_parser.add_argument("--split-by", type=str, default="paragraph", help="分割方式（paragraph/line）")
    batch_parser.add_argument("--naming", type=str, default="index", help="命名方式（index/text/prefix_index）")
    batch_parser.add_argument("--engine", type=str, default="edge", help="引擎类型")

    # convert 命令
    convert_parser = subparsers.add_parser("convert", help="音频格式转换")
    convert_parser.add_argument("--input", type=str, required=True, help="输入文件路径")
    convert_parser.add_argument("--output", type=str, required=True, help="输出文件路径")
    convert_parser.add_argument("--format", type=str, default=None, help="目标格式（可选，从输出路径推断）")

    # merge 命令
    merge_parser = subparsers.add_parser("merge", help="合并多个音频文件")
    merge_parser.add_argument("--files", type=str, nargs="+", required=True, help="要合并的文件列表")
    merge_parser.add_argument("--output", type=str, required=True, help="输出文件路径")
    merge_parser.add_argument("--format", type=str, default="mp3", help="输出格式")

    # info 命令
    info_parser = subparsers.add_parser("info", help="获取音频文件信息")
    info_parser.add_argument("--file", type=str, required=True, help="音频文件路径")

    # web 命令
    web_parser = subparsers.add_parser("web", help="启动Web UI服务")
    web_parser.add_argument("--host", type=str, default="0.0.0.0", help="监听地址")
    web_parser.add_argument("--port", type=int, default=8080, help="监听端口")
    web_parser.add_argument("--debug", action="store_true", help="调试模式")

    # project 命令
    project_parser = subparsers.add_parser("project", help="项目管理")
    project_subparsers = project_parser.add_subparsers(dest="project_action", help="项目操作")

    # project save
    project_save = project_subparsers.add_parser("save", help="保存项目")
    project_save.add_argument("--name", type=str, required=True, help="项目名称")
    project_save.add_argument("--texts", type=str, required=True, help="文本列表（逗号分隔）")
    project_save.add_argument("--output-dir", type=str, default="./output", help="输出目录")
    project_save.add_argument("--voice", type=str, default="", help="音色")
    project_save.add_argument("--rate", type=str, default="+0%", help="语速")
    project_save.add_argument("--volume", type=str, default="+0%", help="音量")
    project_save.add_argument("--pitch", type=str, default="+0Hz", help="音调")

    # project load
    project_load = project_subparsers.add_parser("load", help="加载项目")
    project_load.add_argument("path", type=str, help="项目文件路径")

    # project list
    project_list = project_subparsers.add_parser("list", help="列出所有项目")
    project_list.add_argument("--dir", type=str, default="./projects", help="项目目录")

    # project export
    project_export = project_subparsers.add_parser("export", help="导出项目")
    project_export.add_argument("path", type=str, help="项目文件路径")
    project_export.add_argument("--output-dir", type=str, default=None, help="导出目录")

    # version 命令
    subparsers.add_parser("version", help="显示版本号")

    return parser


async def _cmd_speak(args: argparse.Namespace) -> None:
    """执行speak命令：文本转语音合成

    参数：
        args: 命令行参数
    """
    engine = EngineFactory.create_engine(args.engine)

    kwargs = {
        "rate": args.rate,
        "volume": args.volume,
        "pitch": args.pitch,
    }
    if args.voice:
        kwargs["voice"] = args.voice

    print(f"正在合成语音: \"{args.text[:50]}{'...' if len(args.text) > 50 else ''}\"")
    output_path = await engine.speak(args.text, args.output, **kwargs)
    print(f"合成完成: {output_path}")


async def _cmd_voices(args: argparse.Namespace) -> None:
    """执行voices命令：列出可用音色

    参数：
        args: 命令行参数
    """
    engine = EngineFactory.create_engine("edge")
    voices = await engine.get_voices(lang=args.lang)

    if not voices:
        print("未找到可用音色。")
        return

    # 按语言分组
    grouped: dict = {}
    for v in voices:
        locale = v.get("locale", "unknown")
        if locale not in grouped:
            grouped[locale] = []
        grouped[locale].append(v)

    if args.list:
        for locale in sorted(grouped.keys()):
            print(f"\n[{locale}]")
            for v in grouped[locale]:
                gender = v.get("gender", "")
                desc = v.get("description", v.get("name", ""))
                print(f"  - {v['name']} ({gender}) {desc}")
    else:
        print(f"共找到 {len(voices)} 个音色:")
        for v in voices:
            print(f"  {v['name']:40s} [{v['locale']}] {v.get('gender', '')}")


async def _cmd_preview(args: argparse.Namespace) -> None:
    """执行preview命令：预览语音合成效果

    参数：
        args: 命令行参数
    """
    engine = EngineFactory.create_engine("edge")

    kwargs = {
        "rate": args.rate,
        "volume": args.volume,
        "pitch": args.pitch,
    }
    if args.voice:
        kwargs["voice"] = args.voice

    print(f"正在生成预览: \"{args.text[:30]}...\"")
    await engine.preview(args.text, **kwargs)


async def _cmd_batch(args: argparse.Namespace) -> None:
    """执行batch命令：批量文本转语音

    参数：
        args: 命令行参数
    """
    engine = EngineFactory.create_engine(args.engine)
    processor = BatchProcessor()

    kwargs = {}
    if args.voice:
        kwargs["voice"] = args.voice

    def on_progress(current: int, total: int, text: str, output_file: str) -> None:
        """进度回调函数"""
        pct = current / total * 100
        short_text = text[:20] + "..." if len(text) > 20 else text
        print(f"  [{pct:5.1f}%] ({current}/{total}) {short_text} -> {os.path.basename(output_file)}")

    print(f"开始批量处理，文件: {args.file}")
    results = await processor.process_file(
        input_file=args.file,
        engine=engine,
        output_dir=args.output_dir,
        split_by=args.split_by,
        naming=args.naming,
        format=args.format,
        callback=on_progress,
        **kwargs,
    )

    summary = processor.get_summary()
    print(f"\n批量处理完成:")
    print(f"  总计: {summary['total']}")
    print(f"  成功: {summary['success']}")
    print(f"  失败: {summary['failed']}")
    print(f"  成功率: {summary['success_rate']}")


def _cmd_convert(args: argparse.Namespace) -> None:
    """执行convert命令：音频格式转换

    参数：
        args: 命令行参数
    """
    processor = AudioProcessor()

    # 如果未指定格式，从输出路径推断
    fmt = args.format
    if not fmt:
        _, ext = os.path.splitext(args.output)
        fmt = ext.lstrip(".") if ext else "mp3"

    print(f"转换格式: {args.input} -> {args.output} ({fmt})")
    result = processor.convert_format(args.input, args.output, fmt)
    print(f"转换完成: {result}")


def _cmd_merge(args: argparse.Namespace) -> None:
    """执行merge命令：合并音频文件

    参数：
        args: 命令行参数
    """
    processor = AudioProcessor()

    print(f"合并 {len(args.files)} 个音频文件...")
    result = processor.merge_audio(args.files, args.output, args.format)
    print(f"合并完成: {result}")


def _cmd_info(args: argparse.Namespace) -> None:
    """执行info命令：获取音频文件信息

    参数：
        args: 命令行参数
    """
    processor = AudioProcessor()

    info = processor.get_info(args.file)
    print(f"音频文件信息: {args.file}")
    print(f"  格式:     {info['format']}")
    print(f"  采样率:   {info['sample_rate']} Hz")
    print(f"  通道数:   {info['channels']}")
    print(f"  时长:     {info['duration']:.2f} 秒")
    print(f"  比特率:   {info['bitrate']}")
    print(f"  文件大小: {info['file_size']} 字节")


def _cmd_web(args: argparse.Namespace) -> None:
    """执行web命令：启动Web UI服务

    参数：
        args: 命令行参数
    """
    from voiceforge.web.app import create_app

    app = create_app()
    print(f"VoiceForge Web UI 启动中...")
    print(f"访问地址: http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)


def _cmd_project(args: argparse.Namespace) -> None:
    """执行project命令：项目管理

    参数：
        args: 命令行参数
    """
    if args.project_action == "save":
        manager = ProjectManager()
        texts = [t.strip() for t in args.texts.split(",") if t.strip()]

        settings = {
            "voice": args.voice,
            "rate": args.rate,
            "volume": args.volume,
            "pitch": args.pitch,
        }

        path = manager.save_project(args.name, texts, settings, args.output_dir)
        print(f"项目已保存: {path}")
        print(f"  名称: {args.name}")
        print(f"  文本数: {len(texts)}")

    elif args.project_action == "load":
        manager = ProjectManager()
        project = manager.load_project(args.path)
        print(f"项目: {project['name']}")
        print(f"  创建时间: {project.get('created_at', 'N/A')}")
        print(f"  文本数: {len(project['texts'])}")
        print(f"  设置: {project['settings']}")
        print(f"  输出目录: {project.get('output_dir', 'N/A')}")

    elif args.project_action == "list":
        manager = ProjectManager(args.dir)
        projects = manager.list_projects()

        if not projects:
            print("暂无项目。")
            return

        print(f"共 {len(projects)} 个项目:")
        for p in projects:
            print(f"  - {p['name']} (创建: {p['created_at']}, 文本数: {p['text_count']})")
            print(f"    路径: {p['path']}")

    elif args.project_action == "export":
        manager = ProjectManager()
        export_dir = manager.export_project(args.path, args.output_dir)
        print(f"项目已导出到: {export_dir}")

    else:
        print("请指定项目操作: save, load, list, export")
        print("使用 voiceforge project --help 查看帮助")


def main(argv: Optional[List[str]] = None) -> None:
    """VoiceForge CLI主入口函数

    参数：
        argv: 命令行参数列表，为None时使用sys.argv
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    if args.command == "version":
        print(f"VoiceForge v{__version__}")
        return

    if not args.command:
        parser.print_help()
        return

    # 异步命令
    async_commands = {
        "speak": _cmd_speak,
        "voices": _cmd_voices,
        "preview": _cmd_preview,
        "batch": _cmd_batch,
    }

    # 同步命令
    sync_commands = {
        "convert": _cmd_convert,
        "merge": _cmd_merge,
        "info": _cmd_info,
        "web": _cmd_web,
        "project": _cmd_project,
    }

    if args.command in async_commands:
        try:
            asyncio.run(async_commands[args.command](args))
        except Exception as e:
            print(f"错误: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.command in sync_commands:
        try:
            sync_commands[args.command](args)
        except Exception as e:
            print(f"错误: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
