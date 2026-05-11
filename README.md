# geo-audit

Check if an AI search engine knows about your brand.

## What it does

Takes a brand name and keyword. Queries 8 AI engines — Doubao, Kimi, DeepSeek, Qwen (Chinese) and ChatGPT, Perplexity, Gemini, Claude (Western). Checks if the brand appears in responses. Outputs a visibility score and a markdown report.

## How it works

For each keyword × engine combination, it sends a search query and parses the result for brand mentions. Chinese engines go through the Tavily search API. Western engines can use OpenRouter for direct model queries.

The report breaks down visibility into four dimensions:
- **Mention rate** — how often the brand shows up at all
- **Top position rate** — how often it appears early in the response
- **Citation depth** — how many distinct sources cite it
- **Sentiment** — tone of mentions

## Why

People are switching from Google to AI search. But AI engines don't rank pages — they synthesize answers. A brand can rank #1 on Google and still be invisible to ChatGPT or DeepSeek. This tool makes that visibility measurable.

## Quick start

```bash
export TAVILY_API_KEY="your-key"
export OPENROUTER_API_KEY="your-key"  # optional, for Western engine direct queries

python3 scripts/audit_engine.py \
  --brand "Your Brand" \
  --keywords "keyword1,keyword2" \
  --lang both
```

Requires Python 3.8+. No other dependencies.

## Engines covered

| Engine | Region | Query Method |
|--------|--------|-------------|
| Doubao | China | Tavily |
| Kimi | China | Tavily |
| DeepSeek | China | Tavily |
| Qwen | China | Tavily |
| ChatGPT | Global | Tavily or OpenRouter |
| Perplexity | Global | Tavily or OpenRouter |
| Gemini | Global | Tavily or OpenRouter |
| Claude | Global | Tavily or OpenRouter |

## Files

```
scripts/audit_engine.py    — core engine, CLI + importable module
references/                — platform matrix, compliance docs
templates/                 — report template
```

## Notes

This is a measurement tool. It reads AI search results — it does not modify or inject anything. Built against the GEO methodology described by Princeton researchers (Aggarwal et al., KDD 2024).
