# =============================================================================
# modules/video_inserter.py - 视频插入模块
# =============================================================================

import re
import os
from typing import List, Dict
from modules.logger import setup_logger


class VideoInserter:
    """视频插入器，将生成的视频插入到原文中"""

    def __init__(self):
        self.logger = setup_logger()

    def insert_videos(self, original_text: str, scenes: List[Dict],
                      video_results: Dict[str, Dict], output_format: str = "html") -> str:
        """
        将视频插入到原文中

        Args:
            original_text: 原始文本
            scenes: 场景列表
            video_results: 视频生成结果
            output_format: 输出格式 (html/markdown)

        Returns:
            包含视频的最终内容
        """

        try:
            if output_format == "html":
                return self._insert_videos_html(original_text, scenes, video_results)
            elif output_format == "markdown":
                return self._insert_videos_markdown(original_text, scenes, video_results)
            else:
                raise ValueError(f"不支持的输出格式: {output_format}")

        except Exception as e:
            self.logger.error(f"视频插入失败: {str(e)}")
            return original_text

    def _insert_videos_html(self, original_text: str, scenes: List[Dict],
                            video_results: Dict[str, Dict]) -> str:
        """插入视频到HTML格式"""

        # 将文本分割成句子
        sentences = re.split(r'([。！？；])', original_text)
        sentences = [s for s in sentences if s.strip()]

        # 重新组合句子，保持标点符号
        reconstructed_sentences = []
        for i in range(0, len(sentences), 2):
            if i + 1 < len(sentences):
                reconstructed_sentences.append(sentences[i] + sentences[i + 1])
            else:
                reconstructed_sentences.append(sentences[i])

        # 创建HTML内容
        html_parts = []
        html_parts.append("""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>文本配视频内容</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }
        .content { max-width: 800px; margin: 0 auto; }
        .text-section { margin: 20px 0; font-size: 16px; }
        .video-section { margin: 30px 0; text-align: center; }
        video { max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        .video-caption { margin-top: 10px; font-size: 14px; color: #666; font-style: italic; }
    </style>
</head>
<body>
    <div class="content">
        """)

        # 按位置排序场景
        scenes_by_position = {scene["position"]: scene for scene in scenes}

        # 插入文本和视频
        for i, sentence in enumerate(reconstructed_sentences, 1):
            # 添加文本段落
            html_parts.append(f'        <div class="text-section">{sentence.strip()}</div>')

            # 检查是否有对应位置的视频
            if i in scenes_by_position:
                scene = scenes_by_position[i]
                scene_id = scene["id"]

                if scene_id in video_results:
                    result = video_results[scene_id]
                    if result["status"] == "success" and result["video_path"]:
                        video_filename = os.path.basename(result["video_path"])

                        html_parts.append(f"""
        <div class="video-section">
            <video controls>
                <source src="{video_filename}" type="video/mp4">
                您的浏览器不支持视频播放。
            </video>
            <div class="video-caption">场景: {scene["prompt"]}</div>
        </div>""")

        html_parts.append("""
    </div>
</body>
</html>""")

        return "\n".join(html_parts)

    def _insert_videos_markdown(self, original_text: str, scenes: List[Dict],
                                video_results: Dict[str, Dict]) -> str:
        """插入视频到Markdown格式"""

        # 将文本分割成句子
        sentences = re.split(r'([。！？；])', original_text)
        sentences = [s for s in sentences if s.strip()]

        # 重新组合句子
        reconstructed_sentences = []
        for i in range(0, len(sentences), 2):
            if i + 1 < len(sentences):
                reconstructed_sentences.append(sentences[i] + sentences[i + 1])
            else:
                reconstructed_sentences.append(sentences[i])

        # 创建Markdown内容
        md_parts = []
        md_parts.append("# 文本配视频内容\n")

        # 按位置排序场景
        scenes_by_position = {scene["position"]: scene for scene in scenes}

        # 插入文本和视频
        for i, sentence in enumerate(reconstructed_sentences, 1):
            # 添加文本段落
            md_parts.append(f"{sentence.strip()}\n")

            # 检查是否有对应位置的视频
            if i in scenes_by_position:
                scene = scenes_by_position[i]
                scene_id = scene["id"]

                if scene_id in video_results:
                    result = video_results[scene_id]
                    if result["status"] == "success" and result["video_path"]:
                        video_filename = os.path.basename(result["video_path"])

                        md_parts.append(f"""
<video controls width="100%">
  <source src="{video_filename}" type="video/mp4">
  您的浏览器不支持视频播放。
</video>

*场景: {scene["prompt"]}*

""")

        return "\n".join(md_parts)