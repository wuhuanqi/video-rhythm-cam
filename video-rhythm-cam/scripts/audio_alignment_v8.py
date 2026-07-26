#!/usr/bin/env python3
"""
音频对齐工具 — align_v8
找最小裁剪 (原版裁 i, 参考裁 j) 使得 A[i:] ≈ B[j:]

用法:
  python3 align_v8.py 原版.mp4 参考.mp4 -o 输出.mp4
  python3 align_v8.py --all                     # 批量处理 Downloads 中 072x/073x 全部
  python3 align_v8.py --all --crop              # 只显示偏移量, 不合成
"""
import os, sys, tempfile, shutil, argparse
import numpy as np
import librosa
import soundfile as sf


def _detect_bpm(y, sr):
    """BPM检测 (onset自相关法)"""
    try:
        onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=512)
        auto = np.correlate(onset_env - np.mean(onset_env),
                            onset_env - np.mean(onset_env), mode='full')
        auto = auto[len(auto)//2:]
        frame_rate = sr / 512
        mf1, mf2 = int(60 * frame_rate / 200), int(60 * frame_rate / 40)
        if mf2 >= len(auto):
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            return float(tempo)
        peak = mf1 + np.argmax(auto[mf1:mf2])
        return 60.0 / (peak / frame_rate)
    except:
        return 120.0


def find_alignment(orig_audio, ref_audio, sr=22050, hop=256):
    """
    找对齐裁剪量, 返回 (cut_orig_s, cut_ref_s, confidence, stretch_rate)
    """
    yo, _ = librosa.load(orig_audio, sr=sr)
    yr, _ = librosa.load(ref_audio, sr=sr)

    # ── BPM检测 + 速度拉伸 ──
    bpm_orig = _detect_bpm(yo, sr)
    bpm_ref = _detect_bpm(yr, sr)
    stretch_rate = bpm_orig / bpm_ref if bpm_ref > 0 else 1.0
    need_stretch = abs(stretch_rate - 1.0) > 0.05

    if need_stretch and abs(len(yo)/sr / (len(yr)/sr) - 1.0) < 0.3:
        for p in [2, 4, 0.5, 0.25]:
            if abs(stretch_rate - p) < 0.1:
                need_stretch = False
                stretch_rate = 1.0
                break

    stretched = False
    if need_stretch:
        yr = librosa.effects.time_stretch(y=yr, rate=stretch_rate)
        stretched = True

    # ── Onset 特征 (节奏模式) ──
    ons_o = librosa.onset.onset_strength(y=yo, sr=sr, hop_length=hop)
    ons_r = librosa.onset.onset_strength(y=yr, sr=sr, hop_length=hop)
    ons_o = (ons_o - ons_o.mean()) / (ons_o.std() + 1e-10)
    ons_r = (ons_r - ons_r.mean()) / (ons_r.std() + 1e-10)

    # ── 探针搜索 ──
    pr_sec, pr_len = 8.0, int(8 * sr / hop)
    max_start = min(int(15 * sr / hop), len(ons_o) - pr_len)
    if max_start <= 0:
        pr_sec = min(5.0, len(yo) / sr - 1)
        pr_len = int(pr_sec * sr / hop)
        max_start = len(ons_o) - pr_len

    candidates = []
    for orig_start in range(0, max_start, int(0.5 * sr / hop)):
        if orig_start + pr_len > len(ons_o):
            break
        probe = ons_o[orig_start:orig_start + pr_len]
        bo, bs, ss = 0, -1, -1
        for off in range(len(ons_r) - pr_len):
            c = float(np.corrcoef(probe, ons_r[off:off+pr_len])[0, 1])
            if np.isnan(c):
                continue
            if c > bs:
                ss, bs, bo = bs, c, off
            elif c > ss:
                ss = c
        if bs <= 0.15 or bs - ss <= 0.02:
            continue
        stab = []
        for ext in [10, 12]:
            el = int(ext * sr / hop)
            if orig_start+el <= len(ons_o) and bo+el <= len(ons_r):
                sc = float(np.corrcoef(ons_o[orig_start:orig_start+el],
                                       ons_r[bo:bo+el])[0, 1])
                if not np.isnan(sc):
                    stab.append(sc)
        if stab:
            os_ = orig_start * hop / sr
            rs_ = bo * hop / sr
            candidates.append((os_, rs_, os_+rs_, bs, bs-ss, float(np.mean(stab))))

    if not candidates:
        return 0.0, 0.0, 0.0, 1.0

    candidates.sort(key=lambda x: x[2])          # 最小 i+j
    best = candidates[0]

    # ── 低置信度时 RMS 回退 ──
    if best[3] < 0.78:
        rms_r = librosa.feature.rms(y=yr, hop_length=hop)[0]
        rms_o = librosa.feature.rms(y=yo, hop_length=hop)[0]
        rms_diff_r = np.diff(rms_r)
        mr = np.argmax(rms_diff_r[:int(15*sr/hop)]) * hop / sr
        rms_o_n = (rms_o - rms_o.mean()) / (rms_o.std() + 1e-10)
        rms_r_n = (rms_r - rms_r.mean()) / (rms_r.std() + 1e-10)
        best_ro, best_rc = 0, -1
        for off in range(len(rms_o)):
            win = min(int(5*sr/hop), len(rms_o)-off, len(rms_r_n))
            if win < 20:
                break
            c = float(np.corrcoef(rms_o_n[off:off+win], rms_r_n[:win])[0, 1])
            if not np.isnan(c) and c > best_rc:
                best_rc, best_ro = c, off
        rms_orig = best_ro * hop / sr
        if rms_orig < 1.0:
            return rms_orig, mr, best_rc, stretch_rate if stretched else 1.0

    return best[0], best[1], best[3], stretch_rate if stretched else 1.0


def produce(orig_video, ref_video, output, cut_orig, cut_ref, stretch_rate=1.0, sr=22050):
    """合成裁剪后的视频"""
    from moviepy import VideoFileClip, AudioFileClip
    from tqdm import tqdm
    import threading, time

    yr, _ = librosa.load(ref_video, sr=sr)
    if abs(stretch_rate - 1.0) > 0.005:
        yr = librosa.effects.time_stretch(y=yr, rate=stretch_rate)
        print(f"  速度拉伸: rate={stretch_rate:.3f}")

    video = VideoFileClip(orig_video)
    if cut_orig > 0:
        video = video.subclipped(cut_orig, video.duration)
    td = video.duration
    rs = int(cut_ref * sr)
    take = min(len(yr) - rs, int(td * sr))
    if take <= 0:
        return False
    audio_data = yr[rs:rs + take]
    ta = os.path.join(tempfile.gettempdir(), f"aligned_{os.getpid()}.wav")
    sf.write(ta, audio_data, sr)
    na = AudioFileClip(ta)
    md = min(video.duration, na.duration)
    if na.duration > md:
        na = na.subclipped(0, md)
    if video.duration > md:
        video = video.subclipped(0, md)
    final = video.with_audio(na)

    with tqdm(total=100, desc="  合成", ncols=80,
              bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}") as pbar:
        done = [False]
        def upd():
            p = 0
            while not done[0] and p < 95:
                p = min(p + max(0.5, 5-p*0.05), 95)
                pbar.n = int(p); pbar.refresh(); time.sleep(0.2)
        pt = threading.Thread(target=upd); pt.daemon = True; pt.start()
        final.write_videofile(output, codec='libx264', audio_codec='aac', logger=None)
        done[0] = True; pt.join(timeout=1); pbar.update(100-pbar.n)

    video.close(); na.close(); final.close()
    os.unlink(ta)
    return True


def _stream_copy_produce(orig_video, ref_video, output, cut_orig, cut_ref, stretch_rate=1.0, sr=22050):
    """用 FFmpeg 流复制合成 — 视频零质量损失"""
    import subprocess, tempfile as _tf
    from pathlib import Path

    yr, _ = librosa.load(ref_video, sr=sr)
    if abs(stretch_rate - 1.0) > 0.005:
        yr = librosa.effects.time_stretch(y=yr, rate=stretch_rate)

    rs = int(cut_ref * sr)
    # 获取视频原时长
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                            "format=duration", "-of", "csv=p=0", orig_video],
                           capture_output=True, text=True)
    orig_dur = float(probe.stdout.strip())
    leftover = max(0, orig_dur - cut_orig)
    take = min(len(yr) - rs, int(leftover * sr))
    if take <= 0:
        return False

    audio_data = yr[rs:rs + take]
    audio_wav = _tf.mktemp(suffix=".wav")
    audio_aac = _tf.mktemp(suffix=".aac")
    sf.write(audio_wav, audio_data, sr)

    # Step 1: 裁剪视频 (流复制, 不重编码)
    video_cut = _tf.mktemp(suffix=".mp4")
    subprocess.run(["ffmpeg", "-i", orig_video, "-ss", str(cut_orig),
                    "-c:v", "copy", "-an", "-y", video_cut],
                   capture_output=True)

    # Step 2: 音频转 AAC
    subprocess.run(["ffmpeg", "-i", audio_wav,
                    "-c:a", "aac", "-b:a", "320k", "-y", audio_aac],
                   capture_output=True)

    # Step 3: 合并 (视频流复制, 用新音频)
    subprocess.run(["ffmpeg", "-i", video_cut, "-i", audio_aac,
                    "-c:v", "copy", "-c:a", "copy",
                    "-map", "0:v:0", "-map", "1:a:0",
                    "-shortest", "-y", output],
                   capture_output=True)

    os.unlink(audio_wav)
    os.unlink(audio_aac)
    os.unlink(video_cut)
    return True


