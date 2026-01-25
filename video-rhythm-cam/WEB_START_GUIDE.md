# 🌐 Web 应用启动指南

Video Rhythm Cam Web 应用需要同时运行两个服务器。

## 🚀 快速启动

### 方式 1：使用启动脚本（推荐）

**macOS/Linux:**
```bash
cd /Users/a123/AI/pipi/video-rhythm-cam
./start-web.sh
```

**Windows:**
```cmd
cd C:\path\to\video-rhythm-cam
start-web.bat
```

### 方式 2：手动启动

#### 终端 1 - 启动 Python API
```bash
cd /Users/a123/AI/pipi/video-rhythm-cam/python-api
python3 api.py
```

#### 终端 2 - 启动 Web 前端
```bash
cd /Users/a123/AI/pipi/video-rhythm-cam/web
npm run dev
```

---

## 📋 服务地址

启动成功后，访问以下地址：

| 服务 | 地址 | 说明 |
|------|------|------|
| **Web 应用** | http://localhost:3000 | 前端界面 |
| **展示页** | http://localhost:3000 | 项目介绍 |
| **应用页** | http://localhost:3000/app | 视频处理 |
| **文档页** | http://localhost:3000/docs | 使用文档 |
| **API 服务** | http://localhost:8000 | 后端 API |
| **API 文档** | http://localhost:8000/docs | Swagger 文档 |

---

## 🔍 常见问题

### 1. 视频上传没有反应

**原因：** Python API 服务器没有运行

**解决：**
```bash
# 检查 API 是否运行
lsof -i :8000

# 启动 API 服务器
cd python-api && python3 api.py
```

### 2. 找不到模块错误

**解决：**
```bash
# 安装 Python 依赖
cd python-api
pip install -r requirements.txt

# 安装 Node 依赖
cd web
npm install
```

### 3. 端口已被占用

**解决：**
```bash
# 查找占用端口的进程
lsof -i :3000  # 前端
lsof -i :8000  # 后端

# 杀死进程
kill -9 <PID>
```

---

## 🛑 停止服务

### 如果使用启动脚本
按 `Ctrl + C`，脚本会自动停止所有服务

### 手动停止
```bash
# 停止前端
# 在终端按 Ctrl+C

# 停止后端
# 在另一个终端按 Ctrl+C

# 或强制杀死
kill -9 $(lsof -t -i:3000)
kill -9 $(lsof -t -i:8000)
```

---

## 📝 开发模式

### 前端开发
```bash
cd web
npm run dev      # 启动开发服务器
npm run build    # 构建生产版本
npm run start    # 启动生产服务器
```

### 后端开发
```bash
cd python-api
python3 api.py   # 启动 API 服务器（带热重载）
```

---

## 🔧 配置

### API 地址配置

如果 API 服务器不在 `localhost:8000`，修改 `web/components/VideoUploader.tsx`:

```typescript
const response = await fetch("http://你的地址:端口/api/upload", {
  method: "POST",
  body: formData,
});
```

---

## 📦 部署到生产环境

查看 [DEPLOYMENT.md](./DEPLOYMENT.md) 了解如何部署到 Vercel 或其他平台。

---

## 💡 提示

1. **首次运行**：确保已安装所有依赖
2. **开发时**：使用启动脚本最方便
3. **调试时**：查看两个终端的日志输出
4. **API 文档**：访问 http://localhost:8000/docs 查看完整 API

---

现在试试上传视频吧！🎉
