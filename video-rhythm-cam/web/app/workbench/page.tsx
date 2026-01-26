"use client";

import { useState } from "react";
import { Music, ArrowLeft, Github } from "lucide-react";
import Link from "next/link";
import { VideoUploader } from "@/components/VideoUploader";
import { ControlPanel } from "@/components/ControlPanel";
import { AudioAlignmentPanel } from "@/components/AudioAlignmentPanel";
import { BeatVisualizer } from "@/components/BeatVisualizer";
import { Timeline } from "@/components/Timeline";
import { PreviewPlayer } from "@/components/PreviewPlayer";
import { useRhythmCamStore } from "@/lib/store";

export default function WorkbenchPage() {
  const { currentVideo, beatsData } = useRhythmCamStore();
  const [showAudioAlignment, setShowAudioAlignment] = useState(false);

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
                <p className="text-xs text-muted-foreground">音频对齐工作台</p>
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
      <div className="flex-1 flex overflow-hidden">
        {/* 左侧边栏 */}
        <aside className="w-80 border-r border-border bg-card overflow-y-auto">
          <div className="p-4 space-y-6">
            {/* 视频上传 */}
            <VideoUploader />

            {/* 切换按钮 */}
            {currentVideo && (
              <div className="flex gap-2">
                <button
                  onClick={() => setShowAudioAlignment(false)}
                  className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
                    !showAudioAlignment
                      ? "bg-primary text-primary-foreground"
                      : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
                  }`}
                >
                  节奏运镜
                </button>
                <button
                  onClick={() => setShowAudioAlignment(true)}
                  className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
                    showAudioAlignment
                      ? "bg-primary text-primary-foreground"
                      : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
                  }`}
                >
                  音频对齐
                </button>
              </div>
            )}

            {/* 控制面板 */}
            {currentVideo && !showAudioAlignment && <ControlPanel />}

            {/* 音频对齐面板 */}
            {currentVideo && showAudioAlignment && <AudioAlignmentPanel />}
          </div>
        </aside>

        {/* 主工作区 */}
        <main className="flex-1 flex flex-col overflow-hidden">
          {currentVideo ? (
            <>
              {/* 视频预览和节拍可视化 */}
              <div className="flex-1 overflow-y-auto p-6">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full">
                  {/* 预览播放器 */}
                  <div className="space-y-4">
                    <h2 className="text-lg font-semibold text-white">视频预览</h2>
                    <div className="bg-black rounded-lg overflow-hidden aspect-video">
                      <PreviewPlayer />
                    </div>
                  </div>

                  {/* 节拍可视化 */}
                  <div className="space-y-4">
                    <h2 className="text-lg font-semibold text-white">节拍分析</h2>
                    <div className="bg-card rounded-lg p-4 h-[calc(100%-3rem)]">
                      <BeatVisualizer />
                    </div>
                  </div>
                </div>
              </div>

              {/* 时间轴 */}
              {beatsData && (
                <div className="border-t border-border bg-card p-4">
                  <Timeline />
                </div>
              )}
            </>
          ) : (
            /* 空状态 */
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <div className="bg-primary/10 w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Music className="w-10 h-10 text-primary" />
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  开始创作
                </h3>
                <p className="text-muted-foreground max-w-md">
                  上传你的舞蹈视频，使用音频对齐功能替换为高质量音频，
                  或者使用节奏运镜功能添加动态效果
                </p>
              </div>
            </div>
          )}
        </main>
      </div>
    </main>
  );
}
