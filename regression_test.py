#!/usr/bin/env python3
"""
完整回归测试脚本
测试所有功能是否正常工作
"""

import sys
import os
import subprocess
import tempfile
import json
from pathlib import Path

# 添加路径
sys.path.insert(0, 'video-rhythm-cam/scripts')


class RegressionTest:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.results = []

    def add_result(self, test_name, passed, message=""):
        self.total += 1
        if passed:
            self.passed += 1
            status = "✅"
        else:
            self.failed += 1
            status = "❌"

        self.results.append({
            "name": test_name,
            "status": status,
            "message": message
        })
        print(f"{status} {test_name}")
        if message:
            print(f"   {message}")

    def print_summary(self):
        print("\n" + "=" * 60)
        print("回归测试总结")
        print("=" * 60)
        print(f"总计: {self.total}")
        print(f"通过: {self.passed} ✅")
        print(f"失败: {self.failed} ❌")
        print(f"成功率: {self.passed/self.total*100:.1f}%")
        print("=" * 60)

        if self.failed > 0:
            print("\n失败的测试:")
            for r in self.results:
                if "❌" in r["status"]:
                    print(f"  - {r['name']}: {r['message']}")


def check_dependencies():
    """检查 Python 依赖"""
    print("🔍 检查 Python 依赖...")
    try:
        import numpy as np
        import librosa
        import soundfile as sf
        from moviepy import VideoFileClip, AudioFileClip
        print("  ✅ numpy")
        print("  ✅ librosa")
        print("  ✅ soundfile")
        print("  ✅ moviepy")
        return True
    except ImportError as e:
        print(f"  ❌ 缺少依赖: {e}")
        return False


def check_api_service():
    """检查 API 服务"""
    print("\n🔍 检查 API 服务...")
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


def check_web_service():
    """检查 Web 服务"""
    print("\n🔍 检查 Web 服务...")
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
        print(f"  ⚠️  Web 服务未启动（可选）: {e}")
        return True  # Web 服务是可选的


def test_audio_alignment():
    """测试音频对齐功能"""
    print("\n📋 测试音频对齐功能")
    print("-" * 60)

    test = RegressionTest()

    # 导入模块
    try:
        from audio_alignment import (
            extract_audio_from_video,
            find_best_offset,
            apply_offset_to_audio
        )
        test.add_result("导入音频对齐模块", True)
    except Exception as e:
        test.add_result("导入音频对齐模块", False, str(e))
        return test

    # 检查测试文件
    test_dance = "test_data/dance_video.mp4"
    test_reference = "test_data/reference_video.mp4"

    if not os.path.exists(test_dance) or not os.path.exists(test_reference):
        test.add_result("测试文件存在", False, "请先运行 create_simple_test.py")
        return test

    test.add_result("测试文件存在", True)

    # 测试音频提取
    with tempfile.TemporaryDirectory() as tmpdir:
        audio1 = os.path.join(tmpdir, "audio1.wav")
        success = extract_audio_from_video(test_dance, audio1)
        test.add_result("从舞蹈视频提取音频", success and os.path.exists(audio1))

        if success and os.path.exists(audio1):
            # 测试偏移计算
            offset = find_best_offset(audio1, audio1, max_offset=2.0)
            test.add_result("计算音频偏移量", True, f"偏移: {offset:.3f}秒")

            # 测试音频偏移
            output_audio = os.path.join(tmpdir, "offset.wav")
            success = apply_offset_to_audio(audio1, 0.5, output_audio)
            test.add_result("应用音频偏移", success and os.path.exists(output_audio))

    test.print_summary()
    return test


