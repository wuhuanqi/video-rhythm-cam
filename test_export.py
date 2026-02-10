#!/usr/bin/env python3
"""
测试导出功能（快速验证）
"""

import sys
import os
sys.path.insert(0, 'video-rhythm-cam/scripts')

def test_export():
    """测试导出功能"""
    print("=" * 60)
    print("测试导出功能")
    print("=" * 60)

    # 检查测试视频
    test_video = "test_data/dance_video.mp4"
    if not os.path.exists(test_video):
        print("❌ 测试视频不存在，请先运行: python3 create_simple_test.py")
        return False

    print(f"✅ 测试视频: {test_video}")

    # 导入模块
    try:
        from rhythm_remotion import process_video_with_remotion
        print("✅ 导入 rhythm_remotion 模块")
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

    # 导出测试
    output_path = "video-rhythm-cam/output/test_export.mp4"
    remotion_dir = "video-rhythm-cam/remotion"

    print(f"\n🎬 开始测试导出...")
    print(f"   输入: {test_video}")
    print(f"   输出: {output_path}")
    print(f"   Remotion 目录: {remotion_dir}")

    success = process_video_with_remotion(
        video_path=test_video,
        output_path=output_path,
        remotion_dir=remotion_dir,
        sensitivity=0.5,
        zoom_min=1.0,
        zoom_max=1.3,
        zoom_duration=0.2,
        quality=90,
        keep_temp=False
    )

    if success:
        print(f"\n✅ 导出成功!")
        print(f"📁 输出文件: {output_path}")

        # 检查文件
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path) / (1024 * 1024)
            print(f"📊 文件大小: {file_size:.2f} MB")
            return True
        else:
            print("❌ 输出文件不存在")
            return False
    else:
        print("\n❌ 导出失败")
        return False

if __name__ == "__main__":
    success = test_export()
    sys.exit(0 if success else 1)
