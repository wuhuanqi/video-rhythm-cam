"use client";

import { useState } from "react";
import { useRhythmCamStore } from "@/lib/store";
import { Music, Upload, RefreshCw, CheckCircle, Video, ArrowDown } from "lucide-react";

export function AudioAlignmentPanel() {
  const {
    currentVideo,
    referenceVideo,
    setCurrentVideo,
    setReferenceVideo,
    isAligning,
    setAligning,
    setError,
  } = useRhythmCamStore();

  const [isUploadingDance, setIsUploadingDance] = useState(false);
  const [isUploadingRef, setIsUploadingRef] = useState(false);
  const [alignResult, setAlignResult] = useState<{ success: boolean; offset?: number; message?: string } | null>(null);

  // 上传舞蹈视频
  const handleUploadDance = async (file: File) => {
    setIsUploadingDance(true);
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
        setCurrentVideo({
          filename: result.filename,
          path: result.path,
          duration: result.duration,
          fps: result.fps,
          size: 0,
        });
        setAlignResult(null);
      } else {
        throw new Error(result.error || "上传失败");
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : "上传失败");
      alert(`❌ ${error instanceof Error ? error.message : "上传失败"}`);
    } finally {
      setIsUploadingDance(false);
    }
  };

  // 上传参考视频
  const handleUploadReference = async (file: File) => {
    setIsUploadingRef(true);
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
          size: 0,
        });
        setAlignResult(null);
      } else {
        throw new Error(result.error || "上传失败");
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : "上传失败");
      alert(`❌ ${error instanceof Error ? error.message : "上传失败"}`);
    } finally {
      setIsUploadingRef(false);
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
        const filename = result.outputPath.split("/").pop();

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

  return (
    <div className="space-y-4">
      {/* 步骤说明 */}
      <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg text-xs text-blue-500">
        <p className="font-medium mb-2">🎯 音频对齐功能</p>
        <p>用参考视频的高质量音频替换你舞蹈视频的音频，系统会自动对齐卡点。</p>
      </div>

      {/* 第一步：舞蹈视频 */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <span className="flex items-center justify-center w-5 h-5 rounded-full bg-primary text-primary-foreground text-xs font-bold">1</span>
          <h3 className="text-sm font-semibold flex items-center gap-2">
            <Video className="w-4 h-4" />
            舞蹈视频（你的录制）
          </h3>
        </div>
        <p className="text-xs text-muted-foreground ml-7">
          你自己拍的舞蹈视频，音质可能不太好
        </p>

        <div className="ml-7">
          <input
            type="file"
            accept="video/*"
            onChange={(e) => e.target.files?.[0] && handleUploadDance(e.target.files[0])}
            disabled={isUploadingDance || isAligning}
            className="hidden"
            id="dance-video-upload"
          />
          <label
            htmlFor="dance-video-upload"
            className={`flex items-center justify-center gap-2 w-full py-3 border-2 border-dashed border-orange-500/50 rounded-lg cursor-pointer hover:border-orange-500 hover:bg-orange-500/5 transition-colors ${
              isUploadingDance || isAligning ? "opacity-50 cursor-not-allowed" : ""
            }`}
          >
            {isUploadingDance ? (
              <>
                <RefreshCw className="w-5 h-5 animate-spin text-orange-500" />
                <span className="text-orange-500">上传中...</span>
              </>
            ) : (
              <>
                <Upload className="w-5 h-5 text-orange-500" />
                <span className="text-orange-500">{currentVideo ? "更换舞蹈视频" : "上传舞蹈视频"}</span>
              </>
            )}
          </label>

          {currentVideo && (
            <div className="mt-2 p-2 bg-orange-500/10 rounded-lg text-xs">
              <div className="flex items-center gap-2 text-orange-500">
                <CheckCircle className="w-4 h-4" />
                <span className="font-medium truncate">{currentVideo.filename}</span>
              </div>
              <div className="text-muted-foreground mt-1">
                时长: {Math.floor(currentVideo.duration / 60)}:{(currentVideo.duration % 60).toFixed(1).padStart(4, "0")}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 箭头 */}
      <div className="flex justify-center">
        <ArrowDown className="w-5 h-5 text-muted-foreground" />
      </div>

      {/* 第二步：参考视频 */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <span className="flex items-center justify-center w-5 h-5 rounded-full bg-primary text-primary-foreground text-xs font-bold">2</span>
          <h3 className="text-sm font-semibold flex items-center gap-2">
            <Music className="w-4 h-4" />
            参考视频（高质量音频）
          </h3>
        </div>
        <p className="text-xs text-muted-foreground ml-7">
          同一首歌的MV或其他高音质视频，用来提取音频
        </p>

        <div className="ml-7">
          <input
            type="file"
            accept="video/*"
            onChange={(e) => e.target.files?.[0] && handleUploadReference(e.target.files[0])}
            disabled={isUploadingRef || isAligning}
            className="hidden"
            id="reference-video-upload"
          />
          <label
            htmlFor="reference-video-upload"
            className={`flex items-center justify-center gap-2 w-full py-3 border-2 border-dashed border-green-500/50 rounded-lg cursor-pointer hover:border-green-500 hover:bg-green-500/5 transition-colors ${
              isUploadingRef || isAligning ? "opacity-50 cursor-not-allowed" : ""
            }`}
          >
            {isUploadingRef ? (
              <>
                <RefreshCw className="w-5 h-5 animate-spin text-green-500" />
                <span className="text-green-500">上传中...</span>
              </>
            ) : (
              <>
                <Upload className="w-5 h-5 text-green-500" />
                <span className="text-green-500">{referenceVideo ? "更换参考视频" : "上传参考视频"}</span>
              </>
            )}
          </label>

          {referenceVideo && (
            <div className="mt-2 p-2 bg-green-500/10 rounded-lg text-xs">
              <div className="flex items-center gap-2 text-green-500">
                <CheckCircle className="w-4 h-4" />
                <span className="font-medium truncate">{referenceVideo.filename}</span>
              </div>
              <div className="text-muted-foreground mt-1">
                时长: {Math.floor(referenceVideo.duration / 60)}:{(referenceVideo.duration % 60).toFixed(1).padStart(4, "0")}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 箭头 */}
      <div className="flex justify-center">
        <ArrowDown className="w-5 h-5 text-muted-foreground" />
      </div>

      {/* 第三步：对齐按钮 */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <span className="flex items-center justify-center w-5 h-5 rounded-full bg-primary text-primary-foreground text-xs font-bold">3</span>
          <h3 className="text-sm font-semibold">开始对齐</h3>
        </div>

        <div className="ml-7">
          <button
            onClick={handleAlignAudio}
            disabled={!currentVideo || !referenceVideo || isAligning}
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

          {!currentVideo && !referenceVideo && (
            <p className="text-xs text-muted-foreground mt-2 text-center">请先上传两个视频</p>
          )}
          {currentVideo && !referenceVideo && (
            <p className="text-xs text-muted-foreground mt-2 text-center">请上传参考视频</p>
          )}
          {!currentVideo && referenceVideo && (
            <p className="text-xs text-muted-foreground mt-2 text-center">请上传舞蹈视频</p>
          )}

          {alignResult && (
            <div className={`mt-3 p-3 rounded-lg text-sm ${alignResult.success ? "bg-green-500/10 text-green-500" : "bg-red-500/10 text-red-500"}`}>
              {alignResult.message}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
