#!/usr/bin/env python3
"""
Video Rhythm Cam - Python API 服务
使用 FastAPI 提供节奏检测和视频处理能力
"""

import os
import sys
import tempfile
import uvicorn
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

# 添加 scripts 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from detect_beats import detect_beats_with_strength, beats_to_json
from audio_alignment_v8 import align_and_replace_audio
import subprocess
import json

# Pydantic 模型
class BeatDetectionRequest(BaseModel):
    videoPath: str
    sensitivity: float = 0.5

class Beat(BaseModel):
    time: float
    strength: float
    frame: int

class BeatsData(BaseModel):
    bpm: float
    duration: float
    fps: int
    beats: List[Beat]

class BeatDetectionResponse(BaseModel):
    success: bool
    data: Optional[BeatsData] = None
    error: Optional[str] = None

class ExportRequest(BaseModel):
    videoPath: str
    outputPath: str
    sensitivity: float = 0.5
    zoomMin: float = 1.0
    zoomMax: float = 1.3
    zoomDuration: float = 0.2
    quality: int = 90

class ExportResponse(BaseModel):
    success: bool
    outputPath: Optional[str] = None
    error: Optional[str] = None

class AudioAlignRequest(BaseModel):
    danceVideoPath: str
    referenceVideoPath: str
    maxOffset: float = 5.0

class AudioAlignResponse(BaseModel):
    success: bool
    outputPath: Optional[str] = None
    offset: Optional[float] = None
    error: Optional[str] = None

