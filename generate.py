#!/usr/bin/env python3
"""Generate a sitemap.xml for the static HTML pages in this project."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlsplit
from xml.etree import ElementTree

SITEMAP_NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"
ElementTree.register_namespace("", SITEMAP_NAMESPACE)


def parse_base_url(value: str) -> str:
    """Validate and normalize the public base URL of the deployed site."""
    parsed = urlsplit(value)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.netloc
        or parsed.query
        or parsed.fragment
    ):
        raise argparse.ArgumentTypeError(
            "base URL must be an absolute HTTP(S) URL without a query or fragment"
        )
    return value.rstrip("/")


def build_sitemap(site_dir: Path, base_url: str) -> ElementTree.Element:
    """Build a sitemap containing each HTML file under site_dir."""
    root = ElementTree.Element(f"{{{SITEMAP_NAMESPACE}}}urlset")

    excluded_dirs = {".git", ".venv", "__pycache__"}
    html_files = sorted(
        path
        for path in site_dir.rglob("*.html")
        if not any(part in excluded_dirs for part in path.relative_to(site_dir).parts)
    )

    for html_file in html_files:
        relative_path = html_file.relative_to(site_dir).as_posix()
        location = f"{base_url}/{quote(relative_path, safe='/')}"
        last_modified = datetime.fromtimestamp(
            html_file.stat().st_mtime, tz=timezone.utc
        ).date().isoformat()

        url = ElementTree.SubElement(root, f"{{{SITEMAP_NAMESPACE}}}url")
        ElementTree.SubElement(
            url, f"{{{SITEMAP_NAMESPACE}}}loc"
        ).text = location
        ElementTree.SubElement(
            url, f"{{{SITEMAP_NAMESPACE}}}lastmod"
        ).text = last_modified

    return root


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create sitemap.xml for the HTML pages in a GitHub Pages site."
    )
    parser.add_argument(
        "--base-url",
        required=True,
        type=parse_base_url,
        help="public site URL, e.g. https://username.github.io/repository",
    )
    parser.add_argument(
        "--directory",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="site directory to scan (defaults to the directory containing this script)",
    )
    args = parser.parse_args()

    site_dir = args.directory.resolve()
    if not site_dir.is_dir():
        parser.error(f"site directory does not exist: {site_dir}")

    sitemap = build_sitemap(site_dir, args.base_url)
    output_path = site_dir / "sitemap.xml"
    ElementTree.ElementTree(sitemap).write(
        output_path, encoding="utf-8", xml_declaration=True
    )
    print(f"Generated {output_path}")


if __name__ == "__main__":
    main()
