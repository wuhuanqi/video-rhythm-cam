#!/usr/bin/env python3
"""
生成测试视频 - 包含简单的动画和节奏音乐
"""

import numpy as np
import cv2
from moviepy import VideoFileClip, AudioFileClip
import soundfile as sf
import tempfile
import os


def create_test_audio(audio_path, duration=10, bpm=120):
    """
    创建带有节奏的测试音频

    Args:
        audio_path: 输出音频路径
        duration: 音频时长(秒)
        bpm: 每分钟节拍数
    """
    import numpy as np

    print(f"🎵 正在生成测试音频 (BPM: {bpm})...")

    # 音频参数
    sample_rate = 44100
    total_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, total_samples)

    # 生成节拍
    beat_interval = 60 / bpm  # 每个节拍的间隔(秒)
    audio = np.zeros(total_samples)

    # 在每个节拍处添加一个短促的音调
    for beat_time in np.arange(0, duration, beat_interval):
        beat_sample = int(beat_time * sample_rate)
        # 生成一个0.1秒的音调
        tone_duration = int(0.1 * sample_rate)
        if beat_sample + tone_duration < total_samples:
            # 440Hz (A4) 音调
            tone = 0.3 * np.sin(2 * np.pi * 440 * np.linspace(0, 0.1, tone_duration))
            # 添加指数衰减
            envelope = np.exp(-np.linspace(0, 10, tone_duration))
            tone = tone * envelope
            audio[beat_sample:beat_sample+tone_duration] += tone

    # 添加背景节奏音
    for beat_time in np.arange(0, duration, beat_interval / 2):
        beat_sample = int(beat_time * sample_rate)
        kick_duration = int(0.05 * sample_rate)
        if beat_sample + kick_duration < total_samples:
            # 低频踢鼓声
            kick = 0.2 * np.sin(2 * np.pi * 80 * np.linspace(0, 0.05, kick_duration))
            envelope = np.exp(-np.linspace(0, 8, kick_duration))
            kick = kick * envelope
            audio[beat_sample:beat_sample+kick_duration] += kick

    # 归一化
    audio = audio / np.max(np.abs(audio))

    # 保存为 WAV 文件
    sf.write(audio_path, audio, sample_rate)
    print(f"✅ 音频已生成: {audio_path}")


def create_test_video(video_path, duration=10, fps=30):
    """
    创建带有动画的测试视频

    Args:
        video_path: 输出视频路径
        duration: 视频时长(秒)
        fps: 帧率
    """
    print(f"🎬 正在生成测试视频...")

    # 视频参数
    width, height = 1280, 720
    total_frames = int(duration * fps)

    # 创建视频写入器
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))

    # 生成动画帧
    for frame_idx in range(total_frames):
        # 创建渐变背景
        t = frame_idx / fps
        hue_shift = int(t * 30) % 360

        # 创建背景色 (从蓝色渐变到紫色)
        bg_color = (
            int(100 + 50 * np.sin(2 * np.pi * t / 5)),
            int(50 + 30 * np.cos(2 * np.pi * t / 3)),
            int(150 + 50 * np.sin(2 * np.pi * t / 4))
        )

        frame = np.full((height, width, 3), bg_color, dtype=np.uint8)

        # 添加移动的文字
        text = "DANCE TEST VIDEO"
        text_x = int(width/2 + 200 * np.sin(2 * np.pi * t / 3))
        text_y = int(height/2 + 100 * np.cos(2 * np.pi * t / 2))

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2
        font_thickness = 3
        text_color = (255, 255, 255)

        # 计算文字大小以居中
        text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
        text_x = int((width - text_size[0]) / 2)
        text_y = int((height + text_size[1]) / 2)

        cv2.putText(frame, text, (text_x, text_y), font,
                    font_scale, text_color, font_thickness)

        # 添加时间戳
        timestamp = f"Time: {t:.1f}s"
        cv2.putText(frame, timestamp, (50, 50),
                    font, 1, (255, 255, 0), 2)

        # 添加一些装饰性圆圈
        center = (width // 2, height // 2)
        for i in range(3):
            radius = int(100 + 50 * i + 30 * np.sin(2 * np.pi * t / (2 + i)))
            cv2.circle(frame, center, radius,
                      (255, 255 - i*80, 255 - i*80), 2)

        # 显示进度
        if frame_idx % 30 == 0:
            print(f"   进度: {frame_idx/total_frames*100:.1f}%")

        out.write(frame)

    out.release()
    print(f"✅ 视频已生成: {video_path}")


def combine_audio_video(video_path, audio_path, output_path):
    """合并音频和视频"""
    print("🔄 正在合并音频和视频...")

    try:
        # 加载视频和音频
        video = VideoFileClip(video_path)
        audio = AudioFileClip(audio_path)

        # 使用新的 API 设置音频
        video_with_audio = video.with_audio(audio)

        # 输出
        video_with_audio.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac'
        )

        # 关闭
        video.close()
        audio.close()
        video_with_audio.close()

        print(f"✅ 合并完成: {output_path}")

    except Exception as e:
        print(f"❌ 合并失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    import argparse

    parser = argparse.ArgumentParser(description='生成测试视频用于节奏运镜')
    parser.add_argument('-o', '--output', default='test_dance.mp4',
                       help='输出视频路径 (默认: test_dance.mp4)')
    parser.add_argument('-d', '--duration', type=float, default=10,
                       help='视频时长(秒) (默认: 10)')
    parser.add_argument('--bpm', type=int, default=120,
                       help='音乐节奏 (默认: 120)')

    args = parser.parse_args()

    # 检查依赖
    try:
        import moviepy
    except ImportError:
        print("❌ 缺少依赖库")
        print("请运行: pip install moviepy opencv-python soundfile numpy")
        return 1

    print(f"🎥 开始生成测试视频 ({args.duration}秒, {args.bpm} BPM)")

    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = os.path.join(tmpdir, "audio.wav")
        video_only_path = os.path.join(tmpdir, "video_only.mp4")

        # 创建音频
        create_test_audio(audio_path, args.duration, args.bpm)

        # 创建视频
        create_test_video(video_only_path, args.duration)

        # 合并
        combine_audio_video(video_only_path, audio_path, args.output)

    print(f"\n✅ 测试视频已生成: {args.output}")
    print(f"\n🚀 现在可以测试节奏运镜:")
    print(f"   python3 ~/.claude/skills/video-rhythm-cam/scripts/rhythm_cam.py {args.output}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
