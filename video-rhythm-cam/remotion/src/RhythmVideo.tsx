import React, { useMemo } from "react";
import { AbsoluteFill, OffthreadVideo, useCurrentFrame, useVideoConfig, staticFile } from "remotion";
import { interpolate } from "remotion";

interface Beat {
  time: number;
  strength: number;
  frame: number;
}

interface BeatsData {
  bpm: number;
  duration: number;
  fps: number;
  beats: Beat[];
}

/**
 * 查找最近的节拍
 */
function findNearestBeat(frame: number, beats: Beat[]): Beat | null {
  if (!beats || beats.length === 0) return null;

  let nearestBeat: Beat | null = null;
  let minDistance = Infinity;

  for (const beat of beats) {
    const distance = Math.abs(frame - beat.frame);
    if (distance < minDistance) {
      minDistance = distance;
      nearestBeat = beat;
    }
  }

  return nearestBeat;
}

/**
 * 根据节拍数据计算当前帧的缩放比例
 */
function calculateScale(
  frame: number,
  beats: Beat[],
  fps: number,
  zoomDuration: number = 0.2 // 缩放持续时间（秒）
): number {
  const nearestBeat = findNearestBeat(frame, beats);

  if (!nearestBeat) return 1.0;

  const beatFrame = nearestBeat.frame;
  const zoomFrames = Math.round(zoomDuration * fps);

  // 检查是否在缩放窗口内
  const distanceFromBeat = frame - beatFrame;

  if (distanceFromBeat < 0 || distanceFromBeat > zoomFrames) {
    return 1.0;
  }

  // 根据节拍强度确定最大缩放
  // 重拍（强度>0.6）: 1.15 - 1.3
  // 弱拍（强度<=0.6）: 1.08 - 1.15
  const maxZoom = nearestBeat.strength > 0.6 ? 1.3 : 1.15;
  const minZoom = 1.0;

  // 在节拍处放大，然后衰减
  const progress = distanceFromBeat / zoomFrames;
  const scale = interpolate(progress, [0, 1], [maxZoom, minZoom], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  return scale;
}

/**
 * 主视频组件 - 应用节奏缩放效果
 */
export const RhythmVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // 从静态文件加载节拍数据
  const beatsData = useMemo(() => {
    try {
      // 在实际运行时，这个文件会由 Python 脚本动态生成
      const beatsDataJson = require("./beats.json");
      return beatsDataJson as BeatsData;
    } catch (error) {
      console.error("无法加载节拍数据:", error);
      return null;
    }
  }, []);

  // 如果没有节拍数据，直接显示视频
  if (!beatsData || !beatsData.beats || beatsData.beats.length === 0) {
    return (
      <AbsoluteFill style={{ backgroundColor: "black" }}>
        <OffthreadVideo src={staticFile("input.mp4")} />
      </AbsoluteFill>
    );
  }

  // 计算当前帧的缩放比例
  const scale = calculateScale(frame, beatsData.beats, fps, 0.2);

  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          transform: `scale(${scale})`,
          transformOrigin: "center",
        }}
      >
        <OffthreadVideo src={staticFile("input.mp4")} />
      </div>
    </AbsoluteFill>
  );
};
