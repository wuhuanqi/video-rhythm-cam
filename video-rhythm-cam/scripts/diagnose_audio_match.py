#!/usr/bin/env python3
"""
音频匹配诊断工具
检查两个音频是否相似，以及找到正确的偏移量
"""

import os
import sys
import numpy as np
import librosa
import tempfile
import matplotlib
matplotlib.use('Agg')  # 无GUI模式
import matplotlib.pyplot as plt
from pathlib import Path

def extract_audio(video_path: str) -> str:
    """从视频中提取音频"""
    from moviepy import VideoFileClip

    tmp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    tmp_path = tmp_file.name
    tmp_file.close()

    video = VideoFileClip(video_path)
    audio = video.audio

    if audio is None:
        video.close()
        return None

    audio.write_audiofile(tmp_path, logger=None)
    audio.close()
    video.close()

    return tmp_path

def analyze_audio_similarity(audio1_path: str, audio2_path: str, max_offset: float = 30.0):
    """分析两个音频的相似度和最佳偏移量"""
    print("🔍 加载音频...")
    y1, sr1 = librosa.load(audio1_path, sr=22050)
    y2, sr2 = librosa.load(audio2_path, sr=22050)

    print(f"   音频1时长: {len(y1)/sr1:.2f}秒")
    print(f"   音频2时长: {len(y2)/sr2:.2f}秒")

    # 计算节拍强度
    hop_length = 512
    onset_env1 = librosa.onset.onset_strength(y=y1, sr=sr1, hop_length=hop_length)
    onset_env2 = librosa.onset.onset_strength(y=y2, sr=sr2, hop_length=hop_length)

    # 归一化
    onset_env1_norm = (onset_env1 - onset_env1.mean()) / (onset_env1.std() + 1e-8)
    onset_env2_norm = (onset_env2 - onset_env2.mean()) / (onset_env2.std() + 1e-8)

    # 计算全范围交叉相关
    max_samples = int(max_offset * sr1 / hop_length)

    # 计算不同偏移量的相关性
    print(f"\n🔍 测试多个偏移量...")

    offsets_to_test = list(range(-max_samples, max_samples + 1, 10))
    correlations = []

    for offset in offsets_to_test:
        try:
            if offset >= 0:
                # audio1 向后移动
                max_len = min(len(onset_env1_norm) - offset, len(onset_env2_norm))
                env1_slice = onset_env1_norm[offset:offset+max_len]
                env2_slice = onset_env2_norm[:max_len]
            else:
                # audio1 向前移动
                max_len = min(len(onset_env1_norm), len(onset_env2_norm) + offset)
                env1_slice = onset_env1_norm[:max_len]
                env2_slice = onset_env2_norm[-offset:-offset+max_len]

            if len(env1_slice) > 0 and len(env2_slice) > 0 and len(env1_slice) == len(env2_slice):
                corr = np.corrcoef(env1_slice, env2_slice)[0, 1]
                if not np.isnan(corr):
                    correlations.append((offset * hop_length / sr1, corr))
        except:
            pass

    # 找到最佳偏移
    correlations.sort(key=lambda x: x[1], reverse=True)

    print(f"\n📊 Top 10 最佳偏移量:")
    print("-" * 60)
    for i, (offset, corr) in enumerate(correlations[:10]):
        print(f"{i+1:2d}. 偏移: {offset:+7.3f}秒  相关系数: {corr:+.4f}")

    # 检测节拍点
    tempo1, beats1 = librosa.beat.beat_track(y=y1, sr=sr1)
    tempo2, beats2 = librosa.beat.beat_track(y=y2, sr=sr2)

    print(f"\n🎵 节拍分析:")
    print("-" * 60)
    print(f"音频1 - BPM: {float(tempo1):.1f}, 节拍数: {len(beats1)}")
    print(f"音频2 - BPM: {float(tempo2):.1f}, 节拍数: {len(beats2)}")

    if abs(tempo1 - tempo2) > 5:
        print(f"\n⚠️  警告: BPM差异较大 ({abs(tempo1-tempo2):.1f})，可能不是同一首歌！")

    # 检查前几个节拍的时间点
    print(f"\n🥁 前5个节拍时间点:")
    print("-" * 60)
    print(f"音频1: {[f'{t:.2f}s' for t in librosa.frames_to_time(beats1[:5], sr=sr1)]}")
    print(f"音频2: {[f'{t:.2f}s' for t in librosa.frames_to_time(beats2[:5], sr=sr2)]}")

    return correlations[0] if correlations else (0, 0)

def main():
    if len(sys.argv) != 3:
        print("用法: python diagnose_audio_match.py <视频1> <视频2>")
        sys.exit(1)

    video1_path = sys.argv[1]
    video2_path = sys.argv[2]

    print("="*60)
    print("🔍 音频匹配诊断工具")
    print("="*60)

    print(f"\n📹 视频1: {Path(video1_path).name}")
    print(f"📹 视频2: {Path(video2_path).name}")

    # 提取音频
    print(f"\n📤 提取音频...")
    audio1_path = extract_audio(video1_path)
    audio2_path = extract_audio(video2_path)

    if audio1_path is None or audio2_path is None:
        print("❌ 提取音频失败")
        sys.exit(1)

    try:
        # 分析相似度
        best_offset, correlation = analyze_audio_similarity(audio1_path, audio2_path, max_offset=30.0)

        print(f"\n{'='*60}")
        print(f"📋 诊断结果")
        print(f"{'='*60}")
        print(f"✅ 最佳偏移量: {best_offset:+.3f}秒")
        print(f"📊 相关系数: {correlation:+.4f}")

        if correlation < 0.3:
            print(f"\n⚠️  相关系数较低 ({correlation:.3f})")
            print(f"   可能原因:")
            print(f"   1. 两个视频的音乐不是同一首歌")
            print(f"   2. 音频质量差异过大")
            print(f"   3. 音乐版本不同（如Remix、Live版等）")

        print(f"\n💡 建议命令:")
        print(f"   python audio_alignment_v2.py \"{video1_path}\" \"{video2_path}\"")
        print(f"   -o output.mp4 --max-offset 30.0")

    finally:
        # 清理临时文件
        if os.path.exists(audio1_path):
            os.remove(audio1_path)
        if os.path.exists(audio2_path):
            os.remove(audio2_path)

if __name__ == "__main__":
    main()
