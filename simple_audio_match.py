#!/usr/bin/env python3
"""
简单直接的音频匹配算法
使用频谱图2D交叉相关，就像"看"频谱一样匹配
"""

import os
import tempfile
import numpy as np
import librosa
import soundfile as sf
from moviepy import VideoFileClip


def extract_audio(video_path: str, output_path: str) -> bool:
    """提取音频"""
    try:
        print(f"📤 提取音频: {os.path.basename(video_path)}")
        video = VideoFileClip(video_path)
        if video.audio:
            video.audio.write_audiofile(output_path, logger=None)
            video.close()
            print(f"✅ 完成")
            return True
        video.close()
        return False
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False


def find_match_by_spectrogram(ref_audio: str, orig_audio: str, max_offset: int = 60):
    """
    使用频谱图进行2D匹配 - 就像人眼看频谱图一样
    """
    print("\n🎨 使用频谱图匹配...")
    print("   这就像直接对比两个音频的'图片'")

    # 加载音频
    sr = 22050
    y_ref, _ = librosa.load(ref_audio, sr=sr)
    y_orig, _ = librosa.load(orig_audio, sr=sr)

    print(f"   参考音频: {len(y_ref)/sr:.2f}秒")
    print(f"   原始音频: {len(y_orig)/sr:.2f}秒")

    # 计算短时傅里叶变换（STFT）得到频谱图
    print(f"   计算频谱图...")

    n_fft = 2048
    hop_length = 512

    # 获取频谱图（幅度谱）
    stft_ref = np.abs(librosa.stft(y_ref, n_fft=n_fft, hop_length=hop_length))
    stft_orig = np.abs(librosa.stft(y_orig, n_fft=n_fft, hop_length=hop_length))

    print(f"   参考频谱形状: {stft_ref.shape} (频率x时间)")
    print(f"   原始频谱形状: {stft_orig.shape}")

    # 对数缩放（人耳对响度的感知）
    stft_ref_db = librosa.amplitude_to_db(stft_ref, ref=np.max)
    stft_orig_db = librosa.amplitude_to_db(stft_orig, ref=np.max)

    # 使用原始音频的前N秒
    compare_frames = stft_orig.shape[1]  # 使用全部
    template = stft_orig_db[:, :compare_frames]

    print(f"\n🔍 在参考音频中搜索...")
    print(f"   模板: {template.shape[1]}帧 ({template.shape[1]*hop_length/sr:.2f}秒)")

    # 滑动窗口搜索
    max_search_frames = int(max_offset * sr / hop_length)
    max_search_frames = min(max_search_frames, stft_ref_db.shape[1] - template.shape[1])

    best_offset = 0
    best_score = -float('inf')

    # 为了加速，计算每一帧的总能量作为快速索引
    energy_ref = np.sum(stft_ref_db, axis=0)
    energy_orig = np.sum(template, axis=0)

    print(f"   搜索 {max_search_frames} 个位置...")

    # 步长可以大一点加速
    step = max(1, max_search_frames // 100)

    for offset in range(0, max_search_frames, step):
        end = offset + template.shape[1]
        if end > stft_ref_db.shape[1]:
            break

        # 提取片段
        segment = stft_ref_db[:, offset:end]

        # 计算相似度（简单的余弦相似度）
        # 展平
        flat_seg = segment.flatten()
        flat_temp = template.flatten()

        # 余弦相似度
        dot_product = np.dot(flat_seg, flat_temp)
        norm_seg = np.linalg.norm(flat_seg)
        norm_temp = np.linalg.norm(flat_temp)

        if norm_seg > 0 and norm_temp > 0:
            similarity = dot_product / (norm_seg * norm_temp)
        else:
            similarity = -1

        if similarity > best_score:
            best_score = similarity
            best_offset = offset

    # 转换为秒
    best_offset_sec = best_offset * hop_length / sr

    print(f"\n✅ 找到最佳匹配:")
    print(f"   位置: {best_offset_sec:+.3f}秒")
    print(f"   相似度: {best_score:.4f} ({best_score*100:.1f}%)")

    # 在最佳位置附近精细搜索
    print(f"\n🔬 精细搜索...")

    search_start = max(0, best_offset - step)
    search_end = min(max_search_frames, best_offset + step + template.shape[1])

    for offset in range(search_start, search_end):
        end = offset + template.shape[1]
        if end > stft_ref_db.shape[1]:
            break

        segment = stft_ref_db[:, offset:end]

        # 计算相似度
        flat_seg = segment.flatten()
        flat_temp = template.flatten()

        dot_product = np.dot(flat_seg, flat_temp)
        norm_seg = np.linalg.norm(flat_seg)
        norm_temp = np.linalg.norm(flat_temp)

        if norm_seg > 0 and norm_temp > 0:
            similarity = dot_product / (norm_seg * norm_temp)
        else:
            similarity = -1

        if similarity > best_score:
            best_score = similarity
            best_offset = offset

    best_offset_sec = best_offset * hop_length / sr

    print(f"   精细后位置: {best_offset_sec:+.3f}秒")
    print(f"   精细后相似度: {best_score:.4f} ({best_score*100:.1f}%)")

    return best_offset_sec, best_score


def align_videos(orig_video: str, ref_video: str, output: str, offset: float):
    """对齐视频"""
    print(f"\n🎬 合成视频...")

    # 提取参考音频片段
    sr = 22050
    y_ref, _ = librosa.load(ref_video, sr=sr)
    y_orig, _ = librosa.load(orig_video, sr=sr)

    # 从偏移位置开始
    start_sample = int(offset * sr)
    y_ref_aligned = y_ref[start_sample:]

    # 裁剪到相同长度
    min_len = min(len(y_orig), len(y_ref_aligned))
    y_ref_final = y_ref_aligned[:min_len]

    # 保存音频
    temp_audio = "/tmp/aligned_audio.wav"
    sf.write(temp_audio, y_ref_final, sr)

    # 合成视频
    video = VideoFileClip(orig_video)
    from moviepy.audio.io.AudioFileClip import AudioFileClip
    audio = AudioFileClip(temp_audio)

    if audio.duration < video.duration:
        video = video.subclipped(0, audio.duration)
    elif audio.duration > video.duration:
        audio = audio.subclipped(0, video.duration)

    final = video.with_audio(audio)
    final.write_videofile(output, codec='libx264', audio_codec='aac', logger=None)

    video.close()
    audio.close()
    final.close()

    print(f"✅ 完成: {output}")


def main():
    import sys

    if len(sys.argv) < 3:
        print("用法: python simple_audio_match.py <原视频> <参考视频> [输出]")
        sys.exit(1)

    orig_video = sys.argv[1]
    ref_video = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) > 3 else orig_video.replace(".MP4", "_aligned.MP4")

    print("="*70)
    print("🎵 简单音频匹配 - 频谱图对比")
    print("="*70)

    with tempfile.TemporaryDirectory() as tmpdir:
        # 提取音频
        orig_audio = os.path.join(tmpdir, "orig.wav")
        ref_audio = os.path.join(tmpdir, "ref.wav")

        if not extract_audio(orig_video, orig_audio):
            sys.exit(1)

        if not extract_audio(ref_video, ref_audio):
            sys.exit(1)

        # 找到匹配位置
        offset, score = find_match_by_spectrogram(ref_audio, orig_audio)

        print(f"\n📊 总结:")
        print(f"   偏移: {offset:+.3f}秒")
        print(f"   相似度: {score:.1%}")

        if score < 0.3:
            print(f"\n⚠️  相似度很低，可能不是同一首歌")
            response = input("   继续吗？(y/n): ")
            if response.lower() != 'y':
                sys.exit(1)

        # 合成视频
        align_videos(orig_video, ref_video, output, offset)

        print(f"\n🎉 完成!")
        print(f"   输出: {output}")


if __name__ == "__main__":
    main()
