import argparse
import json
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent))

from modules.text_analyzer import TextAnalyzer
from modules.video_generator import VideoGenerator
from modules.video_inserter import VideoInserter
from modules.logger import setup_logger
from config.config import Config


def main():
    """主程序入口"""
    parser = argparse.ArgumentParser(description='文本生成视频工具')
    parser.add_argument('--input', '-i', required=True, help='输入文本文件路径')
    parser.add_argument('--output', '-o', default='output', help='输出目录')
    parser.add_argument('--format', '-f', choices=['html', 'markdown'], default='html', help='输出格式')

    args = parser.parse_args()

    # 设置日志
    logger = setup_logger()

    try:
        # 读取输入文本
        with open(args.input, 'r', encoding='utf-8') as f:
            input_text = f.read()

        logger.info(f"开始处理文本文件: {args.input}")

        # 初始化模块
        text_analyzer = TextAnalyzer()
        video_generator = VideoGenerator()
        video_inserter = VideoInserter()

        # 步骤1: 分析文本，提取场景
        logger.info("步骤1: 分析文本，提取场景")
        scenes = text_analyzer.extract_scenes(input_text)
        logger.info(f"提取到 {len(scenes)} 个场景")

        # 保存场景信息
        os.makedirs(args.output, exist_ok=True)
        scenes_file = os.path.join(args.output, 'scenes.json')
        with open(scenes_file, 'w', encoding='utf-8') as f:
            json.dump(scenes, f, ensure_ascii=False, indent=2)

        # 步骤2: 生成视频
        logger.info("步骤2: 生成视频")
        video_results = video_generator.generate_videos(scenes, args.output)

        # 步骤3: 插入视频到原文
        logger.info("步骤3: 插入视频到原文")
        output_content = video_inserter.insert_videos(
            input_text, scenes, video_results, args.format
        )

        # 保存最终结果
        output_ext = 'html' if args.format == 'html' else 'md'
        output_file = os.path.join(args.output, f'result.{output_ext}')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_content)

        logger.info(f"处理完成！结果保存在: {output_file}")

    except Exception as e:
        logger.error(f"处理过程中发生错误: {str(e)}")
        raise


if __name__ == "__main__":
    main()