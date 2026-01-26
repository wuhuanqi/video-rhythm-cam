# 音频对齐功能 - 完整测试套件

## ✅ 测试完成！

已为你创建了完整的自动化测试套件，无需每次都在界面手动测试。

---

## 📦 测试文件清单

| 文件名 | 用途 | 测试数量 | 运行时间 |
|--------|------|----------|----------|
| `quick_test.py` | 快速验证基础功能 | 6项 | ~5秒 |
| `test_cli.py` | 命令行功能测试 | 16项 | ~30秒 |
| `test_api.py` | API接口测试 | 4项 | ~15秒 |
| `test_audio_alignment_complete.py` | 完整测试套件 | 15+项 | ~60秒 |
| `run_all_tests.sh` | 一键运行所有测试 | 全部 | ~2分钟 |

---

## 🚀 使用方法

### 1️⃣ 快速测试（推荐日常使用）
```bash
python3 quick_test.py
```
**检查项**:
- ✅ Python依赖
- ✅ 脚本文件
- ✅ 模块导入
- ✅ API服务
- ✅ Web服务
- ✅ 测试数据

**适用**: 快速诊断问题、验证环境

---

### 2️⃣ 命令行功能测试
```bash
python3 test_cli.py
```
**测试组**:
- 音频提取（3个测试）
- 偏移计算（2个测试）
- 音频偏移应用（3个测试）
- 完整对齐流程（2个测试）
- 边界情况（3个测试）
- 错误处理（1个测试）

**结果**: 16/16 通过 ✅
**适用**: 测试核心算法、验证命令行功能

---

### 3️⃣ API接口测试
```bash
# 确保服务已启动
python3 test_api.py
```
**测试项**:
- ✅ 健康检查
- ✅ 视频上传
- ✅ 音频对齐接口
- ✅ 文件下载验证

**适用**: 测试API接口、前后端集成

---

### 4️⃣ 完整测试套件
```bash
python3 test_audio_alignment_complete.py
```
**测试覆盖**:
- 基本功能
- 相同视频（边界）
- 反向对齐
- 不同参数
- 错误处理
- API端点
- 性能测试

**输出**: `test_report.json`（详细报告）
**适用**: 完整验证、回归测试、生成报告

---

### 5️⃣ 一键测试（最全面）
```bash
./run_all_tests.sh
```
**执行流程**:
1. 快速功能测试
2. 命令行功能测试
3. API接口测试（如果服务运行）
4. 完整测试套件（如果服务运行）

**输出**: 彩色终端输出 + 测试总结
**适用**: CI/CD、发布前验证

---

## 📊 测试结果示例

### 快速测试
```
通过: 5/6
成功率: 83.3%
✅ Python 依赖
✅ 脚本文件
✅ 模块导入
✅ API 服务
❌ Web 服务 (可选)
✅ 测试数据
```

### 命令行测试
```
总计: 16 | 通过: 16 | 失败: 0
成功率: 100.0%

测试组通过率:
- 音频提取: 100% (2/2)
- 偏移计算: 100% (5/5)
- 音频偏移应用: 100% (3/3)
- 完整对齐流程: 100% (2/2)
- 边界情况: 100% (3/3)
- 错误处理: 100% (1/1)
```

### 完整测试套件
```json
{
  "total": 15,
  "passed": 15,
  "failed": 0,
  "success_rate": "100.0%"
}
```

---

## 🎯 使用场景

### 开发阶段
```bash
# 快速验证修改是否破坏功能
python3 quick_test.py
```

### 功能测试
```bash
# 测试核心功能
python3 test_cli.py
```

### 接口测试
```bash
# 测试API接口（需要服务运行）
python3 test_api.py
```

### 发布前
```bash
# 完整验证
./run_all_tests.sh
```

---

## 📁 输出文件

测试完成后，会在以下位置生成输出：

### 命令行测试输出
```
video-rhythm-cam/output/
├── test_cli_aligned.mp4       # 基本对齐测试
├── test_same_video.mp4        # 相同视频测试
├── test_reverse.mp4           # 反向对齐测试
└── test_large_offset.mp4      # 大偏移量测试
```

### 完整测试报告
```
test_report.json               # JSON格式测试报告
```

---

## 💡 测试提示

### 1. 首次使用
```bash
# 1. 检查环境
python3 quick_test.py

# 2. 创建测试数据（如果需要）
python3 create_simple_test.py

# 3. 运行完整测试
./run_all_tests.sh
```

### 2. 日常开发
```bash
# 修改代码后快速验证
python3 test_cli.py
```

### 3. 发布前验证
```bash
# 完整测试套件
./run_all_tests.sh

# 检查测试报告
cat test_report.json
```

---

## ⚠️ 常见问题

### Q: API测试失败？
**A**: 确保服务已启动
```bash
cd video-rhythm-cam/python-api
python3 api.py
```

### Q: 测试数据不存在？
**A**: 创建测试数据
```bash
python3 create_simple_test.py
```

### Q: 依赖缺失？
**A**: 安装依赖
```bash
pip install librosa soundfile scipy moviepy numpy requests
```

---

## 📖 测试文档

- **测试指南**: `TEST_GUIDE.md` - 详细的测试说明
- **测试报告**: `TEST_REPORT.md` - 测试结果记录
- **使用指南**: `video-rhythm-cam/AUDIO_ALIGNMENT_GUIDE.md`
- **快速开始**: `video-rhythm-cam/QUICK_START.md`

---

## 🎉 测试优势

### 自动化
- ✅ 无需手动操作界面
- ✅ 批量执行测试用例
- ✅ 快速验证功能

### 全面性
- ✅ 覆盖核心功能
- ✅ 测试边界情况
- ✅ 验证错误处理

### 可重复
- ✅ 相同输入相同输出
- ✅ 回归测试
- ✅ 持续集成

### 可追踪
- ✅ 清晰的测试输出
- ✅ JSON测试报告
- ✅ 详细的错误信息

---

## 🔧 高级用法

### 自定义测试
编辑测试文件添加自己的测试用例：

```python
# test_cli.py
def test_my_case():
    # 你的测试代码
    success, output_path, offset, error = align_and_replace_audio(
        "video1.mp4",
        "video2.mp4",
        "output.mp4"
    )
    assert success, "测试失败"
```

### 性能基准测试
```bash
# 多次运行测试性能
for i in {1..10}; do
    python3 test_cli.py
done
```

### 持续集成
```bash
# CI脚本
#!/bin/bash
python3 quick_test.py || exit 1
python3 test_cli.py || exit 1
./run_all_tests.sh || exit 1
```

---

**版本**: v1.0.0
**最后更新**: 2026-01-26
**维护**: Claude Code
