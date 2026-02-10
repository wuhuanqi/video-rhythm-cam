#!/usr/bin/env python3
"""
手动对齐工具
让用户手动指定偏移量，然后验证是否正确
"""

import os
import tempfile
import numpy as np
import librosa
import soundfile as sf
from moviepy import VideoFileClip, AudioFileClip
import subprocess


def extract_segment(audio_path, start_sec, duration, output_path):
    """提取音频片段"""
    y, _ = librosa.load(audio_path, sr=22050, offset=start_sec, duration=duration)
    sf.write(output_path, y, 22050)


def compare_segments(audio1_path, audio2_path):
    """对比两个音频片段"""
    y1, _ = librosa.load(audio1_path, sr=22050)
    y2, _ = librosa.load(audio2_path, sr=22050)

    # 确保长度一致
    min_len = min(len(y1), len(y2))
    y1 = y1[:min_len]
    y2 = y2[:min_len]

    # Chroma相似度
    chroma1 = librosa.feature.chroma_cqt(y=y1, sr=22050, hop_length=512)
    chroma2 = librosa.feature.chroma_cqt(y=y2, sr=22050, hop_length=512)

    similarity = np.mean([
        np.corrcoef(chroma1[i], chroma2[i])[0,1]
        for i in range(12)
        if not np.isnan(np.corrcoef(chroma1[i], chroma2[i])[0,1])
    ])

    return similarity


def main():
    orig_video = "/Users/a123/Downloads/原视频.MP4"
    ref_video = "/Users/a123/Downloads/对齐音频.MP4"

    print("="*70)
    print("🎵 手动对齐工具")
    print("="*70)

    # 获取原视频时长
    v1 = VideoFileClip(orig_video)
    orig_duration = v1.duration
    v1.close()

    print(f"\n📹 原视频时长: {orig_duration:.2f}秒")
    print(f"📹 参考视频时长: 53.80秒")

    print(f"\n💡 说明:")
    print(f"   我会从参考视频提取不同位置的音频")
    print(f"   与原视频对比，让你听哪个位置匹配")

    with tempfile.TemporaryDirectory() as tmpdir:
        # 提取原视频音频
        orig_audio = os.path.join(tmpdir, "orig.wav")
        v1 = VideoFileClip(orig_video)
        v1.audio.write_audiofile(orig_audio, logger=None)
        v1.close()

        # 测试几个关键位置
        test_positions = [0, 5, 10, 11, 11.5, 11.7, 12, 15, 20, 25, 30]
        sr = 22050  # 固定采样率

        print(f"\n🔍 测试参考视频的不同位置...")
        print("-"*70)

        best_pos = 0
        best_score = -1

        for pos in test_positions:
            if pos + orig_duration > 53.8:
                continue

            # 提取参考视频片段
            ref_segment = os.path.join(tmpdir, f"ref_{pos}.wav")
            extract_segment(ref_video, pos, orig_duration, ref_segment)

            # 对比
            score = compare_segments(orig_audio, ref_segment)

            status = "🏆" if score > best_score else "  "
            print(f"{status} 参考视频 {pos:5.1f}秒开始: 相似度 {score:6.1%}")

            if score > best_score:
                best_score = score
                best_pos = pos

        print("-"*70)
        print(f"\n✅ 算法找到的最佳位置: 参考视频 {best_pos:.1f}秒")
        print(f"   相似度: {best_score:.1%}")

        if best_score < 0.5:
            print(f"\n⚠️  警告: 相似度低于50%，可能不对")

        # 生成对比文件让用户听
        print(f"\n🎧 生成对比音频...")

        # 使用最佳位置
        ref_best = os.path.join(tmpdir, "ref_best.wav")
        extract_segment(ref_video, best_pos, orig_duration, ref_best)

        # 混合音频
        mixed_path = "/tmp/mixed_audio.wav"

        y_orig, _ = librosa.load(orig_audio, sr=22050)
        y_ref, _ = librosa.load(ref_best, sr=22050)

        min_len = min(len(y_orig), len(y_ref))
        y_orig = y_orig[:min_len]
        y_ref = y_ref[:min_len]

        # 混合（左右声道）
        y_mixed = np.column_stack([y_orig, y_ref])
        sf.write(mixed_path, y_mixed, 22050)

        min_len = min(len(y_orig), len(y_ref))
        y_orig = y_orig[:min_len]
        y_ref = y_ref[:min_len]

        # 混合（左右声道）
        y_mixed = np.column_stack([y_orig, y_ref])
        sf.write(mixed_path, y_mixed, sr)

        print(f"✅ 已生成对比音频: {mixed_path}")
        print(f"   左声道: 原视频音频")
        print(f"   右声道: 参考视频音频（从{best_pos:.1f}秒开始）")

        # 播放
        print(f"\n🔊 播放对比音频...")
        subprocess.run(["afplay", mixed_path])

        # 询问用户
        print(f"\n❓ 听起来对吗？")
        print(f"   如果不对，请告诉我参考视频应该从哪个位置开始")

        response = input("   输入位置（秒），或按回车使用算法找到的位置: ").strip()

        if response:
            try:
                final_pos = float(response)
            except:
                final_pos = best_pos
        else:
            final_pos = best_pos

        # 生成最终视频
        print(f"\n🎬 生成最终视频...")
        print(f"   从参考视频的 {final_pos:.1f}秒 处开始")

        output_video = "/Users/a123/Downloads/原视频_手动对齐.MP4"

        # 提取参考音频
        final_ref_audio = os.path.join(tmpdir, "final_ref.wav")
        extract_segment(ref_video, final_pos, orig_duration, final_ref_audio)

        # 合成视频
        video = VideoFileClip(orig_video)
        audio = AudioFileClip(final_ref_audio)

        if audio.duration < video.duration:
            video = video.subclipped(0, audio.duration)
        elif audio.duration > video.duration:
            audio = audio.subclipped(0, video.duration)

        final = video.with_audio(audio)
        final.write_videofile(output_video, codec='libx264', audio_codec='aac', logger=None)

        video.close()
        audio.close()
        final.close()

        print(f"\n✅ 完成!")
        print(f"   输出: {output_video}")


if __name__ == "__main__":
    main()
