"""Benchmark Venice image generation across models and output formats."""

from __future__ import annotations

import argparse
import base64
import json
import os
import statistics
import time
from dataclasses import dataclass, asdict
from pathlib import Path

import requests
from dotenv import load_dotenv

VENICE_URL = "https://api.venice.ai/api/v1/image/generate"

# ONE prompt for every config. The variable under test must be the only thing
# that changes, or the comparison means nothing.
PROMPT = "a red apple on a wooden table, soft natural lighting"

CONFIGS = [
    ("z-image-turbo", "png"),
    ("z-image-turbo", "webp"),
    ("venice-sd35", "png"),
    ("venice-sd35", "webp"),
    # ("seedream-v5-pro", "png"),   # ~56s per call -- enable deliberately
]


@dataclass
class Run:
    model: str
    fmt: str
    ok: bool
    generation_s: float | None = None
    transfer_s: float | None = None
    total_s: float | None = None
    bytes_: int | None = None
    error: str | None = None


def one_run(api_key: str, model: str, fmt: str, timeout: float = 180.0) -> Run:
    payload = {
        "model": model,
        "prompt": PROMPT,
        "format": fmt,
        "width": 1024,
        "height": 1024,
        "variants": 1,
        "return_binary": False,
        "hide_watermark": True,
    }
    headers = {"Authorization": f"Bearer {api_key}",
               "Content-Type": "application/json"}

    t0 = time.perf_counter()
    try:
        response = requests.post(VENICE_URL, json=payload, headers=headers,
                                 timeout=timeout, stream=True)
        t_headers = time.perf_counter()
        body = response.content
        t_body = time.perf_counter()

        if response.status_code >= 400:
            return Run(model, fmt, ok=False,
                       error=f"HTTP {response.status_code}: {body[:200]!r}")

        image_bytes = base64.b64decode(response.json()["images"][0])
        return Run(model, fmt, ok=True,
                   generation_s=t_headers - t0,
                   transfer_s=t_body - t_headers,
                   total_s=t_body - t0,
                   bytes_=len(image_bytes))
    except Exception as exc:
        return Run(model, fmt, ok=False, error=f"{type(exc).__name__}: {exc}")


def summarize(runs: list[Run]) -> None:
    print(f"\n{'model':<18}{'fmt':<6}{'ok':>7}{'gen med':>10}{'gen min':>9}"
          f"{'gen max':>9}{'xfer med':>10}{'size':>10}")
    print("-" * 79)

    for model, fmt in CONFIGS:
        group = [r for r in runs if r.model == model and r.fmt == fmt]
        if not group:
            continue
        good = [r for r in group if r.ok]
        rate = f"{len(good)}/{len(group)}"
        if not good:
            print(f"{model:<18}{fmt:<6}{rate:>7}   all failed: {group[0].error}")
            continue

        gen = sorted(r.generation_s for r in good)
        xfer = sorted(r.transfer_s for r in good)
        kb = statistics.median(r.bytes_ for r in good) / 1024
        print(f"{model:<18}{fmt:<6}{rate:>7}"
              f"{statistics.median(gen):>9.2f}s{min(gen):>8.2f}s{max(gen):>8.2f}s"
              f"{statistics.median(xfer):>9.2f}s{kb:>8.0f}KB")

    n_ok = len([r for r in runs if r.ok])
    per_config = n_ok / max(len(CONFIGS), 1)
    if per_config < 20:
        print(f"\nNote: ~{per_config:.0f} successful runs per config. "
              f"Report min/median/max; p95 needs >=20 per config.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--out", default="results.json")
    parser.add_argument("--analyze", help="re-analyze existing results, no API calls")
    args = parser.parse_args()

    if args.analyze:
        summarize([Run(**r) for r in json.loads(Path(args.analyze).read_text())])
        return

    load_dotenv()
    api_key = os.getenv("VENICE_API_KEY")
    if not api_key:
        raise SystemExit("VENICE_API_KEY not set (check your .env)")

    results: list[Run] = []
    for model, fmt in CONFIGS:
        print(f"{model}/{fmt}: warm-up...", flush=True)
        one_run(api_key, model, fmt)          # discarded on purpose

        for i in range(args.runs):
            r = one_run(api_key, model, fmt)
            status = f"{r.total_s:.2f}s" if r.ok else f"FAILED ({r.error})"
            print(f"{model}/{fmt}: run {i+1}/{args.runs}  {status}", flush=True)
            results.append(r)

    Path(args.out).write_text(json.dumps([asdict(r) for r in results], indent=2))
    print(f"\nRaw records written to {args.out}")
    summarize(results)


if __name__ == "__main__":
    main()