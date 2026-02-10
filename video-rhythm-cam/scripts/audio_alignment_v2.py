#!/usr/bin/env python3
"""
音频对齐模块 V2 - 简化版本
思路:
1. 从原视频提取音频 (音频A)
2. 从参考视频提取音频 (音频B)
3. 用算法找到两个音频的最佳对齐偏移量
4. 应用偏移量到音频B
5. 裁剪两个音频到交叉的部分（取时长的交集）
6. 将对齐后的音频B替换回原视频
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

        print(f"📤 正在从视频提取音频: {os.path.basename(video_path)}")
        video = VideoFileClip(video_path)
        audio = video.audio

        if audio is None:
            print("❌ 视频中没有音频轨道")
            video.close()
            return False

        audio.write_audiofile(output_audio, logger=None)
        audio.close()
        video.close()

        print(f"✅ 音频已提取: {os.path.basename(output_audio)}")
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

        print(f"   音频1时长: {len(y1)/sr1:.2f}秒")
        print(f"   音频2时长: {len(y2)/sr2:.2f}秒")

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

        print(f"   搜索范围: ±{max_offset}秒")

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


def align_and_trim_audio(
    reference_audio_path: str,
    original_audio_path: str,
    output_audio_path: str,
    offset: float
) -> bool:
    """
    对齐并裁剪音频到交叉部分

    Args:
        reference_audio_path: 参考音频路径（需要对齐）
        original_audio_path: 原始音频路径
        output_audio_path: 输出音频路径
        offset: 时间偏移量（秒）

    Returns:
        是否成功
    """
    try:
        print(f"🔧 正在对齐并裁剪音频...")

        # 加载音频
        y_ref, sr = librosa.load(reference_audio_path)
        y_orig, sr_orig = librosa.load(original_audio_path)

        # 确保采样率一致
        if sr != sr_orig:
            print(f"⚠️  采样率不一致，重新加载原始音频")
            y_orig, sr = librosa.load(original_audio_path, sr=sr)

        ref_duration = len(y_ref) / sr
        orig_duration = len(y_orig) / sr

        print(f"   参考音频时长: {ref_duration:.2f}秒")
        print(f"   原始音频时长: {orig_duration:.2f}秒")
        print(f"   偏移量: {offset:.3f}秒")

        # 计算偏移后的样本数
        offset_samples = int(offset * sr)

        # 应用偏移
        if offset_samples > 0:
            # 正偏移：参考音频前面加静音
            silence = np.zeros(offset_samples)
            y_ref_aligned = np.concatenate([silence, y_ref])
            aligned_duration = len(y_ref_aligned) / sr
        elif offset_samples < 0:
            # 负偏移：参考音频前面截断
            y_ref_aligned = y_ref[-offset_samples:]
            aligned_duration = len(y_ref_aligned) / sr
        else:
            y_ref_aligned = y_ref
            aligned_duration = ref_duration

        print(f"   对齐后时长: {aligned_duration:.2f}秒")

        # 计算交叉部分（取两个音频的最小时长）
        final_duration = min(orig_duration, aligned_duration)
        final_samples = int(final_duration * sr)

        print(f"   最终时长: {final_duration:.2f}秒（交叉部分）")

        # 裁剪到相同长度
        y_ref_final = y_ref_aligned[:final_samples]
        y_orig_final = y_orig[:final_samples]

        # 保存对齐后的参考音频
        sf.write(output_audio_path, y_ref_final, sr)

        print(f"✅ 音频对齐完成: {os.path.basename(output_audio_path)}")
        return True

    except Exception as e:
        print(f"❌ 对齐音频失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def replace_audio_in_video(
    video_path: str,
    new_audio_path: str,
    output_video_path: str
) -> bool:
    """
    替换视频的音频

    Args:
        video_path: 原始视频路径
        new_audio_path: 新音频路径
        output_video_path: 输出视频路径

    Returns:
        是否成功
    """
    try:
        from moviepy import VideoFileClip, AudioFileClip

        print(f"🎬 正在合成视频...")

        # 加载视频和音频
        video = VideoFileClip(video_path)
        new_audio = AudioFileClip(new_audio_path)

        print(f"   视频时长: {video.duration:.2f}秒")
        print(f"   音频时长: {new_audio.duration:.2f}秒")

        # 音频和视频应该时长一致（在上一步已经对齐）
        # 但为了保险，如果音频比视频短，就裁剪视频
        if new_audio.duration < video.duration:
            print(f"   裁剪视频到音频长度")
            video = video.subclipped(0, new_audio.duration)
        elif new_audio.duration > video.duration:
            print(f"   裁剪音频到视频长度")
            new_audio = new_audio.subclipped(0, video.duration)

        # 设置音频
        final_video = video.with_audio(new_audio)

        # 写入输出文件
        final_video.write_videofile(
            output_video_path,
            codec='libx264',
            audio_codec='aac',
            logger=None
        )

        # 清理
        video.close()
        new_audio.close()
        final_video.close()

        print(f"✅ 视频合成完成: {os.path.basename(output_video_path)}")
        return True

    except Exception as e:
        print(f"❌ 合成视频失败: {e}")
        import traceback
        traceback.print_exc()
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
        print("\n" + "="*60)
        print("🎵 音频对齐工具 V2")
        print("="*60)

        # 步骤1: 提取音频
        print("\n📤 步骤 1/4: 提取音频")
        print("-"*60)

        dance_audio = os.path.join(tmpdir, "dance_audio.wav")
        reference_audio = os.path.join(tmpdir, "reference_audio.wav")

        if not extract_audio_from_video(dance_video_path, dance_audio):
            return False, 0.0

        if not extract_audio_from_video(reference_video_path, reference_audio):
            return False, 0.0

        # 步骤2: 计算时间偏移
        print("\n🎯 步骤 2/4: 计算时间偏移")
        print("-"*60)

        offset = find_best_offset(reference_audio, dance_audio, max_offset)

        # 步骤3: 对齐并裁剪音频
        print("\n🔧 步骤 3/4: 对齐并裁剪音频")
        print("-"*60)

        aligned_audio = os.path.join(tmpdir, "aligned_audio.wav")
        if not align_and_trim_audio(reference_audio, dance_audio, aligned_audio, offset):
            return False, 0.0

        # 步骤4: 替换视频音频
        print("\n🎬 步骤 4/4: 替换视频音频")
        print("-"*60)

        if not replace_audio_in_video(dance_video_path, aligned_audio, output_video_path):
            return False, 0.0

        print("\n" + "="*60)
        print("✅ 全部完成!")
        print(f"📁 输出文件: {output_video_path}")
        print(f"📊 音频偏移量: {offset:.3f} 秒")
        print("="*60 + "\n")

        return True, offset


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='对齐两个视频的音频并合成（V2版本）'
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
