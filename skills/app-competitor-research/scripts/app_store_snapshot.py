#!/usr/bin/env python3
"""Snapshot an App Store listing into raw JSON plus Markdown fact files.

Usage:
    python3 -I research/tools/app_store_snapshot.py <bundle-id> <out-dir> [--country cn]

Writes:
    <out-dir>/sources/{lookup,page-data,reviews}.json   raw responses
    <out-dir>/app-store.md                              listing facts
    <out-dir>/app-store-reviews.md                      written reviews, verbatim
    <out-dir>/screenshots/app-store/{iphone,ipad}/      listing screenshots

Fact IDs are derived from stable keys (field name, version string, Apple
review ID) so re-running the snapshot does not renumber existing facts.
"""

import argparse
import datetime
import json
import pathlib
import re
import urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def cell(text):
    return str(text if text is not None else "").replace("|", "\\|").replace("\n", "<br>").strip()


def fetch_lookup(bundle_id, country):
    data = json.loads(get(f"https://itunes.apple.com/lookup?bundleId={bundle_id}&country={country}"))
    if not data["results"]:
        raise SystemExit(f"no App Store listing for {bundle_id} in {country}")
    return data["results"][0]


def fetch_page_data(track_id, country):
    html = get(f"https://apps.apple.com/{country}/app/id{track_id}").decode()
    m = re.search(r'<script type="application/json" id="serialized-server-data">(.*?)</script>', html, re.S)
    return json.loads(m.group(1))["data"][0]["data"]


def fetch_reviews(track_id, country):
    # The RSS feed caps at 10 pages of 50 and only returns reviews with text.
    reviews = []
    for page in range(1, 11):
        url = f"https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={track_id}/sortby=mostrecent/json"
        entries = json.loads(get(url))["feed"].get("entry", [])
        if isinstance(entries, dict):
            entries = [entries]
        if not entries:
            break
        reviews += [
            {
                "id": e["id"]["label"],
                "updated": e["updated"]["label"],
                "rating": int(e["im:rating"]["label"]),
                "version": e["im:version"]["label"],
                "title": e["title"]["label"],
                "content": e["content"]["label"],
            }
            for e in entries
        ]
    return reviews


def artwork_url(art, max_side=1400):
    scale = min(1, max_side / max(art["width"], art["height"]))
    return art["template"].format(w=round(art["width"] * scale), h=round(art["height"] * scale), c="bb", f="jpg")


def annotation_text(item):
    parts = []
    for sub in item.get("items", []):
        if sub.get("$kind") == "linkableText":
            parts.append(sub["linkableText"]["styledText"]["rawText"].replace("**", ""))
        elif sub.get("$kind") == "textPair":
            parts.append(f"{sub['leadingText']}：{sub['trailingText']}")
    return "；".join(p.replace("\n", " ") for p in parts) or item.get("summary", "")


def download_media(shelves, out):
    rows = []
    for key, device in (("product_media_phone_", "iphone"), ("product_media_pad_", "ipad")):
        items = shelves.get(key, {}).get("items", [])
        folder = out / "screenshots" / "app-store" / device
        index = 0
        for item in items:
            index += 1
            if item.get("video"):
                rows.append((device, index, "视频", item["video"]["videoUrl"]))
                continue
            art = item["screenshot"]
            name = f"{index:02d}.jpg"
            folder.mkdir(parents=True, exist_ok=True)
            (folder / name).write_bytes(get(artwork_url(art)))
            rows.append((device, index, f"截图 {art['width']}×{art['height']}", f"screenshots/app-store/{device}/{name}"))
    return rows


