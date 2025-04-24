from src.llm_agent import recursive_searching

result = recursive_searching("我想在铜锣湾找个餐厅吃晚饭",max_depth=3)
print("\n>>> This is the tree json:\n")
print(result["tree"])
print("\n>>> This is the final response:\n")
print(result["content"])