# 创建 FastAPI 应用
app = FastAPI(
    title="Video Rhythm Cam API",
    description="视频节奏运镜 API 服务",
    version="2.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 上传目录
BASE_DIR = Path(__file__).parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# 输出目录
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

def extract_audio_from_video(video_path: str, audio_path: str) -> bool:
    """从视频中提取音频"""
    try:
        from moviepy import VideoFileClip

        video = VideoFileClip(video_path)
        audio = video.audio

        if audio is None:
            return False

        audio.write_audiofile(audio_path, logger=None)
        audio.close()
        video.close()

        return True
    except Exception as e:
        print(f"提取音频失败: {e}")
        return False

def get_video_info(video_path: str) -> tuple[float, float]:
    """获取视频时长和帧率"""
    try:
        from moviepy import VideoFileClip

        video = VideoFileClip(video_path)
        duration = video.duration
        fps = video.fps if video.fps else 30.0
        video.close()

        return duration, fps
    except Exception as e:
        print(f"获取视频信息失败: {e}")
        return 0.0, 30.0

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Video Rhythm Cam API",
        "version": "2.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}

@app.post("/api/upload", response_model=dict)
async def upload_video(file: UploadFile = File(...)):
    """上传视频文件"""
    try:
        # 验证文件类型
        allowed_extensions = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
        file_ext = Path(file.filename).suffix.lower()

        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式: {file_ext}"
            )

        # 保存文件
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # 获取视频信息
        duration, fps = get_video_info(str(file_path))

        return {
            "success": True,
            "filename": file.filename,
            "path": str(file_path),
            "duration": duration,
            "fps": fps
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/detect-beats", response_model=BeatDetectionResponse)
async def detect_beats(request: BeatDetectionRequest):
    """检测视频中的音乐节拍"""
    try:
        # 验证视频文件存在
        if not os.path.exists(request.videoPath):
            return BeatDetectionResponse(
                success=False,
                error="视频文件不存在"
            )

        # 获取视频信息
        duration, fps = get_video_info(request.videoPath)
        if duration == 0:
            return BeatDetectionResponse(
                success=False,
                error="无法获取视频时长"
            )

        # 创建临时音频文件
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_audio:
            audio_path = tmp_audio.name

        try:
            # 提取音频
            if not extract_audio_from_video(request.videoPath, audio_path):
                return BeatDetectionResponse(
                    success=False,
                    error="视频中没有音频轨道"
                )

            # 检测节拍
            beats_with_strength, _, bpm = detect_beats_with_strength(
                audio_path,
                sensitivity=request.sensitivity,
                fps=int(fps)
            )

            if not beats_with_strength:
                return BeatDetectionResponse(
                    success=False,
                    error="未检测到节拍，请尝试调整灵敏度"
                )

            # 转换为 JSON 格式
            beats_data = beats_to_json(
                beats_with_strength,
                duration,
                bpm,
                int(fps)
            )

            return BeatDetectionResponse(
                success=True,
                data=beats_data
            )

        finally:
            # 清理临时文件
            if os.path.exists(audio_path):
                os.remove(audio_path)

    except Exception as e:
        return BeatDetectionResponse(
            success=False,
            error=f"处理失败: {str(e)}"
        )

@app.get("/api/videos")
async def list_videos():
    """列出已上传的视频"""
    try:
        video_extensions = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
        videos = []

        for file_path in UPLOAD_DIR.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in video_extensions:
                duration, fps = get_video_info(str(file_path))
                videos.append({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "duration": duration,
                    "fps": fps,
                    "size": file_path.stat().st_size
                })

        return {
            "success": True,
            "videos": videos
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/videos/{filename}")
async def get_video(filename: str):
    """获取视频文件（用于预览播放）"""
    try:
        video_path = UPLOAD_DIR / filename

        if not video_path.exists():
            return HTTPException(status_code=404, detail="视频文件不存在")

        # 支持范围请求（用于视频流式播放）
        def iterfile():
            with open(video_path, mode="rb") as file_like:
                yield from file_like

        # 获取文件大小和 MIME 类型
        file_size = video_path.stat().st_size
        content_type = "video/mp4"

        # 根据文件扩展名确定 MIME 类型
        mime_types = {
            ".mp4": "video/mp4",
            ".mov": "video/quicktime",
            ".avi": "video/x-msvideo",
            ".mkv": "video/x-matroska",
            ".webm": "video/webm"
        }

        ext = video_path.suffix.lower()
        if ext in mime_types:
            content_type = mime_types[ext]

        # 返回流式响应
        return StreamingResponse(
            iterfile(),
            media_type=content_type,
            headers={
                "Content-Length": str(file_size),
                "Accept-Ranges": "bytes",
                "Content-Disposition": f"inline; filename={filename}"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取视频失败: {str(e)}")

@app.post("/api/export", response_model=ExportResponse)
async def export_video(request: ExportRequest):
    """导出带节奏运镜效果的视频（带进度显示）"""
    try:
        # 验证视频文件存在
        if not os.path.exists(request.videoPath):
            return ExportResponse(
                success=False,
                error="视频文件不存在"
            )

        # 构建输出文件名（包含参数）
        import datetime
        input_filename = Path(request.videoPath).stem
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{input_filename}_rhythm_s{request.sensitivity}_z{request.zoomMin}-{request.zoomMax}_q{request.quality}_{timestamp}.mp4"
        output_path = OUTPUT_DIR / output_filename

        # 构建命令 - 使用 Remotion 版本（更流畅，无卡顿）
        script_path = BASE_DIR / "scripts" / "rhythm_remotion.py"
        remotion_dir = BASE_DIR / "remotion"

        cmd = [
            "python3",
            str(script_path),
            request.videoPath,
            "--remotion-dir", str(remotion_dir),
            "-s", str(request.sensitivity),
            "--zoom-min", str(request.zoomMin),
            "--zoom-max", str(request.zoomMax),
            "--zoom-duration", str(request.zoomDuration),
            "-q", str(request.quality),
            "-o", str(output_path)
        ]

        # 执行导出命令（实时输出）
        print(f"🎬 开始导出视频...")
        print(f"📁 输入: {request.videoPath}")
        print(f"📁 输出: {output_path}")

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # 实时读取输出并打印
        for line in process.stdout:
            line = line.strip()
            if line:
                print(line)  # 打印到服务器日志

        returncode = process.wait()

        if returncode != 0:
            print(f"❌ 导出失败 (返回码: {returncode})")
            return ExportResponse(
                success=False,
                error=f"导出失败，返回码: {returncode}"
            )

        print(f"✅ 导出成功: {output_path}")

        return ExportResponse(
            success=True,
            outputPath=str(output_path)
        )

    except Exception as e:
        print(f"❌ 导出异常: {e}")
        import traceback
        traceback.print_exc()
        return ExportResponse(
            success=False,
            error=f"导出异常: {str(e)}"
        )

@app.post("/api/align-audio", response_model=AudioAlignResponse)
async def align_audio(request: AudioAlignRequest):
    """对齐两个视频的音频并合成"""
    try:
        # 验证文件存在
        if not os.path.exists(request.danceVideoPath):
            return AudioAlignResponse(
                success=False,
                error="舞蹈视频文件不存在"
            )

        if not os.path.exists(request.referenceVideoPath):
            return AudioAlignResponse(
                success=False,
                error="参考视频文件不存在"
            )

        # 构建输出文件名
        input_filename = Path(request.danceVideoPath).stem
        output_filename = f"{input_filename}_aligned.mp4"
        output_path = OUTPUT_DIR / output_filename

        print(f"🎵 开始音频对齐...")
        print(f"💃 舞蹈视频: {request.danceVideoPath}")
        print(f"🎵 参考视频: {request.referenceVideoPath}")
        print(f"📁 输出: {output_path}")

        # 调用音频对齐函数
        success, offset = align_and_replace_audio(
            request.danceVideoPath,
            request.referenceVideoPath,
            str(output_path),
            request.maxOffset
        )

        if success:
            print(f"✅ 音频对齐成功: {output_path}")
            return AudioAlignResponse(
                success=True,
                outputPath=str(output_path),
                offset=offset
            )
        else:
            return AudioAlignResponse(
                success=False,
                error="音频对齐失败"
            )

    except Exception as e:
        print(f"❌ 音频对齐异常: {e}")
        import traceback
        traceback.print_exc()
        return AudioAlignResponse(
            success=False,
            error=f"音频对齐异常: {str(e)}"
        )

@app.get("/api/download/{filename}")
async def download_video(filename: str):
    """下载导出的视频文件"""
    try:
        video_path = OUTPUT_DIR / filename

        if not video_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")

        return FileResponse(
            path=str(video_path),
            filename=filename,
            media_type="video/mp4"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")

if __name__ == "__main__":
    print("🚀 启动 Video Rhythm Cam API 服务...")
    print(f"📁 上传目录: {UPLOAD_DIR}")
    print("📖 API 文档: http://localhost:8000/docs")

    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
