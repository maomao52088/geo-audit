# GEO审计报告模板

> 这是geo-audit生成的标准报告格式，所有审计报告按此结构输出

---

# 📊 GEO审计报告: {brand_name}

> 生成时间: {timestamp} | 语言: {language} | 深度: {depth}

---

## 执行摘要

- **综合可见度**: {overall_score}/100 {grade_emoji}
- **被引用平台**: {mentioned_count}/{total_platforms}
- **缺失平台**: {missing_platforms}
- **关键发现**: {one_line_insight}

---

## 维度评分

| 维度 | 得分 | 说明 |
|------|------|------|
| 引用率(mention_rate) | {mention_rate}% | 在AI回答中被提及的比例 |
| 首位率(top_position) | {top_position_rate}% | 被提及且排名靠前的比例 |
| 引用深度(citation_depth) | {citation_depth}% | 被引用的来源数量丰富度 |
| 情感倾向(sentiment) | {sentiment_score}% | 正面提及的比例 |

### 评分等级
- 🟢 优秀 (≥70): 品牌在AI搜索中有强存在感
- 🟡 一般 (40-69): 有引用但存在明显短板
- 🔴 较差 (<40): 品牌在AI搜索中几乎不可见

---

## 各平台详情

### {platform_name} {status_emoji}

**搜索词**: {keyword_used}
**品牌提及**: ✅已引用 / ❌未引用

{if_mentioned}
- **位置**: 🥇首位 / 📍中间 / 🔚末尾
- **引用来源**:
  - {source_url_1}
  - {source_url_2}
- **上下文片段**:
  > {context_snippet_1}
  > {context_snippet_2}
{endif}

{if_not_mentioned}
- 该平台搜索结果中未发现品牌提及
- **建议**: {platform_specific_recommendation}
{endif}

---

## 引用份额 (Share of Voice)

| 品牌 | 引用份额 |
|------|---------|
| **{brand_name}** | {brand_sov}% ████████░░░░ |
| {competitor_1} | {comp1_sov}% ████░░░░░░░░░░ |
| {competitor_2} | {comp2_sov}% ██░░░░░░░░░░░░ |

---

## 问题诊断

### ❌ 缺失平台({count}个)
- **{platform}** — {diagnosis}

### ⚠️ 薄弱环节
- {weak_point_1}
- {weak_point_2}

---

## 优化建议（按优先级排序）

1. **{action_1}** — {reason_1} → 预期提升{expected_gain_1}
2. **{action_2}** — {reason_2} → 预期提升{expected_gain_2}
3. **{action_3}** — {reason_3} → 预期提升{expected_gain_3}

### 推荐使用的GEO指令包
- → `geo-content-optimizer`: 优化内容格式和结构
- → `geo-schema-builder`: 添加结构化数据标记
- → `geo-platform-strategy`: 针对特定平台定制优化

---

## 合规声明

本报告遵循合规GEO方法论：
- ✅ 所有审计数据来自真实AI搜索结果
- ✅ 优化建议基于真实内容结构化，不虚构信息
- ✅ 不使用批量生成、虚假软文、伪造共识等投毒手段
- ✅ 所有操作可追溯、可审计
- ✅ 符合国家市场监管总局AI广告监管要求

---

*报告由 geo-audit v1.0 生成 | 合规GEO方法论 | {timestamp}*