def align_and_replace_audio(dance_video_path, reference_video_path, output_video_path, max_offset=60.0):
    """
    V4 兼容接口 — 供 API 使用
    返回: (success: bool, offset: float)
    """
    cut_orig, cut_ref, conf, stretch = find_alignment(dance_video_path, reference_video_path)
    if conf < 0.15:
        return False, 0.0
    ok = _stream_copy_produce(dance_video_path, reference_video_path, output_video_path, cut_orig, cut_ref, stretch)
    return ok, cut_orig


def process(label, orig, ref, output, crop_only=False):
    """处理一对视频"""
    print(f"\n{'='*50}\n🎬 {label}")

    if not (os.path.exists(orig) and os.path.exists(ref)):
        print(f"  ⚠️  文件不存在: {orig} 或 {ref}")
        return

    tmp = tempfile.mkdtemp()
    da = os.path.join(tmp, "d.wav"); ra = os.path.join(tmp, "r.wav")
    from moviepy import VideoFileClip
    for vp, ap in [(orig, da), (ref, ra)]:
        v = VideoFileClip(vp); v.audio.write_audiofile(ap, logger=None); v.close()

    cut_orig, cut_ref, conf, stretch = find_alignment(da, ra)
    extra = f"  拉伸: {stretch:.3f}" if abs(stretch-1) > 0.01 else ""
    print(f"  原版裁: {cut_orig:.3f}s  参考裁: {cut_ref:.3f}s  "
          f"总计: {cut_orig+cut_ref:.3f}s  置信度: {conf:.2%}{extra}")

    if not crop_only and conf > 0.15:
        ok = _stream_copy_produce(orig, ref, output, cut_orig, cut_ref, stretch)
        print(f"  {'✅' if ok else '❌'} {output}")
    elif crop_only:
        print(f"  (仅查看)")
    else:
        print(f"  ⚠️  置信度过低, 跳过合成")

    shutil.rmtree(tmp)


