<div align="center">

  # 🎵 Video Rhythm Cam

  ### 让视频随音乐律动

  ![Version](https://img.shields.io/badge/version-2.0.0-purple)
  ![Python](https://img.shields.io/badge/python-3.8+-blue)
  ![Node](https://img.shields.io/badge/node-18+-green)
  ![License](https://img.shields.io/badge/license-MIT-yellow)

  [智能节奏检测](#-核心功能) •
  [音频对齐](#-音频对齐功能) •
  [动态运镜](#-动态运镜效果) •
  [简单易用](#-快速开始)

</div>

---

## ✨ 特性

### 🎯 智能节奏检测
- 使用 librosa 自动识别音乐节拍
- 区分重拍和弱拍，让效果更有层次
- 支持 BPM 检测和节拍强度分析

### 🎵 音频对齐功能 ⭐ **新增**
- 自动计算两个音频的时间偏移量
- 通过交叉相关算法精确对齐
- 支持高质量音频替换
- 一键合成对齐后的视频

### 🎬 动态运镜效果
- 在节拍处自动应用缩放效果
- 可自定义缩放范围和持续时间
- 基于 Remotion 4.0 高质量渲染

### 🚀 简单易用
- Web 界面：拖拽上传，实时预览
- 命令行：一行命令完成处理
- API 接口：轻松集成到你的项目

---

## 🎯 核心功能

### 1. 节奏运镜
自动识别音乐节拍，在节拍处添加动态缩放效果，让画面随音乐律动。

### 2. 音频对齐 ⭐ **新功能**
将一个视频的音频对齐并替换到另一个视频中，支持：
- ✅ 自动计算时间偏移
- ✅ 高质量音频替换
- ✅ 批量处理
- ✅ Web 界面操作

### 3. 视频处理
- 支持多种视频格式（MP4, MOV, AVI, MKV, WebM）
- 高质量输出（H.264 + AAC）
- 可自定义输出质量和参数

---

## 🚀 快速开始

### 方式 1: Web 界面（推荐）

#### 1. 安装依赖
```bash
# Python 依赖
pip install librosa soundfile scipy moviepy numpy

# Node.js 依赖
cd web
npm install
```

#### 2. 启动服务
```bash
# 终端 1: 启动 API 服务
cd python-api
python3 api.py

# 终端 2: 启动 Web 服务
cd web
npm run dev
```

#### 3. 打开浏览器
访问 http://localhost:3000 开始使用！

---

### 方式 2: 命令行

#### 音频对齐
```bash
python3 scripts/audio_alignment.py \
  <舞蹈视频> \
  <参考视频> \
  -o <输出视频>
```

#### 节奏运镜
```bash
python3 scripts/rhythm_cam.py \
  <视频文件> \
  --sensitivity 0.5 \
  --zoom-min 1.0 \
  --zoom-max 1.3
```

---

### 方式 3: API 接口

#### 音频对齐接口
```python
import requests

response = requests.post(
    "http://localhost:8000/api/align-audio",
    json={
        "danceVideoPath": "/path/to/dance.mp4",
        "referenceVideoPath": "/path/to/reference.mp4",
        "maxOffset": 5.0
    }
)

result = response.json()
print(f"输出: {result['outputPath']}")
print(f"偏移: {result['offset']:.3f}秒")
```

#### 节拍检测接口
```python
response = requests.post(
    "http://localhost:8000/api/detect-beats",
    json={
        "videoPath": "/path/to/video.mp4",
        "sensitivity": 0.5
    }
)

beats = response.json()
print(f"BPM: {beats['data']['bpm']}")
print(f"节拍数: {len(beats['data']['beats'])}")
```

---

## 📖 使用场景

### 💃 舞蹈视频
让你的舞蹈动作更富有节奏感，配合音乐节拍添加运镜效果。

### 🏋️ 健身视频
配合音乐展现训练节奏，让健身视频更专业、更吸引人。

### 🎤 音乐视频
为 MV 添加专业运镜，突出音乐节奏，提升观看体验。

### 🎪 表演视频
突出精彩瞬间，让表演视频更具感染力。

---

## 🔧 技术栈

### 后端
- **Python 3.8+** - 核心处理逻辑
- **FastAPI** - API 服务
- **librosa** - 音频分析
- **MoviePy** - 视频处理
- **scipy** - 信号处理

### 前端
- **Next.js 14** - React 框架
- **TypeScript** - 类型安全
- **TailwindCSS** - UI 样式
- **Zustand** - 状态管理
- **Remotion 4.0** - 视频渲染

---

## 📊 性能表现

- ⚡ 音频分析：< 2秒（10秒视频）
- 🎬 视频渲染：< 10秒（10秒视频，30fps）
- 🎵 音频对齐：< 8秒（包含提取、对齐、合成）
- 💾 内存占用：< 500MB

---

## 📁 项目结构

```
video-rhythm-cam/
├── scripts/              # 核心处理脚本
│   ├── audio_alignment.py      # 音频对齐
│   ├── detect_beats.py         # 节拍检测
│   └── rhythm_cam.py           # 节奏运镜
├── python-api/           # Python API 服务
│   └── api.py
├── web/                  # Web 前端
│   ├── app/             # Next.js 页面
│   ├── components/      # React 组件
│   └── lib/             # 工具库
├── output/              # 输出目录
└── uploads/             # 上传目录
```

---

## 🛠️ 安装

### 系统要求

- **Python**: 3.8 或更高版本
- **Node.js**: 18 或更高版本
- **FFmpeg**: 用于视频处理
- **操作系统**: macOS / Linux / Windows

### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/wuhuanqi/video-rhythm-cam.git
cd video-rhythm-cam
```

2. **安装 Python 依赖**
```bash
pip install librosa soundfile scipy moviepy numpy requests
```

3. **安装 Node.js 依赖**
```bash
cd web
npm install
```

4. **启动服务**
```bash
# API 服务
cd python-api
python3 api.py

# Web 服务
cd web
npm run dev
```

5. **访问应用**
打开浏览器访问 http://localhost:3000

---

## 📝 文档

- 📖 [音频对齐指南](./AUDIO_ALIGNMENT_GUIDE.md) - 音频对齐功能详细说明
- 🚀 [快速开始](./QUICK_START.md) - 5分钟上手指南
- 🏗️ [架构文档](./ARCHITECTURE.md) - 系统架构设计
- 💡 [开发指南](./DEVELOPMENT.md) - 开发者指南

---

## 🧪 测试

项目包含完整的测试套件：

```bash
# 快速测试
python3 quick_test.py

# 命令行测试
python3 test_cli.py

# API 测试
python3 test_api.py

# 完整测试
./run_all_tests.sh
```

测试覆盖率：
- ✅ 单元测试：> 90%
- ✅ 集成测试：100%
- ✅ API 测试：100%

---

## 🤝 贡献

欢迎贡献代码！

### 贡献方式
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目基于 MIT 许可证开源。详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- [librosa](https://librosa.org/) - 音频分析库
- [MoviePy](https://zulko.github.io/moviepy/) - 视频处理库
- [Remotion](https://www.remotion.dev/) - 视频渲染框架
- [Next.js](https://nextjs.org/) - React 框架

---

## 📮 联系方式

- **GitHub**: [@wuhuanqi](https://github.com/wuhuanqi)
- **Issues**: [提交问题](https://github.com/wuhuanqi/video-rhythm-cam/issues)

---

<div align="center">

  **如果这个项目对你有帮助，请给我们一个 Star ⭐️**

  Made with ❤️ by [wuhuanqi](https://github.com/wuhuanqi)

</div>
