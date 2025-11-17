# 双升AI - 纯启发式策略版本

本项目已移除所有PyTorch机器学习相关代码，现在使用**纯启发式规则**进行决策。

## 项目结构

### 核心文件
- **mvGen.py** - 出牌策略生成器（启发式算法）
  - `gen_single_new()` - 单张出牌策略
  - `gen_pair_new()` - 对子出牌策略
  - `gen_tractor()` - 拖拉机出牌策略
  - `gen_throw()` - 甩牌策略
  - `gen_one_action()` - 首家出牌策略
  - `cover_Pub()` - 埋牌策略

- **myutils.py** - 工具函数库
  - `call_Snatch()` - 报/反决策
  - `evaluate_score()` - 手牌评分
  - `checkPokerType()` - 牌型识别
  - 其他辅助函数

- **env.py** - 游戏环境模拟

- **__main__.py** - 推理入口（纯启发式版本）

## 依赖

```bash
pip install numpy
```

**注意**：不再需要PyTorch！

## 使用方法

### 离线模式
将输入JSON放在 `input/log_forAI.json`，然后运行：

```bash
python __main__.py
```

输出JSON格式：
```json
{
    "response": [...]
}
```

### 在线模式
设置环境变量 `USER=root`，通过标准输入传入JSON：

```bash
export USER=root
echo '{"requests": [...], "responses": [...]}' | python __main__.py
```

## 输入格式

```json
{
    "requests": [
        {
            "stage": "deal",           // 阶段：deal/cover/play
            "deliver": [107],          // 发牌
            "global": {
                "level": "2",
                "banking": {
                    "called": -1,
                    "snatched": -1,
                    "major": "",
                    "banker": -1
                }
            },
            "playerpos": 3
        },
        ...
    ],
    "responses": [...]
}
```

### 三个阶段

1. **deal阶段** - 发牌时决定是否报/反
   - 输入：新收到的牌
   - 输出：报牌列表（空列表表示不报/反）

2. **cover阶段** - 庄家埋牌
   - 输入：底牌
   - 输出：要埋的8张牌

3. **play阶段** - 出牌
   - 输入：当前回合历史
   - 输出：出牌列表

## 启发式策略说明

### 报/反策略（call_Snatch）
基于手牌评分决定是否报主：
- 评估各花色强度（单牌、对子、级牌等）
- 分数阈值：`>= 5.6` 报主，`>= major_score + 0.5` 反主
- 考虑手牌中级牌的数量和质量

### 出牌策略
1. **单张出牌（gen_single_new）**
   - 队友大时：出分值小牌/垫牌
   - 需要接管时：尝试压过或出最小
   - 空门时：毙分或出小主牌

2. **对子出牌（gen_pair_new）**
   - 类似单张策略，但要求出对子
   - 考虑对子强度和分值

3. **拖拉机（gen_tractor）**
   - 识别并跟出拖拉机
   - 优先级：同花色拖拉机 > 主牌拖拉机

4. **甩牌（gen_throw）**
   - 尝试跟甩或拆牌跟随

5. **首家出牌（gen_one_action）**
   - 优先出拖拉机
   - 考虑主攻/副攻花色
   - 甩牌机会检测

### 埋牌策略（cover_Pub）
- 贪心地选择花色埋牌
- 优先埋副花色小牌
- 保留主牌和大牌

## 技术特点

- ✅ 无机器学习依赖
- ✅ 纯规则驱动
- ✅ 快速决策
- ✅ 可解释性强
- ✅ 低资源消耗

## 与原版本的差异

| 特性 | 原版本 | 当前版本 |
|------|--------|----------|
| 决策方式 | PyTorch CNN模型 | 纯启发式规则 |
| 依赖 | PyTorch, numpy | 仅numpy |
| 训练 | 需要PPO训练 | 无需训练 |
| 推理速度 | 较慢（神经网络） | 快速（规则匹配） |
| 可解释性 | 低（黑盒） | 高（规则透明） |
| 资源占用 | 高（GPU/CPU + 模型） | 低（仅CPU） |

## 文件大小

删除了约30MB的模型检查点文件和训练相关代码，项目更加轻量化。
