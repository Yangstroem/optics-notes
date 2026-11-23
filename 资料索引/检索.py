"""Search local page text; use the original PDF to verify equations."""

import argparse
from pathlib import Path
import re
import unicodedata


def normalize(text):
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", text)).casefold()


def main():
    parser = argparse.ArgumentParser(description="按关键词检索光学a资料，返回文件和 PDF 页码。")
    parser.add_argument("keywords", nargs="+", help="多个关键词按 AND 匹配")
    parser.add_argument("--book", default="", help="限定文件名，如 1-01 或 光学")
    parser.add_argument("--limit", type=int, default=15)
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit 必须大于零")
    root = Path(__file__).resolve().parent / "全文"
    hits = []
    terms = [normalize(word) for word in args.keywords]
    for path in root.glob("*/*.txt"):
        if normalize(args.book) not in normalize(path.parent.name):
            continue
        text = path.read_text(encoding="utf-8")
        header, _, body = text.partition("\n\n")
        compact = normalize(body)
        if not all(term in compact for term in terms):
            continue
        source = header.splitlines()[0].removeprefix("来源: ")
        priority = 0 if source.startswith("课件/") else 1 if source.startswith("习题/") else 2 if source.startswith("教材/") else 3
        hits.append((priority, source, int(path.stem), header, compact, path))
    hits.sort(key=lambda row: row[:3])
    print(f"共 {len(hits)} 页匹配，显示前 {min(len(hits), args.limit)} 页。")
    for _, _, _, header, body, path in hits[:args.limit]:
        start = max(0, body.find(terms[0]) - 65)
        print(f"\n{header}\n片段: {body[start:start + 240]}\n文本: {path}")


if __name__ == "__main__":
    main()
