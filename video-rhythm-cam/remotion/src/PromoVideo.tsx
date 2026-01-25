import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Sequence,
  staticFile,
} from "remotion";

// ============================================
// 工具函数
// ============================================

/**
 * 文字淡入 + 向上移动动画
 */
function FadeInText({
  children,
  frame,
  delay,
  duration = 30,
}: {
  children: React.ReactNode;
  frame: number;
  delay: number;
  duration?: number;
}) {
  const opacity = interpolate(frame, [delay, delay + duration], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  const translateY = interpolate(frame, [delay, delay + duration], [30, 0], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  return (
    <div
      style={{
        opacity,
        transform: `translateY(${translateY}px)`,
      }}
    >
      {children}
    </div>
  );
}

/**
 * 脉冲缩放动画
 */
function PulseEffect({ children, frame, duration = 60 }: { children: React.ReactNode; frame: number; duration?: number }) {
  const scale = spring({
    frame: frame % duration,
    fps: 30,
    config: {
      damping: 10,
      stiffness: 100,
    },
  });

  const pulsingScale = interpolate(scale, [0, 1], [0.95, 1.05], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  return (
    <div
      style={{
        transform: `scale(${pulsingScale})`,
      }}
    >
      {children}
    </div>
  );
}

/**
 * 功能卡片组件
 */
function FeatureCard({
  icon,
  title,
  description,
  frame,
  delay,
}: {
  icon: string;
  title: string;
  description: string;
  frame: number;
  delay: number;
}) {
  const scale = spring({
    frame: Math.max(0, frame - delay),
    fps: 30,
    config: {
      damping: 15,
      stiffness: 100,
    },
  });

  const cardScale = interpolate(scale, [0, 1], [0.8, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  const opacity = interpolate(frame, [delay, delay + 15], [0, 1], {
    extrapolateRight: "clamp",
    extrapolateLeft: "clamp",
  });

  return (
    <div
      style={{
        scale: cardScale,
        opacity,
        backgroundColor: "rgba(255, 255, 255, 0.1)",
        backdropFilter: "blur(10px)",
        borderRadius: 20,
        padding: 30,
        margin: 15,
        flex: 1,
        minWidth: 280,
        maxWidth: 320,
        border: "1px solid rgba(255, 255, 255, 0.2)",
      }}
    >
      <div style={{ fontSize: 48, marginBottom: 15 }}>{icon}</div>
      <h3
        style={{
          color: "#fff",
          fontSize: 28,
          fontWeight: "bold",
          margin: "0 0 10px 0",
        }}
      >
        {title}
      </h3>
      <p
        style={{
          color: "rgba(255, 255, 255, 0.8)",
          fontSize: 18,
          margin: 0,
          lineHeight: 1.5,
        }}
      >
        {description}
      </p>
    </div>
  );
}

// ============================================
// 场景组件
// ============================================

/**
 * 场景1: 开场标题
 */
function Scene1_Opening({ frame }: { frame: number }) {
  const titleOpacity = interpolate(frame, [0, 30], [0, 1], {
    extrapolateRight: "clamp",
  });

  const titleScale = spring({
    frame,
    fps: 30,
    config: {
      damping: 15,
      stiffness: 100,
    },
  });

  const scaleValue = interpolate(titleScale, [0, 1], [0.5, 1], {
    extrapolateRight: "clamp",
  });

  const subtitleOpacity = interpolate(frame, [30, 60], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#0a0a0a" }}>
      {/* 背景渐变 */}
      <div
        style={{
          position: "absolute",
          width: "100%",
          height: "100%",
          background: "radial-gradient(circle at center, #1a1a2e 0%, #0a0a0a 100%)",
        }}
      />

      {/* 装饰性圆圈 */}
      <div
        style={{
          position: "absolute",
          width: 600,
          height: 600,
          borderRadius: "50%",
          border: "2px solid rgba(139, 92, 246, 0.3)",
          left: "50%",
          top: "50%",
          transform: `translate(-50%, -50%) scale(${scaleValue})`,
        }}
      />

      {/* 标题 */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "45%",
          transform: "translate(-50%, -50%)",
          textAlign: "center",
          width: "100%",
        }}
      >
        <h1
          style={{
            fontSize: 96,
            fontWeight: "900",
            margin: 0,
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            opacity: titleOpacity,
            transform: `scale(${scaleValue})`,
          }}
        >
          Video Rhythm Cam
        </h1>

        <p
          style={{
            fontSize: 36,
            color: "rgba(255, 255, 255, 0.9)",
            marginTop: 20,
            opacity: subtitleOpacity,
          }}
        >
          让视频随音乐律动
        </p>
      </div>

      {/* 节奏动画圆点 */}
      <div style={{ position: "absolute", bottom: 100, left: 0, right: 0, display: "flex", justifyContent: "center", gap: 15 }}>
        {[0, 1, 2, 3, 4].map((i) => {
          const delay = i * 8;
          const dotScale = spring({
            frame: Math.max(0, frame - 30 - delay),
            fps: 30,
            config: { damping: 10, stiffness: 200 },
          });
          const scale = interpolate(dotScale, [0, 1], [0.5, 1.5]);
          const opacity = interpolate(frame, [30 + delay, 45 + delay], [0, 1], {
            extrapolateLeft: "clamp",
          });

          return (
            <div
              key={i}
              style={{
                width: 20,
                height: 20,
                borderRadius: "50%",
                backgroundColor: "#8b5cf6",
                scale,
                opacity,
              }}
            />
          );
        })}
      </div>
    </AbsoluteFill>
  );
}

/**
 * 场景2: 问题引入
 */
function Scene2_Problem({ frame }: { frame: number }) {
  return (
    <AbsoluteFill style={{ backgroundColor: "#0a0a0a" }}>
      <div
        style={{
          position: "absolute",
          width: "100%",
          height: "100%",
          background: "radial-gradient(circle at center, #1a0a1a 0%, #0a0a0a 100%)",
        }}
      />

      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "50%",
          transform: "translate(-50%, -50%)",
          textAlign: "center",
          width: "80%",
        }}
      >
        <FadeInText frame={frame} delay={0}>
          <h2
            style={{
              fontSize: 72,
              fontWeight: "bold",
              color: "#fff",
              margin: 0,
            }}
          >
            你的舞蹈视频...
          </h2>
        </FadeInText>

        <FadeInText frame={frame} delay={20}>
          <p
            style={{
              fontSize: 48,
              color: "rgba(255, 255, 255, 0.7)",
              marginTop: 30,
            }}
          >
            缺少节奏感？
          </p>
        </FadeInText>

        <FadeInText frame={frame} delay={40}>
          <div
            style={{
              fontSize: 36,
              color: "#ef4444",
              marginTop: 40,
              padding: "20px 40px",
              backgroundColor: "rgba(239, 68, 68, 0.1)",
              borderRadius: 15,
              border: "2px solid rgba(239, 68, 68, 0.3)",
            }}
          >
            😴 画面平淡无奇
          </div>
        </FadeInText>
      </div>
    </AbsoluteFill>
  );
}

/**
 * 场景3: 解决方案
 */
function Scene3_Solution({ frame }: { frame: number }) {
  const bgOpacity = interpolate(frame, [0, 30], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#0a0a0a" }}>
      <div
        style={{
          position: "absolute",
          width: "100%",
          height: "100%",
          background: "radial-gradient(circle at center, #0a1a2e 0%, #0a0a0a 100%)",
          opacity: bgOpacity,
        }}
      />

      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "50%",
          transform: "translate(-50%, -50%)",
          textAlign: "center",
          width: "80%",
        }}
      >
        <FadeInText frame={frame} delay={0}>
          <h2
            style={{
              fontSize: 72,
              fontWeight: "bold",
              color: "#fff",
              margin: 0,
            }}
          >
            自动跟随音乐节奏
          </h2>
        </FadeInText>

        <FadeInText frame={frame} delay={20}>
          <p
            style={{
              fontSize: 42,
              color: "#8b5cf6",
              marginTop: 30,
              fontWeight: "bold",
            }}
          >
            🎵 智能节拍检测
          </p>
        </FadeInText>

        <FadeInText frame={frame} delay={35}>
          <p
            style={{
              fontSize: 42,
              color: "#8b5cf6",
              marginTop: 20,
              fontWeight: "bold",
            }}
          >
            🎬 动态运镜效果
          </p>
        </FadeInText>

        <FadeInText frame={frame} delay={50}>
          <div
            style={{
              fontSize: 32,
              color: "#10b981",
              marginTop: 40,
              padding: "20px 40px",
              backgroundColor: "rgba(16, 185, 129, 0.1)",
              borderRadius: 15,
              border: "2px solid rgba(16, 185, 129, 0.3)",
            }}
          >
            ✨ 让视频动起来！
          </div>
        </FadeInText>
      </div>
    </AbsoluteFill>
  );
}

