#!/usr/bin/env python3
"""
视频节奏运镜脚本 - Remotion 版
为舞蹈视频自动添加跟随音乐节奏的缩放运镜效果
使用 Remotion 进行高质量视频渲染
"""

import os
import sys
import argparse
import tempfile
from pathlib import Path
from typing import List, Optional

# 导入本地模块
from detect_beats import detect_beats_with_strength, beats_to_json
from remotion_integration import RemotionIntegration


def check_dependencies():
    """检查必要的依赖"""
    try:
        from moviepy import VideoFileClip
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖库: {e}")
        print("\n请安装以下依赖:")
        print("  pip install moviepy librosa soundfile numpy")
        return False


def extract_audio(video_path: str, audio_path: str) -> bool:
    """从视频中提取音频"""
    from moviepy import VideoFileClip

    try:
        print("📤 正在提取音频...")
        video = VideoFileClip(video_path)
        audio = video.audio

        if audio is None:
            print("❌ 视频中没有音频轨道")
            return False

        audio.write_audiofile(audio_path)
        audio.close()
        video.close()

        print(f"✅ 音频已提取")
        return True
    except Exception as e:
        print(f"❌ 提取音频失败: {e}")
        return False


def get_video_fps(video_path: str) -> float:
    """获取视频帧率"""
    from moviepy import VideoFileClip

    try:
        video = VideoFileClip(video_path)
        fps = video.fps
        video.close()
        return fps
    except Exception as e:
        print(f"⚠️  无法获取视频帧率，使用默认值 30: {e}")
        return 30.0


def get_video_duration(video_path: str) -> float:
    """获取视频时长"""
    from moviepy import VideoFileClip

    try:
        video = VideoFileClip(video_path)
        duration = video.duration
        video.close()
        return duration
    except Exception as e:
        print(f"⚠️  无法获取视频时长: {e}")
        return 0.0


def process_video_with_remotion(
    video_path: str,
    output_path: str,
    remotion_dir: str,
    sensitivity: float = 0.5,
    zoom_min: float = 1.0,
    zoom_max: float = 1.3,
    zoom_duration: float = 0.2,
    quality: int = 90,
    keep_temp: bool = False,
    progress_callback = None
) -> bool:
    """
    使用 Remotion 处理视频

    Args:
        video_path: 输入视频路径
        output_path: 输出视频路径（如果为 None，自动生成带参数的文件名）
        remotion_dir: Remotion 项目目录
        sensitivity: 节拍检测灵敏度 (0.0-1.0)
        zoom_min: 最小缩放比例
        zoom_max: 最大缩放比例
        zoom_duration: 缩放持续时间(秒)
        quality: 渲染质量 (1-100)
        keep_temp: 是否保留临时文件
        progress_callback: 进度回调函数(progress: int)

    Returns:
        是否成功
    """
    # 验证输入
    if not os.path.exists(video_path):
        print(f"❌ 视频文件不存在: {video_path}")
        return False

    # 获取视频信息
    fps = get_video_fps(video_path)
    duration = get_video_duration(video_path)

    if duration == 0:
        print("❌ 无法获取视频时长")
        return False

    print(f"📹 视频信息: {duration:.2f}秒, {fps:.2f}fps")

    # 如果没有指定输出路径，生成带参数的文件名
    if output_path is None:
        import datetime
        video_name = Path(video_path).stem
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{video_name}_rhythm_s{sensitivity}_z{zoom_min}-{zoom_max}_q{quality}_{timestamp}.mp4"
        output_path = str(Path(video_path).parent / output_filename)
        print(f"📁 自动生成输出路径: {output_path}")

    # 创建临时目录
    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = os.path.join(tmpdir, "audio.wav")

        # 步骤1: 提取音频
        if not extract_audio(video_path, audio_path):
            return False

        # 步骤2: 检测节拍
        beats_with_strength, _, bpm = detect_beats_with_strength(
            audio_path,
            sensitivity=sensitivity,
            fps=int(fps)
        )

        if not beats_with_strength:
            print("❌ 未检测到节拍")
            return False

        # 转换为 JSON 格式
        beats_data = beats_to_json(beats_with_strength, duration, bpm, int(fps))

        # 步骤3: 设置 Remotion 项目
        remotion = RemotionIntegration(remotion_dir)

        # 检查依赖
        if not remotion.check_dependencies():
            print("📦 Remotion 依赖未安装，正在安装...")
            if not remotion.install_dependencies():
                print("❌ 安装依赖失败")
                return False

        # 设置项目环境
        if not remotion.setup_remotion_project(video_path, beats_data, video_name="input.mp4"):
            return False

        # 步骤4: 渲染视频（带进度）
        try:
            print(f"🎬 开始渲染视频到: {output_path}")

            # 打印渲染参数
            print(f"📊 渲染参数:")
            print(f"   - 灵敏度: {sensitivity}")
            print(f"   - 缩放范围: {zoom_min}x - {zoom_max}x")
            print(f"   - 缩放时长: {zoom_duration}秒")
            print(f"   - 质量: {quality}")

            success = remotion.render_video(
                output_path=output_path,
                composition="RhythmVideo",
                codec="h264",
                pixel_format="yuv420p",
                quality=quality,
                concurrency=1,
                progress_callback=progress_callback
            )

            if success:
                print(f"✅ 视频处理完成!")
                print(f"📁 输出文件: {output_path}")
            else:
                print("❌ 视频渲染失败")

            return success

        except Exception as e:
            print(f"❌ 处理失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # 清理临时文件（如果不需要保留）
            if not keep_temp:
                remotion.cleanup()


def batch_process_videos(
    input_dir: str,
    output_dir: str,
    remotion_dir: str,
    sensitivity: float = 0.5,
    quality: int = 90,
    keep_temp: bool = False
) -> bool:
    """
    批量处理视频

    Args:
        input_dir: 输入目录
        output_dir: 输出目录
        remotion_dir: Remotion 项目目录
        sensitivity: 节拍检测灵敏度
        quality: 渲染质量
        keep_temp: 是否保留临时文件

    Returns:
        是否全部成功
    """
    # 支持的视频格式
    video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}

    # 查找所有视频文件
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"❌ 输入目录不存在: {input_dir}")
        return False

    video_files = [
        f for f in input_path.iterdir()
        if f.is_file() and f.suffix.lower() in video_extensions
    ]

    if not video_files:
        print(f"❌ 在 {input_dir} 中未找到视频文件")
        return False

    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"📁 找到 {len(video_files)} 个视频文件")
    print(f"📁 输出目录: {output_dir}")

    # 处理每个视频
    success_count = 0
    failed_videos = []

    for video_file in video_files:
        print(f"\n{'='*60}")
        print(f"处理: {video_file.name}")
        print(f"{'='*60}")

        output_file = output_path / f"{video_file.stem}_rhythm{video_file.suffix}"

        success = process_video_with_remotion(
            str(video_file),
            str(output_file),
            remotion_dir,
            sensitivity=sensitivity,
            quality=quality,
            keep_temp=keep_temp
        )

        if success:
            success_count += 1
        else:
            failed_videos.append(video_file.name)

    # 打印汇总
    print(f"\n{'='*60}")
    print(f"批量处理完成!")
    print(f"成功: {success_count}/{len(video_files)}")
    if failed_videos:
        print(f"失败: {len(failed_videos)}")
        for video in failed_videos:
            print(f"  - {video}")
    print(f"{'='*60}")

    return success_count == len(video_files)


