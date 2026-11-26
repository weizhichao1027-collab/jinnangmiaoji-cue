#!/usr/bin/env python3
"""Resize approved promotional PNGs into the website's release screenshots.

Requires Pillow. From the full product workspace, run this script directly.
From a standalone website checkout, pass --source-root pointing to the product
workspace's docs/designs/store-previews-2026-11-12 directory.
"""

import argparse
import hashlib
import io
import json
from pathlib import Path

from PIL import Image, __version__ as pillow_version


SITE_ROOT = Path(__file__).resolve().parent
SOURCE_DIRECTORY = Path("docs/designs/store-previews-2026-11-12")
OUTPUT_ROOT = SITE_ROOT / "shots/release-20261114"
LOCALES = (
    "zh-Hans", "zh-Hant", "en", "ja", "ko", "es", "fr", "de",
    "pt-BR", "ru", "ar", "hi", "id",
)
JPEG_OPTIONS = {
    "format": "JPEG",
    "quality": 90,
    "subsampling": 0,
    "progressive": True,
    "optimize": True,
}


def source_specs():
    """Keep the chosen theme and exact source dimensions explicit."""
    result = []
    for locale in LOCALES:
        for index, theme in enumerate(("01-hero", "02-notes", "03-history"), 1):
            result.append((
                "mac", locale,
                Path(f"mac/screenshots/{locale}/{theme}.png"),
                Path(f"mac/{locale}/{index:02}.jpg"),
                (2560, 1600), (1280, 800), theme,
            ))
        for index, theme in enumerate(("03-record", "04-replay", "06-summary-export"), 1):
            result.append((
                "iphone", locale,
                Path(f"iphone/exports/{locale}/{theme}-{locale}.png"),
                Path(f"iphone/{locale}/{index:02}.jpg"),
                (1320, 2868), (660, 1434), theme,
            ))
        result.append((
            "ipad", locale,
            Path(f"wide/ipad/exports/{locale}/06-summary-export.png"),
            Path(f"ipad/{locale}/01.jpg"),
            (2752, 2064), (1032, 774), "06-summary-export",
        ))
        result.append((
            "watch", locale,
            Path(f"watch/watch/exports/{locale}/02-start.png"),
            Path(f"watch/{locale}/01.jpg"),
            (1248, 1488), (416, 496), "02-start",
        ))
    return result


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def write_atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        temporary.write_bytes(data)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-root", type=Path,
        default=SITE_ROOT.parent / SOURCE_DIRECTORY,
        help="Directory containing mac/, iphone/, wide/ and watch/ source assets.",
    )
    args = parser.parse_args()
    source_root = args.source_root.resolve()
    specs = source_specs()
    missing = [str(source) for _, _, source, *_ in specs if not (source_root / source).is_file()]
    if missing:
        parser.error("Missing source assets under --source-root\n" + "\n".join(missing))

    # Validate every source before replacing any website asset.
    for _, _, source, _, expected, target, _ in specs:
        with Image.open(source_root / source) as image:
            if image.format != "PNG" or image.mode != "RGB" or image.size != expected:
                raise ValueError(f"Unexpected source format, mode or dimensions: {source}")
            if expected[0] * target[1] != expected[1] * target[0]:
                raise ValueError(f"Aspect ratio mismatch: {source}")
            image.verify()

    entries = []
    for platform, locale, source, output, expected, target, theme in specs:
        source_bytes = (source_root / source).read_bytes()
        with Image.open(io.BytesIO(source_bytes)) as image:
            resized = image.resize(target, Image.Resampling.LANCZOS)
            encoded = io.BytesIO()
            resized.save(encoded, **JPEG_OPTIONS)
        output_bytes = encoded.getvalue()
        with Image.open(io.BytesIO(output_bytes)) as image:
            if image.format != "JPEG" or image.mode != "RGB" or image.size != target:
                raise ValueError(f"Invalid output: {output}")
            image.verify()
        write_atomic(OUTPUT_ROOT / output, output_bytes)
        entries.append({
            "platform": platform,
            "locale": locale,
            "theme": theme,
            "source": source.as_posix(),
            "sourceSha256": sha256(source_bytes),
            "sourceDimensions": list(expected),
            "sourceBytes": len(source_bytes),
            "output": output.as_posix(),
            "outputSha256": sha256(output_bytes),
            "outputDimensions": list(target),
            "outputBytes": len(output_bytes),
        })

    actual = {path.relative_to(OUTPUT_ROOT).as_posix() for path in OUTPUT_ROOT.rglob("*.jpg")}
    expected_outputs = {entry["output"] for entry in entries}
    if actual != expected_outputs or len(entries) != 104:
        raise ValueError("Release screenshot coverage must be exactly 104 JPEGs")
    for entry in entries:
        data = (OUTPUT_ROOT / entry["output"]).read_bytes()
        if sha256(data) != entry["outputSha256"]:
            raise ValueError(f"Output hash verification failed: {entry['output']}")

    manifest = {
        "schemaVersion": 1,
        "releaseDate": "2026-11-14",
        "sourceRoot": SOURCE_DIRECTORY.as_posix(),
        "sourcePathConvention": "Each source is relative to sourceRoot in the product workspace.",
        "outputPathConvention": "Each output is relative to this manifest's directory.",
        "generator": "prepare-release-assets.py",
        "pillowVersion": pillow_version,
        "resampling": "LANCZOS, proportional resize of the complete image",
        "jpeg": {key: value for key, value in JPEG_OPTIONS.items() if key != "format"},
        "locales": list(LOCALES),
        "imageCount": len(entries),
        "totalBytes": sum(entry["outputBytes"] for entry in entries),
        "evidenceStatement": {
            "zh-Hans": "沿用最新商店宣传成品及实际应用组件画面，笔记、纪要、录音时长、重点和接收状态含合成示例。画面用于展示界面与功能，不构成识别准确率、模型质量、设备间传输或电池续航实测。",
            "en": "These promotional images reuse the latest store artwork and captured app components. Notes, summaries, durations, highlights and receipt states include synthetic examples. They demonstrate the interface and features and provide no measured recognition accuracy, model quality, device-transfer or battery-life results.",
        },
        "sourceEvidence": [
            "mac/README.md",
            "watch/README.md",
            "wide/README.md",
            "evidence/button-refresh-20261112/README.md",
        ],
        "images": entries,
    }
    write_atomic(OUTPUT_ROOT / "manifest.json", (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode())
    print(f"Verified {len(entries)} screenshots across {len(LOCALES)} locales, {manifest['totalBytes']:,} bytes")


def mobile_20261126_specs():
    """iPhone, iPad and Watch frames that match the live 1.1.3 store set."""
    result = []
    themes = (
        (1, "02-transcript", "02-transcript-{locale}.png"),
        (2, "04-replay", "04-replay-{locale}.png"),
        (3, "06-summary-export", "06-summary-export-{locale}.png"),
    )
    for locale in LOCALES:
        for index, theme, name in themes:
            result.append((
                "iphone", locale, theme,
                Path(f"iphone/exports/{locale}/{name.format(locale=locale)}"),
                Path(f"iphone/{locale}/{index:02}.jpg"),
                (1320, 2868), (660, 1434),
            ))
        result.append((
            "ipad", locale, "02-transcript",
            Path(f"wide/ipad/exports/{locale}/02-transcript.png"),
            Path(f"ipad/{locale}/01.jpg"),
            (2752, 2064), (1032, 774),
        ))
        result.append((
            "watch", locale, "02-start",
            Path(f"watch/watch/exports/{locale}/02-start.png"),
            Path(f"watch/{locale}/01.jpg"),
            (1248, 1488), (416, 496),
        ))
    return result


def build_mobile_20261126(source_root):
    output_root = SITE_ROOT / "shots/release-20261126"
    specs = mobile_20261126_specs()
    missing = [str(item[3]) for item in specs if not (source_root / item[3]).is_file()]
    if missing:
        raise SystemExit("Missing 1.1.3 screenshot sources:\n" + "\n".join(missing))
    entries = []
    for platform, locale, theme, source, output, expected, target in specs:
        source_bytes = (source_root / source).read_bytes()
        with Image.open(io.BytesIO(source_bytes)) as image:
            if image.format != "PNG" or image.size != expected:
                raise ValueError(f"Unexpected source: {source} {image.format} {image.size}")
            if image.mode != "RGB":
                image = image.convert("RGB")
            resized = image.resize(target, Image.Resampling.LANCZOS)
            encoded = io.BytesIO()
            resized.save(encoded, **JPEG_OPTIONS)
        output_bytes = encoded.getvalue()
        with Image.open(io.BytesIO(output_bytes)) as image:
            if image.format != "JPEG" or image.mode != "RGB" or image.size != target:
                raise ValueError(f"Invalid output: {output}")
        write_atomic(output_root / output, output_bytes)
        entries.append({
            "platform": platform,
            "locale": locale,
            "theme": theme,
            "source": source.as_posix(),
            "sourceSha256": sha256(source_bytes),
            "sourceDimensions": list(expected),
            "output": output.as_posix(),
            "outputSha256": sha256(output_bytes),
            "outputDimensions": list(target),
            "outputBytes": len(output_bytes),
        })
    actual = {path.relative_to(output_root).as_posix() for path in output_root.rglob("*.jpg")}
    expected_outputs = {entry["output"] for entry in entries}
    if actual != expected_outputs or len(entries) != 65:
        raise ValueError(f"Expected 65 mobile screenshots, found {len(entries)} entries and {len(actual)} files")
    manifest = {
        "schemaVersion": 1,
        "releaseDate": "2026-11-26",
        "storeVersion": "iOS 1.1.3",
        "sourceRoot": "docs/designs/store-previews-2026-11-24",
        "keptMacScreenshots": "shots/release-20261114/mac",
        "generator": "prepare-release-assets.py --mobile-20261126",
        "pillowVersion": pillow_version,
        "imageCount": len(entries),
        "totalBytes": sum(entry["outputBytes"] for entry in entries),
        "evidenceStatement": {
            "zh-Hans": "iPhone、iPad 与 Apple Watch 画面来自已上架 1.1.3 使用的 2026-11-24 商店图。Mac 网页继续使用仍在销售的 1.2.3 画面。笔记、纪要和时长含合成示例。",
            "en": "iPhone, iPad and Apple Watch images come from the 2026-11-24 store artwork used by the live 1.1.3 release. Mac images on the site remain the live 1.2.3 artwork. Notes, summaries and durations include synthetic examples.",
        },
        "images": entries,
    }
    write_atomic(output_root / "manifest.json", (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode())
    print(f"Verified {len(entries)} live 1.1.3 screenshots, {manifest['totalBytes']:,} bytes")


def main_cli():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=SITE_ROOT.parent / SOURCE_DIRECTORY)
    parser.add_argument("--mobile-20261126", action="store_true")
    args = parser.parse_args()
    if args.mobile_20261126:
        source = args.source_root
        if source == (SITE_ROOT.parent / SOURCE_DIRECTORY).resolve() or source == SITE_ROOT.parent / SOURCE_DIRECTORY:
            source = SITE_ROOT.parent / "docs/designs/store-previews-2026-11-24"
        build_mobile_20261126(source.resolve())
        return
    main()


if __name__ == "__main__":
    main_cli()
