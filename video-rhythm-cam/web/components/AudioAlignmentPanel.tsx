"use client";

import { useState } from "react";
import { useRhythmCamStore } from "@/lib/store";
import { Music, Upload, RefreshCw, CheckCircle } from "lucide-react";

export function AudioAlignmentPanel() {
  const {
    currentVideo,
    referenceVideo,
    setReferenceVideo,
    isAligning,
    setAligning,
    setError,
  } = useRhythmCamStore();

  const [isUploading, setIsUploading] = useState(false);
  const [alignResult, setAlignResult] = useState<{ success: boolean; offset?: number; message?: string } | null>(null);

  // 上传参考视频
  const handleUploadReference = async (file: File) => {
    if (!currentVideo) {
      alert("请先上传舞蹈视频");
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("http://localhost:8000/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("上传失败");
      }

      const result = await response.json();

      if (result.success) {
        setReferenceVideo({
          filename: result.filename,
          path: result.path,
          duration: result.duration,
          fps: result.fps,
          size: 0, // 不需要 size
        });
        setAlignResult(null);
      } else {
        throw new Error(result.error || "上传失败");
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : "上传失败");
      alert(`❌ ${error instanceof Error ? error.message : "上传失败"}`);
    } finally {
      setIsUploading(false);
    }
  };

  // 对齐音频
  const handleAlignAudio = async () => {
    if (!currentVideo || !referenceVideo) {
      alert("请先上传舞蹈视频和参考视频");
      return;
    }

    setAligning(true);
    setError(null);
    setAlignResult(null);

    try {
      const response = await fetch("http://localhost:8000/api/align-audio", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          danceVideoPath: currentVideo.path,
          referenceVideoPath: referenceVideo.path,
          maxOffset: 5.0,
        }),
      });

      if (!response.ok) {
        throw new Error("对齐失败");
      }

      const result = await response.json();

      if (result.success && result.outputPath) {
        // 提取文件名
        const filename = result.outputPath.split("/").pop();

        // 下载视频
        const downloadUrl = `http://localhost:8000/api/download/${filename}`;
        const link = document.createElement("a");
        link.href = downloadUrl;
        link.download = filename || "aligned_video.mp4";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        setAlignResult({
          success: true,
          offset: result.offset,
          message: `✅ 音频对齐成功！偏移量: ${result.offset?.toFixed(3)} 秒`,
        });
      } else {
        throw new Error(result.error || "对齐失败");
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : "对齐失败";
      setError(errorMsg);
      setAlignResult({
        success: false,
        message: `❌ ${errorMsg}`,
      });
      alert(`❌ ${errorMsg}`);
    } finally {
      setAligning(false);
    }
  };

  // 文件输入处理
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleUploadReference(file);
    }
  };

  return (
    <div className="space-y-6">
      {/* 参考视频上传 */}
      <div className="space-y-3">
        <h3 className="text-sm font-semibold flex items-center gap-2">
          <Music className="w-4 h-4" />
          参考视频（高质量音频）
        </h3>
        <p className="text-xs text-muted-foreground">
          上传一个包含同一首音乐的参考视频，系统会自动对齐音频并替换到舞蹈视频中
        </p>

        <div className="space-y-3">
          {/* 上传按钮 */}
          <label className="block">
            <input
              type="file"
              accept="video/*"
              onChange={handleFileChange}
              disabled={isUploading || isAligning}
              className="hidden"
              id="reference-video-upload"
            />
            <label
              htmlFor="reference-video-upload"
              className={`flex items-center justify-center gap-2 w-full py-3 border-2 border-dashed border-border rounded-lg cursor-pointer hover:border-primary hover:bg-primary/5 transition-colors ${
                isUploading || isAligning ? "opacity-50 cursor-not-allowed" : ""
              }`}
            >
              {isUploading ? (
                <>
                  <RefreshCw className="w-5 h-5 animate-spin" />
                  上传中...
                </>
              ) : (
                <>
                  <Upload className="w-5 h-5" />
                  {referenceVideo ? "更换参考视频" : "上传参考视频"}
                </>
              )}
            </label>
          </label>

          {/* 参考视频信息 */}
          {referenceVideo && (
            <div className="p-3 bg-secondary rounded-lg space-y-2 text-sm">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span className="font-medium">已上传参考视频</span>
              </div>
              <div className="space-y-1 text-xs">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">文件名:</span>
                  <span className="font-mono truncate ml-2">{referenceVideo.filename}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">时长:</span>
                  <span className="font-mono">
                    {Math.floor(referenceVideo.duration / 60)}:{(referenceVideo.duration % 60).toFixed(2).padStart(5, "0")}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 对齐按钮 */}
      {referenceVideo && (
        <div className="space-y-3">
          <button
            onClick={handleAlignAudio}
            disabled={isAligning}
            className="w-full py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2 font-medium"
          >
            {isAligning ? (
              <>
                <RefreshCw className="w-5 h-5 animate-spin" />
                对齐中...
              </>
            ) : (
              <>
                <Music className="w-5 h-5" />
                对齐音频并合成
              </>
            )}
          </button>

          {/* 对齐结果 */}
          {alignResult && (
            <div className={`p-3 rounded-lg text-sm ${alignResult.success ? "bg-green-500/10 text-green-500" : "bg-red-500/10 text-red-500"}`}>
              {alignResult.message}
            </div>
          )}
        </div>
      )}

      {/* 说明 */}
      <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg text-xs text-blue-500 space-y-1">
        <p className="font-medium">💡 使用说明：</p>
        <ul className="space-y-1 ml-4 list-disc">
          <li>参考视频应包含与舞蹈视频同一首音乐</li>
          <li>系统会自动计算两个音频的时间偏移量</li>
          <li>对齐后会自动下载合成后的视频</li>
        </ul>
      </div>
    </div>
  );
}
