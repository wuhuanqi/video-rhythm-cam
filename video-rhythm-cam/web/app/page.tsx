"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Music,
  Video,
  Zap,
  Download,
  Play,
  Github,
  Star,
  ArrowRight,
  CheckCircle2,
  Sparkles,
  Workflow,
  Globe,
} from "lucide-react";

export default function Home() {
  const [email, setEmail] = useState("");

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950">
      {/* 导航栏 */}
      <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-lg bg-slate-950/80 border-b border-purple-500/20">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-purple-500 to-pink-500 p-2 rounded-lg">
              <Music className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">Video Rhythm Cam</h1>
              <p className="text-xs text-purple-300">让你的视频随音乐律动</p>
            </div>
          </div>

          <div className="flex items-center gap-6">
            <Link
              href="/docs"
              className="text-sm text-gray-300 hover:text-white transition-colors"
            >
              文档
            </Link>
            <Link
              href="/workbench"
              className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
            >
              <Play className="w-4 h-4" />
              开始使用
            </Link>
            <a
              href="https://github.com/wuhuanqi/video-rhythm-cam"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-300 hover:text-white transition-colors"
            >
              <Github className="w-5 h-5" />
            </a>
          </div>
        </div>
      </nav>

      {/* Hero 区域 */}
      <section className="pt-32 pb-20 px-4">
        <div className="container mx-auto text-center">
          {/* 徽章 */}
          <div className="inline-flex items-center gap-2 bg-purple-500/10 border border-purple-500/30 rounded-full px-4 py-2 mb-8">
            <Sparkles className="w-4 h-4 text-purple-400" />
            <span className="text-sm text-purple-300">
              开源 · 免费 · 基于 Remotion 4.0
            </span>
          </div>

          {/* 标题 */}
          <h1 className="text-6xl md:text-7xl font-bold text-white mb-6 leading-tight">
            让视频
            <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400 bg-clip-text text-transparent">
              {" "}随音乐律动
            </span>
          </h1>

          {/* 副标题 */}
          <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            自动识别音乐节拍，智能添加动态运镜效果。
            <br />
            让你的舞蹈、健身、音乐视频瞬间变得专业。
          </p>

          {/* CTA 按钮 */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <Link
              href="/workbench"
              className="group bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-8 py-4 rounded-xl text-lg font-semibold transition-all shadow-lg shadow-purple-500/30 hover:shadow-purple-500/50 flex items-center justify-center gap-2"
            >
              <Play className="w-5 h-5" />
              立即体验
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>

            <a
              href="https://github.com/wuhuanqi/video-rhythm-cam"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-slate-800 hover:bg-slate-700 text-white px-8 py-4 rounded-xl text-lg font-semibold transition-all border border-slate-700 flex items-center justify-center gap-2"
            >
              <Github className="w-5 h-5" />
              GitHub
            </a>
          </div>

          {/* 统计数据 */}
          <div className="flex flex-wrap justify-center gap-8 text-sm text-gray-400">
            <div className="flex items-center gap-2">
              <Star className="w-5 h-5 text-yellow-500" />
              <span>开源免费</span>
            </div>
            <div className="flex items-center gap-2">
              <Download className="w-5 h-5 text-purple-500" />
              <span>基于 Remotion 4.0</span>
            </div>
            <div className="flex items-center gap-2">
              <Globe className="w-5 h-5 text-blue-500" />
              <span>支持所有视频格式</span>
            </div>
          </div>
        </div>
      </section>

      {/* 功能特性 */}
      <section className="py-20 px-4 bg-slate-900/50">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">
              强大的功能特性
            </h2>
            <p className="text-gray-400 text-lg">
              一切都为了让你的视频更加出色
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* 特性 1 */}
            <div className="bg-slate-800/50 backdrop-blur-lg border border-slate-700 rounded-2xl p-8 hover:border-purple-500/50 transition-all group">
              <div className="bg-purple-500/10 w-14 h-14 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Music className="w-7 h-7 text-purple-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-3">
                智能节奏检测
              </h3>
              <p className="text-gray-400 leading-relaxed">
                使用 librosa 自动识别音乐节拍点，精准捕捉每一拍。
                区分重拍和弱拍，让效果更有层次感。
              </p>
            </div>

            {/* 特性 2 */}
            <div className="bg-slate-800/50 backdrop-blur-lg border border-slate-700 rounded-2xl p-8 hover:border-pink-500/50 transition-all group">
              <div className="bg-pink-500/10 w-14 h-14 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Video className="w-7 h-7 text-pink-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-3">
                动态运镜效果
              </h3>
              <p className="text-gray-400 leading-relaxed">
                在节拍处自动应用缩放效果，画面随音乐律动。
                基于 Remotion 4.0 渲染，输出高质量 MP4 视频。
              </p>
            </div>

            {/* 特性 3 */}
            <div className="bg-slate-800/50 backdrop-blur-lg border border-slate-700 rounded-2xl p-8 hover:border-blue-500/50 transition-all group">
              <div className="bg-blue-500/10 w-14 h-14 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Zap className="w-7 h-7 text-blue-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-3">
                简单易用
              </h3>
              <p className="text-gray-400 leading-relaxed">
                一行命令即可生成效果。支持批量处理，
                高质量输出。预览功能实时查看效果。
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 使用场景 */}
      <section className="py-20 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">
              适用于多种场景
            </h2>
            <p className="text-gray-400 text-lg">
              无论你想做什么样的视频，都能轻松驾驭
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { emoji: "💃", title: "舞蹈视频", desc: "让舞蹈动作更富有节奏感" },
              { emoji: "🏋️", title: "健身视频", desc: "配合音乐展现训练节奏" },
              { emoji: "🎤", title: "音乐视频", desc: "为 MV 添加专业运镜" },
              { emoji: "🎪", title: "表演视频", desc: "突出精彩瞬间" },
            ].map((item, index) => (
              <div
                key={index}
                className="bg-slate-800/30 backdrop-blur-lg border border-slate-700 rounded-xl p-6 text-center hover:border-purple-500/30 hover:bg-slate-800/50 transition-all"
              >
                <div className="text-5xl mb-4">{item.emoji}</div>
                <h3 className="text-lg font-bold text-white mb-2">
                  {item.title}
                </h3>
                <p className="text-sm text-gray-400">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 快速开始 */}
      <section className="py-20 px-4 bg-slate-900/50">
        <div className="container mx-auto">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-white mb-4">
                快速开始
              </h2>
              <p className="text-gray-400 text-lg">
                只需 3 步，即可让你的视频动起来
              </p>
            </div>

            <div className="space-y-6">
              {[
                {
                  step: "01",
                  title: "安装依赖",
                  code: "pip install librosa soundfile",
                  desc: "安装 Python 依赖包",
                },
                {
                  step: "02",
                  title: "运行处理",
                  code: "python rhythm_remotion.py dance.mp4",
                  desc: "一行命令，自动处理视频",
                },
                {
                  step: "03",
                  title: "享受效果",
                  code: "output.mp4",
                  desc: "得到带节奏运镜的视频",
                },
              ].map((item, index) => (
                <div
                  key={index}
                  className="bg-slate-800/50 backdrop-blur-lg border border-slate-700 rounded-2xl p-6 hover:border-purple-500/30 transition-all"
                >
                  <div className="flex items-start gap-6">
                    <div className="text-4xl font-bold text-purple-500/30">
                      {item.step}
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-white mb-2">
                        {item.title}
                      </h3>
                      <p className="text-gray-400 mb-4">{item.desc}</p>
                      <div className="bg-slate-900 rounded-lg p-4 font-mono text-sm text-purple-300 overflow-x-auto">
                        {item.code}
                      </div>
                    </div>
                    <CheckCircle2 className="w-6 h-6 text-green-500 flex-shrink-0" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA 区域 */}
      <section className="py-20 px-4">
        <div className="container mx-auto">
          <div className="bg-gradient-to-r from-purple-900/50 to-pink-900/50 backdrop-blur-lg border border-purple-500/30 rounded-3xl p-12 text-center">
            <h2 className="text-4xl font-bold text-white mb-4">
              准备好了吗？
            </h2>
            <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
              立即体验 Video Rhythm Cam，让你的视频随音乐律动起来
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/workbench"
                className="bg-white text-slate-900 hover:bg-gray-100 px-8 py-4 rounded-xl text-lg font-semibold transition-all flex items-center justify-center gap-2"
              >
                <Play className="w-5 h-5" />
                在线体验
              </Link>
              <Link
                href="/docs"
                className="bg-slate-800 hover:bg-slate-700 text-white px-8 py-4 rounded-xl text-lg font-semibold transition-all border border-slate-700 flex items-center justify-center gap-2"
              >
                <Workflow className="w-5 h-5" />
                查看文档
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* 页脚 */}
      <footer className="py-12 px-4 border-t border-slate-800">
        <div className="container mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-br from-purple-500 to-pink-500 p-2 rounded-lg">
                <Music className="w-5 h-5 text-white" />
              </div>
              <span className="text-white font-semibold">
                Video Rhythm Cam
              </span>
            </div>

            <div className="text-sm text-gray-400">
              基于{" "}
              <a
                href="https://www.remotion.dev/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-purple-400 hover:text-purple-300"
              >
                Remotion 4.0
              </a>{" "}
              构建
            </div>

            <div className="flex items-center gap-4">
              <a
                href="https://github.com/wuhuanqi/video-rhythm-cam"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-white transition-colors"
              >
                <Github className="w-5 h-5" />
              </a>
              <span className="text-sm text-gray-400">
                © 2026 Video Rhythm Cam
              </span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
