/**
 * Remotion 集成工具
 * 使用 Remotion 进行快速预览渲染
 */

import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs/promises';

export interface RemotionRenderOptions {
  remotionDir: string;
  inputPath: string;
  outputPath: string;
  beatsData: {
    beats: Array<{ time: number; strength: number; frame: number }>;
    bpm: number;
    duration: number;
    fps: number;
  };
  parameters: {
    zoomMin: number;
    zoomMax: number;
    zoomDuration: number;
  };
  quality?: number;
  onProgress?: (progress: number) => void;
}

/**
 * 使用 Remotion 渲染预览视频
 */
export async function renderPreviewWithRemotion(
  options: RemotionRenderOptions
): Promise<string> {
  const {
    remotionDir,
    inputPath,
    outputPath,
    beatsData,
    parameters,
    quality = 70,
    onProgress,
  } = options;

  return new Promise((resolve, reject) => {
    try {
      // 1. 准备 Remotion 项目
      // 复制视频到 Remotion public 目录
      setupRemotionProject(remotionDir, inputPath, beatsData, parameters)
        .then(() => {
          // 2. 执行 Remotion 渲染
          const args = [
            'remotion', 'render',
            'RhythmVideo',
            outputPath,
            '--codec', 'h264',
            '--pixel-format', 'yuv420p',
            '--quality', quality.toString(),
            '--concurrency', '1',
          ];

          console.log('Remotion 命令:', args.join(' '));

          const remotion = spawn('npx', args, {
            cwd: remotionDir,
            stdio: 'inherit',
          });

          remotion.on('close', (code) => {
            if (code === 0) {
              resolve(outputPath);
            } else {
              reject(new Error(`Remotion 渲染失败，退出代码: ${code}`));
            }
          });

          remotion.on('error', (err) => {
            reject(new Error(`Remotion 执行失败: ${err.message}`));
          });
        })
        .catch(reject);

    } catch (error) {
      reject(error);
    }
  });
}

/**
 * 设置 Remotion 项目
 * 复制视频文件并生成节拍数据
 */
async function setupRemotionProject(
  remotionDir: string,
  inputPath: string,
  beatsData: any,
  parameters: any
): Promise<void> {
  try {
    // 1. 创建 public 目录（如果不存在）
    const publicDir = path.join(remotionDir, 'public');
    await fs.mkdir(publicDir, { recursive: true });

    // 2. 复制视频文件
    const targetVideo = path.join(publicDir, 'input.mp4');
    await fs.copyFile(inputPath, targetVideo);

    // 3. 生成节拍数据 JSON
    const beatsJson = JSON.stringify(beatsData, null, 2);
    await fs.writeFile(
      path.join(remotionDir, 'src', 'beats.json'),
      beatsJson
    );

    // 4. 更新 Root.tsx 中的 durationInFrames
    const rootPath = path.join(remotionDir, 'src', 'Root.tsx');
    const rootContent = await fs.readFile(rootPath, 'utf-8');
    const updatedRoot = rootContent.replace(
      /durationInFrames=\$\{(\d+)\}/,
      `durationInFrames={${Math.floor(beatsData.duration * beatsData.fps)}}`
    );
    await fs.writeFile(rootPath, updatedRoot);

    console.log('✅ Remotion 项目设置完成');
  } catch (error) {
    console.error('❌ Remotion 项目设置失败:', error);
    throw error;
  }
}

/**
 * 启动 Remotion Studio（开发模式）
 */
export async function startRemotionStudio(
  remotionDir: string
): Promise<void> {
  return new Promise((resolve, reject) => {
    const remotion = spawn('npx', ['remotion', 'studio'], {
      cwd: remotionDir,
      stdio: 'inherit',
    });

    remotion.on('close', (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(`Remotion Studio 退出，代码: ${code}`));
      }
    });

    remotion.on('error', (err) => {
      reject(new Error(`Remotion Studio 启动失败: ${err.message}`));
    });
  });
}

/**
 * 检查 Remotion 是否安装
 */
export async function checkRemotionAvailable(
  remotionDir: string
): Promise<boolean> {
  try {
    const packageJsonPath = path.join(remotionDir, 'package.json');
    await fs.access(packageJsonPath);
    return true;
  } catch {
    return false;
  }
}
