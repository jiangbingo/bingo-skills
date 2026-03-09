# Complexity Mapper

代码复杂度分析工具，帮助识别需要重构的代码区域。

## 功能特性

- 📊 **多语言支持**: 支持 Python (radon) 和多语言 (lizard)
- 🎯 **圈复杂度分析**: 测量代码路径和决策点数量
- 🔥 **风险识别**: 识别高复杂度和高风险代码区域
- 📈 **可视化报告**: 生成带有复杂度热图的报告
- 🏆 **排名系统**: 按复杂度对函数和文件进行排名
- 💡 **重构建议**: 提供基于复杂度的重构优先级建议

## 使用场景

### 分析代码复杂度
```
"分析代码复杂度"
"Analyze code complexity"
"检查代码复杂度"
```

### 查找需要重构的代码
```
"哪些文件需要重构"
"Show me refactoring priorities"
"找出最复杂的函数"
```

### 生成复杂度热图
```
"生成复杂度热图"
"Complexity heatmap"
```

## 使用方法

### 1. 安装分析工具

#### Python 项目 (推荐 radon)
```bash
pip install radon
```

#### 多语言项目 (推荐 lizard)
```bash
pip install lizard
```

### 2. 运行分析

```bash
python3 skillsets/complexity-mapper/impl.py
```

### 3. 查看报告

生成的报告将保存为 `complexity_map_report.txt`

## 输出报告说明

报告包含以下部分：

### 📈 总体统计
- 分析函数总数
- 平均复杂度
- 最高复杂度

### 🎯 风险等级分布
- 🟢 低风险 (CC < 15)
- 🟡 中风险 (CC 15-25)
- 🟠 高风险 (CC 25-50)
- 🔴 紧急风险 (CC > 50)

### 🔝 最复杂函数
按复杂度排名的函数列表，显示：
- 复杂度分数
- 文件路径
- 类名和方法名

### 📁 文件复杂度排名
按平均复杂度排序的文件列表

### 💡 改进建议
- 紧急/重要/建议级别的函数数量
- 重构优先级列表

## 复杂度指标说明

### 圈复杂度 (Cyclomatic Complexity)

圈复杂度衡量代码中的独立路径数量。每增加一个决策点（if、for、while、case等），复杂度加1。

| 复杂度范围 | 风险级别 | 说明 |
|-----------|---------|------|
| 1-10 | 低风险 | 代码简单，易于理解和测试 |
| 11-20 | 中风险 | 代码中等复杂，需要关注 |
| 21-50 | 高风险 | 代码复杂，难以测试和维护 |
| 50+ | 紧急风险 | 代码极其复杂，必须重构 |

### 重构建议阈值

- **函数 CC > 15**: 考虑拆分函数
- **函数 CC > 25**: 应该拆分函数
- **函数 CC > 50**: 必须拆分函数
- **文件平均 CC > 20**: 文件需要重组
- **嵌套深度 > 4**: 减少嵌套层级

## 常见问题

**Q: 复杂度和代码行数有关系吗？**
A: 不一定。短代码也可以很复杂（多个嵌套条件），长代码也可能很简单（顺序执行）。

**Q: 什么样的复杂度是可接受的？**
A: 一般建议：
- 简单工具函数：CC < 10
- 业务逻辑函数：CC < 20
- 复杂算法：CC < 50

**Q: 如何降低代码复杂度？**
A: 常用方法：
1. 提取方法：将大函数拆分为小函数
2. 减少嵌套：使用早返回和卫语句
3. 策略模式：用多态替换复杂条件
4. 状态机：简化复杂状态管理

**Q: 100% 的低复杂度代码好吗？**
A: 过度追求低复杂度可能导致代码碎片化。关键是保持合理的复杂度水平。

**Q: 支持哪些编程语言？**
A: 
- radon: Python
- lizard: Python, C/C++, Java, JavaScript, Go, 等多种语言

## 重构策略

### 1. 提取方法 (Extract Method)

**重构前** (高复杂度):
```python
def process_order(order):
    if order.status == 'pending':
        if order.payment:
            if order.inventory:
                # 处理订单
                pass
```

**重构后** (低复杂度):
```python
def process_order(order):
    if order.status != 'pending':
        return
    if not can_process_payment(order):
        return
    if not has_inventory(order):
        return
    ship_order(order)
```

### 2. 卫语句 (Guard Clauses)

**重构前**:
```python
def calculate_discount(customer, order):
    if customer is not None:
        if order is not None:
            if customer.is_vip:
                return 0.2
            else:
                return 0.1
```

**重构后**:
```python
def calculate_discount(customer, order):
    if customer is None:
        return 0
    if order is None:
        return 0
    return 0.2 if customer.is_vip else 0.1
```

### 3. 策略模式

**重构前**:
```python
def calculate_shipping(order):
    if order.type == 'standard':
        return 5
    elif order.type == 'express':
        return 15
    elif order.type == 'overnight':
        return 30
    # 更多条件...
```

**重构后**:
```python
class ShippingStrategy:
    def get_cost(self, order):
        raise NotImplementedError

class StandardShipping(ShippingStrategy):
    def get_cost(self, order):
        return 5

# 使用策略
def calculate_shipping(order):
    strategy = strategies.get(order.type)
    return strategy.get_cost(order)
```

## 示例输出

```
================================================================================
📊 代码复杂度分析报告 (Code Complexity Analysis)
⏰ 分析时间: 2025-01-30 15:00:00
🔧 分析工具: RADON
================================================================================

📈 总体统计
--------------------------------------------------------------------------------
分析函数总数: 156
平均复杂度: 8.45
最高复杂度: 87

🎯 风险等级分布
--------------------------------------------------------------------------------
🟢 低风险 (CC < 15): 120 个函数
🟡 中风险 (CC 15-25): 25 个函数
🟠 高风险 (CC 25-50): 9 个函数
🔴 紧急风险 (CC > 50): 2 个函数

🔴 紧急风险函数 (CC > 50)
--------------------------------------------------------------------------------
  [████████████████████] 87 src/utils/parser.py:Parser.parse_expression
  [██████████████░░░░░░] 56 src/services/auth.py:Auth.validate_user

🔝 Top 20 最复杂函数
--------------------------------------------------------------------------------
1. [████████████████████] 🔴
     src/utils/parser.py:Parser.parse_expression

2. [██████████████░░░░░░] 🔴
     src/services/auth.py:Auth.validate_user
...
```

## 最佳实践

1. **定期分析**: 在代码审查前运行复杂度分析
2. **设置阈值**: 为项目设置最大复杂度限制
3. **增量改进**: 每次重构时选择 1-2 个高复杂度函数
4. **自动化检查**: 将复杂度检查集成到 CI/CD
5. **团队约定**: 团队内部约定可接受的复杂度标准

## 下一步

1. 查看 `complexity_map_report.txt` 获取详细分析
2. 从高复杂度函数开始重构
3. 定期运行分析以跟踪复杂度变化
4. 将复杂度检查集成到开发工作流

## License

MIT
