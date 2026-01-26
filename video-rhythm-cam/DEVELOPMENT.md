# Video Rhythm Cam - 开发指南

## 🛠️ 开发环境设置

### 推荐工具

- **IDE**: VS Code
- **浏览器**: Chrome 或 Edge
- **API 测试**: Postman 或 curl

### VS Code 扩展

```json
{
  "recommendations": [
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss",
    "ms-python.python",
    "ms-python.vscode-pylance",
    "github.copilot"
  ]
}
```

## 📂 项目结构详解

### Web 应用 (`/web`)

```
web/
├── app/                    # Next.js App Router
│   ├── page.tsx           # 主页面
│   ├── layout.tsx         # 根布局
│   └── globals.css        # 全局样式
├── components/            # React 组件
│   ├── VideoUploader.tsx  # 视频上传
│   ├── Timeline.tsx       # 时间轴
│   ├── PreviewPlayer.tsx  # 预览播放器
│   ├── ControlPanel.tsx   # 控制面板
│   └── BeatVisualizer.tsx # 节奏可视化
├── lib/                   # 工具库
│   ├── store.ts          # Zustand 状态管理
│   ├── ffmpeg.ts         # FFmpeg 封装
│   ├── remotion.ts       # Remotion 集成
│   └── utils.ts          # 工具函数
├── public/               # 静态资源
├── next.config.js        # Next.js 配置
├── tailwind.config.ts    # Tailwind 配置
└── package.json          # 依赖管理
```

### Python API (`/python-api`)

```
python-api/
├── api.py               # FastAPI 应用主文件
├── beat_detector.py     # 节奏检测模块
└── requirements.txt     # Python 依赖
```

## 🔄 开发工作流

### 启动开发环境

```bash
# Terminal 1: Python API
cd python-api
python api.py

# Terminal 2: Web 应用
cd web
npm run dev

# Terminal 3: Remotion Studio (可选)
cd remotion
npm start
```

### 代码规范

#### TypeScript

```bash
# 类型检查
npm run type-check

# Lint
npm run lint

# 自动修复
npm run lint -- --fix
```

#### Python

```bash
# 格式化代码
black .

# 类型检查
mypy python-api/

# Lint
flake8 python-api/
```

## 🧪 测试

### API 测试

使用 curl 测试 Python API:

```bash
# 健康检查
curl http://localhost:8000/health

# 上传视频
curl -X POST http://localhost:8000/api/upload \
  -F "file=@test.mp4"

# 检测节拍
curl -X POST http://localhost:8000/api/detect-beats \
  -H "Content-Type: application/json" \
  -d '{"videoPath":"/path/to/video.mp4","sensitivity":0.5}'
```

### 组件测试

```bash
# 安装测试依赖
npm install --save-dev jest @testing-library/react

# 运行测试
npm test
```

## 🎨 UI 开发

### 添加新组件

1. 在 `web/components/` 创建组件文件
2. 使用 TypeScript 定义 Props
3. 遵循 OpenCut 的深色主题风格

示例:

```tsx
// web/components/MyComponent.tsx
"use client";

import { useRhythmCamStore } from "@/lib/store";

interface MyComponentProps {
  title: string;
}

export function MyComponent({ title }: MyComponentProps) {
  const { parameters } = useRhythmCamStore();

  return (
    <div className="p-4 bg-card rounded-lg border border-border">
      <h3 className="text-sm font-semibold">{title}</h3>
    </div>
  );
}
```

### 样式指南

- 使用 Tailwind CSS 类名
- 遵循深色主题配色
- 使用 CSS 变量 (`--background`, `--foreground`, `--primary`)
- 保持一致的圆角 (`rounded-lg`)
- 使用语义化的颜色 (`bg-primary`, `text-muted-foreground`)

## 🔌 API 开发

### 添加新的 API 端点

在 `python-api/api.py` 中添加:

```python
@app.post("/api/my-endpoint")
async def my_endpoint(request: MyRequest):
    """API 描述"""
    try:
        # 实现逻辑
        result = process_request(request)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### 数据模型

使用 Pydantic 定义请求/响应模型:

```python
from pydantic import BaseModel