def main():
    parser = argparse.ArgumentParser(
        description='为舞蹈视频添加跟随音乐节奏的缩放运镜效果 (Remotion 版)'
    )
    parser.add_argument('video', nargs='?', help='输入视频文件路径')
    parser.add_argument('-o', '--output', help='输出视频路径')
    parser.add_argument('-s', '--sensitivity', type=float, default=0.5,
                       help='节拍检测灵敏度 (0.0-1.0, 默认: 0.5)')
    parser.add_argument('--zoom-min', type=float, default=1.0,
                       help='最小缩放比例 (默认: 1.0)')
    parser.add_argument('--zoom-max', type=float, default=1.3,
                       help='最大缩放比例 (默认: 1.3)')
    parser.add_argument('--zoom-duration', type=float, default=0.2,
                       help='缩放持续时间(秒) (默认: 0.2)')
    parser.add_argument('--quality', type=int, default=90,
                       help='渲染质量 (1-100, 默认: 90)')
    parser.add_argument('--remotion-dir', default='./remotion',
                       help='Remotion 项目目录 (默认: ./remotion)')
    parser.add_argument('--batch', metavar='DIR',
                       help='批量处理模式：处理指定目录下的所有视频')
    parser.add_argument('--output-dir', metavar='DIR',
                       help='批量处理的输出目录 (默认: 与输入目录相同)')
    parser.add_argument('--keep-temp', action='store_true',
                       help='保留临时文件（用于调试）')

    args = parser.parse_args()

    # 检查依赖
    if not check_dependencies():
        sys.exit(1)

    # 批量处理模式
    if args.batch:
        output_dir = args.output_dir or args.batch
        success = batch_process_videos(
            args.batch,
            output_dir,
            args.remotion_dir,
            sensitivity=args.sensitivity,
            quality=args.quality,
            keep_temp=args.keep_temp
        )
        sys.exit(0 if success else 1)

    # 单视频处理模式
    if not args.video:
        parser.print_help()
        print("\n❌ 请指定视频文件或使用 --batch 批量处理")
        sys.exit(1)

    # 设置输出路径
    if args.output:
        output_path = args.output
    else:
        base, _ = os.path.splitext(args.video)
        output_path = f"{base}_rhythm.mp4"

    # 处理视频
    success = process_video_with_remotion(
        args.video,
        output_path,
        args.remotion_dir,
        sensitivity=args.sensitivity,
        zoom_min=args.zoom_min,
        zoom_max=args.zoom_max,
        zoom_duration=args.zoom_duration,
        quality=args.quality,
        keep_temp=args.keep_temp
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
