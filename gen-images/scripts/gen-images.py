#!/usr/bin/env python3
"""
Blog image generator via OpenRouter image models.

Usage:
    export OPENROUTER_API_KEY="sk-or-v1-..."
    python3 gen-images.py                        # default: scripts/images.yaml in CWD
    python3 gen-images.py path/to/config.yaml    # custom config
    python3 gen-images.py --force                 # regenerate existing images

Config YAML format — see templates/images.yaml.example in the skill directory.
"""

import os
import sys
import json
import base64
import re
import urllib.request
import urllib.error
import concurrent.futures

SKIP_KEYS = {"reasoning", "reasoning_details", "refusal"}


def find_b64_images(obj, path="root"):
    results = []
    if isinstance(obj, str):
        if obj.startswith("data:image"):
            results.append((path, "data_uri", obj))
        elif len(obj) > 200 and re.fullmatch(r"[A-Za-z0-9+/=\n\r]+", obj[:500]):
            results.append((path, "raw_b64", obj))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k in SKIP_KEYS:
                continue
            results.extend(find_b64_images(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            results.extend(find_b64_images(v, f"{path}[{i}]"))
    return results


def call_model(api_key, model_id, model_label, prompt, output_png):
    tag = f"[{model_label}]"
    print(f"{tag} Calling {model_id} ...")

    body = json.dumps({
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()

    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            result = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        msg = e.read().decode()[:500]
        print(f"{tag} HTTP {e.code}: {msg}")
        return model_label, f"FAILED (HTTP {e.code})"
    except Exception as e:
        print(f"{tag} Request error: {e}")
        return model_label, f"FAILED ({e})"

    choices = result.get("choices", [])
    if not choices:
        print(f"{tag} No choices. Keys: {list(result.keys())}")
        return model_label, "FAILED (no choices)"

    finish = choices[0].get("finish_reason", "?")
    print(f"{tag} finish_reason={finish}")

    images = find_b64_images(result)
    if not images:
        print(f"{tag} No image data found in response.")
        return model_label, "FAILED (no image)"

    print(f"{tag} Found {len(images)} image(s)")
    path, kind, data_str = images[0]
    print(f"{tag} Extracting from: {path} ({kind})")

    if kind == "data_uri":
        _, b64_part = data_str.split(",", 1)
        img_bytes = base64.b64decode(b64_part)
    elif kind == "raw_b64":
        img_bytes = base64.b64decode(data_str)
    else:
        return model_label, f"FAILED (unknown kind: {kind})"

    magic = img_bytes[:4]
    if magic == b"\x89PNG":
        fmt = "PNG"
    elif magic[:2] == b"\xff\xd8":
        fmt = "JPEG"
    elif magic == b"RIFF":
        fmt = "WebP"
    else:
        fmt = f"unknown ({magic.hex()})"
    print(f"{tag} Format: {fmt}, {len(img_bytes):,} bytes")

    with open(output_png, "wb") as f:
        f.write(img_bytes)
    print(f"{tag} Saved to {output_png}")
    return model_label, f"OK -> {output_png} ({len(img_bytes):,} bytes)"


def main():
    try:
        import yaml
    except ImportError:
        print("[ERROR] pyyaml not installed. Run: pip3 install pyyaml")
        sys.exit(1)

    force = "--force" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--force"]

    # Default: scripts/images.yaml relative to CWD (project root)
    default_config = os.path.join(os.getcwd(), "scripts", "images.yaml")
    config_path = args[0] if args else default_config

    if not os.path.exists(config_path):
        print(f"[ERROR] Config not found: {config_path}")
        print(f"[HINT] Create a config file at scripts/images.yaml")
        sys.exit(1)

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("[ERROR] OPENROUTER_API_KEY not set")
        print("[HINT] export OPENROUTER_API_KEY=\"sk-or-v1-...\"")
        print("[HINT] Get a key at https://openrouter.ai/keys")
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)

    models = config["models"]
    images = config["images"]
    project_root = os.getcwd()

    tasks = []
    for img in images:
        name = img["name"]
        prompt = img["prompt"]
        abs_output_dir = os.path.join(project_root, img["output_dir"])
        os.makedirs(abs_output_dir, exist_ok=True)
        for model in models:
            mid = model["id"]
            mlabel = model["label"]
            out_png = os.path.join(abs_output_dir, f"{name}-{mlabel}.png")
            if os.path.exists(out_png) and not force:
                print(f"[SKIP] {out_png} already exists")
                continue
            tasks.append((mid, mlabel, prompt, out_png, name))

    if not tasks:
        print("[INFO] Nothing to generate. All images exist. Use --force to regenerate.")
        return

    print(f"[INFO] {len(tasks)} generation task(s) across {len(models)} model(s)")
    print(f"[INFO] This may take 30-120 seconds per image...\n")

    max_workers = min(len(tasks), len(models))
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {}
        for mid, mlabel, prompt, out_png, img_name in tasks:
            tag = f"{img_name}/{mlabel}"
            fut = pool.submit(call_model, api_key, mid, tag, prompt, out_png)
            futures[fut] = tag
        for fut in concurrent.futures.as_completed(futures):
            tag = futures[fut]
            try:
                label, msg = fut.result()
            except Exception as e:
                label, msg = tag, f"EXCEPTION: {e}"
            results.append((label, msg))

    print(f"\n{'='*60}")
    print("Summary:")
    for label, msg in sorted(results):
        print(f"  [{label}] {msg}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
