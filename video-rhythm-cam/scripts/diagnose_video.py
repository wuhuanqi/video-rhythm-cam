#!/usr/bin/env python3
"""
视频导出问题诊断工具
分析导出视频卡顿的原因
"""

import os
import sys
import json
import subprocess


def analyze_video_info(video_path: str) -> dict:
    """使用 ffprobe 分析视频信息"""
    try:
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
            return None
    except Exception as e:
        print(f"❌ 分析视频失败: {e}")
        return None


def check_video_issues(video_path: str) -> list:
    """检查视频可能存在的问题"""
    issues = []

    if not os.path.exists(video_path):
        issues.append("视频文件不存在")
        return issues

    info = analyze_video_info(video_path)
    if not info:
        issues.append("无法读取视频信息")
        return issues

    # 检查视频流
    video_streams = [s for s in info.get('streams', []) if s.get('codec_type') == 'video']
    if not video_streams:
        issues.append("没有找到视频流")
        return issues

    video_stream = video_streams[0]

    # 检查帧率
    fps_str = video_stream.get('r_frame_rate', '0/0')
    try:
        num, den = map(int, fps_str.split('/'))
        fps = num / den if den != 0 else 0
        print(f"📊 视频帧率: {fps:.2f} fps")

        if fps < 24:
            issues.append(f"帧率过低 ({fps:.2f} fps)，建议至少 24 fps")
        elif fps > 60:
            issues.append(f"帧率过高 ({fps:.2f} fps)，可能导致编码问题")
    except:
        issues.append("无法解析帧率信息")

    # 检查分辨率
    width = int(video_stream.get('width', 0))
    height = int(video_stream.get('height', 0))
    print(f"📊 视频分辨率: {width}x{height}")

    if width > 3840 or height > 2160:
        issues.append(f"分辨率过高 ({width}x{height})，建议降低分辨率")

    # 检查编码格式
    codec = video_stream.get('codec_name', 'unknown')
    print(f"📊 视频编码: {codec}")

    # 检查比特率
    format_info = info.get('format', {})
    bitrate = int(format_info.get('bit_rate', 0))
    if bitrate > 0:
        bitrate_mbps = bitrate / 1000000
        print(f"📊 视频比特率: {bitrate_mbps:.2f} Mbps")

        if bitrate_mbps < 2:
            issues.append(f"比特率过低 ({bitrate_mbps:.2f} Mbps)，可能导致画质差")
        elif bitrate_mbps > 20:
            issues.append(f"比特率过高 ({bitrate_mbps:.2f} Mbps)，可能导致编码慢")

    # 检查是否为 VFR（可变帧率）
    avg_fps_str = video_stream.get('avg_frame_rate', '0/0')
    try:
        avg_num, avg_den = map(int, avg_fps_str.split('/'))
        avg_fps = avg_num / avg_den if avg_den != 0 else 0
        if abs(fps - avg_fps) > 1:
            issues.append(f"检测到可变帧率 (VFR)，可能导致导出卡顿")
    except:
        pass

    # 检查音频
    audio_streams = [s for s in info.get('streams', []) if s.get('codec_type') == 'audio']
    if audio_streams:
        audio_stream = audio_streams[0]
        audio_codec = audio_stream.get('codec_name', 'unknown')
        sample_rate = int(audio_stream.get('sample_rate', 0))
        print(f"📊 音频编码: {audio_codec}, 采样率: {sample_rate} Hz")

    return issues


def check_ffmpeg_installed():
    """检查 ffmpeg 是否安装"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True)
        if result.returncode == 0:
            version_line = result.stdout.decode().split('\n')[0]
            print(f"✅ {version_line}")
            return True
    except:
        pass

    print("❌ FFmpeg 未安装或不在 PATH 中")
    return False


def check_dependencies():
    """检查 Python 依赖"""
    print("🔍 检查 Python 依赖...")

    dependencies = {
        'moviepy': 'MoviePy (视频处理)',
        'librosa': 'librosa (音频分析)',
        'numpy': 'NumPy (数值计算)',
        'cv2': 'OpenCV (图像处理，可选)',
    }

    missing = []
    for module, description in dependencies.items():
        try:
            __import__(module)
            print(f"  ✅ {description}")
        except ImportError:
            print(f"  ❌ {description}")
            if module != 'cv2':  # cv2 是可选的
                missing.append(module)

    return missing


def recommend_solutions(issues: list) -> list:
    """根据问题推荐解决方案"""
    solutions = []

    for issue in issues:
        if "帧率过低" in issue:
            solutions.append("💡 提高输出帧率：在 write_videofile 中明确指定 fps=30 或 fps=60")
        elif "帧率过高" in issue:
            solutions.append("💡 降低输出帧率到 30 fps 以提高兼容性")
        elif "可变帧率" in issue:
            solutions.append("💡 使用 ffmpeg 先转换为固定帧率:")
            solutions.append("   ffmpeg -i input.mp4 -r 30 -vsync cfr output.mp4")
        elif "分辨率过高" in issue:
            solutions.append("💡 降低输出分辨率以提高性能")
        elif "比特率" in issue:
            solutions.append("💡 调整编码参数:")
            solutions.append("   - 低比特率: 增加 bitrate 参数")
            solutions.append("   - 高比特率: 降低 bitrate 或使用 CRF 模式")
        elif "OpenCV" in issue:
            solutions.append("💡 安装 OpenCV: pip install opencv-python")

    return solutions


def main():
    print("=" * 60)
    print("视频导出问题诊断工具")
    print("=" * 60)
    print()

    # 检查 FFmpeg
    print("1️⃣ 检查 FFmpeg")
    print("-" * 60)
    ffmpeg_ok = check_ffmpeg_installed()
    print()

    # 检查 Python 依赖
    print("2️⃣ 检查 Python 依赖")
    print("-" * 60)
    missing_deps = check_dependencies()
    print()

    if missing_deps:
        print(f"❌ 缺少依赖: {', '.join(missing_deps)}")
        print("   请运行: pip install " + " ".join(missing_deps))
        return

    # 分析视频
    print("3️⃣ 分析视频文件")
    print("-" * 60)

    if len(sys.argv) < 2:
        print("请提供视频文件路径:")
        print("  python3 diagnose_video.py <视频文件路径>")
        return

    video_path = sys.argv[1]

    print(f"📁 分析视频: {video_path}")
    print()

    issues = check_video_issues(video_path)

    print()
    print("4️⃣ 诊断结果")
    print("-" * 60)

    if not issues:
        print("✅ 未发现明显问题")
    else:
        print("❌ 发现以下问题:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")

    # 推荐解决方案
    if issues:
        print()
        print("5️⃣ 推荐解决方案")
        print("-" * 60)
        solutions = recommend_solutions(issues)
        for solution in solutions:
            print(solution)

    print()
    print("=" * 60)
    print("📋 优化建议")
    print("=" * 60)
    print("""
通用优化建议:

1. 使用固定帧率 (CFR)
   ffmpeg -i input.mp4 -r 30 -vsync cfr input_cfr.mp4

2. 优化编码参数
   - preset='medium' (平衡速度和质量)
   - crf=20 (高质量)
   - 明确指定 fps 参数

3. 避免逐帧处理
   使用 MoviePy 的 fl 滤镜而不是循环处理每一帧

4. 使用优化版本的脚本
   python3 scripts/rhythm_cam_optimized.py <视频文件>

5. 检查系统资源
   - CPU 使用率
   - 内存使用
   - 磁盘 I/O
    """)


if __name__ == "__main__":
    main()
