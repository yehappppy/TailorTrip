import asyncio
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.tools.amap import AmapTools

async def main():
    try:
        # 1. 初始化 MCP
        amap = AmapTools(url="https://mcp.amap.com/sse?key=9844bb9e68e07657eb1222cf6e26f3ed")
        await amap.connect_server()
        await amap.setup_tools()

        # 2. 配置 LLM
        llm = ChatOpenAI(
            model="Qwen/QwQ-32B",
            base_url="https://api.siliconflow.cn/v1/",
            api_key="sk-rkaaajuldwebwppljkefybgzhtoslzjaukylvnivrzanbhjk"
        )
        
        # 3. 创建 prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个集成了高德地图服务的助手"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # 4. 创建 Agent
        agent = AgentExecutor.from_agent_and_tools(
            agent=create_tool_calling_agent(llm, amap.tools, prompt),
            tools=amap.tools
        )
        
        # 5. 执行查询
        result = await agent.ainvoke({"input": "查询北京今天的天气"})
        print(result)
        
    finally:
        # 6. 确保断开连接
        if 'amap' in locals():
            try:
                await amap.disconnect()
            except Exception as e:
                print(f"关闭连接时出错: {e}")

if __name__ == "__main__":
    asyncio.run(main())