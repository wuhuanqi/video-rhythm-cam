#!/usr/bin/env python3
"""
找出两个音频中最相似的部分并对其
适用于同一首歌的不同片段
"""

import os
import tempfile
import numpy as np
import librosa
import soundfile as sf
from typing import Tuple, Dict
from scipy import signal
from moviepy import VideoFileClip, AudioFileClip


def extract_audio_from_video(video_path: str, output_audio: str) -> bool:
    """从视频中提取音频"""
    try:
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


def find_best_matching_segment(
    audio1_path: str,
    audio2_path: str,
    min_segment_length: float = 10.0
) -> Dict:
    """
    找出两个音频中最相似的片段（滑动窗口方式）

    Args:
        audio1_path: 参考音频路径
        audio2_path: 原始音频路径
        min_segment_length: 最小片段长度（秒）

    Returns:
        包含最佳匹配信息的字典
    """
    try:
        print("🔍 正在分析音频，寻找最相似的部分...")

        # 加载音频
        y1, sr = librosa.load(audio1_path, sr=22050)
        y2, sr2 = librosa.load(audio2_path, sr=22050)

        duration1 = len(y1) / sr
        duration2 = len(y2) / sr

        print(f"   音频1时长: {duration1:.2f}秒")
        print(f"   音频2时长: {duration2:.2f}秒")

        # 提取MFCC特征（最能反映旋律和音色）
        hop_length = 512
        n_mfcc = 20

        print(f"   正在提取MFCC特征...")
        mfcc1 = librosa.feature.mfcc(y=y1, sr=sr, n_mfcc=n_mfcc, hop_length=hop_length)
        mfcc2 = librosa.feature.mfcc(y=y2, sr=sr, n_mfcc=n_mfcc, hop_length=hop_length)

        # 计算最小片段长度对应的帧数
        min_frames = int(min_segment_length * sr / hop_length)

        print(f"   正在搜索最佳匹配片段（最小{min_segment_length}秒）...")

        # 在音频1中滑动窗口，寻找与音频2开头最匹配的部分
        # 我们假设音频2的开头需要和音频1的某一部分对齐
        best_score = float('inf')
        best_pos_in_audio1 = 0

        # 只搜索音频1的前80%（确保有足够的音频来对齐）
        max_search_frames = int(len(mfcc1[0]) * 0.8)
        compare_frames = min(len(mfcc2[0]), max_search_frames)

        # 滑动窗口搜索
        for start_pos in range(0, max_search_frames, 10):  # 步长10加速
            end_pos = min(start_pos + compare_frames, len(mfcc1[0]))

            if end_pos - start_pos < min_frames:
                continue

            # 提取音频1的这个片段
            mfcc1_segment = mfcc1[:, start_pos:end_pos]

            # 提取音频2的开头片段
            mfcc2_segment = mfcc2[:, :min(len(mfcc2[0]), end_pos - start_pos)]

            # 确保两个片段长度一致
            min_len = min(len(mfcc1_segment[0]), len(mfcc2_segment[0]))
            if min_len < min_frames:
                continue

            mfcc1_segment = mfcc1_segment[:, :min_len]
            mfcc2_segment = mfcc2_segment[:, :min_len]

            # 计算距离（使用DTW）
            D = librosa.sequence.dtw(mfcc1_segment, mfcc2_segment)[0]
            score = D[-1, -1]  # DTW路径的总距离

            if score < best_score:
                best_score = score
                best_pos_in_audio1 = start_pos

        # 转换为时间（秒）
        best_time_in_audio1 = best_pos_in_audio1 * hop_length / sr
        best_time_in_audio2 = 0.0  # 我们假设音频2从头开始

        print(f"\n✅ 找到最相似的部分!")
        print(f"   音频1位置: {best_time_in_audio1:.2f}秒")
        print(f"   音频2位置: {best_time_in_audio2:.2f}秒")
        print(f"   相似度距离: {best_score:.2f} (越小越相似)")

        # 计算偏移量
        offset = best_time_in_audio1 - best_time_in_audio2

        print(f"   偏移量: {offset:+.2f}秒")

        return {
            'audio1_time': best_time_in_audio1,
            'audio2_time': best_time_in_audio2,
            'offset': offset,
            'distance': best_score,
            'hop_length': hop_length,
            'sr': sr
        }

    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def align_audios_at_best_match(
    reference_audio_path: str,
    original_audio_path: str,
    output_audio_path: str,
    match_info: Dict
) -> bool:
    """
    基于最佳匹配位置对齐音频

    Args:
        reference_audio_path: 参考音频路径
        original_audio_path: 原始音频路径
        output_audio_path: 输出音频路径
        match_info: 匹配信息字典

    Returns:
        是否成功
    """
    try:
        print(f"🔧 正在对齐音频...")

        # 加载音频
        y_ref, sr = librosa.load(reference_audio_path)
        y_orig, sr_orig = librosa.load(original_audio_path)

        if sr != sr_orig:
            y_orig, sr = librosa.load(original_audio_path, sr=sr)

        ref_duration = len(y_ref) / sr
        orig_duration = len(y_orig) / sr

        offset = match_info['offset']
        offset_samples = int(offset * sr)

        print(f"   参考音频时长: {ref_duration:.2f}秒")
        print(f"   原始音频时长: {orig_duration:.2f}秒")
        print(f"   偏移量: {offset:+.3f}秒")

        # 应用偏移
        if offset_samples > 0:
            # 正偏移：从参考音频的 offset_samples 位置开始截取
            # 因为 offset > 0 表示参考音频的这个位置才是对齐点
            y_ref_aligned = y_ref[offset_samples:]
        elif offset_samples < 0:
            # 负偏移：参考音频前面需要填充
            y_ref_aligned = np.concatenate([y_orig[:offset_samples], y_ref])
        else:
            y_ref_aligned = y_ref

        aligned_duration = len(y_ref_aligned) / sr
        print(f"   对齐后时长: {aligned_duration:.2f}秒")

        # 裁剪到原始音频长度
        final_samples = min(len(y_orig), len(y_ref_aligned))
        y_ref_final = y_ref_aligned[:final_samples]

        print(f"   最终时长: {final_samples/sr:.2f}秒")

        # 保存对齐后的音频
        sf.write(output_audio_path, y_ref_final, sr)

        print(f"✅ 音频对齐完成: {os.path.basename(output_audio_path)}")
        return True

    except Exception as e:
        print(f"❌ 对齐失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def replace_audio_in_video(
    video_path: str,
    new_audio_path: str,
    output_video_path: str
) -> bool:
    """替换视频的音频"""
    try:
        print(f"🎬 正在合成视频...")

        video = VideoFileClip(video_path)
        new_audio = AudioFileClip(new_audio_path)

        print(f"   视频时长: {video.duration:.2f}秒")
        print(f"   音频时长: {new_audio.duration:.2f}秒")

        # 调整时长
        if new_audio.duration < video.duration:
            video = video.subclipped(0, new_audio.duration)
        elif new_audio.duration > video.duration:
            new_audio = new_audio.subclipped(0, video.duration)

        final_video = video.with_audio(new_audio)

        final_video.write_videofile(
            output_video_path,
            codec='libx264',
            audio_codec='aac',
            logger=None
        )

        video.close()
        new_audio.close()
        final_video.close()

        print(f"✅ 视频合成完成: {os.path.basename(output_video_path)}")
        return True

    except Exception as e:
        print(f"❌ 合成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def align_videos_by_best_match(
    dance_video_path: str,
    reference_video_path: str,
    output_video_path: str
) -> Tuple[bool, Dict]:
    """
    通过找出最相似的部分来对齐两个视频的音频

    Args:
        dance_video_path: 原始舞蹈视频路径
        reference_video_path: 参考视频路径
        output_video_path: 输出视频路径

    Returns:
        (是否成功, 匹配信息)
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        print("\n" + "="*60)
        print("🎵 音频对齐工具 - 最佳匹配版")
        print("="*60)

        # 步骤1: 提取音频
        print("\n📤 步骤 1/4: 提取音频")
        print("-"*60)

        dance_audio = os.path.join(tmpdir, "dance_audio.wav")
        reference_audio = os.path.join(tmpdir, "reference_audio.wav")

        if not extract_audio_from_video(dance_video_path, dance_audio):
            return False, None

        if not extract_audio_from_video(reference_video_path, reference_audio):
            return False, None

        # 步骤2: 找出最相似的部分
        print("\n🎯 步骤 2/4: 寻找最佳匹配")
        print("-"*60)

        match_info = find_best_matching_segment(reference_audio, dance_audio)

        if match_info is None:
            return False, None

        # 步骤3: 对齐音频
        print("\n🔧 步骤 3/4: 对齐音频")
        print("-"*60)

        aligned_audio = os.path.join(tmpdir, "aligned_audio.wav")
        if not align_audios_at_best_match(reference_audio, dance_audio, aligned_audio, match_info):
            return False, None

        # 步骤4: 替换视频音频
        print("\n🎬 步骤 4/4: 替换视频音频")
        print("-"*60)

        if not replace_audio_in_video(dance_video_path, aligned_audio, output_video_path):
            return False, None

        print("\n" + "="*60)
        print("✅ 全部完成!")
        print(f"📁 输出文件: {output_video_path}")
        print(f"📊 音频1匹配点: {match_info['audio1_time']:.2f}秒")
        print(f"📊 音频2匹配点: {match_info['audio2_time']:.2f}秒")
        print(f"📊 偏移量: {match_info['offset']:+.2f}秒")
        print("="*60 + "\n")

        return True, match_info


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='通过找出最相似的部分来对齐音频'
    )
    parser.add_argument('dance_video', help='原始舞蹈视频文件路径')
    parser.add_argument('reference_video', help='参考视频文件路径')
    parser.add_argument('-o', '--output', help='输出视频路径')

    args = parser.parse_args()

    # 设置输出路径
    if args.output:
        output_path = args.output
    else:
        base, _ = os.path.splitext(args.dance_video)
        output_path = f"{base}_best_match.mp4"

    # 对齐并合成
    success, match_info = align_videos_by_best_match(
        args.dance_video,
        args.reference_video,
        output_path
    )

    if success:
        print(f"\n🎉 成功！")
    else:
        print("\n❌ 失败")

    exit(0 if success else 1)
