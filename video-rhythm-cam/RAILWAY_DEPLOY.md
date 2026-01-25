# 🚀 部署到 Railway 完整指南

## 📋 部署前检查清单

- [ ] ✅ 代码已推送到 GitHub
- [ ] ✅ Python API 配置文件已创建（Dockerfile, railway.json）
- [ ] ✅ Web 前端配置文件已创建（railway.json）
- [ ] ⬜ Railway 账号已注册
- [ ] ⬜ 开始部署

---

## 🎯 部署步骤（约 10 分钟）

### 第 1 步：注册 Railway（2 分钟）

1. **访问 Railway**
   ```
   https://railway.app
   ```

2. **注册账号**
   - 点击右上角 **"Login"**
   - 选择 **"Continue with GitHub"** ⭐ 推荐用 GitHub 登录
   - 或者用邮箱注册

3. **授权 GitHub**
   - 点击 **"Authorize Railway"**
   - 选择 **"Hobby"** 计划（免费）

4. **完善信息**
   - 设置用户名
   - 绑定支付方式（可选，但需要绑定才能部署）
   - Railway 会给你 $5 免费额度/月

---

### 第 2 步：创建新项目（1 分钟）

1. **登录后，点击：**
   - 左上角 **"+ New Project"**
   - 或点击中间的 **"New Project"** 按钮

2. **选择部署方式**
   - 选择 **"Deploy from GitHub repo"**

3. **选择仓库**
   - 在列表中找到 `wuhuanqi/video-rhythm-cam`
   - 如果找不到，点击 **"Configure GitHub App"** 授权
   - 选择仓库后点击 **"Import"**

---

### 第 3 步：配置服务（3 分钟）

Railway 会自动检测到你的项目，并创建服务。

#### 服务 1：Python API（后端）

Railway 会识别 `python-api` 目录并创建服务。

**配置：**
- **Name:** `Video Rhythm API`（可自定义）
- **Root Directory:** `python-api`
- **Build Command:** 自动检测为 Dockerfile
- **Start Command:** `python api.py`

**环境变量（自动添加）：**
```
PORT = 8000
```

**点击 "Deploy" 开始部署** 🚀

#### 等待服务 1 部署完成...

---

#### 服务 2：Web 前端

在同一个项目中，再添加一个服务。

**点击：**
- 项目页面右上角 **"New Service"**
- 选择 **"GitHub Repo"**
- 选择同一个仓库 `wuhuanqi/video-rhythm-cam`

**配置：**
- **Name:** `Video Rhythm Web`（可自定义）
- **Root Directory:** `web`
- **Build Command:** `npm run build`
- **Start Command:** `npm start`

**环境变量（重要！）：**
```
NEXT_PUBLIC_API_URL = <你的 API 服务 URL>
PORT = 3000
```

**如何获取 API URL：**
1. 回到 "Video Rhythm API" 服务
2. 点击 **"Networking"**
3. 复制 **"Public URL"**（例如：`https://video-rhythm-api.up.railway.app`）
4. 在 "Video Rhythm Web" 服务的环境变量中添加：
   ```
   NEXT_PUBLIC_API_URL = https://video-rhythm-api.up.railway.app
   ```

**点击 "Deploy" 开始部署** 🚀

---

### 第 4 步：验证部署（2 分钟）

#### 检查后端 API

1. 在 Railway 项目页面，点击 **"Video Rhythm API"** 服务
2. 等待状态变为 **"Active"**（绿色）
3. 点击生成的 URL（例如：`https://video-rhythm-api.up.railway.app`）
4. 访问：`https://video-rhythm-api.up.railway.app/docs`
5. 应该看到 FastAPI 的文档页面 ✅

#### 检查前端

1. 点击 **"Video Rhythm Web"** 服务
2. 等待状态变为 **"Active"**（绿色）
3. 点击生成的 URL（例如：`https://video-rhythm-web.up.railway.app`）
4. 应该看到你的网站首页 ✅

---

### 第 5 步：测试完整功能（2 分钟）

1. **访问前端**
   ```
   https://video-rhythm-web.up.railway.app
   ```

2. **点击"在线体验"或访问**
   ```
   https://video-rhythm-web.up.railway.app/app
   ```

3. **上传视频测试**
   - 点击"上传视频"
   - 选择一个小视频文件（建议 < 10MB）
   - 等待上传和处理
   - 查看效果

---

## 🔧 配置说明

### Python API 服务

**Dockerfile 配置：**
- 基础镜像：`python:3.11-slim`
- 安装依赖：librosa, soundfile, fastapi 等
- 暴露端口：8000
- 启动命令：`uvicorn api:app --host 0.0.0.0 --port 8000`

**railway.json 配置：**
- 使用 Nixpacks 构建
- 健康检查：`/docs`
- 失败自动重启（最多 10 次）

---

### Web 前端服务

