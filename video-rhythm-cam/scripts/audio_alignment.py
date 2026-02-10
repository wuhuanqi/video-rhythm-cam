#!/usr/bin/env python3
"""
音频对齐模块
将两个音频通过时间偏移进行节奏对齐
用于替换舞蹈视频的音频为高质量音频
"""

import os
import tempfile
import numpy as np
import librosa
import soundfile as sf
from typing import Tuple
from scipy import signal


def extract_audio_from_video(video_path: str, output_audio: str) -> bool:
    """从视频中提取音频"""
    try:
        from moviepy import VideoFileClip

        print(f"📤 正在从视频提取音频: {video_path}")
        video = VideoFileClip(video_path)
        audio = video.audio

        if audio is None:
            print("❌ 视频中没有音频轨道")
            return False

        audio.write_audiofile(output_audio, logger=None)
        audio.close()
        video.close()

        print(f"✅ 音频已提取: {output_audio}")
        return True
    except Exception as e:
        print(f"❌ 提取音频失败: {e}")
        return False


def find_best_offset(audio1_path: str, audio2_path: str, max_offset: float = 5.0) -> float:
    """
    找到两个音频之间的最佳时间偏移量
    使用交叉相关算法

    Args:
        audio1_path: 参考音频路径（高质量音频）
        audio2_path: 原始音频路径（舞蹈视频的音频）
        max_offset: 最大偏移量（秒）

    Returns:
        最佳时间偏移量（秒），正数表示 audio1 需要向后移动
    """
    try:
        print("🔍 正在计算最佳时间偏移量...")

        # 加载音频
        y1, sr1 = librosa.load(audio1_path, sr=22050)  # 降采样以提高速度
        y2, sr2 = librosa.load(audio2_path, sr=22050)

        # 计算节拍强度（onset strength）
        hop_length = 512
        onset_env1 = librosa.onset.onset_strength(y=y1, sr=sr1, hop_length=hop_length)
        onset_env2 = librosa.onset.onset_strength(y=y2, sr=sr1, hop_length=hop_length)

        # 归一化
        onset_env1 = (onset_env1 - onset_env1.mean()) / (onset_env1.std() + 1e-8)
        onset_env2 = (onset_env2 - onset_env2.mean()) / (onset_env2.std() + 1e-8)

        # 限制搜索范围
        max_frames = int(max_offset * sr1 / hop_length)
        search_range = min(len(onset_env2), max_frames * 2)

        # 使用交叉相关找到最佳偏移
        correlation = signal.correlate(onset_env1, onset_env2[:search_range], mode='valid')

        # 找到最大相关性的位置
        max_corr_idx = np.argmax(correlation)

        # 转换为时间（秒）
        offset_frames = max_corr_idx - len(onset_env2[:search_range]) + 1
        offset_seconds = offset_frames * hop_length / sr1

        print(f"✅ 最佳时间偏移量: {offset_seconds:.3f} 秒")

        return offset_seconds

    except Exception as e:
        print(f"❌ 计算偏移量失败: {e}")
        import traceback
        traceback.print_exc()
        return 0.0


def apply_offset_to_audio(audio_path: str, offset: float, output_path: str) -> bool:
    """
    对音频应用时间偏移

    Args:
        audio_path: 输入音频路径
        offset: 时间偏移量（秒），正数表示向后移动（前面加静音）
        output_path: 输出音频路径

    Returns:
        是否成功
    """
    try:
        print(f"🔧 正在应用时间偏移: {offset:.3f} 秒")

        # 加载音频
        y, sr = librosa.load(audio_path)
        audio_duration = len(y) / sr

        # 计算偏移的样本数
        offset_samples = int(offset * sr)

        # 确保不会裁剪掉太多音频（保留至少 80% 的原始音频）
        max_negative_offset = -int(len(y) * 0.8)
        if offset_samples < max_negative_offset:
            print(f"⚠️  警告: 偏移量过大，调整为 {max_negative_offset / sr:.3f} 秒")
            offset_samples = max_negative_offset

        if offset_samples > 0:
            # 向后移动：在前面添加静音
            silence = np.zeros(offset_samples)
            y_offset = np.concatenate([silence, y])
        elif offset_samples < 0:
            # 向前移动：删除前面的部分
            y_offset = y[-offset_samples:]
        else:
            # 没有偏移
            y_offset = y

        # 保存音频
        sf.write(output_path, y_offset, sr)

        print(f"✅ 偏移后的音频已保存: {output_path}")
        return True

    except Exception as e:
        print(f"❌ 应用偏移失败: {e}")
        return False


