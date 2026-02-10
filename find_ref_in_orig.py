#!/usr/bin/env python3
"""
在原视频中找到参考视频音频的位置
然后用那个位置的高质量音频替换原视频
"""

import os
import tempfile
import numpy as np
import librosa
import soundfile as sf
from moviepy import VideoFileClip, AudioFileClip


def find_reference_in_original(ref_audio_path, orig_audio_path):
    """
    在原视频音频中找到参考视频音频的位置

    假设：参考视频的音频内容 = 原视频音频的一个片段
    """
    print("🔍 在原视频音频中搜索参考视频音频...")

    sr = 22050
    y_ref, _ = librosa.load(ref_audio_path, sr=sr)
    y_orig, _ = librosa.load(orig_audio_path, sr=sr)

    print(f"   参考音频: {len(y_ref)/sr:.2f}秒")
    print(f"   原始音频: {len(y_orig)/sr:.2f}秒")

    # 提取参考音频的特征
    # 使用更短的前奏来匹配（前10秒）
    ref_compare_duration = min(10.0, len(y_ref)/sr)
    ref_compare_samples = int(ref_compare_duration * sr)
    y_ref_template = y_ref[:ref_compare_samples]

    # 在原音频中搜索
    print(f"\n   在原音频中搜索...")
    print(f"   使用参考音频的前{ref_compare_duration:.2f}秒作为模板")

    # 计算互相关
    print(f"   计算互相关...")

    # 下采样加速
    ds_factor = 8
    y_ref_ds = y_ref_template[::ds_factor]
    y_orig_ds = y_orig[::ds_factor]

    # 归一化互相关
    y_ref_norm = (y_ref_ds - np.mean(y_ref_ds)) / np.std(y_ref_ds)
    y_orig_norm = (y_orig_ds - np.mean(y_orig_ds)) / np.std(y_orig_ds)

    # 计算互相关
    correlation = np.correlate(y_orig_norm, y_ref_norm, mode='valid')

    # 找到最大值的位置
    max_idx = np.argmax(correlation)
    max_corr = correlation[max_idx]

    # 转换为秒（考虑下采样）
    orig_start_sample = max_idx * ds_factor
    orig_start_second = orig_start_sample / sr

    print(f"\n✅ 找到最佳匹配:")
    print(f"   原音频位置: {orig_start_second:+.3f}秒")
    print(f"   互相关值: {max_corr:.4f}")

    # 验证匹配质量
    # 提取两个片段对比
    orig_end_sample = orig_start_sample + len(y_ref)
    if orig_end_sample > len(y_orig):
        print(f"   ⚠️  超出原音频长度，调整")
        orig_end_sample = len(y_orig)

    y_orig_match = y_orig[orig_start_sample:orig_end_sample]
    y_ref_match = y_ref[:len(y_orig_match)]

    # Chroma相似度验证
    chroma_orig = librosa.feature.chroma_cqt(y=y_orig_match, sr=sr, hop_length=512)
    chroma_ref = librosa.feature.chroma_cqt(y=y_ref_match, sr=sr, hop_length=512)

    chroma_sim = np.mean([
        np.corrcoef(chroma_orig[i], chroma_ref[i])[0,1]
        for i in range(12)
        if not np.isnan(np.corrcoef(chroma_orig[i], chroma_ref[i])[0,1])
    ])

    print(f"   Chroma相似度: {chroma_sim:.1%}")

    return orig_start_second, max_corr, chroma_sim


def main():
    orig_video = "/Users/a123/Downloads/原视频.MP4"
    ref_video = "/Users/a123/Downloads/对齐音频.MP4"
    output = "/Users/a123/Downloads/原视频_正确对齐.MP4"

    print("="*70)
    print("🎵 在原视频中找到参考音频，然后替换")
    print("="*70)

    with tempfile.TemporaryDirectory() as tmpdir:
        # 提取音频
        print(f"\n📤 提取音频...")

        orig_audio = os.path.join(tmpdir, "orig.wav")
        v1 = VideoFileClip(orig_video)
        v1.audio.write_audiofile(orig_audio, logger=None)
        orig_dur = v1.duration
        v1.close()

        ref_audio = os.path.join(tmpdir, "ref.wav")
        v2 = VideoFileClip(ref_video)
        v2.audio.write_audiofile(ref_audio, logger=None)
        ref_dur = v2.duration
        v2.close()

        print(f"   原视频: {orig_dur:.2f}秒")
        print(f"   参考视频: {ref_dur:.2f}秒")

        # 在原音频中找参考音频
        print(f"\n🔍 步骤1: 在原音频中找参考音频")
        print("-"*70)

        pos, corr, chroma = find_reference_in_original(ref_audio, orig_audio)

        if chroma < 0.3:
            print(f"\n⚠️  警告: 匹配度很低({chroma:.1%})")
            print(f"   可能理解有误，请确认")

        # 从原音频的该位置提取片段
        print(f"\n🔧 步骤2: 从原音频提取匹配片段")
        print("-"*70)

        sr = 22050
        y_orig, _ = librosa.load(orig_audio, sr=sr)

        start_sample = int(pos * sr)
        # 提取参考视频长度的片段
        end_sample = min(start_sample + int(ref_dur * sr), len(y_orig))

        print(f"   从原音频的 {pos:.3f}秒 开始")
        print(f"   提取到 {pos:.3f}秒 - {end_sample/sr:.3f}秒")

        y_extracted = y_orig[start_sample:end_sample]

        # 保存提取的音频
        extracted_audio = os.path.join(tmpdir, "extracted.wav")
        sf.write(extracted_audio, y_extracted, sr)

        print(f"   ✅ 提取完成")

        # 替换原视频音频
        print(f"\n🎬 步骤3: 替换原视频音频")
        print("-"*70)

        video = VideoFileClip(orig_video)
        audio = AudioFileClip(extracted_audio)

        # 调整长度
        if audio.duration < video.duration:
            video = video.subclipped(0, audio.duration)
        elif audio.duration > video.duration:
            audio = audio.subclipped(0, video.duration)

        final = video.with_audio(audio)
        final.write_videofile(output, codec='libx264', audio_codec='aac', logger=None)

        video.close()
        audio.close()
        final.close()

        print(f"\n✅ 完成!")
        print(f"   输出: {output}")
        print(f"   从原音频的 {pos:.3f}秒处提取")


if __name__ == "__main__":
    main()
