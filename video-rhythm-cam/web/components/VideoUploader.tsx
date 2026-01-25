"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, Video as VideoIcon, FileVideo, X } from "lucide-react";
import { useRhythmCamStore } from "@/lib/store";
import { useRouter } from "next/navigation";

interface UploadedVideo {
  filename: string;
  path: string;
  duration: number;
  fps: number;
  size: number;
}

interface VideoUploaderProps {
  onVideoUploaded?: (video: UploadedVideo) => void;
}

export function VideoUploader({ onVideoUploaded }: VideoUploaderProps) {
  const [uploading, setUploading] = useState(false);
  const [uploadedVideos, setUploadedVideos] = useState<UploadedVideo[]>([]);
  const { setCurrentVideo, setError } = useRhythmCamStore();

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      // 创建 FormData
      const formData = new FormData();
      formData.append("file", file);

      // 上传视频到 Python API
      const response = await fetch("http://localhost:8000/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("上传失败");
      }

      const result = await response.json();

      if (result.success) {
        const videoInfo: UploadedVideo = {
          filename: result.filename,
          path: result.path,
          duration: result.duration,
          fps: result.fps,
          size: 0, // 需要从 API 返回
        };

        // 自动设置当前视频
        setCurrentVideo(videoInfo);

        // 调用回调函数
        if (onVideoUploaded) {
          onVideoUploaded(videoInfo);
        }

        // 可选：也添加到列表中
        setUploadedVideos((prev) => [...prev, videoInfo]);
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : "上传失败");
    } finally {
      setUploading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "video/*": [".mp4", ".mov", ".avi", ".mkv", ".webm"],
    },
    maxFiles: 1,
  });

  const handleSelectVideo = (video: UploadedVideo) => {
    setCurrentVideo(video);
  };

  const handleDeleteVideo = (filename: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setUploadedVideos((prev) => prev.filter((v) => v.filename !== filename));
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* 上传区域 */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-12 text-center cursor-pointer
          transition-colors duration-200
          ${isDragActive
            ? "border-primary bg-primary/10"
            : "border-border hover:border-primary/50"
          }
          ${uploading ? "opacity-50 cursor-not-allowed" : ""}
        `}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center gap-4">
          <div className="p-4 bg-primary/10 rounded-full">
            {uploading ? (
              <div className="animate-spin">
                <Upload className="w-12 h-12 text-primary" />
              </div>
            ) : (
              <Upload className="w-12 h-12 text-primary" />
            )}
          </div>
          <div>
            <h3 className="text-xl font-semibold mb-2">
              {uploading ? "上传中..." : "拖拽或点击上传视频"}
            </h3>
            <p className="text-muted-foreground">
              支持 MP4, MOV, AVI, MKV, WEBM 格式
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
