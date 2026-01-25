"use client";

import { useRef, useState, useEffect } from "react";
import { useRhythmCamStore } from "@/lib/store";

export function PreviewPlayer() {
  const {
    currentVideo,
    beatsData,
    parameters,
    previewUrl,
    setPreviewUrl,
  } = useRhythmCamStore();

  const [currentTime, setCurrentTime] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [scale, setScale] = useState(1.0);
  const [videoError, setVideoError] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  // 计算当前缩放
  useEffect(() => {
    if (!beatsData || !beatsData.beats.length) {
      setScale(1.0);
      return;
    }

    // 查找最近的节拍
    const fps = beatsData.fps;
    const currentFrame = Math.floor(currentTime * fps);

    let nearestBeat = null;
    let minDistance = Infinity;

    for (const beat of beatsData.beats) {
      const distance = Math.abs(currentFrame - beat.frame);
      if (distance < minDistance) {
        minDistance = distance;
        nearestBeat = beat;
      }
    }

    if (!nearestBeat) {
      setScale(1.0);
      return;
    }

    const beatFrame = nearestBeat.frame;
    const zoomFrames = Math.round(parameters.zoomDuration * fps);
    const distanceFromBeat = currentFrame - beatFrame;

    if (distanceFromBeat < 0 || distanceFromBeat > zoomFrames) {
      setScale(1.0);
      return;
    }

    // 根据节拍强度确定最大缩放
    const maxZoom = nearestBeat.strength > 0.6 ? parameters.zoomMax : 1.15;
    const minZoom = parameters.zoomMin;

    // 线性插值
    const progress = distanceFromBeat / zoomFrames;
    const newScale = maxZoom - (maxZoom - minZoom) * progress;

    setScale(newScale);
  }, [currentTime, beatsData, parameters]);

  // 视频时间更新
  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime);
    }
  };

  // 播放控制
  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play().catch(err => {
          console.error("播放失败:", err);
          setVideoError(`播放失败: ${err.message}`);
        });
      }
      setIsPlaying(!isPlaying);
    }
  };

  // 视频加载错误处理
  const handleVideoError = () => {
    if (videoRef.current) {
      const error = videoRef.current.error;
      console.error("视频加载错误:", error);
      setVideoError(`视频加载失败: ${error?.message || '未知错误'}`);
    }
  };

  if (!currentVideo) {
    return (
      <div className="h-full flex items-center justify-center bg-card rounded-lg border border-border">
        <div className="text-center text-muted-foreground">
          <p>请先上传视频</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-card rounded-lg border border-border overflow-hidden">
      {/* 视频预览区域 */}
      <div className="flex-1 relative flex items-center justify-center bg-black">
        <div
          className="relative transition-transform duration-75 ease-out"
          style={{
            transform: `scale(${scale})`,
            transformOrigin: "center",
          }}
        >
          {/* 这里应该显示实际视频，使用 file:// 协议或通过服务提供 */}
          <video
            ref={videoRef}
            src={`http://localhost:8000/videos/${encodeURIComponent(currentVideo.filename)}`}
            className="max-h-full max-w-full"
            onTimeUpdate={handleTimeUpdate}
            onPlay={() => setIsPlaying(true)}
            onPause={() => setIsPlaying(false)}
            onError={handleVideoError}
            controls
          />
        </div>

        {/* 错误提示 */}
        {videoError && (
          <div className="absolute top-4 left-4 bg-destructive text-destructive-foreground px-4 py-2 rounded-lg text-sm">
            {videoError}
          </div>
        )}

        {/* 缩放指示器 */}
        {scale > 1.0 && (
          <div className="absolute top-4 right-4 bg-primary/90 text-primary-foreground px-3 py-1 rounded-full text-sm font-medium">
            缩放: {scale.toFixed(2)}x
          </div>
        )}
      </div>

      {/* 控制栏 */}
      <div className="h-16 border-t border-border flex items-center justify-between px-4">
        <div className="flex items-center gap-4">
          {/* 播放/暂停按钮 */}
          <button
            onClick={togglePlay}
            className="p-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
          >
            {isPlaying ? (
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M5 4h3v12H5V4zm7 0h3v12h-3V4z" />
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M6 4l10 6-10 6V4z" />
              </svg>
            )}
          </button>

          {/* 当前时间 */}
          <div className="font-mono text-sm">
            {Math.floor(currentTime / 60)}:{(currentTime % 60).toFixed(2).padStart(5, "0")}
            {" / "}
            {Math.floor((currentVideo.duration || 0) / 60)}:{((currentVideo.duration || 0) % 60).toFixed(2).padStart(5, "0")}
          </div>
        </div>

        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <span>缩放范围: {parameters.zoomMin.toFixed(1)}x - {parameters.zoomMax.toFixed(1)}x</span>
        </div>
      </div>
    </div>
  );
}
