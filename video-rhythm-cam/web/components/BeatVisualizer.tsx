"use client";

import { useMemo } from "react";
import { useRhythmCamStore } from "@/lib/store";

export function BeatVisualizer() {
  const { beatsData } = useRhythmCamStore();

  const stats = useMemo(() => {
    if (!beatsData || !beatsData.beats.length) {
      return null;
    }

    const strongBeats = beatsData.beats.filter((b) => b.strength > 0.6).length;
    const weakBeats = beatsData.beats.length - strongBeats;
    const avgStrength =
      beatsData.beats.reduce((sum, b) => sum + b.strength, 0) / beatsData.beats.length;

    return {
      total: beatsData.beats.length,
      strong: strongBeats,
      weak: weakBeats,
      avgStrength: avgStrength,
      bpm: beatsData.bpm,
    };
  }, [beatsData]);

  if (!stats) {
    return (
      <div className="p-4 bg-card rounded-lg border border-border">
        <p className="text-sm text-muted-foreground text-center">暂无节拍数据</p>
      </div>
    );
  }

  return (
    <div className="p-4 bg-card rounded-lg border border-border space-y-4">
      <h3 className="text-sm font-semibold">节拍统计</h3>

      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <p className="text-muted-foreground">总节拍数</p>
          <p className="text-2xl font-bold">{stats.total}</p>
        </div>
        <div>
          <p className="text-muted-foreground">BPM</p>
          <p className="text-2xl font-bold">{stats.bpm.toFixed(1)}</p>
        </div>
        <div>
          <p className="text-muted-foreground">重拍</p>
          <p className="text-lg font-semibold text-primary">{stats.strong}</p>
        </div>
        <div>
          <p className="text-muted-foreground">弱拍</p>
          <p className="text-lg font-semibold text-primary/50">{stats.weak}</p>
        </div>
      </div>

      <div>
        <p className="text-sm text-muted-foreground mb-2">平均强度</p>
        <div className="h-3 bg-secondary rounded-full overflow-hidden">
          <div
            className="h-full bg-primary transition-all duration-500"
            style={{ width: `${stats.avgStrength * 100}%` }}
          />
        </div>
        <p className="text-xs text-muted-foreground mt-1 text-right">
          {(stats.avgStrength * 100).toFixed(0)}%
        </p>
      </div>
    </div>
  );
}
