#!/usr/bin/env python3
"""
音频对齐模块 V6 - 基于Chroma特征（音级/调性）
使用chroma特征匹配，对速度变化和音色差异更鲁棒
能够识别同一首歌的旋律骨架
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


def find_match_with_chroma(
    reference_audio_path: str,
    original_audio_path: str,
    max_offset: float = 60.0
) -> Tuple[float, float, float]:
    """
    使用Chroma特征（音级/调性）找到匹配位置

    Chroma特征将音频映射到12个音级，对速度和音色变化鲁棒
    适合识别同一首歌的不同版本/速度

    Args:
        reference_audio_path: 参考音频路径
        original_audio_path: 原始音频路径
        max_offset: 最大偏移量（秒）

    Returns:
        (参考音频开始位置秒数, chroma相似度, 置信度)
    """
    try:
        print("🔍 正在使用Chroma特征（音级/调性）分析...")
        print("   这种方法对速度和音色差异更鲁棒...")

        # 加载音频
        sr = 22050
        y_ref, sr_ref = librosa.load(reference_audio_path, sr=sr)
        y_orig, sr_orig = librosa.load(original_audio_path, sr=sr)

        ref_duration = len(y_ref) / sr
        orig_duration = len(y_orig) / sr

        print(f"   参考音频时长: {ref_duration:.2f}秒")
        print(f"   原始音频时长: {orig_duration:.2f}秒")

        # 提取Chroma特征
        # Chroma将音频映射到12个音级（C, C#, D, D#, E, F, F#, G, G#, A, A#, B）
        hop_length = 512

        print(f"   正在提取Chroma特征（音级/调性）...")

        # 使用更长的窗口提高频率分辨率
        chroma_ref = librosa.feature.chroma_cqt(
            y=y_ref,
            sr=sr,
            hop_length=hop_length,
            n_octaves=7,
            bins_per_octave=36
        )

        chroma_orig = librosa.feature.chroma_cqt(
            y=y_orig,
            sr=sr,
            hop_length=hop_length,
            n_octaves=7,
            bins_per_octave=36
        )

        print(f"   Chroma特征形状:")
        print(f"     参考音频: {chroma_ref.shape}")
        print(f"     原始音频: {chroma_orig.shape}")

        # 使用原始音频的前N秒作为模板
        compare_duration = min(orig_duration, 30.0)  # 最多30秒
        orig_frames = int(compare_duration * sr / hop_length)

        chroma_orig_template = chroma_orig[:, :orig_frames]

        print(f"\n   在参考音频中搜索匹配...")
        print(f"   搜索范围: 前{max_offset:.0f}秒")
        print(f"   模板长度: {compare_duration:.2f}秒")

        # 滑动窗口搜索
        best_offset = 0.0
        best_score = -float('inf')
        scores = []

        # 计算最大搜索帧数
        max_search_frames = int(max_offset * sr / hop_length)
        max_search_frames = min(max_search_frames, chroma_ref.shape[1] - orig_frames)

        # 使用较大的步长加速搜索
        step = max(1, max_search_frames // 200)  # 最多检查200个位置

        print(f"   检查 {max_search_frames // step + 1} 个位置...")

        for offset in range(0, max_search_frames + 1, step):
            ref_end = offset + orig_frames

            if ref_end > chroma_ref.shape[1]:
                break

            # 提取对应片段
            chroma_ref_slice = chroma_ref[:, offset:ref_end]

            # 计算Chroma相似度
            # 使用多种距离度量
            # 1. 欧氏距离（L2距离）
            l2_dist = np.linalg.norm(chroma_ref_slice - chroma_orig_template)

            # 2. 余弦相似度
            flat_ref = chroma_ref_slice.flatten()
            flat_orig = chroma_orig_template.flatten()

            cosine_sim = np.dot(flat_ref, flat_orig) / (
                np.linalg.norm(flat_ref) * np.linalg.norm(flat_orig)
            )

            # 3. 逐帧相关性
            frame_corrs = []
            min_frames = min(chroma_ref_slice.shape[1], chroma_orig_template.shape[1])
            for i in range(12):  # 12个音级
                corr = np.corrcoef(
                    chroma_ref_slice[i, :min_frames],
                    chroma_orig_template[i, :min_frames]
                )[0, 1]
                if not np.isnan(corr):
                    frame_corrs.append(corr)

            avg_corr = np.mean(frame_corrs) if frame_corrs else 0.0

            # 综合分数（余弦相似度权重最高）
            combined_score = cosine_sim * 0.6 + avg_corr * 0.4

            scores.append((offset, combined_score, cosine_sim, avg_corr))

            if combined_score > best_score:
                best_score = combined_score
                best_offset = offset

        # 转换为秒
        best_offset_second = best_offset * hop_length / sr

        # 获取最佳位置的详细分数
        best_entry = max(scores, key=lambda x: x[1])
        best_cosine = best_entry[2]
        best_avg_corr = best_entry[3]

        print(f"\n✅ 找到最佳匹配位置:")
        print(f"   参考音频开始位置: {best_offset_second:+.3f}秒")
        print(f"   综合相似度: {best_score:.4f}")
        print(f"   余弦相似度: {best_cosine:.4f}")
        print(f"   Chroma相关性: {best_avg_corr:.4f}")

        # 计算置信度
        confidence = best_score

        if confidence > 0.7:
            print(f"   ✅ 高置信度匹配（{confidence:.2%}）")
        elif confidence > 0.4:
            print(f"   ⚠️  中等置信度匹配（{confidence:.2%}）")
        else:
            print(f"   ❌ 低置信度匹配（{confidence:.2%}）")
            print(f"   💡 可能不是同一首歌，或者版本差异很大")

        return best_offset_second, best_avg_corr, confidence

    except Exception as e:
        print(f"❌ 计算偏移量失败: {e}")
        import traceback
        traceback.print_exc()
        return 0.0, 0.0, 0.0


def align_audio_segment(
    reference_audio_path: str,
    original_audio_path: str,
    output_audio_path: str,
    ref_start_second: float
) -> bool:
    """
    从参考音频的指定位置开始，替换原始音频
    """
    try:
        print(f"🔧 正在对齐并替换音频...")

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
        print(f"   从参考音频的 {ref_start_second:.3f}秒 处开始")

        # 从参考音频的指定位置开始截取
        ref_start_sample = int(ref_start_second * sr)

        if ref_start_sample >= len(y_ref):
            print(f"   ❌ 开始位置超出参考音频长度")
            return False

        y_ref_aligned = y_ref[ref_start_sample:]

        # 计算最终时长（取两个音频的最小时长）
        final_duration = min(orig_duration, len(y_ref_aligned) / sr)
        final_samples = int(final_duration * sr)

        print(f"   对齐后时长: {final_duration:.2f}秒")

        # 裁剪到相同长度
        if len(y_ref_aligned) > final_samples:
            y_ref_final = y_ref_aligned[:final_samples]
        else:
            # 如果参考音频太短，后面加静音
            silence = np.zeros(final_samples - len(y_ref_aligned))
            y_ref_final = np.concatenate([y_ref_aligned, silence])

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
    """
    try:
        from moviepy import VideoFileClip, AudioFileClip

        print(f"🎬 正在合成视频...")

        # 加载视频和音频
        video = VideoFileClip(video_path)
        new_audio = AudioFileClip(new_audio_path)

        print(f"   视频时长: {video.duration:.2f}秒")
        print(f"   音频时长: {new_audio.duration:.2f}秒")

        # 裁剪到相同长度
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
    max_offset: float = 60.0
) -> Tuple[bool, float]:
    """
    对齐两个视频的音频并替换到舞蹈视频中

    Args:
        dance_video_path: 原始舞蹈视频路径
        reference_video_path: 参考视频路径（包含高质量音频）
        output_video_path: 输出视频路径
        max_offset: 最大偏移量（秒）

    Returns:
        (是否成功, 参考音频开始位置)
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        print("\n" + "="*70)
        print("🎵 音频对齐工具 V6 - Chroma特征版（音级/调性）")
        print("="*70)

        # 步骤1: 提取音频
        print("\n📤 步骤 1/4: 提取音频")
        print("-"*70)

        dance_audio = os.path.join(tmpdir, "dance_audio.wav")
        reference_audio = os.path.join(tmpdir, "reference_audio.wav")

        if not extract_audio_from_video(dance_video_path, dance_audio):
            return False, 0.0

        if not extract_audio_from_video(reference_video_path, reference_audio):
            return False, 0.0

        # 步骤2: 使用Chroma特征找到最佳匹配位置
        print("\n🎯 步骤 2/4: 使用Chroma特征查找匹配")
        print("-"*70)

        ref_start_second, chroma_score, confidence = find_match_with_chroma(
            reference_audio,
            dance_audio,
            max_offset
        )

        if confidence < 0.2:
            print(f"\n⚠️  警告: 置信度很低({confidence:.2%})")
            print(f"   继续...")

        # 步骤3: 对齐并替换音频
        print("\n🔧 步骤 3/4: 对齐并替换音频")
        print("-"*70)

        aligned_audio = os.path.join(tmpdir, "aligned_audio.wav")
        if not align_audio_segment(reference_audio, dance_audio, aligned_audio, ref_start_second):
            return False, 0.0

        # 步骤4: 替换视频音频
        print("\n🎬 步骤 4/4: 合成视频")
        print("-"*70)

        if not replace_audio_in_video(dance_video_path, aligned_audio, output_video_path):
            return False, 0.0

        print("\n" + "="*70)
        print("✅ 全部完成!")
        print(f"📁 输出文件: {output_video_path}")
        print(f"📊 从参考音频的 {ref_start_second:+.3f} 秒处开始")
        print(f"🎼 Chroma相似度: {chroma_score:.4f}")
        print(f"📈 综合置信度: {confidence:.2%}")
        print("="*70 + "\n")

        return True, ref_start_second


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='对齐两个视频的音频并合成（V6版本 - Chroma特征）'
    )
    parser.add_argument('dance_video', help='原始视频文件路径')
    parser.add_argument('reference_video', help='参考视频文件路径（高质量音频）')
    parser.add_argument('-o', '--output', help='输出视频路径')
    parser.add_argument('--max-offset', type=float, default=60.0,
                       help='最大偏移量（秒）(默认: 60.0)')

    args = parser.parse_args()

    # 设置输出路径
    if args.output:
        output_path = args.output
    else:
        base, _ = os.path.splitext(args.dance_video)
        output_path = f"{base}_aligned_v6.mp4"

    # 对齐并合成
    success, offset = align_and_replace_audio(
        args.dance_video,
        args.reference_video,
        output_path,
        args.max_offset
    )

    if success:
        print(f"\n🎉 成功！从参考音频的 {offset:+.3f} 秒处开始")
    else:
        print("\n❌ 失败")

    exit(0 if success else 1)