/**
 * 场景4: 核心功能
 */
function Scene4_Features({ frame }: { frame: number }) {
  return (
    <AbsoluteFill style={{ backgroundColor: "#0a0a0a" }}>
      <div
        style={{
          position: "absolute",
          width: "100%",
          height: "100%",
          background: "linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%)",
        }}
      />

      {/* 标题 */}
      <FadeInText frame={frame} delay={0}>
        <h2
          style={{
            position: "absolute",
            top: 80,
            left: 0,
            right: 0,
            fontSize: 64,
            fontWeight: "bold",
            color: "#fff",
            textAlign: "center",
            margin: 0,
          }}
        >
          核心功能
        </h2>
      </FadeInText>

      {/* 功能卡片网格 */}
      <div
        style={{
          position: "absolute",
          top: 200,
          left: 0,
          right: 0,
          bottom: 0,
          display: "flex",
          flexWrap: "wrap",
          alignItems: "center",
          justifyContent: "center",
          padding: 40,
        }}
      >
        <FeatureCard
          frame={frame}
          delay={15}
          icon="🎵"
          title="智能节奏检测"
          description="使用 librosa 自动识别音乐节拍点，精准捕捉每一拍"
        />
        <FeatureCard
          frame={frame}
          delay={25}
          icon="🔍"
          title="动态缩放"
          description="在节拍处自动应用缩放效果，区分重拍和弱拍"
        />
        <FeatureCard
          frame={frame}
          delay={35}
          icon="⚡"
          title="批量处理"
          description="一次处理多个视频，节省时间和精力"
        />
        <FeatureCard
          frame={frame}
          delay={45}
          icon="🎨"
          title="高质量渲染"
          description="基于 Remotion 渲染，输出高质量 MP4 视频"
        />
      </div>
    </AbsoluteFill>
  );
}

