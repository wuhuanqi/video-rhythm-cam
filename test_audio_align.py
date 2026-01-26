#!/usr/bin/env python3
"""
简单测试音频对齐功能
"""

import sys
sys.path.insert(0, 'video-rhythm-cam/scripts')

from audio_alignment import find_best_offset, apply_offset_to_audio
import os

print("=" * 60)
print("测试音频对齐功能")
print("=" * 60)

# 测试1: 两个相同的音频
print("\n测试1: 两个相同的音频")
offset = find_best_offset('test_audio1.wav', 'test_audio2.wav', max_offset=2.0)
print(f"计算出的偏移量: {offset:.3f} 秒")

# 测试2: 应用偏移
print("\n测试2: 应用偏移")
if apply_offset_to_audio('test_audio1.wav', 0.5, 'test_audio_offset.wav'):
    print("✅ 成功应用偏移")

# 清理
print("\n清理测试文件...")
for f in ['test_audio1.wav', 'test_audio2.wav', 'test_audio_offset.wav']:
    if os.path.exists(f):
        os.remove(f)
        print(f"删除 {f}")

print("\n✅ 测试完成！")
