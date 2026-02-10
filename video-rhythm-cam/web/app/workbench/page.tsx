"use client";

import { useState, useEffect } from "react";
import { useRhythmCamStore } from "@/lib/store";
import { 
  Upload, 
  CheckCircle2, 
  Loader2, 
  Sparkles,
  ArrowRight,
  Download,
  Volume2,
  Music2,
  Waves,
  Video,
  Zap
} from "lucide-react";

// 波形可视化组件
function WaveformVisualizer({ active = false, color = "pink" }: { active?: boolean; color?: "pink" | "cyan" }) {
  const colorClass = color === "pink" ? "bg-[var(--neon-pink)]" : "bg-[var(--neon-cyan)]";
  
  return (
    <div className="flex items-center justify-center gap-[3px] h-8">
      {[...Array(8)].map((_, i) => (
        <div
          key={i}
          className={`w-1 rounded-full ${colorClass} ${active ? 'waveform-bar' : 'opacity-30'}`}
          style={{ 
            height: active ? '100%' : '30%',
            animationDelay: `${i * 0.1}s`
          }}
        />
      ))}
    </div>
  );
}

// 背景装饰波形
function BackgroundWaves() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none opacity-20">
      <svg className="absolute bottom-0 left-0 w-full h-64" viewBox="0 0 1440 320" preserveAspectRatio="none">
        <defs>
          <linearGradient id="wave-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="var(--neon-pink)" />
            <stop offset="50%" stopColor="var(--neon-purple)" />
            <stop offset="100%" stopColor="var(--neon-cyan)" />
          </linearGradient>
        </defs>
        <path 
          fill="url(#wave-gradient)" 
          fillOpacity="0.3"
          d="M0,160L48,176C96,192,192,224,288,213.3C384,203,480,149,576,138.7C672,128,768,160,864,181.3C960,203,1056,213,1152,197.3C1248,181,1344,139,1392,117.3L1440,96L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"
        >
          <animate
            attributeName="d"
            dur="10s"
            repeatCount="indefinite"
            values="
              M0,160L48,176C96,192,192,224,288,213.3C384,203,480,149,576,138.7C672,128,768,160,864,181.3C960,203,1056,213,1152,197.3C1248,181,1344,139,1392,117.3L1440,96L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z;
              M0,128L48,144C96,160,192,192,288,197.3C384,203,480,181,576,165.3C672,149,768,139,864,154.7C960,171,1056,213,1152,218.7C1248,224,1344,192,1392,176L1440,160L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z;
              M0,160L48,176C96,192,192,224,288,213.3C384,203,480,149,576,138.7C672,128,768,160,864,181.3C960,203,1056,213,1152,197.3C1248,181,1344,139,1392,117.3L1440,96L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z
            "
          />
        </path>
      </svg>
    </div>
  );
}

