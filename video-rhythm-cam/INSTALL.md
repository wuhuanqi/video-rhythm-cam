# Video Rhythm Cam - 安装指南

## 📋 系统要求

### 必需软件

| 软件 | 版本要求 | 用途 |
|------|---------|------|
| Node.js | >= 18.0.0 | Web 应用运行时 |
| Python | >= 3.8 | 后端 API 和脚本 |
| FFmpeg | >= 4.0 | 视频处理 |
| npm 或 pnpm | 最新版 | 包管理器 |

### 可选软件

| 软件 | 用途 |
|------|------|
| Git | 版本控制 |
| VS Code | 推荐的代码编辑器 |

## 🔧 详细安装步骤

### macOS

#### 1. 安装 Homebrew（如果未安装）

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 2. 安装 FFmpeg

```bash
brew install ffmpeg
brew install libsndfile
```

#### 3. 安装 Node.js

```bash
brew install node
```

#### 4. 安装 Python（通常系统自带）

```bash
python3 --version
# 如果版本 < 3.8，使用以下命令安装
brew install python@3.9
```

#### 5. 验证安装

```bash
ffmpeg -version
node --version
python3 --version
npm --version
```

### Ubuntu/Debian Linux

#### 1. 更新软件包列表

```bash
sudo apt update
sudo apt upgrade -y
```

#### 2. 安装 FFmpeg

```bash
sudo apt install -y ffmpeg libsndfile1
```

#### 3. 安装 Node.js

```bash
# 使用 NodeSource 仓库
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

#### 4. 安装 Python

```bash
sudo apt install -y python3 python3-pip python3-venv
```

#### 5. 验证安装

```bash
ffmpeg -version
node --version
python3 --version
npm --version
```

### Windows

#### 1. 安装 FFmpeg

**方法 A: 使用 Chocolatey（推荐）**

```powershell
# 以管理员身份运行 PowerShell
choco install ffmpeg
```

**方法 B: 手动安装**

1. 下载 FFmpeg: https://ffmpeg.org/download.html#build-windows
2. 解压到 `C:\ffmpeg`
3. 添加到系统 PATH:
   - 右键"此电脑" -> 属性 -> 高级系统设置
   - 环境变量 -> 系统变量 -> Path -> 编辑
   - 添加 `C:\ffmpeg\bin`

#### 2. 安装 Node.js

1. 下载安装包: https://nodejs.org/
2. 运行安装程序（使用默认选项）

#### 3. 安装 Python

1. 下载安装包: https://www.python.org/downloads/
2. 运行安装程序
3. **重要**: 勾选 "Add Python to PATH"

#### 4. 验证安装

打开新的命令提示符或 PowerShell：

```powershell
ffmpeg -version
node --version
python --version
npm --version
```

## 📦 安装项目依赖

### 1. 克隆或下载项目

```bash
git clone <repository-url>
cd video-rhythm-cam
```

### 2. 安装 Python 依赖

#### 使用虚拟环境（推荐）

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install --upgrade pip
pip install moviepy librosa soundfile numpy

# 安装 Python API 依赖
cd python-api
pip install -r requirements.txt
cd ..
```

#### 直接安装（不推荐）

```bash
pip install moviepy librosa soundfile numpy
pip install -r python-api/requirements.txt
```

### 3. 安装 Web 应用依赖

```bash
cd web
npm install
cd ..
```

### 4. 安装 Remotion 依赖

```bash
cd remotion
npm install
cd ..
```

## 🚀 验证安装

### 测试 Python API

```bash
cd python-api
python api.py
```

访问 http://localhost:8000/docs 查看 API 文档

### 测试 Web 应用

```bash
cd web
npm run dev
```

访问 http://localhost:3000

### 测试 CLI 脚本

```bash
# 测试节奏检测
python scripts/detect_beats.py --help

# 测试 Remotion 版
python scripts/rhythm_remotion.py --help
```

## ⚠️ 常见问题

### 问题 1: FFmpeg 未找到

**症状**: `ffmpeg: command not found`

**解决方案**:

1. 确认 FFmpeg 已安装: `ffmpeg -version`
2. 检查 PATH 环境变量
3. 重启终端

**macOS/Linux**:
```bash
which ffmpeg
# 如果没有输出，添加到 PATH
export PATH=$PATH:/usr/local/bin
```

**Windows**:
- 确保已将 FFmpeg 添加到系统 PATH
- 重启命令提示符

### 问题 2: Python 依赖安装失败

**症状**: `error: Microsoft Visual C++ 14.0 is required` (Windows)

**解决方案**:

1. 安装 Microsoft C++ Build Tools:
   https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. 或使用预编译的 wheel 包:
```bash
pip install --upgrade pip wheel
pip install moviepy librosa soundfile numpy --only-binary :all:
```

### 问题 3: librosa 安装失败

**症状**: `ImportError: libsndfile.so not found`

**解决方案**:

**macOS**:
```bash
brew install libsndfile
```

**Ubuntu/Debian**:
```bash
sudo apt install libsndfile1
```

**Windows**:
- 通常已包含在预编译包中
- 或使用 conda: `conda install -c conda-forge librosa`

### 问题 4: Node.js 依赖安装超时

**解决方案**:

使用国内镜像:
```bash
npm config set registry https://registry.npmmirror.com
npm install
```

或使用 cnpm:
```bash
npm install -g cnpm --registry=https://registry.npmmirror.com
cnpm install
```

### 问题 5: 端口已被占用

**症状**: `Error: listen EADDRINUSE: address already in use :::3000`

**解决方案**:

**macOS/Linux**:
```bash
# 查找并终止占用端口的进程
lsof -i :3000
kill -9 <PID>
```

**Windows**:
```powershell
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

或使用其他端口:
```bash
npm run dev -- -p 3001
```

## 📚 下一步

安装完成后，请查看 [README.md](./README.md) 了解如何使用项目。

## 💡 性能优化建议

### GPU 加速（可选）

如果您的系统支持 GPU 加速，可以显著提升渲染速度：

#### NVIDIA GPU

```bash
# 安装 CUDA 支持的 FFmpeg
# macOS: 不支持
# Ubuntu:
sudo apt install ffmpeg-nv

# 使用 GPU 加速渲染
python scripts/rhythm_remotion.py input.mp4 --hwaccel cuda
```

#### AMD GPU

```bash
# Ubuntu
sudo apt install ffmpeg-amd

python scripts/rhythm_remotion.py input.mp4 --hwaccel vaapi
```

## 🔗 相关链接

- [FFmpeg 官方文档](https://ffmpeg.org/documentation.html)
- [Node.js 下载页面](https://nodejs.org/)
- [Python 官方网站](https://python.org/)
- [librosa 文档](https://librosa.org/doc/latest/index.html)

---

如有其他问题，请提交 [Issue](https://github.com/yourusername/video-rhythm-cam/issues)
