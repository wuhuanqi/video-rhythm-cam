# Video Rhythm Cam 宣传片使用指南

## 宣传片预览和渲染

### 1. 启动 Remotion Studio 预览

```bash
cd /Users/a123/AI/pipi/video-rhythm-cam/remotion
npm start
```

在浏览器中会自动打开 Remotion Studio，你可以：
- 选择 **PromoVideo** composition
- 实时预览宣传片效果
- 播放、暂停、拖动时间轴

### 2. 渲染宣传片

#### 渲染为 MP4 视频

```bash
cd /Users/a123/AI/pipi/video-rhythm-cam/remotion

# 基础渲染
npx remotion render PromoVideo out/promo-video.mp4

# 高质量渲染
npx remotion render PromoVideo out/promo-video.mp4 --quality=95

# 指定渲染参数
npx remotion render PromoVideo out/promo-video.mp4 --frames=0-900 --jpeg-quality=90
```

#### 渲染为 GIF

```bash
npx remotion render PromoVideo out/promo-video.gif --frames=0-900
```

## 宣传片内容结构

总时长：**30 秒** (900 帧 @ 30fps)

### 场景 1: 开场标题 (0-3秒)
- Video Rhythm Cam 大标题
- 副标题："让视频随音乐律动"
- 节奏动画圆点
- 紫色渐变主题

### 场景 2: 问题引入 (3-6秒)
- "你的舞蹈视频...缺少节奏感？"
- "画面平淡无奇"
- 引起观众共鸣

### 场景 3: 解决方案 (6-9秒)
- "自动跟随音乐节奏"
- "🎵 智能节拍检测"
- "🎬 动态运镜效果"
- "✨ 让视频动起来！"

### 场景 4: 核心功能 (9-15秒)
展示 4 个核心功能：
1. **🎵 智能节奏检测** - 使用 librosa 自动识别音乐节拍点
2. **🔍 动态缩放** - 在节拍处自动应用缩放效果
3. **⚡ 批量处理** - 一次处理多个视频
4. **🎨 高质量渲染** - 基于 Remotion 输出高质量视频

### 场景 5: 使用场景 (15-20秒)
适用于多种场景：
- 💃 舞蹈视频
- 🏋️ 健身视频
- 🎤 音乐视频
- 🎪 表演视频

### 场景 6: 使用方法 (20-25秒)
展示简单的命令行用法：
```bash
$ python rhythm_remotion.py dance.mp4
✅ 一行命令，即刻生成
```

### 场景 7: 结束 (25-30秒)
- Video Rhythm Cam 大标题
- "让你的视频随音乐律动 ✨"
- GitHub 链接
- "立即体验 🚀" CTA 按钮

## 自定义宣传片

### 修改时长

如果需要调整宣传片时长，修改 `Root.tsx` 中的 `durationInFrames`：

```tsx
// 30 秒 = 900 帧 @ 30fps
durationInFrames={900}

// 修改为 60 秒
durationInFrames={1800}
```

### 修改颜色主题

在 `PromoVideo.tsx` 中搜索颜色值并替换：
- `#8b5cf6` - 紫色 (主色)
- `#667eea` - 蓝紫色 (渐变)
- `#764ba2` - 深紫色 (渐变)
- `#10b981` - 绿色 (成功)
- `#ef4444` - 红色 (警告)

### 修改文案

在 `PromoVideo.tsx` 中直接修改对应的文字内容。

### 添加/删除场景

在 `PromoVideo.tsx` 的 `PromoVideo` 组件中，修改 `<Sequence>` 的配置：

```tsx
// 添加新场景
<Sequence from={900} durationInFrames={90}>
  <YourNewScene frame={useCurrentFrame()} />
</Sequence>
```

## 技术特点

### 遵循 Remotion 最佳实践

1. ✅ 使用 `useCurrentFrame()` hook 驱动动画
2. ✅ 使用 `interpolate()` 实现平滑过渡
3. ✅ 使用 `spring()` 实现弹性动画
4. ✅ 使用 `<Sequence>` 组件组织场景
5. ✅ 使用 `AbsoluteFill` 作为根容器
6. ✅ 合理使用 `staticFile()` 引用资源

### 动画效果

- **淡入动画**: `FadeInText` 组件
- **缩放动画**: `PulseEffect` 组件
- **弹性动画**: 使用 `spring()` 函数
- **线性插值**: 使用 `interpolate()` 函数

## 输出参数建议

### 网络发布（推荐）
```bash
npx remotion render PromoVideo out/promo-web.mp4 \
  --quality=90 \
  --jpeg-quality=90 \
  --codec=h264
```

### 高质量存档
```bash
npx remotion render PromoVideo out/promo-hq.mp4 \
  --quality=95 \
  --jpeg-quality=95 \
  --codec=h264 \
  --pixel-ratio=2
```

### 快速预览
```bash
npx remotion render PromoVideo out/promo-fast.mp4 \
  --quality=80 \
  --jpeg-quality=80 \
  --scale=0.5
```

## 常见问题

### 预览时画面空白
- 检查浏览器控制台是否有错误
- 确保所有依赖都已安装 (`npm install`)
- 尝试重启 Remotion Studio

### 渲染失败
- 检查是否有足够的磁盘空间
- 尝试降低质量参数
- 查看 Remotion 日志获取详细错误信息

### 动画不流畅
- 确保使用 30fps 帧率
- 检查 `interpolate()` 和 `spring()` 的参数
- 避免在单帧内进行过多计算

## 许可证

MIT