export default function WorkbenchPage() {
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
  const [alignResult, setAlignResult] = useState<{ 
    success: boolean; 
    offset?: number; 
    message?: string;
    filename?: string;
  } | null>(null);
  const [dragOverDance, setDragOverDance] = useState(false);
  const [dragOverRef, setDragOverRef] = useState(false);

  // 上传处理函数
  const uploadVideo = async (file: File, type: "dance" | "ref") => {
    const setUploading = type === "dance" ? setIsUploadingDance : setIsUploadingRef;
    const setVideo = type === "dance" ? setCurrentVideo : setReferenceVideo;
    
    setUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("http://localhost:8000/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("上传失败");

      const result = await response.json();
      if (result.success) {
        setVideo({
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
    } finally {
      setUploading(false);
    }
  };

  // 对齐处理
  const handleAlignAudio = async () => {
    if (!currentVideo || !referenceVideo) return;

    setAligning(true);
    setError(null);
    setAlignResult(null);

    try {
      const response = await fetch("http://localhost:8000/api/align-audio", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          danceVideoPath: currentVideo.path,
          referenceVideoPath: referenceVideo.path,
          maxOffset: 5.0,
        }),
      });

      if (!response.ok) throw new Error("对齐失败");

      const result = await response.json();

      if (result.success && result.outputPath) {
        const filename = result.outputPath.split("/").pop();
        
        setAlignResult({
          success: true,
          offset: result.offset,
          message: `音频对齐成功`,
          filename,
        });
      } else {
        throw new Error(result.error || "对齐失败");
      }
    } catch (error) {
      setAlignResult({
        success: false,
        message: error instanceof Error ? error.message : "对齐失败",
      });
    } finally {
      setAligning(false);
    }
  };

  // 下载处理
  const handleDownload = () => {
    if (!alignResult?.filename) return;
    const downloadUrl = `http://localhost:8000/api/download/${alignResult.filename}`;
    const link = document.createElement("a");
    link.href = downloadUrl;
    link.download = alignResult.filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // 拖放处理
  const handleDrop = (e: React.DragEvent, type: "dance" | "ref") => {
    e.preventDefault();
    type === "dance" ? setDragOverDance(false) : setDragOverRef(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith("video/")) {
      uploadVideo(file, type);
    }
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const canAlign = currentVideo && referenceVideo && !isAligning;

  return (
    <main className="min-h-screen relative overflow-hidden">
      <BackgroundWaves />
      
      {/* Header */}
      <header className="relative z-10 px-8 py-6">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-[var(--neon-pink)] to-[var(--neon-purple)] flex items-center justify-center glow-pink">
                <Waves className="w-6 h-6 text-white" />
              </div>
              <div className="absolute -bottom-1 -right-1 w-4 h-4 rounded-full bg-[var(--neon-cyan)] animate-pulse" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight">
                <span className="gradient-text">PIPI</span>
                <span className="text-white/60 font-light ml-2">Audio Sync</span>
              </h1>
              <p className="text-sm text-white/40 font-mono">音频对齐工作台</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <div className="status-badge status-badge-success">
              <span className="w-1.5 h-1.5 rounded-full bg-[var(--neon-cyan)]" />
              <span className="font-mono">API Connected</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="relative z-10 px-8 pb-12">
        <div className="max-w-6xl mx-auto">
          
          {/* Hero Section */}
          <div className="text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              <span className="text-white">用</span>
              <span className="text-[var(--neon-cyan)] text-glow-cyan mx-2">高质量音频</span>
              <span className="text-white">替换你的</span>
              <span className="text-[var(--neon-pink)] text-glow-pink ml-2">舞蹈视频</span>
            </h2>
            <p className="text-white/50 text-lg max-w-2xl mx-auto">
              上传你的舞蹈视频和参考音源，AI 自动分析音频频谱，精准对齐每一个卡点
            </p>
          </div>

          {/* Upload Section */}
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            
            {/* Dance Video Upload */}
            <div
              className={`upload-zone upload-zone-dance ${currentVideo ? 'has-file' : ''} ${dragOverDance ? 'scale-[1.02]' : ''} cursor-pointer`}
              onDragOver={(e) => { e.preventDefault(); setDragOverDance(true); }}
              onDragLeave={() => setDragOverDance(false)}
              onDrop={(e) => handleDrop(e, "dance")}
              onClick={() => document.getElementById("dance-input")?.click()}
            >
              <input
                id="dance-input"
                type="file"
                accept="video/*"
                className="hidden"
                onChange={(e) => e.target.files?.[0] && uploadVideo(e.target.files[0], "dance")}
                disabled={isUploadingDance}
              />
              
              <div className="p-8">
                <div className="flex items-start justify-between mb-6">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-[var(--neon-pink)]/20 flex items-center justify-center">
                      <Video className="w-5 h-5 text-[var(--neon-pink)]" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-white">舞蹈视频</h3>
                      <p className="text-xs text-white/40">你录制的视频</p>
                    </div>
                  </div>
                  <span className="text-xs font-mono text-[var(--neon-pink)]/60 px-2 py-1 rounded bg-[var(--neon-pink)]/10">
                    STEP 1
                  </span>
                </div>

                {isUploadingDance ? (
                  <div className="flex flex-col items-center justify-center py-8">
                    <Loader2 className="w-10 h-10 text-[var(--neon-pink)] animate-spin mb-4" />
                    <p className="text-white/60">上传中...</p>
                  </div>
                ) : currentVideo ? (
                  <div className="space-y-4">
                    <div className="flex items-center gap-3 p-4 rounded-xl bg-black/30">
                      <div className="w-12 h-12 rounded-lg bg-[var(--neon-pink)]/20 flex items-center justify-center">
                        <CheckCircle2 className="w-6 h-6 text-[var(--neon-pink)]" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-white truncate">{currentVideo.filename}</p>
                        <p className="text-sm text-white/40 font-mono">
                          {formatDuration(currentVideo.duration)} · {currentVideo.fps}fps
                        </p>
                      </div>
                    </div>
                    <WaveformVisualizer active color="pink" />
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-8 text-center">
                    <div className="w-16 h-16 rounded-2xl bg-[var(--neon-pink)]/10 flex items-center justify-center mb-4 float">
                      <Upload className="w-8 h-8 text-[var(--neon-pink)]/60" />
                    </div>
                    <p className="text-white/60 mb-2">拖放视频到这里</p>
                    <p className="text-xs text-white/30">或点击选择文件</p>
                  </div>
                )}
              </div>
            </div>

            {/* Reference Video Upload */}
            <div
              className={`upload-zone upload-zone-ref ${referenceVideo ? 'has-file' : ''} ${dragOverRef ? 'scale-[1.02]' : ''} cursor-pointer`}
              onDragOver={(e) => { e.preventDefault(); setDragOverRef(true); }}
              onDragLeave={() => setDragOverRef(false)}
              onDrop={(e) => handleDrop(e, "ref")}
              onClick={() => document.getElementById("ref-input")?.click()}
            >
              <input
                id="ref-input"
                type="file"
                accept="video/*"
                className="hidden"
                onChange={(e) => e.target.files?.[0] && uploadVideo(e.target.files[0], "ref")}
                disabled={isUploadingRef}
              />
              
              <div className="p-8">
                <div className="flex items-start justify-between mb-6">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-[var(--neon-cyan)]/20 flex items-center justify-center">
                      <Music2 className="w-5 h-5 text-[var(--neon-cyan)]" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-white">参考视频</h3>
                      <p className="text-xs text-white/40">高质量音源</p>
                    </div>
                  </div>
                  <span className="text-xs font-mono text-[var(--neon-cyan)]/60 px-2 py-1 rounded bg-[var(--neon-cyan)]/10">
                    STEP 2
                  </span>
                </div>

                {isUploadingRef ? (
                  <div className="flex flex-col items-center justify-center py-8">
                    <Loader2 className="w-10 h-10 text-[var(--neon-cyan)] animate-spin mb-4" />
                    <p className="text-white/60">上传中...</p>
                  </div>
                ) : referenceVideo ? (
                  <div className="space-y-4">
                    <div className="flex items-center gap-3 p-4 rounded-xl bg-black/30">
                      <div className="w-12 h-12 rounded-lg bg-[var(--neon-cyan)]/20 flex items-center justify-center">
                        <CheckCircle2 className="w-6 h-6 text-[var(--neon-cyan)]" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-white truncate">{referenceVideo.filename}</p>
                        <p className="text-sm text-white/40 font-mono">
                          {formatDuration(referenceVideo.duration)} · {referenceVideo.fps}fps
                        </p>
                      </div>
                    </div>
                    <WaveformVisualizer active color="cyan" />
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center py-8 text-center">
                    <div className="w-16 h-16 rounded-2xl bg-[var(--neon-cyan)]/10 flex items-center justify-center mb-4 float">
                      <Upload className="w-8 h-8 text-[var(--neon-cyan)]/60" />
                    </div>
                    <p className="text-white/60 mb-2">拖放视频到这里</p>
                    <p className="text-xs text-white/30">MV 或高音质视频</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Action Section */}
          <div className="flex flex-col items-center gap-6">
            
            {/* Align Button */}
            <button
              onClick={handleAlignAudio}
              disabled={!canAlign}
              className="btn-action px-12 py-4 rounded-2xl text-white text-lg flex items-center gap-3"
            >
              {isAligning ? (
                <>
                  <Loader2 className="w-6 h-6 animate-spin" />
                  <span>分析音频频谱中...</span>
                </>
              ) : (
                <>
                  <Zap className="w-6 h-6" />
                  <span>开始对齐</span>
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>

            {!currentVideo && !referenceVideo && (
              <p className="text-white/30 text-sm">请先上传两个视频</p>
            )}
            {currentVideo && !referenceVideo && (
              <p className="text-white/30 text-sm">请上传参考视频</p>
            )}
            {!currentVideo && referenceVideo && (
              <p className="text-white/30 text-sm">请上传舞蹈视频</p>
            )}

            {/* Result */}
            {alignResult && (
              <div className={`glass-strong rounded-2xl p-6 w-full max-w-lg ${alignResult.success ? '' : 'border-red-500/30'}`}>
                {alignResult.success ? (
                  <div className="text-center space-y-4">
                    <div className="w-16 h-16 rounded-full bg-[var(--neon-cyan)]/20 flex items-center justify-center mx-auto glow-cyan">
                      <CheckCircle2 className="w-8 h-8 text-[var(--neon-cyan)]" />
                    </div>
                    <div>
                      <h3 className="text-xl font-semibold text-white mb-1">对齐完成！</h3>
                      <p className="text-white/50 text-sm">
                        时间偏移: <span className="font-mono text-[var(--neon-cyan)]">{alignResult.offset?.toFixed(3)}s</span>
                      </p>
                    </div>
                    <button
                      onClick={handleDownload}
                      className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-[var(--neon-cyan)] text-black font-semibold hover:bg-[var(--neon-cyan)]/90 transition-colors"
                    >
                      <Download className="w-5 h-5" />
                      <span>下载视频</span>
                    </button>
                  </div>
                ) : (
                  <div className="text-center">
                    <p className="text-red-400">{alignResult.message}</p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Info Cards */}
          <div className="grid md:grid-cols-3 gap-4 mt-16">
            {[
              { icon: Waves, title: "频谱分析", desc: "自动分析音频波形特征" },
              { icon: Zap, title: "智能对齐", desc: "精准匹配音乐卡点位置" },
              { icon: Volume2, title: "无损替换", desc: "保持视频画质不变" },
            ].map((item, i) => (
              <div key={i} className="glass rounded-2xl p-6 text-center">
                <div className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center mx-auto mb-4">
                  <item.icon className="w-6 h-6 text-white/60" />
                </div>
                <h4 className="font-semibold text-white mb-1">{item.title}</h4>
                <p className="text-sm text-white/40">{item.desc}</p>
              </div>
            ))}
          </div>

        </div>
      </div>
    </main>
  );
}
