# backend/generate_manifest.py
import json, os, glob, datetime, pathlib

OUTPUT_DIR = pathlib.Path(__file__).resolve().parents[1] / "frontend" / "output"
REFRESH_SEC = int(os.getenv("REFRESH_SEC", "300"))  # 5 นาที default

def iso_utc_now():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def load_sidecar_meta(img_path: pathlib.Path):
    """
    ถ้ามีไฟล์เมตาคู่กัน เช่น AAPL_5min.meta.json จะอ่าน metrics/last_point_utc มาด้วย
    โครงไฟล์เมตาที่แนะนำ:
    {
      "symbol": "AAPL",
      "interval": "5min",
      "last_point_utc": "2025-10-05T09:25:00Z",
      "metrics": {"close": 173.45, "change": -0.15, "change_pct": -0.09, "volume": 123456}
    }
    """
    meta_path = img_path.with_suffix("").with_suffix(".meta.json")  # ทำให้รองรับ .png/.svg/.webp
    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                pass
    return {}

def infer_symbol_interval(filename: str):
    # รองรับไฟล์รูปแบบ SYMBOL_INTERVAL.ext เช่น AAPL_5min.png
    stem = os.path.splitext(filename)[0]
    parts = stem.split("_", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return stem, "unknown"

def build_manifest():
    charts = []
    patterns = ["*.png", "*.svg", "*.webp"]
    files = []
    for pat in patterns:
        files.extend(OUTPUT_DIR.glob(pat))

    for img in sorted(files):
        meta = load_sidecar_meta(img)
        symbol = meta.get("symbol")
        interval = meta.get("interval")
        if not symbol or not interval:
            s, itv = infer_symbol_interval(img.name)
            symbol = symbol or s
            interval = interval or itv

        # ถ้าไม่มี last_point_utc ใน meta ใช้ mtime ของไฟล์ (แปลงเป็น UTC)
        last_utc = meta.get("last_point_utc")
        if not last_utc:
            ts = datetime.datetime.utcfromtimestamp(img.stat().st_mtime).replace(microsecond=0)
            last_utc = ts.isoformat() + "Z"

        charts.append({
            "symbol": symbol,
            "interval": interval,
            "image": f"output/{img.name}",
            "last_point_utc": last_utc,
            "metrics": meta.get("metrics", {"close": 0, "change": 0, "change_pct": 0, "volume": 0})
        })

    # summary แบบง่าย (ถ้ามี metrics จะคำนวณ top_gainer ให้)
    top = None
    for c in charts:
        cp = (c.get("metrics") or {}).get("change_pct")
        if isinstance(cp, (int, float)):
            if top is None or cp > top["change_pct"]:
                top = {"symbol": c["symbol"], "change_pct": cp}
    summary = {
        "total_symbols": len({c["symbol"] for c in charts}),
        "top_gainer": top or {"symbol": "-", "change_pct": 0.0}
    }

    manifest = {
        "build_id": iso_utc_now(),
        "generated_at_utc": iso_utc_now(),
        "refresh_suggested_sec": REFRESH_SEC,
        "summary": summary,
        "charts": charts,
    }

    # เขียนแบบ atomic
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    tmp = OUTPUT_DIR / "manifest.tmp"
    final = OUTPUT_DIR / "manifest.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    os.replace(tmp, final)
    print(f"[OK] manifest.json written with {len(charts)} chart(s).")

if __name__ == "__main__":
    build_manifest()
