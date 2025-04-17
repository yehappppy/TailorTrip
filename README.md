# TailorTrip项目代码
- requirements.txt: 依赖包安装（python3.12+）
- 还要pip install: langchain-openai, langchain-deepseek
- 由于python引用的特性，需要运行代码请在最外层目录下写entry point，通过package调用内部层级的代码进行运行

## 目录结构
- config: 存放着配置文件
    - *使用yaml来在各个代码文件间共享环境变量*
- data: 数据文件夹
- interface：存放前端界面文件
- src: 源代码文件夹
    - llm_agent: 
        - *agent本身存放的文件夹，每个agent来执行一个特定的任务*
        - prompt：用来存放各个agent的system prompt
        - sample_chatbot：写了一些如何调用llm的示例代码（cot，toolcall, streaming）
        - user_intention（to be filled）：读取user的意图，修正query并返回扩充后的回答和flag
    - rag db:
        - *rag数据库存放的文件夹，用于存储和检索文档*
    - tools:
        - *llm tool存放的文件夹，用于存放和管理工具*
        - retrieve（to be filled）：通过rag获取文档
        - crawl（to be filled）：通过爬虫获取相关帖子信息
    - utils:
        - *共用工具代码存放的文件夹*
        - llm：调用llm通过这里进行即可
        - util：存放一些共用的工具代码，例如导入config，logging等等
- run_sample.py: 运行示例代码的entry_point

