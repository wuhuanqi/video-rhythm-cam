"use client";

import Link from "next/link";
import { ArrowRight, Waves, Sparkles, Zap, Volume2, Music2 } from "lucide-react";

// 背景装饰
function HeroBackground() {
  return (
    <div className="absolute inset-0 overflow-hidden">
      {/* Gradient Orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[var(--neon-pink)] rounded-full blur-[150px] opacity-20 animate-pulse" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-[var(--neon-cyan)] rounded-full blur-[150px] opacity-20 animate-pulse" style={{ animationDelay: '1s' }} />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-[var(--neon-purple)] rounded-full blur-[200px] opacity-10" />
      
      {/* Grid Pattern */}
      <div 
        className="absolute inset-0 opacity-[0.02]"
        style={{
          backgroundImage: `
            linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)
          `,
          backgroundSize: '100px 100px'
        }}
      />
    </div>
  );
}

// 波形动画
function WaveformAnimation() {
  return (
    <div className="flex items-end justify-center gap-1 h-20">
      {[...Array(20)].map((_, i) => {
        const height = Math.sin((i / 20) * Math.PI) * 100;
        const delay = i * 0.05;
        return (
          <div
            key={i}
            className="w-1.5 rounded-full bg-gradient-to-t from-[var(--neon-pink)] to-[var(--neon-cyan)]"
            style={{
              height: `${20 + height * 0.8}%`,
              animation: `waveform 1.5s ease-in-out infinite`,
              animationDelay: `${delay}s`,
            }}
          />
        );
      })}
    </div>
  );
}

export default function Home() {
  return (
    <main className="min-h-screen relative overflow-hidden">
      <HeroBackground />
      
      {/* Navigation */}
      <nav className="relative z-10 px-8 py-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[var(--neon-pink)] to-[var(--neon-purple)] flex items-center justify-center">
              <Waves className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold gradient-text">PIPI</span>
          </div>
          
          <Link
            href="/workbench"
            className="px-5 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white/80 hover:bg-white/10 hover:text-white transition-all text-sm font-medium"
          >
            进入工作台
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative z-10 px-8 pt-20 pb-32">
        <div className="max-w-5xl mx-auto text-center">
          
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 mb-8">
            <Sparkles className="w-4 h-4 text-[var(--neon-cyan)]" />
            <span className="text-sm text-white/60">AI 驱动的音频处理工具</span>
          </div>

          {/* Main Headline */}
          <h1 className="text-6xl md:text-7xl lg:text-8xl font-bold leading-[1.1] mb-8">
            <span className="text-white">用</span>
            <span className="text-[var(--neon-cyan)] text-glow-cyan">完美音质</span>
            <br />
            <span className="text-white">替换你的</span>
            <span className="text-[var(--neon-pink)] text-glow-pink">舞蹈视频</span>
          </h1>

          {/* Subheadline */}
          <p className="text-xl md:text-2xl text-white/40 max-w-2xl mx-auto mb-12 leading-relaxed">
            上传舞蹈视频和高质量音源，
            <br className="hidden md:block" />
            AI 自动分析频谱，精准对齐每一个卡点
          </p>

          {/* Waveform Animation */}
          <div className="mb-12">
            <WaveformAnimation />
          </div>

          {/* CTA Button */}
          <Link
            href="/workbench"
            className="group inline-flex items-center gap-3 px-10 py-5 rounded-2xl btn-action text-white text-xl"
          >
            <Zap className="w-6 h-6" />
            <span>开始使用</span>
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </Link>

        </div>
      </section>

      {/* Features Section */}
      <section className="relative z-10 px-8 py-20">
        <div className="max-w-5xl mx-auto">
          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                icon: Waves,
                title: "频谱分析",
                desc: "使用 AI 算法分析音频波形特征，自动识别节拍位置",
                color: "pink"
              },
              {
                icon: Zap,
                title: "智能对齐",
                desc: "通过交叉相关算法精准匹配，确保每个卡点完美同步",
                color: "purple"
              },
              {
                icon: Volume2,
                title: "无损替换",
                desc: "保持原视频画质不变，仅替换音频轨道",
                color: "cyan"
              }
            ].map((feature, i) => (
              <div
                key={i}
                className="glass rounded-3xl p-8 hover:bg-white/[0.04] transition-all group"
              >
                <div 
                  className={`w-14 h-14 rounded-2xl flex items-center justify-center mb-6 ${
                    feature.color === 'pink' ? 'bg-[var(--neon-pink)]/10' :
                    feature.color === 'purple' ? 'bg-[var(--neon-purple)]/10' :
                    'bg-[var(--neon-cyan)]/10'
                  }`}
                >
                  <feature.icon 
                    className={`w-7 h-7 ${
                      feature.color === 'pink' ? 'text-[var(--neon-pink)]' :
                      feature.color === 'purple' ? 'text-[var(--neon-purple)]' :
                      'text-[var(--neon-cyan)]'
                    }`} 
                  />
                </div>
                <h3 className="text-xl font-semibold text-white mb-3">{feature.title}</h3>
                <p className="text-white/40 leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it Works */}
      <section className="relative z-10 px-8 py-20">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-16">
            <span className="text-white">简单</span>
            <span className="gradient-text ml-2">三步</span>
            <span className="text-white">，完成音频对齐</span>
          </h2>

          <div className="space-y-8">
            {[
              {
                step: "01",
                title: "上传舞蹈视频",
                desc: "你自己拍摄的舞蹈视频，音质可能不太好",
                color: "pink"
              },
              {
                step: "02", 
                title: "上传参考音源",
                desc: "同一首歌的 MV 或高音质视频",
                color: "cyan"
              },
              {
                step: "03",
                title: "自动对齐输出",
                desc: "AI 分析频谱，精准对齐，输出高质量音频的舞蹈视频",
                color: "purple"
              }
            ].map((item, i) => (
              <div
                key={i}
                className="flex items-start gap-6 glass rounded-2xl p-6"
              >
                <div 
                  className={`text-5xl font-bold font-mono ${
                    item.color === 'pink' ? 'text-[var(--neon-pink)]/30' :
                    item.color === 'cyan' ? 'text-[var(--neon-cyan)]/30' :
                    'text-[var(--neon-purple)]/30'
                  }`}
                >
                  {item.step}
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">{item.title}</h3>
                  <p className="text-white/40">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Final CTA */}
          <div className="text-center mt-16">
            <Link
              href="/workbench"
              className="inline-flex items-center gap-3 px-8 py-4 rounded-xl bg-white text-black font-semibold hover:bg-white/90 transition-colors"
            >
              <Music2 className="w-5 h-5" />
              <span>立即体验</span>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 px-8 py-8 border-t border-white/5">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Waves className="w-5 h-5 text-white/40" />
            <span className="text-white/40 text-sm">PIPI Audio Sync</span>
          </div>
          <p className="text-white/20 text-sm">AI-Powered Audio Alignment</p>
        </div>
      </footer>
    </main>
  );
}
