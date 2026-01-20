#!/usr/bin/env python3
"""
节奏检测模块
从视频中提取音频并检测节拍点,输出 JSON 格式的节拍数据
"""

import os
import sys
import json
import argparse
import tempfile
import librosa
import soundfile as sf
import numpy as np
from typing import List, Tuple, Dict, Any


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


def detect_beats_with_strength(audio_path: str, sensitivity: float = 0.5, fps: int = 30) -> Tuple[List[Tuple[float, float]], float, float]:
    """
    检测音频中的节拍点，并区分重拍和弱拍

    Args:
        audio_path: 音频文件路径
        sensitivity: 节拍检测灵敏度 (0.0-1.0), 越高检测到的节拍越多
        fps: 视频帧率，用于计算节拍帧号

    Returns:
        ((时间, 强度) 列表, 音频时长, BPM)
    """
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

        return beats_with_strength, duration, float(tempo)

    except Exception as e:
        print(f"❌ 节拍检测失败: {e}")
        return [], 0.0, 0.0


def beats_to_json(beats_with_strength: List[Tuple[float, float]], duration: float, bpm: float, fps: int = 30) -> Dict[str, Any]:
    """
    将节拍数据转换为 JSON 格式

    Args:
        beats_with_strength: (时间, 强度) 列表
        duration: 音频时长
        bpm: 节拍速度
        fps: 视频帧率

    Returns:
        JSON 格式的节拍数据
    """
    beats_list = [
        {
            "time": float(beat_time),
            "strength": float(strength),
            "frame": int(beat_time * fps)
        }
        for beat_time, strength in beats_with_strength
    ]

    return {
        "bpm": bpm,
        "duration": duration,
        "fps": fps,
        "beats": beats_list
    }


def detect_and_export(video_path: str, output_json: str, sensitivity: float = 0.5, fps: int = 30) -> bool:
    """
    从视频检测节拍并导出为 JSON 文件

    Args:
        video_path: 视频文件路径
        output_json: 输出 JSON 文件路径
        sensitivity: 节拍检测灵敏度
        fps: 视频帧率

    Returns:
        是否成功
    """
    # 验证输入
    if not os.path.exists(video_path):
        print(f"❌ 视频文件不存在: {video_path}")
        return False

    # 创建临时目录
    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = os.path.join(tmpdir, "audio.wav")

        # 提取音频
        if not extract_audio(video_path, audio_path):
            return False

        # 检测节拍
        beats_with_strength, duration, bpm = detect_beats_with_strength(audio_path, sensitivity, fps)
        if not beats_with_strength:
            print("❌ 未检测到节拍")
            return False

        # 转换为 JSON
        beats_data = beats_to_json(beats_with_strength, duration, bpm, fps)

        # 写入 JSON 文件
        try:
            os.makedirs(os.path.dirname(output_json) if os.path.dirname(output_json) else '.', exist_ok=True)
            with open(output_json, 'w', encoding='utf-8') as f:
                json.dump(beats_data, f, indent=2, ensure_ascii=False)
            print(f"✅ 节拍数据已保存到: {output_json}")
            return True
        except Exception as e:
            print(f"❌ 保存 JSON 失败: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description='从视频中检测节拍并导出为 JSON 格式'
    )
    parser.add_argument('video', help='输入视频文件路径')
    parser.add_argument('-o', '--output', help='输出 JSON 文件路径 (默认: beats.json)')
    parser.add_argument('-s', '--sensitivity', type=float, default=0.5,
                       help='节拍检测灵敏度 (0.0-1.0, 默认: 0.5)')
    parser.add_argument('--fps', type=int, default=30,
                       help='视频帧率 (默认: 30)')

    args = parser.parse_args()

    # 设置输出路径
    if args.output:
        output_path = args.output
    else:
        base, _ = os.path.splitext(args.video)
        output_path = f"{base}_beats.json"

    # 检测并导出
    success = detect_and_export(
        args.video,
        output_path,
        sensitivity=args.sensitivity,
        fps=args.fps
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
