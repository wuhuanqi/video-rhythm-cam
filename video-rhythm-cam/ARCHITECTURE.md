# Video Rhythm Cam - 混合架构设计

## 📐 整体架构

```
video-rhythm-cam/
├── web/                          # Next.js Web 应用 (新增)
│   ├── app/                      # Next.js App Router
│   │   ├── api/                  # API Routes
│   │   │   ├── detect-beats/     # 节奏检测 API
│   │   │   ├── render-preview/   # Remotion 预览渲染
│   │   │   └── render-final/     # FFmpeg 最终渲染
│   │   ├── page.tsx              # 主页面
│   │   └── layout.tsx            # 布局组件
│   ├── components/               # React 组件 (借鉴 OpenCut)
│   │   ├── VideoUploader.tsx     # 视频上传
│   │   ├── Timeline.tsx          # 时间轴
│   │   ├── BeatVisualizer.tsx    # 节奏点可视化
│   │   ├── PreviewPlayer.tsx     # 预览播放器
│   │   └── ControlPanel.tsx      # 控制面板
│   ├── lib/                      # 工具库
│   │   ├── ffmpeg.ts             # FFmpeg 封装
│   │   ├── remotion.ts           # Remotion 集成
│   │   └── store.ts              # Zustand 状态管理
│   ├── public/                   # 静态资源
│   └── package.json
│
├── scripts/                      # Python 脚本 (现有)
│   ├── detect_beats.py           # 节奏检测
│   ├── rhythm_cam.py             # 原版
│   └── rhythm_remotion.py        # Remotion 版
│
├── remotion/                     # Remotion 项目 (现有)
│   └── src/
│
└── python-api/                   # Python API 服务 (新增)
    ├── api.py                    # FastAPI 服务
    ├── beat_detector.py          # 节奏检测模块
    └── requirements.txt
```

## 🔄 数据流

### 1. 视频上传流程
```
用户上传视频
    ↓
存储到 uploads/ 目录
    ↓
提取音频信息
    ↓
调用 Python API 检测节拍
    ↓
返回节拍数据 (JSON)
    ↓
可视化展示在时间轴
```

### 2. 预览流程
```
用户调整参数
    ↓
调用 /api/render-preview
    ↓
Remotion 快速渲染低质量预览
    ↓
实时预览效果
```

### 3. 最终渲染流程
```
用户确认效果并点击"导出"
    ↓
调用 /api/render-final
    ↓
FFmpeg 高质量渲染
    ↓
下载最终视频
```

## 🎨 技术栈

### 前端
- **Next.js 15** - App Router
- **React 18** - UI 框架
- **TypeScript** - 类型安全
- **Zustand** - 状态管理
- **Tailwind CSS** - 样式
- **shadcn/ui** - UI 组件库

### 后端
- **Next.js API Routes** - API 层
- **FastAPI (Python)** - 节奏检测服务
- **librosa** - 音频分析
- **FFmpeg** - 视频处理

### 渲染引擎
- **Remotion** - 快速预览
- **FFmpeg** - 最终输出

## 📡 API 设计

### POST /api/detect-beats
```typescript
Request: {
  videoPath: string;
  sensitivity: number;
}

Response: {
  beats: Array<{ time: number; strength: number; frame: number }>;
  bpm: number;
  duration: number;
  fps: number;
}
```

### POST /api/render-preview
```typescript
Request: {
  videoPath: string;
  beatsData: BeatsData;
  zoomMin: number;
  zoomMax: number;
  zoomDuration: number;
}

Response: {
  previewUrl: string;
}
```

### POST /api/render-final
```typescript
Request: {
  videoPath: string;
  beatsData: BeatsData;
  outputPath: string;
  quality: number;
}

Response: {
  outputPath: string;
  status: 'success' | 'failed';
}
```

## 🎯 核心特性

### 1. 智能节奏检测
- 使用 librosa 检测音乐节拍
- 区分重拍和弱拍
- 可调节灵敏度

### 2. 可视化时间轴
- 显示视频时间轴
- 标记所有节奏点
- 支持手动编辑

### 3. 实时预览
- 快速渲染低质量预览
- 实时查看效果
- 支持参数调整

### 4. 高质量输出
- FFmpeg 硬件加速
- 可调节输出质量
- 支持多种格式

## 🔧 配置文件

### Next.js 配置 (next.config.js)
```javascript
module.exports = {
  webpack: (config) => {
    // 支持 Python 脚本调用
    config.externals = [...config.externals, 'ffmpeg-static'];
    return config;
  },
  // FFmpeg 支持
  experimental: {
    serverActions: true,
  },
};
```

### Zustand Store (lib/store.ts)
```typescript
interface VideoStore {
  currentVideo: string | null;
  beatsData: BeatsData | null;
  parameters: {
    sensitivity: number;
    zoomMin: number;
    zoomMax: number;
    zoomDuration: number;
  };
  isProcessing: boolean;
  setCurrentVideo: (video: string) => void;
  setBeatsData: (data: BeatsData) => void;
  updateParameter: (key: string, value: number) => void;
}
```

## 📦 依赖管理

### Web (Next.js)
```json
{
  "dependencies": {
    "next": "^15.0.0",
    "react": "^18.3.0",
    "zustand": "^4.5.0",
    "@ffmpeg/ffmpeg": "^0.12.0",
    "remotion": "^4.0.407",
    "fluent-ffmpeg": "^2.1.2"
  }
}
```

### Python API
```txt
fastapi==0.115.0
uvicorn==0.32.0
python-multipart==0.0.12
librosa==0.10.0
soundfile==0.12.1
numpy==1.24.0
```

## 🚀 部署方案

### 开发环境
1. 启动 Python API: `cd python-api && uvicorn api:app --reload`
2. 启动 Next.js: `cd web && npm run dev`
3. 访问: http://localhost:3000

### 生产环境
1. Docker 容器化
2. Nginx 反向代理
3. PM2 进程管理

## 🎨 UI 参考 (借鉴 OpenCut)

### 主题设计
- 深色模式为主
- 简洁的界面设计
- 直观的控制面板

### 核心组件
1. **上传区域** - 拖拽上传视频
2. **时间轴** - 可视化节奏点
3. **预览窗口** - 实时预览效果
4. **控制面板** - 参数调整
5. **导出按钮** - 一键渲染

## 📝 开发计划

### Phase 1: 基础架构
- [x] 创建分支
- [x] 架构设计
- [ ] 初始化 Next.js 项目
- [ ] 创建 Python API 服务

### Phase 2: 核心功能
- [ ] 实现节奏检测 API
- [ ] 创建前端 UI 组件
- [ ] 集成 FFmpeg 渲染

### Phase 3: 高级功能
- [ ] Remotion 预览
- [ ] 手动编辑节奏点
- [ ] 预设效果库

### Phase 4: 优化和发布
- [ ] 性能优化
- [ ] 错误处理
- [ ] 文档完善
