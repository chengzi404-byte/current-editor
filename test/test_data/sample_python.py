"""
Python代码示例 - 用于测试语法高亮
"""

import os
import sys
from typing import List, Dict, Optional


def calculate_fibonacci(n: int) -> List[int]:
    """计算斐波那契数列"""
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    
    fib_sequence = [0, 1]
    for i in range(2, n):
        next_num = fib_sequence[i-1] + fib_sequence[i-2]
        fib_sequence.append(next_num)
    
    return fib_sequence


class DataProcessor:
    """数据处理类"""
    
    def __init__(self, data: List[Dict]):
        self.data = data
        self.processed_data = []
    
    async def process_data(self) -> None:
        """异步处理数据"""
        for item in self.data:
            processed_item = await self._process_single_item(item)
            self.processed_data.append(processed_item)
    
    async def _process_single_item(self, item: Dict) -> Dict:
        """处理单个数据项"""
        try:
            # 模拟一些数据处理逻辑
            result = {
                'id': item.get('id', 0),
                'name': item.get('name', 'Unknown').upper(),
                'value': item.get('value', 0) * 2
            }
            return result
        except Exception as e:
            print(f"Error processing item: {e}")
            return {}


# 使用示例
if __name__ == "__main__":
    # 计算斐波那契数列
    fib_numbers = calculate_fibonacci(10)
    print(f"Fibonacci sequence: {fib_numbers}")
    
    # 数据处理示例
    sample_data = [
        {'id': 1, 'name': 'Alice', 'value': 100},
        {'id': 2, 'name': 'Bob', 'value': 200},
        {'id': 3, 'name': 'Charlie', 'value': 300}
    ]
    
    processor = DataProcessor(sample_data)
    
    import asyncio
    asyncio.run(processor.process_data())
    
    print(f"Processed data: {processor.processed_data}")