---
name: video-rhythm-cam
description: 为舞蹈视频自动添加跟随音乐节奏的缩放运镜效果。当用户请求为视频添加节奏感、动态运镜、音乐同步缩放等效果时使用此技能。适用于 MP4 等视频格式,特别是舞蹈、健身、音乐类视频。
---

# Video Rhythm Cam

## Overview

为舞蹈视频自动添加跟随音乐节奏的缩放运镜效果,让视频画面随音乐节拍动态缩放,增强视觉冲击力和节奏感。

## Quick Start

基本使用:

```bash
python3 scripts/rhythm_cam.py input_video.mp4
```

指定输出文件:

```bash
python3 scripts/rhythm_cam.py input_video.mp4 -o output.mp4
```

## Workflow

### 1. 检查依赖

首次使用前安装所需依赖:

```bash
pip install moviepy librosa soundfile numpy opencv-python
```

### 2. 处理视频

脚本自动执行以下步骤:

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

示例: 强烈节奏效果

```bash
python3 scripts/rhythm_cam.py dance.mp4 -s 0.7 --zoom-max 1.5 --zoom-duration 0.15
```

示例: 轻微节奏效果

```bash
python3 scripts/rhythm_cam.py dance.mp4 -s 0.3 --zoom-max 1.2 --zoom-duration 0.3
```

## Resources

### scripts/rhythm_cam.py

核心视频处理脚本,包含完整的运镜效果生成流程。

主要功能:
- `extract_audio()`: 从视频提取音频
- `detect_beats()`: 使用 librosa 检测节拍
- `process_video()`: 主处理流程,应用缩放效果

直接运行脚本处理视频,无需加载到上下文。

## Tips

- **处理时间**: 视频处理较耗时,建议先用短片段测试效果
- **节拍密度**: 如果缩放太频繁,降低 sensitivity 参数
- **缩放强度**: 如果效果不明显,增大 zoom_max 参数
- **音频质量**: 视频必须有音轨,否则无法检测节奏
- **输出格式**: 输出为 MP4 格式,使用 H.264 编码

## Troubleshooting

**"缺少依赖库" 错误**
- 安装所有必需的 Python 包

**"未检测到节拍"**
- 检查视频是否有音频
- 尝试调整 sensitivity 参数

**处理速度慢**
- 这是正常现象,视频渲染需要时间
- 考虑降低视频分辨率或缩短视频长度

**内存不足**
- 处理较短的视频片段
- 关闭其他应用程序释放内存
