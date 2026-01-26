#!/usr/bin/env python3
"""
音频对齐功能 - 完整测试套件
包含各种场景的自动化测试用例
"""

import sys
import os
import json
import requests
import time
from pathlib import Path

# 添加路径
sys.path.insert(0, 'video-rhythm-cam/scripts')

# API 配置
API_BASE = "http://localhost:8000"
TEST_DATA_DIR = "test_data"
OUTPUT_DIR = "video-rhythm-cam/output"


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
            status = "✅ PASS"
        else:
            self.failed += 1
            status = "❌ FAIL"
        self.results.append({
            "name": test_name,
            "status": status,
            "message": message
        })
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")

    def print_summary(self):
        print("\n" + "=" * 60)
        print("测试总结")
        print("=" * 60)
        print(f"总计: {self.total}")
        print(f"通过: {self.passed} ✅")
        print(f"失败: {self.failed} ❌")
        print(f"成功率: {self.passed/self.total*100:.1f}%")
        print("=" * 60)

        if self.failed > 0:
            print("\n失败的测试:")
            for r in self.results:
                if "FAIL" in r["status"]:
                    print(f"  - {r['name']}: {r['message']}")


def check_api_health():
    """检查 API 服务是否运行"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def upload_video(file_path):
    """上传视频文件"""
    if not os.path.exists(file_path):
        return None, f"文件不存在: {file_path}"

    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'video/mp4')}
            response = requests.post(f"{API_BASE}/api/upload", files=files, timeout=30)

        if response.status_code == 200:
            result = response.json()
            return result['path'], None
        else:
            return None, f"上传失败: {response.status_code}"
    except Exception as e:
        return None, f"上传异常: {e}"


def align_audio(dance_video_path, reference_video_path, max_offset=5.0):
    """调用音频对齐接口"""
    try:
        payload = {
            "danceVideoPath": dance_video_path,
            "referenceVideoPath": reference_video_path,
            "maxOffset": max_offset
        }

        response = requests.post(
            f"{API_BASE}/api/align-audio",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            if result['success']:
                return True, result['outputPath'], result['offset'], None
            else:
                return False, None, 0, result.get('error', '未知错误')
        else:
            return False, None, 0, f"HTTP {response.status_code}"
    except Exception as e:
        return False, None, 0, f"请求异常: {e}"


def run_tests():
    """运行所有测试用例"""
    results = TestResult()

    print("=" * 60)
    print("音频对齐功能 - 完整测试套件")
    print("=" * 60)
    print()

    # 检查 API 服务
    print("🔍 检查 API 服务...")
    if not check_api_health():
        print("❌ API 服务未运行！")
        print("   请先启动服务: cd video-rhythm-cam/python-api && python3 api.py")
        return
    print("✅ API 服务正常运行\n")

    # 测试用例 1: 基本功能测试
    print("\n📋 测试用例 1: 基本音频对齐")
    print("-" * 60)

    dance_path = os.path.join(TEST_DATA_DIR, "dance_video.mp4")
    reference_path = os.path.join(TEST_DATA_DIR, "reference_video.mp4")

    # 上传舞蹈视频
    print("1. 上传舞蹈视频...")
    dance_uploaded, error = upload_video(dance_path)
    results.add("上传舞蹈视频", dance_uploaded is not None, error or "成功上传")

    if not dance_uploaded:
        results.print_summary()
        return

    # 上传参考视频
    print("2. 上传参考视频...")
    reference_uploaded, error = upload_video(reference_path)
    results.add("上传参考视频", reference_uploaded is not None, error or "成功上传")

    if not reference_uploaded:
        results.print_summary()
        return

    # 执行音频对齐
    print("3. 执行音频对齐...")
    success, output_path, offset, error = align_audio(dance_uploaded, reference_uploaded)
    results.add("音频对齐处理", success, error or f"偏移量: {offset:.3f}秒")

    # 检查输出文件
    if success:
        file_exists = os.path.exists(output_path)
        file_size = os.path.getsize(output_path) / (1024 * 1024) if file_exists else 0
        results.add("输出文件生成", file_exists,
                    f"文件大小: {file_size:.2f} MB" if file_exists else "文件不存在")

    # 测试用例 2: 相同视频测试
    print("\n📋 测试用例 2: 相同视频对齐（边界情况）")
    print("-" * 60)

    print("1. 使用相同视频作为舞蹈视频和参考视频...")
    success, output_path, offset, error = align_audio(dance_uploaded, dance_uploaded)
    results.add("相同视频对齐", success, error or f"偏移量: {offset:.3f}秒")

    # 测试用例 3: 反向视频测试
    print("\n📋 测试用例 3: 反向对齐（交换视频）")
    print("-" * 60)

    print("1. 交换舞蹈视频和参考视频...")
    success, output_path, offset, error = align_audio(reference_uploaded, dance_uploaded)
    results.add("反向对齐", success, error or f"偏移量: {offset:.3f}秒")

    # 测试用例 4: 不同 maxOffset 参数测试
    print("\n📋 测试用例 4: 不同 maxOffset 参数")
    print("-" * 60)

    for max_offset in [1.0, 3.0, 5.0, 10.0]:
        print(f"{max_offset}. 测试 maxOffset={max_offset}...")
        success, output_path, offset, error = align_audio(
            dance_uploaded, reference_uploaded, max_offset
        )
        results.add(f"maxOffset={max_offset}", success,
                    error or f"偏移量: {offset:.3f}秒")

    # 测试用例 5: 错误处理测试
    print("\n📋 测试用例 5: 错误处理")
    print("-" * 60)

    # 不存在的文件
    print("1. 测试不存在的文件...")
    success, output_path, offset, error = align_audio(
        "/nonexistent/video1.mp4",
        "/nonexistent/video2.mp4"
    )
    results.add("不存在文件处理", not success, error or "应该失败但成功了")

    # 测试用例 6: API 端点测试
    print("\n📋 测试用例 6: API 端点")
    print("-" * 60)

    # 列出视频
    print("1. 列出已上传的视频...")
    try:
        response = requests.get(f"{API_BASE}/api/videos")
        results.add("API: 列出视频", response.status_code == 200,
                    f"返回 {len(response.json().get('videos', []))} 个视频" if response.status_code == 200 else f"HTTP {response.status_code}")
    except Exception as e:
        results.add("API: 列出视频", False, str(e))

    # 检测节拍
    print("2. 检测视频节拍...")
    try:
        payload = {
            "videoPath": dance_uploaded,
            "sensitivity": 0.5
        }
        response = requests.post(f"{API_BASE}/api/detect-beats", json=payload)
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('data'):
                bpm = result['data']['bpm']
                beat_count = len(result['data']['beats'])
                results.add("API: 检测节拍", True, f"BPM: {bpm:.1f}, 节拍数: {beat_count}")
            else:
                results.add("API: 检测节拍", False, result.get('error', '未知错误'))
        else:
            results.add("API: 检测节拍", False, f"HTTP {response.status_code}")
    except Exception as e:
        results.add("API: 检测节拍", False, str(e))

    # 测试用例 7: 性能测试
    print("\n📋 测试用例 7: 性能测试")
    print("-" * 60)

    print("1. 测试处理时间...")
    start_time = time.time()
    success, output_path, offset, error = align_audio(dance_uploaded, reference_uploaded)
    elapsed = time.time() - start_time
    results.add("处理性能", success,
                error or f"处理时间: {elapsed:.1f}秒")

    # 打印测试总结
    results.print_summary()

    # 保存测试报告
    report_path = "test_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total": results.total,
            "passed": results.passed,
            "failed": results.failed,
            "success_rate": f"{results.passed/results.total*100:.1f}%",
            "tests": results.results
        }, f, indent=2, ensure_ascii=False)
    print(f"\n📄 测试报告已保存: {report_path}")

    return results


def main():
    """主函数"""
    # 检查测试数据
    if not os.path.exists(TEST_DATA_DIR):
        print("❌ 测试数据目录不存在！")
        print("   请先运行: python3 create_simple_test.py")
        return

    # 运行测试
    results = run_tests()

    # 返回退出码
    sys.exit(0 if results.failed == 0 else 1)


if __name__ == "__main__":
    main()
