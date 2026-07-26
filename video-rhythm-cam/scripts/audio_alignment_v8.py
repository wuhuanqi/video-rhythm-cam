#!/usr/bin/env python3
"""
音频对齐 V8 — Onset 探针 + 最小裁剪

算法:
  1. 在原版不同位置取长探针(8s), 去参考中检索
  2. 取 i+j 最小的那对作为裁剪量
  3. 合成时用 FFmpeg 流复制 (无损)
"""
import os, sys, tempfile, shutil, subprocess, argparse
import numpy as np
import librosa
import soundfile as sf


def find_alignment(orig_audio, ref_audio, sr=22050, hop=256):
    """
    找最小裁剪对 (cut_orig, cut_ref) 使得 orig[cut_orig:] ≈ ref[cut_ref:]
    返回: (cut_orig_sec, cut_ref_sec, confidence, stretch_rate)
    """
    yo, _ = librosa.load(orig_audio, sr=sr)
    yr, _ = librosa.load(ref_audio, sr=sr)

    ons_o = librosa.onset.onset_strength(y=yo, sr=sr, hop_length=hop)
    ons_r = librosa.onset.onset_strength(y=yr, sr=sr, hop_length=hop)
    ons_o = (ons_o - ons_o.mean()) / (ons_o.std() + 1e-10)
    ons_r = (ons_r - ons_r.mean()) / (ons_r.std() + 1e-10)

    # 用原版取探针，在参考中检索
    pr_len = int(8 * sr / hop)
    max_start = min(int(15 * sr / hop), len(ons_o) - pr_len)
    if max_start <= 0:
        pr_len = int(5 * sr / hop)
        max_start = len(ons_o) - pr_len

    candidates = []
    for orig_start in range(0, max_start, int(0.5 * sr / hop)):
        if orig_start + pr_len > len(ons_o):
            break
        probe = ons_o[orig_start:orig_start + pr_len]
        bo, bs, ss = 0, -1, -1
        for off in range(len(ons_r) - pr_len):
            c = float(np.corrcoef(probe, ons_r[off:off + pr_len])[0, 1])
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
            if orig_start + el <= len(ons_o) and bo + el <= len(ons_r):
                sc = float(np.corrcoef(ons_o[orig_start:orig_start + el],
                                       ons_r[bo:bo + el])[0, 1])
                if not np.isnan(sc):
                    stab.append(sc)
        if stab:
            os_ = orig_start * hop / sr
            rs_ = bo * hop / sr
            candidates.append((os_, rs_, os_ + rs_, bs, bs - ss, float(np.mean(stab))))

    if not candidates:
        return 0.0, 0.0, 0.0, 1.0

    # 最小裁剪量优先
    candidates.sort(key=lambda x: x[2])
    best = candidates[0]
    return best[0], best[1], best[3], 1.0


def _stream_copy_produce(orig_video, ref_video, output, cut_orig, cut_ref, sr=22050):
    """FFmpeg 流复制合成（视频无损）"""
    yr, _ = librosa.load(ref_video, sr=sr)
    rs = int(cut_ref * sr)
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                            "format=duration", "-of", "csv=p=0", orig_video],
                           capture_output=True, text=True)
    orig_dur = float(probe.stdout.strip())
    leftover = max(0, orig_dur - cut_orig)
    take = min(len(yr) - rs, int(leftover * sr))
    if take <= 0:
        return False
    audio_data = yr[rs:rs + take]
    aw = tempfile.mktemp(suffix=".wav")
    aa = tempfile.mktemp(suffix=".aac")
    vc = tempfile.mktemp(suffix=".mp4")
    sf.write(aw, audio_data, sr)
    subprocess.run(["ffmpeg", "-i", orig_video, "-ss", str(cut_orig),
                    "-c:v", "copy", "-an", "-y", vc], capture_output=True)
    subprocess.run(["ffmpeg", "-i", aw, "-c:a", "aac", "-b:a", "320k", "-y", aa],
                   capture_output=True)
    subprocess.run(["ffmpeg", "-i", vc, "-i", aa, "-c:v", "copy", "-c:a", "copy",
                    "-map", "0:v:0", "-map", "1:a:0", "-shortest", "-y", output],
                   capture_output=True)
    for f in [aw, aa, vc]:
        os.unlink(f)
    return True


def align_and_replace_audio(dance_video_path, reference_video_path, output_video_path, max_offset=60.0):
    """V4 兼容接口"""
    da = dance_video_path if dance_video_path.endswith('.wav') else None
    ra = reference_video_path if reference_video_path.endswith('.wav') else None
    cut_orig, cut_ref, conf, _ = find_alignment(dance_video_path, reference_video_path)
    if conf < 0.15:
        return False, 0.0
    ok = _stream_copy_produce(dance_video_path, reference_video_path, output_video_path, cut_orig, cut_ref)
    return ok, cut_orig if cut_orig > 0 else -cut_ref


def process(label, orig, ref, output, crop_only=False):
    print(f"\n{'='*50}\n🎬 {label}")
    if not (os.path.exists(orig) and os.path.exists(ref)):
        print(f"  ⚠️  文件不存在")
        return
    tmp = tempfile.mkdtemp()
    da = os.path.join(tmp, "d.wav")
    ra = os.path.join(tmp, "r.wav")
    from moviepy import VideoFileClip
    for vp, ap in [(orig, da), (ref, ra)]:
        v = VideoFileClip(vp)
        v.audio.write_audiofile(ap, logger=None)
        v.close()
    cut_orig, cut_ref, conf, _ = find_alignment(da, ra)
    print(f"  原版裁: {cut_orig:.3f}s  参考裁: {cut_ref:.3f}s  "
          f"总计: {cut_orig+cut_ref:.3f}s  置信度: {conf:.2%}")
    if not crop_only and conf > 0.15:
        ok = _stream_copy_produce(orig, ref, output, cut_orig, cut_ref)
        print(f"  {'✅' if ok else '❌'} {output}")
    elif crop_only:
        print(f"  (仅查看)")
    else:
        print(f"  ⚠️  置信度不足")
    shutil.rmtree(tmp)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("orig", nargs="?")
    parser.add_argument("ref", nargs="?")
    parser.add_argument("-o", "--output")
    parser.add_argument("--all", action="store_true",
                        help="批量处理 Downloads/0726-0730")
    parser.add_argument("--crop", action="store_true")
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
        print("\n用法: python3 align_v8.py --all")
        sys.exit(1)

    label = os.path.splitext(os.path.basename(args.orig))[0]
    out = args.output or f"{os.path.dirname(args.orig) or '.'}/{label}_aligned.mp4"
    process(label, args.orig, args.ref, out, args.crop)


if __name__ == "__main__":
    main()
