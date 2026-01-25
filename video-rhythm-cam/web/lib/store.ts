import { create } from 'zustand';

export interface Beat {
  time: number;
  strength: number;
  frame: number;
}

export interface BeatsData {
  bpm: number;
  duration: number;
  fps: number;
  beats: Beat[];
}

export interface VideoInfo {
  filename: string;
  path: string;
  duration: number;
  fps: number;
  size: number;
}

interface RhythmCamStore {
  // 当前视频
  currentVideo: VideoInfo | null;
  setCurrentVideo: (video: VideoInfo | null) => void;

  // 节奏数据
  beatsData: BeatsData | null;
  setBeatsData: (data: BeatsData | null) => void;

  // 参数设置
  parameters: {
    sensitivity: number;
    zoomMin: number;
    zoomMax: number;
    zoomDuration: number;
    quality: number;
  };
  updateParameter: (key: string, value: number) => void;
  resetParameters: () => void;

  // 处理状态
  isProcessing: boolean;
  setProcessing: (processing: boolean) => void;

  // 预览状态
  previewUrl: string | null;
  setPreviewUrl: (url: string | null) => void;

  // 错误信息
  error: string | null;
  setError: (error: string | null) => void;

  // 导出状态
  isExporting: boolean;
  exportProgress: number;
  setExporting: (exporting: boolean, progress?: number) => void;
}

const defaultParameters = {
  sensitivity: 0.5,
  zoomMin: 1.0,
  zoomMax: 1.3,
  zoomDuration: 0.2,
  quality: 90,
};

export const useRhythmCamStore = create<RhythmCamStore>((set) => ({
  // 初始状态
  currentVideo: null,
  setCurrentVideo: (video) => set({ currentVideo: video }),

  beatsData: null,
  setBeatsData: (data) => set({ beatsData: data }),

  parameters: defaultParameters,
  updateParameter: (key, value) =>
    set((state) => ({
      parameters: {
        ...state.parameters,
        [key]: value,
      },
    })),
  resetParameters: () => set({ parameters: defaultParameters }),

  isProcessing: false,
  setProcessing: (processing) => set({ isProcessing: processing }),

  previewUrl: null,
  setPreviewUrl: (url) => set({ previewUrl: url }),

  error: null,
  setError: (error) => set({ error }),

  isExporting: false,
  exportProgress: 0,
  setExporting: (exporting, progress = 0) =>
    set({ isExporting: exporting, exportProgress: progress }),
}));
