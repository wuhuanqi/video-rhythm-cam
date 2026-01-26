# 音频对齐功能 - 测试用例说明

## 📋 测试文件清单

### 1. 快速测试
**文件**: `quick_test.py`
**用途**: 快速验证基础功能和服务状态
**测试内容**:
- ✅ Python 依赖检查
- ✅ 脚本文件检查
- ✅ 模块导入测试
- ✅ API 服务状态
- ✅ Web 服务状态
- ✅ 测试数据检查

**运行方式**:
```bash
python3 quick_test.py
```

**适用场景**:
- 快速诊断问题
- 验证环境配置
- 检查服务状态

---

### 2. 命令行功能测试
**文件**: `test_cli.py`
**用途**: 测试命令行音频对齐功能
**测试内容**:
- ✅ 音频提取功能
- ✅ 偏移计算算法
- ✅ 音频偏移应用
- ✅ 完整对齐流程
- ✅ 边界情况处理
- ✅ 错误处理

**测试组**:
1. 音频提取功能（3个测试）
2. 偏移计算（2个测试）
3. 音频偏移应用（3个测试）
4. 完整对齐流程（2个测试）
5. 边界情况（3个测试）
6. 错误处理（1个测试）

**运行方式**:
```bash
python3 test_cli.py
```

**适用场景**:
- 测试核心算法
- 验证命令行功能
- 性能测试

---

### 3. API 接口测试
**文件**: `test_api.py`
**用途**: 测试 API 接口功能
**测试内容**:
- ✅ 健康检查
- ✅ 视频上传
- ✅ 音频对齐接口
- ✅ 节拍检测接口
- ✅ 文件下载

**运行方式**:
```bash
# 确保服务已启动
python3 test_api.py
```

**适用场景**:
- 测试 API 接口
- 验证前后端集成
- 接口回归测试

---

### 4. 完整测试套件
**文件**: `test_audio_alignment_complete.py`
**用途**: 运行所有测试用例
**测试内容**:
- ✅ 基本功能测试
- ✅ 相同视频测试（边界）
- ✅ 反向对齐测试
- ✅ 不同参数测试
- ✅ 错误处理测试
- ✅ API 端点测试
- ✅ 性能测试

**运行方式**:
```bash
python3 test_audio_alignment_complete.py
```

**输出**: `test_report.json`（测试报告）

**适用场景**:
- 完整功能验证
- 回归测试
- 生成测试报告

---

### 5. 一键测试脚本
**文件**: `run_all_tests.sh`
**用途**: 自动运行所有测试
**运行方式**:
```bash
./run_all_tests.sh
```

**执行流程**:
1. 快速功能测试
2. 命令行功能测试
3. API 接口测试（如果服务运行）
4. 完整测试套件（如果服务运行）

**适用场景**:
- 完整验证
- CI/CD 集成
- 发布前测试

---

## 🚀 快速开始

### 方式 1: 一键测试（推荐）
```bash
./run_all_tests.sh
```

### 方式 2: 分步测试

#### 步骤 1: 快速检查
```bash
python3 quick_test.py
```

#### 步骤 2: 测试命令行功能
```bash
python3 test_cli.py
```

#### 步骤 3: 测试 API 接口（需先启动服务）
```bash
# 终端 1: 启动 API
cd video-rhythm-cam/python-api
python3 api.py

# 终端 2: 运行测试
python3 test_api.py
```

#### 步骤 4: 完整测试套件（需先启动服务）
```bash
python3 test_audio_alignment_complete.py
```

---

## 📊 测试覆盖范围

### 功能测试
- [x] 音频提取
- [x] 偏移计算
- [x] 音频对齐
- [x] 视频合成
- [x] 文件上传
- [x] 文件下载

### 边界测试
- [x] 相同视频
- [x] 反向对齐
- [x] 大偏移量
- [x] 零偏移
- [x] 不存在的文件

### 性能测试
- [x] 处理速度
- [x] 文件大小
- [x] 内存使用

### API 测试
- [x] 健康检查
- [x] POST /api/upload
- [x] POST /api/align-audio
- [x] POST /api/detect-beats
- [x] GET /api/videos
- [x] GET /api/download/{filename}

---

## 📁 测试数据

### 创建测试数据
```bash
python3 create_simple_test.py
```

### 生成的测试文件
- `test_data/dance_video.mp4` - 舞蹈视频（10秒，60 BPM）
- `test_data/reference_video.mp4` - 参考视频（10秒，音频延迟2秒）
- `test_data/audio_with_beats.wav` - 节奏音频

---

## 🔧 测试环境要求

### Python 依赖
```bash
pip install librosa soundfile scipy moviepy numpy
```

### 服务要求（可选）
- Python API 服务: http://localhost:8000
- Web 前端服务: http://localhost:3000

---

## 📝 测试报告

### 查看测试报告
完整测试套件会生成 JSON 格式的测试报告：

```bash
# 运行完整测试
python3 test_audio_alignment_complete.py

# 查看报告
cat test_report.json
```

### 报告内容
```json
{
  "timestamp": "2026-01-26 10:30:00",
  "total": 15,
  "passed": 15,
  "failed": 0,
  "success_rate": "100.0%",
  "tests": [...]
}
```

---

## ⚠️ 常见问题

### Q1: 测试失败 - "API 服务未启动"
**A**: 先启动 API 服务
```bash
cd video-rhythm-cam/python-api
python3 api.py
```

### Q2: 测试失败 - "测试数据不存在"
**A**: 先创建测试数据
```bash
python3 create_simple_test.py
```

### Q3: 测试失败 - "缺少依赖"
**A**: 安装所需依赖
```bash
pip install librosa soundfile scipy moviepy
```

### Q4: 偏移量不准确
**A**: 这是正常的，测试数据比较简单。真实视频会得到更准确的结果。

---

## 💡 测试建议

### 开发阶段
- 使用 `quick_test.py` 快速验证
- 使用 `test_cli.py` 测试核心功能

### 集成阶段
- 使用 `test_api.py` 测试接口
- 使用 `test_audio_alignment_complete.py` 完整测试

### 发布前
- 运行 `run_all_tests.sh` 确保所有测试通过
- 检查测试报告
- 手工验证 Web 界面

---

## 🎯 测试目标

### 最小测试集
```bash
python3 quick_test.py
```

### 推荐测试集
```bash
python3 quick_test.py && python3 test_cli.py
```

### 完整测试集
```bash
./run_all_tests.sh
```

---

**最后更新**: 2026-01-26
**测试版本**: v1.0.0