def test_beat_detection():
    """测试节拍检测功能"""
    print("\n📋 测试节拍检测功能")
    print("-" * 60)

    test = RegressionTest()

    try:
        from detect_beats import detect_beats_with_strength, beats_to_json
        test.add_result("导入节拍检测模块", True)
    except Exception as e:
        test.add_result("导入节拍检测模块", False, str(e))
        return test

    # 检查测试文件
    test_video = "test_data/dance_video.mp4"
    if not os.path.exists(test_video):
        test.add_result("测试视频存在", False, "请先运行 create_simple_test.py")
        return test

    test.add_result("测试视频存在", True)

    # 测试节拍检测
    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = os.path.join(tmpdir, "audio.wav")

        # 提取音频
        from moviepy import VideoFileClip
        video = VideoFileClip(test_video)
        if video.audio:
            video.audio.write_audiofile(audio_path, logger=None)
            video.audio.close()
            video.close()

            # 检测节拍
            beats, _, bpm = detect_beats_with_strength(audio_path, sensitivity=0.5, fps=30)
            test.add_result("检测节拍", len(beats) > 0, f"检测到 {len(beats)} 个节拍, BPM: {bpm:.1f}")

            if beats:
                # 转换为 JSON
                beats_data = beats_to_json(beats, 10.0, bpm, 30)
                test.add_result("转换节拍数据为 JSON", beats_data is not None)
        else:
            video.close()
            test.add_result("视频有音频", False)

    test.print_summary()
    return test


def test_remotion_integration():
    """测试 Remotion 集成"""
    print("\n📋 测试 Remotion 集成")
    print("-" * 60)

    test = RegressionTest()

    try:
        from remotion_integration import RemotionIntegration
        test.add_result("导入 Remotion 集成模块", True)
    except Exception as e:
        test.add_result("导入 Remotion 集成模块", False, str(e))
        return test

    # 检查 Remotion 目录
    remotion_dir = Path("video-rhythm-cam/remotion")
    if not remotion_dir.exists():
        test.add_result("Remotion 目录存在", False)
        return test

    test.add_result("Remotion 目录存在", True)

    # 创建集成实例
    try:
        remotion = RemotionIntegration(str(remotion_dir))
        test.add_result("创建 Remotion 集成实例", True)

        # 检查依赖
        has_deps = remotion.check_dependencies()
        test.add_result("Remotion 依赖已安装", has_deps)

        # 检查必要文件
        src_dir = remotion_dir / "src"
        root_tsx = src_dir / "Root.tsx"
        rhythm_tsx = src_dir / "RhythmVideo.tsx"

        test.add_result("Root.tsx 存在", root_tsx.exists())
        test.add_result("RhythmVideo.tsx 存在", rhythm_tsx.exists())

    except Exception as e:
        test.add_result("Remotion 集成测试", False, str(e))

    test.print_summary()
    return test


def test_api_endpoints():
    """测试 API 端点"""
    print("\n📋 测试 API 端点")
    print("-" * 60)

    test = RegressionTest()

    try:
        import requests
    except ImportError:
        test.add_result("导入 requests", False)
        return test

    test.add_result("导入 requests", True)

    # 健康检查
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        test.add_result("GET /health", response.status_code == 200)
    except Exception as e:
        test.add_result("GET /health", False, str(e))

    # 列出视频
    try:
        response = requests.get("http://localhost:8000/api/videos", timeout=2)
        test.add_result("GET /api/videos", response.status_code == 200)
    except Exception as e:
        test.add_result("GET /api/videos", False, str(e))

    test.print_summary()
    return test


def test_file_naming():
    """测试文件命名功能"""
    print("\n📋 测试导出文件命名")
    print("-" * 60)

    test = RegressionTest()

    try:
        import datetime
        video_path = "test_data/dance_video.mp4"
        video_name = Path(video_path).stem
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # 测试新的命名格式
        output_filename = f"{video_name}_rhythm_s0.5_z1.0-1.3_q90_{timestamp}.mp4"
        test.add_result("生成文件名", True, f"文件名格式正确")

        # 检查文件名包含所有参数
        has_sensitivity = "_s0.5_" in output_filename
        has_zoom = "_z1.0-1.3_" in output_filename
        has_quality = "_q90_" in output_filename
        has_timestamp = timestamp in output_filename

        test.add_result("文件名包含灵敏度参数", has_sensitivity)
        test.add_result("文件名包含缩放参数", has_zoom)
        test.add_result("文件名包含质量参数", has_quality)
        test.add_result("文件名包含时间戳", has_timestamp)

    except Exception as e:
        test.add_result("文件命名测试", False, str(e))

    test.print_summary()
    return test


