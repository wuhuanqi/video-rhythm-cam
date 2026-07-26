#!/usr/bin/env python3
"""
音频对齐模块 V5 - 速度自适应版
支持不同BPM的音频匹配（速度拉伸后匹配，再拉伸回原速替换）
"""
import os, tempfile
import numpy as np
import librosa
import soundfile as sf
from typing import Tuple
from tqdm import tqdm


def extract_audio_from_video(video_path: str, output_audio: str) -> bool:
    try:
        from moviepy import VideoFileClip
        print(f"📤 正在从视频提取音频: {os.path.basename(video_path)}")
        video = VideoFileClip(video_path)
        audio = video.audio
        if audio is None:
            print("❌ 视频中没有音频轨道"); video.close(); return False
        with tqdm(total=100, desc=f"  提取音频", unit="%", ncols=80,
                  bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as pbar:
            for i in range(10): pbar.update(10); import time; time.sleep(0.05)
            audio.write_audiofile(output_audio, logger=None)
            pbar.update(100 - pbar.n)
        audio.close(); video.close()
        print(f"✅ 音频已提取: {os.path.basename(output_audio)}")
        return True
    except Exception as e:
        print(f"❌ 提取音频失败: {e}"); return False


def detect_bpm(y, sr) -> float:
    """检测音频BPM — 用onset自相关，更稳定"""
    try:
        hop_length = 512
        onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
        # 自相关检测周期性
        auto = np.correlate(onset_env - np.mean(onset_env), onset_env - np.mean(onset_env), mode='full')
        auto = auto[len(auto)//2:]
        
        frame_rate = sr / hop_length
        min_frames = int(60 * frame_rate / 200)  # 200 BPM上限
        max_frames = int(60 * frame_rate / 40)   # 40 BPM下限
        
        if max_frames >= len(auto):
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            return float(tempo)
        
        peak = min_frames + np.argmax(auto[min_frames:max_frames])
        bpm = 60.0 / (peak / frame_rate)
        return float(bpm)
    except:
        return 120.0


def find_best_match_simple(
    reference_audio_path: str,
    original_audio_path: str,
    max_offset: float = 30.0
) -> Tuple[float, float, float, float, np.ndarray]:
    """
    Chroma + BPM自适应匹配
    
    返回: (offset, chroma_score, bpm_orig, stretch_rate, stretched_ref_audio)
    - offset: 在拉伸后音频中的匹配位置(秒)
    - stretch_rate: 速度拉伸率 (ref_bpm / orig_bpm)
    - stretched_ref_audio: 拉伸后的参考音频（用于替换）
    """
    print("🔍 正在分析音频 (BPM自适应 + Chroma匹配)...")
    
    print("  [1/5] 加载音频...")
    y_ref, sr = librosa.load(reference_audio_path, sr=22050)
    y_orig, _ = librosa.load(original_audio_path, sr=22050)
    ref_dur = len(y_ref) / sr
    orig_dur = len(y_orig) / sr
    print(f"   参考: {ref_dur:.2f}s  原视频: {orig_dur:.2f}s")
    
    # BPM检测
    print("  [2/5] 检测BPM...")
    bpm_ref = detect_bpm(y_ref, sr)
    bpm_orig = detect_bpm(y_orig, sr)
    print(f"   参考BPM: {bpm_ref:.1f}  原视频BPM: {bpm_orig:.1f}")
    
    # 速度拉伸：使参考音频的BPM匹配原视频
    stretch_rate = bpm_ref / bpm_orig
    need_stretch = abs(stretch_rate - 1.0) > 0.05  # 差异>5%就拉伸
    
    # 特殊判断：BPM差2倍但时长差不多 → 拍子层级不同，不拉伸
    if need_stretch:
        dur_ratio = orig_dur / ref_dur
        bpm_ratio = stretch_rate
        # BPM比接近2的幂次(2, 0.5, 4, 0.25...)但时长比接近1 → 同速不同拍
        if abs(dur_ratio - 1.0) < 0.3:
            for power in [2, 4, 0.5, 0.25]:
                if abs(bpm_ratio - power) < 0.1:
                    need_stretch = False
                    stretch_rate = 1.0
                    print(f"  [3/5] BPM差{bpm_ratio:.0f}倍但时长相近，视为同速（拍子层级差异）")
                    print(f"       检测BPM: 参考{bpm_ref:.0f} vs 原版{bpm_orig:.0f}，实际同速")
                    break
    
    if need_stretch:
        print(f"  [3/5] 速度拉伸: 参考 {bpm_ref:.0f}BPM → {bpm_orig:.0f}BPM (比率{stretch_rate:.3f})")
        y_ref_stretched = librosa.effects.time_stretch(y=y_ref, rate=stretch_rate)
        stretched_dur = len(y_ref_stretched) / sr
        print(f"   拉伸前: {ref_dur:.2f}s  拉伸后: {stretched_dur:.2f}s")
    else:
        print(f"  [3/5] BPM接近 ({bpm_ref:.0f} vs {bpm_orig:.0f}), 无需拉伸")
        y_ref_stretched = y_ref.copy()
        stretch_rate = 1.0
    
    # Chroma匹配（在拉伸后的音频上进行）
    hop_length = 512
    time_res = hop_length / sr
    
    print(f"  [4/5] 计算Chroma特征...")
    
    if len(y_ref_stretched) > len(y_orig):
        # 参考更长 → 在拉伸后的参考中搜索原视频
        print(f"   在拉伸后的参考音频中搜索原视频...")
        chroma_t = librosa.feature.chroma_cqt(y=y_orig, sr=sr, hop_length=hop_length)
        chroma_s = librosa.feature.chroma_cqt(y=y_ref_stretched, sr=sr, hop_length=hop_length)
        
        max_search = min(max_offset / stretch_rate if need_stretch else max_offset,
                        len(y_ref_stretched)/sr - orig_dur - 0.5)
        if max_search <= 0:
            max_search = len(y_ref_stretched)/sr - orig_dur - 0.1
        max_frames = int(max_search / time_res)
        max_frames = min(max_frames, chroma_s.shape[1] - chroma_t.shape[1])
        if max_frames <= 0:
            max_frames = chroma_s.shape[1] - chroma_t.shape[1]
        
        tf = chroma_t.shape[1]
        step = max(1, max_frames // 50)
        
        print(f"   搜索范围: {max_frames*time_res:.1f}s  步长: {step}帧")
        best_frame, best_score = 0, -1.0
        
        with tqdm(total=max_frames//step+1, desc="  搜索", unit="步", ncols=80) as pbar:
            for off in range(0, max_frames + 1, step):
                ef = off + tf
                if ef > chroma_s.shape[1]: break
                sc = chroma_s[:, off:ef]
                sims = [np.corrcoef(chroma_t[i], sc[i])[0,1]
                        for i in range(12) if not np.isnan(np.corrcoef(chroma_t[i], sc[i])[0,1])]
                if sims and np.mean(sims) > best_score:
                    best_score, best_frame = np.mean(sims), off
                pbar.update(1)
        
        # 精细搜索
        fs = max(0, best_frame - step)
        fe = min(chroma_s.shape[1] - tf, best_frame + step)
        for off in range(fs, fe + 1):
            ef = off + tf
            if ef > chroma_s.shape[1]: break
            sc = chroma_s[:, off:ef]
            sims = [np.corrcoef(chroma_t[i], sc[i])[0,1]
                    for i in range(12) if not np.isnan(np.corrcoef(chroma_t[i], sc[i])[0,1])]
            if sims and np.mean(sims) > best_score:
                best_score, best_frame = np.mean(sims), off
        
        best_offset = best_frame * time_res
        print(f"\n✅ 匹配完成: 在拉伸后参考的第 {best_offset:.3f}s 处")
        print(f"   Chroma相似度: {best_score:.2%}")
        print(f"   速度拉伸率: {stretch_rate:.3f}")
        
        return best_offset, best_score, bpm_orig, stretch_rate, y_ref_stretched
    
    else:
        # 原视频更长 → 在原视频中搜索参考
        print(f"   在原视频中搜索参考音频...")
        chroma_t = librosa.feature.chroma_cqt(y=y_ref_stretched, sr=sr, hop_length=hop_length)
        chroma_s = librosa.feature.chroma_cqt(y=y_orig, sr=sr, hop_length=hop_length)
        
        max_search = min(max_offset, orig_dur - len(y_ref_stretched)/sr - 0.5)
        if max_search <= 0:
            max_search = orig_dur - len(y_ref_stretched)/sr - 0.1
        max_frames = int(max_search / time_res)
        max_frames = min(max_frames, chroma_s.shape[1] - chroma_t.shape[1])
        if max_frames <= 0:
            max_frames = chroma_s.shape[1] - chroma_t.shape[1]
        
        tf = chroma_t.shape[1]
        step = max(1, max_frames // 50)
        
        print(f"   搜索范围: {max_frames*time_res:.1f}s  步长: {step}帧")
        best_frame, best_score = 0, -1.0
        
        with tqdm(total=max_frames//step+1, desc="  搜索", unit="步", ncols=80) as pbar:
            for off in range(0, max_frames + 1, step):
                ef = off + tf
                if ef > chroma_s.shape[1]: break
                sc = chroma_s[:, off:ef]
                sims = [np.corrcoef(chroma_t[i], sc[i])[0,1]
                        for i in range(12) if not np.isnan(np.corrcoef(chroma_t[i], sc[i])[0,1])]
                if sims and np.mean(sims) > best_score:
                    best_score, best_frame = np.mean(sims), off
                pbar.update(1)
        
        fs = max(0, best_frame - step)
        fe = min(chroma_s.shape[1] - tf, best_frame + step)
        for off in range(fs, fe + 1):
            ef = off + tf
            if ef > chroma_s.shape[1]: break
            sc = chroma_s[:, off:ef]
            sims = [np.corrcoef(chroma_t[i], sc[i])[0,1]
                    for i in range(12) if not np.isnan(np.corrcoef(chroma_t[i], sc[i])[0,1])]
            if sims and np.mean(sims) > best_score:
                best_score, best_frame = np.mean(sims), off
        
        best_offset = best_frame * time_res
        print(f"\n✅ 匹配完成: 参考音频在原视频的第 {best_offset:.3f}s 处")
        print(f"   Chroma相似度: {best_score:.2%}")
        
        return best_offset, best_score, bpm_orig, stretch_rate, y_ref_stretched


def align_and_replace_audio_pipeline(
    reference_audio_path: str,
    original_audio_path: str,
    output_audio_path: str,
    offset: float,
    stretch_rate: float,
    y_ref_stretched: np.ndarray
) -> Tuple[np.ndarray, float]:
    """
    替换音频 — 使用已拉伸的参考音频
    
    返回: (新音频数据, 视频裁剪位置秒)
    """
    try:
        print(f"🔧 正在替换音频 (偏移 {offset:+.3f}s)...")
        y_orig, sr = librosa.load(original_audio_path, sr=22050)
        orig_len = len(y_orig)
        ref_len = len(y_ref_stretched)
        
        pos = int(offset * sr)
        if pos < 0: pos = 0
        
        if ref_len >= orig_len:
            # 场景: 拉伸后的参考 >= 原视频
            # 裁掉原视频前offset秒, 用拉伸参考的offset处开始取
            new_len = orig_len - pos
            if new_len <= 0:
                print(f"   ⚠️  偏移({offset:.2f}s) >= 视频长度({orig_len/sr:.2f}s)")
                return y_orig, 0
            
            y_out = y_ref_stretched[pos:pos + new_len]
            print(f"   视频裁掉前{offset:.2f}s → 剩余{new_len/sr:.1f}s")
            print(f"   音频从拉伸后参考的第{offset:.2f}s取{new_len/sr:.1f}s (已匹配BPM)")
            sf.write(output_audio_path, y_out, sr)
            return y_out, offset
        else:
            # 场景: 拉伸后的参考 < 原视频
            # 裁掉前offset秒, 用参考音频填充
            # 参考播完就结束, 不循环
            new_len = orig_len - pos
            take = min(new_len, len(y_ref_stretched))
            y_seg = y_ref_stretched[:take]
            
            print(f"   裁掉前{offset:.2f}s")
            print(f"   参考音频{take/sr:.1f}s播完即止（不循环）")
            y_out = y_seg
            sf.write(output_audio_path, y_out, sr)
            return y_out, offset
    except Exception as e:
        print(f"❌ 替换音频失败: {e}")
        import traceback; traceback.print_exc()
        return None, 0


def replace_audio_in_video(video_path, new_audio_path, output_video_path, trim_start=0):
    try:
        from moviepy import VideoFileClip, AudioFileClip
        import threading, time
        print(f"🎬 正在合成视频...")
        video = VideoFileClip(video_path)
        new_audio = AudioFileClip(new_audio_path)
        
        if trim_start > 0:
            print(f"   裁切视频前{trim_start:.2f}s")
            video = video.subclipped(trim_start, video.duration)
        
        print(f"   视频: {video.duration:.2f}s  音频: {new_audio.duration:.2f}s")
        if new_audio.duration > video.duration:
            new_audio = new_audio.subclipped(0, video.duration)
        elif new_audio.duration < video.duration:
            print(f"   音频更短, 视频同步裁到{new_audio.duration:.2f}s")
            video = video.subclipped(0, new_audio.duration)
        final_video = video.with_audio(new_audio)
        with tqdm(total=100, desc=f"  合成视频", unit="%", ncols=80,
                  bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as pbar:
            write_done = [False]
            def upd():
                p = 0
                while not write_done[0] and p < 95:
                    p = min(p + max(0.5, 5-p*0.05), 95)
                    pbar.n = int(p); pbar.refresh(); time.sleep(0.2)
            pt = threading.Thread(target=upd); pt.daemon = True; pt.start()
            final_video.write_videofile(output_video_path, codec='libx264', audio_codec='aac', logger=None)
            write_done[0] = True; pt.join(timeout=1); pbar.update(100 - pbar.n)
        video.close(); new_audio.close(); final_video.close()
        print(f"✅ 视频合成完成")
        return True
    except Exception as e:
        print(f"❌ 合成视频失败: {e}"); import traceback; traceback.print_exc(); return False


def align_and_replace_audio(dance_video_path, reference_video_path, output_video_path, max_offset=30.0):
    with tempfile.TemporaryDirectory() as tmpdir:
        print("\n" + "="*60)
        print("🎵 音频对齐工具 V5 - 速度自适应版")
        print("="*60)
        print("\n📤 步骤 1/4: 提取音频"); print("-"*60)
        da = os.path.join(tmpdir, "dance_audio.wav")
        ra = os.path.join(tmpdir, "reference_audio.wav")
        if not extract_audio_from_video(dance_video_path, da): return False, 0.0
        if not extract_audio_from_video(reference_video_path, ra): return False, 0.0
        
        print("\n🎯 步骤 2/4: BPM检测+速度匹配"); print("-"*60)
        offset, cs, bpm_orig, stretch_rate, y_stretched = \
            find_best_match_simple(ra, da, max_offset)
        
        print(f"\n   原视频BPM: {bpm_orig:.0f}")
        print(f"   拉伸率: {stretch_rate:.3f}")
        print(f"   偏移: {offset:.3f}s  Chroma: {cs:.2%}")
        
        # 保存拉伸后的参考音频用于替换
        stretched_path = os.path.join(tmpdir, "reference_stretched.wav")
        sf.write(stretched_path, y_stretched, 22050)
        
        print("\n🔧 步骤 3/4: 替换音频 (速度已匹配)"); print("-"*60)
        aligned = os.path.join(tmpdir, "aligned_audio.wav")
        _, trim_start = align_and_replace_audio_pipeline(
            ra, da, aligned, offset, stretch_rate, y_stretched)
        if _ is None: return False, 0.0
        
        print("\n🎬 步骤 4/4: 合成视频"); print("-"*60)
        if not replace_audio_in_video(dance_video_path, aligned, output_video_path, trim_start):
            return False, 0.0
        
        print("\n" + "="*60)
        print("✅ 全部完成!"); print(f"📁 {output_video_path}")
        print(f"📊 BPM: {bpm_orig:.0f}  拉伸: {stretch_rate:.3f}")
        print(f"   偏移: {offset:+.3f}s  Chroma: {cs:.2%}")
        print("="*60)
        return True, offset


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description='音频对齐 V5 速度自适应')
    p.add_argument('dance_video')
    p.add_argument('reference_video')
    p.add_argument('-o', '--output')
    p.add_argument('--max-offset', type=float, default=30.0)
    a = p.parse_args()
    if not a.output:
        base, _ = os.path.splitext(a.dance_video)
        a.output = f"{base}_aligned_v5.mp4"
    success, offset = align_and_replace_audio(a.dance_video, a.reference_video, a.output, a.max_offset)
    print(f"\n{'🎉 成功!' if success else '❌ 失败'} 偏移: {offset:+.3f}s")
    exit(0 if success else 1)
