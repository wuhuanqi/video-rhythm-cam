# Video Rhythm Cam - Remotion 版

为舞蹈视频自动添加跟随音乐节奏的缩放运镜效果，使用 Remotion 进行高质量视频渲染。

## 项目结构

```
video-rhythm-cam/
├── scripts/                    # Python 脚本
│   ├── rhythm_cam.py          # 原版 (MoviePy)
│   ├── rhythm_remotion.py     # Remotion 版主脚本 (推荐)
│   ├── detect_beats.py        # 节奏检测模块
│   └── remotion_integration.py # Remotion 集成工具
├── remotion/                   # Remotion 项目
│   ├── src/
│   │   ├── RhythmVideo.tsx    # 主视频组件
│   │   ├── Root.tsx           # 根组件
│   │   └── index.ts           # 入口
│   ├── package.json
│   └── remotion.config.ts
└── SKILL.md                   # 详细文档
```

## 快速开始

### 1. 安装依赖

**Python 依赖：**
```bash
pip install moviepy librosa soundfile numpy
```

**Node.js 依赖（首次使用）：**
```bash
cd remotion
npm install --registry=https://registry.npmmirror.com
```

### 2. 基本使用

**处理单个视频：**
```bash
python scripts/rhythm_remotion.py input_video.mp4
```

**指定输出文件：**
```bash
python scripts/rhythm_remotion.py input_video.mp4 -o output.mp4
```

**批量处理：**
```bash
python scripts/rhythm_remotion.py --batch ./input_videos --output-dir ./output_videos
```

### 3. 参数调整

```bash
# 强烈节奏效果
python scripts/rhythm_remotion.py dance.mp4 -s 0.7 --zoom-max 1.5 --zoom-duration 0.15

# 轻微节奏效果
python scripts/rhythm_remotion.py dance.mp4 -s 0.3 --zoom-max 1.2 --zoom-duration 0.3

# 高质量渲染
python scripts/rhythm_remotion.py dance.mp4 --quality 95
```

## 参数说明

| 参数 | 说明 | 默认值 | 范围 |
|------|------|--------|------|
| `-s, --sensitivity` | 节拍检测灵敏度 | 0.5 | 0.0-1.0 |
| `--zoom-min` | 最小缩放比例 | 1.0 | - |
| `--zoom-max` | 最大缩放比例 | 1.3 | - |
| `--zoom-duration` | 缩放持续时间(秒) | 0.2 | - |
| `--quality` | 渲染质量 | 90 | 1-100 |
| `--batch` | 批量处理目录 | - | - |
| `--output-dir` | 批量处理输出目录 | - | - |

## 技术架构

```
视频输入 → Python 节奏检测 → 生成 JSON 数据 → Remotion 渲染 → MP4 输出
    ↓           ↓                  ↓                ↓
 dance.mp4   librosa         beats.json      React组件   output.mp4
```

### 工作流程

1. **提取音频**：从视频中提取音轨
2. **检测节拍**：使用 librosa 分析音频，识别节拍点和强度
3. **生成数据**：输出 JSON 格式的节拍数据
4. **Remotion 渲染**：使用 Remotion 应用缩放效果并渲染
5. **输出视频**：生成带运镜效果的高质量视频

## 版本对比

| 特性 | 原版 (rhythm_cam.py) | Remotion 版 |
|------|---------------------|-------------|
| 渲染方式 | 逐帧处理 (慢) | Web 技术 (快) |
| 画质 | 可能损失 | 高质量 |
| 可编辑性 | 不可编辑 | 可调整代码 |
| 跨平台 | ✅ | ✅ |
| 自动化 | ✅ | ✅ |
| 批量处理 | ❌ | ✅ |
| 预览 | ❌ | ✅ (Remotion Studio) |

## 独立使用模块

### 节奏检测

仅检测节拍并导出 JSON：
```bash
python scripts/detect_beats.py input_video.mp4 -o beats.json
```

### 预览效果

启动 Remotion Studio 预览：
```bash
cd remotion
npm start
```

## 常见问题

### "npm: command not found"
需要先安装 Node.js: https://nodejs.org/

### "Cannot find module 'remotion'"
进入 remotion 目录运行 `npm install`

### 渲染失败或卡住
- 检查视频文件是否损坏
- 尝试降低 --quality 参数
- 使用 --keep-temp 参数保留临时文件以便调试

### 处理速度慢
- 这是正常现象，视频渲染需要时间
- Remotion 版通常比原版更快

## License

MIT
