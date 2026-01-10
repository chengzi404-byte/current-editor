/*
JavaScript代码示例 - 用于测试语法高亮
*/

// 计算斐波那契数列
function calculateFibonacci(n) {
    if (n <= 0) return [];
    if (n === 1) return [0];
    
    const fibSequence = [0, 1];
    for (let i = 2; i < n; i++) {
        const nextNum = fibSequence[i-1] + fibSequence[i-2];
        fibSequence.push(nextNum);
    }
    
    return fibSequence;
}

// 数据处理类
class DataProcessor {
    constructor(data) {
        this.data = data;
        this.processedData = [];
    }
    
    async processData() {
        for (const item of this.data) {
            const processedItem = await this.processSingleItem(item);
            this.processedData.push(processedItem);
        }
    }
    
    async processSingleItem(item) {
        try {
            return {
                id: item.id || 0,
                name: (item.name || 'Unknown').toUpperCase(),
                value: (item.value || 0) * 2
            };
        } catch (error) {
            console.error(`Error processing item: ${error}`);
            return {};
        }
    }
}

// 使用示例
const fibNumbers = calculateFibonacci(10);
console.log(`Fibonacci sequence: ${fibNumbers}`);

const sampleData = [
    { id: 1, name: 'Alice', value: 100 },
    { id: 2, name: 'Bob', value: 200 },
    { id: 3, name: 'Charlie', value: 300 }
];

const processor = new DataProcessor(sampleData);
processor.processData().then(() => {
    console.log(`Processed data: ${JSON.stringify(processor.processedData)}`);
});