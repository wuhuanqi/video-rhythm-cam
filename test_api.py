#!/usr/bin/env python3
"""
测试音频对齐 API 接口
"""

import requests
import json
import os

print("=" * 60)
print("测试音频对齐 API")
print("=" * 60)

API_BASE = "http://localhost:8000"

# 1. 健康检查
print("\n1️⃣ 健康检查...")
try:
    response = requests.get(f"{API_BASE}/health")
    print(f"✅ API 服务状态: {response.json()}")
except Exception as e:
    print(f"❌ API 服务未响应: {e}")
    exit(1)

# 2. 上传舞蹈视频
print("\n2️⃣ 上传舞蹈视频...")
try:
    with open('test_data/dance_video.mp4', 'rb') as f:
        files = {'file': ('dance_video.mp4', f, 'video/mp4')}
        response = requests.post(f"{API_BASE}/api/upload", files=files)

    if response.status_code == 200:
        result = response.json()
        print(f"✅ 上传成功: {result['filename']}")
        print(f"   时长: {result['duration']:.1f}秒")
        print(f"   路径: {result['path']}")
        dance_video_path = result['path']
    else:
        print(f"❌ 上传失败: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"❌ 上传异常: {e}")
    exit(1)

# 3. 上传参考视频
print("\n3️⃣ 上传参考视频...")
try:
    with open('test_data/reference_video.mp4', 'rb') as f:
        files = {'file': ('reference_video.mp4', f, 'video/mp4')}
        response = requests.post(f"{API_BASE}/api/upload", files=files)

    if response.status_code == 200:
        result = response.json()
        print(f"✅ 上传成功: {result['filename']}")
        print(f"   时长: {result['duration']:.1f}秒")
        print(f"   路径: {result['path']}")
        reference_video_path = result['path']
    else:
        print(f"❌ 上传失败: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"❌ 上传异常: {e}")
    exit(1)

# 4. 调用音频对齐接口
print("\n4️⃣ 调用音频对齐接口...")
print(f"   舞蹈视频: {dance_video_path}")
print(f"   参考视频: {reference_video_path}")

try:
    payload = {
        "danceVideoPath": dance_video_path,
        "referenceVideoPath": reference_video_path,
        "maxOffset": 5.0
    }

    response = requests.post(
        f"{API_BASE}/api/align-audio",
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print(f"✅ 音频对齐成功!")
            print(f"   输出路径: {result['outputPath']}")
            print(f"   音频偏移: {result['offset']:.3f} 秒")

            # 检查输出文件是否存在
            if os.path.exists(result['outputPath']):
                file_size = os.path.getsize(result['outputPath']) / (1024 * 1024)
                print(f"   文件大小: {file_size:.2f} MB")
            else:
                print(f"   ⚠️  警告: 输出文件不存在")
        else:
            print(f"❌ 音频对齐失败: {result.get('error', '未知错误')}")
    else:
        print(f"❌ API 请求失败: {response.status_code}")
        print(f"   响应: {response.text}")
except Exception as e:
    print(f"❌ 请求异常: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("✅ API 测试完成！")
print("=" * 60)
print("\n💡 提示: 现在可以打开浏览器访问 http://localhost:3000")
print("   点击'开始使用'进入工作台，然后切换到'音频对齐'选项卡")
print("   上传 test_data/ 目录下的两个测试视频进行测试")
