#!/usr/bin/env python3
"""
提取对比音频片段
将原视频音频和对齐后视频音频的重叠部分提取出来，用于验证对齐是否正确
"""

import os
import tempfile
from moviepy import VideoFileClip
import librosa
import numpy as np
import soundfile as sf


def extract_audio_from_video(video_path: str, output_audio: str) -> bool:
    """从视频中提取音频"""
    try:
        print(f"📤 提取音频: {os.path.basename(video_path)}")
        video = VideoFileClip(video_path)
        audio = video.audio

        if audio is None:
            print(f"❌ 视频中没有音频: {video_path}")
            video.close()
            return False

        audio.write_audiofile(output_audio, logger=None)
        audio.close()
        video.close()
        print(f"✅ 音频已保存: {os.path.basename(output_audio)}")
        return True
    except Exception as e:
        print(f"❌ 提取音频失败: {e}")
        return False


def find_overlap_section(audio1_path: str, audio2_path: str, output_dir: str):
    """
    找到两个音频的重叠部分并提取

    Args:
        audio1_path: 原视频音频
        audio2_path: 对齐后的音频
        output_dir: 输出目录
    """
    try:
        print("\n🔍 分析音频重叠部分...")

        # 加载音频
        y1, sr1 = librosa.load(audio1_path, sr=None)
        y2, sr2 = librosa.load(audio2_path, sr=None)

        duration1 = len(y1) / sr1
        duration2 = len(y2) / sr2

        print(f"   音频1时长: {duration1:.2f}秒")
        print(f"   音频2时长: {duration2:.2f}秒")

        # 取较短的长度的重叠部分
        overlap_duration = min(duration1, duration2)
        overlap_samples = min(len(y1), len(y2))

        print(f"   重叠部分: {overlap_duration:.2f}秒")

        # 提取重叠部分（前10秒）
        compare_duration = min(10.0, overlap_duration)
        compare_samples = int(compare_duration * sr1)

        y1_overlap = y1[:compare_samples]
        y2_overlap = y2[:compare_samples]

        # 保存重叠片段
        output1 = os.path.join(output_dir, "original_audio_segment.wav")
        output2 = os.path.join(output_dir, "aligned_audio_segment.wav")
        output_mix = os.path.join(output_dir, "mixed_audio_segment.wav")

        sf.write(output1, y1_overlap, sr1)
        sf.write(output2, y2_overlap, sr2)

        # 混合音频（左右声道）
        if len(y1_overlap) == len(y2_overlap):
            # 原始音频在左声道，对齐音频在右声道
            y_mix = np.column_stack([y1_overlap, y2_overlap])
            sf.write(output_mix, y_mix, sr1)
            print(f"✅ 混合音频已保存（左声道=原音频，右声道=对齐音频）")

        print(f"\n✅ 音频片段已提取:")
        print(f"   📁 {output1}")
        print(f"   📁 {output2}")
        print(f"   📁 {output_mix}")

        # 计算相关性
        print(f"\n📊 计算音频相关性...")

        # 提取MFCC特征
        n_mfcc = 13
        hop_length = 512

        mfcc1 = librosa.feature.mfcc(y=y1_overlap, sr=sr1, n_mfcc=n_mfcc, hop_length=hop_length)
        mfcc2 = librosa.feature.mfcc(y=y2_overlap, sr=sr2, n_mfcc=n_mfcc, hop_length=hop_length)

        # 计算每个MFCC系数的相关性
        min_frames = min(mfcc1.shape[1], mfcc2.shape[1])
        correlations = []

        for i in range(n_mfcc):
            corr = np.corrcoef(mfcc1[i, :min_frames], mfcc2[i, :min_frames])[0, 1]
            if not np.isnan(corr):
                correlations.append(corr)
                print(f"   MFCC[{i:2d}] 相关系数: {corr:+.4f}")

        avg_correlation = np.mean(correlations)
        print(f"\n   📈 平均相关系数: {avg_correlation:+.4f}")

        if avg_correlation > 0.9:
            print(f"   ✅ 音频高度匹配（相关性 > 0.9）")
        elif avg_correlation > 0.7:
            print(f"   ⚠️  音频基本匹配（相关性 > 0.7）")
        else:
            print(f"   ❌ 音频匹配度较低（相关性 < 0.7）")

        return True

    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='提取原视频和对齐视频的音频重叠部分用于对比'
    )
    parser.add_argument('original_video', help='原始视频文件路径')
    parser.add_argument('aligned_video', help='对齐后的视频文件路径')
    parser.add_argument('-o', '--output-dir', help='输出目录', default='audio_comparison')

    args = parser.parse_args()

    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)

    print("="*60)
    print("🎵 音频对比工具")
    print("="*60)

    with tempfile.TemporaryDirectory() as tmpdir:
        # 提取音频
        original_audio = os.path.join(tmpdir, "original.wav")
        aligned_audio = os.path.join(tmpdir, "aligned.wav")

        if not extract_audio_from_video(args.original_video, original_audio):
            return 1

        if not extract_audio_from_video(args.aligned_video, aligned_audio):
            return 1

        # 找到重叠部分
        if not find_overlap_section(original_audio, aligned_audio, args.output_dir):
            return 1

    print("\n" + "="*60)
    print("✅ 完成！")
    print(f"📁 输出目录: {args.output_dir}")
    print("\n💡 播放建议:")
    print("   1. 先听 original_audio_segment.wav（原始音频）")
    print("   2. 再听 aligned_audio_segment.wav（对齐音频）")
    print("   3. 最后听 mixed_audio_segment.wav（混合对比）")
    print("      - 左声道 = 原始音频")
    print("      - 右声道 = 对齐音频")
    print("="*60)

    return 0


if __name__ == "__main__":
    exit(main())
