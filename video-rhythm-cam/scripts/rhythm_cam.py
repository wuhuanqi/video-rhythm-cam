#!/usr/bin/env python3
"""
视频节奏运镜脚本
为舞蹈视频自动添加跟随音乐节奏的缩放效果
"""

import os
import sys
import argparse
import tempfile
import numpy as np
from typing import List, Tuple


def check_dependencies():
    """检查必要的依赖"""
    try:
        import moviepy
        import librosa
        import librosa.display
        import soundfile as sf
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖库: {e}")
        print("\n请安装以下依赖:")
        print("  pip install moviepy librosa soundfile numpy")
        return False


def extract_audio(video_path: str, audio_path: str) -> bool:
    """从视频中提取音频"""
    from moviepy import VideoFileClip

    try:
        print("📤 正在提取音频...")
        video = VideoFileClip(video_path)
        audio = video.audio

        if audio is None:
            print("❌ 视频中没有音频轨道")
            return False

        audio.write_audiofile(audio_path)
        audio.close()
        video.close()

        print(f"✅ 音频已提取到: {audio_path}")
        return True
    except Exception as e:
        print(f"❌ 提取音频失败: {e}")
        return False


def detect_beats(audio_path: str, sensitivity: float = 0.5) -> Tuple[List[float], float]:
    """
    检测音频中的节拍点

    Args:
        audio_path: 音频文件路径
        sensitivity: 节拍检测灵敏度 (0.0-1.0), 越高检测到的节拍越多

    Returns:
        (节拍时间列表, 音频时长)
    """
    import librosa
    import soundfile as sf

    try:
        print("🎵 正在分析音乐节奏...")

        # 加载音频
        y, sr = librosa.load(audio_path)
        duration = len(y) / sr

        # 检测节拍
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)

        # 将帧转换为时间(秒)
        beat_times = librosa.frames_to_time(beats, sr=sr)

        # 根据灵敏度过滤节拍
        if sensitivity < 1.0:
            # 计算节拍强度
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            beat_strength = onset_env[librosa.time_to_frames(beat_times, sr=sr)]

            # 只保留强度高于阈值的节拍
            threshold = np.percentile(beat_strength, (1 - sensitivity) * 100)
            mask = beat_strength >= threshold
            beat_times = beat_times[mask]

        print(f"✅ 检测到 {len(beat_times)} 个节拍点 (BPM: {float(tempo):.1f})")
        return beat_times.tolist(), duration

    except Exception as e:
        print(f"❌ 节拍检测失败: {e}")
        return [], 0.0


def create_zoom_clip(video_path: str, beat_times: List[float],
                     zoom_min: float = 1.0, zoom_max: float = 1.3,
                     zoom_duration: float = 0.2) -> str:
    """
    创建带节奏缩放效果的视频

    Args:
        video_path: 原视频路径
        beat_times: 节拍时间点列表
        zoom_min: 最小缩放比例
        zoom_max: 最大缩放比例
        zoom_duration: 每次缩放的持续时间(秒)

    Returns:
        输出视频路径
    """
    from moviepy import VideoFileClip

    try:
        print("🎬 正在应用运镜效果...")

        video = VideoFileClip(video_path)
        w, h = video.size

        # 为每个节拍创建缩放关键帧
        # 使用简单的缩放策略: 在节拍处放大,然后缩小
        def zoom_effect(get_frame, t):
            # 找到最近的节拍
            if not beat_times:
                return get_frame(t)

            # 找到最近的节拍时间
            beat_deltas = [abs(t - beat) for beat in beat_times]
            nearest_beat_dist = min(beat_deltas)

            # 如果接近节拍,应用缩放
            if nearest_beat_dist < zoom_duration:
                # 计算缩放因子: 节拍处最大,然后衰减
                progress = nearest_beat_dist / zoom_duration
                zoom_factor = zoom_max - (zoom_max - zoom_min) * progress
            else:
                zoom_factor = zoom_min

            # 应用缩放
            frame = get_frame(t)
            # 计算缩放后的尺寸
            new_w, new_h = int(w / zoom_factor), int(h / zoom_factor)

            # 居中裁剪
            x1 = (w - new_w) // 2
            y1 = (h - new_h) // 2
            x2 = x1 + new_w
            y2 = y1 + new_h

            # 裁剪并缩放回原尺寸
            from cv2 import resize
            cropped = frame[y1:y2, x1:x2]
            if cropped.size == 0:
                return frame
            return resize(cropped, (w, h))

        # 应用效果
        result = video.fl(zoom_effect)

        print(f"✅ 运镜效果已应用")
        return result

    except Exception as e:
        print(f"❌ 应用效果失败: {e}")
        return None


