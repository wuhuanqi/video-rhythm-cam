"use client";

import { useRef, useState, useEffect, useMemo, useCallback } from "react";
import { useRhythmCamStore } from "@/lib/store";

export function ComparePlayer() {
  const {
    currentVideo,
    beatsData,
    parameters,
  } = useRhythmCamStore();

  const [currentTime, setCurrentTime] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [scale, setScale] = useState(1.0);
  const [showOriginal, setShowOriginal] = useState(false); // 新增：切换显示原始/效果视频
  const [isFullscreen, setIsFullscreen] = useState(false);

  const videoRef = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const animationFrameRef = useRef<number>();

  // 简化的缩放计算 - 使用更可靠的算法
  const calculateScale = useCallback((time: number) => {
    if (!beatsData || !beatsData.beats.length) {
      return 1.0;
    }

    const fps = beatsData.fps;
    const currentFrame = Math.floor(time * fps);
    const zoomFrames = Math.round(parameters.zoomDuration * fps);

    // 找到最近的一个节拍（使用简单的线性搜索）
    let nearestBeat = null;
    let minDistance = Infinity;

    for (const beat of beatsData.beats) {
      const distance = Math.abs(currentFrame - beat.frame);
      if (distance < minDistance) {
        minDistance = distance;
        nearestBeat = beat;
      }
    }

    if (!nearestBeat) return 1.0;

    // 计算当前帧相对于节拍帧的距离
    const distanceFromBeat = currentFrame - nearestBeat.frame;

    // 只在节拍后的 zoomFrames 范围内应用缩放
    if (distanceFromBeat < 0 || distanceFromBeat > zoomFrames) {
      return 1.0;
    }

    // 根据节拍强度和距离计算缩放
    const maxZoom = nearestBeat.strength > 0.6 ? parameters.zoomMax : 1.15;
    const minZoom = parameters.zoomMin;
    const progress = distanceFromBeat / zoomFrames;

    // 线性衰减：从 maxZoom 逐渐减小到 minZoom
    return maxZoom - (maxZoom - minZoom) * progress;
  }, [beatsData, parameters]);

  // 大幅降低更新频率：每 200ms 更新一次（5fps）
  // 始终计算缩放，无论显示哪个视频
  const lastUpdateTimeRef = useRef(0);
  useEffect(() => {
    const now = performance.now();
    if (now - lastUpdateTimeRef.current > 200) {
      const s = calculateScale(currentTime);
      setScale(s);
      lastUpdateTimeRef.current = now;
    }
  }, [currentTime, calculateScale]);

  // 简化的时间更新
  const lastTimeUpdateRef = useRef(0);
  const handleTimeUpdate = useCallback(() => {
    const now = performance.now();
    if (now - lastTimeUpdateRef.current > 100) {
      setCurrentTime(videoRef.current?.currentTime || 0);
      lastTimeUpdateRef.current = now;
    }
  }, []);

  // 播放控制
  const togglePlay = useCallback(() => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play().catch(err => {
          console.error("播放失败:", err);
        });
      }
      setIsPlaying(!isPlaying);
    }
  }, [isPlaying]);

  // 全屏控制 - 全屏包含缩放效果的容器
  const toggleFullscreen = useCallback(() => {
    if (!containerRef.current) return;

    if (!isFullscreen) {
      // 进入全屏
      if (containerRef.current.requestFullscreen) {
        containerRef.current.requestFullscreen();
      } else if ((containerRef.current as any).webkitRequestFullscreen) {
        (containerRef.current as any).webkitRequestFullscreen();
      } else if ((containerRef.current as any).mozRequestFullScreen) {
        (containerRef.current as any).mozRequestFullScreen();
      }
    } else {
      // 退出全屏
      if (document.exitFullscreen) {
        document.exitFullscreen();
      } else if ((document as any).webkitExitFullscreen) {
        (document as any).webkitExitFullscreen();
      } else if ((document as any).mozCancelFullScreen) {
        (document as any).mozCancelFullScreen();
      }
    }
  }, [isFullscreen]);

  // 监听全屏变化
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener("fullscreenchange", handleFullscreenChange);
    return () => {
      document.removeEventListener("fullscreenchange", handleFullscreenChange);
    };
  }, []);

  if (!currentVideo) {
    return (
      <div className="h-full flex items-center justify-center bg-card rounded-lg border border-border">
        <div className="text-center text-muted-foreground">
          <p>请先上传视频</p>
        </div>
      </div>
    );
  }

  const duration = currentVideo.duration || 0;

  return (
    <div className="h-full flex flex-col bg-card rounded-lg border border-border overflow-hidden">
      {/* 标题栏 */}
      <div className="flex-shrink-0 flex items-center justify-between px-4 py-2 border-b border-border bg-muted/50">
        <div className="flex items-center gap-4">
          <h3 className="text-sm font-semibold">
            {showOriginal ? "原始视频" : "节奏运镜效果"}
          </h3>
          <div className="flex items-center gap-2">
            <label className="text-xs text-muted-foreground">显示:</label>
            <select
              value={showOriginal ? "original" : "effect"}
              onChange={(e) => setShowOriginal(e.target.value === "original")}
              className="px-2 py-1 text-xs bg-background border border-border rounded"
            >
              <option value="effect">效果视频</option>
              <option value="original">原始视频</option>
            </select>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span>缩放: {scale.toFixed(2)}x</span>
        </div>
      </div>

      {/* 视频区域 - 只显示一个视频 */}
      <div
        ref={containerRef}
        className="flex-1 relative bg-black rounded-lg overflow-hidden min-h-0"
      >
        <div className="absolute inset-0 flex items-center justify-center p-2">
          {/* 统一的视频容器结构 - 无论是原始视频还是效果视频 */}
          <div
            className="transition-transform duration-200 ease-out will-change-transform"
            style={{
              transform: showOriginal ? "scale(1.0)" : `scale(${scale.toFixed(3)})`,
              transformOrigin: "center",
              backfaceVisibility: "hidden",
              WebkitHardwareAccelerated: true,
            } as React.CSSProperties}
          >
            <video
              ref={videoRef}
              src={`http://localhost:8000/videos/${encodeURIComponent(currentVideo.filename)}`}
              className="max-h-full max-w-full object-contain"
              preload="auto"
              playsInline
              style={{ WebkitHardwareAccelerated: true } as React.CSSProperties}
              onTimeUpdate={handleTimeUpdate}
              onPlay={() => setIsPlaying(true)}
              onPause={() => setIsPlaying(false)}
            />
          </div>
        </div>

        {/* 缩放指示器 */}
        {!showOriginal && scale > 1.0 && (
          <div className="absolute top-4 right-4 bg-primary/90 text-white px-3 py-1 rounded-full text-sm font-medium">
            缩放: {scale.toFixed(2)}x
          </div>
        )}

        {/* 自定义全屏按钮 */}
        <button
          onClick={toggleFullscreen}
          className="absolute bottom-4 right-4 p-2 bg-black/60 text-white rounded-lg hover:bg-black/80 transition-colors"
          title={isFullscreen ? "退出全屏" : "全屏"}
        >
          {isFullscreen ? (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          ) : (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
            </svg>
          )}
        </button>
      </div>

      {/* 控制栏 */}
      <div className="flex-shrink-0 h-14 border-t border-border flex items-center justify-between px-4 bg-muted/30">
        <div className="flex items-center gap-4">
          {/* 播放/暂停按钮 */}
          <button
            onClick={togglePlay}
            className="p-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
          >
            {isPlaying ? (
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M5 4h3v12H5V4zm7 0h3v12h-3V4z" />
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M6 4l10 6-10 6V4z" />
              </svg>
            )}
          </button>

          {/* 当前时间 */}
          <div className="font-mono text-sm">
            {Math.floor(currentTime / 60)}:{(currentTime % 60).toFixed(1).padStart(4, "0")}
            {" / "}
            {Math.floor(duration / 60)}:{(duration % 60).toFixed(1).padStart(4, "0")}
          </div>
        </div>

        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span>缩放范围:</span>
          <span className="font-mono">{parameters.zoomMin.toFixed(1)}x - {parameters.zoomMax.toFixed(1)}x</span>
        </div>
      </div>
    </div>
  );
}