def main():
    parser = argparse.ArgumentParser(description="音频对齐 — 最小裁剪匹配")
    parser.add_argument("orig", nargs="?", help="原版视频路径")
    parser.add_argument("ref", nargs="?", help="参考视频路径")
    parser.add_argument("-o", "--output", default=None, help="输出路径")
    parser.add_argument("--all", action="store_true", help="批量处理 0726-0730")
    parser.add_argument("--crop", action="store_true", help="仅显示偏移, 不合成")
    args = parser.parse_args()

    if args.all:
        base = "/Users/a123/Downloads"
        desk = "/Users/a123/Desktop"
        pairs = [
            ("0726", f"{base}/0726原视频.MP4", f"{base}/0726参考音频.MP4"),
            ("0727", f"{base}/0727原版1.MP4", f"{base}/0727参考.MP4"),
            ("0728", f"{base}/0728原版.MP4", f"{base}/0728参考.MP4"),
            ("0730", f"{base}/0730原版.MP4", f"{base}/0730参考.MP4"),
        ]
        for label, orig, ref in pairs:
            process(label, orig, ref, f"{desk}/{label}_aligned.mp4", args.crop)
        print(f"\n{'='*50}\n✅ 全部完成!")
        return

    if not args.orig or not args.ref:
        parser.print_help()
        print("\n示例:")
        print("  python3 align_v8.py --all")
        print("  python3 align_v8.py 原版.mp4 参考.mp4 -o 结果.mp4")
        sys.exit(1)

    label = os.path.splitext(os.path.basename(args.orig))[0]
    out = args.output or f"{os.path.dirname(args.orig) or '.'}/{label}_aligned.mp4"
    process(label, args.orig, args.ref, out, args.crop)


if __name__ == "__main__":
    main()
