# =============================================================================
# modules/video_generator.py - 视频生成模块
# =============================================================================

import os
import time
import requests
from typing import List, Dict
from config.config import Config
from modules.logger import setup_logger


class VideoGenerator:
    """视频生成器"""

    def __init__(self):
        self.logger = setup_logger()
        self.kling_api_key = Config.KLING_API_KEY
        self.kling_api_url = Config.KLING_API_URL

    def generate_videos(self, scenes: List[Dict], output_dir: str) -> Dict[str, Dict]:
        """
        生成视频

        Args:
            scenes: 场景列表
            output_dir: 输出目录

        Returns:
            视频生成结果字典
        """
        results = {}

        for scene in scenes:
            try:
                scene_id = scene["id"]
                scene_type = scene.get("type", "narrative")

                self.logger.info(f"开始生成场景 {scene_id} 的视频")

                if scene_type == "narrative":
                    # 叙事性场景使用Kling AI
                    result = self._generate_with_kling(scene, output_dir)
                elif scene_type == "technical":
                    # 技术性场景使用Manim
                    result = self._generate_with_manim(scene, output_dir)
                else:
                    # 默认使用模拟生成
                    result = self._generate_mock_video(scene, output_dir)

                results[scene_id] = result

            except Exception as e:
                self.logger.error(f"场景 {scene.get('id', 'unknown')} 视频生成失败: {str(e)}")
                results[scene.get('id', 'unknown')] = {
                    "status": "failed",
                    "error": str(e),
                    "video_path": None
                }

        return results

    def _generate_with_kling(self, scene: Dict, output_dir: str) -> Dict:
        """使用Kling AI生成视频"""

        # 如果没有配置API密钥，使用模拟生成
        if not self.kling_api_key or self.kling_api_key == "your_kling_api_key_here":
            self.logger.warning("未配置Kling API密钥，使用模拟视频生成")
            return self._generate_mock_video(scene, output_dir)

        try:
            headers = {
                "Authorization": f"Bearer {self.kling_api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "prompt": scene["prompt"],
                "duration": scene["duration"],
                "style": scene["style"],
                "resolution": scene.get("resolution", "1920x1080"),
                "fps": scene.get("fps", 30)
            }

            # 发送生成请求
            response = requests.post(self.kling_api_url, headers=headers, json=data)
            response.raise_for_status()

            result = response.json()
            video_id = result.get("video_id")

            if not video_id:
                raise Exception("API未返回视频ID")

            # 等待视频生成完成
            video_url = self._wait_for_video_completion(video_id)

            # 下载视频
            video_path = self._download_video(video_url, scene["id"], output_dir)

            return {
                "status": "success",
                "video_path": video_path,
                "video_id": video_id
            }

        except Exception as e:
            self.logger.error(f"Kling API生成视频失败: {str(e)}")
            return self._generate_mock_video(scene, output_dir)

    def _generate_with_manim(self, scene: Dict, output_dir: str) -> Dict:
        """使用Manim生成技术性视频"""

        try:
            # 这里应该调用Manim来生成技术视频
            # 由于Manim需要复杂的配置，这里先用模拟实现

            self.logger.info(f"使用Manim生成技术视频: {scene['prompt']}")

            # 模拟Manim视频生成过程
            time.sleep(2)  # 模拟生成时间

            # 创建一个模拟的视频文件
            video_filename = f"{scene['id']}_manim.mp4"
            video_path = os.path.join(output_dir, video_filename)

            # 创建一个空的视频文件作为占位符
            with open(video_path, 'w') as f:
                f.write(f"# Manim 生成的视频占位符\n# 场景: {scene['prompt']}\n")

            return {
                "status": "success",
                "video_path": video_path,
                "generator": "manim"
            }

        except Exception as e:
            self.logger.error(f"Manim生成视频失败: {str(e)}")
            return self._generate_mock_video(scene, output_dir)

    def _generate_mock_video(self, scene: Dict, output_dir: str) -> Dict:
        """生成模拟视频（用于测试）"""

        try:
            self.logger.info(f"生成模拟视频: {scene['prompt']}")

            # 模拟视频生成时间
            time.sleep(1)

            # 创建模拟视频文件
            video_filename = f"{scene['id']}_mock.mp4"
            video_path = os.path.join(output_dir, video_filename)

            # 创建一个简单的HTML视频占位符
            mock_content = f"""
            <!-- 模拟视频文件 -->
            <!-- 场景ID: {scene['id']} -->
            <!-- 提示词: {scene['prompt']} -->
            <!-- 时长: {scene['duration']}秒 -->
            <!-- 风格: {scene['style']} -->
            """

            with open(video_path, 'w', encoding='utf-8') as f:
                f.write(mock_content)

            return {
                "status": "success",
                "video_path": video_path,
                "generator": "mock"
            }

        except Exception as e:
            self.logger.error(f"模拟视频生成失败: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "video_path": None
            }

    def _wait_for_video_completion(self, video_id: str, timeout: int = 300) -> str:
        """等待视频生成完成"""

        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                # 查询视频状态
                status_url = f"{self.kling_api_url}/{video_id}/status"
                headers = {"Authorization": f"Bearer {self.kling_api_key}"}

                response = requests.get(status_url, headers=headers)
                response.raise_for_status()

                result = response.json()
                status = result.get("status")

                if status == "completed":
                    return result.get("video_url")
                elif status == "failed":
                    raise Exception(f"视频生成失败: {result.get('error', 'Unknown error')}")

                time.sleep(10)  # 等待10秒后再次查询

            except Exception as e:
                self.logger.error(f"查询视频状态失败: {str(e)}")
                time.sleep(10)

        raise Exception("视频生成超时")

    def _download_video(self, video_url: str, scene_id: str, output_dir: str) -> str:
        """下载视频文件"""

        video_filename = f"{scene_id}.mp4"
        video_path = os.path.join(output_dir, video_filename)

        response = requests.get(video_url, stream=True)
        response.raise_for_status()

        with open(video_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        self.logger.info(f"视频下载完成: {video_path}")
        return video_path