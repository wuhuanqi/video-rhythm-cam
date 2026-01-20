import { Composition } from "remotion";
import { RhythmVideo } from "./RhythmVideo";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="RhythmVideo"
        component={RhythmVideo}
        durationInFrames={$952} // 默认 10 秒 @ 30fps，会根据实际视频调整
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
