/**
 * FFmpeg 视频处理工具
 * 使用 FFmpeg 为视频添加节奏运镜效果
 */

import { spawn } from 'child_process';
import { promisify } from 'util';
import { writeFile, unlink } from 'fs/promises';
import path from 'path';
import os from 'os';

export interface FFmpegRenderOptions {
  inputPath: string;
  outputPath: string;
  beatsData: {
    beats: Array<{ time: number; strength: number; frame: number }>;
    fps: number;
    duration: number;
  };
  parameters: {
    zoomMin: number;
    zoomMax: number;
    zoomDuration: number;
    quality: number;
  };
  onProgress?: (progress: number) => void;
}

/**
 * 使用 FFmpeg 渲染带节奏运镜效果的视频
 */
export async function renderWithFFmpeg(
  options: FFmpegRenderOptions
): Promise<string> {
  const {
    inputPath,
    outputPath,
    beatsData,
    parameters,
    onProgress,
  } = options;

  return new Promise((resolve, reject) => {
    try {
      // 构建复杂的滤镜表达式，实现基于节拍的缩放效果
      const filterComplex = buildZoomFilter(
        beatsData.beats,
        beatsData.fps,
        parameters
      );

      // FFmpeg 命令参数
      const args = [
        '-i', inputPath,
        '-filter_complex', filterComplex,
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', `${100 - parameters.quality}`, // 质量转换为 CRF
        '-pix_fmt', 'yuv420p',
        '-c:a', 'copy',
        '-y', // 覆盖输出文件
        outputPath,
      ];

      console.log('FFmpeg 命令:', 'ffmpeg', args.join(' '));

      const ffmpeg = spawn('ffmpeg', args);

      let stderr = '';

      // 捕获错误输出用于进度解析
      ffmpeg.stderr.on('data', (data) => {
        stderr += data.toString();

        // 尝试解析进度
        const progressMatch = stderr.match(/frame=\s*(\d+)/);
        if (progressMatch && onProgress) {
          const currentFrame = parseInt(progressMatch[1]);
          const totalFrames = Math.floor(beatsData.duration * beatsData.fps);
          const progress = Math.min((currentFrame / totalFrames) * 100, 100);
          onProgress(progress);
        }
      });

      ffmpeg.on('close', (code) => {
        if (code === 0) {
          resolve(outputPath);
        } else {
          reject(new Error(`FFmpeg 进程退出，代码: ${code}\n${stderr}`));
        }
      });

      ffmpeg.on('error', (err) => {
        reject(new Error(`FFmpeg 执行失败: ${err.message}`));
      });

    } catch (error) {
      reject(error);
    }
  });
}

/**
 * 构建缩放滤镜表达式
 * 根据节拍数据生成动态缩放效果
 */
function buildZoomFilter(
  beats: Array<{ time: number; strength: number; frame: number }>,
  fps: number,
  parameters: { zoomMin: number; zoomMax: number; zoomDuration: number }
): string {
  const zoomFrames = Math.round(parameters.zoomDuration * fps);

  // 为每个节拍创建缩放关键帧
  // 使用 expr 滤镜实现动态缩放
  const zoomExpressions: string[] = [];

  for (let i = 0; i < beats.length; i++) {
    const beat = beats[i];
    const maxZoom = beat.strength > 0.6 ? parameters.zoomMax : 1.15;

    // 为每个节拍创建一个缩放窗口
    const startFrame = beat.frame;
    const endFrame = startFrame + zoomFrames;

    // 构建 if-else 条件表达式
    const condition = `between(T,${startFrame},${endFrame})`;
    const zoomValue = `${maxZoom}-((${maxZoom}-${parameters.zoomMin})*(T-${startFrame})/${zoomFrames})`;

    zoomExpressions.push(`(${condition})?${zoomValue}:1`);
  }

  // 组合所有缩放表达式
  const zoomExpression = zoomExpressions.length > 0
    ? zoomExpressions.join('+')
    : '1';

  // 确保不会超过最大值（处理叠加情况）
  const finalZoomExpr = `min(2.0,${zoomExpression})`;

  // 构建 zoompan 滤镜
  return `[0:v]zoompan=z='${finalZoomExpr}':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080[video]`;
}

