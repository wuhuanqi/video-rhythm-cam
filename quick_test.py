#!/usr/bin/env python3
"""
快速测试脚本 - 验证基本功能
"""

import sys
import os

def test_dependencies():
    """测试 Python 依赖"""
    print("🔍 检查 Python 依赖...")
    try:
        import numpy as np
        print("  ✅ numpy")
        import librosa
        print("  ✅ librosa")
        import soundfile as sf
        print("  ✅ soundfile")
        from scipy import signal
        print("  ✅ scipy")
        from moviepy import VideoFileClip, AudioFileClip
        print("  ✅ moviepy")
        return True
    except ImportError as e:
        print(f"  ❌ 缺少依赖: {e}")
        return False


def test_scripts():
    """测试脚本文件"""
    print("\n🔍 检查脚本文件...")
    scripts = [
        "video-rhythm-cam/scripts/audio_alignment.py",
        "video-rhythm-cam/scripts/detect_beats.py",
        "video-rhythm-cam/python-api/api.py",
    ]

    all_exist = True
    for script in scripts:
        if os.path.exists(script):
            print(f"  ✅ {script}")
        else:
            print(f"  ❌ {script} (不存在)")
            all_exist = False
    return all_exist


def test_import():
    """测试导入模块"""
    print("\n🔍 测试导入模块...")
    try:
        sys.path.insert(0, 'video-rhythm-cam/scripts')
        from audio_alignment import (
            extract_audio_from_video,
            find_best_offset,
            apply_offset_to_audio,
            align_and_replace_audio
        )
        print("  ✅ audio_alignment 模块")
        return True
    except Exception as e:
        print(f"  ❌ 导入失败: {e}")
        return False


def test_api():
    """测试 API 服务"""
    print("\n🔍 测试 API 服务...")
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            print("  ✅ API 服务正常运行")
            return True
        else:
            print(f"  ❌ API 服务响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ API 服务未启动: {e}")
        return False


def test_web():
    """测试 Web 服务"""
    print("\n🔍 测试 Web 服务...")
    try:
        import requests
        response = requests.get("http://localhost:3000", timeout=2)
        if response.status_code == 200:
            print("  ✅ Web 服务正常运行")
            return True
        else:
            print(f"  ❌ Web 服务响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Web 服务未启动: {e}")
        return False


def test_data():
    """测试测试数据"""
    print("\n🔍 检查测试数据...")
    test_files = [
        "test_data/dance_video.mp4",
        "test_data/reference_video.mp4",
    ]

    all_exist = True
    for f in test_files:
        if os.path.exists(f):
            size = os.path.getsize(f) / (1024 * 1024)
            print(f"  ✅ {f} ({size:.2f} MB)")
        else:
            print(f"  ❌ {f} (不存在)")
            all_exist = False
    return all_exist


def main():
    """主函数"""
    print("=" * 60)
    print("快速功能测试")
    print("=" * 60)

    results = []

    # 运行测试
    results.append(("Python 依赖", test_dependencies()))
    results.append(("脚本文件", test_scripts()))
    results.append(("模块导入", test_import()))
    results.append(("API 服务", test_api()))
    results.append(("Web 服务", test_web()))
    results.append(("测试数据", test_data()))

    # 总结
    print("\n" + "=" * 60)
    print("测试结果")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")

    print(f"\n通过: {passed}/{total}")
    print(f"成功率: {passed/total*100:.1f}%")

    # 建议
    if passed < total:
        print("\n💡 建议:")
        if not results[0][1]:  # 依赖
            print("   安装依赖: pip install librosa soundfile scipy moviepy")
        if not results[4][1]:  # API
            print("   启动 API: cd video-rhythm-cam/python-api && python3 api.py")
        if not results[5][1]:  # Web
            print("   启动 Web: cd video-rhythm-cam/web && npm run dev")
        if not results[5][1]:  # 数据
            print("   创建数据: python3 create_simple_test.py")

    print("=" * 60)

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
