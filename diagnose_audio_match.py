#!/usr/bin/env python3
"""
音频匹配诊断工具
分析为什么两个音频无法正确匹配
"""

import os
import tempfile
import numpy as np
import librosa
import soundfile as sf
from matplotlib import pyplot as plt


def diagnose_audio_mismatch(video1_path: str, video2_path: str):
    """诊断为什么两个音频无法匹配"""

    print("="*70)
    print("🔍 音频匹配诊断工具")
    print("="*70)

    # 提取音频
    with tempfile.TemporaryDirectory() as tmpdir:
        from moviepy import VideoFileClip

        print("\n📤 步骤1: 提取音频")
        print("-"*70)

        # 提取第一个视频音频
        v1 = VideoFileClip(video1_path)
        audio1_path = os.path.join(tmpdir, "audio1.wav")
        if v1.audio:
            v1.audio.write_audiofile(audio1_path, logger=None)
            print(f"✅ 视频1音频已提取")
        else:
            print("❌ 视频1没有音频")
            return
        v1.close()

        # 提取第二个视频音频
        v2 = VideoFileClip(video2_path)
        audio2_path = os.path.join(tmpdir, "audio2.wav")
        if v2.audio:
            v2.audio.write_audiofile(audio2_path, logger=None)
            print(f"✅ 视频2音频已提取")
        else:
            print("❌ 视频2没有音频")
            return
        v2.close()

        print("\n🎵 步骤2: 分析音频特征")
        print("-"*70)

        # 加载音频
        sr = 22050
        y1, _ = librosa.load(audio1_path, sr=sr)
        y2, _ = librosa.load(audio2_path, sr=sr)

        duration1 = len(y1) / sr
        duration2 = len(y2) / sr

        print(f"\n📊 基本信息:")
        print(f"   音频1时长: {duration1:.2f}秒")
        print(f"   音频2时长: {duration2:.2f}秒")

        # 检测节拍和节奏
        print(f"\n🥁 节奏分析:")
        tempo1, beats1 = librosa.beat.beat_track(y=y1, sr=sr)
        tempo2, beats2 = librosa.beat.beat_track(y=y2, sr=sr)

        # tempo可能是数组，取第一个值
        t1 = float(tempo1) if np.isscalar(tempo1) else float(tempo1[0])
        t2 = float(tempo2) if np.isscalar(tempo2) else float(tempo2[0])

        print(f"   音频1 BPM: {t1:.2f}")
        print(f"   音频2 BPM: {t2:.2f}")
        print(f"   BPM差异: {abs(t1 - t2):.2f}")

        # 分析音色/频谱
        print(f"\n🎼 音色分析:")

        # 计算频谱质心（亮度）
        spectral_centroid1 = librosa.feature.spectral_centroid(y=y1, sr=sr)[0]
        spectral_centroid2 = librosa.feature.spectral_centroid(y=y2, sr=sr)[0]

        print(f"   音频1频谱质心: {np.mean(spectral_centroid1):.2f} Hz")
        print(f"   音频2频谱质心: {np.mean(spectral_centroid2):.2f} Hz")
        print(f"   频谱质心差异: {abs(np.mean(spectral_centroid1) - np.mean(spectral_centroid2)):.2f} Hz")

        # 计算零交叉率（反映音色）
        zcr1 = librosa.feature.zero_crossing_rate(y1)[0]
        zcr2 = librosa.feature.zero_crossing_rate(y2)[0]

        print(f"   音频1零交叉率: {np.mean(zcr1):.4f}")
        print(f"   音频2零交叉率: {np.mean(zcr2):.4f}")

        # 分析能量/响度
        print(f"\n🔊 能量分析:")
        rms1 = librosa.feature.rms(y=y1)[0]
        rms2 = librosa.feature.rms(y=y2)[0]

        print(f"   音频1平均能量: {np.mean(rms1):.6f}")
        print(f"   音频2平均能量: {np.mean(rms2):.6f}")

        # MFCC特征对比
        print(f"\n🎵 MFCC特征对比（前10秒）:")
        n_mfcc = 13
        hop_length = 512

        compare_samples = min(10 * sr, len(y1), len(y2))

        mfcc1 = librosa.feature.mfcc(y=y1[:compare_samples], sr=sr, n_mfcc=n_mfcc, hop_length=hop_length)
        mfcc2 = librosa.feature.mfcc(y=y2[:compare_samples], sr=sr, n_mfcc=n_mfcc, hop_length=hop_length)

        print(f"\n   MFCC相关性分析（逐帧对比）:")
        for i in range(n_mfcc):
            corr = np.corrcoef(mfcc1[i], mfcc2[i])[0, 1]
            if not np.isnan(corr):
                status = "✅" if abs(corr) > 0.5 else "⚠️" if abs(corr) > 0.2 else "❌"
                print(f"   MFCC[{i:2d}]: {corr:+.4f} {status}")

        avg_corr = np.mean([
            np.corrcoef(mfcc1[i], mfcc2[i])[0, 1]
            for i in range(n_mfcc)
            if not np.isnan(np.corrcoef(mfcc1[i], mfcc2[i])[0, 1])
        ])
        print(f"\n   平均MFCC相关性: {avg_corr:+.4f}")

        # 交叉相关分析
        print(f"\n📈 交叉相关分析:")

        # 下采样加速
        ds_factor = 8
        y1_ds = y1[:compare_samples:ds_factor]
        y2_ds = y2[:compare_samples:ds_factor]

        # 计算互相关
        correlation = np.correlate(y2_ds, y1_ds, mode='valid')
        correlation = correlation / (np.std(y1_ds) * np.std(y2_ds) * len(y1_ds))

        max_corr_idx = np.argmax(correlation)
        max_corr_value = correlation[max_corr_idx]
        max_offset_sample = max_corr_idx * ds_factor
        max_offset_second = max_offset_sample / sr

        print(f"   最大交叉相关值: {max_corr_value:.4f}")
        print(f"   对应偏移量: {max_offset_second:+.3f}秒")

        # 相关性分布
        print(f"   相关性分布:")
        print(f"     >0.8: {np.sum(correlation > 0.8)} 个位置")
        print(f"     >0.5: {np.sum(correlation > 0.5)} 个位置")
        print(f"     >0.3: {np.sum(correlation > 0.3)} 个位置")
        print(f"     >0.1: {np.sum(correlation > 0.1)} 个位置")

        # 诊断结论
        print(f"\n" + "="*70)
        print(f"📋 诊断结论")
        print(f"="*70)

        issues = []
        recommendations = []

        # 检查BPM差异
        t1 = float(tempo1) if np.isscalar(tempo1) else float(tempo1[0])
        t2 = float(tempo2) if np.isscalar(tempo2) else float(tempo2[0])

        if abs(t1 - t2) > 10:
            issues.append(f"⚠️  BPM差异很大 ({abs(t1 - t2):.1f})")
            recommendations.append("   → 可能是不同速度的版本（加速/减速版）")
        else:
            print(f"✅ BPM基本一致")

        # 检查音色差异
        if abs(np.mean(spectral_centroid1) - np.mean(spectral_centroid2)) > 1000:
            issues.append(f"⚠️  音色差异很大（频谱质心差异 {abs(np.mean(spectral_centroid1) - np.mean(spectral_centroid2)):.0f} Hz）")
            recommendations.append("   → 可能是不同录音或音源")

        # 检查相关性
        if avg_corr < 0.3:
            issues.append(f"❌ MFCC相关性很低 ({avg_corr:.2%})")
            recommendations.append("   → 两个音频可能不是同一首歌")
            recommendations.append("   → 或者是完全不同的编曲/混音版本")

        if max_corr_value < 0.3:
            issues.append(f"❌ 交叉相关值很低 ({max_corr_value:.2%})")
            recommendations.append("   → 波形特征差异很大")

        # 能量差异
        if abs(np.mean(rms1) - np.mean(rms2)) / max(np.mean(rms1), np.mean(rms2)) > 0.5:
            issues.append(f"⚠️  能量差异很大")
            recommendations.append("   → 可能一个音量很大，一个很小")

        if issues:
            print(f"\n发现的问题:")
            for issue in issues:
                print(f"  {issue}")

            print(f"\n💡 可能的原因和建议:")
            for rec in recommendations:
                print(f"  {rec}")
        else:
            print(f"\n✅ 音频特征基本匹配，可能需要调整算法参数")

        print(f"\n" + "="*70)

        # 尝试手动分段对比
        print(f"\n🔬 分段对比分析（每5秒一段）:")
        print("-"*70)

        segment_duration = 5  # 5秒
        num_segments1 = int(duration1 // segment_duration)
        num_segments2 = int(duration2 // segment_duration)

        best_match = None
        best_score = -float('inf')

        for seg1 in range(min(num_segments1, 5)):  # 只看前5段
            start1 = seg1 * segment_duration
            end1 = start1 + segment_duration
            y1_seg = y1[int(start1*sr):int(end1*sr)]

            for seg2 in range(min(num_segments2, 10)):  # 看前10段
                start2 = seg2 * segment_duration
                end2 = start2 + segment_duration
                y2_seg = y2[int(start2*sr):int(end2*sr)]

                # 计算相关性
                if len(y1_seg) > 0 and len(y2_seg) > 0:
                    mfcc1_seg = librosa.feature.mfcc(y=y1_seg, sr=sr, n_mfcc=13)
                    mfcc2_seg = librosa.feature.mfcc(y=y2_seg, sr=sr, n_mfcc=13)

                    min_frames = min(mfcc1_seg.shape[1], mfcc2_seg.shape[1])
                    if min_frames > 0:
                        corrs = [
                            np.corrcoef(mfcc1_seg[i, :min_frames], mfcc2_seg[i, :min_frames])[0, 1]
                            for i in range(13)
                            if not np.isnan(np.corrcoef(mfcc1_seg[i, :min_frames], mfcc2_seg[i, :min_frames])[0, 1])
                        ]
                        if corrs:
                            score = np.mean(corrs)
                            if score > best_score:
                                best_score = score
                                best_match = (seg1, seg2, start1, start2, score)

                            if score > 0.5:  # 显示高相关性
                                print(f"   音频1 [{start1:.0f}s-{end1:.0f}s] vs 音频2 [{start2:.0f}s-{end2:.0f}s]: {score:+.4f} {'✅' if score > 0.7 else '⚠️'}")

        if best_match:
            seg1, seg2, start1, start2, score = best_match
            print(f"\n🏆 最佳匹配:")
            print(f"   音频1 [{start1:.0f}s-{start1+segment_duration:.0f}s]")
            print(f"   音频2 [{start2:.0f}s-{start2+segment_duration:.0f}s]")
            print(f"   相关性: {score:+.4f} ({score:.1%})")

            if score < 0.3:
                print(f"\n   ❌ 即使是最佳匹配，相关性也很低")
                print(f"   → 建议：确认两个音频是否为同一首歌")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("用法: python diagnose_audio_match.py <视频1> <视频2>")
        sys.exit(1)

    diagnose_audio_mismatch(sys.argv[1], sys.argv[2])
