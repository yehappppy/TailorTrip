# TailorTrip - 智能旅行规划助手

TailorTrip是一个基于LLM的智能旅行规划助手，能够根据用户的需求和偏好，自动生成个性化的旅行建议。

## 主要功能

- 🔍 递归搜索：从用户描述出发，通过递归方式不断细化搜索关键词
- 🌐 信息抽取：从小红书等平台获取真实旅游信息
- 🎯 智能规划：根据搜索结果生成个性化旅行建议
- 🤖 对话交互：支持自然语言交互，理解用户意图

## 快速开始

### 环境要求
- Python 3.12+
- 依赖包：见requirements.txt（懒人安装requirements_solid.txt，钉死版本能运行）
- 额外依赖：`pip install langchain-openai langchain-deepseek`

### 运行说明
1. 复制`config/config.example.yaml`为`config/config.yaml`并填写配置
2. 在项目根目录下运行示例：`python run_sample.py`

## 项目结构

```
TailorTrip/
├── config/                # 配置文件
│   ├── config.yaml       # 环境变量配置
│   └── config.example.yaml
├── src/
│   ├── llm_agent/       # LLM智能代理
│   │   ├── content_generation/  # 内容生成模块
│   │   ├── sample/      # 示例代码
│   │   └── user_intention/  # 用户意图理解
│   ├── tools/           # 工具函数
│   │   ├── crawl.py     # 爬虫工具
│   │   └── retriever.py # 文档检索
│   └── utils/           # 通用工具
│       ├── llm.py       # LLM调用封装
│       └── util.py      # 通用工具函数
└── requirements.txt
```

## 开发状态

### 功能列表
- [x] 基于树结构的递归搜索框架
- [x] 小红书爬虫集成
- [x] 基础的LLM调用封装
- [x] 示例代码和文档
- [ ] 优化搜索策略：先获取宏观攻略，再针对具体地点深入搜索
- [ ] 改进关键词提取：优化prompt和stopping criteria
- [ ] 完善用户意图理解模块
- [ ] 集成RAG检索功能

## 贡献指南

1. 所有代码请在项目根目录下创建entry point
2. 通过package方式调用内部模块
3. 遵循代码注释规范，保持中文注释的一致性
4. 新功能开发请先在`sample`目录下测试

## 关于Elasticsearch和Docker容器

1. 下载 [docker desktop](https://docs.docker.com/get-started/get-docker/)
2. 打开 docker desktop
3. 请把爬虫的测试数据放在 [data/docs](data/docs)路径下
4. 示例：运行 [test_retriever.py](test_retriever.py)
5. 现在就可以正常构建elasticsearch容器和使用elasticsearch服务了