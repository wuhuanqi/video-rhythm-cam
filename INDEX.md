# 音频对齐功能 - 总索引

## 📚 项目文档导航

### 🚀 快速开始
- **[快速开始指南](video-rhythm-cam/QUICK_START.md)** - 5分钟上手指南
- **[测试说明](TESTING_README.md)** - 测试套件使用说明
- **[测试指南](TEST_GUIDE.md)** - 详细的测试文档

### 📖 使用文档
- **[音频对齐指南](video-rhythm-cam/AUDIO_ALIGNMENT_GUIDE.md)** - 完整功能说明
- **[测试报告](TEST_REPORT.md)** - 功能测试报告

### 💻 开发文档
- **[架构说明](video-rhythm-cam/ARCHITECTURE.md)** - 系统架构设计
- **[开发指南](video-rhythm-cam/DEVELOPMENT.md)** - 开发者指南
- **[优化方案](video-rhythm-cam/ADVANCED_OPTIMIZATION.md)** - 高级优化

---

## 🎯 核心功能

### 音频对齐
将参考视频的音频对齐并替换到舞蹈视频中

**使用方式**:
1. 命令行: `python3 video-rhythm-cam/scripts/audio_alignment.py <舞蹈视频> <参考视频>`
2. API接口: `POST /api/align-audio`
3. Web界面: http://localhost:3000/workbench

---

## 🧪 测试套件

### 测试文件
| 文件 | 描述 | 用时 |
|------|------|------|
| `quick_test.py` | 快速验证 | ~5秒 |
| `test_cli.py` | 命令行测试 | ~30秒 |
| `test_api.py` | API测试 | ~15秒 |
| `test_audio_alignment_complete.py` | 完整测试 | ~60秒 |
| `run_all_tests.sh` | 一键测试 | ~2分钟 |

### 运行测试
```bash
# 快速验证
python3 quick_test.py

# 命令行测试
python3 test_cli.py

# API测试（需启动服务）
python3 test_api.py

# 完整测试
./run_all_tests.sh
```

---

## 📂 项目结构

```
.
├── video-rhythm-cam/           # 主项目
│   ├── scripts/
│   │   └── audio_alignment.py  # 音频对齐核心
│   ├── python-api/
│   │   └── api.py              # API服务
│   ├── web/
│   │   ├── components/
│   │   │   └── AudioAlignmentPanel.tsx
│   │   └── app/
│   │       └── workbench/
│   │           └── page.tsx    # 工作台
│   └── output/                 # 输出目录
├── test_data/                  # 测试数据
│   ├── dance_video.mp4
│   └── reference_video.mp4
├── create_simple_test.py       # 创建测试数据
├── quick_test.py               # 快速测试
├── test_cli.py                 # 命令行测试
├── test_api.py                 # API测试
├── test_audio_alignment_complete.py  # 完整测试
└── run_all_tests.sh            # 一键测试
```

---

## 🔧 环境要求

### Python依赖
```bash
pip install librosa soundfile scipy moviepy numpy requests
```

### 服务端口
- API服务: http://localhost:8000
- Web服务: http://localhost:3000

---

## 📝 快速命令

### 启动服务
```bash
# API服务
cd video-rhythm-cam/python-api && python3 api.py

# Web服务
cd video-rhythm-cam/web && npm run dev
```

### 创建测试数据
```bash
python3 create_simple_test.py
```

### 运行测试
```bash
./run_all_tests.sh
```

### 命令行使用
```bash
python3 video-rhythm-cam/scripts/audio_alignment.py \
  test_data/dance_video.mp4 \
  test_data/reference_video.mp4 \
  -o output.mp4
```

---

## ✅ 功能验证

### 测试结果
- ✅ 命令行测试: 16/16 通过 (100%)
- ✅ API接口测试: 全部通过
- ✅ 功能验证: 完全正常

### 核心功能
- ✅ 音频提取
- ✅ 偏移计算
- ✅ 音频对齐
- ✅ 视频合成
- ✅ API接口
- ✅ Web界面

---

## 🎓 使用示例

### 1. 命令行方式
```bash
python3 video-rhythm-cam/scripts/audio_alignment.py \
  dance.mp4 \
  reference.mp4 \
  -o aligned.mp4
```

### 2. API方式
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
```

### 3. Web界面方式
1. 访问 http://localhost:3000
2. 点击"开始使用"
3. 上传舞蹈视频
4. 切换到"音频对齐"
5. 上传参考视频
6. 点击"对齐音频并合成"
7. 等待下载

---

## 📞 获取帮助

### 问题排查
1. 运行 `python3 quick_test.py` 检查环境
2. 查看测试报告 `TEST_REPORT.md`
3. 阅读使用指南 `video-rhythm-cam/QUICK_START.md`

### 文档索引
- **功能说明**: `video-rhythm-cam/AUDIO_ALIGNMENT_GUIDE.md`
- **快速开始**: `video-rhythm-cam/QUICK_START.md`
- **测试说明**: `TEST_GUIDE.md`
- **测试总览**: `TESTING_README.md`

---

## 🎉 开始使用

### 最快的方式
```bash
# 1. 快速验证
python3 quick_test.py

# 2. 创建测试数据
python3 create_simple_test.py

# 3. 测试功能
python3 test_cli.py

# 4. 开始使用
python3 video-rhythm-cam/scripts/audio_alignment.py \
  test_data/dance_video.mp4 \
  test_data/reference_video.mp4 \
  -o output.mp4
```

### Web界面方式
```bash
# 1. 启动服务
cd video-rhythm-cam/python-api && python3 api.py &

# 2. 启动前端
cd video-rhythm-cam/web && npm run dev &

# 3. 访问
open http://localhost:3000
```

---

**版本**: v1.0.0
**更新时间**: 2026-01-26
**状态**: ✅ 完全可用
