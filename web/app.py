#!/usr/bin/env python3
"""GEO Audit Web Server — 纯标准库，零依赖"""
import json
import os
import sys
import threading
import time
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import datetime

# 把 audit_engine 加到 path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from audit_engine import run_audit, AI_PLATFORMS

TAVILY_KEY = os.environ.get("TAVILY_API_KEY", "")
if Path(os.path.expanduser("~/.hermes/.secrets/tavily.key")).exists():
    TAVILY_KEY = Path(os.path.expanduser("~/.hermes/.secrets/tavily.key")).read_text().strip()

WEB_DIR = Path(__file__).resolve().parent
HISTORY_FILE = Path(os.path.expanduser("~/.geo-audit-history.json"))

# 结果缓存（品牌名→结果）
_cache = {}
_cache_lock = threading.Lock()

# 行业默认关键词映射
INDUSTRY_KEYWORDS = {
    "餐饮": ["附近好吃的", "推荐餐厅", "必吃榜"],
    "教育": ["推荐培训机构", "学什么好", "培训班推荐"],
    "电商": ["好用的产品推荐", "什么值得买", "性价比"],
    "护肤": ["护肤品推荐", "敏感肌用什么", "好用的面霜"],
    "本地服务": ["附近推荐", "靠谱的店", "口碑好的"],
    "SaaS": ["好用的工具推荐", "效率工具", "办公软件"],
}

def get_keywords(industry, custom=None):
    base = INDUSTRY_KEYWORDS.get(industry, ["推荐", "哪个好", "口碑"])
    if custom:
        base = [k.strip() for k in custom.split(",") if k.strip()] + base
    return base[:4]


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            html = (WEB_DIR / "index.html").read_text()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode())
        elif self.path == "/api/health":
            self._json({"status": "ok", "timestamp": datetime.now().isoformat()})
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/audit":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            brand = body.get("brand", "").strip()
            industry = body.get("industry", "")
            custom_kw = body.get("keywords", "")

            if not brand:
                self._json({"error": "请输入品牌名"}, 400)
                return

            keywords = get_keywords(industry, custom_kw)
            cache_key = f"{brand}:{','.join(keywords)}"

            with _cache_lock:
                if cache_key in _cache:
                    self._json(_cache[cache_key])
                    return

            try:
                result = run_audit(
                    brand_name=brand,
                    keywords=keywords,
                    language="zh",
                    api_key=TAVILY_KEY,
                )

                # 精简返回（不传完整raw_results）
                response = {
                    "brand": brand,
                    "keywords": keywords,
                    "visibility": result.get("visibility", {}),
                    "report": result.get("report_markdown", ""),
                    "timestamp": datetime.now().isoformat(),
                }

                with _cache_lock:
                    _cache[cache_key] = response

                # 存历史
                self._save_history(brand, response)
                self._json(response)

            except Exception as e:
                self._json({"error": str(e)}, 500)
        else:
            self.send_response(404)
            self.end_headers()

    def _json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def _save_history(self, brand, result):
        try:
            history = []
            if HISTORY_FILE.exists():
                history = json.loads(HISTORY_FILE.read_text())
            history.append({
                "brand": brand,
                "score": result["visibility"].get("overall_score", 0),
                "timestamp": datetime.now().isoformat(),
            })
            # 只保留最近100条
            history = history[-100:]
            HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
            HISTORY_FILE.write_text(json.dumps(history, ensure_ascii=False, indent=2))
        except:
            pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def main():
    port = int(os.environ.get("PORT", 8899))
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"\n🌐 GEO Audit 已启动: http://localhost:{port}")
    print(f"   API: http://localhost:{port}/api/audit")
    print(f"   Ctrl+C 停止\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 已停止")


if __name__ == "__main__":
    main()
