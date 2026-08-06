#!/usr/bin/env python3
"""Генерирует graph.json из wikilinks в MD файлах vault."""

import json
import os
import re

import vault_write

DOCS_DIR = "docs"
OUTPUT = os.path.join(DOCS_DIR, "assets", "javascripts", "graph.json")

def get_md_files(root):
    files = []
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if f.endswith(".md"):
                files.append(os.path.join(dirpath, f))
    return files

def slug(path):
    return os.path.splitext(os.path.basename(path))[0]

def parse_wikilinks(text):
    return re.findall(r'\[\[([^\|\]#]+?)(?:\|[^\]]+)?\]\]', text)

def main():
    files = get_md_files(DOCS_DIR)

    # id по slug имени файла
    nodes_map = {}
    for i, f in enumerate(files):
        s = slug(f)
        status = None
        if "01_Assessments" in f:
            with open(f, encoding="utf-8", errors="ignore") as fh:
                frontmatter, _ = vault_write.parse_frontmatter(fh.read())
            if frontmatter:
                status = frontmatter.get("status")
        nodes_map[s] = {"id": str(i), "name": s, "path": f, "symbolSize": 1, "status": status}

    links = []
    for f in files:
        with open(f, encoding="utf-8", errors="ignore") as fh:
            text = fh.read()
        src_slug = slug(f)
        for wl in parse_wikilinks(text):
            # roamlinks-style: ищем по частичному совпадению
            wl_clean = wl.strip()
            target = None
            for s in nodes_map:
                if s == wl_clean or s.startswith(wl_clean) or wl_clean in s:
                    target = s
                    break
            if target and target != src_slug:
                links.append({
                    "source": nodes_map[src_slug]["id"],
                    "target": nodes_map[target]["id"]
                })
                nodes_map[src_slug]["symbolSize"] += 1
                nodes_map[target]["symbolSize"] += 1

    data = {
        "nodes": [{"id": v["id"], "name": v["name"], "symbolSize": min(v["symbolSize"], 30), "value": "/" + v["path"].replace(DOCS_DIR + "/", "").replace(".md", "/"), "status": v["status"]} for v in nodes_map.values()],
        "links": links
    }

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"graph.json: {len(data['nodes'])} узлов, {len(data['links'])} связей")

if __name__ == "__main__":
    main()
