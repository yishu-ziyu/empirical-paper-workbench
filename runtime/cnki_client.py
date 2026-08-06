"""CNKI search via Playwright + Chrome CDP (cookjohn/cnki-skills approach).

Requires Chrome launched with remote debugging, e.g.:
  Google Chrome --remote-debugging-port=9333 --user-data-dir=$HOME/.cache/cnki-chrome-profile-9333

Does not solve captcha; returns error='captcha' for human intervention.
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any

DEFAULT_CDP = "http://127.0.0.1:9333"

SEARCH_JS = """(q) => {
  return new Promise(async (resolve) => {
    const wait = (pred, max=50) => new Promise((r,j) => {
      let n=0; const c=()=>{ if(pred()) r(); else if(++n>max) j('timeout'); else setTimeout(c,400); }; c();
    });
    try {
      await wait(() => document.querySelector('input.search-input'));
      const outer = document.querySelector('#tcaptcha_transform_dy');
      if (outer && outer.getBoundingClientRect().top >= 0) return resolve({error:'captcha'});
      const input = document.querySelector('input.search-input');
      input.focus();
      input.value = q;
      input.dispatchEvent(new Event('input', {bubbles:true}));
      document.querySelector('input.search-btn')?.click();
      await wait(() => document.body.innerText.includes('条结果') || document.body.innerText.includes('检索结果'));
      await new Promise(r => setTimeout(r, 700));
      const outer2 = document.querySelector('#tcaptcha_transform_dy');
      if (outer2 && outer2.getBoundingClientRect().top >= 0) return resolve({error:'captcha'});
      const rows = document.querySelectorAll('.result-table-list tbody tr');
      const checkboxes = document.querySelectorAll('.result-table-list tbody input.cbItem');
      const results = Array.from(rows).map((row, i) => {
        const titleLink = row.querySelector('td.name a.fz14');
        const authors = Array.from(row.querySelectorAll('td.author a.KnowledgeNetLink') || []).map(a => a.innerText?.trim());
        return {
          n: i+1,
          title: titleLink?.innerText?.trim() || '',
          href: titleLink?.href || '',
          exportId: checkboxes[i]?.value || '',
          authors: authors.join('; '),
          journal: row.querySelector('td.source a')?.innerText?.trim() || '',
          date: row.querySelector('td.date')?.innerText?.trim() || '',
          citations: row.querySelector('td.quote')?.innerText?.trim() || '',
          downloads: row.querySelector('td.download')?.innerText?.trim() || '',
        };
      });
      resolve({
        query: q,
        total: document.querySelector('.pagerTitleCell')?.innerText?.match(/([\\d,]+)/)?.[1] || '0',
        page: document.querySelector('.countPageMark')?.innerText || '1/1',
        results,
      });
    } catch (e) {
      resolve({error: String(e)});
    }
  });
}"""


def search_queries(
    queries: list[str],
    *,
    cdp_url: str = DEFAULT_CDP,
    out_dir: Path | None = None,
    sleep_s: float = 2.0,
) -> dict[str, Any]:
    from playwright.sync_api import sync_playwright

    out_dir = Path(out_dir) if out_dir else Path("litreview/cnki")
    out_dir.mkdir(parents=True, exist_ok=True)
    by_title: dict[str, dict] = {}
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(cdp_url)
        ctx = browser.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto("https://kns.cnki.net/kns8s/search", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(1000)
        for q in queries:
            res = page.evaluate(SEARCH_JS, q)
            if res.get("error") == "captcha":
                (out_dir / "CAPTCHA_NEEDED.txt").write_text(
                    "Solve CNKI captcha in Chrome, then re-run.\n", encoding="utf-8"
                )
                return {"error": "captcha", "partial": list(by_title.values())}
            safe = re.sub(r"[^\w\u4e00-\u9fff]+", "_", q)[:40]
            (out_dir / f"search_{safe}.json").write_text(
                json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            for it in res.get("results") or []:
                t = it.get("title") or ""
                if t:
                    by_title[t] = {**it, "query": q}
            time.sleep(sleep_s)
    pack = {
        "source": "cnki_client",
        "queries": queries,
        "unique_titles": len(by_title),
        "results": list(by_title.values()),
    }
    (out_dir / "last_search_pack.json").write_text(
        json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return pack
