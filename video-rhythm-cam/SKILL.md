---
name: video-rhythm-cam
description: 为舞蹈视频自动添加跟随音乐节奏的缩放运镜效果。当用户请求为视频添加节奏感、动态运镜、音乐同步缩放等效果时使用此技能。适用于 MP4 等视频格式,特别是舞蹈、健身、音乐类视频。
---

# Video Rhythm Cam

## Overview

为舞蹈视频自动添加跟随音乐节奏的缩放运镜效果,让视频画面随音乐节拍动态缩放,增强视觉冲击力和节奏感。

## Quick Start

### 版本选择

本项目提供两个版本：

1. **rhythm_cam.py** - 原版 (MoviePy)
   - 基于 Python + MoviePy + OpenCV
   - 逐帧渲染，较慢但依赖简单
   - 适合短视频和简单场景

2. **rhythm_remotion.py** - Remotion 版 (推荐)
   - 基于 Python 节奏检测 + Remotion 渲染
   - 更快速度，更好质量，支持批量处理
   - 需要安装 Node.js 环境

### 原版 (MoviePy)

基本使用:

```bash
python3 scripts/rhythm_cam.py input_video.mp4
```

指定输出文件:

```bash
python3 scripts/rhythm_cam.py input_video.mp4 -o output.mp4
```

### Remotion 版 (推荐)

首次使用需要安装 Node.js 依赖：

```bash
cd remotion
npm install
```

基本使用：

```bash
python3 scripts/rhythm_remotion.py input_video.mp4
```

批量处理：

```bash
python3 scripts/rhythm_remotion.py --batch ./videos --output-dir ./output
```

## Workflow

### 1. 检查依赖

#### 原版 (MoviePy) 依赖

```bash
pip install moviepy librosa soundfile numpy opencv-python
```

#### Remotion 版依赖

需要安装 Python 和 Node.js 依赖：

```bash
# Python 依赖
pip install moviepy librosa soundfile numpy

# Node.js 依赖 (首次使用)
cd remotion
npm install
```

### 2. 处理视频

#### Remotion 版处理流程：

1. **提取音频**: 从视频中提取音轨
2. **检测节拍**: 使用 librosa 分析音频，识别节拍点和强度
3. **生成数据**: 输出 JSON 格式的节拍数据
4. **Remotion 渲染**: 使用 Remotion 应用缩放效果并渲染
5. **输出视频**: 生成带运镜效果的高质量视频

#### 原版 (MoviePy) 处理流程：

1. **提取音频**: 从视频中提取音轨
2. **检测节拍**: 分析音频,识别音乐节拍点 (使用 librosa)
3. **应用缩放**: 在节拍处应用动态缩放效果
4. **渲染输出**: 生成带运镜效果的新视频

### 3. 参数调整

**节拍检测灵敏度** (`-s`, `--sensitivity`)
- 范围: 0.0 - 1.0
- 默认: 0.5
- 越高检测到的节拍越多,缩放越频繁

**缩放范围** (`--zoom-min`, `--zoom-max`)
- 默认: 1.0 - 1.3
- 控制最小和最大缩放比例
- 建议: 1.0 - 1.5 之间

**缩放持续时间** (`--zoom-duration`)
- 默认: 0.2 秒
- 控制每次缩放的动画时长

**渲染质量** (`--quality`) [仅 Remotion 版]
- 范围: 1-100
- 默认: 90
- 越高画质越好但渲染越慢

示例: 强烈节奏效果

```bash
# Remotion 版
python3 scripts/rhythm_remotion.py dance.mp4 -s 0.7 --zoom-max 1.5 --zoom-duration 0.15

# 原版
python3 scripts/rhythm_cam.py dance.mp4 -s 0.7 --zoom-max 1.5 --zoom-duration 0.15
```

示例: 轻微节奏效果

```bash
# Remotion 版
python3 scripts/rhythm_remotion.py dance.mp4 -s 0.3 --zoom-max 1.2 --zoom-duration 0.3

# 原版
python3 scripts/rhythm_cam.py dance.mp4 -s 0.3 --zoom-max 1.2 --zoom-duration 0.3
```

示例: 批量处理 [仅 Remotion 版]

```bash
python3 scripts/rhythm_remotion.py --batch ./input_videos --output-dir ./output_videos -s 0.6
```

