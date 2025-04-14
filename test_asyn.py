import asyncio

class MyAsyncClass:
    async def async_method(self, value):
        print(f"开始处理: {value}")
        await asyncio.sleep(3)  # 模拟耗时操作
        print(f"完成处理: {value}")
        return value * 2

async def main():
    my_instance = MyAsyncClass()

    # 启动多个异步任务
    task1 = asyncio.create_task(my_instance.async_method(1))
    task2 = asyncio.create_task(my_instance.async_method(2))
    task3 = asyncio.create_task(my_instance.async_method(3))

    print("所有任务已启动，继续执行其他操作...")

    # 等待所有任务完成
    results = await asyncio.gather(task1, task2, task3)
    print(f"所有任务结果: {results}")

if __name__ == "__main__":
    asyncio.run(main())