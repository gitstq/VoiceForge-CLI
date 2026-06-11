"""
Web UI模块

本模块提供了基于Flask的Web界面，用于语音合成的可视化管理。
包含语音合成、音色选择、批量处理和项目管理等功能。

使用示例：
    from voiceforge.web.app import create_app

    app = create_app()
    app.run(host="0.0.0.0", port=8080)
"""

import os
from typing import Any, Dict

from flask import Flask, jsonify, render_template_string, request, send_from_directory

from voiceforge.audio import AudioProcessor
from voiceforge.batch import BatchProcessor
from voiceforge.engine import EngineFactory
from voiceforge.project import ProjectManager

# 输出目录配置
OUTPUT_DIR = os.path.join(os.getcwd(), "output")
PROJECTS_DIR = os.path.join(os.getcwd(), "projects")

# 确保目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PROJECTS_DIR, exist_ok=True)

# HTML模板 - 现代化深色主题UI
HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VoiceForge - AI语音合成</title>
    <style>
        :root {
            --bg-primary: #0f0f1a;
            --bg-secondary: #1a1a2e;
            --bg-card: #16213e;
            --bg-input: #0f3460;
            --accent: #e94560;
            --accent-hover: #ff6b81;
            --text-primary: #eaeaea;
            --text-secondary: #a0a0b0;
            --border: #2a2a4a;
            --success: #00d2d3;
            --warning: #feca57;
            --radius: 12px;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 1px solid var(--border);
            margin-bottom: 30px;
        }

        header h1 {
            font-size: 2.5em;
            background: linear-gradient(135deg, var(--accent), var(--accent-hover));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 8px;
        }

        header p {
            color: var(--text-secondary);
            font-size: 1.1em;
        }

        .tabs {
            display: flex;
            gap: 8px;
            margin-bottom: 24px;
            border-bottom: 2px solid var(--border);
            padding-bottom: 8px;
        }

        .tab-btn {
            padding: 10px 24px;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: var(--radius) var(--radius) 0 0;
            color: var(--text-secondary);
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s;
        }

        .tab-btn:hover {
            background: var(--bg-card);
            color: var(--text-primary);
        }

        .tab-btn.active {
            background: var(--accent);
            color: white;
            border-color: var(--accent);
        }

        .panel {
            display: none;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 24px;
        }

        .panel.active {
            display: block;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: var(--text-secondary);
            font-weight: 500;
        }

        textarea, select, input[type="text"], input[type="number"] {
            width: 100%;
            padding: 12px 16px;
            background: var(--bg-input);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-primary);
            font-size: 1em;
            transition: border-color 0.3s;
        }

        textarea:focus, select:focus, input:focus {
            outline: none;
            border-color: var(--accent);
        }

        textarea {
            min-height: 120px;
            resize: vertical;
            font-family: inherit;
        }

        select {
            cursor: pointer;
            appearance: none;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23a0a0b0' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 12px center;
            padding-right: 36px;
        }

        .slider-group {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .slider-group input[type="range"] {
            flex: 1;
            -webkit-appearance: none;
            height: 6px;
            background: var(--bg-input);
            border-radius: 3px;
            border: none;
            padding: 0;
        }

        .slider-group input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 20px;
            height: 20px;
            background: var(--accent);
            border-radius: 50%;
            cursor: pointer;
        }

        .slider-value {
            min-width: 50px;
            text-align: center;
            color: var(--accent);
            font-weight: bold;
        }

        .btn-row {
            display: flex;
            gap: 12px;
            margin-top: 20px;
        }

        .btn {
            padding: 12px 28px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: 500;
        }

        .btn-primary {
            background: var(--accent);
            color: white;
        }

        .btn-primary:hover {
            background: var(--accent-hover);
            transform: translateY(-1px);
        }

        .btn-secondary {
            background: var(--bg-card);
            color: var(--text-primary);
            border: 1px solid var(--border);
        }

        .btn-secondary:hover {
            background: var(--bg-input);
        }

        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .audio-player {
            margin-top: 20px;
            padding: 16px;
            background: var(--bg-card);
            border-radius: 8px;
            display: none;
        }

        .audio-player.active {
            display: block;
        }

        .audio-player audio {
            width: 100%;
            margin-top: 8px;
        }

        .status-msg {
            margin-top: 12px;
            padding: 10px 16px;
            border-radius: 8px;
            display: none;
        }

        .status-msg.success {
            display: block;
            background: rgba(0, 210, 211, 0.1);
            border: 1px solid var(--success);
            color: var(--success);
        }

        .status-msg.error {
            display: block;
            background: rgba(233, 69, 96, 0.1);
            border: 1px solid var(--accent);
            color: var(--accent);
        }

        .status-msg.info {
            display: block;
            background: rgba(254, 202, 87, 0.1);
            border: 1px solid var(--warning);
            color: var(--warning);
        }

        .project-list {
            list-style: none;
        }

        .project-list li {
            padding: 12px 16px;
            background: var(--bg-card);
            border-radius: 8px;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .project-list li .name {
            font-weight: 500;
        }

        .project-list li .meta {
            color: var(--text-secondary);
            font-size: 0.9em;
        }

        .batch-progress {
            margin-top: 16px;
        }

        .progress-bar {
            width: 100%;
            height: 8px;
            background: var(--bg-input);
            border-radius: 4px;
            overflow: hidden;
        }

        .progress-bar .fill {
            height: 100%;
            background: linear-gradient(90deg, var(--accent), var(--accent-hover));
            transition: width 0.3s;
            width: 0%;
        }

        .progress-text {
            margin-top: 8px;
            color: var(--text-secondary);
            font-size: 0.9em;
        }

        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        @media (max-width: 768px) {
            .grid-2 {
                grid-template-columns: 1fr;
            }
            .btn-row {
                flex-direction: column;
            }
        }

        .loading {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid var(--text-secondary);
            border-top-color: var(--accent);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin-right: 8px;
            vertical-align: middle;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>VoiceForge</h1>
            <p>轻量级AI语音合成与声音克隆工具</p>
        </header>

        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('synthesize')">语音合成</button>
            <button class="tab-btn" onclick="switchTab('batch')">批量处理</button>
            <button class="tab-btn" onclick="switchTab('projects')">项目管理</button>
        </div>

        <!-- 语音合成面板 -->
        <div id="panel-synthesize" class="panel active">
            <div class="form-group">
                <label>输入文本</label>
                <textarea id="synth-text" placeholder="请输入要合成的文本内容..."></textarea>
            </div>

            <div class="grid-2">
                <div class="form-group">
                    <label>音色选择</label>
                    <select id="synth-voice">
                        <option value="">加载中...</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>输出格式</label>
                    <select id="synth-format">
                        <option value="mp3">MP3</option>
                        <option value="wav">WAV</option>
                        <option value="ogg">OGG</option>
                    </select>
                </div>
            </div>

            <div class="form-group">
                <label>语速调节</label>
                <div class="slider-group">
                    <input type="range" id="synth-rate" min="-50" max="100" value="0" oninput="updateSlider('rate')">
                    <span class="slider-value" id="rate-value">+0%</span>
                </div>
            </div>

            <div class="form-group">
                <label>音量调节</label>
                <div class="slider-group">
                    <input type="range" id="synth-volume" min="-50" max="50" value="0" oninput="updateSlider('volume')">
                    <span class="slider-value" id="volume-value">+0%</span>
                </div>
            </div>

            <div class="form-group">
                <label>音调调节</label>
                <div class="slider-group">
                    <input type="range" id="synth-pitch" min="-20" max="20" value="0" oninput="updateSlider('pitch')">
                    <span class="slider-value" id="pitch-value">+0Hz</span>
                </div>
            </div>

            <div class="btn-row">
                <button class="btn btn-primary" id="btn-synthesize" onclick="synthesize()">合成语音</button>
                <button class="btn btn-secondary" id="btn-preview" onclick="preview()">预览</button>
            </div>

            <div id="synth-status" class="status-msg"></div>

            <div id="audio-player" class="audio-player">
                <strong>合成结果：</strong>
                <audio id="audio-element" controls></audio>
            </div>
        </div>

        <!-- 批量处理面板 -->
        <div id="panel-batch" class="panel">
            <div class="form-group">
                <label>批量文本（每行一段）</label>
                <textarea id="batch-text" placeholder="第一段文本&#10;第二段文本&#10;第三段文本"></textarea>
            </div>

            <div class="grid-2">
                <div class="form-group">
                    <label>音色选择</label>
                    <select id="batch-voice">
                        <option value="">加载中...</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>输出格式</label>
                    <select id="batch-format">
                        <option value="mp3">MP3</option>
                        <option value="wav">WAV</option>
                    </select>
                </div>
            </div>

            <div class="btn-row">
                <button class="btn btn-primary" id="btn-batch" onclick="batchSynthesize()">开始批量合成</button>
            </div>

            <div class="batch-progress" id="batch-progress" style="display:none;">
                <div class="progress-bar"><div class="fill" id="batch-fill"></div></div>
                <div class="progress-text" id="batch-progress-text">准备中...</div>
            </div>

            <div id="batch-status" class="status-msg"></div>
        </div>

        <!-- 项目管理面板 -->
        <div id="panel-projects" class="panel">
            <div class="btn-row" style="margin-bottom: 20px;">
                <button class="btn btn-primary" onclick="refreshProjects()">刷新项目列表</button>
            </div>

            <ul class="project-list" id="project-list">
                <li style="color: var(--text-secondary);">加载中...</li>
            </ul>

            <div id="project-status" class="status-msg"></div>
        </div>
    </div>

    <script>
        let voicesLoaded = false;

        // 页面加载时获取音色列表
        document.addEventListener('DOMContentLoaded', function() {
            loadVoices();
            refreshProjects();
        });

        // 切换标签页
        function switchTab(name) {
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById('panel-' + name).classList.add('active');
        }

        // 更新滑块显示值
        function updateSlider(type) {
            if (type === 'rate') {
                const val = document.getElementById('synth-rate').value;
                document.getElementById('rate-value').textContent = (val >= 0 ? '+' : '') + val + '%';
            } else if (type === 'volume') {
                const val = document.getElementById('synth-volume').value;
                document.getElementById('volume-value').textContent = (val >= 0 ? '+' : '') + val + '%';
            } else if (type === 'pitch') {
                const val = document.getElementById('synth-pitch').value;
                document.getElementById('pitch-value').textContent = (val >= 0 ? '+' : '') + val + 'Hz';
            }
        }

        // 加载音色列表
        async function loadVoices() {
            try {
                const resp = await fetch('/api/voices');
                const data = await resp.json();
                const selects = [document.getElementById('synth-voice'), document.getElementById('batch-voice')];
                selects.forEach(sel => {
                    sel.innerHTML = '';
                    data.voices.forEach(v => {
                        const opt = document.createElement('option');
                        opt.value = v.name;
                        opt.textContent = v.description + ' [' + v.locale + ']';
                        sel.appendChild(opt);
                    });
                });
                voicesLoaded = true;
            } catch (e) {
                console.error('加载音色失败:', e);
            }
        }

        // 显示状态消息
        function showStatus(elementId, message, type) {
            const el = document.getElementById(elementId);
            el.textContent = message;
            el.className = 'status-msg ' + type;
        }

        // 语音合成
        async function synthesize() {
            const text = document.getElementById('synth-text').value.trim();
            if (!text) {
                showStatus('synth-status', '请输入要合成的文本', 'error');
                return;
            }

            const btn = document.getElementById('btn-synthesize');
            btn.disabled = true;
            btn.innerHTML = '<span class="loading"></span>合成中...';
            showStatus('synth-status', '', '');

            try {
                const rate = document.getElementById('synth-rate').value;
                const volume = document.getElementById('synth-volume').value;
                const pitch = document.getElementById('synth-pitch').value;

                const resp = await fetch('/api/synthesize', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        text: text,
                        voice: document.getElementById('synth-voice').value,
                        rate: (rate >= 0 ? '+' : '') + rate + '%',
                        volume: (volume >= 0 ? '+' : '') + volume + '%',
                        pitch: (pitch >= 0 ? '+' : '') + pitch + 'Hz',
                        format: document.getElementById('synth-format').value
                    })
                });

                const data = await resp.json();
                if (data.success) {
                    showStatus('synth-status', '合成成功！', 'success');
                    const player = document.getElementById('audio-player');
                    const audio = document.getElementById('audio-element');
                    audio.src = '/api/audio/' + data.filename;
                    player.classList.add('active');
                } else {
                    showStatus('synth-status', '合成失败: ' + (data.error || '未知错误'), 'error');
                }
            } catch (e) {
                showStatus('synth-status', '请求失败: ' + e.message, 'error');
            } finally {
                btn.disabled = false;
                btn.textContent = '合成语音';
            }
        }

        // 预览
        async function preview() {
            const text = document.getElementById('synth-text').value.trim();
            if (!text) {
                showStatus('synth-status', '请输入要预览的文本', 'error');
                return;
            }

            const btn = document.getElementById('btn-preview');
            btn.disabled = true;
            btn.innerHTML = '<span class="loading"></span>预览中...';

            try {
                const resp = await fetch('/api/preview/' + encodeURIComponent(text));
                const data = await resp.json();
                if (data.success) {
                    showStatus('synth-status', '预览音频已生成: ' + data.file, 'success');
                    const player = document.getElementById('audio-player');
                    const audio = document.getElementById('audio-element');
                    audio.src = '/api/audio/' + data.filename;
                    player.classList.add('active');
                } else {
                    showStatus('synth-status', '预览失败: ' + (data.error || '未知错误'), 'error');
                }
            } catch (e) {
                showStatus('synth-status', '请求失败: ' + e.message, 'error');
            } finally {
                btn.disabled = false;
                btn.textContent = '预览';
            }
        }

        // 批量合成
        async function batchSynthesize() {
            const text = document.getElementById('batch-text').value.trim();
            if (!text) {
                showStatus('batch-status', '请输入批量文本', 'error');
                return;
            }

            const btn = document.getElementById('btn-batch');
            btn.disabled = true;
            btn.innerHTML = '<span class="loading"></span>处理中...';
            document.getElementById('batch-progress').style.display = 'block';
            showStatus('batch-status', '', '');

            try {
                const texts = text.split('\n').filter(t => t.trim());
                const resp = await fetch('/api/batch', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        texts: texts,
                        voice: document.getElementById('batch-voice').value,
                        format: document.getElementById('batch-format').value
                    })
                });

                const data = await resp.json();
                document.getElementById('batch-fill').style.width = '100%';

                if (data.success) {
                    const summary = data.summary;
                    document.getElementById('batch-progress-text').textContent =
                        '完成！成功: ' + summary.success + '/' + summary.total + ' (' + summary.success_rate + ')';
                    showStatus('batch-status', '批量合成完成！', 'success');
                } else {
                    showStatus('batch-status', '批量合成失败: ' + (data.error || '未知错误'), 'error');
                }
            } catch (e) {
                showStatus('batch-status', '请求失败: ' + e.message, 'error');
            } finally {
                btn.disabled = false;
                btn.textContent = '开始批量合成';
            }
        }

        // 刷新项目列表
        async function refreshProjects() {
            try {
                const resp = await fetch('/api/projects');
                const data = await resp.json();
                const list = document.getElementById('project-list');

                if (!data.projects || data.projects.length === 0) {
                    list.innerHTML = '<li style="color: var(--text-secondary);">暂无项目</li>';
                    return;
                }

                list.innerHTML = '';
                data.projects.forEach(p => {
                    const li = document.createElement('li');
                    li.innerHTML = '<div><div class="name">' + p.name + '</div>' +
                        '<div class="meta">创建: ' + p.created_at + ' | 文本数: ' + p.text_count + '</div></div>';
                    list.appendChild(li);
                });
            } catch (e) {
                console.error('刷新项目列表失败:', e);
            }
        }
    </script>
