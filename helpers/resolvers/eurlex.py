"""
Resolver for eur-lex.europa.eu legal URLs.

Strategy: ELI/CELEX → CELEX ID → CELLAR XHTML → eurlex_html extractor
"""
import re
from urllib.parse import parse_qs, urlparse

import requests

from extractors import eurlex_html

PATTERN = re.compile(
    r"eur-lex\.europa\.eu/(?:eli/|legal-content/)"
)

_TYPE_LETTER = {"reg": "R", "dir": "L", "dec": "D"}
_CELLAR_SPARQL = "https://publications.europa.eu/webapi/rdf/sparql"
_LANG_CODES = {
    "bg": "BG",
    "spa": "ES",
    "cs": "CS",
    "dan": "DA",
    "deu": "DE",
    "de": "DE",
    "est": "ET",
    "el": "EL",
    "eng": "EN",
    "en": "EN",
    "fra": "FR",
    "fr": "FR",
    "gle": "GA",
    "hrv": "HR",
    "ita": "IT",
    "it": "IT",
    "lav": "LV",
    "lit": "LT",
    "hun": "HU",
    "mlt": "MT",
    "nld": "NL",
    "pol": "PL",
    "por": "PT",
    "ron": "RO",
    "slk": "SK",
    "slv": "SL",
    "fin": "FI",
    "swe": "SV",
}
_CELLAR_LANG = {
    "BG": "BUL",
    "ES": "SPA",
    "CS": "CES",
    "DA": "DAN",
    "DE": "DEU",
    "ET": "EST",
    "EL": "ELL",
    "EN": "ENG",
    "FR": "FRA",
    "GA": "GLE",
    "HR": "HRV",
    "IT": "ITA",
    "LV": "LAV",
    "LT": "LIT",
    "HU": "HUN",
    "MT": "MLT",
    "NL": "NLD",
    "PL": "POL",
    "PT": "POR",
    "RO": "RON",
    "SK": "SLK",
    "SL": "SLV",
    "FI": "FIN",
    "SV": "SWE",
}


def _eli_to_celex(eli_path: str) -> str:
    # eli_path: reg/2016/679[/oj/lang/...]
    parts = eli_path.strip("/").split("/")
    if len(parts) < 3:
        raise ValueError(f"Cannot parse ELI path: {eli_path}")
    doc_type, year, number = parts[0], parts[1], parts[2]
    letter = _TYPE_LETTER.get(doc_type, "X")
    return f"3{year}{letter}{int(number):04d}"


def _legal_content_to_celex(url: str) -> str:
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    uri = (params.get("uri") or [""])[0]
    m = re.search(r"CELEX:([0-9A-Z]+)", uri, re.I)
    if not m:
        raise ValueError(f"Cannot parse CELEX URI: {url}")
    return m.group(1).upper()


def _eli_lang(eli_path: str) -> str:
    parts = eli_path.strip("/").split("/")
    if len(parts) >= 5 and parts[3] == "oj":
        return _LANG_CODES.get(parts[4], "EN")
    return "DE"


def _legal_content_lang(url: str) -> str:
    parts = urlparse(url).path.strip("/").split("/")
    if len(parts) >= 2 and parts[0] == "legal-content":
        return _LANG_CODES.get(parts[1].lower(), parts[1].upper())
    return "DE"


def _sparql(query: str) -> list[dict]:
    resp = requests.get(
        _CELLAR_SPARQL,
        params={"query": query},
        headers={
            "Accept": "application/sparql-results+json",
            "User-Agent": "Mozilla/5.0",
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["results"]["bindings"]


def _cellar_work_uri(celex: str) -> str:
    query = f"""
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
SELECT ?work WHERE {{
  ?work cdm:resource_legal_id_celex ?celex .
  FILTER(str(?celex) = "{celex}")
}}
LIMIT 1
"""
    bindings = _sparql(query)
    if not bindings:
        raise ValueError(f"No CELLAR work found for {celex}")
    return bindings[0]["work"]["value"]


def _cellar_item_url(celex: str, lang: str) -> str:
    work = _cellar_work_uri(celex)
    cellar_lang = _CELLAR_LANG[lang]
    query = f"""
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
SELECT ?item WHERE {{
  ?expr cdm:expression_belongs_to_work <{work}> ;
        cdm:expression_uses_language
        <http://publications.europa.eu/resource/authority/language/{cellar_lang}> .
  ?manif cdm:manifestation_manifests_expression ?expr ;
         cdm:manifestation_type ?format .
  ?item cdm:item_belongs_to_manifestation ?manif .
  FILTER(str(?format) = "xhtml")
}}
LIMIT 1
"""
    bindings = _sparql(query)
    if not bindings:
        raise ValueError(f"No CELLAR XHTML item found for {celex}/{lang}")
    return bindings[0]["item"]["value"]


def resolve(url: str) -> str:
    parsed = urlparse(url)
    if parsed.path.startswith("/eli/"):
        eli_path = parsed.path.removeprefix("/eli/")
        celex = _eli_to_celex(eli_path)
        lang = _eli_lang(eli_path)
    else:
        celex = _legal_content_to_celex(url)
        lang = _legal_content_lang(url)
    item_url = _cellar_item_url(celex, lang)
    resp = requests.get(
        item_url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=60,
    )
    resp.raise_for_status()
    return eurlex_html.extract(resp.text, source_url=url)
