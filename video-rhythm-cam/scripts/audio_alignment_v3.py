#!/usr/bin/env python3
"""
音频对齐模块 V3 - 使用旋律和频率分析
通过MFCC和Chroma特征找到音频中最相似的部分
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


def find_best_match_with_melody(
    reference_audio_path: str,
    original_audio_path: str,
    max_offset: float = 30.0
) -> Tuple[float, float, float]:
    """
    使用MFCC和Chroma特征找到最佳匹配位置

    Args:
        reference_audio_path: 参考音频路径（高质量音频）
        original_audio_path: 原始音频路径（舞蹈视频的音频）
        max_offset: 最大偏移量（秒）

    Returns:
        (最佳偏移量, 相似度分数, 相似度分数)
    """
    try:
        print("🔍 正在使用MFCC和Chroma特征分析音频...")

        # 加载音频
        y_ref, sr = librosa.load(reference_audio_path, sr=22050)
        y_orig, sr_orig = librosa.load(original_audio_path, sr=22050)

        ref_duration = len(y_ref) / sr
        orig_duration = len(y_orig) / sr

        print(f"   参考音频时长: {ref_duration:.2f}秒")
        print(f"   原始音频时长: {orig_duration:.2f}秒")

        # 提取MFCC特征（Mel-frequency cepstral coefficients）
        # MFCC可以捕捉音色和旋律特征
        hop_length = 512
        n_mfcc = 20

        print(f"   正在提取MFCC特征...")
        mfcc_ref = librosa.feature.mfcc(y=y_ref, sr=sr, n_mfcc=n_mfcc, hop_length=hop_length)
        mfcc_orig = librosa.feature.mfcc(y=y_orig, sr=sr, n_mfcc=n_mfcc, hop_length=hop_length)

        # 提取Chroma特征（用于分析和声和调性）
        print(f"   正在提取Chroma特征...")
        chroma_ref = librosa.feature.chroma_stft(y=y_ref, sr=sr, hop_length=hop_length)
        chroma_orig = librosa.feature.chroma_stft(y=y_orig, sr=sr, hop_length=hop_length)

        # 提取频谱对比度（Spectral Contrast）
        print(f"   正在提取频谱对比度...")
        contrast_ref = librosa.feature.spectral_contrast(y=y_ref, sr=sr, hop_length=hop_length)
        contrast_orig = librosa.feature.spectral_contrast(y=y_orig, sr=sr, hop_length=hop_length)

        # 提取Tonnetz特征（音高空间）
        print(f"   正在提取Tonnetz特征...")
        tonnetz_ref = librosa.feature.tonnetz(y=y_ref, sr=sr, hop_length=hop_length)
        tonnetz_orig = librosa.feature.tonnetz(y=y_orig, sr=sr, hop_length=hop_length)

        print(f"   正在计算最佳匹配...")

        # 计算最大搜索范围
        max_offset_samples = int(max_offset * sr / hop_length)
        search_range = min(len(mfcc_orig[0]), max_offset_samples)

        best_offset = 0.0
        best_score = -float('inf')
        best_mfcc_score = -float('inf')
        best_chroma_score = -float('inf')

        # 滑动窗口搜索最佳匹配位置
        # 我们尝试将参考音频的不同位置与原始音频的开头对齐
        for offset in range(-search_range, search_range + 1, 5):  # 步长5以加速
            try:
                if offset >= 0:
                    # 参考音频向后移动
                    ref_start = offset
                    ref_end = min(len(mfcc_orig[0]) + offset, len(mfcc_ref[0]))
                    orig_start = 0
                    orig_end = min(len(mfcc_orig[0]), len(mfcc_ref[0]) - offset)
                else:
                    # 参考音频向前移动
                    ref_start = 0
                    ref_end = min(len(mfcc_orig[0]) + offset, len(mfcc_ref[0]))
                    orig_start = -offset
                    orig_end = min(len(mfcc_orig[0]) - offset, len(mfcc_orig[0]))

                # 确保两个片段长度一致
                if ref_end <= ref_start or orig_end <= orig_start:
                    continue

                length = min(ref_end - ref_start, orig_end - orig_start)
                if length < 100:  # 至少要100帧
                    continue

                ref_end = ref_start + length
                orig_end = orig_start + length

                # 提取对应片段
                mfcc_ref_slice = mfcc_ref[:, ref_start:ref_end]
                mfcc_orig_slice = mfcc_orig[:, orig_start:orig_end]

                chroma_ref_slice = chroma_ref[:, ref_start:ref_end]
                chroma_orig_slice = chroma_orig[:, orig_start:orig_end]

                contrast_ref_slice = contrast_ref[:, ref_start:ref_end]
                contrast_orig_slice = contrast_orig[:, orig_start:orig_end]

                tonnetz_ref_slice = tonnetz_ref[:, ref_start:ref_end]
                tonnetz_orig_slice = tonnetz_orig[:, orig_start:orig_end]

                # 计算MFCC相似度（使用动态时间规整DTW）
                mfcc_dist = librosa.sequence.dtw(mfcc_ref_slice, mfcc_orig_slice)[0][-1, -1]
                mfcc_sim = -mfcc_dist  # 转换为相似度

                # 计算Chroma相似度
                chroma_sim = np.mean([
                    np.corrcoef(chroma_ref_slice[i], chroma_orig_slice[i])[0, 1]
                    for i in range(12)
                    if not np.isnan(np.corrcoef(chroma_ref_slice[i], chroma_orig_slice[i])[0, 1])
                ])

                # 计算频谱对比度相似度
                contrast_sim = np.mean([
                    np.corrcoef(contrast_ref_slice[i], contrast_orig_slice[i])[0, 1]
                    for i in range(7)
                    if not np.isnan(np.corrcoef(contrast_ref_slice[i], contrast_orig_slice[i])[0, 1])
                ])

                # 计算Tonnetz相似度
                tonnetz_sim = np.mean([
                    np.corrcoef(tonnetz_ref_slice[i], tonnetz_orig_slice[i])[0, 1]
                    for i in range(6)
                    if not np.isnan(np.corrcoef(tonnetz_ref_slice[i], tonnetz_orig_slice[i])[0, 1])
                ])

                # 综合分数（加权平均）
                # MFCC权重最高，因为它最能反映旋律和音色
                if not np.isnan(chroma_sim) and not np.isnan(contrast_sim) and not np.isnan(tonnetz_sim):
                    combined_score = (
                        mfcc_sim * 0.5 +      # MFCC权重50%
                        chroma_sim * 0.25 +    # Chroma权重25%
                        contrast_sim * 0.15 +  # Spectral Contrast权重15%
                        tonnetz_sim * 0.10     # Tonnetz权重10%
                    )

                    if combined_score > best_score:
                        best_score = combined_score
                        best_offset = offset * hop_length / sr
                        best_mfcc_score = mfcc_sim
                        best_chroma_score = chroma_sim

            except Exception as e:
                continue

        print(f"\n✅ 最佳匹配位置:")
        print(f"   偏移量: {best_offset:+.3f}秒")
        print(f"   综合相似度: {best_score:.4f}")
        print(f"   MFCC相似度: {best_mfcc_score:.4f}")
        print(f"   Chroma相似度: {best_chroma_score:.4f}")

        return best_offset, best_mfcc_score, best_chroma_score

    except Exception as e:
        print(f"❌ 计算偏移量失败: {e}")
        import traceback
        traceback.print_exc()
        return 0.0, 0.0, 0.0


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
        print(f"   偏移量: {offset:+.3f}秒")

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
    max_offset: float = 30.0
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
        print("🎵 音频对齐工具 V3 - 旋律匹配版")
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

        # 步骤2: 使用MFCC和Chroma计算最佳偏移
        print("\n🎯 步骤 2/4: 分析旋律和频率")
        print("-"*60)

        offset, mfcc_score, chroma_score = find_best_match_with_melody(
            reference_audio,
            dance_audio,
            max_offset
        )

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
        print(f"📊 音频偏移量: {offset:+.3f} 秒")
        print(f"🎵 MFCC相似度: {mfcc_score:.4f}")
        print(f"🎼 Chroma相似度: {chroma_score:.4f}")
        print("="*60 + "\n")

        return True, offset


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='对齐两个视频的音频并合成（V3版本 - 旋律匹配）'
    )
    parser.add_argument('dance_video', help='原始舞蹈视频文件路径')
    parser.add_argument('reference_video', help='参考视频文件路径（高质量音频）')
    parser.add_argument('-o', '--output', help='输出视频路径')
    parser.add_argument('--max-offset', type=float, default=30.0,
                       help='最大偏移量（秒）(默认: 30.0)')

    args = parser.parse_args()

    # 设置输出路径
    if args.output:
        output_path = args.output
    else:
        base, _ = os.path.splitext(args.dance_video)
        output_path = f"{base}_aligned_v3.mp4"

    # 对齐并合成
    success, offset = align_and_replace_audio(
        args.dance_video,
        args.reference_video,
        output_path,
        args.max_offset
    )

    if success:
        print(f"\n🎉 成功！偏移量: {offset:+.3f} 秒")
    else:
        print("\n❌ 失败")

    exit(0 if success else 1)