</body>
</html>
"""


def create_app() -> Flask:
    """创建并配置Flask应用实例

    返回：
        配置完成的Flask应用实例
    """
    app = Flask(
        __name__,
        static_folder=None,
    )

    # 初始化组件
    project_manager = ProjectManager(PROJECTS_DIR)
    audio_processor = AudioProcessor()

    @app.route("/")
    def index() -> str:
        """渲染主页面

        返回：
            渲染后的HTML页面字符串
        """
        return render_template_string(HTML_TEMPLATE)

    @app.route("/api/voices", methods=["GET", "POST"])
    def api_voices() -> Dict[str, Any]:
        """获取可用的音色列表API

        GET请求返回所有可用音色。
        POST请求支持按语言过滤。

        请求参数（POST）：
            lang: 语言代码过滤（如"zh-CN"）

        返回：
            JSON响应，包含voices字段（音色列表）
        """
        try:
            import asyncio

            engine = EngineFactory.create_engine("edge")

            if request.method == "POST":
                data = request.get_json(silent=True) or {}
                lang = data.get("lang")
            else:
                lang = request.args.get("lang")

            voices = asyncio.run(engine.get_voices(lang=lang))
            return jsonify({"success": True, "voices": voices})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

    @app.route("/api/synthesize", methods=["POST"])
    def api_synthesize() -> Dict[str, Any]:
        """语音合成API

        接收文本和参数，合成语音文件。

        请求体（JSON）：
            text: 要合成的文本
            voice: 音色名称（可选）
            rate: 语速（可选，如"+20%"）
            volume: 音量（可选，如"+10%"）
            pitch: 音调（可选，如"+5Hz"）
            format: 输出格式（可选，默认"mp3"）

        返回：
            JSON响应，包含success、filename、filepath字段
        """
        try:
            import asyncio
            import uuid

            data = request.get_json()
            text = data.get("text", "").strip()
            if not text:
                return jsonify({"success": False, "error": "文本不能为空"})

            voice = data.get("voice", "")
            rate = data.get("rate", "+0%")
            volume = data.get("volume", "+0%")
            pitch = data.get("pitch", "+0Hz")
            output_format = data.get("format", "mp3")

            engine = EngineFactory.create_engine("edge")

            # 生成唯一文件名
            filename = f"{uuid.uuid4().hex[:8]}.{output_format}"
            output_path = os.path.join(OUTPUT_DIR, filename)

            kwargs: Dict[str, Any] = {
                "rate": rate,
                "volume": volume,
                "pitch": pitch,
            }
            if voice:
                kwargs["voice"] = voice

            result_path = asyncio.run(engine.speak(text, output_path, **kwargs))

            # 如果请求的格式不是mp3，需要进行格式转换
            if output_format != "mp3" and result_path:
                converted_path = output_path
                audio_processor.convert_format(result_path, converted_path, output_format)
                result_path = converted_path

            return jsonify({
                "success": True,
                "filename": filename,
                "filepath": result_path,
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

    @app.route("/api/preview/<path:text>")
    def api_preview(text: str) -> Dict[str, Any]:
        """语音预览API

        参数：
            text: 要预览的文本内容

        返回：
            JSON响应，包含success和file字段
        """
        try:
            import asyncio
            import uuid

            engine = EngineFactory.create_engine("edge")

            filename = f"preview_{uuid.uuid4().hex[:8]}.mp3"
            output_path = os.path.join(OUTPUT_DIR, filename)

            asyncio.run(engine.speak(text, output_path))

            return jsonify({
                "success": True,
                "filename": filename,
                "file": output_path,
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

    @app.route("/api/audio/<filename>")
    def api_audio(filename: str) -> Any:
        """获取生成的音频文件

        参数：
            filename: 音频文件名

        返回：
            音频文件响应
        """
        return send_from_directory(OUTPUT_DIR, filename)

    @app.route("/api/projects", methods=["GET", "POST"])
    def api_projects() -> Dict[str, Any]:
        """项目管理API

        GET请求：列出所有项目
        POST请求：创建新项目

        请求体（POST，JSON）：
            name: 项目名称
            texts: 文本列表
            settings: 引擎设置字典
            output_dir: 输出目录

        返回：
            JSON响应
        """
        try:
            if request.method == "GET":
                projects = project_manager.list_projects()
                return jsonify({"success": True, "projects": projects})
            else:
                data = request.get_json()
                name = data.get("name", "")
                texts = data.get("texts", [])
                settings = data.get("settings", {})
                output_dir = data.get("output_dir", OUTPUT_DIR)

                path = project_manager.save_project(name, texts, settings, output_dir)
                return jsonify({"success": True, "path": path})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

    @app.route("/api/batch", methods=["POST"])
    def api_batch() -> Dict[str, Any]:
        """批量语音合成API

        请求体（JSON）：
            texts: 文本列表
            voice: 音色名称（可选）
            format: 输出格式（可选）
            rate: 语速（可选）
            volume: 音量（可选）
            pitch: 音调（可选）

        返回：
            JSON响应，包含success、results、summary字段
        """
        try:
            import asyncio

            data = request.get_json()
            texts = data.get("texts", [])
            voice = data.get("voice", "")
            output_format = data.get("format", "mp3")
            rate = data.get("rate", "+0%")
            volume = data.get("volume", "+0%")
            pitch = data.get("pitch", "+0Hz")

            if not texts:
                return jsonify({"success": False, "error": "文本列表不能为空"})

            engine = EngineFactory.create_engine("edge")
            processor = BatchProcessor()

            kwargs: Dict[str, Any] = {
                "rate": rate,
                "volume": volume,
                "pitch": pitch,
            }
            if voice:
                kwargs["voice"] = voice

            results = asyncio.run(
                processor.process_texts(
                    texts=texts,
                    engine=engine,
                    output_dir=OUTPUT_DIR,
                    format=output_format,
                    **kwargs,
                )
            )

            summary = processor.get_summary()
            return jsonify({
                "success": True,
                "results": results,
                "summary": summary,
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

    return app
