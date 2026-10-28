"""Extrai os países de origem de cada artigo a partir da coluna 'Filiação'."""
import re
import sys
import unicodedata

import pandas as pd

import settings as cfg

CSV_PATH = "Mapeamento_-_Aceitos_-_Características.csv"
OUT_PATH = "output/paises_por_artigo.csv"


def normalize(text: str) -> str:
    """Minúsculas e sem acentos, para comparar nomes."""
    text = unicodedata.normalize("NFKD", str(text))
    return "".join(c for c in text if not unicodedata.combining(c)).lower()


def find_terms(text: str, terms):
    """Termos que aparecem como palavras inteiras no texto."""
    found = []
    for term in terms:
        pattern = r"(?<!\w)" + re.escape(normalize(term)) + r"(?!\w)"
        if re.search(pattern, normalize(text)):
            found.append(term)
    return found


def extract(article_id: int, affiliation: str):
    """Retorna (lista de ISO-3, fonte da decisão, evidências usadas)."""
    if article_id in cfg.MANUAL_OVERRIDES:
        ov = cfg.MANUAL_OVERRIDES[article_id]
        return ov["countries"], "manual", ov["reason"]

    countries, evidence = [], []
    for iso, aliases in cfg.COUNTRY_ALIASES.items():
        hits = find_terms(affiliation, aliases)
        if hits:
            countries.append(iso)
            evidence.append(hits[0])

    # Pistas por cidade/instituição complementam (não substituem) os países citados
    hint_isos = []
    for term, iso in cfg.CITY_HINTS.items():
        if find_terms(affiliation, [term]) and iso not in countries:
            if iso not in hint_isos:
                hint_isos.append(iso)
                evidence.append(f"{term} -> {iso} (inferido)")
    countries += hint_isos

    if not countries:
        return [], "não encontrado", ""
    source = "text" if not hint_isos else ("hint" if not any(
        find_terms(affiliation, cfg.COUNTRY_ALIASES[i]) for i in countries if i not in hint_isos
    ) else "text+hint")
    return countries, source, ", ".join(evidence)


def main() -> int:
    df = pd.read_csv(CSV_PATH)
    rows = []
    for _, r in df.iterrows():
        isos, source, evidence = extract(int(r["ID"]), r["Filiação"])
        rows.append({
            "ID": int(r["ID"]),
            "Ano": int(r["Ano"]),
            "Filiação": str(r["Filiação"]).replace("\n", " ").strip(),
            "Países": "; ".join(isos),
            "Fonte": cfg.SOURCE_LABELS.get(source, source),
            "Evidência": evidence,
        })
    out = pd.DataFrame(rows)
    out.to_csv(OUT_PATH, index=False, encoding="utf-8")

    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 60)
    print(out[["ID", "Ano", "Países", "Fonte", "Evidência"]].to_string(index=False))

    unresolved = out[out["Países"] == ""]
    if len(unresolved):
        print(f"\nAtenção: {len(unresolved)} artigo(s) sem país resolvido.")
        return 1

    # Contagem: cada país conta uma vez por artigo
    counts = {}
    for isos in out["Países"]:
        for iso in set(filter(None, isos.split("; "))):
            counts[iso] = counts.get(iso, 0) + 1
    print("\nContagem por país (uma vez por artigo):")
    for iso, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {iso}: {n}")
    print(f"\nTotal de artigos: {len(out)}  |  Países distintos: {len(counts)}")
    print(f"Arquivo salvo em {OUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