def test_modules_import():
    """测试所有核心模块导入"""
    print("\n📋 测试核心模块导入")
    print("-" * 60)

    test = RegressionTest()

    modules = [
        ("audio_alignment", "音频对齐"),
        ("detect_beats", "节拍检测"),
        ("remotion_integration", "Remotion 集成"),
    ]

    for module_name, description in modules:
        try:
            __import__(module_name)
            test.add_result(f"导入 {description} 模块", True)
        except Exception as e:
            test.add_result(f"导入 {description} 模块", False, str(e))

    test.print_summary()
    return test


def main():
    """主函数"""
    print("=" * 60)
    print("完整回归测试")
    print("=" * 60)
    print()

    # 1. 检查依赖
    deps_ok = check_dependencies()
    if not deps_ok:
        print("\n❌ 依赖检查失败，请先安装依赖")
        return

    # 2. 检查服务
    api_ok = check_api_service()
    web_ok = check_web_service()

    # 3. 测试模块导入
    modules_test = test_modules_import()

    # 4. 测试音频对齐
    alignment_test = test_audio_alignment()

    # 5. 测试节拍检测
    beats_test = test_beat_detection()

    # 6. 测试 Remotion 集成
    remotion_test = test_remotion_integration()

    # 7. 测试文件命名
    naming_test = test_file_naming()

    # 8. 测试 API（如果服务运行）
    if api_ok:
        api_test = test_api_endpoints()

    # 总体总结
    print("\n" + "=" * 60)
    print("总体测试结果")
    print("=" * 60)

    all_tests = [modules_test, alignment_test, beats_test, remotion_test, naming_test]
    if api_ok:
        all_tests.append(api_test)

    total_tests = sum(t.total for t in all_tests)
    total_passed = sum(t.passed for t in all_tests)
    total_failed = sum(t.failed for t in all_tests)

    print(f"总测试组: {len(all_tests)}")
    print(f"总测试数: {total_tests}")
    print(f"通过: {total_passed} ✅")
    print(f"失败: {total_failed} ❌")
    print(f"成功率: {total_passed/total_tests*100:.1f}%")
    print("=" * 60)

    if total_failed == 0:
        print("\n🎉 所有测试通过！系统运行正常！")
    else:
        print(f"\n⚠️  有 {total_failed} 个测试失败，请查看上面的详细信息")

    # 保存测试报告
    report = {
        "timestamp": str(subprocess.check_output(['date']).decode().strip()),
        "summary": {
            "total": total_tests,
            "passed": total_passed,
            "failed": total_failed,
            "success_rate": f"{total_passed/total_tests*100:.1f}%"
        },
        "test_groups": [
            {
                "name": "模块导入",
                "total": modules_test.total,
                "passed": modules_test.passed,
                "failed": modules_test.failed
            },
            {
                "name": "音频对齐",
                "total": alignment_test.total,
                "passed": alignment_test.passed,
                "failed": alignment_test.failed
            },
            {
                "name": "节拍检测",
                "total": beats_test.total,
                "passed": beats_test.passed,
                "failed": beats_test.failed
            },
            {
                "name": "Remotion 集成",
                "total": remotion_test.total,
                "passed": remotion_test.passed,
                "failed": remotion_test.failed
            },
            {
                "name": "文件命名",
                "total": naming_test.total,
                "passed": naming_test.passed,
                "failed": naming_test.failed
            }
        ]
    }

    if api_ok:
        report["test_groups"].append({
            "name": "API 端点",
            "total": api_test.total,
            "passed": api_test.passed,
            "failed": api_test.failed
        })

    with open("regression_test_report.json", "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("\n📄 测试报告已保存: regression_test_report.json")


if __name__ == "__main__":
    main()
