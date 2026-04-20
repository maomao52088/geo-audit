---
name: geo-audit
description: 品牌AI引用率审计 — 自动搜索8大AI引擎，抓取品牌被引用/提及情况，生成可视化引用率报告。GEO指令包#1，免费引流入口。
version: 1.0.0
category: geo
triggers:
  - pattern: "geo-audit|品牌审计|AI引用率|AI搜索报告|AI可见度"
  - pattern: "我在AI搜索里是什么形象|品牌AI曝光"
---

# geo-audit：品牌AI引用率审计

> 你的品牌在AI搜索里是什么形象？被引用了还是被忽略了？

## 用途

输入品牌名/产品名/关键词 → 自动在8大AI搜索引擎中检索 → 输出完整的AI引用率报告，包括：
- 品牌在各AI引擎中的**可见度评分**
- 被引用的**内容片段**和**来源分析**
- 竞品对比**引用份额**
- 优化建议**优先级排序**

## 前置输入

用户需要提供：

| 参数 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `brand_name` | ✅ | 品牌名/产品名/人名 | "Surya Bonaly" / "大龙猫" |
| `keywords` | ✅ | 目标搜索词列表（3-10个） | ["花样滑冰传奇", "backflip skating"] |
| `competitors` | ⬜ | 竞品列表（最多5个） | ["Tonya Harding", "Michelle Kwan"] |
| `language` | ⬜ | 审计语言，默认双语 | "zh" / "en" / "both" |
| `depth` | ⬜ | 审计深度，默认标准 | "quick" / "standard" / "deep" |

## 执行步骤

### Step 1: 合规预检

```
□ 确认brand_name是真实存在的品牌/产品/人物
□ 确认keywords不包含虚假/误导性词汇
□ 确认审计目的不是用于投毒/操纵
□ 记录审计时间和操作者
```

> ⚠️ 如果合规预检不通过，拒绝执行并提示原因。详见 `references/compliance-checklist.md`

### Step 2: 多引擎检索

按以下矩阵执行搜索，记录每个引擎的响应：

**中文AI引擎：**
| # | 平台 | 搜索方式 | 检索指令 |
|---|------|---------|---------|
| 1 | 豆包 | Web搜索/API | 对每个keyword执行搜索 |
| 2 | Kimi | Web搜索/API | 对每个keyword执行搜索 |
| 3 | DeepSeek | Web搜索/API | 对每个keyword执行搜索 |
| 4 | 通义千问 | Web搜索/API | 对每个keyword执行搜索 |

**英文AI引擎：**
| # | 平台 | 搜索方式 | 检索指令 |
|---|------|---------|---------|
| 5 | ChatGPT Search | Web搜索/API | 对每个keyword执行搜索 |
| 6 | Perplexity | Web搜索/API | 对每个keyword执行搜索 |
| 7 | Gemini | Web搜索/API | 对每个keyword执行搜索 |
| 8 | Claude | Web搜索/API | 对每个keyword执行搜索 |

**每个搜索记录：**
- 是否提及brand_name → Y/N
- 提及位置 → 首位/中间/末尾
- 提及语境 → 正面/中性/负面
- 引用的来源URL（如有）
- 回答中引用的其他品牌（竞品出现情况）

### Step 3: 引用率计算

```python
# 引用率核心算法
visibility_score = {
    "mention_rate": 被提及的引擎数 / 总引擎数,        # 0-100%
    "top_position_rate": 首位提及数 / 被提及总数,      # 0-100%
    "citation_depth": 引用来源数 / 最大可能来源数,      # 0-100%
    "sentiment_score": 正面提及数 / 总提及数,          # 0-100%
}

# 综合可见度评分（加权）
overall_score = (
    mention_rate * 0.35 +
    top_position_rate * 0.25 +
    citation_depth * 0.25 +
    sentiment_score * 0.15
)
```

### Step 4: 竞品对比

如果有竞品数据，计算**引用份额**（Share of Voice）：

```
引用份额 = 品牌被提及次数 / (品牌+所有竞品被提及总次数)
```

输出对比矩阵：
| 品牌 | 豆包 | Kimi | DeepSeek | 通义 | ChatGPT | Perplexity | Gemini | Claude | 综合 |
|------|------|------|----------|------|---------|------------|--------|--------|------|

### Step 5: 生成报告

按 `templates/audit-report-template.md` 格式输出完整报告，包含：

1. **执行摘要** — 一页纸结论
2. **各平台详情** — 每个AI引擎的搜索结果截图/文本
3. **引用率评分** — 可见度评分+各维度得分
4. **竞品对比** — 引用份额矩阵
5. **问题诊断** — 哪些平台缺失、什么内容没被引用
6. **优化建议** — 按优先级排序的行动清单

### Step 6: 合规归档

```
□ 审计报告仅基于真实搜索结果，不篡改数据
□ 不建议通过虚假内容提升引用率
□ 所有优化建议基于合规GEO方法论
□ 报告存档备查
```

## 输出格式

- **快速模式(quick)**: 控制台摘要 + JSON数据
- **标准模式(standard)**: Markdown完整报告
- **深度模式(deep)**: Markdown报告 + 原始数据CSV + 可视化图表

## 技术实现

- 核心引擎: `scripts/audit_engine.py`
- 支持Tavily API进行Web检索
- 支持手动输入搜索结果（API不可用时）
- 输出JSON/Markdown双格式

## 合规声明

本指令包遵循合规GEO原则，与315曝光的"投毒GEO"完全不同：
- ✅ 审计真实引用情况，不操纵结果
- ✅ 优化建议基于真实内容结构化，不虚构信息
- ✅ 所有操作可追溯、可审计
- ❌ 不支持批量生成虚假内容
- ❌ 不支持虚构品牌/产品投毒

详见 `references/compliance-checklist.md`
