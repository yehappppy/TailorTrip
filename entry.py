from src.llm_agent import generate_travel_plan
import time

start_time = time.time()
result = generate_travel_plan("我想在铜锣湾找个餐厅吃晚饭",max_depth=3)
end_time = time.time()
print(f"\n>>> This is the tree json, generated in {end_time-start_time:.2f} seconds:\n")
print(result["tree"])
print("\n>>> This is the final response:\n")
print(result["content"])