**railway.json 配置：**
- 使用 Nixpacks 构建
- 构建命令：`npm run build`
- 启动命令：`npm start`
- 健康检查：`/`

**重要：环境变量**
- `NEXT_PUBLIC_API_URL`：后端 API 的 URL
- `PORT`：前端端口（3000）

---

## 💰 费用说明

### Railway 定价

| 项目 | 价格 |
|------|------|
| **免费额度** | $5/月 |
| **CPU** | $0.000452/秒（空闲时免费） |
| **内存** | $0.000152/MB秒 |
| **存储** | $0.25/GB/月 |

### 实际费用估算

**轻度使用：**
- 每天处理 10 个视频
- 每个 1 分钟
- 月费用：约 $5-10

**中度使用：**
- 每天处理 50 个视频
- 每个 2 分钟
- 月费用：约 $15-30

**重度使用：**
- 每天处理 100+ 个视频
- 长时间处理
- 月费用：$30-50

**注意：** 只要不超过 $5 免费额度，就是免费的！

---

## 🛠️ 常见问题

### 1. 部署失败

**问题：** Build 失败

**解决方案：**
- 检查 Dockerfile 语法
- 查看构建日志
- 确保所有依赖都在 requirements.txt 中

---

### 2. 服务无法启动

**问题：** 状态一直显示 "Crashed"

**解决方案：**
- 查看 Logs 标签页的错误信息
- 检查 Start Command 是否正确
- 确认端口配置正确

---

### 3. 前端无法连接后端

**问题：** 上传视频时显示网络错误

**解决方案：**
1. 检查前端的环境变量 `NEXT_PUBLIC_API_URL`
2. 确保后端 API 服务正在运行
3. 查看 Network 标签，确保两个服务在同一项目
4. 如果使用了域名，确保配置正确

---

### 4. 视频处理太慢

**问题：** 处理大视频超时

**解决方案：**
1. 增加服务配置（CPU/RAM）
2. 在服务设置中，点击 "Settings" → "Generate Autoscale Policy"
3. 设置最小/最大实例数

---

### 5. 超出免费额度

**问题：** 收到账单

**解决方案：**
1. 在项目设置中设置消费限制
2. 监控使用情况
3. 优化代码减少资源消耗
4. 升级到付费计划（如需要）

---

## 🔄 更新部署

当代码更新后，Railway 会自动重新部署：

```bash
# 修改代码
git add .
git commit -m "feat: 新功能"
git push origin main

# Railway 自动检测并重新部署！
```

**手动重新部署：**
1. 进入服务页面
2. 点击 **"Deployments"** 标签
3. 点击 **"New Deployment"**
4. 选择最新的 commit
5. 点击 **"Deploy"**

---

## 📊 监控和日志

### 查看日志

1. 进入服务页面
2. 点击 **"Logs"** 标签
3. 实时查看应用日志

### 查看指标

1. 进入服务页面
2. 点击 **"Metrics"** 标签
3. 查看：
   - CPU 使用率
   - 内存使用
   - 网络流量
   - 请求次数

### 设置告警

1. 进入项目设置
2. 点击 **"Notifications"**
3. 配置告警规则（邮件、Discord、Slack 等）

---

## 🌐 自定义域名

### 设置自定义域名

1. **购买域名**（可选）
   - Namecheap: https://www.namecheap.com
   - Google Domains: https://domains.google

2. **在 Railway 添加域名**
   - 进入服务设置
   - 点击 **"Networking"**
   - 点击 **"Custom Domain"**
   - 输入你的域名（如：`video-rhythm-cam.com`）

3. **配置 DNS**
   - Railway 会给你 CNAME 记录
   - 在域名提供商添加 DNS 记录

4. **等待生效**
   - 通常需要 5-30 分钟

---

## ✅ 部署完成检查清单

部署完成后，确认：

- [ ] ✅ 后端 API 状态为 "Active"
- [ ] ✅ 前端 Web 状态为 "Active"
- [ ] ✅ 可以访问 `/docs`（API 文档）
- [ ] ✅ 可以访问首页 `/`
- [ ] ✅ 可以访问应用 `/app`
- [ ] ✅ 上传视频功能正常
- [ ] ✅ 视频处理功能正常
- [ ] ✅ 下载功能正常

---

## 🎉 完成！

恭喜！你的 Video Rhythm Cam 已经部署到 Railway 了！

**访问地址：**
- 前端：`https://video-rhythm-web.up.railway.app`（你的实际 URL）
- 后端：`https://video-rhythm-api.up.railway.app`（你的实际 URL）

**分享给朋友：**
直接分享前端 URL 就可以了！

---

## 📞 需要帮助？

- [Railway 文档](https://docs.railway.app)
- [Railway 社区](https://discord.gg/railway)
- [GitHub Issues](https://github.com/wuhuanqi/video-rhythm-cam/issues)

---

祝部署顺利！🚀
