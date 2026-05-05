"""
Resolver for fedlex.admin.ch ELI URLs.

Strategy: ELI path → Fedlex metadata → current XML fileUrl → extractor
"""
import re

import requests

from extractors import akoma_ntoso

PATTERN = re.compile(r"fedlex\.admin\.ch/eli/(.+)")

_ELASTIC = "https://www.fedlex.admin.ch/elasticsearch/proxy/_search?index=data"


def _walk_strings(value):
    if isinstance(value, dict):
        for child in value.values():
            yield from _walk_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_strings(child)
    elif isinstance(value, str):
        yield value


def _metadata_xml_url(eli_path: str, lang: str) -> str:
    eli_uri = f"https://fedlex.data.admin.ch/eli/{eli_path}"
    query = {
        "size": 1,
        "query": {"term": {"data.uri.keyword": eli_uri}},
    }
    resp = requests.post(_ELASTIC, json=query, timeout=30)
    resp.raise_for_status()
    hits = resp.json()["hits"]["hits"]
    if not hits:
        raise ValueError(f"No Fedlex metadata found for ELI {eli_path}")

    prefix = f"/eli/{eli_path}/"
    marker = f"/{lang}/xml/"
    urls = [
        value
        for value in _walk_strings(hits[0]["_source"])
        if (
            value.startswith("https://fedlex.data.admin.ch/filestore/")
            and prefix in value
            and marker in value
            and value.endswith(".xml")
        )
    ]
    if not urls:
        raise ValueError(f"No XML file URL found for ELI {eli_path}/{lang}")

    def key(url: str) -> str:
        match = re.search(r"/(\d{8})/[a-z]{2}/xml/", url)
        return match.group(1) if match else ""

    return sorted(set(urls), key=key)[-1]


def resolve(url: str) -> str:
    m = PATTERN.search(url)
    path = m.group(1).rstrip("/")

    lang_m = re.search(r"^(.+)/([a-z]{2})$", path)
    if lang_m:
        eli_path, lang = lang_m.group(1), lang_m.group(2)
    else:
        eli_path, lang = path, "de"

    xml_url = _metadata_xml_url(eli_path, lang)
    resp = requests.get(xml_url, timeout=30)
    resp.raise_for_status()
    return akoma_ntoso.extract(resp.content, source_url=url)
