#!/usr/bin/env python3
"""Generate synthetic comic files with known content for comic/image reader tests.

Every page prints its page number, total pages, pixel size and source file
name, with a colored band on each edge (top red, right green, bottom blue,
left yellow) so screenshots reveal page order, cropping and fitting.

Usage:
    uv run --with pillow python -I generate_comic_materials.py <out-dir>

Requires Pillow and the `7z` binary (Homebrew `sevenzip`) for 7z and
password-protected archives. RAR/CBR cannot be produced without the
proprietary `rar` tool and is skipped.
"""

import io
import pathlib
import shutil
import subprocess
import sys
import tarfile
import zipfile

from PIL import Image, ImageDraw, ImageFont

FONT = "/System/Library/Fonts/Menlo.ttc"
EDGES = {"top": (220, 40, 40), "right": (40, 170, 60), "bottom": (40, 80, 220), "left": (230, 190, 30)}


def page(number, total, size, label, background=(250, 250, 250), margin=0):
    w, h = size
    img = Image.new("RGB", size, (255, 255, 255) if margin else background)
    draw = ImageDraw.Draw(img)
    x0, y0, x1, y1 = margin, margin, w - margin, h - margin
    if margin:
        draw.rectangle([x0, y0, x1, y1], fill=background)
    band = max(12, min(w, h) // 40)
    draw.rectangle([x0, y0, x1, y0 + band], fill=EDGES["top"])
    draw.rectangle([x1 - band, y0, x1, y1], fill=EDGES["right"])
    draw.rectangle([x0, y1 - band, x1, y1], fill=EDGES["bottom"])
    draw.rectangle([x0, y0, x0 + band, y1], fill=EDGES["left"])
    step = max(100, min(w, h) // 10)
    for x in range(x0 + step, x1, step):
        draw.line([x, y0, x, y1], fill=(225, 225, 225), width=2)
    for y in range(y0 + step, y1, step):
        draw.line([x0, y, x1, y], fill=(225, 225, 225), width=2)
    big = ImageFont.truetype(FONT, max(48, min(x1 - x0, 4000) // 4))
    small = ImageFont.truetype(FONT, max(20, min(x1 - x0, 4000) // 30))
    cx, cy = w // 2, h // 2
    draw.text((cx, cy), str(number), font=big, fill=(20, 20, 20), anchor="mm")
    info = f"{number}/{total}  {w}x{h}\n{label}"
    draw.multiline_text((cx, cy + big.size), info, font=small, fill=(60, 60, 60), anchor="ma", align="center")
    # Label halves of landscape pages so spread splitting shows which side is displayed.
    if w > h:
        for half, x in (("L", x0 + (x1 - x0) // 4), ("R", x0 + 3 * (x1 - x0) // 4)):
            draw.text((x, y0 + band * 3), f"{number}-{half}", font=small, fill=(150, 30, 30), anchor="ma")
    # Repeat the page number along a tall strip so any viewport shows it.
    if h > 3 * w:
        for y in range(y0 + step, y1, step * 4):
            draw.text((x0 + band * 2, y), f"P{number} y={y}", font=small, fill=(90, 90, 90))
    return img


def encode(img, fmt="JPEG"):
    buf = io.BytesIO()
    if fmt == "JPEG":
        img.save(buf, "JPEG", quality=85)
    elif fmt == "GIF":
        img.convert("P").save(buf, "GIF")
    else:
        img.save(buf, fmt)
    return buf.getvalue()


def pages(count, size, label, ext="jpg", start=1, **kw):
    fmt = {"jpg": "JPEG", "png": "PNG", "webp": "WEBP", "gif": "GIF"}[ext]
    return [(f"{i:03d}.{ext}", encode(page(i, count, size, label, **kw), fmt)) for i in range(start, start + count)]


def write_zip(path, entries):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_STORED) as zf:
        for name, data in entries:
            zf.writestr(name, data)


def write_gbk_zip(path, entries):
    # zipfile always flags non-ASCII names as UTF-8, so write same-length ASCII
    # placeholders and patch in the raw GBK bytes afterwards.
    raw = {}
    for k, (name, _) in enumerate(entries):
        gbk = name.encode("gbk")
        placeholder = f"{k:0{len(gbk)}d}".encode()
        raw[placeholder] = gbk
    write_zip(path, [(p.decode(), data) for p, (_, data) in zip(raw, entries)])
    blob = path.read_bytes()
    for placeholder, gbk in raw.items():
        blob = blob.replace(placeholder, gbk)
    path.write_bytes(blob)


def write_dir(path, entries):
    for name, data in entries:
        target = path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


def write_7z(path, entries, password=None, fmt="7z"):
    staging = path.parent / f".stage-{path.name}"
    write_dir(staging, entries)
    args = ["7z", "a", f"-t{fmt}", str(path.resolve()), "."]
    if password:
        args.insert(3, f"-p{password}")
    subprocess.run(args, cwd=staging, check=True, stdout=subprocess.DEVNULL)
    shutil.rmtree(staging)


def write_tar(path, entries):
    with tarfile.open(path, "w") as tf:
        for name, data in entries:
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))


def write_pdf(path, count, size, label):
    imgs = [page(i, count, size, label) for i in range(1, count + 1)]
    imgs[0].save(path, "PDF", save_all=True, append_images=imgs[1:], resolution=150)


def write_epub(path, entries, title):
    names = [n for n, _ in entries]
    manifest = "\n".join(f'<item id="i{k}" href="{n}" media-type="image/jpeg"/>' for k, n in enumerate(names))
    manifest += "\n" + "\n".join(f'<item id="p{k}" href="p{k}.xhtml" media-type="application/xhtml+xml"/>' for k in range(len(names)))
    spine = "\n".join(f'<itemref idref="p{k}"/>' for k in range(len(names)))
    opf = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="id">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:identifier id="id">synthetic-epub</dc:identifier>
<dc:title>{title}</dc:title><dc:language>zh</dc:language>
<meta property="rendition:layout">pre-paginated</meta></metadata>
<manifest>{manifest}<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/></manifest>
<spine>{spine}</spine></package>"""
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        zf.writestr("META-INF/container.xml", '<?xml version="1.0"?><container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>')
        zf.writestr("OEBPS/content.opf", opf)
        zf.writestr("OEBPS/nav.xhtml", '<?xml version="1.0"?><html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops"><body><nav epub:type="toc"><ol><li><a href="p0.xhtml">1</a></li></ol></nav></body></html>')
        for k, (name, data) in enumerate(entries):
            zf.writestr(f"OEBPS/{name}", data)
            zf.writestr(f"OEBPS/p{k}.xhtml", f'<?xml version="1.0"?><html xmlns="http://www.w3.org/1999/xhtml"><body><img src="{name}"/></body></html>')


def main():
    out = pathlib.Path(sys.argv[1])
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    portrait = (1500, 2250)
    manifest = []

    def add(name, purpose):
        manifest.append((name, purpose))

    # Formats: identical 10-page content in each container.
    base = pages(10, portrait, "format")
    for ext in ("cbz", "zip"):
        write_zip(out / f"F01-格式-{ext}.{ext}", base)
        add(f"F01-格式-{ext}.{ext}", f"{ext.upper()} 容器，10 页竖图")
    write_7z(out / "F01-格式-7z.7z", base)
    write_7z(out / "F01-格式-cb7.cb7", base)
    write_tar(out / "F01-格式-tar.tar", base)
    write_tar(out / "F01-格式-cbt.cbt", base)
    write_pdf(out / "F01-格式-pdf.pdf", 10, portrait, "pdf")
    write_epub(out / "F01-格式-epub.epub", base, "F01 格式 EPUB")
    write_dir(out / "F01-格式-文件夹", base)
    for name in ("7z", "cb7", "tar", "cbt", "pdf", "epub"):
        add(f"F01-格式-{name}.{name}", f"{name.upper()} 容器，10 页竖图")
    add("F01-格式-文件夹/", "散图文件夹，10 页竖图")

    # Image encodings mixed in one book.
    mixed = []
    for i, ext in enumerate(("jpg", "png", "webp", "gif", "jpg", "png"), start=1):
        fmt = {"jpg": "JPEG", "png": "PNG", "webp": "WEBP", "gif": "GIF"}[ext]
        mixed.append((f"{i:03d}.{ext}", encode(page(i, 6, portrait, f"encoding {ext}"), fmt)))
    write_zip(out / "F02-混合图片编码.cbz", mixed)
    add("F02-混合图片编码.cbz", "同一本内混合 JPG/PNG/WebP/GIF")

    # Page order and naming.
    natural = [(f"{i}.jpg", data) for i, (_, data) in enumerate(pages(12, portrait, "natural sort"), start=1)]
    write_zip(out / "O01-自然排序-1到12.cbz", natural)
    add("O01-自然排序-1到12.cbz", "文件名 1.jpg…12.jpg，无前导零，检查 2 是否排在 10 之前")
    shuffled = pages(8, portrait, "zip entry order")
    write_zip(out / "O02-压缩包内条目逆序.cbz", list(reversed(shuffled)))
    add("O02-压缩包内条目逆序.cbz", "条目在压缩包中按 008…001 存放，文件名有序")
    write_gbk_zip(out / "O03-GBK文件名.zip", [(f"第{i:02d}页.jpg", d) for i, (_, d) in enumerate(pages(5, portrait, "gbk names"), start=1)])
    add("O03-GBK文件名.zip", "条目名为 GBK 编码中文、无 UTF-8 标志")

    # Layout: spreads, cover, margins.
    spread = []
    for i in range(1, 11):
        size = (3000, 2250) if i in (4, 7) else portrait
        spread.append((f"{i:03d}.jpg", encode(page(i, 10, size, "spread at 4,7" if size[0] > size[1] else "single"))))
    write_zip(out / "L01-跨页-第4和7页为横图.cbz", spread)
    add("L01-跨页-第4和7页为横图.cbz", "第 4、7 页是 3000×2250 横向跨页，其余竖图；用于双页、拆分、封面单页")
    write_zip(out / "L02-白边-四周留白.cbz", pages(6, portrait, "white margin 150px", margin=150))
    add("L02-白边-四周留白.cbz", "每页四周 150px 纯白边，用于白边裁剪")
    write_zip(out / "L03-奇数页数-9页.cbz", pages(9, portrait, "odd count"))
    add("L03-奇数页数-9页.cbz", "9 页，双页模式下末页单独")
    write_zip(out / "L04-深色背景.cbz", pages(6, portrait, "dark page", background=(30, 30, 30)))
    add("L04-深色背景.cbz", "深色底页面，观察背景色与页面边界")

    # Webtoon and large images.
    write_zip(out / "W01-条漫-800x12000x8.cbz", pages(8, (800, 12000), "webtoon strip"))
    add("W01-条漫-800x12000x8.cbz", "8 张 800×12000 长条，用于条漫检测与连续滚动")
    write_zip(out / "W02-条漫-宽度不一.cbz", [(f"{i:03d}.jpg", encode(page(i, 6, (w, 6000), "webtoon width"))) for i, w in enumerate((720, 800, 1080, 720, 1200, 800), start=1)])
    add("W02-条漫-宽度不一.cbz", "6 张长条，宽度 720–1200 不一")
    write_pdf(out / "W03-PDF条漫.pdf", 4, (800, 8000), "pdf webtoon")
    add("W03-PDF条漫.pdf", "4 页 800×8000 的 PDF 长页（版本 2.1.2 曾修复 PDF 条漫白屏）")
    write_zip(out / "H01-超大图-8000x12000.cbz", pages(3, (8000, 12000), "huge page"))
    add("H01-超大图-8000x12000.cbz", "3 张 8000×12000（9600 万像素）JPEG")
    write_zip(out / "H02-超长图-1000x60000.cbz", pages(1, (1000, 60000), "very tall", ext="png"))
    add("H02-超长图-1000x60000.cbz", "1 张 1000×60000 PNG")
    write_zip(out / "H03-页数多-300页.cbz", pages(300, (750, 1125), "many pages"))
    add("H03-页数多-300页.cbz", "300 页小图，用于进度条、跳页、缩略图")

    # Structure: nested folders, chapters, collections.
    nested = []
    for vol in (1, 2):
        for ch in (1, 2, 3):
            for name, data in pages(3, portrait, f"vol{vol} ch{ch}"):
                nested.append((f"S01-多级目录/第{vol}卷/第{ch}话/{name}", data))
    write_zip(out / "S01-多级目录-2卷x3话.zip", nested)
    add("S01-多级目录-2卷x3话.zip", "压缩包内 第1卷/第1话/001.jpg 形式的两级目录")
    write_dir(out, nested)
    add("S01-多级目录/", "同上结构的文件夹形式")
    series = out / "S02-系列-分卷文件"
    series.mkdir()
    for vol in range(1, 6):
        write_zip(series / f"测试系列 第{vol:02d}卷.cbz", pages(4, portrait, f"series vol {vol}"))
    add("S02-系列-分卷文件/", "文件夹内 5 个分卷 CBZ，用于合集整理")
    write_zip(out / "S03-带ComicInfo.cbz", pages(5, portrait, "comicinfo") + [("ComicInfo.xml", '<?xml version="1.0"?><ComicInfo><Title>ComicInfo 标题</Title><Series>ComicInfo 系列</Series><Number>3</Number><Writer>测试作者</Writer><Manga>YesAndRightToLeft</Manga><PageCount>5</PageCount></ComicInfo>'.encode())])
    add("S03-带ComicInfo.cbz", "含 ComicInfo.xml（标题、系列、作者、右到左），检查元数据是否被读取")

    # Library volume: many small books with varied names.
    shelf = out / "B01-书架批量-40本"
    shelf.mkdir()
    titles = ["Alpha", "beta", "Γάμμα", "あいうえお", "가나다", "中文书名", "长书名" * 8, "123数字开头", "_下划线", "Emoji🙂"]
    for k in range(40):
        write_zip(shelf / f"{titles[k % len(titles)]}-{k:02d}.cbz", pages(3, (600, 900), f"shelf {k}"))
    add("B01-书架批量-40本/", "40 本 3 页小书，书名含多种文字、超长名、数字和符号开头")

    # Failure cases.
    good = pages(5, portrait, "broken image at 3")
    good[2] = (good[2][0], good[2][1][:2000])
    write_zip(out / "E01-第3页图片损坏.cbz", good)
    add("E01-第3页图片损坏.cbz", "第 3 页 JPEG 被截断")
    data = (out / "F01-格式-cbz.cbz").read_bytes()
    (out / "E02-压缩包截断.cbz").write_bytes(data[: len(data) // 2])
    add("E02-压缩包截断.cbz", "CBZ 文件被截去后半")
    write_zip(out / "E03-空压缩包.cbz", [("readme.txt", b"no images")])
    add("E03-空压缩包.cbz", "只含一个 txt，没有图片")
    write_7z(out / "E04-密码zip-密码1234.zip", pages(4, portrait, "password zip"), password="1234", fmt="zip")
    write_7z(out / "E05-密码7z-密码1234.7z", pages(4, portrait, "password 7z"), password="1234")
    add("E04-密码zip-密码1234.zip", "ZIP 加密，密码 1234")
    add("E05-密码7z-密码1234.7z", "7z 加密，密码 1234")

    lines = ["# 测试素材清单", "", "由 `generate_comic_materials.py` 生成，生成命令见脚本开头。每页印有页码、总页数、像素尺寸和标签；四边色带：上红、右绿、下蓝、左黄；横图左右半边分别标 `<页码>-L`、`<页码>-R`。", "", "| 文件 | 内容 |", "|---|---|"]
    lines += [f"| `{n}` | {p} |" for n, p in manifest]
    (out / "MANIFEST.md").write_text("\n".join(lines) + "\n")
    print(f"{len(manifest)} items -> {out}")


if __name__ == "__main__":
    main()
