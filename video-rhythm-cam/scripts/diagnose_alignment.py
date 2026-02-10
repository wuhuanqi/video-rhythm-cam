#!/usr/bin/env python3
"""
音频对齐诊断脚本
检查视频文件信息,诊断音频对齐失败的原因
"""

import os
import sys
import json
from pathlib import Path


def check_ffmpeg():
    """检查 ffmpeg 是否可用"""
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            return True
    except:
        pass
    return False


def get_video_info_ffprobe(video_path: str) -> dict:
    """使用 ffprobe 获取详细的视频信息"""
    try:
        import subprocess

        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {}

    except Exception as e:
        print(f"❌ ffprobe 执行失败: {e}")
        return {}


def check_video_file(video_path: str) -> dict:
    """检查视频文件的详细信息"""
    print(f"\n{'='*60}")
    print(f"📹 检查文件: {Path(video_path).name}")
    print(f"{'='*60}")

    info = {
        'path': video_path,
        'exists': False,
        'size': 0,
        'has_video': False,
        'has_audio': False,
        'duration': 0,
        'video_codec': None,
        'audio_codec': None,
        'sample_rate': None,
        'channels': None,
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

    # 使用 ffprobe 获取详细信息
    probe_data = get_video_info_ffprobe(video_path)

    if not probe_data:
        info['error'] = "无法读取视频信息"
        print(f"❌ {info['error']}")
        return info

    # 解析流信息
    streams = probe_data.get('streams', [])
    format_info = probe_data.get('format', {})

    info['duration'] = float(format_info.get('duration', 0))
    print(f"⏱️  时长: {info['duration']:.2f} 秒")

    for stream in streams:
        codec_type = stream.get('codec_type')

        if codec_type == 'video':
            info['has_video'] = True
            info['video_codec'] = stream.get('codec_name')
            print(f"🎥 视频编解码: {info['video_codec']}")
            print(f"   分辨率: {stream.get('width')}x{stream.get('height')}")
            print(f"   帧率: {eval(stream.get('r_frame_rate', '0/1')):.2f} fps")

        elif codec_type == 'audio':
            info['has_audio'] = True
            info['audio_codec'] = stream.get('codec_name')
            info['sample_rate'] = int(stream.get('sample_rate', 0))
            info['channels'] = int(stream.get('channels', 0))

            print(f"🎵 音频编解码: {info['audio_codec']}")
            print(f"   采样率: {info['sample_rate']} Hz")
            print(f"   声道数: {info['channels']}")
            print(f"   时长: {float(stream.get('duration', 0)):.2f} 秒")

    if not info['has_audio']:
        info['error'] = "视频中没有音频轨道"
        print(f"❌ {info['error']}")

    return info


def check_audio_alignment_compatibility(video1_info: dict, video2_info: dict) -> list:
    """检查两个视频是否适合音频对齐"""
    print(f"\n{'='*60}")
    print("🔍 兼容性检查")
    print(f"{'='*60}")

    issues = []

    # 检查两个视频是否都有音频
    if not video1_info.get('has_audio'):
        issues.append(f"❌ {Path(video1_info['path']).name} 没有音频轨道")

    if not video2_info.get('has_audio'):
        issues.append(f"❌ {Path(video2_info['path']).name} 没有音频轨道")

    # 检查时长差异
    if video1_info.get('duration', 0) > 0 and video2_info.get('duration', 0) > 0:
        duration_diff = abs(video1_info['duration'] - video2_info['duration'])
        duration_ratio = duration_diff / max(video1_info['duration'], video2_info['duration'])

        print(f"⏱️  时长差异: {duration_diff:.2f} 秒 ({duration_ratio*100:.1f}%)")

        if duration_diff > 10:
            issues.append(f"⚠️  两个视频时长差异过大 ({duration_diff:.2f} 秒)")

    # 检查采样率
    if video1_info.get('sample_rate') and video2_info.get('sample_rate'):
        if video1_info['sample_rate'] != video2_info['sample_rate']:
            print(f"⚠️  采样率不同: {video1_info['sample_rate']} Hz vs {video2_info['sample_rate']} Hz")

    # 检查声道数
    if video1_info.get('channels') and video2_info.get('channels'):
        if video1_info['channels'] != video2_info['channels']:
            print(f"⚠️  声道数不同: {video1_info['channels']} vs {video2_info['channels']}")

    return issues


def test_audio_extraction(video_path: str) -> bool:
    """测试音频提取"""
    print(f"\n{'='*60}")
    print(f"🧪 测试音频提取: {Path(video_path).name}")
    print(f"{'='*60}")

    try:
        from moviepy import VideoFileClip

        video = VideoFileClip(video_path)
        audio = video.audio

        if audio is None:
            print("❌ MoviePy 无法读取音频轨道")
            video.close()
            return False

        print(f"✅ MoviePy 成功读取音频")
        print(f"   时长: {audio.duration:.2f} 秒")

        # 尝试写入临时文件
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp_path = tmp.name

        try:
            audio.write_audiofile(tmp_path, logger=None)
            print(f"✅ 成功提取音频到临时文件")

            # 检查文件大小
            if os.path.exists(tmp_path):
                size = os.path.getsize(tmp_path)
                print(f"   音频文件大小: {size / (1024*1024):.2f} MB")
                os.remove(tmp_path)
                return True

        except Exception as e:
            print(f"❌ 写入音频文件失败: {e}")
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            return False
        finally:
            audio.close()
            video.close()

    except Exception as e:
        print(f"❌ 音频提取失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    if len(sys.argv) != 3:
        print("用法: python diagnose_alignment.py <视频1> <视频2>")
        print("\n示例:")
        print("  python diagnose_alignment.py /path/to/对齐音频.MP4 /path/to/原视频.MP4")
        sys.exit(1)

    video1_path = sys.argv[1]
    video2_path = sys.argv[2]

    print("🔧 音频对齐诊断工具")
    print("="*60)

    # 检查 ffmpeg
    if not check_ffmpeg():
        print("⚠️  警告: ffmpeg 未安装或不在 PATH 中")
        print("   某些功能可能无法使用")

    # 检查两个视频文件
    video1_info = check_video_file(video1_path)
    video2_info = check_video_file(video2_path)

    # 兼容性检查
    issues = check_audio_alignment_compatibility(video1_info, video2_info)

    if issues:
        print(f"\n{'='*60}")
        print("⚠️  发现的问题:")
        print(f"{'='*60}")
        for issue in issues:
            print(issue)

    # 测试音频提取
    if video1_info.get('has_audio'):
        test_audio_extraction(video1_path)

    if video2_info.get('has_audio'):
        test_audio_extraction(video2_path)

    # 总结
    print(f"\n{'='*60}")
    print("📋 诊断总结")
    print(f"{'='*60}")

    can_align = True
    reasons = []

    if not video1_info.get('has_audio'):
        can_align = False
        reasons.append(f"• {Path(video1_path).name} 没有音频轨道")

    if not video2_info.get('has_audio'):
        can_align = False
        reasons.append(f"• {Path(video2_path).name} 没有音频轨道")

    if issues:
        can_align = False
        reasons.extend(issues)

    if can_align:
        print("✅ 两个视频可以进行音频对齐")
        print("\n💡 建议:")
        print("   1. 确保两个视频的音乐是同一首歌")
        print("   2. 如果对齐效果不好,可以调整 --max-offset 参数")
        print("   3. 运行命令:")
        print(f"      python audio_alignment.py \"{video2_path}\" \"{video1_path}\" -o output.mp4")
    else:
        print("❌ 音频对齐可能会失败")
        print("\n原因:")
        for reason in reasons:
            print(reason)

    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
