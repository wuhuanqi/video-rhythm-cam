# 🎬 Video Rhythm Cam 宣传片

为你自动生成的 Remotion 宣传片，展示 Video Rhythm Cam 的核心功能！

## 🚀 快速开始

### 方法 1: 使用启动脚本（推荐）

**macOS/Linux:**
```bash
cd /Users/a123/AI/pipi/video-rhythm-cam

# 预览宣传片
./promo.sh preview

# 渲染宣传片
./promo.sh render
```

**Windows:**
```cmd
cd C:\path\to\video-rhythm-cam

# 预览宣传片
promo.bat preview

# 渲染宣传片
promo.bat render
```

### 方法 2: 手动启动

```bash
# 1. 进入 Remotion 目录
cd /Users/a123/AI/pipi/video-rhythm-cam/remotion

# 2. 启动预览
npm start

# 3. 在浏览器中选择 "PromoVideo" composition

# 4. 渲染视频
npx remotion render PromoVideo ../output/promo-video.mp4
```

## 📋 宣传片内容

**总时长:** 30 秒

| 时间 | 场景 | 内容 |
|------|------|------|
| 0-3s | 开场标题 | Video Rhythm Cam 大标题 + 动画 |
| 3-6s | 问题引入 | "你的舞蹈视频...缺少节奏感？" |
| 6-9s | 解决方案 | "自动跟随音乐节奏" + 功能亮点 |
| 9-15s | 核心功能 | 4 个核心功能卡片展示 |
| 15-20s | 使用场景 | 舞蹈、健身、音乐、表演视频 |
| 20-25s | 使用方法 | 命令行使用示例 |
| 25-30s | 结束 | CTA + GitHub 链接 |

## 🎨 特色

- ✨ 炫酷的渐变动画效果
- 🎵 节奏感十足的视觉设计
- 📱 响应式布局设计
- 🎯 清晰的功能展示
- 🚀 强有力的 CTA（行动号召）

## 🛠️ 自定义

### 修改颜色主题

编辑 `remotion/src/PromoVideo.tsx`，搜索并替换颜色值：

```tsx
// 主色调
'#8b5cf6'  // 紫色
'#667eea'  // 蓝紫色
'#764ba2'  // 深紫色
```

### 修改文案

直接在 `PromoVideo.tsx` 中修改对应的文字内容。

### 调整时长

编辑 `remotion/src/Root.tsx`：

```tsx
durationInFrames={900}  // 30 秒 @ 30fps
```

## 📦 渲染选项

```bash
# 标准质量
./promo.sh render

# 高质量
./promo.sh render-hq

# 快速预览
./promo.sh render-fast
```

## 📚 更多信息

查看完整文档: [PROMO_GUIDE.md](./PROMO_GUIDE.md)

## 📄 许可证

MIT

---

**现在就预览你的宣传片吧！** 🎉
