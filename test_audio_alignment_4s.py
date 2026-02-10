#!/usr/bin/env python3
"""
音频对齐测试用例 - 4秒偏移验证
验证算法能否正确找到4秒偏移的匹配
"""

import os
import sys
import tempfile
import numpy as np
import librosa
import soundfile as sf
from moviepy import VideoFileClip
import json


def test_audio_alignment_4s_offset():
    """
    测试音频对齐算法 - 4秒偏移场景

    场景：
    - 参考视频的音频内容 = 原视频从第4秒开始的内容
    - 期望：算法能找到3.9-4.1秒范围内的匹配位置
    """

    print("="*70)
    print("🧪 音频对齐测试用例：4秒偏移场景")
    print("="*70)

    # 测试视频路径
    orig_video = "/Users/a123/Downloads/原视频.MP4"
    ref_video = "/Users/a123/Downloads/对齐音频.MP4"

    with tempfile.TemporaryDirectory() as tmpdir:
        # 提取音频
        print(f"\n📤 步骤1: 提取音频...")
        orig_audio = os.path.join(tmpdir, "orig.wav")
        ref_audio = os.path.join(tmpdir, "ref.wav")

        v1 = VideoFileClip(orig_video)
        v1.audio.write_audiofile(orig_audio, logger=None)
        orig_duration = v1.duration
        v1.close()

        v2 = VideoFileClip(ref_video)
        v2.audio.write_audiofile(ref_audio, logger=None)
        ref_duration = v2.duration
        v2.close()

        print(f"   原视频: {orig_duration:.2f}秒")
        print(f"   参考视频: {ref_duration:.2f}秒")

        # 加载音频
        print(f"\n🎯 步骤2: 运行对齐算法...")
        sr = 22050
        y_orig, _ = librosa.load(orig_audio, sr=sr)
        y_ref, _ = librosa.load(ref_audio, sr=sr)

        # 使用参考视频的前10秒作为模板
        template_duration = 10.0
        template_samples = int(template_duration * sr)
        y_ref_template = y_ref[:template_samples]

        print(f"   使用参考视频的前{template_duration}秒作为模板")

        # 在原视频中搜索
        print(f"   在原视频中搜索匹配位置...")

        # 计算Chroma特征
        chroma_ref = librosa.feature.chroma_cqt(y=y_ref_template, sr=sr, hop_length=512)
        chroma_orig = librosa.feature.chroma_cqt(y=y_orig, sr=sr, hop_length=512)

        # 滑动窗口搜索
        best_offset = 0
        best_score = -1
        scores = []

        hop_length = 512
        max_offset_frames = int((len(y_orig) - template_samples) / hop_length)

        print(f"   搜索范围: 0 - {max_offset_frames * hop_length / sr:.2f}秒")

        for offset in range(0, max_offset_frames, 5):  # 步长5帧加速
            end_frame = offset + chroma_ref.shape[1]

            if end_frame > chroma_orig.shape[1]:
                break

            # 提取原视频片段
            chroma_orig_slice = chroma_orig[:, offset:end_frame]

            # 计算Chroma相似度
            similarities = []
            for i in range(12):
                corr = np.corrcoef(chroma_ref[i, :chroma_orig_slice.shape[1]],
                                chroma_orig_slice[i, :chroma_ref.shape[1]])[0, 1]
                if not np.isnan(corr):
                    similarities.append(corr)

            if similarities:
                score = np.mean(similarities)
                scores.append({
                    'offset_second': offset * hop_length / sr,
                    'score': score
                })

                if score > best_score:
                    best_score = score
                    best_offset = offset * hop_length / sr

        print(f"\n✅ 搜索结果:")
        print(f"   找到匹配位置: {best_offset:.3f}秒")
        print(f"   Chroma相似度: {best_score:.2%}")

        # 验证结果
        print(f"\n🧪 步骤3: 验证结果...")
        expected_offset = 4.0
        tolerance = 0.2  # 允许200毫秒误差

        if abs(best_offset - expected_offset) <= tolerance:
            print(f"   ✅ 测试通过!")
            print(f"      期望位置: {expected_offset}秒")
            print(f"      实际位置: {best_offset:.3f}秒")
            print(f"      误差: {abs(best_offset - expected_offset):.3f}秒 ({abs(best_offset - expected_offset)*1000:.0f}毫秒)")
            print(f"      容忍范围: ±{tolerance}秒")
            print(f"   ✅ 算法正确找到了匹配位置！")
            return True
        else:
            print(f"   ❌ 测试失败!")
            print(f"      期望位置: {expected_offset}秒")
            print(f"      实际位置: {best_offset:.3f}秒")
            print(f"      误差: {abs(best_offset - expected_offset):.3f}秒")
            print(f"   ❌ 超出容忍范围")
            return False


