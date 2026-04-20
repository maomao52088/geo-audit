#!/usr/bin/env python3
"""
geo-audit 核心引擎 — 品牌AI引用率审计
支持Tavily API检索 + 手动输入 + 多平台分析

用法:
  python3 audit_engine.py --brand "Surya Bonaly" --keywords "花样滑冰传奇,backflip skating" --lang both
  python3 audit_engine.py --brand "大龙猫" --keywords "AI助手,自动化" --lang zh
  python3 audit_engine.py --config audit_config.json
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime
from pathlib import Path

# ========== 配置 ==========

TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")
TAVILY_API_URL = "https://api.tavily.com/search"

# AI搜索引擎映射 — 每个平台用不同的搜索query模板
AI_PLATFORMS = {
    # 中文平台
    "doubao": {
        "name": "豆包",
        "lang": "zh",
        "query_template": "{keyword} 推荐 排名",
        "weight": 0.20,
    },
    "kimi": {
        "name": "Kimi",
        "lang": "zh",
        "query_template": "{keyword} 深度分析",
        "weight": 0.15,
    },
    "deepseek": {
        "name": "DeepSeek",
        "lang": "zh",
        "query_template": "{keyword} 技术详解",
        "weight": 0.15,
    },
    "qwen": {
        "name": "通义千问",
        "lang": "zh",
        "query_template": "{keyword} 对比评测",
        "weight": 0.10,
    },
    # 英文平台
    "chatgpt": {
        "name": "ChatGPT Search",
        "lang": "en",
        "query_template": "best {keyword} recommendations",
        "weight": 0.15,
    },
    "perplexity": {
        "name": "Perplexity",
        "lang": "en",
        "query_template": "{keyword} expert review comparison",
        "weight": 0.10,
    },
    "gemini": {
        "name": "Gemini",
        "lang": "en",
        "query_template": "top {keyword} guide",
        "weight": 0.08,
    },
    "claude": {
        "name": "Claude",
        "lang": "en",
        "query_template": "{keyword} analysis overview",
        "weight": 0.07,
    },
}


# ========== 合规预检 ==========

class ComplianceChecker:
    """315合规预检 — 拒绝投毒型请求"""

    RED_FLAGS = [
        "虚构", "虚假", "造假", "投毒", "操控", "刷量",
        "fake", "fabricate", "manipulate", "poison",
    ]

    @classmethod
    def check(cls, brand_name: str, keywords: list) -> dict:
        result = {"passed": True, "warnings": []}

        # 检查品牌名是否为空白/疑似虚假
        if not brand_name or len(brand_name.strip()) < 2:
            result["passed"] = False
            result["warnings"].append("品牌名过短或为空")

        # 检查keywords中是否包含红线词
        all_text = brand_name + " " + " ".join(keywords)
        for flag in cls.RED_FLAGS:
            if flag in all_text.lower():
                result["passed"] = False
                result["warnings"].append(f"检测到红线词: '{flag}' — 审计不应用于投毒目的")

        # 检查关键词数量
        if len(keywords) < 1:
            result["passed"] = False
            result["warnings"].append("至少需要1个关键词")

        result["checked_at"] = datetime.now().isoformat()
        return result


# ========== Tavily搜索 ==========

def tavily_search(query: str, max_results: int = 5, search_depth: str = "advanced") -> dict:
    """通过Tavily API执行搜索"""
    if not TAVILY_API_KEY:
        return {"error": "TAVILY_API_KEY not set", "results": []}

    payload = json.dumps({
        "api_key": TAVILY_API_KEY,
        "query": query,
        "max_results": max_results,
        "search_depth": search_depth,
        "include_answer": True,
    }).encode("utf-8")

    req = urllib.request.Request(
        TAVILY_API_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:500]
        return {"error": f"HTTP {e.code}: {body}", "results": []}
    except Exception as e:
        return {"error": str(e), "results": []}


# ========== 引用分析 ==========

class CitationAnalyzer:
    """分析搜索结果中品牌的引用情况"""

    @staticmethod
    def analyze_mention(search_result: dict, brand_name: str) -> dict:
        """分析单次搜索结果中品牌是否被提及"""
        mention = {
            "brand_found": False,
            "position": None,  # "first" / "middle" / "last" / None
            "sentiment": None,  # "positive" / "neutral" / "negative" / None
            "cited_urls": [],
            "context_snippets": [],
            "competitors_found": [],
        }

        # 检查AI回答中是否提及
        answer = search_result.get("answer", "") or ""
        if brand_name.lower() in answer.lower():
            mention["brand_found"] = True
            # 判断位置
            idx = answer.lower().index(brand_name.lower())
            if idx < len(answer) * 0.3:
                mention["position"] = "first"
            elif idx < len(answer) * 0.7:
                mention["position"] = "middle"
            else:
                mention["position"] = "last"
            mention["context_snippets"].append(answer[:500])

        # 检查搜索结果中是否提及
        for item in search_result.get("results", []):
            content = (item.get("content", "") or "") + (item.get("title", "") or "")
            if brand_name.lower() in content.lower():
                mention["brand_found"] = True
                mention["cited_urls"].append(item.get("url", ""))
                # 提取上下文片段
                lower_content = content.lower()
                idx = lower_content.find(brand_name.lower())
                start = max(0, idx - 100)
                end = min(len(content), idx + len(brand_name) + 100)
                mention["context_snippets"].append(content[start:end])

        return mention

    @staticmethod
    def calculate_visibility(mentions: dict, competitors: list = None) -> dict:
        """计算综合可见度评分"""
        total_platforms = len(mentions)
        if total_platforms == 0:
            return {"overall_score": 0, "dimensions": {}}

        # 各维度计算
        mention_rate = sum(1 for m in mentions.values() if m["brand_found"]) / total_platforms
        top_position_count = sum(1 for m in mentions.values() if m["position"] == "first")
        mentioned_count = sum(1 for m in mentions.values() if m["brand_found"])
        top_position_rate = top_position_count / max(mentioned_count, 1)

        citation_depth = sum(len(m["cited_urls"]) for m in mentions.values()) / max(total_platforms * 3, 1)
        citation_depth = min(citation_depth, 1.0)

        positive_count = sum(1 for m in mentions.values() if m.get("sentiment") == "positive")
        sentiment_score = positive_count / max(mentioned_count, 1)

        # 加权综合评分
        overall = (
            mention_rate * 0.35 +
            top_position_rate * 0.25 +
            citation_depth * 0.25 +
            sentiment_score * 0.15
        )

        dimensions = {
            "mention_rate": round(mention_rate * 100, 1),
            "top_position_rate": round(top_position_rate * 100, 1),
            "citation_depth": round(citation_depth * 100, 1),
            "sentiment_score": round(sentiment_score * 100, 1),
        }

        return {
            "overall_score": round(overall * 100, 1),
            "dimensions": dimensions,
            "mentioned_platforms": [k for k, v in mentions.items() if v["brand_found"]],
            "missing_platforms": [k for k, v in mentions.items() if not v["brand_found"]],
        }

    @staticmethod
    def calculate_share_of_voice(brand_score: float, competitor_scores: dict) -> dict:
        """计算引用份额（Share of Voice）"""
        total = brand_score
        sov = {"brand": brand_score}

        for name, score in competitor_scores.items():
            sov[name] = score
            total += score

        if total > 0:
            sov = {k: round(v / total * 100, 1) for k, v in sov.items()}

        return sov


# ========== 报告生成 ==========

class ReportGenerator:
    """生成Markdown审计报告"""

    @staticmethod
    def generate(config: dict, mentions: dict, visibility: dict, sov: dict = None) -> str:
        brand = config["brand_name"]
        keywords = config["keywords"]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        lines = []
        lines.append(f"# 📊 GEO审计报告: {brand}")
        lines.append(f"> 生成时间: {timestamp} | 语言: {config.get('language', 'both')}")
        lines.append("")

        # 执行摘要
        lines.append("## 执行摘要")
        lines.append("")
        score = visibility.get("overall_score", 0)
        grade = "🟢 优秀" if score >= 70 else "🟡 一般" if score >= 40 else "🔴 较差"
        lines.append(f"- **综合可见度**: {score}/100 {grade}")
        lines.append(f"- **被引用平台**: {len(visibility.get('mentioned_platforms', []))}/{len(mentions)}")
        lines.append(f"- **缺失平台**: {', '.join(visibility.get('missing_platforms', [])) or '无'}")
        lines.append("")

        # 各维度评分
        lines.append("## 维度评分")
        lines.append("")
        dims = visibility.get("dimensions", {})
        lines.append("| 维度 | 得分 | 说明 |")
        lines.append("|------|------|------|")
        lines.append(f"| 引用率(mention_rate) | {dims.get('mention_rate', 0)}% | 在AI回答中被提及的比例 |")
        lines.append(f"| 首位率(top_position) | {dims.get('top_position_rate', 0)}% | 被提及且排名靠前的比例 |")
        lines.append(f"| 引用深度(citation_depth) | {dims.get('citation_depth', 0)}% | 被引用的来源数量 |")
        lines.append(f"| 情感倾向(sentiment) | {dims.get('sentiment_score', 0)}% | 正面提及的比例 |")
        lines.append("")

        # 各平台详情
        lines.append("## 各平台详情")
        lines.append("")
        for platform_id, mention in mentions.items():
            platform_info = AI_PLATFORMS.get(platform_id, {})
            platform_name = platform_info.get("name", platform_id)
            status = "✅ 被引用" if mention["brand_found"] else "❌ 未引用"
            lines.append(f"### {platform_name} {status}")
            if mention["brand_found"]:
                if mention["position"]:
                    pos_map = {"first": "🥇 首位", "middle": "📍 中间", "last": "🔚 末尾"}
                    lines.append(f"- 位置: {pos_map.get(mention['position'], mention['position'])}")
                if mention["cited_urls"]:
                    lines.append(f"- 引用来源({len(mention['cited_urls'])}个):")
                    for url in mention["cited_urls"][:3]:
                        lines.append(f"  - {url}")
                if mention["context_snippets"]:
                    lines.append(f"- 上下文片段:")
                    for snippet in mention["context_snippets"][:2]:
                        lines.append(f"  > {snippet[:200]}")
            else:
                lines.append("- 该平台搜索结果中未发现品牌提及")
            lines.append("")

        # 引用份额
        if sov:
            lines.append("## 引用份额 (Share of Voice)")
            lines.append("")
            lines.append("| 品牌 | 引用份额 |")
            lines.append("|------|---------|")
            for name, share in sov.items():
                bar = "█" * int(share / 5) + "░" * (20 - int(share / 5))
                label = f"**{brand}**" if name == "brand" else name
                lines.append(f"| {label} | {share}% {bar} |")
            lines.append("")

        # 诊断与建议
        lines.append("## 问题诊断")
        lines.append("")
        missing = visibility.get("missing_platforms", [])
        if missing:
            lines.append(f"### ❌ 缺失平台({len(missing)}个)")
            for p in missing:
                pinfo = AI_PLATFORMS.get(p, {})
                lines.append(f"- **{pinfo.get('name', p)}** — 需要针对该平台优化内容格式")
            lines.append("")

        # 优化建议
        lines.append("## 优化建议（按优先级排序）")
        lines.append("")
        priority = 1
        if missing:
            lines.append(f"{priority}. **补全缺失平台内容** — 针对{', '.join(missing)}创建适配内容")
            priority += 1
        if dims.get("top_position_rate", 0) < 50:
            lines.append(f"{priority}. **提升首位引用率** — 当前首位率{dims.get('top_position_rate', 0)}%，优化FAQ和摘要前置")
            priority += 1
        if dims.get("citation_depth", 0) < 30:
            lines.append(f"{priority}. **增加引用来源数量** — 在更多权威平台发布内容，建立引用网络")
            priority += 1
        if dims.get("mention_rate", 0) < 60:
            lines.append(f"{priority}. **提升基础引用率** — 添加Schema.org结构化数据，部署llms.txt")
            priority += 1

        lines.append("")
        lines.append("---")
        lines.append(f"*报告由 geo-audit v1.0 生成 | 合规GEO方法论 | {timestamp}*")

        return "\n".join(lines)


# ========== 主流程 ==========

def run_audit(brand_name: str, keywords: list, language: str = "both",
              competitors: list = None, depth: str = "standard",
              api_key: str = None) -> dict:
    """执行完整审计流程"""

    # 注入API key
    global TAVILY_API_KEY
    if api_key:
        TAVILY_API_KEY = api_key

    # Step 1: 合规预检
    compliance = ComplianceChecker.check(brand_name, keywords)
    if not compliance["passed"]:
        return {"error": "合规预检未通过", "compliance": compliance}

    # Step 2: 多引擎检索
    mentions = {}
    raw_results = {}

    # 根据语言过滤平台
    target_platforms = {}
    for pid, pinfo in AI_PLATFORMS.items():
        if language == "both":
            target_platforms[pid] = pinfo
        elif language == "zh" and pinfo["lang"] == "zh":
            target_platforms[pid] = pinfo
        elif language == "en" and pinfo["lang"] == "en":
            target_platforms[pid] = pinfo

    for keyword in keywords:
        for platform_id, platform_info in target_platforms.items():
            query = platform_info["query_template"].format(keyword=keyword)
            print(f"[检索] {platform_info['name']} → {query}")

            result = tavily_search(query, max_results=5, search_depth="advanced")
            raw_results[f"{platform_id}:{keyword}"] = result

            # 分析引用
            mention = CitationAnalyzer.analyze_mention(result, brand_name)
            # 如果已找到，保持found=True；如果没找到，也记录
            if platform_id not in mentions:
                mentions[platform_id] = mention
            elif not mentions[platform_id]["brand_found"] and mention["brand_found"]:
                mentions[platform_id] = mention

            # 避免请求过快
            time.sleep(1)

    # Step 3: 计算可见度
    visibility = CitationAnalyzer.calculate_visibility(mentions, competitors)

    # Step 4: 竞品对比（如果有竞品）
    sov = None
    if competitors:
        competitor_scores = {}
        for comp in competitors:
            comp_mentions = {}
            for keyword in keywords[:3]:  # 竞品只搜前3个关键词
                for platform_id, platform_info in target_platforms.items():
                    query = platform_info["query_template"].format(keyword=keyword)
                    result = tavily_search(query, max_results=3)
                    mention = CitationAnalyzer.analyze_mention(result, comp)
                    if platform_id not in comp_mentions:
                        comp_mentions[platform_id] = mention
                    elif not comp_mentions[platform_id]["brand_found"] and mention["brand_found"]:
                        comp_mentions[platform_id] = mention
                    time.sleep(1)
            comp_vis = CitationAnalyzer.calculate_visibility(comp_mentions)
            competitor_scores[comp] = comp_vis.get("overall_score", 0)

        sov = CitationAnalyzer.calculate_share_of_voice(
            visibility.get("overall_score", 0), competitor_scores
        )

    # Step 5: 生成报告
    config = {
        "brand_name": brand_name,
        "keywords": keywords,
        "language": language,
        "depth": depth,
        "competitors": competitors or [],
    }
    report = ReportGenerator.generate(config, mentions, visibility, sov)

    return {
        "config": config,
        "compliance": compliance,
        "visibility": visibility,
        "mentions": mentions,
        "share_of_voice": sov,
        "raw_results_count": len(raw_results),
        "report_markdown": report,
    }


# ========== CLI ==========

def main():
    parser = argparse.ArgumentParser(description="geo-audit: 品牌AI引用率审计")
    parser.add_argument("--brand", required=True, help="品牌名/产品名")
    parser.add_argument("--keywords", required=True, help="搜索关键词，逗号分隔")
    parser.add_argument("--competitors", default="", help="竞品名，逗号分隔")
    parser.add_argument("--lang", default="both", choices=["zh", "en", "both"], help="审计语言")
    parser.add_argument("--depth", default="standard", choices=["quick", "standard", "deep"], help="审计深度")
    parser.add_argument("--api-key", default=None, help="Tavily API Key")
    parser.add_argument("--output", default=None, help="输出文件路径(.md)")
    parser.add_argument("--json", action="store_true", help="同时输出JSON数据")

    args = parser.parse_args()

    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
    competitors = [c.strip() for c in args.competitors.split(",") if c.strip()] or None

    print(f"\n🔍 GEO审计启动: {args.brand}")
    print(f"   关键词: {keywords}")
    print(f"   语言: {args.lang} | 深度: {args.depth}")
    if competitors:
        print(f"   竞品: {competitors}")
    print()

    result = run_audit(
        brand_name=args.brand,
        keywords=keywords,
        language=args.lang,
        competitors=competitors,
        depth=args.depth,
        api_key=args.api_key,
    )

    if "error" in result:
        print(f"\n❌ {result['error']}")
        if "compliance" in result:
            for w in result["compliance"].get("warnings", []):
                print(f"  ⚠️ {w}")
        sys.exit(1)

    # 输出报告
    report = result["report_markdown"]
    print("\n" + "=" * 60)
    print(report)

    # 保存到文件
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding="utf-8")
        print(f"\n📄 报告已保存: {out_path}")

    # 保存JSON
    if args.json:
        json_path = Path(args.output or "audit_report").with_suffix(".json")
        json_data = {k: v for k, v in result.items() if k != "report_markdown"}
        json_path.write_text(json.dumps(json_data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"📊 JSON数据已保存: {json_path}")


if __name__ == "__main__":
    main()