def process_video(video_path: str, output_path: str,
                  sensitivity: float = 0.5,
                  zoom_min: float = 1.0,
                  zoom_max: float = 1.3,
                  zoom_duration: float = 0.2) -> bool:
    """
    处理视频的主函数

    Args:
        video_path: 输入视频路径
        output_path: 输出视频路径
        sensitivity: 节拍检测灵敏度 (0.0-1.0)
        zoom_min: 最小缩放比例
        zoom_max: 最大缩放比例
        zoom_duration: 缩放持续时间(秒)

    Returns:
        是否成功
    """
    from moviepy import VideoFileClip

    # 验证输入
    if not os.path.exists(video_path):
        print(f"❌ 视频文件不存在: {video_path}")
        return False

    # 创建临时目录
    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = os.path.join(tmpdir, "audio.wav")

        # 步骤1: 提取音频
        if not extract_audio(video_path, audio_path):
            return False

        # 步骤2: 检测节拍
        beat_times, duration = detect_beats(audio_path, sensitivity)
        if not beat_times:
            print("❌ 未检测到节拍")
            return False

        # 步骤3: 应用缩放效果
        try:
            print("🎬 正在渲染最终视频...")

            video = VideoFileClip(video_path)
            original_audio = video.audio
            w, h = video.size
            fps = video.fps

            # 使用 cv2 进行更高效的处理
            try:
                import cv2
            except ImportError:
                print("❌ 需要安装 cv2 (opencv-python)")
                print("  pip install opencv-python")
                return False

            # 创建临时无音频视频文件
            temp_video_no_audio = os.path.join(tmpdir, "temp_no_audio.mp4")

            # 使用 H.264 编码器获得更好的质量
            fourcc = cv2.VideoWriter_fourcc(*'avc1')
            out = cv2.VideoWriter(temp_video_no_audio, fourcc, fps, (w, h))

            # 逐帧处理
            total_frames = int(duration * fps)
            for i in range(total_frames):
                t = i / fps

                # 获取原始帧
                frame = video.get_frame(t)

                # 计算缩放因子
                if beat_times:
                    beat_deltas = [abs(t - beat) for beat in beat_times]
                    nearest_beat_dist = min(beat_deltas)

                    if nearest_beat_dist < zoom_duration:
                        progress = nearest_beat_dist / zoom_duration
                        zoom_factor = zoom_max - (zoom_max - zoom_min) * progress
                    else:
                        zoom_factor = zoom_min
                else:
                    zoom_factor = zoom_min

                # 应用缩放
                if zoom_factor > zoom_min:
                    new_w, new_h = int(w / zoom_factor), int(h / zoom_factor)
                    x1 = (w - new_w) // 2
                    y1 = (h - new_h) // 2
                    x2 = x1 + new_w
                    y2 = y1 + new_h

                    # OpenCV 使用 BGR 格式
                    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    cropped = frame_bgr[y1:y2, x1:x2]
                    # 使用 LANCZOS 插值获得更好的缩放质量
                    frame = cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LANCZOS4)
                else:
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                out.write(frame)

                # 显示进度
                if i % 30 == 0:
                    print(f"   进度: {i/total_frames*100:.1f}%")

            out.release()

            # 如果有音频，先保存到临时文件
            temp_audio_path = None
            if original_audio is not None:
                print("🔊 正在保存音频...")
                temp_audio_path = os.path.join(tmpdir, "temp_audio.wav")
                original_audio.write_audiofile(temp_audio_path)
                # 关闭原始音频和视频以释放资源
                original_audio.close()
                original_audio = None
            video.close()

            # 添加音频到视频
            print("🔊 正在合并音频和视频...")
            video_processed = VideoFileClip(temp_video_no_audio)

            if temp_audio_path is not None:
                from moviepy import AudioFileClip
                audio_final = AudioFileClip(temp_audio_path)
                final_video = video_processed.with_audio(audio_final)
            else:
                final_video = video_processed

            # 使用高比特率输出以保证质量
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                bitrate='8000k'  # 高比特率保证质量
            )

            video_processed.close()
            final_video.close()

            print(f"✅ 视频处理完成!")
            print(f"📁 输出文件: {output_path}")
            return True

        except Exception as e:
            print(f"❌ 处理失败: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    parser = argparse.ArgumentParser(
        description='为舞蹈视频添加跟随音乐节奏的缩放运镜效果'
    )
    parser.add_argument('video', help='输入视频文件路径')
    parser.add_argument('-o', '--output', help='输出视频路径 (默认: output_rhythm.mp4)')
    parser.add_argument('-s', '--sensitivity', type=float, default=0.5,
                       help='节拍检测灵敏度 (0.0-1.0, 默认: 0.5)')
    parser.add_argument('--zoom-min', type=float, default=1.0,
                       help='最小缩放比例 (默认: 1.0)')
    parser.add_argument('--zoom-max', type=float, default=1.3,
                       help='最大缩放比例 (默认: 1.3)')
    parser.add_argument('--zoom-duration', type=float, default=0.2,
                       help='缩放持续时间(秒) (默认: 0.2)')

    args = parser.parse_args()

    # 检查依赖
    if not check_dependencies():
        sys.exit(1)

    # 设置输出路径
    if args.output:
        output_path = args.output
    else:
        base, _ = os.path.splitext(args.video)
        output_path = f"{base}_rhythm.mp4"

    # 处理视频
    success = process_video(
        args.video,
        output_path,
        sensitivity=args.sensitivity,
        zoom_min=args.zoom_min,
        zoom_max=args.zoom_max,
        zoom_duration=args.zoom_duration
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