def align_and_replace_audio(
    dance_video_path: str,
    reference_video_path: str,
    output_video_path: str,
    max_offset: float = 5.0
) -> Tuple[bool, float]:
    """
    对齐两个视频的音频并替换到舞蹈视频中

    Args:
        dance_video_path: 原始舞蹈视频路径
        reference_video_path: 参考视频路径（包含高质量音频）
        output_video_path: 输出视频路径
        max_offset: 最大偏移量（秒）

    Returns:
        (是否成功, 实际偏移量)
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # 提取音频
        reference_audio = os.path.join(tmpdir, "reference_audio.wav")
        dance_audio = os.path.join(tmpdir, "dance_audio.wav")

        print("\n" + "="*60)
        print("🎵 第一步：提取音频")
        print("="*60)

        if not extract_audio_from_video(reference_video_path, reference_audio):
            return False, 0.0

        if not extract_audio_from_video(dance_video_path, dance_audio):
            return False, 0.0

        print("\n" + "="*60)
        print("🎯 第二步：计算时间偏移")
        print("="*60)

        # 计算最佳偏移（参考音频需要移动多少才能对齐舞蹈音频）
        offset = find_best_offset(reference_audio, dance_audio, max_offset)

        print("\n" + "="*60)
        print("🔧 第三步：应用偏移并合成视频")
        print("="*60)

        # 应用偏移到参考音频
        aligned_audio = os.path.join(tmpdir, "aligned_audio.wav")
        if not apply_offset_to_audio(reference_audio, offset, aligned_audio):
            return False, 0.0

        # 使用 moviepy 替换音频
        try:
            from moviepy import VideoFileClip, AudioFileClip

            print(f"🎬 正在合成视频...")

            # 加载视频和音频
            dance_video = VideoFileClip(dance_video_path)
            new_audio = AudioFileClip(aligned_audio)

            # 调整音频长度以匹配视频
            if new_audio.duration > dance_video.duration:
                # 音频比视频长，裁剪音频
                new_audio = new_audio.subclipped(0, dance_video.duration)

            # 裁剪视频长度以匹配音频（如果音频更短）
            if dance_video.duration > new_audio.duration:
                dance_video = dance_video.subclipped(0, new_audio.duration)

            # 设置音频
            final_video = dance_video.with_audio(new_audio)

            # 写入输出文件
            final_video.write_videofile(
                output_video_path,
                codec='libx264',
                audio_codec='aac',
                logger=None
            )

            # 清理
            dance_video.close()
            new_audio.close()
            final_video.close()

            print(f"\n✅ 视频合成完成: {output_video_path}")
            print(f"📊 音频偏移量: {offset:.3f} 秒")

            return True, offset

        except Exception as e:
            print(f"❌ 合成视频失败: {e}")
            import traceback
            traceback.print_exc()
            return False, 0.0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='对齐两个视频的音频并合成'
    )
    parser.add_argument('dance_video', help='原始舞蹈视频文件路径')
    parser.add_argument('reference_video', help='参考视频文件路径（高质量音频）')
    parser.add_argument('-o', '--output', help='输出视频路径')
    parser.add_argument('--max-offset', type=float, default=5.0,
                       help='最大偏移量（秒）(默认: 5.0)')

    args = parser.parse_args()

    # 设置输出路径
    if args.output:
        output_path = args.output
    else:
        base, _ = os.path.splitext(args.dance_video)
        output_path = f"{base}_aligned.mp4"

    # 对齐并合成
    success, offset = align_and_replace_audio(
        args.dance_video,
        args.reference_video,
        output_path,
        args.max_offset
    )

    if success:
        print(f"\n🎉 成功！偏移量: {offset:.3f} 秒")
    else:
        print("\n❌ 失败")

    exit(0 if success else 1)
