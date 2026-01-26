#!/usr/bin/env python3
"""
命令行音频对齐功能测试套件
直接测试 audio_alignment.py 模块
"""

import sys
import os
import time
import subprocess
from pathlib import Path

# 添加路径
sys.path.insert(0, 'video-rhythm-cam/scripts')

from audio_alignment import (
    extract_audio_from_video,
    find_best_offset,
    apply_offset_to_audio,
    align_and_replace_audio
)


class TestResult:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.results = []

    def add(self, test_name, passed, message=""):
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
        print("测试总结")
        print("=" * 60)
        print(f"总计: {self.total} | 通过: {self.passed} | 失败: {self.failed}")
        print(f"成功率: {self.passed/self.total*100:.1f}%")
        print("=" * 60)


def run_cli_tests():
    """运行命令行测试"""
    results = TestResult()

    print("=" * 60)
    print("命令行音频对齐功能测试")
    print("=" * 60)
    print()

    # 测试文件路径
    test_data_dir = Path("test_data")
    dance_video = str(test_data_dir / "dance_video.mp4")
    reference_video = str(test_data_dir / "reference_video.mp4")
    output_dir = Path("video-rhythm-cam/output")
    output_dir.mkdir(exist_ok=True)

    # 检查测试文件
    if not os.path.exists(dance_video):
        print(f"❌ 测试文件不存在: {dance_video}")
        print("   请先运行: python3 create_simple_test.py")
        return results

    # 测试 1: 音频提取
    print("\n📋 测试组 1: 音频提取功能")
    print("-" * 60)

    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        audio1 = os.path.join(tmpdir, "audio1.wav")
        audio2 = os.path.join(tmpdir, "audio2.wav")

        # 从舞蹈视频提取音频
        print("1. 从舞蹈视频提取音频...")
        start = time.time()
        success = extract_audio_from_video(dance_video, audio1)
        elapsed = time.time() - start
        results.add("提取舞蹈视频音频", success and os.path.exists(audio1),
                    f"耗时: {elapsed:.2f}秒")

        # 从参考视频提取音频
        print("2. 从参考视频提取音频...")
        start = time.time()
        success = extract_audio_from_video(reference_video, audio2)
        elapsed = time.time() - start
        results.add("提取参考视频音频", success and os.path.exists(audio2),
                    f"耗时: {elapsed:.2f}秒")

        # 测试 2: 偏移计算
        print("\n📋 测试组 2: 偏移计算")
        print("-" * 60)

        if os.path.exists(audio1) and os.path.exists(audio2):
            # 计算偏移
            print("1. 计算最佳偏移量...")
            start = time.time()
            offset = find_best_offset(audio1, audio2, max_offset=5.0)
            elapsed = time.time() - start
            results.add("计算偏移量", True,
                        f"偏移: {offset:.3f}秒, 耗时: {elapsed:.2f}秒")

            # 测试不同的 maxOffset
            print("2. 测试不同 maxOffset 参数...")
            for max_off in [1.0, 3.0, 5.0, 10.0]:
                offset = find_best_offset(audio1, audio2, max_offset=max_off)
                results.add(f"maxOffset={max_off}", True, f"偏移: {offset:.3f}秒")

        # 测试 3: 音频偏移应用
        print("\n📋 测试组 3: 音频偏移应用")
        print("-" * 60)

        if os.path.exists(audio1):
            # 测试正偏移（添加静音）
            print("1. 测试正偏移（添加静音）...")
            output_pos = os.path.join(tmpdir, "offset_positive.wav")
            success = apply_offset_to_audio(audio1, 1.0, output_pos)
            results.add("正偏移应用", success and os.path.exists(output_pos),
                        "在音频前添加1秒静音")

            # 测试负偏移（裁剪）
            print("2. 测试负偏移（裁剪）...")
            output_neg = os.path.join(tmpdir, "offset_negative.wav")
            success = apply_offset_to_audio(audio1, -1.0, output_neg)
            results.add("负偏移应用", success and os.path.exists(output_neg),
                        "裁剪音频前1秒")

            # 测试零偏移
            print("3. 测试零偏移...")
            output_zero = os.path.join(tmpdir, "offset_zero.wav")
            success = apply_offset_to_audio(audio1, 0.0, output_zero)
            results.add("零偏移应用", success and os.path.exists(output_zero),
                        "不改变音频")

        # 测试 4: 完整流程
        print("\n📋 测试组 4: 完整对齐流程")
        print("-" * 60)

        print("1. 执行完整音频对齐...")
        output_video = str(output_dir / "test_cli_aligned.mp4")
        start = time.time()
        success, offset = align_and_replace_audio(
            dance_video,
            reference_video,
            output_video,
            max_offset=5.0
        )
        elapsed = time.time() - start
        results.add("完整对齐流程", success and os.path.exists(output_video),
                    f"偏移: {offset:.3f}秒, 耗时: {elapsed:.2f}秒")

        # 检查输出文件大小
        if os.path.exists(output_video):
            file_size = os.path.getsize(output_video) / (1024 * 1024)
            results.add("输出文件检查", file_size > 0,
                        f"文件大小: {file_size:.2f} MB")

    # 测试 5: 边界情况
    print("\n📋 测试组 5: 边界情况")
    print("-" * 60)

    # 相同视频
    print("1. 相同视频对齐...")
    output_same = str(output_dir / "test_same_video.mp4")
    success, offset = align_and_replace_audio(dance_video, dance_video, output_same)
    results.add("相同视频对齐", success and os.path.exists(output_same),
                f"偏移: {offset:.3f}秒")

    # 反向对齐
    print("2. 反向对齐...")
    output_reverse = str(output_dir / "test_reverse.mp4")
    success, offset = align_and_replace_audio(reference_video, dance_video, output_reverse)
    results.add("反向对齐", success and os.path.exists(output_reverse),
                f"偏移: {offset:.3f}秒")

    # 大偏移量
    print("3. 大偏移量测试...")
    output_large = str(output_dir / "test_large_offset.mp4")
    success, offset = align_and_replace_audio(
        dance_video, reference_video, output_large, max_offset=10.0
    )
    results.add("大偏移量处理", success and os.path.exists(output_large),
                f"maxOffset=10.0, 偏移: {offset:.3f}秒")

    # 测试 6: 错误处理
    print("\n📋 测试组 6: 错误处理")
    print("-" * 60)

    # 不存在的文件
    print("1. 不存在的输入文件...")
    output_error = str(output_dir / "test_error.mp4")
    success, offset = align_and_replace_audio(
        "/nonexistent/video1.mp4",
        "/nonexistent/video2.mp4",
        output_error
    )
    results.add("不存在文件处理", not success, "正确返回失败")

    # 打印总结
    results.print_summary()

    return results


def main():
    """主函数"""
    # 检查测试数据
    if not os.path.exists("test_data"):
        print("❌ 测试数据目录不存在！")
        print("   请先运行: python3 create_simple_test.py")
        sys.exit(1)

    # 运行测试
    results = run_cli_tests()

    # 退出码
    sys.exit(0 if results.failed == 0 else 1)


if __name__ == "__main__":
    main()
