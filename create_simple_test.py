#!/usr/bin/env python3
"""
创建简单的测试视频数据
"""

import numpy as np
import soundfile as sf
from moviepy import VideoClip, AudioFileClip
import os

print("🎬 创建测试视频数据...")

# 创建临时目录
os.makedirs('test_data', exist_ok=True)

# 1. 创建测试音频（带节奏的音乐）
sr = 22050
duration = 10.0  # 10秒
t = np.linspace(0, duration, int(sr * duration))

# 创建一个有节奏的音频（每秒一个节拍）
audio = np.zeros_like(t)
bpm = 60  # 每分钟60拍
beat_interval = 60 / bpm  # 每拍的时间间隔

for i in range(int(duration / beat_interval)):
    beat_time = i * beat_interval
    beat_idx = int(beat_time * sr)
    # 在每个节拍处添加一个短促的音调
    if beat_idx < len(t):
        beat_duration = 0.1  # 节拍持续0.1秒
        beat_end_idx = min(beat_idx + int(beat_duration * sr), len(t))
        # 添加440Hz的正弦波
        audio[beat_idx:beat_end_idx] += np.sin(2 * np.pi * 440 * t[beat_idx:beat_end_idx]) * 0.5

# 归一化
audio = audio / np.max(np.abs(audio)) * 0.8

# 保存音频
sf.write('test_data/audio_with_beats.wav', audio, sr)
print(f"✅ 创建音频: test_data/audio_with_beats.wav ({duration}秒, {bpm} BPM)")

# 2. 创建测试视频1（舞蹈视频）
print("\n📹 创建测试视频1（舞蹈视频）...")

def make_frame1(t):
    # 根据时间计算颜色（模拟舞蹈动作）
    beat_idx = int(t / beat_interval)
    colors = [
        [255, 100, 100],  # 红色
        [100, 255, 100],  # 绿色
        [100, 100, 255],  # 蓝色
        [255, 255, 100],  # 黄色
        [255, 100, 255],  # 紫色
    ]
    color = colors[beat_idx % len(colors)]
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frame[:, :] = color
    return frame

video1 = VideoClip(make_frame1, duration=duration)
video1.fps = 30

# 添加音频
audio_clip = AudioFileClip('test_data/audio_with_beats.wav')
video1 = video1.with_audio(audio_clip)

# 保存视频
video1.write_videofile('test_data/dance_video.mp4', codec='libx264', audio_codec='aac', logger=None)
print(f"✅ 创建视频1: test_data/dance_video.mp4")

video1.close()
audio_clip.close()

# 3. 创建测试视频2（参考视频 - 带音频偏移）
print("\n📹 创建测试视频2（参考视频 - 音频延迟2秒）...")

def make_frame2(t):
    # 不同的视觉效果（渐变圆圈）
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    center_x, center_y = 320, 240
    radius = int(50 + 30 * np.sin(2 * np.pi * t))
    y, x = np.ogrid[:480, :640]
    mask = (x - center_x)**2 + (y - center_y)**2 <= radius**2
    frame[mask] = [100, 200, 255]  # 蓝色圆圈
    return frame

video2 = VideoClip(make_frame2, duration=duration)
video2.fps = 30

# 创建一个带2秒延迟的音频（前面加2秒静音）
silence_samples = int(2.0 * sr)
audio_with_delay = np.concatenate([np.zeros(silence_samples), audio])

# 保存延迟后的音频
sf.write('test_data/audio_delayed.wav', audio_with_delay[:int(sr * duration)], sr)

# 添加延迟的音频
audio_clip2 = AudioFileClip('test_data/audio_delayed.wav')
video2 = video2.with_audio(audio_clip2)

# 保存视频
video2.write_videofile('test_data/reference_video.mp4', codec='libx264', audio_codec='aac', logger=None)
print(f"✅ 创建视频2: test_data/reference_video.mp4 (音频延迟2秒)")

video2.close()
audio_clip2.close()

print("\n✅ 测试数据创建完成！")
print("📁 文件位置:")
print("   - 舞蹈视频: test_data/dance_video.mp4 (音频无延迟)")
print("   - 参考视频: test_data/reference_video.mp4 (音频延迟2秒)")
print("   - 音频文件: test_data/audio_with_beats.wav")
print("\n💡 这两个视频的音频相差2秒，可以用来测试音频对齐功能")
