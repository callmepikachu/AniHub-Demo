# AniHub-Demo
泛动画知识平台
"""
文本生成视频项目 - 主要代码文件
项目结构：
text_to_video/
├── main.py
├── modules/
│   ├── __init__.py
│   ├── text_analyzer.py
│   ├── video_generator.py

│   ├── video_inserter.py
│   └── logger.py
├── config/
│   └── config.py
├── output/
├── logs/
└── requirements.txt
"""


# =============================================================================
# 使用说明和示例
# =============================================================================

"""
使用方法：

1. 安装依赖：
   pip install -r requirements.txt

2. 配置API密钥（可选）：
   编辑 config/config.py 文件，填入您的API密钥

3. 准备输入文本文件：
   创建一个txt文件，包含要处理的文本内容

4. 运行程序：
   python main.py -i test/input.txt -o output -f html

5. 查看结果：
   在output目录中查看生成的HTML文件和视频文件

示例输入文本 (input.txt)：
1839年，林则徐在虎门海滩销毁鸦片。首先，人们将装满鸦片的木桶搬运至销烟池旁。接着，石灰被倒入池中，与鸦片发生化学反应，产生大量浓烟。最终，鸦片被彻底销毁。

程序特点：
1. 模块化设计，易于扩展
2. 支持多种视频生成方式（API/本地工具/模拟）
3. 完整的错误处理和日志记录
4. 支持HTML和Markdown输出格式
5. 可以在没有API密钥的情况下运行（使用模拟模式）

注意事项：
1. 首次运行会使用模拟视频生成
2. 要使用真实的API服务，需要配置相应的API密钥
3. Manim集成需要额外的环境配置
4. 视频文件需要与HTML文件放在同一目录下才能正常播放
"""


python版本需要多少才合适?