/**
 * 场景5: 使用场景
 */
function Scene5_UseCases({ frame }: { frame: number }) {
  const useCases = [
    { emoji: "💃", title: "舞蹈视频", color: "#ec4899" },
    { emoji: "🏋️", title: "健身视频", color: "#f59e0b" },
    { emoji: "🎤", title: "音乐视频", color: "#8b5cf6" },
    { emoji: "🎪", title: "表演视频", color: "#10b981" },
  ];

  return (
    <AbsoluteFill style={{ backgroundColor: "#0a0a0a" }}>
      <div
        style={{
          position: "absolute",
          width: "100%",
          height: "100%",
          background: "radial-gradient(circle at center, #1a1a2e 0%, #0a0a0a 100%)",
        }}
      />

      <FadeInText frame={frame} delay={0}>
        <h2
          style={{
            position: "absolute",
            top: 80,
            left: 0,
            right: 0,
            fontSize: 64,
            fontWeight: "bold",
            color: "#fff",
            textAlign: "center",
            margin: 0,
          }}
        >
          适用于多种场景
        </h2>
      </FadeInText>

      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
          display: "flex",
          gap: 40,
          flexWrap: "wrap",
          justifyContent: "center",
          width: "90%",
        }}
      >
        {useCases.map((useCase, index) => {
          const delay = index * 15;
          const scale = spring({
            frame: Math.max(0, frame - delay),
            fps: 30,
            config: { damping: 15, stiffness: 100 },
          });
          const cardScale = interpolate(scale, [0, 1], [0.5, 1]);
          const opacity = interpolate(frame, [delay, delay + 15], [0, 1], {
            extrapolateRight: "clamp",
          });

          return (
            <div
              key={index}
              style={{
                backgroundColor: "rgba(255, 255, 255, 0.1)",
                backdropFilter: "blur(10px)",
                borderRadius: 20,
                padding: "40px 60px",
                textAlign: "center",
                border: `2px solid ${useCase.color}40`,
                scale: cardScale,
                opacity,
              }}
            >
              <div style={{ fontSize: 80, marginBottom: 15 }}>{useCase.emoji}</div>
              <h3
                style={{
                  fontSize: 32,
                  fontWeight: "bold",
                  color: useCase.color,
                  margin: 0,
                }}
              >
                {useCase.title}
              </h3>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
}

/**
 * 场景6: 使用方法
 */
function Scene6_Usage({ frame }: { frame: number }) {
  const codeOpacity = interpolate(frame, [0, 30], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#0a0a0a" }}>
      <div
        style={{
          position: "absolute",
          width: "100%",
          height: "100%",
          background: "linear-gradient(135deg, #0a0a0a 0%, #0f1a2e 100%)",
        }}
      />

      <FadeInText frame={frame} delay={0}>
        <h2
          style={{
            position: "absolute",
            top: 80,
            left: 0,
            right: 0,
            fontSize: 64,
            fontWeight: "bold",
            color: "#fff",
            textAlign: "center",
            margin: 0,
          }}
        >
          简单易用
        </h2>
      </FadeInText>

      {/* 代码示例 */}
      <FadeInText frame={frame} delay={20}>
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: "50%",
            transform: "translate(-50%, -50%)",
            backgroundColor: "#1e1e1e",
            borderRadius: 15,
            padding: 40,
            boxShadow: "0 20px 60px rgba(0, 0, 0, 0.5)",
            border: "2px solid rgba(139, 92, 246, 0.3)",
            opacity: codeOpacity,
          }}
        >
          <pre
            style={{
              fontSize: 24,
              color: "#a5b4fc",
              margin: 0,
              fontFamily: "'Fira Code', monospace",
              lineHeight: 1.8,
            }}
          >
            <code>
              <span style={{ color: "#c084fc" }}>$</span> python rhythm_remotion.py dance.mp4
            </code>
          </pre>

          <div
            style={{
              marginTop: 25,
              padding: "15px 20px",
              backgroundColor: "rgba(16, 185, 129, 0.1)",
              borderRadius: 8,
              border: "1px solid rgba(16, 185, 129, 0.3)",
            }}
          >
            <p
              style={{
                fontSize: 18,
                color: "#10b981",
                margin: 0,
                textAlign: "center",
              }}
            >
              ✅ 一行命令，即刻生成
            </p>
          </div>
        </div>
      </FadeInText>
    </AbsoluteFill>
  );
}

/**
 * 场景7: 结束
 */
function Scene7_Outro({ frame }: { frame: number }) {
  const scale = spring({
    frame,
    fps: 30,
    config: { damping: 15, stiffness: 100 },
  });

  const scaleValue = interpolate(scale, [0, 1], [0.8, 1]);

  const ctaOpacity = interpolate(frame, [30, 60], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#0a0a0a" }}>
      {/* 动态背景 */}
      <div
        style={{
          position: "absolute",
          width: "100%",
          height: "100%",
          background: "radial-gradient(circle at center, #2a1a4e 0%, #0a0a0a 100%)",
        }}
      />

      {/* 装饰圆圈 */}
      {[0, 1, 2].map((i) => {
        const circleScale = scaleValue * (1 + i * 0.2);
        const opacity = interpolate(frame, [0, 30], [0, 0.3], {
          extrapolateRight: "clamp",
        });
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              width: 400 + i * 150,
              height: 400 + i * 150,
              borderRadius: "50%",
              border: "2px solid rgba(139, 92, 246, 0.2)",
              left: "50%",
              top: "50%",
              transform: `translate(-50%, -50%) scale(${circleScale})`,
              opacity,
            }}
          />
        );
      })}

      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "40%",
          transform: "translate(-50%, -50%)",
          textAlign: "center",
          width: "100%",
        }}
      >
        <PulseEffect frame={frame}>
          <h1
            style={{
              fontSize: 88,
              fontWeight: "900",
              margin: 0,
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            Video Rhythm Cam
          </h1>
        </PulseEffect>

        <FadeInText frame={frame} delay={20}>
          <p
            style={{
              fontSize: 42,
              color: "rgba(255, 255, 255, 0.9)",
              marginTop: 30,
            }}
          >
            让你的视频随音乐律动 ✨
          </p>
        </FadeInText>

        <FadeInText frame={frame} delay={40}>
          <p
            style={{
              fontSize: 32,
              color: "#8b5cf6",
              marginTop: 40,
            }}
          >
            GitHub: github.com/remotion-dev
          </p>
        </FadeInText>

        <FadeInText frame={frame} delay={55}>
          <div
            style={{
              marginTop: 50,
              padding: "20px 60px",
              backgroundColor: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              borderRadius: 50,
              display: "inline-block",
              boxShadow: "0 10px 40px rgba(102, 126, 234, 0.4)",
              opacity: ctaOpacity,
            }}
          >
            <span
              style={{
                fontSize: 36,
                fontWeight: "bold",
                color: "#fff",
              }}
            >
              立即体验 🚀
            </span>
          </div>
        </FadeInText>
      </div>
    </AbsoluteFill>
  );
}

