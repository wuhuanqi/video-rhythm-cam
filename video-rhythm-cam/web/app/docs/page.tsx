"use client";

import Link from "next/link";
import {
  Music,
  ArrowLeft,
  BookOpen,
  Terminal,
  Download,
  Settings,
  Zap,
  Code,
  FileVideo,
  HelpCircle,
} from "lucide-react";

export default function DocsPage() {
  return (
    <div className="min-h-screen bg-slate-950">
      {/* 导航栏 */}
      <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-lg bg-slate-950/80 border-b border-purple-500/20">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link
              href="/"
              className="text-gray-400 hover:text-white transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-br from-purple-500 to-pink-500 p-2 rounded-lg">
                <Music className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">Video Rhythm Cam</h1>
                <p className="text-xs text-purple-300">文档中心</p>
              </div>
            </div>
          </div>

          <Link
            href="/app"
            className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            在线体验
          </Link>
        </div>
      </nav>

      {/* 内容区域 */}
      <div className="pt-24 pb-16 px-4">
        <div className="container mx-auto max-w-4xl">
          {/* 标题 */}
          <div className="mb-12">
            <div className="inline-flex items-center gap-2 bg-purple-500/10 border border-purple-500/30 rounded-full px-4 py-2 mb-6">
              <BookOpen className="w-4 h-4 text-purple-400" />
              <span className="text-sm text-purple-300">使用文档</span>
            </div>
            <h1 className="text-5xl font-bold text-white mb-4">
              快速开始指南
            </h1>
            <p className="text-xl text-gray-400">
              了解如何使用 Video Rhythm Cam 让你的视频随音乐律动
            </p>
          </div>

          {/* 文档章节 */}
          <div className="space-y-6">
            {/* 章节卡片 */}
            {[
              {
                icon: Download,
                title: "安装",
                description:
                  "了解如何安装 Video Rhythm Cam 及其依赖项",
                link: "#install",
                color: "purple",
              },
              {
                icon: Terminal,
                title: "基本使用",
                description: "学习如何处理你的第一个视频",
                link: "#usage",
                color: "blue",
              },
              {
                icon: Settings,
                title: "参数配置",
                description: "自定义节奏检测和缩放效果参数",
                link: "#config",
                color: "green",
              },
              {
                icon: Zap,
                title: "高级功能",
                description: "批量处理、高质量渲染等高级特性",
                link: "#advanced",
                color: "yellow",
              },
              {
                icon: Code,
                title: "API 参考",
                description: "完整的命令行参数和配置选项",
                link: "#api",
                color: "pink",
              },
              {
                icon: HelpCircle,
                title: "常见问题",
                description: "解答使用过程中的常见问题",
                link: "#faq",
                color: "red",
              },
            ].map((section, index) => (
              <Link
                key={index}
                href={section.link}
                className="block bg-slate-800/50 backdrop-blur-lg border border-slate-700 rounded-xl p-6 hover:border-purple-500/50 transition-all group"
              >
                <div className="flex items-start gap-4">
                  <div
                    className={`bg-${section.color}-500/10 w-12 h-12 rounded-lg flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform`}
                  >
                    <section.icon className={`w-6 h-6 text-${section.color}-400`} />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-white mb-2">
                      {section.title}
                    </h3>
                    <p className="text-gray-400">{section.description}</p>
                  </div>
                  <div className="text-gray-500 group-hover:text-purple-400 transition-colors">
                    →
                  </div>
                </div>
              </Link>
            ))}
          </div>

          {/* 快速开始 */}
          <div className="mt-16 bg-gradient-to-r from-purple-900/50 to-pink-900/50 backdrop-blur-lg border border-purple-500/30 rounded-2xl p-8">
            <h2 className="text-3xl font-bold text-white mb-4">
              30 秒快速开始
            </h2>

            <div className="space-y-4">
              <div className="bg-slate-900/50 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-purple-400 font-mono text-sm">1</span>
                  <span className="text-white font-semibold">安装依赖</span>
                </div>
                <div className="bg-slate-950 rounded p-3 font-mono text-sm text-purple-300">
                  pip install librosa soundfile numpy
                </div>
              </div>

              <div className="bg-slate-900/50 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-purple-400 font-mono text-sm">2</span>
                  <span className="text-white font-semibold">处理视频</span>
                </div>
                <div className="bg-slate-950 rounded p-3 font-mono text-sm text-purple-300">
                  python rhythm_remotion.py dance.mp4
                </div>
              </div>

              <div className="bg-slate-900/50 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-purple-400 font-mono text-sm">3</span>
                  <span className="text-white font-semibold">查看结果</span>
                </div>
                <div className="bg-slate-950 rounded p-3 font-mono text-sm text-purple-300">
                  output.mp4
                </div>
              </div>
            </div>
          </div>

          {/* 参数说明 */}
          <div className="mt-12">
            <h2 className="text-3xl font-bold text-white mb-6">
              常用参数
            </h2>

            <div className="bg-slate-800/50 backdrop-blur-lg border border-slate-700 rounded-xl overflow-hidden">
              <table className="w-full">
                <thead className="bg-slate-900/50">
                  <tr>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-white">
                      参数
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-white">
                      说明
                    </th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-white">
                      默认值
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700">
                  {[
                    {
                      param: "-s, --sensitivity",
                      desc: "节拍检测灵敏度",
                      default: "0.5",
                    },
                    {
                      param: "--zoom-min",
                      desc: "最小缩放比例",
                      default: "1.0",
                    },
                    {
                      param: "--zoom-max",
                      desc: "最大缩放比例",
                      default: "1.3",
                    },
                    {
                      param: "--zoom-duration",
                      desc: "缩放持续时间（秒）",
                      default: "0.2",
                    },
                    {
                      param: "--quality",
                      desc: "渲染质量（1-100）",
                      default: "90",
                    },
                  ].map((item, index) => (
                    <tr key={index} className="hover:bg-slate-700/30">
                      <td className="px-6 py-4 font-mono text-sm text-purple-300">
                        {item.param}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-300">
                        {item.desc}
                      </td>
                      <td className="px-6 py-4 font-mono text-sm text-gray-400">
                        {item.param}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
