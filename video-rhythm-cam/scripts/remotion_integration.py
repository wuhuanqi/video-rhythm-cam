#!/usr/bin/env python3
"""
Remotion 集成工具
负责 Remotion 项目的设置、渲染和管理
"""

import os
import json
import subprocess
import shutil
from typing import Dict, Any, Optional
from pathlib import Path


class RemotionIntegration:
    """Remotion 集成管理器"""

    def __init__(self, remotion_dir: str):
        """
        初始化 Remotion 集成管理器

        Args:
            remotion_dir: Remotion 项目目录路径
        """
        self.remotion_dir = Path(remotion_dir)
        self.public_dir = self.remotion_dir / "public"
        self.videos_dir = self.public_dir / "videos"
        self.src_dir = self.remotion_dir / "src"

    def setup_remotion_project(
        self,
        video_path: str,
        beats_data: Dict[str, Any],
        video_name: str = "input.mp4"
    ) -> bool:
        """
        设置 Remotion 项目环境

        Args:
            video_path: 视频文件路径
            beats_data: 节拍数据（JSON 格式）
            video_name: 目标视频文件名

        Returns:
            是否成功
        """
        try:
            # 确保必要的目录存在
            self.videos_dir.mkdir(parents=True, exist_ok=True)

            # 1. 复制视频到 public/videos/
            target_video = self.videos_dir / video_name
            print(f"📹 复制视频到: {target_video}")
            shutil.copy2(video_path, target_video)

            # 2. 写入节拍数据到 public/beats.json
            beats_json = self.public_dir / "beats.json"
            print(f"💾 保存节拍数据到: {beats_json}")
            with open(beats_json, 'w', encoding='utf-8') as f:
                json.dump(beats_data, f, indent=2, ensure_ascii=False)

            # 3. 更新 Root.tsx 以加载正确的视频时长
            self._update_root_composition(beats_data)

            print("✅ Remotion 项目设置完成")
            return True

        except Exception as e:
            print(f"❌ 设置 Remotion 项目失败: {e}")
            return False

    def _update_root_composition(self, beats_data: Dict[str, Any]) -> None:
        """
        更新 Root.tsx 中的视频时长设置

        Args:
            beats_data: 节拍数据
        """
        duration = beats_data.get("duration", 30)
        fps = beats_data.get("fps", 30)
        total_frames = int(duration * fps)

        root_tsx = self.src_dir / "Root.tsx"

        try:
            with open(root_tsx, 'r', encoding='utf-8') as f:
                content = f.read()

            # 替换 durationInFrames
            import re
            content = re.sub(
                r'durationInFrames=\{\d+\}',
                f'durationInFrames={{${total_frames}}}',
                content
            )

            with open(root_tsx, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"✅ 更新视频时长: {duration}秒 ({total_frames}帧 @ {fps}fps)")

        except Exception as e:
            print(f"⚠️  更新 Root.tsx 失败: {e}")

    def render_video(
        self,
        output_path: str,
        composition: str = "RhythmVideo",
        codec: str = "h264",
        pixel_format: str = "yuv420p",
        quality: int = 90,
        concurrency: int = 1,
        progress_callback = None
    ) -> bool:
        """
        使用 Remotion CLI 渲染视频

        Args:
            output_path: 输出视频路径
            composition: 组合名称
            codec: 视频编解码器
            pixel_format: 像素格式
            quality: 画质 (1-100)
            concurrency: 并发渲染实例数
            progress_callback: 进度回调函数(progress: int)

        Returns:
            是否成功
        """
        try:
            print("🎬 开始渲染视频...")

            # 构建命令
            cmd = [
                "npx", "remotion", "render",
                composition,
                "--output", output_path,
                "--codec", codec,
                "--pixel-format", pixel_format,
                "--jpeg-quality", str(quality),
                "--concurrency", str(concurrency),
                "--overwrite"
            ]

            print(f"🔧 执行命令: {' '.join(cmd)}")

            # 运行命令，实时捕获输出
            process = subprocess.Popen(
                cmd,
                cwd=self.remotion_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # 实时读取输出并解析进度
            for line in process.stdout:
                line = line.strip()
                if line:
                    print(line)  # 打印原始输出

                    # 解析 Remotion 的进度输出
                    # Remotion 输出格式: "[123/300] 41%"
                    if "[" in line and "%" in line:
                        try:
                            # 提取百分比
                            percent_str = line.split("%")[0].split()[-1]
                            progress = int(float(percent_str))

                            if progress_callback:
                                progress_callback(progress)
                        except (ValueError, IndexError):
                            pass

            # 等待进程结束
            returncode = process.wait()

            if returncode == 0:
                print("✅ 视频渲染成功")
                return True
            else:
                print(f"❌ 视频渲染失败 (返回码: {returncode})")
                return False

        except Exception as e:
            print(f"❌ 渲染视频时出错: {e}")
            return False

    def install_dependencies(self) -> bool:
        """
        安装 Remotion 项目依赖

        Returns:
            是否成功
        """
        try:
            print("📦 安装 Remotion 依赖...")
            package_json = self.remotion_dir / "package.json"

            if not package_json.exists():
                print("❌ package.json 不存在")
                return False

            # 运行 npm install
            result = subprocess.run(
                ["npm", "install"],
                cwd=self.remotion_dir,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print("✅ 依赖安装成功")
                return True
            else:
                print(f"❌ 依赖安装失败")
                print(f"stderr: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ 安装依赖时出错: {e}")
            return False

    def cleanup(self) -> None:
        """清理临时文件"""
        try:
            # 清理 public/videos/
            if self.videos_dir.exists():
                shutil.rmtree(self.videos_dir)
                print("🧹 清理临时视频文件")

            # 清理 public/beats.json
            beats_json = self.public_dir / "beats.json"
            if beats_json.exists():
                beats_json.unlink()
                print("🧹 清理节拍数据文件")

        except Exception as e:
            print(f"⚠️  清理临时文件时出错: {e}")

    def check_dependencies(self) -> bool:
        """
        检查 Remotion 依赖是否已安装

        Returns:
            是否已安装
        """
        node_modules = self.remotion_dir / "node_modules"
        return node_modules.exists()
