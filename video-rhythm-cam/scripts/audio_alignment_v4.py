#!/usr/bin/env python3
"""
音频对齐模块 V4 - 修复版本
修复了音频长度差异大时的匹配问题
"""

import os
import tempfile
import numpy as np
import librosa
import soundfile as sf
from typing import Tuple
from tqdm import tqdm


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

        # 创建进度条
        with tqdm(
            total=100,
            desc=f"  提取音频 {os.path.basename(video_path)[:20]}",
            unit="%",
            ncols=80,
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}"
        ) as pbar:
            def progress_callback(progress):
                pbar.update(int(progress * 100) - pbar.n)

            # 注意：moviepy 不直接支持进度回调，所以我们用估算
            for i in range(10):
                pbar.update(10)
                import time
                time.sleep(0.05)

            audio.write_audiofile(output_audio, logger=None)
            pbar.update(100 - pbar.n)

        audio.close()
        video.close()

        print(f"✅ 音频已提取: {os.path.basename(output_audio)}")
        return True
    except Exception as e:
        print(f"❌ 提取音频失败: {e}")
        return False


def find_best_match_simple(
    reference_audio_path: str,
    original_audio_path: str,
    max_offset: float = 30.0
) -> Tuple[float, float, float]:
    """
    简化的最佳匹配算法 - 先检查长度差异，再进行精细匹配

    Args:
        reference_audio_path: 参考音频路径（高质量音频）
        original_audio_path: 原始音频路径（舞蹈视频的音频）
        max_offset: 最大偏移量（秒）

    Returns:
        (最佳偏移量, 相似度分数, 相似度分数)
    """
    try:
        print("🔍 正在分析音频...")

        # 加载音频
        print("  [1/4] 加载参考音频...")
        y_ref, sr = librosa.load(reference_audio_path, sr=22050)
        print("  [2/4] 加载原始音频...")
        y_orig, sr_orig = librosa.load(original_audio_path, sr=22050)

        ref_duration = len(y_ref) / sr
        orig_duration = len(y_orig) / sr

        print(f"   参考音频时长: {ref_duration:.2f}秒")
        print(f"   原始音频时长: {orig_duration:.2f}秒")
        print(f"   长度差异: {abs(ref_duration - orig_duration):.2f}秒")

        # 计算长度差异
        duration_diff = ref_duration - orig_duration

        # 提取特征用于验证匹配
        hop_length = 512
        n_mfcc = 13

        print("  [3/4] 提取MFCC特征...")
        # 只提取前10秒的特征进行快速验证
        compare_duration = min(10.0, ref_duration, orig_duration)
        compare_samples = int(compare_duration * sr)

        with tqdm(total=2, desc="    提取特征", unit="个", ncols=70, leave=False) as pbar:
            mfcc_ref = librosa.feature.mfcc(
                y=y_ref[:compare_samples],
                sr=sr,
                n_mfcc=n_mfcc,
                hop_length=hop_length
            )
            pbar.update(1)
            pbar.set_description("    参考音频")

            mfcc_orig = librosa.feature.mfcc(
                y=y_orig[:compare_samples],
                sr=sr,
                n_mfcc=n_mfcc,
                hop_length=hop_length
            )
            pbar.update(1)
            pbar.set_description("    原始音频")

        print("  [4/4] 计算相似度...")

        # 计算开头部分的相关性
        min_frames = min(mfcc_ref.shape[1], mfcc_orig.shape[1])

        # 如果参考音频比原始音频长很多，尝试从不同位置开始匹配
        if duration_diff > 0.5:  # 参考音频比原始音频长0.5秒以上
            print(f"   参考音频更长，尝试从不同位置匹配...")

            best_offset = 0.0
            best_score = -float('inf')

            # 尝试从参考音频的不同位置开始
            # 范围：从0秒到duration_diff秒
            search_offsets = np.linspace(0, min(duration_diff, max_offset), 20)

            with tqdm(
                total=len(search_offsets),
                desc="  匹配音频位置",
                unit="次",
                ncols=80
            ) as pbar:
                for test_offset in search_offsets:
                    start_sample = int(test_offset * sr)
                    if start_sample + compare_samples > len(y_ref):
                        continue

                    # 提取参考音频从test_offset开始的片段
                    mfcc_ref_slice = librosa.feature.mfcc(
                        y=y_ref[start_sample:start_sample + compare_samples],
                        sr=sr,
                        n_mfcc=n_mfcc,
                        hop_length=hop_length
                    )

                    # 计算相关性
                    frames = min(mfcc_ref_slice.shape[1], mfcc_orig.shape[1])
                    if frames < 10:
                        continue

                    # 计算平均相关性
                    correlations = []
                    for i in range(n_mfcc):
                        corr = np.corrcoef(mfcc_ref_slice[i, :frames], mfcc_orig[i, :frames])[0, 1]
                        if not np.isnan(corr):
                            correlations.append(corr)

                    if correlations:
                        score = np.mean(correlations)
                        if score > best_score:
                            best_score = score
                            best_offset = test_offset

                    pbar.update(1)
                    pbar.set_postfix({"最佳相似度": f"{best_score:.4f}"})

            print(f"\n✅ 最佳匹配位置:")
            print(f"   偏移量: {best_offset:+.3f}秒")
            print(f"   相似度: {best_score:.4f}")

            return best_offset, best_score, best_score

        elif duration_diff < -2.0:  # 参考音频比原始音频短2秒以上
            print(f"   参考音频更短，需要在前面加静音")
            offset = abs(duration_diff)

            # 验证开头是否匹配
            frames = min(mfcc_ref.shape[1], mfcc_orig.shape[1])
            correlations = []
            for i in range(n_mfcc):
                corr = np.corrcoef(mfcc_ref[i, :frames], mfcc_orig[i, :frames])[0, 1]
                if not np.isnan(corr):
                    correlations.append(corr)

            score = np.mean(correlations) if correlations else 0.0

            print(f"\n✅ 最佳匹配位置:")
            print(f"   偏移量: {offset:+.3f}秒 (前面加静音)")
            print(f"   相似度: {score:.4f}")

            return offset, score, score

        else:
            # 长度接近，直接从头匹配
            print(f"   音频长度接近，从头开始匹配")

            frames = min(mfcc_ref.shape[1], mfcc_orig.shape[1])
            correlations = []
            for i in range(n_mfcc):
                corr = np.corrcoef(mfcc_ref[i, :frames], mfcc_orig[i, :frames])[0, 1]
                if not np.isnan(corr):
                    correlations.append(corr)

            score = np.mean(correlations) if correlations else 0.0

            print(f"\n✅ 最佳匹配位置:")
            print(f"   偏移量: 0.000秒 (从头开始)")
            print(f"   相似度: {score:.4f}")

            return 0.0, score, score

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
            # 正偏移：从参考音频的offset位置开始截取
            if offset_samples < len(y_ref):
                y_ref_aligned = y_ref[offset_samples:]
            else:
                print(f"   ⚠️  偏移量超过音频长度，使用静音")
                y_ref_aligned = np.zeros(len(y_orig))
            aligned_duration = len(y_ref_aligned) / sr
            print(f"   从参考音频的第{offset:.2f}秒开始")
        elif offset_samples < 0:
            # 负偏移：参考音频前面截断（这种情况很少）
            y_ref_aligned = y_ref[-offset_samples:]
            aligned_duration = len(y_ref_aligned) / sr
        else:
            y_ref_aligned = y_ref
            aligned_duration = ref_duration

        print(f"   对齐后时长: {aligned_duration:.2f}秒")

        # 计算最终时长（取两个音频的最小时长）
        final_duration = min(orig_duration, aligned_duration)
        final_samples = int(final_duration * sr)

        print(f"   最终时长: {final_duration:.2f}秒")

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
        import threading
        import time

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

        # 创建进度条
        with tqdm(
            total=100,
            desc=f"  合成视频 {os.path.basename(output_video_path)[:20]}",
            unit="%",
            ncols=80,
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}"
        ) as pbar:
            # 标记是否完成
            write_done = [False]

            # 启动后台线程模拟进度
            def update_progress():
                progress = 0
                while not write_done[0] and progress < 95:
                    # 模拟进度增长（非线性的）
                    increment = max(0.5, 5 - progress * 0.05)
                    progress = min(progress + increment, 95)
                    pbar.n = int(progress)
                    pbar.refresh()
                    time.sleep(0.2)

            progress_thread = threading.Thread(target=update_progress)
            progress_thread.daemon = True
            progress_thread.start()

            # 写入输出文件
            final_video.write_videofile(
                output_video_path,
                codec='libx264',
                audio_codec='aac',
                logger=None
            )

            # 标记完成
            write_done[0] = True
            progress_thread.join(timeout=1)
            pbar.update(100 - pbar.n)

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
        print("🎵 音频对齐工具 V4 - 修复版")
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

        # 步骤2: 计算最佳偏移
        print("\n🎯 步骤 2/4: 分析音频偏移")
        print("-"*60)

        offset, mfcc_score, chroma_score = find_best_match_simple(
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
        print(f"🎵 相似度: {mfcc_score:.4f}")
        print("="*60 + "\n")

        return True, offset


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='对齐两个视频的音频并合成（V4版本 - 修复版）'
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
        output_path = f"{base}_aligned_v4.mp4"

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
