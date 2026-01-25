"use client";

import { useState } from "react";
import { useRhythmCamStore } from "@/lib/store";
import { Music, Download, RefreshCw, Settings } from "lucide-react";

export function ControlPanel() {
  const {
    currentVideo,
    beatsData,
    parameters,
    updateParameter,
    resetParameters,
    isProcessing,
    isExporting,
    exportProgress,
    setProcessing,
    setExporting,
    setError,
  } = useRhythmCamStore();

  const [showAdvanced, setShowAdvanced] = useState(false);

  // 检测节拍
  const handleDetectBeats = async () => {
    if (!currentVideo) return;

    setProcessing(true);
    setError(null);

    try {
      const response = await fetch("http://localhost:8000/api/detect-beats", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          videoPath: currentVideo.path,
          sensitivity: parameters.sensitivity,
        }),
      });

      if (!response.ok) {
        throw new Error("检测失败");
      }

      const result = await response.json();

      if (result.success && result.data) {
        // 更新 store 中的节奏数据
        useRhythmCamStore.getState().setBeatsData(result.data);
      } else {
        throw new Error(result.error || "检测失败");
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : "检测失败");
    } finally {
      setProcessing(false);
    }
  };

  // 导出视频
  const handleExport = async () => {
    if (!currentVideo || !beatsData) return;

    setExporting(true, 0);
    setError(null);

    try {
      // 调用后端导出API
      const response = await fetch("http://localhost:8000/api/export", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          videoPath: currentVideo.path,
          outputPath: "/tmp/output.mp4", // 后端会自动设置
          sensitivity: parameters.sensitivity,
          zoomMin: parameters.zoomMin,
          zoomMax: parameters.zoomMax,
          zoomDuration: parameters.zoomDuration,
          quality: parameters.quality,
        }),
      });

      if (!response.ok) {
        throw new Error("导出请求失败");
      }

      const result = await response.json();

      if (result.success && result.outputPath) {
        // 提取文件名
        const filename = result.outputPath.split("/").pop();

        // 下载视频
        const downloadUrl = `http://localhost:8000/api/download/${filename}`;
        const link = document.createElement("a");
        link.href = downloadUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        setExporting(false, 0);
        alert(`✅ 导出成功！文件已开始下载`);
      } else {
        throw new Error(result.error || "导出失败");
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : "导出失败");
      alert(`❌ ${error instanceof Error ? error.message : "导出失败"}`);
      setExporting(false, 0);
    }
  };

  return (
    <div className="space-y-6">
      {/* 视频信息 */}
      <div className="space-y-3">
        <h3 className="text-sm font-semibold flex items-center gap-2">
          <Music className="w-4 h-4" />
          视频信息
        </h3>
        {currentVideo && (
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">文件名:</span>
              <span className="font-mono truncate ml-2">{currentVideo.filename}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">时长:</span>
              <span className="font-mono">
                {Math.floor(currentVideo.duration / 60)}:{(currentVideo.duration % 60).toFixed(2).padStart(5, "0")}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">帧率:</span>
              <span className="font-mono">{currentVideo.fps.toFixed(1)} fps</span>
            </div>
          </div>
        )}
      </div>

      {/* 节奏检测 */}
      <div className="space-y-3">
        <h3 className="text-sm font-semibold flex items-center gap-2">
          <Music className="w-4 h-4" />
          节奏检测
        </h3>

        <div className="space-y-4">
          {/* 灵敏度 */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <label className="text-muted-foreground">灵敏度</label>
              <span className="font-mono">{parameters.sensitivity.toFixed(2)}</span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={parameters.sensitivity}
              onChange={(e) => updateParameter("sensitivity", parseFloat(e.target.value))}
              className="w-full h-2 bg-secondary rounded-lg appearance-none cursor-pointer accent-primary"
            />
          </div>

          {/* 检测按钮 */}
          <button
            onClick={handleDetectBeats}
            disabled={isProcessing}
            className="w-full py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
          >
            {isProcessing ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                检测中...
              </>
            ) : (
              <>
                <Music className="w-4 h-4" />
                检测节拍
              </>
            )}
          </button>
        </div>

        {/* 检测结果 */}
        {beatsData && (
          <div className="p-3 bg-secondary rounded-lg space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">BPM:</span>
              <span className="font-mono">{beatsData.bpm.toFixed(1)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">节拍数:</span>
              <span className="font-mono">{beatsData.beats.length}</span>
            </div>
          </div>
        )}
      </div>

      {/* 运镜参数 */}
      {beatsData && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold flex items-center gap-2">
              <Settings className="w-4 h-4" />
              运镜参数
            </h3>
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="text-xs text-muted-foreground hover:text-foreground transition-colors"
            >
              {showAdvanced ? "收起" : "展开"}
            </button>
          </div>

          <div className="space-y-4">
            {/* 最小缩放 */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <label className="text-muted-foreground">最小缩放</label>
                <span className="font-mono">{parameters.zoomMin.toFixed(1)}x</span>
              </div>
              <input
                type="range"
                min="1.0"
                max="1.5"
                step="0.05"
                value={parameters.zoomMin}
                onChange={(e) => updateParameter("zoomMin", parseFloat(e.target.value))}
                className="w-full h-2 bg-secondary rounded-lg appearance-none cursor-pointer accent-primary"
              />
            </div>

            {/* 最大缩放 */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <label className="text-muted-foreground">最大缩放</label>
                <span className="font-mono">{parameters.zoomMax.toFixed(1)}x</span>
              </div>
              <input
                type="range"
                min="1.1"
                max="2.0"
                step="0.05"
                value={parameters.zoomMax}
                onChange={(e) => updateParameter("zoomMax", parseFloat(e.target.value))}
                className="w-full h-2 bg-secondary rounded-lg appearance-none cursor-pointer accent-primary"
              />
            </div>

            {/* 缩放持续时间 */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <label className="text-muted-foreground">缩放持续时间</label>
                <span className="font-mono">{parameters.zoomDuration.toFixed(2)}s</span>
              </div>
              <input
                type="range"
                min="0.1"
                max="0.5"
                step="0.02"
                value={parameters.zoomDuration}
                onChange={(e) => updateParameter("zoomDuration", parseFloat(e.target.value))}
                className="w-full h-2 bg-secondary rounded-lg appearance-none cursor-pointer accent-primary"
              />
            </div>

            {showAdvanced && (
              <>
                {/* 质量设置 */}
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <label className="text-muted-foreground">输出质量</label>
                    <span className="font-mono">{parameters.quality}</span>
                  </div>
                  <input
                    type="range"
                    min="1"
                    max="100"
                    step="5"
                    value={parameters.quality}
                    onChange={(e) => updateParameter("quality", parseInt(e.target.value))}
                    className="w-full h-2 bg-secondary rounded-lg appearance-none cursor-pointer accent-primary"
                  />
                </div>

                {/* 重置按钮 */}
                <button
                  onClick={resetParameters}
                  className="w-full py-2 bg-secondary text-secondary-foreground rounded-lg hover:bg-secondary/80 transition-colors text-sm"
                >
                  重置参数
                </button>
              </>
            )}
          </div>
        </div>
      )}

      {/* 导出 */}
      {beatsData && (
        <div className="pt-4 border-t border-border">
          <button
            onClick={handleExport}
            disabled={isExporting}
            className="w-full py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2 font-medium"
          >
            {isExporting ? (
              <>
                <RefreshCw className="w-5 h-5 animate-spin" />
                导出中... {exportProgress}%
              </>
            ) : (
              <>
                <Download className="w-5 h-5" />
                导出视频
              </>
            )}
          </button>

          {isExporting && (
            <div className="mt-3">
              <div className="h-2 bg-secondary rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary transition-all duration-300"
                  style={{ width: `${exportProgress}%` }}
                />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
