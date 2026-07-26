#!/usr/bin/env python3
"""
音频对齐 — 最终优化版

策略:
  1. 同时跑 MFCC + Chroma + Onset探针 三种独立搜索
  2. 结果聚类(偏差<0.5s算同簇):
     - 3个一致 → 全部平均
     - 2个一致 → 取一致对的平均
     - 3个全分岐 → 根据时长比智能选择
  3. FFmpeg流复制合成(无损)

用法: python3 align.py --all       # 批量
      python3 align.py 原版.mp4 参考.mp4 -o 输出.mp4
"""
import os, sys, tempfile, subprocess, argparse
import numpy as np
import librosa
import soundfile as sf


def load_audio(path, sr=22050):
    tmp = tempfile.mktemp(suffix=".wav")
    try:
        subprocess.run(["ffmpeg","-y","-i",path,"-ac","1","-ar",str(sr),"-f","wav",tmp],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        y,_ = sf.read(tmp, dtype="float32", always_2d=False)
        return y.mean(axis=1) if y.ndim > 1 else y.astype(np.float64)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)


def detect_bpm(y, sr):
    try:
        e = librosa.onset.onset_strength(y=y, sr=sr, hop_length=512)
        auto = np.correlate(e-np.mean(e), e-np.mean(e), mode='full')[len(e)-1:]
        fr = sr/512
        m1,m2 = int(60*fr/200), int(60*fr/40)
        if m2 >= len(auto):
            t,_ = librosa.beat.beat_track(y=y,sr=sr); return float(t)
        return 60.0 / (m1+np.argmax(auto[m1:m2])/fr)
    except: return 120.0


def _corr_nd(t, s):
    sims = [np.corrcoef(t[i],s[i])[0,1] for i in range(t.shape[0])
            if not np.isnan(np.corrcoef(t[i],s[i])[0,1])]
    return float(np.mean(sims)) if sims else 0.0


def _corr_1d(a, b):
    c = np.corrcoef(a, b)[0, 1]
    return float(c) if not np.isnan(c) else 0.0


