#!/usr/bin/env python3
"""Generate the portfolio's editable HTML sections from avatars.json."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit
from typing import Any

ROOT = Path(__file__).resolve().parent


def text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def safe_url(value: Any, field: str, *, allow_empty: bool = False) -> str:
    if allow_empty and value == "":
        return ""
    url = text(value, field)
    parsed = urlsplit(url)
    if not parsed.scheme:
        if url.startswith(("//", "\\")) or "\\" in url or any(
            ord(character) < 32 for character in url
        ):
            raise ValueError(f"{field} must be a safe relative path or absolute URL")
        return url
    if parsed.scheme not in {"https", "http", "mailto"}:
        raise ValueError(f"{field} must be an https://, http://, or mailto: URL")
    if parsed.scheme in {"https", "http"} and not parsed.netloc:
        raise ValueError(f"{field} must include a hostname")
    return url


def items(data: Any, field: str) -> list[dict[str, Any]]:
    if not isinstance(data, list) or not data:
        raise ValueError(f"{field} must be a non-empty list")
    if not all(isinstance(item, dict) for item in data):
        raise ValueError(f"each entry in {field} must be an object")
    return data


def escape(value: str) -> str:
    return html.escape(value, quote=True)


def region(document: str, name: str, content: str) -> str:
    start = f"<!-- GENERATOR:{name}:START -->"
    end = f"<!-- GENERATOR:{name}:END -->"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    replacement = f"{start}{content}{end}"
    updated, count = pattern.subn(lambda _: replacement, document)
    if count != 1:
        raise ValueError(f"expected exactly one HTML region named {name!r}; found {count}")
    return updated


def avatar_cards(avatars: list[dict[str, Any]]) -> str:
    cards: list[str] = []
    for index, avatar in enumerate(avatars, start=1):
        title = escape(text(avatar.get("title"), f"avatars[{index}].title"))
        image = safe_url(
            avatar.get("image", ""),
            f"avatars[{index}].image",
            allow_empty=True,
        )
        demo = safe_url(
            avatar.get("demo_url", ""),
            f"avatars[{index}].demo_url",
            allow_empty=True,
        )
        features = avatar.get("features")
        if not isinstance(features, list) or not all(
            isinstance(feature, str) and feature.strip() for feature in features
        ):
            raise ValueError(f"avatars[{index}].features must be a list of non-empty strings")

        if image:
            visual = (
                f'<img src="{escape(image)}" alt="Preview of {title}" '
                'class="h-64 w-full object-cover" loading="lazy">'
            )
        else:
            visual = (
                f'<div class="avatar-placeholder flex h-64 items-end justify-center overflow-hidden" '
                f'role="img" aria-label="Preview placeholder for {title}"></div>'
            )
        feature_tags = "".join(
            f'<li class="feature-pill rounded-full px-2.5 py-1 text-xs text-slate-300">{escape(feature.strip())}</li>'
            for feature in features
        )
        target = demo or "#contact"
        link_target = ' target="_blank" rel="noopener noreferrer"' if demo else ""
        cards.append(
            '<article class="overflow-hidden rounded-2xl border border-white/10 bg-panel">'
            f"{visual}<div class=\"p-5\"><h3 class=\"text-lg font-bold text-white\">{title}</h3>"
            f'<ul class="mt-3 flex flex-wrap gap-2" aria-label="Features">{feature_tags}</ul>'
            f'<a href="{escape(target)}"{link_target} '
            'class="mt-5 inline-flex text-sm font-semibold text-violet-300 transition hover:text-cyanbeam">'
            f'{"View details / demo video" if demo else "Ask about this avatar"} '
            '<span class="ml-2" aria-hidden="true">↗</span></a></div></article>'
        )
    return "\n".join(cards)


def tier_cards(tiers: list[dict[str, Any]]) -> str:
    cards: list[str] = []
    for index, tier in enumerate(tiers, start=1):
        label = escape(text(tier.get("label", f"Tier {index}"), f"tiers[{index}].label"))
        name = escape(text(tier.get("name"), f"tiers[{index}].name"))
        price = escape(text(tier.get("price"), f"tiers[{index}].price"))
        description = escape(text(tier.get("description"), f"tiers[{index}].description"))
        features = tier.get("features")
        if not isinstance(features, list) or not all(
            isinstance(feature, str) and feature.strip() for feature in features
        ):
            raise ValueError(f"tiers[{index}].features must be a list of non-empty strings")
        border = "border-violet-300/35 shadow-neon" if index == 1 else "border-white/10"
        feature_list = "".join(
            f'<li>✓ {escape(feature.strip())}</li>' for feature in features
        )
        cards.append(
            f'<article class="flex flex-col rounded-2xl border {border} bg-panel p-6">'
            f'<p class="text-xs font-bold uppercase tracking-[.2em] text-violet-300">{label}</p>'
            f'<h3 class="mt-3 text-xl font-bold text-white">{name}</h3>'
            f'<p class="mt-2 text-sm leading-6 text-slate-400">{description}</p>'
            f'<p class="mt-6 text-3xl font-black text-white">{price}</p>'
            f'<ul class="mt-5 space-y-2 text-sm text-slate-300">{feature_list}</ul>'
            '<a href="#contact" class="mt-7 rounded-xl border border-white/10 px-4 py-3 text-center '
            'text-sm font-bold text-violet-200 transition hover:bg-violet-400/10">Ask about this tier</a>'
            '</article>'
        )
    return "\n".join(cards)


def addon_items(addons: list[dict[str, Any]]) -> str:
    rendered: list[str] = []
    for index, addon in enumerate(addons, start=1):
        name = escape(text(addon.get("name"), f"addons[{index}].name"))
        price = escape(text(addon.get("price"), f"addons[{index}].price"))
        rendered.append(
            '<li class="flex justify-between gap-4 rounded-xl border border-white/[.07] '
            f'bg-night/50 px-4 py-3 text-sm"><span class="text-slate-300">{name}</span>'
            f'<span class="shrink-0 font-semibold text-cyanbeam">{price}</span></li>'
        )
    return "\n".join(rendered)


def social_links(socials: list[dict[str, Any]]) -> str:
    rendered: list[str] = []
    for index, social in enumerate(socials, start=1):
        label = escape(text(social.get("label"), f"socials[{index}].label"))
        url = safe_url(
            social.get("url", ""),
            f"socials[{index}].url",
            allow_empty=True,
        )
        if not url:
            continue
        rendered.append(
            f'<a href="{escape(url)}" target="_blank" rel="noopener noreferrer" '
            'class="rounded-xl border border-white/10 bg-night/50 p-4 text-sm font-semibold '
            f'text-slate-300 transition hover:border-violet-300/40 hover:text-white">{label} '
            '<span class="float-right text-violetglow" aria-hidden="true">↗</span></a>'
        )
    return "\n".join(rendered) or (
        '<p class="text-sm text-slate-500">Add your profile links in avatars.json.</p>'
    )


def generate(site_dir: Path) -> Path:
    data_path = site_dir / "avatars.json"
    html_path = site_dir / "index.html"
    try:
        data = json.loads(data_path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"data file not found: {data_path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid JSON in {data_path}: {error}") from error
    if not isinstance(data, dict):
        raise ValueError("avatars.json must contain a JSON object")

    profile = data.get("profile")
    if not isinstance(profile, dict):
        raise ValueError("profile must be an object")
    name = text(profile.get("name"), "profile.name")
    tagline = text(profile.get("tagline"), "profile.tagline")
    discord_tag = text(profile.get("discord_tag"), "profile.discord_tag")
    status = text(profile.get("commission_status"), "profile.commission_status").lower()
    if status not in {"open", "closed"}:
        raise ValueError("profile.commission_status must be 'open' or 'closed'")
    contact = data.get("contact")
    if not isinstance(contact, dict):
        raise ValueError("contact must be an object")
    email = text(contact.get("email"), "contact.email")
    if "@" not in email or any(character in email for character in "<>\"'"):
        raise ValueError("contact.email must be a valid email address")
    avatars = items(data.get("avatars"), "avatars")
    tiers = items(data.get("tiers"), "tiers")
    addons = items(data.get("addons"), "addons")
    socials_data = data.get("socials", [])
    if not isinstance(socials_data, list) or not all(
        isinstance(item, dict) for item in socials_data
    ):
        raise ValueError("socials must be a list of objects")

    document = html_path.read_text(encoding="utf-8")
    generated_regions = {
        "title": f"<title>VRChat Avatar Commissions | {escape(name)}</title>",
        "nav_name": escape(name),
        "footer_name": escape(name),
        "tagline": escape(tagline),
        "discord_tag": (
            '<span class="font-semibold text-white" data-discord-tag="'
            f'{escape(discord_tag)}">{escape(discord_tag)}</span>'
        ),
        "email_contact": (
            '<a id="email-contact" href="mailto:'
            f'{escape(email)}" class="mt-6 inline-flex rounded-xl bg-cyan-300 px-5 py-3 '
            'text-sm font-bold text-night transition hover:bg-cyan-200">Start an email ↗</a>'
        ),
        "avatars": avatar_cards(avatars),
        "tiers": tier_cards(tiers),
        "addons": addon_items(addons),
        "socials": social_links(socials_data),
        "status_badge": (
            '<div class="mb-7 inline-flex items-center gap-2 rounded-full border '
            + (
                "border-emerald-400/30 bg-emerald-400/10 text-emerald-300"
                if status == "open"
                else "border-rose-400/30 bg-rose-400/10 text-rose-300"
            )
            + ' px-3 py-1.5 text-xs font-semibold tracking-wide"><span class="h-2 w-2 rounded-full '
            + (
                "bg-emerald-400 shadow-[0_0_12px_rgba(52,211,153,.8)]"
                if status == "open"
                else "bg-rose-400 shadow-[0_0_12px_rgba(251,113,133,.8)]"
            )
            + '"></span>Commissions '
            + ("Open" if status == "open" else "Closed")
            + "</div>"
        ),
    }
    for name, content in generated_regions.items():
        document = region(document, name, content)
    html_path.write_text(document, encoding="utf-8")
    return html_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Update index.html using avatar, pricing, and social data in avatars.json."
    )
    parser.add_argument(
        "--directory",
        type=Path,
        default=ROOT,
        help="project directory containing index.html and avatars.json",
    )
    args = parser.parse_args()
    try:
        output = generate(args.directory.resolve())
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    print(f"Updated {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
