# 音频对齐功能 - 快速开始

## 功能已实现 ✅

音频对齐功能已经完全实现并可以使用！

## 快速测试

### 1. 通过命令行测试

```bash
# 基本用法
python3 video-rhythm-cam/scripts/audio_alignment.py \
  <舞蹈视频路径> \
  <参考视频路径> \
  -o <输出视频路径>

# 示例
python3 video-rhythm-cam/scripts/audio_alignment.py \
  dance_video.mp4 \
  reference_video.mp4 \
  -o output_aligned.mp4

# 带参数（自定义最大偏移量）
python3 video-rhythm-cam/scripts/audio_alignment.py \
  dance_video.mp4 \
  reference_video.mp4 \
  --max-offset 10.0 \
  -o output_aligned.mp4
```

### 2. 通过 Web 界面使用（推荐）

#### 启动服务

```bash
# 终端 1: 启动 Python API 后端
cd video-rhythm-cam/python-api
python3 api.py

# 终端 2: 启动 Web 前端
cd video-rhythm-cam/web
npm run dev
```

#### 使用步骤

1. 打开浏览器访问 `http://localhost:3000`
2. 点击"开始使用"进入工作台
3. 上传你的舞蹈视频（音质需要改进的那个）
4. 切换到"音频对齐"选项卡
5. 上传参考视频（包含同一首音乐的高质量视频）
6. 点击"对齐音频并合成"
7. 等待处理完成，视频会自动下载

## 工作原理

```
┌─────────────────┐
│ 舞蹈视频        │ ─┐
│ (音质不佳)      │  │
└─────────────────┘  │
                     ├─> 提取音频 ─> 计算偏移 ─> 对齐 ─> 合成 ─> 下载
┌─────────────────┐  │
│ 参考视频        │ ─┘
│ (音质更好)      │
└─────────────────┘
```

### 技术细节

1. **音频提取**: 使用 MoviePy 从视频中提取音频轨道
2. **节拍检测**: 使用 librosa 分析音频的节拍强度（onset strength）
3. **偏移计算**: 通过交叉相关（cross-correlation）找到最佳时间偏移量
4. **音频对齐**: 根据偏移量移动音频（添加静音或裁剪）
5. **视频合成**: 将对齐后的音频替换到舞蹈视频中

## API 接口

### POST /api/align-audio

**请求示例:**
```json
{
  "danceVideoPath": "/path/to/dance.mp4",
  "referenceVideoPath": "/path/to/reference.mp4",
  "maxOffset": 5.0
}
```

**响应示例:**
```json
{
  "success": true,
  "outputPath": "/path/to/output_aligned.mp4",
  "offset": 1.234
}
```

## 参数说明

### maxOffset（最大偏移量）
- **默认值**: 5.0 秒
- **说明**: 限制搜索偏移量的范围
- **建议**:
  - 如果视频开始时间相差不大，保持默认值
  - 如果相差较大，可以增加此值（最多 10-15 秒）
  - 增大此值会略微增加处理时间

## 注意事项

1. **必须是同一首音乐**: 两个视频应该包含同一首音乐，才能准确对齐
2. **参考视频音质更好**: 参考视频的音频质量应该优于舞蹈视频
3. **处理时间**: 取决于视频长度，通常 10-30 秒
4. **输出位置**: 视频保存在 `video-rhythm-cam/output/` 目录

## 文件结构

```
video-rhythm-cam/
├── scripts/
│   └── audio_alignment.py       # 音频对齐核心脚本
├── python-api/
│   └── api.py                    # API 服务（包含 /api/align-audio 接口）
├── web/
│   ├── components/
│   │   └── AudioAlignmentPanel.tsx  # 音频对齐前端组件
│   └── app/
│       └── workbench/
│           └── page.tsx          # 工作台页面
└── output/                        # 输出视频目录
```

## 测试示例

### 命令行测试

```bash
# 使用项目中的测试视频
python3 video-rhythm-cam/scripts/audio_alignment.py \
  test_dance.mp4 \
  test_dance.mp4 \
  -o video-rhythm-cam/output/test_aligned.mp4
```

### Python 代码测试

```python
import sys
sys.path.insert(0, 'video-rhythm-cam/scripts')

from audio_alignment import align_and_replace_audio

# 对齐并合成
success, offset = align_and_replace_audio(
    'dance.mp4',
    'reference.mp4',
    'output.mp4',
    max_offset=5.0
)

if success:
    print(f"✅ 成功！偏移量: {offset:.3f} 秒")
else:
    print("❌ 失败")
```

## 故障排除

### 问题1: 偏移量不准确
- **原因**: 两个音频不是同一首音乐
- **解决**: 确保使用同一首音乐的音频

### 问题2: 音频时长不匹配
- **原因**: 偏移量导致音频裁剪过多
- **解决**: 系统会自动保留至少 80% 的音频，或调整 maxOffset 参数

### 问题3: 处理时间过长
- **原因**: 视频过长或 maxOffset 设置过大
- **解决**: 降低 maxOffset 值或使用更短的视频进行测试

## 下一步

音频对齐功能已经可以使用了！你可以：

1. ✅ 通过命令行处理单个视频
2. ✅ 通过 Web 界面上传和处理
3. ✅ 集成到自己的 Python 代码中

如果需要任何改进或有问题，请随时告诉我！