// ============================================
// 主组件
// ============================================

/**
 * Video Rhythm Cam 宣传视频主组件
 *
 * 总时长: 30 秒 (900 帧 @ 30fps)
 *
 * 场景分配:
 * - 0-3s: 开场标题
 * - 3-6s: 问题引入
 * - 6-9s: 解决方案
 * - 9-15s: 核心功能
 * - 15-20s: 使用场景
 * - 20-25s: 使用方法
 * - 25-30s: 结束
 */
export const PromoVideo: React.FC = () => {
  return (
    <AbsoluteFill>
      {/* 场景1: 开场标题 (0-3秒 = 0-90帧) */}
      <Sequence from={0} durationInFrames={90}>
        <Scene1_Opening frame={useCurrentFrame()} />
      </Sequence>

      {/* 场景2: 问题引入 (3-6秒 = 90-180帧) */}
      <Sequence from={90} durationInFrames={90}>
        <Scene2_Problem frame={useCurrentFrame()} />
      </Sequence>

      {/* 场景3: 解决方案 (6-9秒 = 180-270帧) */}
      <Sequence from={180} durationInFrames={90}>
        <Scene3_Solution frame={useCurrentFrame()} />
      </Sequence>

      {/* 场景4: 核心功能 (9-15秒 = 270-450帧) */}
      <Sequence from={270} durationInFrames={180}>
        <Scene4_Features frame={useCurrentFrame()} />
      </Sequence>

      {/* 场景5: 使用场景 (15-20秒 = 450-600帧) */}
      <Sequence from={450} durationInFrames={150}>
        <Scene5_UseCases frame={useCurrentFrame()} />
      </Sequence>

      {/* 场景6: 使用方法 (20-25秒 = 600-750帧) */}
      <Sequence from={600} durationInFrames={150}>
        <Scene6_Usage frame={useCurrentFrame()} />
      </Sequence>

      {/* 场景7: 结束 (25-30秒 = 750-900帧) */}
      <Sequence from={750} durationInFrames={150}>
        <Scene7_Outro frame={useCurrentFrame()} />
      </Sequence>
    </AbsoluteFill>
  );
};
