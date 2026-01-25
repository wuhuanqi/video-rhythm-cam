"use client";

import { useState } from "react";
import { ComparePlayer } from "@/components/ComparePlayer";
import { ControlPanel } from "@/components/ControlPanel";
import { Timeline } from "@/components/Timeline";
import { useRhythmCamStore } from "@/lib/store";
import { Music, ArrowLeft, Upload, FolderOpen } from "lucide-react";
import Link from "next/link";
import { VideoUploader } from "@/components/VideoUploader";

export default function AppPage() {
  const { currentVideo, setCurrentVideo } = useRhythmCamStore();
  const [showUploadModal, setShowUploadModal] = useState(false);

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

          {/* 右侧操作按钮 */}
          <div className="flex items-center gap-3">
            {/* 上传/更换视频按钮 */}
            <button
              onClick={() => setShowUploadModal(true)}
              className="flex items-center gap-2 bg-primary hover:bg-primary/90 text-primary-foreground px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            >
              <Upload className="w-4 h-4" />
              {currentVideo ? "更换视频" : "上传视频"}
            </button>

            <span className="text-sm text-muted-foreground">
              v2.0.0
            </span>
          </div>
        </div>
      </header>

      {/* 主内容区域 */}
      <div className="flex-1 flex flex-col min-h-0">
        {!currentVideo ? (
          // 空状态 - 没有视频时显示
          <div className="flex-1 flex items-center justify-center p-8">
            <div className="text-center max-w-2xl">
              {/* 大图标 */}
              <div className="inline-flex items-center justify-center w-24 h-24 bg-primary/10 rounded-full mb-6">
                <FolderOpen className="w-12 h-12 text-primary" />
              </div>

              {/* 标题 */}
              <h2 className="text-3xl font-bold text-white mb-4">
                开始创作你的节奏视频
              </h2>

              {/* 说明 */}
              <p className="text-gray-400 text-lg mb-8">
                上传视频文件，自动识别音乐节拍，添加动态运镜效果
              </p>

              {/* 上传按钮 */}
              <button
                onClick={() => setShowUploadModal(true)}
                className="inline-flex items-center gap-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-8 py-4 rounded-xl text-lg font-semibold transition-all shadow-lg shadow-purple-500/30 hover:shadow-purple-500/50"
              >
                <Upload className="w-5 h-5" />
                上传视频文件
              </button>

              {/* 支持格式 */}
              <p className="text-sm text-gray-500 mt-6">
                支持 MP4, MOV, AVI, MKV, WEBM 格式
              </p>
            </div>
          </div>
        ) : (
          // 编辑界面 - 有视频时显示
          <div className="flex-1 flex flex-col min-h-0">
            {/* 预览区域 */}
            <div className="h-[65vh] flex border-b border-border">
              {/* 视频播放器 */}
              <div className="flex-1 p-4">
                <ComparePlayer />
              </div>

              {/* 右侧：控制面板 */}
              <div className="w-80 border-l border-border p-4 overflow-y-auto">
                <ControlPanel />
              </div>
            </div>

            {/* 底部：时间轴 */}
            <div className="h-[35vh] border-t border-border">
              <Timeline />
            </div>
          </div>
        )}
      </div>

      {/* 上传模态框 */}
      {showUploadModal && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
          onClick={() => setShowUploadModal(false)}
        >
          <div
            className="bg-slate-900 border border-slate-700 rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            {/* 模态框头部 */}
            <div className="flex items-center justify-between p-6 border-b border-slate-700">
              <h2 className="text-2xl font-bold text-white">
                {currentVideo ? "更换视频" : "上传视频"}
              </h2>
              <button
                onClick={() => setShowUploadModal(false)}
                className="text-gray-400 hover:text-white transition-colors"
              >
                ✕
              </button>
            </div>

            {/* 模态框内容 - 上传组件 */}
            <div className="p-6">
              <VideoUploader
                onVideoUploaded={(video) => {
                  setCurrentVideo(video);
                  setShowUploadModal(false);
                }}
              />
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
