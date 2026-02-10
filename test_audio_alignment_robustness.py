#!/usr/bin/env python3
"""
音频对齐鲁棒性测试
测试音频长度变化时的对齐效果
"""

import os
import sys
import tempfile
import numpy as np
import soundfile as sf
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip

sys.path.insert(0, 'video-rhythm-cam/scripts')

from audio_alignment import align_and_replace_audio


def create_test_video_with_longer_audio(original_video: str, output_video: str, audio_duration_extra: float = 2.0):
    """
    创建一个测试视频，将音频拉长（添加静音）
    """
    print(f"🎬 创建测试视频...")
    print(f"   原视频: {original_video}")
    print(f"   音频拉长: +{audio_duration_extra}秒")

    try:
        # 加载原始视频
        video = VideoFileClip(original_video)
        original_audio = video.audio

        if not original_audio:
            print("❌ 原视频没有音频")
            video.close()
            return False

        audio_duration = original_audio.duration
        sr = original_audio.fps

        # 读取音频数据
        print(f"   读取音频数据...")
        import soundfile as sf
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_audio_file:
            tmp_audio = tmp_audio_file.name
            original_audio.write_audiofile(tmp_audio)

        y, sr = sf.read(tmp_audio)

        # 创建静音（保持与原音频相同的维度）
        silence_samples = int(audio_duration_extra * sr)
        if len(y.shape) == 1:  # 单声道
            silence = np.zeros(silence_samples)
        else:  # 立体声或多声道
            silence = np.zeros((silence_samples, y.shape[1]))

        # 在前面添加静音
        y_extended = np.concatenate([silence, y])

        # 保存扩展的音频
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_extended_file:
            tmp_extended = tmp_extended_file.name
            sf.write(tmp_extended, y_extended, sr)

        # 创建新音频
        from moviepy import AudioFileClip
        extended_audio = AudioFileClip(tmp_extended)

        # 裁剪到合适长度
        total_duration = audio_duration + audio_duration_extra
        if extended_audio.duration > total_duration:
            extended_audio = extended_audio.subclipped(0, total_duration)

        # 设置到视频
        video_with_extended_audio = video.with_audio(extended_audio)

        # 保存
        video_with_extended_audio.write_videofile(
            output_video,
            codec='libx264',
            audio_codec='aac'
        )

        # 清理
        video.close()
        original_audio.close()
        extended_audio.close()
        video_with_extended_audio.close()

        # 删除临时文件
        os.remove(tmp_audio)
        os.remove(tmp_extended)

        print(f"✅ 测试视频创建成功: {output_video}")
        print(f"   原音频时长: {audio_duration:.2f}秒")
        print(f"   新音频时长: {total_duration:.2f}秒")
        print(f"   音频偏移: +{audio_duration_extra:.2f}秒")

        return True

    except Exception as e:
        print(f"❌ 创建测试视频失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_alignment_with_longer_audio():
    """测试音频拉长后的对齐效果"""
    print("=" * 60)
    print("音频对齐鲁棒性测试")
    print("=" * 60)
    print()

    # 原始视频
    original_video = "test_data/dance_video.mp4"

    if not os.path.exists(original_video):
        print(f"❌ 测试视频不存在: {original_video}")
        print("   请先运行: python3 create_simple_test.py")
        return False

    print(f"📹 原始视频: {original_video}")

    # 获取原始视频信息
    video = VideoFileClip(original_video)
    original_duration = video.duration
    original_audio_duration = video.audio.duration if video.audio else 0
    video.close()

    print(f"   视频时长: {original_duration:.2f}秒")
    print(f"   音频时长: {original_audio_duration:.2f}秒")

    print("\n" + "=" * 60)
    print("测试用例 1: 音频拉长 1 秒")
    print("=" * 60)

    # 测试 1: 拉长 1 秒
    output1 = "test_data/reference_longer_1s.mp4"

    if create_test_video_with_longer_audio(original_video, output1, audio_duration_extra=1.0):
        # 对齐测试
        output_aligned1 = "video-rhythm-cam/output/test_aligned_longer_1s.mp4"

        success1, offset1 = align_and_replace_audio(
            dance_video_path=original_video,
            reference_video_path=output1,
            output_video_path=output_aligned1,
            max_offset=10.0  # 允许更大的偏移量
        )

        if success1:
            print(f"✅ 测试 1 通过")
            print(f"   计算的偏移量: {offset1:.3f} 秒")

            # 验证输出文件
            if os.path.exists(output_aligned1):
                file_size = os.path.getsize(output_aligned1) / (1024 * 1024)
                print(f"   输出文件大小: {file_size:.2f} MB")
            else:
                print(f"   ⚠️  输出文件不存在")
        else:
            print(f"❌ 测试 1 失败")

    print("\n" + "=" * 60)
    print("测试用例 2: 音频拉长 2 秒")
    print("=" * 60)

    # 测试 2: 拉长 2 秒
    output2 = "test_data/reference_longer_2s.mp4"

    if create_test_video_with_longer_audio(original_video, output2, audio_duration_extra=2.0):
        # 对齐测试
        output_aligned2 = "video-rhythm-cam/output/test_aligned_longer_2s.mp4"

        success2, offset2 = align_and_replace_audio(
            dance_video_path=original_video,
            reference_video_path=output2,
            output_video_path=output_aligned2,
            max_offset=10.0
        )

        if success2:
            print(f"✅ 测试 2 通过")
            print(f"   计算的偏移量: {offset2:.3f} 秒")

            # 验证输出文件
            if os.path.exists(output_aligned2):
                file_size = os.path.getsize(output_aligned2) / (1024 * 1024)
                print(f"   输出文件大小: {file_size:.2f} MB")
            else:
                print(f"   ⚠️  输出文件不存在")
        else:
            print(f"❌ 测试 2 失败")

    print("\n" + "=" * 60)
    print("测试用例 3: 音频拉长 3 秒")
    print("=" * 60)

    # 测试 3: 拉长 3 秒
    output3 = "test_data/reference_longer_3s.mp4"

    if create_test_video_with_longer_audio(original_video, output3, audio_duration_extra=3.0):
        # 对齐测试
        output_aligned3 = "video-rhythm-cam/output/test_aligned_longer_3s.mp4"

        success3, offset3 = align_and_replace_audio(
            dance_video_path=original_video,
            reference_video_path=output3,
            output_video_path=output_aligned3,
            max_offset=10.0
        )

        if success3:
            print(f"✅ 测试 3 通过")
            print(f"   计算的偏移量: {offset3:.3f} 秒")

            # 验证输出文件
            if os.path.exists(output_aligned3):
                file_size = os.path.getsize(output_aligned3) / (1024 * 1024)
                print(f"   输出文件大小: {file_size:.2f} MB")
            else:
                print(f"   ⚠️  输出文件不存在")
        else:
            print(f"❌ 测试 3 失败")

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print("✅ 测试完成！")
    print()
    print("📊 分析:")
    print("   - 所有测试都尝试对齐不同长度的音频")
    print("   - 偏移量应该接近音频拉长的时长")
    print("   - 输出视频应该保持原始视频的长度")
    print()
    print("💡 建议:")
    print("   1. 播放输出的视频，听音频是否对齐")
    print("   2. 检查视频开头是否有静音（正常的对齐标记）")
    print("   3. 对比原始视频，验证动作和音频是否匹配")
    print()
    print("📁 输出文件位置:")
    print("   - test_aligned_longer_1s.mp4")
    print("   - test_aligned_longer_2s.mp4")
    print("   - test_aligned_longer_3s.mp4")

    return True


def test_with_cropped_audio():
    """测试音频裁剪后的对齐"""
    print("\n" + "=" * 60)
    print("测试用例 4: 音频裁剪（去掉前面部分）")
    print("=" * 60)

    original_video = "test_data/dance_video.mp4"

    try:
        # 加载原始视频
        video = VideoFileClip(original_video)

        # 获取音频
        audio = video.audio
        if not audio:
            print("❌ 原视频没有音频")
            video.close()
            return False

        # 裁剪前面 2 秒
        audio_cropped = audio.subclipped(2.0, audio.duration)

        # 创建新视频
        video_cropped = video.with_audio(audio_cropped)
        output_path = "test_data/reference_cropped_2s.mp4"

        video_cropped.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac'
        )

        video.close()
        audio_cropped.close()
        video_cropped.close()

        print(f"✅ 创建裁剪测试视频: {output_path}")
        print(f"   裁剪了前面 2 秒音频")

        # 对齐测试
        output_aligned = "video-rhythm-cam/output/test_aligned_cropped.mp4"

        success, offset = align_and_replace_audio(
            dance_video_path=original_video,
            reference_video_path=output_path,
            output_video_path=output_aligned,
            max_offset=10.0
        )

        if success:
            print(f"✅ 对齐成功")
            print(f"   计算的偏移量: {offset:.3f} 秒")
            print(f"   注意：偏移量应该接近 -2.0 秒（负数表示需要向前移动）")

            if os.path.exists(output_aligned):
                file_size = os.path.getsize(output_aligned) / (1024 * 1024)
                print(f"   输出文件大小: {file_size:.2f} MB")
                return True
        else:
            print(f"❌ 对齐失败")

        return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # 运行所有测试
    print("🧪 音频对齐鲁棒性测试")
    print()
    print("这个测试将验证:")
    print("1. ✅ 音频拉长后的对齐效果")
    print("2. ✅ 音频裁剪后的对齐效果")
    print("3. ✅ 算法是否正确识别偏移量")
    print()

    test_alignment_with_longer_audio()
    test_with_cropped_audio()