class MyRequest(BaseModel):
    param1: str
    param2: int = 10

class MyResponse(BaseModel):
    result: str
    count: int
```

## 🎬 渲染引擎开发

### FFmpeg 滤镜开发

在 `web/lib/ffmpeg.ts` 中扩展:

```typescript
export async function customFilter(
  options: RenderOptions
): Promise<string> {
  // 构建自定义滤镜
  const filterExpr = buildCustomFilter(options);

  return new Promise((resolve, reject) => {
    const ffmpeg = spawn('ffmpeg', [
      '-i', options.input,
      '-vf', filterExpr,
      options.output
    ]);

    ffmpeg.on('close', (code) => {
      if (code === 0) resolve(options.output);
      else reject(new Error('FFmpeg failed'));
    });
  });
}
```

### Remotion 组件开发

在 `remotion/src/` 中创建新组件:

```tsx
import { AbsoluteFill, useCurrentFrame } from "remotion";

export const MyComposition: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill style={{ backgroundColor: "white" }}>
      <h1>Frame: {frame}</h1>
    </AbsoluteFill>
  );
};
```

## 📊 状态管理

### Zustand Store 扩展

在 `web/lib/store.ts` 中添加:

```typescript
interface RhythmCamStore {
  // 新状态
  myState: string;
  setMyState: (value: string) => void;
}

export const useRhythmCamStore = create<RhythmCamStore>((set) => ({
  // 初始值
  myState: "",

  // Actions
  setMyState: (value) => set({ myState: value }),
}));
```

## 🐛 调试

### 前端调试

1. 使用 React DevTools
2. 使用 browser console:
   ```javascript
   // 访问 store
   const store = useRhythmCamStore.getState();
   console.log(store.beatsData);
   ```

### 后端调试

1. 查看 FastAPI 自动生成文档: http://localhost:8000/docs
2. 查看 API 日志
3. 使用 Python debugger:
   ```python
   import pdb; pdb.set_trace()
   ```

### FFmpeg 调试

1. 检查命令输出
2. 使用简化滤镜测试
3. 逐步增加复杂度

## 🚀 部署

### 构建 Web 应用

```bash
cd web
npm run build
npm start
```

### Docker 部署

创建 `Dockerfile`:

```dockerfile
FROM node:18-alpine

WORKDIR /app

# 安装 FFmpeg
RUN apk add --no-cache ffmpeg

# 复制并安装依赖
COPY web/package*.json ./web/
RUN cd web && npm install

COPY . .

# 暴露端口
EXPOSE 3000

# 启动应用
CMD ["npm", "start", "--prefix", "web"]
```

### 环境变量

创建 `.env.local`:

```bash
# API 配置
NEXT_PUBLIC_API_URL=http://localhost:8000

# FFmpeg 配置
FFMPEG_PATH=/usr/bin/ffmpeg

# 上传配置
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE=100MB
```

## 📈 性能优化

### 前端优化

1. **代码分割**: 使用动态导入
   ```tsx
   const HeavyComponent = dynamic(() => import('./HeavyComponent'))
   ```

2. **缓存策略**: 使用 React.memo
   ```tsx
   export const MyComponent = React.memo(({ data }) => {
     // ...
   })
   ```

3. **防抖/节流**: 使用 `lib/utils.ts` 中的工具函数

### 后端优化

1. **异步处理**: 使用 FastAPI 的异步端点
2. **缓存**: 添加 Redis 缓存节拍数据
3. **队列**: 使用 Celery 处理长时间任务

### 渲染优化

1. **硬件加速**: 使用 GPU 加速
2. **并行处理**: 多线程渲染
3. **渐进式渲染**: 先生成低质量预览

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支: `git checkout -b feature/my-feature`
3. 提交更改: `git commit -m 'Add my feature'`
4. 推送分支: `git push origin feature/my-feature`
5. 提交 Pull Request

## 📚 学习资源

- [Next.js 文档](https://nextjs.org/docs)
- [Remotion 文档](https://www.remotion.dev/docs)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [FFmpeg 文档](https://ffmpeg.org/documentation.html)
- [librosa 文档](https://librosa.org/doc/latest/)

---

Happy Coding! 🎉
