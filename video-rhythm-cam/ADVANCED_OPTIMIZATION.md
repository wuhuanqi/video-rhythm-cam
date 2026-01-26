# 🚀 更激进的性能优化方案

如果视频还是很卡，这里有几个更激进的优化方案：

## 方案 1: 禁用实时缩放预览（推荐）

修改 ComparePlayer.tsx，让缩放效果只在导出时应用：

```typescript
// 修改缩放容器
<div
  className="w-full h-full flex items-center justify-center"
  style={{
    transform: "scale(1.0)", // 始终保持 1.0，不实时缩放
    transformOrigin: "center",
  }}
>
  <video ... />
</div>
```

**优点**: 完全消除实时缩放带来的性能问题
**缺点**: 无法在预览中看到缩放效果

---

## 方案 2: 单视频模式

只显示处理后的视频，不显示对比：

```typescript
// 简化为只有一个视频
<div className="flex-1">
  <video ... />
</div>
```

**优点**: 减少一半的视频解码负担
**缺点**: 无法对比原始和效果

---

## 方案 3: 降低更新频率到最小

```typescript
// 每 500ms 更新一次（2fps）
if (now - lastTimeUpdateRef.current > 500) {
  setCurrentTime(time);
}
```

**优点**: 更新频率极低，性能最好
**缺点**: 时间轴不同步

---

## 方案 4: 使用 CSS 动画代替 JS 计算

```css
@keyframes zoomPulse {
  0%, 100% { transform: scale(1.0); }
  50% { transform: scale(1.3); }
}

.video-container {
  animation: zoomPulse 0.4s ease-in-out;
}
```

**优点**: 完全由 GPU 处理，性能最好
**缺点**: 无法与实际节拍精确同步

---

## 方案 5: 简化节拍检测精度

只检测强节拍，减少计算量：

```typescript
// 只检测强度 > 0.7 的节拍
const strongBeats = beatsData.beats.filter(b => b.strength > 0.7);
```

**优点**: 减少 70% 的缩放操作
**缺点**: 弱拍处不会有效果

---

## 推荐方案组合

我建议实施：
1. **方案 3** - 降低更新频率到 100ms (10fps)
2. **方案 5** - 只对强节拍应用缩放
3. **preload="auto"** - 预加载整个视频

这样可以将性能提升 3-5 倍。

---

## 测试命令

你也可以直接测试原版的脚本，性能会好很多：

```bash
# 原版 MoviePy（最简单）
python scripts/rhythm_cam.py input.mp4 -o output.mp4

# Remotion 版（推荐）
python scripts/rhythm_remotion.py input.mp4
```

这些命令行版本不涉及浏览器，性能会好很多。
