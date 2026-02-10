#!/usr/bin/env python3
"""
简化版音频对齐诊断脚本
使用 MoviePy 检查视频文件
"""

import os
import sys
from pathlib import Path


def check_video_with_moviepy(video_path: str) -> dict:
    """使用 MoviePy 检查视频文件"""
    print(f"\n{'='*60}")
    print(f"📹 检查文件: {Path(video_path).name}")
    print(f"{'='*60}")

    info = {
        'path': video_path,
        'exists': False,
        'has_video': False,
        'has_audio': False,
        'duration': 0,
        'fps': 0,
        'size': 0,
        'audio_duration': 0,
        'error': None
    }

    # 检查文件是否存在
    if not os.path.exists(video_path):
        info['error'] = "文件不存在"
        print(f"❌ {info['error']}")
        return info

    info['exists'] = True
    info['size'] = os.path.getsize(video_path)
    print(f"✅ 文件存在")
    print(f"📊 文件大小: {info['size'] / (1024*1024):.2f} MB")

    try:
        from moviepy import VideoFileClip

        print("🔧 正在用 MoviePy 读取视频...")
        video = VideoFileClip(video_path)

        info['has_video'] = True
        info['duration'] = video.duration
        info['fps'] = video.fps if video.fps else 0

        print(f"⏱️  视频时长: {info['duration']:.2f} 秒")
        print(f"🎬 视频帧率: {info['fps']:.2f} fps")

        # 检查音频
        audio = video.audio
        if audio is not None:
            info['has_audio'] = True
            info['audio_duration'] = audio.duration
            print(f"🎵 音频轨道: ✅")
            print(f"   音频时长: {info['audio_duration']:.2f} 秒")
        else:
            info['error'] = "没有音频轨道"
            print(f"❌ 没有音频轨道")

        video.close()
        print(f"✅ MoviePy 读取成功")

    except Exception as e:
        info['error'] = str(e)
        print(f"❌ MoviePy 读取失败: {e}")
        import traceback
        traceback.print_exc()

    return info


def test_audio_librosa(video_path: str) -> bool:
    """测试用 librosa 提取音频"""
    print(f"\n🧪 测试 librosa 音频处理...")

    try:
        import tempfile
        from moviepy import VideoFileClip

        # 先用 moviepy 提取音频
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            video = VideoFileClip(video_path)
            audio = video.audio

            if audio is None:
                print("❌ 视频没有音频轨道")
                video.close()
                return False

            audio.write_audiofile(tmp_path, logger=None)
            audio.close()
            video.close()

            print(f"✅ 音频已提取: {tmp_path}")

            # 尝试用 librosa 加载
            import librosa
            print("🔧 正在用 librosa 加载音频...")

            y, sr = librosa.load(tmp_path, sr=22050)
            duration = len(y) / sr

            print(f"✅ librosa 加载成功")
            print(f"   采样率: {sr} Hz")
            print(f"   时长: {duration:.2f} 秒")
            print(f"   样本数: {len(y):,}")

            # 测试节拍检测
            print("\n🎵 测试节拍检测...")
            hop_length = 512
            onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)

            print(f"✅ 节拍强度计算成功")
            print(f"   节拍强度帧数: {len(onset_env):,}")

            return True

        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    except Exception as e:
        print(f"❌ librosa 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    if len(sys.argv) != 3:
        print("用法: python diagnose_simple.py <视频1> <视频2>")
        print("\n示例:")
        print("  python diagnose_simple.py /path/to/对齐音频.MP4 /path/to/原视频.MP4")
        sys.exit(1)

    video1_path = sys.argv[1]
    video2_path = sys.argv[2]

    print("🔧 音频对齐诊断工具 (简化版)")
    print("="*60)

    # 检查两个视频文件
    video1_info = check_video_with_moviepy(video1_path)
    video2_info = check_video_with_moviepy(video2_path)

    # 兼容性检查
    print(f"\n{'='*60}")
    print("🔍 兼容性分析")
    print(f"{'='*60}")

    can_align = True
    issues = []

    if not video1_info.get('has_audio'):
        can_align = False
        issues.append(f"• {Path(video1_path).name} 没有音频轨道")

    if not video2_info.get('has_audio'):
        can_align = False
        issues.append(f"• {Path(video2_path).name} 没有音频轨道")

    if video1_info.get('duration', 0) > 0 and video2_info.get('duration', 0) > 0:
        duration_diff = abs(video1_info['duration'] - video2_info['duration'])
        print(f"⏱️  时长差异: {duration_diff:.2f} 秒")

        if duration_diff > 10:
            issues.append(f"• 时长差异过大 ({duration_diff:.2f} 秒)")

    # 测试音频处理
    if video1_info.get('has_audio'):
        print(f"\n{'='*60}")
        print(f"🧪 深度测试: {Path(video1_path).name}")
        print(f"{'='*60}")
        test_audio_librosa(video1_path)

    if video2_info.get('has_audio'):
        print(f"\n{'='*60}")
        print(f"🧪 深度测试: {Path(video2_path).name}")
        print(f"{'='*60}")
        test_audio_librosa(video2_path)

    # 总结
    print(f"\n{'='*60}")
    print("📋 诊断总结")
    print(f"{'='*60}")

    if can_align:
        print("✅ 两个视频可以进行音频对齐")
        print("\n💡 对齐命令:")
        print(f"   python audio_alignment.py \"{video2_path}\" \"{video1_path}\" -o output.mp4")
    else:
        print("❌ 音频对齐可能会失败")
        print("\n原因:")
        for issue in issues:
            print(issue)

    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
