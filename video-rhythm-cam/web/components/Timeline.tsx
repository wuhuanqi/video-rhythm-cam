"use client";

import { useEffect, useRef, useState } from "react";
import { useRhythmCamStore } from "@/lib/store";
import { Play, Pause } from "lucide-react";

export function Timeline() {
  const {
    currentVideo,
    beatsData,
    parameters,
    updateParameter,
  } = useRhythmCamStore();

  const [currentTime, setCurrentTime] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const animationRef = useRef<number>();
  const startTimeRef = useRef<number>();

  const duration = currentVideo?.duration || 0;
  const zoomDuration = parameters.zoomDuration * 1000; // 转换为毫秒

  // 播放控制
  const togglePlay = () => {
    if (isPlaying) {
      setIsPlaying(false);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    } else {
      setIsPlaying(true);
      startTimeRef.current = performance.now() - currentTime * 1000;
      animate();
    }
  };

  const animate = () => {
    const now = performance.now();
    const elapsed = now - (startTimeRef.current || 0);
    const newTime = Math.min(elapsed / 1000, duration);
    setCurrentTime(newTime);

    if (newTime < duration) {
      animationRef.current = requestAnimationFrame(animate);
    } else {
      setIsPlaying(false);
    }
  };

  // 清理
  useEffect(() => {
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  // 时间轴点击
  const handleTimelineClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = x / rect.width;
    const newTime = percentage * duration;
    setCurrentTime(newTime);

    if (isPlaying) {
      startTimeRef.current = performance.now() - newTime * 1000;
    }
  };

  if (!currentVideo || !beatsData) {
    return (
      <div className="h-full flex items-center justify-center text-muted-foreground">
        <div className="text-center">
          <p>请先选择视频并检测节奏</p>
        </div>
      </div>
    );
  }

  // 时间刻度
  const renderTimeMarkers = () => {
    const markers = [];
    const interval = duration > 60 ? 10 : duration > 30 ? 5 : 1;

    for (let t = 0; t <= duration; t += interval) {
      const percentage = (t / duration) * 100;
      markers.push(
        <div
          key={t}
          className="absolute top-0 h-full flex flex-col items-center"
          style={{ left: `${percentage}%` }}
        >
          <div className="h-2 w-px bg-border" />
          <span className="text-xs text-muted-foreground mt-1">
            {Math.floor(t / 60)}:{(t % 60).toString().padStart(2, "0")}
          </span>
        </div>
      );
    }
    return markers;
  };

  // 节奏点标记
  const renderBeatMarkers = () => {
    return beatsData.beats.map((beat, index) => {
      const percentage = (beat.time / duration) * 100;
      const isStrongBeat = beat.strength > 0.6;

      return (
        <div
          key={index}
          className="absolute top-8 bottom-0 w-0.5 bg-primary/50 hover:bg-primary transition-colors cursor-pointer group"
          style={{ left: `${percentage}%` }}
          title={`时间: ${beat.time.toFixed(2)}s, 强度: ${beat.strength.toFixed(2)}`}
        >
          <div
            className={`
              absolute -top-1 left-1/2 -translate-x-1/2 w-2 h-2 rounded-full
              ${isStrongBeat ? "bg-primary" : "bg-primary/50"}
              group-hover:scale-150 transition-transform
            `}
          />
        </div>
      );
    });
  };

  // 播放头
  const playheadPosition = (currentTime / duration) * 100;

  return (
    <div className="h-full flex flex-col bg-card p-4 overflow-hidden">
      {/* 顶部工具栏 */}
      <div className="flex-shrink-0 flex items-center justify-between mb-3">
        <div className="flex items-center gap-4">
          <button
            onClick={togglePlay}
            className="p-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
          >
            {isPlaying ? (
              <Pause className="w-5 h-5" />
            ) : (
              <Play className="w-5 h-5" />
            )}
          </button>

          <div className="text-sm">
            <span className="text-muted-foreground">时间: </span>
            <span className="font-mono">
              {Math.floor(currentTime / 60)}:{(currentTime % 60).toFixed(2).padStart(5, "0")}
            </span>
            <span className="text-muted-foreground mx-2">/</span>
            <span className="font-mono">
              {Math.floor(duration / 60)}:{(duration % 60).toFixed(2).padStart(5, "0")}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-4 text-sm">
          <div>
            <span className="text-muted-foreground">BPM: </span>
            <span className="font-mono">{beatsData.bpm.toFixed(1)}</span>
          </div>
          <div>
            <span className="text-muted-foreground">节拍数: </span>
            <span className="font-mono">{beatsData.beats.length}</span>
          </div>
        </div>
      </div>

      {/* 时间轴 - 使用 flex-1 和 overflow-hidden */}
      <div className="flex-1 relative overflow-hidden">
        <div
          className="absolute inset-0 bg-secondary rounded-lg overflow-hidden cursor-pointer select-none"
          onClick={handleTimelineClick}
        >
          {/* 时间刻度 */}
          {renderTimeMarkers()}

          {/* 节奏点标记 */}
          {renderBeatMarkers()}

          {/* 播放头 */}
          <div
            className="absolute top-0 bottom-0 w-0.5 bg-red-500 z-10 pointer-events-none"
            style={{ left: `${playheadPosition}%` }}
          >
            <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-3 h-3 bg-red-500 rounded-full" />
          </div>
        </div>
      </div>

      {/* 图例 */}
      <div className="flex items-center gap-6 mt-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-primary rounded-full" />
          <span className="text-muted-foreground">重拍 (> 0.6)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-primary/50 rounded-full" />
          <span className="text-muted-foreground">弱拍 (≤ 0.6)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-red-500 rounded-full" />
          <span className="text-muted-foreground">播放头</span>
        </div>
      </div>
    </div>
  );
}
