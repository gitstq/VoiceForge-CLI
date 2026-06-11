"""
项目管理模块

本模块提供了语音合成项目的保存、加载、列表和导出功能。
项目以JSON格式存储，包含文本列表、引擎设置和输出目录等配置信息。

使用示例：
    from voiceforge.project import ProjectManager

    manager = ProjectManager()
    manager.save_project("我的项目", ["你好", "世界"], {"voice": "zh-CN-XiaoxiaoNeural"}, "./output")
    projects = manager.list_projects("./projects")
"""

import json
import os
import shutil
from datetime import datetime
from typing import Any, Dict, List, Optional


class ProjectManager:
    """项目管理器

    管理语音合成项目的创建、保存、加载和导出。
    每个项目以JSON文件存储，包含文本列表、合成设置和输出目录等信息。

    项目JSON结构：
        {
            "name": "项目名称",
            "created_at": "创建时间",
            "updated_at": "更新时间",
            "texts": ["文本1", "文本2", ...],
            "settings": {"voice": "...", "rate": "...", ...},
            "output_dir": "输出目录路径",
            "audio_files": ["已生成的音频文件列表"]
        }

    使用示例：
        manager = ProjectManager()
        manager.save_project("测试项目", ["你好", "世界"], {}, "./out")
        project = manager.load_project("测试项目.json")
    """

    def __init__(self, projects_dir: Optional[str] = None) -> None:
        """初始化项目管理器

        参数：
            projects_dir: 项目存储目录路径，为None时使用当前目录下的"projects"文件夹
        """
        self.projects_dir: str = projects_dir or os.path.join(os.getcwd(), "projects")
        os.makedirs(self.projects_dir, exist_ok=True)

    def save_project(
        self,
        name: str,
        texts: List[str],
        settings: Dict[str, Any],
        output_dir: str,
    ) -> str:
        """保存项目为JSON文件

        将项目信息（名称、文本列表、引擎设置、输出目录）保存为JSON文件。

        参数：
            name: 项目名称
            texts: 要合成的文本列表
            settings: 引擎设置字典（如voice、rate、volume、pitch等）
            output_dir: 音频输出目录路径

        返回：
            项目JSON文件的绝对路径

        异常：
            ValueError: 项目名称或文本列表为空
            RuntimeError: 保存失败
        """
        if not name or not name.strip():
            raise ValueError("项目名称不能为空")
        if not texts:
            raise ValueError("文本列表不能为空")

        # 确保项目目录存在
        os.makedirs(self.projects_dir, exist_ok=True)

        now = datetime.now().isoformat()
        project_data: Dict[str, Any] = {
            "name": name.strip(),
            "created_at": now,
            "updated_at": now,
            "texts": texts,
            "settings": settings,
            "output_dir": output_dir,
            "audio_files": [],
        }

        # 安全文件名
        safe_name = "".join(
            c for c in name if c.isalnum() or c in ("_", "-", " ")
        ).strip()
        safe_name = safe_name.replace(" ", "_")
        project_filename = f"{safe_name}.json"
        project_path = os.path.join(self.projects_dir, project_filename)

        try:
            with open(project_path, "w", encoding="utf-8") as f:
                json.dump(project_data, f, ensure_ascii=False, indent=2)
            return os.path.abspath(project_path)
        except Exception as e:
            raise RuntimeError(f"保存项目失败: {e}") from e

    def load_project(self, project_path: str) -> Dict[str, Any]:
        """加载项目文件

        从JSON文件中加载项目信息。

        参数：
            project_path: 项目JSON文件的路径

        返回：
            项目数据字典，包含name、texts、settings、output_dir等字段

        异常：
            FileNotFoundError: 项目文件不存在
            RuntimeError: 加载失败或文件格式无效
        """
        if not os.path.exists(project_path):
            raise FileNotFoundError(f"项目文件不存在: {project_path}")

        try:
            with open(project_path, "r", encoding="utf-8") as f:
                data: Dict[str, Any] = json.load(f)

            # 验证必要字段
            required_fields = ["name", "texts", "settings"]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"项目文件缺少必要字段: '{field}'")

            return data
        except json.JSONDecodeError as e:
            raise RuntimeError(f"项目文件格式无效（非有效JSON）: {e}") from e
        except Exception as e:
            raise RuntimeError(f"加载项目失败: {e}") from e

    def list_projects(self, directory: Optional[str] = None) -> List[Dict[str, str]]:
        """列出指定目录下的所有项目

        扫描目录中的JSON文件，解析并返回项目摘要信息列表。

        参数：
            directory: 要扫描的目录路径，为None时使用projects_dir

        返回：
            项目摘要信息列表，每个字典包含name、path、created_at、text_count字段

        异常：
            RuntimeError: 列表获取失败
        """
        target_dir = directory or self.projects_dir

        if not os.path.exists(target_dir):
            return []

        projects: List[Dict[str, str]] = []
        try:
            for filename in sorted(os.listdir(target_dir)):
                if not filename.endswith(".json"):
                    continue
                filepath = os.path.join(target_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    projects.append({
                        "name": data.get("name", filename),
                        "path": os.path.abspath(filepath),
                        "created_at": data.get("created_at", "unknown"),
                        "updated_at": data.get("updated_at", "unknown"),
                        "text_count": str(len(data.get("texts", []))),
                    })
                except (json.JSONDecodeError, KeyError):
                    # 跳过无效的项目文件
                    continue
            return projects
        except Exception as e:
            raise RuntimeError(f"列出项目失败: {e}") from e

    def export_project(
        self,
        project_path: str,
        output_dir: Optional[str] = None,
    ) -> str:
        """导出项目及其所有关联的音频文件

        将项目JSON文件和所有已生成的音频文件复制到指定的导出目录。

        参数：
            project_path: 项目JSON文件路径
            output_dir: 导出目标目录，为None时在项目目录下创建export子目录

        返回：
            导出目录的绝对路径

        异常：
            FileNotFoundError: 项目文件不存在
            RuntimeError: 导出失败
        """
        project_data = self.load_project(project_path)

        if output_dir is None:
            project_dir = os.path.dirname(project_path)
            output_dir = os.path.join(project_dir, "export")

        os.makedirs(output_dir, exist_ok=True)

        try:
            # 复制项目JSON文件
            project_filename = os.path.basename(project_path)
            shutil.copy2(project_path, os.path.join(output_dir, project_filename))

            # 复制音频文件
            audio_files = project_data.get("audio_files", [])
            audio_output_dir = os.path.join(output_dir, "audio")
            copied_count = 0

            for audio_file in audio_files:
                if os.path.exists(audio_file):
                    os.makedirs(audio_output_dir, exist_ok=True)
                    shutil.copy2(
                        audio_file,
                        os.path.join(audio_output_dir, os.path.basename(audio_file)),
                    )
                    copied_count += 1

            print(f"项目导出完成: {copied_count} 个音频文件已复制到 {output_dir}")
            return os.path.abspath(output_dir)
        except Exception as e:
            raise RuntimeError(f"导出项目失败: {e}") from e
