#!/usr/bin/env python3
"""
音频对齐模块 V5 - 使用交叉相关找到相同音乐片段
找出两个音频中相同内容的准确位置
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


def find_best_match_cross_correlation(
    reference_audio_path: str,
    original_audio_path: str,
    max_offset: float = 30.0
) -> Tuple[float, float, float]:
    """
    使用交叉相关找到两个音频中相同片段的准确位置

    Args:
        reference_audio_path: 参考音频路径（高质量音频）
        original_audio_path: 原始音频路径（舞蹈视频的音频）
        max_offset: 最大偏移量（秒）

    Returns:
        (参考音频中开始位置秒数, 相似度分数, 置信度)
    """
    try:
        print("🔍 正在查找相同的音乐片段...")
        print("   使用交叉相关算法...")

        # 加载音频（使用较低采样率加快处理）
        sr = 22050
        y_ref, sr_ref = librosa.load(reference_audio_path, sr=sr)
        y_orig, sr_orig = librosa.load(original_audio_path, sr=sr)

        ref_duration = len(y_ref) / sr
        orig_duration = len(y_orig) / sr

        print(f"   参考音频时长: {ref_duration:.2f}秒")
        print(f"   原始音频时长: {orig_duration:.2f}秒")

        # 计算搜索范围
        max_offset_samples = int(max_offset * sr)

        # 取较短音频的前30秒用于匹配
        compare_duration = min(30.0, orig_duration)
        orig_samples = int(compare_duration * sr)

        # 提取原始音频的开头部分作为模板
        y_orig_template = y_orig[:orig_samples]

        print(f"   使用原始音频的前{compare_duration:.2f}秒作为匹配模板")
        print(f"   在参考音频中搜索...")

        # 计算交叉相关
        # 使用归一化交叉相关找到最佳匹配
        print("   计算交叉相关（这可能需要一点时间）...")

        # 下采样以加快计算
        downsample_factor = 4
        y_orig_ds = y_orig_template[::downsample_factor]
        y_ref_ds = y_ref[::downsample_factor]

        # 计算交叉相关
        correlation = signal.correlate(y_ref_ds, y_orig_ds, mode='valid', method='fft')
        correlation = correlation / (np.std(y_orig_ds) * np.std(y_ref_ds) * len(y_orig_ds))

        # 找到最大相关性的位置
        max_corr_idx = np.argmax(correlation)
        max_corr_value = correlation[max_corr_idx]

        # 转换为秒（考虑下采样）
        ref_start_sample = max_corr_idx * downsample_factor
        ref_start_second = ref_start_sample / sr

        # 限制在合理范围内
        if ref_start_second > max_offset:
            print(f"   ⚠️  最佳匹配位置超出搜索范围，重新搜索...")
            # 在允许范围内找最大值
            max_allowed_idx = int(max_offset * sr / downsample_factor)
            if max_corr_idx > max_allowed_idx:
                correlation_limited = correlation[:max_allowed_idx]
                max_corr_idx = np.argmax(correlation_limited)
                max_corr_value = correlation_limited[max_corr_idx]
                ref_start_sample = max_corr_idx * downsample_factor
                ref_start_second = ref_start_sample / sr

        # 计算置信度
        # 使用MFCC特征验证
        hop_length = 512
        n_mfcc = 13

        # 提取匹配位置的MFCC
        compare_samples = min(orig_samples, len(y_ref) - ref_start_sample)
        if compare_samples < sr:  # 至少1秒
            print(f"   ⚠️  匹配片段太短，使用默认偏移")
            return 0.0, 0.0, 0.0

        y_ref_match = y_ref[ref_start_sample:ref_start_sample + compare_samples]
        y_orig_match = y_orig[:compare_samples]

        mfcc_ref = librosa.feature.mfcc(y=y_ref_match, sr=sr, n_mfcc=n_mfcc, hop_length=hop_length)
        mfcc_orig = librosa.feature.mfcc(y=y_orig_match, sr=sr, n_mfcc=n_mfcc, hop_length=hop_length)

        # 计算MFCC相关性
        min_frames = min(mfcc_ref.shape[1], mfcc_orig.shape[1])
        mfcc_correlations = []
        for i in range(n_mfcc):
            corr = np.corrcoef(mfcc_ref[i, :min_frames], mfcc_orig[i, :min_frames])[0, 1]
            if not np.isnan(corr):
                mfcc_correlations.append(corr)

        avg_mfcc_corr = np.mean(mfcc_correlations) if mfcc_correlations else 0.0

        print(f"\n✅ 找到最佳匹配位置:")
        print(f"   参考音频开始位置: {ref_start_second:+.3f}秒")
        print(f"   交叉相关系数: {max_corr_value:.4f}")
        print(f"   MFCC验证相关性: {avg_mfcc_corr:.4f}")

        # 综合评分
        confidence = (max_corr_value + avg_mfcc_corr) / 2

        if confidence > 0.7:
            print(f"   ✅ 高置信度匹配（{confidence:.2%}）")
        elif confidence > 0.4:
            print(f"   ⚠️  中等置信度匹配（{confidence:.2%}）")
        else:
            print(f"   ❌ 低置信度匹配（{confidence:.2%}），可能不是同一首歌")

        return ref_start_second, avg_mfcc_corr, confidence

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

    Args:
        reference_audio_path: 参考音频路径（高质量）
        original_audio_path: 原始音频路径
        output_audio_path: 输出音频路径
        ref_start_second: 参考音频的开始位置（秒）

    Returns:
        是否成功
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
        print("\n" + "="*60)
        print("🎵 音频对齐工具 V5 - 交叉相关版")
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

        # 步骤2: 使用交叉相关找到最佳匹配位置
        print("\n🎯 步骤 2/4: 查找相同音乐片段")
        print("-"*60)

        ref_start_second, mfcc_score, confidence = find_best_match_cross_correlation(
            reference_audio,
            dance_audio,
            max_offset
        )

        if confidence < 0.3:
            print(f"\n⚠️  警告: 置信度很低({confidence:.2%})")
            print(f"   可能两个音频不是同一首歌")
            print(f"   继续处理...")

        # 步骤3: 对齐并替换音频
        print("\n🔧 步骤 3/4: 对齐并替换音频")
        print("-"*60)

        aligned_audio = os.path.join(tmpdir, "aligned_audio.wav")
        if not align_audio_segment(reference_audio, dance_audio, aligned_audio, ref_start_second):
            return False, 0.0

        # 步骤4: 替换视频音频
        print("\n🎬 步骤 4/4: 合成视频")
        print("-"*60)

        if not replace_audio_in_video(dance_video_path, aligned_audio, output_video_path):
            return False, 0.0

        print("\n" + "="*60)
        print("✅ 全部完成!")
        print(f"📁 输出文件: {output_video_path}")
        print(f"📊 从参考音频的 {ref_start_second:+.3f} 秒处开始")
        print(f"🎵 MFCC相似度: {mfcc_score:.4f}")
        print(f"📈 综合置信度: {confidence:.2%}")
        print("="*60 + "\n")

        return True, ref_start_second


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='对齐两个视频的音频并合成（V5版本 - 交叉相关）'
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
        output_path = f"{base}_aligned_v5.mp4"

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
