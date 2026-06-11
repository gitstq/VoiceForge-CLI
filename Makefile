.PHONY: install dev test build clean web lint format

# 默认目标
all: install

# 安装项目（可编辑模式）
install:
	pip install -e .

# 安装开发依赖
dev:
	pip install -e ".[dev]"

# 运行测试
test:
	pytest tests/ -v --cov=voiceforge --cov-report=term-missing

# 运行测试（快速模式，不生成覆盖率报告）
test-quick:
	pytest tests/ -v

# 代码格式化
format:
	black voiceforge/ tests/
	isort voiceforge/ tests/

# 代码检查
lint:
	flake8 voiceforge/ tests/
	mypy voiceforge/

# 使用PyInstaller打包为可执行文件
build:
	pyinstaller --onefile --name voiceforge --hidden-import=edge_tts --hidden-import=pyttsx3 --hidden-import=pydub voiceforge/cli.py

# 清理构建产物
clean:
	rm -rf build/ dist/ *.egg-info/
	rm -rf .pytest_cache/ htmlcov/ .coverage
	rm -rf output/ projects/ export/
	rm -rf __pycache__/ voiceforge/__pycache__/ voiceforge/web/__pycache__/ tests/__pycache__/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete

# 启动Web UI
web:
	python -m voiceforge.cli web --host 0.0.0.0 --port 8080 --debug

# 启动Web UI（生产模式）
web-prod:
	python -m voiceforge.cli web --host 0.0.0.0 --port 8080
