#!/usr/bin/env python3
"""Blog image generator via OpenAI-compatible APIs. Config: scripts/images.yaml"""

import os, sys, json, base64, re, urllib.request, urllib.error, concurrent.futures

SKIP_KEYS = {"reasoning", "reasoning_details", "refusal"}


def resolve(val):
    if isinstance(val, str) and val.startswith("${") and val.endswith("}"):
        v = os.environ.get(val[2:-1])
        if not v:
            print(f"[ERROR] env {val[2:-1]} not set")
            sys.exit(1)
        return v
    return val


def find_images(obj, path="root"):
    results = []
    if isinstance(obj, str):
        if obj.startswith("data:image"):
            results.append((path, "data_uri", obj))
        elif len(obj) > 200 and re.fullmatch(r"[A-Za-z0-9+/=\n\r]+", obj[:500]):
            results.append((path, "raw_b64", obj))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k not in SKIP_KEYS:
                results.extend(find_images(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            results.extend(find_images(v, f"{path}[{i}]"))
    return results


def generate(api_base, api_key, model_id, tag, prompt, out):
    print(f"[{tag}] {model_id} via {api_base} ...")
    url = f"{api_base.rstrip('/')}/chat/completions"
    body = json.dumps({"model": model_id, "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request(url, data=body, headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            result = json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"[{tag}] HTTP {e.code}: {e.read().decode()[:300]}")
        return tag, f"FAILED (HTTP {e.code})"
    except Exception as e:
        return tag, f"FAILED ({e})"

    imgs = find_images(result)
    if not imgs:
        return tag, "FAILED (no image)"
    _, kind, data = imgs[0]
    raw = base64.b64decode(data.split(",", 1)[1] if kind == "data_uri" else data)
    with open(out, "wb") as f:
        f.write(raw)
    print(f"[{tag}] {len(raw):,} bytes -> {out}")
    return tag, f"OK -> {out}"


def main():
    import yaml
    force = "--force" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--force"]
    cfg_path = args[0] if args else os.path.join(os.getcwd(), "scripts", "images.yaml")
    if not os.path.exists(cfg_path):
        print(f"[ERROR] {cfg_path} not found"); sys.exit(1)
    with open(cfg_path) as f:
        cfg = yaml.safe_load(f)

    tasks = []
    for img in cfg["images"]:
        d = os.path.join(os.getcwd(), img["output_dir"])
        os.makedirs(d, exist_ok=True)
        for m in cfg["models"]:
            out = os.path.join(d, f"{img['name']}-{m['label']}.png")
            if os.path.exists(out) and not force:
                print(f"[SKIP] {out}"); continue
            tasks.append((m.get("api_base", "https://openrouter.ai/api/v1"), resolve(m.get("api_key", "${OPENROUTER_API_KEY}")), m["id"], f"{img['name']}/{m['label']}", img["prompt"], out))

    if not tasks:
        print("[INFO] Nothing to do. Use --force to regenerate."); return
    print(f"[INFO] {len(tasks)} task(s)\n")
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(len(tasks), 4)) as pool:
        futs = {pool.submit(generate, *t[:6]): t[3] for t in tasks}
        for f in concurrent.futures.as_completed(futs):
            try: results.append(f.result())
            except Exception as e: results.append((futs[f], f"EXCEPTION: {e}"))
    print(f"\n{'='*50}\nSummary:")
    for tag, msg in sorted(results):
        print(f"  [{tag}] {msg}")


if __name__ == "__main__":
    main()