/**
 * 使用简化版本：基于时间的缩放
 * 适用于较简单的场景
 */
export async function renderSimpleZoom(
  options: FFmpegRenderOptions
): Promise<string> {
  const {
    inputPath,
    outputPath,
    beatsData,
    parameters,
    onProgress,
  } = options;

  return new Promise((resolve, reject) => {
    try {
      // 计算节拍间隔（秒）
      const beatInterval = beatsData.beats.length > 1
        ? beatsData.beats[1].time - beatsData.beats[0].time
        : 0.5;

      // 简化的缩放表达式
      const zoomExpr = `if(lte(mod(t,${beatInterval}),${parameters.zoomDuration}),${parameters.zoomMax},${parameters.zoomMin})`;

      const args = [
        '-i', inputPath,
        '-vf', `zoompan=z='${zoomExpr}':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'`,
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', `${100 - parameters.quality}`,
        '-pix_fmt', 'yuv420p',
        '-c:a', 'copy',
        '-y',
        outputPath,
      ];

      const ffmpeg = spawn('ffmpeg', args);

      let stderr = '';

      ffmpeg.stderr.on('data', (data) => {
        stderr += data.toString();

        const durationMatch = stderr.match(/Duration:\s+(\d+):(\d+):(\d+\.\d+)/);
        if (durationMatch && onProgress) {
          const timeMatch = stderr.match(/time=\s*(\d+):(\d+):(\d+\.\d+)/);
          if (timeMatch) {
            // 计算进度（简化版）
            onProgress(50); // 占位
          }
        }
      });

      ffmpeg.on('close', (code) => {
        if (code === 0) {
          resolve(outputPath);
        } else {
          reject(new Error(`FFmpeg 失败: ${stderr}`));
        }
      });

      ffmpeg.on('error', (err) => {
        reject(new Error(`FFmpeg 执行失败: ${err.message}`));
      });

    } catch (error) {
      reject(error);
    }
  });
}

/**
 * 检查 FFmpeg 是否可用
 */
export async function checkFFmpegAvailable(): Promise<boolean> {
  return new Promise((resolve) => {
    const ffmpeg = spawn('ffmpeg', ['-version']);
    ffmpeg.on('close', (code) => {
      resolve(code === 0);
    });
    ffmpeg.on('error', () => {
      resolve(false);
    });
  });
}

/**
 * 获取视频信息
 */
export async function getVideoInfo(inputPath: string): Promise<{
  duration: number;
  fps: number;
  width: number;
  height: number;
}> {
  return new Promise((resolve, reject) => {
    const args = [
      '-i', inputPath,
      '-f', 'null',
      '-',
    ];

    const ffmpeg = spawn('ffmpeg', args);
    let stderr = '';

    ffmpeg.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    ffmpeg.on('close', () => {
      try {
        // 解析视频信息
        const durationMatch = stderr.match(/Duration:\s+(\d+):(\d+):(\d+\.\d+)/);
        const fpsMatch = stderr.match(/(\d+(?:\.\d+)?)\s*fps/);
        const resolutionMatch = stderr.match(/(\d+)x(\d+)/);

        if (!durationMatch || !resolutionMatch) {
          reject(new Error('无法解析视频信息'));
          return;
        }

        const duration =
          parseInt(durationMatch[1]) * 3600 +
          parseInt(durationMatch[2]) * 60 +
          parseFloat(durationMatch[3]);

        const fps = fpsMatch ? parseFloat(fpsMatch[1]) : 30;
        const width = parseInt(resolutionMatch[1]);
        const height = parseInt(resolutionMatch[2]);

        resolve({ duration, fps, width, height });
      } catch (error) {
        reject(error);
      }
    });

    ffmpeg.on('error', reject);
  });
}