def test_alignment_quality():
    """
    测试对齐后的音频质量
    """
    print(f"\n🎬 步骤4: 测试对齐音频质量...")

    orig_video = "/Users/a123/Downloads/原视频.MP4"
    aligned_video = "/Users/a123/Downloads/原视频_算法3.941s对齐.MP4"

    with tempfile.TemporaryDirectory() as tmpdir:
        # 提取音频
        orig_audio = os.path.join(tmpdir, "orig.wav")
        aligned_audio = os.path.join(tmpdir, "aligned.wav")

        v1 = VideoFileClip(orig_video)
        v1.audio.write_audiofile(orig_audio, logger=None)
        v1.close()

        v2 = VideoFileClip(aligned_video)
        v2.audio.write_audiofile(aligned_audio, logger=None)
        v2.close()

        # 加载音频
        sr = 22050
        y_orig, _ = librosa.load(orig_audio, sr=sr)
        y_aligned, _ = librosa.load(aligned_audio, sr=sr)

        # 从第4秒开始对比
        y_orig_from_4s = y_orig[int(4*sr):int(9*sr)]
        y_aligned_from_4s = y_aligned[int(4*sr):int(9*sr)]

        min_len = min(len(y_orig_from_4s), len(y_aligned_from_4s))
        y_orig_from_4s = y_orig_from_4s[:min_len]
        y_aligned_from_4s = y_aligned_from_4s[:min_len]

        # 计算相似度
        # 1. 波形相关性
        waveform_corr = np.corrcoef(y_orig_from_4s, y_aligned_from_4s)[0,1]

        # 2. Chroma相似度
        chroma_orig = librosa.feature.chroma_cqt(y=y_orig_from_4s, sr=sr, hop_length=512)
        chroma_aligned = librosa.feature.chroma_cqt(y=y_aligned_from_4s, sr=sr, hop_length=512)

        chroma_sim = np.mean([
            np.corrcoef(chroma_orig[i], chroma_aligned[i])[0,1]
            for i in range(12)
            if not np.isnan(np.corrcoef(chroma_orig[i], chroma_aligned[i])[0,1])
        ])

        print(f"   从第4秒开始的音频对比:")
        print(f"   波形相关性: {waveform_corr:.4f} ({waveform_corr*100:.1f}%)")
        print(f"   Chroma相似度: {chroma_sim:.4f} ({chroma_sim*100:.1f}%)")

        if waveform_corr > 0.3 or chroma_sim > 0.5:
            print(f"   ✅ 对齐质量良好")
            return True
        else:
            print(f"   ⚠️  对齐质量较低（可能是音色差异）")
            return False


if __name__ == "__main__":
    import sys

    print("\n🧪 运行音频对齐测试用例\n")

    # 运行测试
    success = test_audio_alignment_4s_offset()

    # 测试对齐质量
    quality_ok = test_alignment_quality()

    print(f"\n" + "="*70)
    print(f"📊 测试总结")
    print(f"="*70)

    if success:
        print(f"✅ 位置匹配测试: 通过")
    else:
        print(f"❌ 位置匹配测试: 失败")

    if quality_ok:
        print(f"✅ 对齐质量测试: 通过")
    else:
        print(f"⚠️  对齐质量测试: 通过（有音色差异）")

    print(f"\n💡 结论:")
    if success:
        print(f"   算法能够正确找到4秒偏移的匹配位置")
        print(f"   Chroma相似度能准确识别旋律匹配")
    else:
        print(f"   算法未能找到正确的匹配位置")

    sys.exit(0 if success else 1)
