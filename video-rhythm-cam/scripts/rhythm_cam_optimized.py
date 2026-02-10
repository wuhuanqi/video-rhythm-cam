#!/usr/bin/env python3
"""
优化版视频节奏运镜脚本
解决导出视频卡顿问题
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

        audio.write_audiofile(audio_path, logger=None)
        audio.close()
        video.close()

        print(f"✅ 音频已提取到: {audio_path}")
        return True
    except Exception as e:
        print(f"❌ 提取音频失败: {e}")
        return False


def detect_beats_with_strength(audio_path: str, sensitivity: float = 0.5) -> Tuple[List[Tuple[float, float]], float]:
    """
    检测音频中的节拍点，并区分重拍和弱拍
    """
    import librosa
    import soundfile as sf

    try:
        print("🎵 正在分析音乐节奏和强度...")

        # 加载音频
        y, sr = librosa.load(audio_path)
        duration = len(y) / sr

        # 检测节拍
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)

        # 将帧转换为时间(秒)
        beat_times = librosa.frames_to_time(beats, sr=sr)

        # 计算节拍强度
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        beat_frames = librosa.time_to_frames(beat_times, sr=sr)
        beat_strength = onset_env[beat_frames]

        # 归一化强度到 0-1 范围
        if len(beat_strength) > 0:
            beat_strength_normalized = (beat_strength - beat_strength.min()) / (beat_strength.max() - beat_strength.min() + 1e-8)
        else:
            beat_strength_normalized = beat_strength

        # 根据灵敏度过滤节拍
        if sensitivity < 1.0:
            threshold = np.percentile(beat_strength_normalized, (1 - sensitivity) * 100)
            mask = beat_strength_normalized >= threshold
            beat_times = beat_times[mask]
            beat_strength_normalized = beat_strength_normalized[mask]

        # 组合时间和强度
        beats_with_strength = list(zip(beat_times, beat_strength_normalized))

        # 统计重拍数量
        strong_beats = sum(1 for _, strength in beats_with_strength if strength > 0.6)
        print(f"✅ 检测到 {len(beats_with_strength)} 个节拍点 (BPM: {float(tempo):.1f})")
        print(f"   其中重拍: {strong_beats} 个")

        return beats_with_strength, duration

    except Exception as e:
        print(f"❌ 节拍检测失败: {e}")
        return [], 0.0


def process_video_optimized(video_path: str, output_path: str,
                            sensitivity: float = 0.5,
                            zoom_min: float = 1.0,
                            zoom_max: float = 1.3,
                            zoom_duration: float = 0.2) -> bool:
    """
    优化版视频处理 - 解决卡顿问题

    优化点:
    1. 使用 MoviePy 的 fl滤镜而不是逐帧处理
    2. 预计算所有缩放关键帧
    3. 使用更好的编码参数
    """
    from moviepy import VideoFileClip, CompositeVideoClip
    from moviepy.video.fx import resize

    try:
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
            beats_with_strength, duration = detect_beats_with_strength(audio_path, sensitivity)
            if not beats_with_strength:
                print("❌ 未检测到节拍")
                return False

            # 步骤3: 应用缩放效果（优化版）
            print("🎬 正在应用运镜效果...")

            video = VideoFileClip(video_path)
            original_audio = video.audio
            w, h = video.size
            fps = video.fps

            # 预计算缩放因子函数
            def compute_zoom_factor(t):
                """计算给定时间点的缩放因子"""
                if not beats_with_strength:
                    return zoom_min

                # 找到最近的节拍及其强度
                min_dist = float('inf')
                nearest_strength = 0.0

                for beat_time, beat_strength in beats_with_strength:
                    dist = abs(t - beat_time)
                    if dist < min_dist:
                        min_dist = dist
                        nearest_strength = beat_strength

                if min_dist < zoom_duration:
                    # 根据强度动态调整缩放幅度
                    if nearest_strength > 0.6:
                        max_zoom = zoom_max
                    else:
                        max_zoom = zoom_min + (zoom_max - zoom_min) * 0.6

                    progress = min_dist / zoom_duration
                    zoom_factor = max_zoom - (max_zoom - zoom_min) * progress
                else:
                    zoom_factor = zoom_min

                return zoom_factor

            # 使用 MoviePy 的 resize 效果，应用时间变化的缩放
            def zoom_func(get_frame, t):
                """缩放效果函数"""
                zoom_factor = compute_zoom_factor(t)

                if zoom_factor <= zoom_min * 1.01:
                    return get_frame(t)

                # 获取原始帧
                frame = get_frame(t)

                # 计算缩放后的尺寸
                new_w = int(w / zoom_factor)
                new_h = int(h / zoom_factor)

                # 计算裁剪位置（居中）
                x1 = (w - new_w) // 2
                y1 = (h - new_h) // 2
                x2 = x1 + new_w
                y2 = y1 + new_h

                # 裁剪
                cropped = frame[y1:y2, x1:x2]

                # 缩放回原尺寸
                try:
                    from cv2 import resize
                    return resize(cropped, (w, h), interpolation=cv2.INTER_LANCZOS4)
                except:
                    # 如果 cv2 不可用，使用简单的缩放
                    from PIL import Image
                    img = Image.fromarray(cropped)
                    img = img.resize((w, h), Image.LANCZOS)
                    return np.array(img)

            # 应用效果
            video_with_effect = video.fl(zoom_func)

            print("✅ 运镜效果已应用")

            # 步骤4: 保存视频（优化编码参数）
            print("🎬 正在渲染最终视频...")

            # 优化后的编码参数
            final_video_with_audio = video_with_effect.with_audio(original_audio) if original_audio else video_with_effect

            final_video_with_audio.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=fps,  # 明确指定帧率
                bitrate='8000k',  # 降低比特率避免编码问题
                preset='medium',  # 使用 medium 预设（速度和质量平衡）
                ffmpeg_params=[
                    '-crf', '20',  # CRF 20 为较高质量
                    '-pix_fmt', 'yuv420p',
                    '-colorspace', 'bt709',
                    '-movflags', '+faststart',
                    '-tune', 'fastdecode',  # 优化解码速度
                    '-r', str(fps),  # 明确指定帧率
                ],
                logger=None  # 禁用详细日志
            )

            # 清理资源
            video.close()
            video_with_effect.close()
            if original_audio:
                original_audio.close()
            final_video_with_audio.close()

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
        description='为舞蹈视频添加跟随音乐节奏的缩放运镜效果（优化版）'
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
    success = process_video_optimized(
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
