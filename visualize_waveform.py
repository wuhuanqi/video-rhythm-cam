#!/usr/bin/env python3
"""
生成波形图和频谱图可视化
就像剪辑软件显示的那样
"""

import os
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
from moviepy import VideoFileClip
import tempfile


def generate_waveform_comparison(video1_path, video2_path):
    """生成波形图对比"""

    print("="*70)
    print("📊 生成音频波形图和频谱图")
    print("="*70)

    with tempfile.TemporaryDirectory() as tmpdir:
        # 提取音频
        print(f"\n📤 提取音频...")

        audio1 = os.path.join(tmpdir, "audio1.wav")
        v1 = VideoFileClip(video1_path)
        v1.audio.write_audiofile(audio1, logger=None)
        dur1 = v1.duration
        v1.close()

        audio2 = os.path.join(tmpdir, "audio2.wav")
        v2 = VideoFileClip(video2_path)
        v2.audio.write_audiofile(audio2, logger=None)
        dur2 = v2.duration
        v2.close()

        print(f"   视频1（原视频）: {dur1:.2f}秒")
        print(f"   视频2（参考）: {dur2:.2f}秒")

        # 加载音频
        sr = 22050
        y1, _ = librosa.load(audio1, sr=sr)
        y2, _ = librosa.load(audio2, sr=sr)

        print(f"\n📊 生成可视化...")

        # 创建图形
        fig, axes = plt.subplots(4, 1, figsize=(16, 12))

        # 1. 原视频波形
        print(f"   绘制原视频波形...")
        times1 = librosa.times_like(y1, sr=sr)
        axes[0].plot(times1, y1, color='#FF6B6B', linewidth=0.5)
        axes[0].set_title(f'原视频波形 ({dur1:.2f}秒)', fontsize=14, fontweight='bold')
        axes[0].set_xlabel('时间 (秒)')
        axes[0].set_ylabel('振幅')
        axes[0].set_xlim(0, dur1)
        axes[0].grid(True, alpha=0.3)

        # 2. 参考视频波形
        print(f"   绘制参考视频波形...")
        times2 = librosa.times_like(y2, sr=sr)
        axes[1].plot(times2, y2, color='#4ECDC4', linewidth=0.5)
        axes[1].set_title(f'参考视频波形 ({dur2:.2f}秒)', fontsize=14, fontweight='bold')
        axes[1].set_xlabel('时间 (秒)')
        axes[1].set_ylabel('振幅')
        axes[1].set_xlim(0, dur2)
        axes[1].grid(True, alpha=0.3)

        # 3. 波形叠加对比（截取相同长度）
        print(f"   绘制波形叠加...")
        min_dur = min(dur1, dur2)
        min_samples = min(len(y1), len(y2))

        axes[2].plot(times1[:min_samples], y1[:min_samples], color='#FF6B6B',
                    alpha=0.6, linewidth=0.5, label='原视频')
        axes[2].plot(times2[:min_samples], y2[:min_samples], color='#4ECDC4',
                    alpha=0.6, linewidth=0.5, label='参考视频')
        axes[2].set_title(f'波形叠加对比 (前{min_dur:.2f}秒)', fontsize=14, fontweight='bold')
        axes[2].set_xlabel('时间 (秒)')
        axes[2].set_ylabel('振幅')
        axes[2].set_xlim(0, min_dur)
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)

        # 4. 频谱图对比
        print(f"   绘制频谱图...")
        # 计算短时傅里叶变换
        D1 = librosa.amplitude_to_db(np.abs(librosa.stft(y1)), ref=np.max)
        D2 = librosa.amplitude_to_db(np.abs(librosa.stft(y2)), ref=np.max)

        img1 = librosa.display.specshow(D1, sr=sr, x_axis='time', y_axis='hz',
                                         ax=axes[3], cmap='Reds', alpha=0.7)
        img2 = librosa.display.specshow(D2, sr=sr, x_axis='time', y_axis='hz',
                                         ax=axes[3], cmap='Blues', alpha=0.5)

        axes[3].set_title('频谱图对比 (红色=原视频, 蓝色=参考)', fontsize=14, fontweight='bold')
        axes[3].set_xlabel('时间 (秒)')
        axes[3].set_ylabel('频率 (Hz)')

        plt.tight_layout()

        # 保存
        output_path = "/Users/a123/Downloads/waveform_comparison.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"\n✅ 波形图已保存: {output_path}")

        # 分析波形匹配
        print(f"\n🔍 分析波形匹配...")

        # 计算互相关
        print(f"   计算互相关...")

        # 归一化
        y1_norm = (y1 - np.mean(y1)) / np.std(y1)
        y2_norm = (y2 - np.mean(y2)) / np.std(y2)

        # 用原视频前10秒作为模板
        template_samples = int(10 * sr)
        template = y1_norm[:template_samples]

        # 在参考视频中搜索
        correlation = np.correlate(y2_norm, template, mode='valid')
        correlation = correlation / (len(template) * np.std(template) * np.std(y2_norm[:len(template)]))

        # 找到最大相关位置
        max_idx = np.argmax(correlation)
        max_corr = correlation[max_idx]
        best_time = max_idx / sr

        print(f"\n✅ 波形匹配结果:")
        print(f"   最佳匹配位置: 参考视频 {best_time:.2f}秒")
        print(f"   相关系数: {max_corr:.4f}")

        # 在图上标记
        plt.figure(figsize=(16, 4))
        plt.plot(times2, y2, color='#4ECDC4', linewidth=0.5)
        plt.axvline(x=best_time, color='red', linestyle='--', linewidth=2,
                   label=f'最佳匹配位置 ({best_time:.2f}秒)')
        plt.title(f'参考视频波形 - 匹配位置标记', fontsize=14, fontweight='bold')
        plt.xlabel('时间 (秒)')
        plt.ylabel('振幅')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xlim(0, dur2)

        match_path = "/Users/a123/Downloads/waveform_match.png"
        plt.savefig(match_path, dpi=150, bbox_inches='tight')
        print(f"\n✅ 匹配位置图已保存: {match_path}")

        # 打开图片
        import subprocess
        subprocess.run(["open", output_path])
        subprocess.run(["open", match_path])

        print(f"\n💡 请查看波形图:")
        print(f"   可以直观看到音频的波形形状")
        print(f"   匹配的位置已用红线标记")


if __name__ == "__main__":
    generate_waveform_comparison(
        "/Users/a123/Downloads/原视频.MP4",
        "/Users/a123/Downloads/对齐音频.MP4"
    )
