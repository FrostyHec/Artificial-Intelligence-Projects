<div align="center">

# Artificial Intelligence Projects

[中文](#项目结构) / [English](#project-structure)

南方科技大学 **CS311 人工智能**课程项目：反向黑白棋、容量约束弧路径规划与收入预测。

</div>

## 项目结构

```text
Artificial_Intelligence_Projects
├── Course_Materials/                  # 课程项目报告评分要求
├── Project1_Reverse_Reversi_Agent/    # 反向黑白棋智能体
│   ├── Code/                          # 智能体代码及参考仓库
│   └── Docs/                          # 项目报告、图片和参考资料
├── Project2_CARP_Solver/              # 容量约束弧路径问题求解器
│   ├── Code/                          # 求解器代码、结果和参考代码
│   └── Docs/                          # 题目要求、项目报告和参考资料
└── Project3_Income_Predictor/         # 收入预测
    └── Docs/                          # 数据集与项目报告
```

各项目的 `Docs/Report` 中保存了详细报告；项目 3 的代码暂未整理至公开目录。

## 项目介绍

### Project 1：反向黑白棋智能体

**题目：** 为反向黑白棋设计一个对弈智能体。规则与普通黑白棋类似，但游戏结束时棋子较少的一方获胜。

**核心思路：** 主要参考了AlphaZero的训练方法（MCTS+RL+CNN）。结合蒙特卡洛树搜索（MCTS）与CNN网络。网络为棋局提供落子概率和局面评价，搜索利用这些信息选择行动；通过自我对弈生成训练数据，迭代改进网络。

[代码](Project1_Reverse_Reversi_Agent/Code/) · [项目报告](Project1_Reverse_Reversi_Agent/Docs/Report/CS311_Project1_Report_%E9%BB%84%E6%94%BF%E4%B8%9C.pdf)

### Project 2：容量约束弧路径问题

**题目：** 在给定道路网络、道路服务需求和车辆容量的情况下，规划从车场出发并返回的路线，覆盖所有需要服务的路段，同时尽量降低总行驶成本。

**核心思路：** 组合+魔改演化算法XD。先用 Floyd–Warshall 算法计算节点间最短距离，再通过路径扫描生成初始解；结合遗传算法、禁忌搜索与爬山式局部搜索，持续改进路线安排。

[代码](Project2_CARP_Solver/Code/) · [项目报告](Project2_CARP_Solver/Docs/Report/CS311_Project2_Report.pdf) · [题目要求](Project2_CARP_Solver/Docs/Project2_Requirement.pdf)

### Project 3：收入预测

**题目：** 根据个人年龄、教育程度等属性，预测年收入是否超过 50,000 美元，是一个二分类问题。

**核心思路：** 分析数据分布和特征关系，尝试缺失值处理、类别编码、归一化和降维等预处理方法；比较逻辑回归、KNN、决策树、SVM 和 XGBoost 等模型，并通过网格搜索调整参数。实验最终选用 XGBoost 作为预测模型。

[项目报告](Project3_Income_Predictor/Docs/Report/CS311_Project3_Report.pdf) · [数据集](Project3_Income_Predictor/Docs/Developing/data%20%281%29.zip)

## Project Structure

```text
Artificial_Intelligence_Projects
├── Course_Materials/                  # Project report grading policy
├── Project1_Reverse_Reversi_Agent/    # Reversed Reversi agent
│   ├── Code/                          # Agent code and reference repositories
│   └── Docs/                          # Report, images, and references
├── Project2_CARP_Solver/              # Capacitated Arc Routing Problem solver
│   ├── Code/                          # Solver, results, and reference code
│   └── Docs/                          # Requirements, report, and references
└── Project3_Income_Predictor/         # Income prediction
    └── Docs/                          # Dataset and report
```

Detailed reports are available in each project's `Docs/Report` directory. The code for Project 3 has not yet been organized into the public repository.

## Project Introduction

### Project 1: Reversed Reversi Agent

**Problem:** Build an agent for Reversed Reversi. The rules are similar to ordinary Reversi, but the player with fewer pieces at the end wins.

**Approach:** Inspired by AlphaZero's training method, the agent combines Monte Carlo Tree Search (MCTS), reinforcement learning, and a convolutional neural network (CNN). The network estimates move probabilities and board values to guide the search; self-play generates training examples to iteratively improve the network.

[Code](Project1_Reverse_Reversi_Agent/Code/) · [Report](Project1_Reverse_Reversi_Agent/Docs/Report/CS311_Project1_Report_%E9%BB%84%E6%94%BF%E4%B8%9C.pdf)

### Project 2: Capacitated Arc Routing Problem

**Problem:** Given a road network, service demands on its roads, and vehicle capacity limits, plan routes that start and end at a depot, serve all required roads, and minimize total travel cost.

**Approach:** A combination of adapted evolutionary algorithms. Floyd–Warshall computes shortest paths between vertices, and path scanning generates initial solutions. Genetic algorithms, tabu search, and hill-climbing local search are then combined to improve the routes.

[Code](Project2_CARP_Solver/Code/) · [Report](Project2_CARP_Solver/Docs/Report/CS311_Project2_Report.pdf) · [Requirements](Project2_CARP_Solver/Docs/Project2_Requirement.pdf)

### Project 3: Income Prediction

**Problem:** Predict whether a person's annual income exceeds $50,000 from attributes such as age and education level. This is a binary classification task.

**Approach:** Analyze data distributions and feature relationships, then experiment with missing-value handling, categorical encoding, normalization, and dimensionality reduction. Compare models including logistic regression, KNN, decision trees, SVM, and XGBoost, and tune their parameters with grid search. XGBoost was selected as the final predictor.

[Report](Project3_Income_Predictor/Docs/Report/CS311_Project3_Report.pdf) · [Dataset](Project3_Income_Predictor/Docs/Developing/data%20%281%29.zip)
