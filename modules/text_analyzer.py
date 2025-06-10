# =============================================================================
# modules/text_analyzer.py - 文本分析模块
# =============================================================================

import re
import json
import requests
from typing import List, Dict
from config.config import Config
from modules.logger import setup_logger


class TextAnalyzer:
    """文本分析器，用于从文本中提取场景"""

    def __init__(self):
        self.logger = setup_logger()
        self.api_key = Config.DEEPSEEK_API_KEY
        self.api_url = Config.DEEPSEEK_API_URL

    def extract_scenes(self, text: str) -> List[Dict]:
        """
        从文本中提取场景

        Args:
            text: 输入文本

        Returns:
            场景列表
        """
        try:
            # 如果没有配置API密钥，使用规则提取
            if not self.api_key or self.api_key == "your_deepseek_api_key_here":
                self.logger.warning("未配置DeepSeek API密钥，使用规则提取场景")
                return self._extract_scenes_by_rules(text)

            # 使用DeepSeek API提取场景
            return self._extract_scenes_by_api(text)

        except Exception as e:
            self.logger.error(f"场景提取失败: {str(e)}")
            # 降级到规则提取
            return self._extract_scenes_by_rules(text)

    def _extract_scenes_by_api(self, text: str) -> List[Dict]:
        """使用DeepSeek API提取场景"""

        system_prompt = """
        你是一个专业的场景提取助手。请从给定的文本中提取适合制作视频的场景。

        要求：
        1. 提取具有视觉表现力的场景
        2. 每个场景应该包含具体的动作、人物或事物
        3. 场景描述要简洁明了，适合作为视频生成的提示词
        4. 返回JSON格式，包含以下字段：
           - id: 场景唯一标识符
           - prompt: 场景描述提示词
           - position: 场景在原文中的大致位置（句子序号）
           - duration: 建议视频时长（秒）
           - style: 视频风格（realistic/cartoon/animation）
           - type: 场景类型（narrative/technical）

        示例输出：
        [
            {
                "id": "scene_001",
                "prompt": "林则徐站在虎门海滩上，身着清朝官服，表情严肃",
                "position": 1,
                "duration": 5,
                "style": "realistic",
                "type": "narrative"
            }
        ]
        """

        user_prompt = f"请从以下文本中提取场景：\n\n{text}"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }

        response = requests.post(self.api_url, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()
        content = result["choices"][0]["message"]["content"]

        # 解析JSON
        try:
            scenes = json.loads(content)
            return self._validate_scenes(scenes)
        except json.JSONDecodeError:
            self.logger.error("API返回的内容不是有效的JSON格式")
            return self._extract_scenes_by_rules(text)

    def _extract_scenes_by_rules(self, text: str) -> List[Dict]:
        """使用规则提取场景"""

        scenes = []
        sentences = re.split(r'[。！？；]', text)

        scene_id = 1
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue

            # 简单的关键词匹配来识别可视化场景
            visual_keywords = [
                '站在', '走向', '搬运', '倒入', '发生', '产生', '销毁',
                '建造', '实验', '反应', '展示', '演示', '操作'
            ]

            if any(keyword in sentence for keyword in visual_keywords):
                scene = {
                    "id": f"scene_{scene_id:03d}",
                    "prompt": sentence,
                    "position": i + 1,
                    "duration": 5,
                    "style": "realistic",
                    "type": "narrative"
                }
                scenes.append(scene)
                scene_id += 1

        return scenes

    def _validate_scenes(self, scenes: List[Dict]) -> List[Dict]:
        """验证场景数据的有效性"""

        validated_scenes = []
        required_fields = ["id", "prompt", "position", "duration", "style", "type"]

        for scene in scenes:
            if not isinstance(scene, dict):
                continue

            # 检查必需字段
            if not all(field in scene for field in required_fields):
                self.logger.warning(f"场景缺少必需字段: {scene}")
                continue

            # 设置默认值
            scene.setdefault("resolution", "1920x1080")
            scene.setdefault("fps", 30)

            validated_scenes.append(scene)

        return validated_scenes