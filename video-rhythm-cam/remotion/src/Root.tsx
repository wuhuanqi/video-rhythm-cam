import { Composition } from "remotion";
import { RhythmVideo } from "./RhythmVideo";
import { PromoVideo } from "./PromoVideo";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* 宣传视频 - 30秒 */}
      <Composition
        id="PromoVideo"
        component={PromoVideo}
        durationInFrames={900} // 30 秒 @ 30fps
        fps={30}
        width={1920}
        height={1080}
      />

      {/* 节奏视频 - 根据实际视频时长调整 */}
      <Composition
        id="RhythmVideo"
        component={RhythmVideo}
        durationInFrames={952} // 默认 10 秒 @ 30fps，会根据实际视频调整
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
