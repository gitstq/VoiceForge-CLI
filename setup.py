"""
VoiceForge-CLI 安装配置文件

使用setuptools构建和安装VoiceForge命令行工具。
"""

import os

from setuptools import find_packages, setup

# 读取README文件（如果存在）
_readme_path = os.path.join(os.path.dirname(__file__) or ".", "README.md")
if os.path.exists(_readme_path):
    with open(_readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()
else:
    long_description = "VoiceForge - 轻量级AI语音合成与声音克隆CLI工具"

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="voiceforge-cli",
    version="1.0.0",
    description="轻量级AI语音合成与声音克隆CLI工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="VoiceForge Team",
    license="MIT",
    python_requires=">=3.9",
    packages=find_packages(),
    package_data={
        "voiceforge": ["web/**/*"],
    },
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
        ],
        "build": [
            "pyinstaller>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "voiceforge=voiceforge.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Environment :: Console",
    ],
)
