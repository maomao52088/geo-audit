# GEO Audit — 品牌AI搜索可见度审计

**你的品牌在AI搜索里存在吗？** 免费查 → 4引擎快照。完整审计 → 8引擎 + 竞品对比 + Content Brief。

> 对标 PromptScout，但我们覆盖中国引擎（豆包/Kimi/DeepSeek/通义千问）。

## 🔥 免费一键检查

输入品牌名，30秒看4大AI引擎的可见性。不用注册，不用付费。

```
POST /api/quick-check
{"brand": "你的品牌名"}
→ 返回：可见性得分 + 每个引擎的✅/—
```

## 📊 完整审计

8大AI引擎全覆盖 + 竞品对比 + 引用来源分析 + Content Brief（告诉你怎么修）。

```
POST /api/audit
{"brand": "你的品牌名", "industry": "餐饮", "keywords": "推荐,排名"}
→ 返回：完整报告 + 可见性评分 + 修复建议
```

## 引擎覆盖

| 引擎 | 区域 | 免费检查 | 完整审计 |
|------|------|----------|----------|
| 豆包 (Doubao) | 中国 | ✅ | ✅ |
| Kimi | 中国 | ✅ | ✅ |
| DeepSeek | 中国 | — | ✅ |
| 通义千问 (Qwen) | 中国 | — | ✅ |
| ChatGPT | 全球 | ✅ | ✅ |
| Perplexity | 全球 | ✅ | ✅ |
| Gemini | 全球 | — | ✅ |
| Claude | 全球 | — | ✅ |

## 四维度评分

- **Mention rate** — 品牌出现的频率
- **Top position rate** — 在回答中靠前出现的比例
- **Citation depth** — 有多少不同来源引用了你
- **Sentiment** — 提及的情感倾向

## 为什么重要

越来越多人用AI搜索代替传统搜索。AI不排名网页——它合成答案。品牌可能在Google排第一，但在豆包或Kimi的回答里完全隐形。每个看不见你的用户，都是一个丢掉的客户。

## 快速开始

```bash
export TAVILY_API_KEY="your-key"
export OPENROUTER_API_KEY="your-key"  # 可选

# CLI模式
python3 scripts/audit_engine.py \
  --brand "你的品牌" \
  --keywords "关键词1,关键词2" \
  --lang both

# Web模式
cd web && python3 app.py
# → http://localhost:8899
```

零依赖，纯Python标准库。

## 方法论

仅测量、不操控。读取AI搜索结果，不修改、不注入任何内容。基于Princeton大学KDD 2024发表的GEO方法论（Aggarwal et al.）。

## 文件

```
scripts/audit_engine.py    — 核心引擎
web/app.py                 — Web API + 免费快速检查
web/index.html             — 落地页
references/                — 平台矩阵、合规文档
templates/                 — 报告模板
```

🔗 [trygeoaudit.com](https://trygeoaudit.com) · [Product Hunt](https://www.producthunt.com)