def render_listing(lookup, shelves, lockup, media, fetched, country):
    info = {a["title"]: a for a in shelves["information"]["items"]}
    ratings = shelves["productRatings"]["items"][0]
    basics = [
        ("name", "名称", lookup["trackName"]),
        ("subtitle", "副标题", lockup.get("subtitle")),
        ("bundle-id", "bundle ID", lookup["bundleId"]),
        ("track-id", "App ID", lookup["trackId"]),
        ("seller", "开发者", lookup["sellerName"]),
        ("copyright", "版权", info.get("版权", {}).get("summary")),
        ("version", "当前版本", f"{lookup['version']}（{lookup['currentVersionReleaseDate'][:10]}）"),
        ("first-release", "首次发布", lookup["releaseDate"][:10]),
        ("price", "价格", lookup["formattedPrice"]),
        ("genres", "类别", "、".join(lookup.get("genres", []))),
        ("size", "大小", info.get("大小", {}).get("summary")),
        ("compatibility", "兼容性", annotation_text(info["兼容性"]) if "兼容性" in info else lookup.get("minimumOsVersion")),
        ("languages", "语言", annotation_text(info["语言"]) if "语言" in info else ""),
        ("age-rating", "年龄分级", lookup.get("contentAdvisoryRating")),
        ("rating", "评分", f"{ratings['ratingAverage']}，共 {ratings['totalNumberOfRatings']} 个评分"),
        ("rating-histogram", "评分分布（5→1 星）", " / ".join(str(n) for n in ratings["ratingCounts"])),
    ]
    for badge in shelves["informationRibbon"]["items"]:
        if badge.get("type") == "chartPosition":
            basics.append(("chart", "排行榜", f"{badge['caption']} #{badge['content']['position']}"))
    basics.append(("support-url", "开发者网站（商店字段）", lookup.get("sellerUrl") or "未提供"))

    lines = [
        f"# App Store 信息：{lookup['trackName']}",
        "",
        f"来源：[App Store（{country}）]({lookup['trackViewUrl'].split('?')[0]})、iTunes Lookup API、iTunes 评论 RSS。"
        f"抓取时间：{fetched}。原始响应见 `sources/`。本文件由 `research/tools/app_store_snapshot.py` 生成，重新抓取会覆盖。",
        "",
        "编号规则：`AS-<字段>`、`AS-V<版本号>`；评论原文见 [app-store-reviews.md](app-store-reviews.md)。",
        "",
        "## 基本信息",
        "",
        "| 编号 | 项 | 值 |",
        "|---|---|---|",
    ]
    lines += [f"| AS-{key} | {label} | {cell(value)} |" for key, label, value in basics]

    lines += ["", "## 描述原文（AS-description）", "", "```text", lookup.get("description", "").strip(), "```"]

    lines += ["", "## App 内购买（AS-iap）", "", "| 项目 | 价格 |", "|---|---|"]
    iap = info.get("App内购买", {})
    lines += [f"| {cell(s['leadingText'])} | {cell(s['trailingText'])} |" for s in iap.get("items", []) if s.get("$kind") == "textPair"]
    if not iap:
        lines.append("| 无 | |")

    lines += ["", "## 版本历史", "", "商店只展示最近的版本记录，更早版本不在此列。", "", "| 编号 | 版本 | 日期 | 更新说明原文 |", "|---|---|---|---|"]
    history = shelves["mostRecentVersion"]["seeAllAction"]["pageData"]["shelves"][0]["items"]
    for item in history:
        version = item["primarySubtitle"].replace("版本 ", "")
        date = datetime.datetime.strptime(item["secondarySubtitle"][:15], "%a %b %d %Y").date()
        lines.append(f"| AS-V{version} | {version} | {date} | {cell(item['text'])} |")

    lines += ["", "## 隐私标签（AS-privacy）", ""]
    for ptype in shelves["privacyTypes"]["items"]:
        cats = "、".join(c["title"] for c in ptype["categories"])
        lines.append(f"- {ptype['title']}：{ptype['detail']}{cats}")
    access = shelves.get("accessibilityHeader", {}).get("items", [])
    if access:
        text = access[0]["text"]["styledText"]["rawText"].replace("进一步了解", "")
        lines += ["", f"辅助功能（AS-accessibility）：{text}"]
    caps = [c["title"] for c in shelves.get("capabilities", {}).get("items", [])]
    if caps:
        lines += ["", f"支持（AS-capabilities）：{'、'.join(caps)}"]

    lines += ["", "## 商店媒体（AS-media）", "", "| 设备 | 序号 | 类型 | 文件或地址 |", "|---|---|---|---|"]
    lines += [f"| {d} | {i} | {t} | {p} |" for d, i, t, p in media]

    more = shelves.get("moreByDeveloper", {}).get("items", [])
    if more:
        lines += ["", "## 同开发者的其他 App（AS-developer-apps）", ""]
        lines += [f"- {a['title']}（`{a.get('bundleId')}`）：{a.get('subtitle') or ''}" for a in more]
    return "\n".join(lines) + "\n"


def render_reviews(name, reviews, fetched):
    counts = {s: sum(r["rating"] == s for r in reviews) for s in range(5, 0, -1)}
    lines = [
        f"# App Store 评论原文：{name}",
        "",
        f"来源：iTunes 评论 RSS（按时间倒序，最多 500 条，只含有正文的评论）。抓取时间：{fetched}。共 {len(reviews)} 条，"
        + "、".join(f"{s} 星 {n} 条" for s, n in counts.items())
        + "。评论者昵称不收录。评论是用户的说法，不代表对 App 行为的验证。",
        "",
        "编号为 `AS-R<Apple 评论 ID>`。",
        "",
        "| 编号 | 日期 | 版本 | 星级 | 标题 | 正文 |",
        "|---|---|---|---|---|---|",
    ]
    lines += [
        f"| AS-R{r['id']} | {r['updated'][:10]} | {r['version']} | {r['rating']} | {cell(r['title'])} | {cell(r['content'])} |"
        for r in reviews
    ]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle_id")
    parser.add_argument("out_dir", type=pathlib.Path)
    parser.add_argument("--country", default="cn")
    args = parser.parse_args()

    out = args.out_dir
    (out / "sources").mkdir(parents=True, exist_ok=True)
    fetched = datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %z")

    lookup = fetch_lookup(args.bundle_id, args.country)
    page = fetch_page_data(lookup["trackId"], args.country)
    reviews = fetch_reviews(lookup["trackId"], args.country)
    for name, data in (("lookup", lookup), ("page-data", page), ("reviews", reviews)):
        (out / "sources" / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False, indent=1))

    media = download_media(page["shelfMapping"], out)
    listing = render_listing(lookup, page["shelfMapping"], page["lockup"], media, fetched, args.country)
    (out / "app-store.md").write_text(listing)
    (out / "app-store-reviews.md").write_text(render_reviews(lookup["trackName"], reviews, fetched))
    print(f"{lookup['trackName']} {lookup['version']}: {len(reviews)} reviews, {len(media)} media items -> {out}")


if __name__ == "__main__":
    main()