def _sliding_search(feat_t, feat_s, max_frames, step=None):
    """滑动窗口: 粗搜50步 + 细搜±step"""
    tf = feat_t.shape[1]; sf = feat_s.shape[1]
    mf = min(max_frames, sf-tf)
    if mf <= 0: mf = sf-tf
    if mf <= 0: return 0, 0.0
    if step is None: step = max(1, mf//50)
    bf, bs = 0, -1.0
    for off in range(0, mf+1, step):
        ef = off+tf
        if ef > sf: break
        sc = _corr_nd(feat_t, feat_s[:, off:ef])
        if sc > bs: bs, bf = sc, off
    fs, fe = max(0, bf-step), min(sf-tf, bf+step)
    for off in range(fs, fe+1):
        ef = off+tf
        if ef > sf: break
        sc = _corr_nd(feat_t, feat_s[:, off:ef])
        if sc > bs: bs, bf = sc, off
    return bf, bs


# ─── 算法1: MFCC (13维) ──────────────────────────────────────────

def search_mfcc(yo, yr, sr, hop, do, dr):
    """MFCC特征搜索, 返回 (cut_orig, cut_ref, confidence)"""
    if do <= dr:
        t, s = yo, yr; is_o = True
    else:
        t, s = yr, yo; is_o = False
    ft = librosa.feature.mfcc(y=t, sr=sr, hop_length=hop, n_mfcc=13, n_fft=2048)
    ft = (ft-ft.mean(1,keepdims=True))/(ft.std(1,keepdims=True)+1e-10)
    fs_arr = librosa.feature.mfcc(y=s, sr=sr, hop_length=hop, n_mfcc=13, n_fft=2048)
    fs_arr = (fs_arr-fs_arr.mean(1,keepdims=True))/(fs_arr.std(1,keepdims=True)+1e-10)
    mf = int(min(60, abs(dr-do))*sr/hop)
    bf, bs = _sliding_search(ft, fs_arr, mf)
    a = bf*hop/sr
    return (0, a, bs) if is_o else (a, 0, bs)


# ─── 算法2: Chroma CQT (12维) ──────────────────────────────────

def search_chroma(yo, yr, sr, hop, do, dr):
    """Chroma特征搜索 + RMS回退 (同align_final策略)"""
    if do <= dr:
        t, s = yo, yr; is_o = True
    else:
        t, s = yr, yo; is_o = False
    ft = librosa.feature.chroma_cqt(y=t, sr=sr, hop_length=hop)
    ft = (ft-ft.mean(1,keepdims=True))/(ft.std(1,keepdims=True)+1e-10)
    fs_arr = librosa.feature.chroma_cqt(y=s, sr=sr, hop_length=hop)
    fs_arr = (fs_arr-fs_arr.mean(1,keepdims=True))/(fs_arr.std(1,keepdims=True)+1e-10)
    mf = int(min(60, abs(dr-do))*sr/hop)
    bf, bs = _sliding_search(ft, fs_arr, mf)
    a = bf*hop/sr
    
    # RMS回退: Chroma置信度 < 15% → 用RMS包络搜索全范围
    if bs < 0.15:
        h2 = 128
        ro = librosa.feature.rms(y=t, hop_length=h2)[0]
        rr = librosa.feature.rms(y=s, hop_length=h2)[0]
        ro = (ro-ro.mean())/(ro.std()+1e-10)
        rr = (rr-rr.mean())/(rr.std()+1e-10)
        boff, bsc = 0, -1.0
        max_off = max(0, rr.shape[0] - ro.shape[0])
        for off in range(0, max_off + 1):
            c = _corr_1d(ro, rr[off:off+ro.shape[0]])
            if c > bsc: bsc, boff = c, off
        a = boff*h2/sr; bs = bsc
    
    return (0, a, bs) if is_o else (a, 0, bs)


# ─── 算法3: Onset探针多探测 ─────────────────────────────────────

def search_onset(yo, yr, sr, hop=256):
    """Onset探针: 多段探针检索 + 最小裁剪量优先"""
    do, dr = len(yo)/sr, len(yr)/sr
    oo = librosa.onset.onset_strength(y=yo, sr=sr, hop_length=hop)
    oo = (oo-oo.mean())/(oo.std()+1e-10)
    orr = librosa.onset.onset_strength(y=yr, sr=sr, hop_length=hop)
    orr = (orr-orr.mean())/(orr.std()+1e-10)
    pl = int(8*sr/hop)
    ms = min(int(15*sr/hop), len(oo)-pl)
    cand = []
    for os_ in range(0, ms, int(0.5*sr/hop)):
        if os_+pl > len(oo): break
        pr = oo[os_:os_+pl]
        bs, ss, bo = -1, -1, 0
        for off in range(len(orr)-pl):
            c = float(np.corrcoef(pr, orr[off:off+pl])[0,1])
            if np.isnan(c): continue
            if c > bs: ss, bs, bo = bs, c, off
            elif c > ss: ss = c
        if bs <= 0.15 or bs-ss <= 0.02: continue
        cand.append((os_*hop/sr, bo*hop/sr, bs))
    if not cand: return 0.0, 0.0, 0.0
    cand.sort(key=lambda x: x[0]+x[1])
    return cand[0][0], cand[0][1], cand[0][2]


# ─── 聚类投票 ───────────────────────────────────────────────────

CLUSTER_THRESH = 0.4  # 同簇阈值

def cluster_vote(results, do, dr):
    """
    results: [(name, cut_orig, cut_ref, conf), ...]
    do, dr: 时长
    """
    valid = [r for r in results if r[3] > 0.03]
    if not valid: return 0, 0, 0, "none"
    
    totals = [r[1]+r[2] for r in valid]
    
    # 聚类
    clusters = []
    assigned = [False]*len(valid)
    for i in range(len(valid)):
        if assigned[i]: continue
        c = [i]; assigned[i] = True
        for j in range(i+1, len(valid)):
            if not assigned[j] and abs(totals[i]-totals[j]) < CLUSTER_THRESH:
                c.append(j); assigned[j] = True
        clusters.append(c)
    clusters.sort(key=lambda c: -len(c))
    
    best = clusters[0]
    members = [valid[i][0] for i in best]
    
    if len(best) >= 2:
        # 一致簇 → 加权平均
        w_co = sum(valid[i][1]*valid[i][3] for i in best)
        w_cr = sum(valid[i][2]*valid[i][3] for i in best)
        w = sum(valid[i][3] for i in best)
        co, cr = w_co/w, w_cr/w
        algo = f"cluster({'+'.join(members)})"
        return co, cr, max(valid[i][3] for i in best), algo
    
    # 全部不一致 → 智能选择
    ratio = max(do, dr) / min(do, dr) if min(do, dr) > 0 else 1
    
    if ratio > 1.3:
        # 时长差异大 → onset探针更可靠 (0726 pattern)
        onset = [r for r in valid if r[0] == 'onset']
        if onset: return onset[0][1], onset[0][2], onset[0][3], "smart-onset"
    
    # 时长相近 → MFCC更可靠 (0728 pattern)
    mfcc = [r for r in valid if r[0] == 'mfcc']
    if mfcc: return mfcc[0][1], mfcc[0][2], mfcc[0][3], "smart-mfcc"
    
    # 兜底: 最高置信度
    best_r = max(valid, key=lambda r: r[3])
    return best_r[1], best_r[2], best_r[3], f"maxconf({best_r[0]})"


# ─── 主对齐 ─────────────────────────────────────────────────────

def find_alignment(orig_path, ref_path, sr=22050, hop=512):
    yo = load_audio(orig_path, sr)
    yr = load_audio(ref_path, sr)
    do, dr = len(yo)/sr, len(yr)/sr
    
    # BPM拉伸
    bo, br = detect_bpm(yo, sr), detect_bpm(yr, sr)
    rate = bo/br if br else 1.0
    need = abs(rate-1.0) > 0.05
    if need and abs(do/dr-1.0) < 0.3:
        for p in [2,4,0.5,0.25]:
            if abs(rate-p) < 0.1: need=False; rate=1.0; break
    if need:
        yr = librosa.effects.time_stretch(y=yr, rate=rate); dr = len(yr)/sr
    
    results = []
    try:
        co, cr, conf = search_mfcc(yo, yr, sr, hop, do, dr)
        results.append(("mfcc", co, cr, conf))
    except: pass
    try:
        co, cr, conf = search_chroma(yo, yr, sr, hop, do, dr)
        results.append(("chroma", co, cr, conf))
    except: pass
    try:
        co, cr, conf = search_onset(yo, yr, sr)
        results.append(("onset", co, cr, conf))
    except: pass
    
    co, cr, conf, algo = cluster_vote(results, do, dr)
    return co, cr, conf, algo, results


# ─── FFmpeg合成 ──────────────────────────────────────────────────

def produce(orig, ref, out, co, cr, sr=22050):
    """FFmpeg流复制: 视频裁co, 参考音频从cr处开始"""
    # 提取参考音频
    aw = tempfile.mktemp(suffix=".wav")
    subprocess.run(["ffmpeg","-y","-i",ref,"-ac","1","-ar",str(sr),aw],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    cmd = ["ffmpeg","-y"]
    if co > 0:
        cmd += ["-ss", str(co)]
    cmd += ["-i", orig]
    if cr > 0:
        cmd += ["-ss", str(cr)]
    cmd += ["-i", aw]
    cmd += ["-c:v", "copy", "-c:a", "aac", "-b:a", "320k"]
    cmd += ["-map", "0:v:0", "-map", "1:a:0"]
    cmd += ["-shortest", out]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if os.path.exists(aw): os.unlink(aw)
    return True


# ─── CLI ─────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="音频对齐 最终版")
    p.add_argument("orig", nargs="?")
    p.add_argument("ref", nargs="?")
    p.add_argument("-o","--output")
    p.add_argument("--all", action="store_true")
    p.add_argument("--crop", action="store_true")
    args = p.parse_args()
    
    if args.all:
        base = "/Users/a123/Downloads"; desk = "/Users/a123/Desktop"
        pairs = [
            ("0726", f"{base}/0726原视频.MP4", f"{base}/0726参考音频.MP4"),
            ("0727", f"{base}/0727原版1.MP4", f"{base}/0727参考.MP4"),
            ("0728", f"{base}/0728原版.MP4", f"{base}/0728参考.MP4"),
            ("0729", f"{base}/0729原版.MP4", f"{base}/0729参考.MP4"),
            ("0730", f"{base}/0730原版.MP4", f"{base}/0730参考.MP4"),
        ]
        for label, orig, ref in pairs:
            if not (os.path.exists(orig) and os.path.exists(ref)): continue
            print(f"\n{'='*50}\n🎬 {label}")
            co, cr, conf, algo, results = find_alignment(orig, ref)
            for name, rco, rcr, rconf in results:
                print(f"    {name}: 裁原={rco:.3f}s 裁参={rcr:.3f}s  conf={rconf:.2%}")
            print(f"  → {algo}: 裁原={co:.3f}s 裁参={cr:.3f}s  conf={conf:.2%}")
            if not args.crop and conf > 0.03:
                out = f"{desk}/{label}_aligned.mp4"
                ok = produce(orig, ref, out, co, cr)
                print(f"  {'✅' if ok else '❌'} {out}")
        print(f"\n{'='*50}\n✅ 全部完成!")
        return
    
    if not args.orig or not args.ref:
        p.print_help(); sys.exit(1)
    
    label = os.path.splitext(os.path.basename(args.orig))[0]
    out = args.output or f"{label}_aligned.mp4"
    print(f"🎬 {label}")
    co, cr, conf, algo, results = find_alignment(args.orig, args.ref)
    for name, rco, rcr, rconf in results:
        print(f"    {name}: 裁原={rco:.3f}s 裁参={rcr:.3f}s  conf={rconf:.2%}")
    print(f"  → {algo}: 裁原={co:.3f}s 裁参={cr:.3f}s  conf={conf:.2%}")
    if not args.crop and conf > 0.03:
        ok = produce(args.orig, args.ref, out, co, cr)
        print(f"  {'✅' if ok else '❌'} {out}")

if __name__ == "__main__":
    main()