## Resources

### scripts/rhythm_remotion.py (推荐 - Remotion 版)

Remotion 版主控脚本，支持批量处理和高质量渲染。

主要功能:
- `process_video_with_remotion()`: 处理单个视频
- `batch_process_videos()`: 批量处理多个视频
- 支持自定义渲染质量和并发参数

**特性**:
- 更快的渲染速度
- 更好的视频质量
- 支持批量处理
- 自动管理 Remotion 项目

### scripts/rhythm_cam.py (原版 - MoviePy)

核心视频处理脚本,包含完整的运镜效果生成流程。

主要功能:
- `extract_audio()`: 从视频提取音频
- `detect_beats()`: 使用 librosa 检测节拍
- `process_video()`: 主处理流程,应用缩放效果

直接运行脚本处理视频,无需加载到上下文。

### scripts/detect_beats.py

节奏检测模块，可独立使用。

主要功能:
- `detect_beats_with_strength()`: 检测节拍并计算强度
- `beats_to_json()`: 将节拍数据转换为 JSON 格式
- `detect_and_export()`: 检测节拍并导出为 JSON 文件

### scripts/remotion_integration.py

Remotion 集成工具，管理 Remotion 项目。

主要功能:
- `setup_remotion_project()`: 设置 Remotion 项目环境
- `render_video()`: 调用 Remotion CLI 渲染视频
- `install_dependencies()`: 安装 Node.js 依赖

### remotion/

Remotion 项目目录，包含 React 组件。

核心组件:
- `RhythmVideo.tsx`: 主视频组件，应用节奏缩放
- `Root.tsx`: 根组件，定义视频组合

## Tips

### 通用 Tips

- **处理时间**: 视频处理较耗时,建议先用短片段测试效果
- **节拍密度**: 如果缩放太频繁,降低 sensitivity 参数
- **缩放强度**: 如果效果不明显,增大 zoom_max 参数
- **音频质量**: 视频必须有音轨,否则无法检测节奏
- **输出格式**: 输出为 MP4 格式,使用 H.264 编码

### Remotion 版专属 Tips

- **首次使用**: 需要先在 remotion/ 目录运行 `npm install` 安装依赖
- **批量处理**: 使用 `--batch` 参数可以一次处理多个视频
- **渲染质量**: 使用 `--quality` 参数调整画质 (1-100)，默认 90
- **预览功能**: 可以在浏览器中预览效果 (`cd remotion && npm start`)
- **并发渲染**: 可以通过修改代码调整并发数以加快渲染速度

### 版本选择建议

- **短视频 (< 1分钟)**: 两个版本都可以
- **长视频 (> 1分钟)**: 推荐使用 Remotion 版
- **批量处理**: 仅 Remotion 版支持
- **简单快速**: 原版依赖更少，上手更快

## Troubleshooting

### 通用问题

**"缺少依赖库" 错误**
- 安装所有必需的 Python 包

**"未检测到节拍"**
- 检查视频是否有音频
- 尝试调整 sensitivity 参数

### Remotion 版专属问题

**"npm: command not found"**
- 需要先安装 Node.js: https://nodejs.org/
- 安装后重启终端

**"Cannot find module 'remotion'"**
- 进入 remotion 目录运行 `npm install`
- 确保 node_modules 目录存在

**渲染失败或卡住**
- 检查视频文件是否损坏
- 尝试降低 --quality 参数
- 使用 --keep-temp 参数保留临时文件以便调试

**"视频时长不匹配"**
- 确保 Root.tsx 中的 durationInFrames 已正确更新
- 检查原始视频是否能正常播放

**批量处理时某些视频失败**
- 检查视频格式是否支持 (mp4, mov, avi, mkv, webm)
- 确保所有视频都有音轨
- 查看具体错误信息进行调试

### 性能问题

**处理速度慢 (通用)**
- 这是正常现象,视频渲染需要时间
- 考虑降低视频分辨率或缩短视频长度

**Remotion 版渲染慢**
- 可以通过修改 concurrency 参数提高并发数
- 使用较快的 CPU 可以显著提升速度
- 考虑降低 --quality 参数

**内存不足**
- 处理较短的视频片段
- 关闭其他应用程序释放内存
- Remotion 版通常内存占用更少
