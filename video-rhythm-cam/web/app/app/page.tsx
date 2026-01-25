"use client";

import { Music, ArrowLeft, Download, Github, Terminal, Play } from "lucide-react";
import Link from "next/link";

export default function AppPage() {
  return (
    <main className="flex flex-col h-screen overflow-hidden bg-slate-950">
      {/* 顶部导航栏 */}
      <header className="flex-shrink-0 border-b border-border bg-card">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link
              href="/"
              className="text-gray-400 hover:text-white transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div className="flex items-center gap-2">
              <div className="bg-primary p-2 rounded-lg">
                <Music className="w-6 h-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">Video Rhythm Cam</h1>
                <p className="text-xs text-muted-foreground">智能节奏运镜</p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <a
              href="https://github.com/wuhuanqi/video-rhythm-cam"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors px-3 py-2 rounded-lg hover:bg-slate-800"
            >
              <Github className="w-4 h-4" />
              <span className="text-sm">GitHub</span>
            </a>
          </div>
        </div>
      </header>

      {/* 主内容区域 */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="max-w-4xl mx-auto text-center">
          {/* 标题 */}
          <div className="mb-12">
            <h2 className="text-5xl font-bold text-white mb-4">
              本地运行版本
            </h2>
            <p className="text-xl text-gray-400">
              Video Rhythm Cam 需要在本地运行，以实现最佳的视频处理性能
            </p>
          </div>

          {/* 卡片网格 */}
          <div className="grid md:grid-cols-2 gap-6 mb-12">
            {/* 下载卡片 */}
            <div className="bg-slate-900/50 backdrop-blur-lg border border-slate-700 rounded-2xl p-8 hover:border-purple-500/50 transition-all">
              <div className="flex justify-center mb-6">
                <div className="bg-purple-500/10 p-4 rounded-full">
                  <Download className="w-12 h-12 text-purple-400" />
                </div>
              </div>

              <h3 className="text-2xl font-bold text-white mb-4">
                下载到本地
              </h3>

              <p className="text-gray-400 mb-6">
                克隆仓库到本地，安装依赖后运行。支持所有功能，包括视频上传、节奏检测、运镜渲染。
              </p>

              <div className="space-y-3 text-left bg-slate-950/50 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <div className="bg-purple-500/20 rounded-full p-1 mt-0.5">
                    <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                  </div>
                  <div>
                    <div className="text-sm text-white font-mono">git clone https://github.com/wuhuanqi/video-rhythm-cam.git</div>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="bg-purple-500/20 rounded-full p-1 mt-0.5">
                    <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-300">按照 README.md 中的步骤安装依赖</div>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <div className="bg-purple-500/20 rounded-full p-1 mt-0.5">
                    <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-300">启动服务并开始处理视频</div>
                  </div>
                </div>
              </div>

              <a
                href="https://github.com/wuhuanqi/video-rhythm-cam"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center gap-2 w-full bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-xl font-semibold transition-colors mt-6"
              >
                <Github className="w-5 h-5" />
                前往 GitHub
              </a>
            </div>

            {/* 功能特点卡片 */}
            <div className="bg-slate-900/50 backdrop-blur-lg border border-slate-700 rounded-2xl p-8 hover:border-pink-500/50 transition-all">
              <div className="flex justify-center mb-6">
                <div className="bg-pink-500/10 p-4 rounded-full">
                  <Play className="w-12 h-12 text-pink-400" />
                </div>
              </div>

              <h3 className="text-2xl font-bold text-white mb-4">
                核心功能
              </h3>

              <ul className="space-y-4 text-left">
                <li className="flex items-start gap-3">
                  <div className="bg-green-500/20 rounded-full p-1 mt-0.5">
                    <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  </div>
                  <div>
                    <div className="text-white font-medium">智能节奏检测</div>
                    <div className="text-sm text-gray-400">使用 librosa 自动识别音乐节拍</div>
                  </div>
                </li>

                <li className="flex items-start gap-3">
                  <div className="bg-green-500/20 rounded-full p-1 mt-0.5">
                    <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  </div>
                  <div>
                    <div className="text-white font-medium">动态运镜效果</div>
                    <div className="text-sm text-gray-400">在节拍处自动应用缩放效果</div>
                  </div>
                </li>

                <li className="flex items-start gap-3">
                  <div className="bg-green-500/20 rounded-full p-1 mt-0.5">
                    <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  </div>
                  <div>
                    <div className="text-white font-medium">高质量渲染</div>
                    <div className="text-sm text-gray-400">基于 Remotion 4.0 输出 MP4</div>
                  </div>
                </li>

                <li className="flex items-start gap-3">
                  <div className="bg-green-500/20 rounded-full p-1 mt-0.5">
                    <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  </div>
                  <div>
                    <div className="text-white font-medium">批量处理</div>
                    <div className="text-sm text-gray-400">一次处理多个视频文件</div>
                  </div>
                </li>
              </ul>
            </div>
          </div>

          {/* 系统要求 */}
          <div className="bg-slate-800/30 backdrop-blur-lg border border-slate-700 rounded-xl p-6 text-left">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Terminal className="w-5 h-5 text-purple-400" />
              系统要求
            </h3>

            <div className="grid md:grid-cols-3 gap-6 text-sm">
              <div>
                <div className="text-white font-medium mb-2">Python</div>
                <div className="text-gray-400">Python 3.8+</div>
                <div className="text-gray-500 text-xs">pip install librosa soundfile</div>
              </div>

              <div>
                <div className="text-white font-medium mb-2">Node.js</div>
                <div className="text-gray-400">Node.js 18+</div>
                <div className="text-gray-500 text-xs">npm install</div>
              </div>

              <div>
                <div className="text-white font-medium mb-2">平台</div>
                <div className="text-gray-400">Mac / Linux / Windows</div>
                <div className="text-gray-500 text-xs">全平台支持</div>
              </div>
            </div>
          </div>

          {/* 快速开始 */}
          <div className="mt-8 bg-gradient-to-r from-purple-900/30 to-pink-900/30 border border-purple-500/30 rounded-xl p-6">
            <h3 className="text-xl font-bold text-white mb-4">
              快速开始（3 步）
            </h3>

            <div className="grid md:grid-cols-3 gap-4">
              <div className="bg-slate-950/50 rounded-lg p-4">
                <div className="text-2xl font-bold text-purple-400 mb-2">01</div>
                <div className="text-white font-medium mb-1">克隆仓库</div>
                <div className="text-xs text-gray-400 font-mono">git clone wuhuanqi/video-rhythm-cam</div>
              </div>

              <div className="bg-slate-950/50 rounded-lg p-4">
                <div className="text-2xl font-bold text-purple-400 mb-2">02</div>
                <div className="text-white font-medium mb-1">安装依赖</div>
                <div className="text-xs text-gray-400">pip install + npm install</div>
              </div>

              <div className="bg-slate-950/50 rounded-lg p-4">
                <div className="text-2xl font-bold text-purple-400 mb-2">03</div>
                <div className="text-white font-medium mb-1">启动服务</div>
                <div className="text-xs text-gray-400">python api.py + npm run dev</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
