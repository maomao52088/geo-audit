# geo-audit：品牌AI引用率审计

> 你的品牌在AI搜索里是什么形象？被引用了还是被忽略了？

## 一句话说明

输入品牌名 → 自动在8大AI搜索引擎中检索 → 输出"你的品牌AI引用率报告"

## 为什么要做这个？

传统SEO看的是Google排名。但越来越多人用**AI搜索**（豆包、Kimi、DeepSeek、ChatGPT、Perplexity……）直接问问题，AI直接给答案。

**问题来了：AI回答里有没有你？**

- 用户问"XX产品推荐"，AI推荐了竞品，没提你 → 你在AI搜索里是隐形的
- 用户问"XX行业最好的是谁"，AI说了别人 → 你丢失了潜在客户
- 你花了很多钱做传统SEO排名，但AI搜索根本不看排名 → 效果归零

**geo-audit帮你看见问题，才能解决问题。**

## 它能做什么

| 功能 | 说明 |
|------|------|
| 🔍 多引擎检索 | 自动在豆包/Kimi/DeepSeek/通义/ChatGPT/Perplexity/Gemini/Claude中搜索 |
| 📊 引用率评分 | 综合可见度0-100分，拆解4个维度 |
| 🥊 竞品对比 | 你的引用份额 vs 竞品，一目了然 |
| 🩺 问题诊断 | 哪些平台缺失、什么场景被忽略 |
| 📋 优化建议 | 按优先级排序的行动清单 |
| ✅ 合规保障 | 内置315合规自检，严格区分合规GEO与投毒GEO |

## 5分钟上手

### 前置条件
- Python 3.8+
- Tavily API Key（[免费申请](https://tavily.com/)）

### 快速运行

```bash
# 1. 设置API Key
export TAVILY_API_KEY="你的key"

# 2. 运行审计
python3 scripts/audit_engine.py \
  --brand "你的品牌名" \
  --keywords "搜索词1,搜索词2,搜索词3" \
  --lang both \
  --output my-brand-audit.md

# 3. 查看报告
cat my-brand-audit.md
```

### 参数说明

| 参数 | 必填 | 说明 | 示例 |
|------|------|------|------|
| `--brand` | ✅ | 品牌/产品/人名 | `"Surya Bonaly"` |
| `--keywords` | ✅ | 搜索词，逗号分隔 | `"花样滑冰传奇,backflip skating"` |
| `--lang` | ⬜ | zh/en/both，默认both | `zh` |
| `--competitors` | ⬜ | 竞品名，逗号分隔 | `"Tonya Harding,Michelle Kwan"` |
| `--depth` | ⬜ | quick/standard/deep | `standard` |
| `--output` | ⬜ | 报告输出路径 | `report.md` |
| `--json` | ⬜ | 同时输出JSON数据 | — |

### 示例输出

```
🔍 GEO审计启动: Surya Bonaly
   关键词: ['Surya Bonaly figure skating', 'backflip ice skating legend']
   语言: both | 深度: standard

[检索] 豆包 → Surya Bonaly figure skating 推荐 排名
[检索] Kimi → Surya Bonaly figure skating 深度分析
[检索] ChatGPT Search → best Surya Bonaly figure skating recommendations
...

📊 综合可见度: 75/100
   引用率: 71.4%
   首位率: 66.7%
   引用深度: 85.0%
   情感倾向: 100.0%
```

## 报告长什么样

生成的Markdown报告包含6个部分：

1. **执行摘要** — 一页纸结论：总分、被引用/缺失平台
2. **维度评分** — 引用率、首位率、引用深度、情感倾向
3. **各平台详情** — 每个AI引擎的搜索结果+上下文片段
4. **引用份额** — 品牌 vs 竞品的对比条形图
5. **问题诊断** — 缺失平台、薄弱环节
6. **优化建议** — 按优先级排序的行动清单

## 文件结构

```
geo-audit/
├── README.md                          ← 你正在看的
├── SKILL.md                           ← 主指令文件（AI Agent可读取）
├── scripts/
│   └── audit_engine.py                ← 核心引擎（CLI + import两种模式）
├── references/
│   ├── platform-matrix.md             ← 8大AI平台引用偏好速查表
│   └── compliance-checklist.md        ← 315合规自检清单
├── templates/
│   └── audit-report-template.md       ← 报告输出模板
└── test-reports/
    ├── Surya-Bonaly-audit.md          ← 测试报告样本
    └── Surya-Bonaly-raw.json          ← 原始数据样本
```

## 合规声明

⚠️ **本工具与315曝光的"投毒GEO"完全不同。**

| | 投毒GEO（315打击） | geo-audit（我们做的事） |
|---|---|---|
| 做什么 | 虚构产品+批量造假操控AI | 审计真实引用情况，不操纵结果 |
| 目的 | 让AI推荐虚假信息 | 让你看见品牌在AI搜索中的真实状况 |
| 合规 | ❌ 违法 | ✅ 合规 |

本工具：
- ✅ 只读取AI搜索结果，不修改、不注入任何内容
- ✅ 不生成虚假软文、不批量灌水
- ✅ 内置合规预检，拒绝投毒型请求
- ✅ 每份报告附带合规声明

## 常见问题

**Q: 必须用Tavily API吗？**
A: 目前是。Tavily免费额度足够日常使用。后续会支持更多搜索API。

**Q: 审计一次要多久？**
A: 3个关键词约30秒，10个关键词约2分钟。建议关键词不超过10个。

**Q: 支持哪些AI搜索引擎？**
A: 豆包、Kimi、DeepSeek、通义千问（中文）+ ChatGPT Search、Perplexity、Gemini、Claude（英文），共8个。

**Q: 审计结果准确吗？**
A: 审计反映的是**搜索时刻**的AI引用情况。AI引擎结果会随内容生态变化，建议每月审计一次跟踪变化。

**Q: 审计完了怎么优化？**
A: 报告中的"优化建议"会给出具体方向。后续会推出 `geo-content-optimizer`（内容优化）和 `geo-schema-builder`（结构化数据）指令包。

## 关于GEO

GEO（Generative Engine Optimization）= AI时代的SEO。传统SEO优化Google排名，GEO优化AI引用率。Princeton大学研究（KDD 2024）证明GEO可提升AI引用可见度40%-115%。

## ☕ 请我喝杯咖啡

如果 geo-audit 帮到你，欢迎打赏支持持续开发！

<div align="center">
<img src="assets/sponsor-qr.jpg" width="150" alt="打赏二维码">
</div>

## License

MIT — 自由使用、修改、分发。但严禁用于投毒/操控AI的违法用途。

---

*🦞 geo-audit v1.0 | 合规GEO方法论 | 2026-04-20*
