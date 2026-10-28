"""Configurações do projeto: mapeamento de países e estilo das figuras."""

# ---------------------------------------------------------------------------
# 1. Extração de países a partir da coluna "Filiação"
# ---------------------------------------------------------------------------

# Nomes de países (PT/EN e variações observadas no CSV) -> código ISO-3
# A busca ignora acentos e maiúsculas/minúsculas.
COUNTRY_ALIASES = {
    "CAN": ["Canada", "Canadá"],
    "CHN": ["China"],
    "CYP": ["Chipre", "Cyprus"],
    "KAZ": ["Cazaquistão", "Kazakhstan"],
    "MYS": ["Malásia", "Malaysia", "Malasya"],
    "IND": ["Índia", "India"],
    "BRA": ["Brasil", "Brazil"],
    "USA": ["Estados Unidos", "EUA", "USA", "United States"],
    "GBR": ["Reino Unido", "United Kingdom"],
    "PAK": ["Pakistan", "Paquistão"],
    "ITA": ["Itália", "Italia", "Italy", "italianas"],
    "ESP": ["Espanha", "Spain"],
    "ARE": ["Emirados Árabes", "United Arab Emirates"],
}

# Pistas por cidade/instituição, usadas somente quando nenhum país é citado.
# Cada entrada: termo -> ISO-3
CITY_HINTS = {
    "Beijing": "CHN",
    "Xi'an": "CHN",
    "Xian": "CHN",
    "Dalian": "CHN",
    "Tianjin": "CHN",
    "Qingyang": "CHN",
    "China University of Petroleum": "CHN",
    "Shandong University": "CHN",
    "Kuala Lumpur": "MYS",
    "Porto Alegre": "BRA",
    "Rio de Janeiro": "BRA",
    "Niterói": "BRA",
    "Universidade Federal": "BRA",
    "PUC-Rio": "BRA",
    "Karachi": "PAK",
    "Islamabad": "PAK",
    "Glasgow": "GBR",
}

# Decisões manuais (com justificativa), sobrescrevem a extração automática.
# Chave: ID do artigo no CSV.
MANUAL_OVERRIDES = {
    37: {
        "countries": ["USA"],
        "reason": "País não informado no CSV; hipótese adotada pelo grupo "
                  "(EUA). Não confirmado na filiação do autor (M. Danis, SPE 195737).",
    },
}

# Código de origem de cada decisão, exibido no relatório de conferência
SOURCE_LABELS = {
    "text": "nome de país no texto",
    "text+hint": "país no texto + inferência por cidade/instituição",
    "hint": "inferido por cidade/instituição",
    "manual": "decisão manual",
}

# Contagem: cada país conta uma vez por artigo (conforme acordado).
COUNT_MODE = "once_per_paper"

# ---------------------------------------------------------------------------
# 2. Figura do mapa (estilo)
# ---------------------------------------------------------------------------

FIGURE = {
    "figsize": (11, 5.8),          # polegadas; proporção próxima à do mapa Robinson
    "dpi_reference": 300,          # usado apenas para PNG de pré-visualização
    "output_format": "pdf",        # vetorial
    "output_path": "output/mapa_papers.pdf",
    "projection": "Robinson",      # ou "PlateCarree"
    "title": "Concentração de papers por país de origem",
    "title_fontsize": 14,
    "title_fontweight": "bold",
    "font_family": "DejaVu Sans",
    "label_fontsize": 9,
    "legend_title": "Nº de papers",
    "background_color": "white",
    "ocean_color": "#eaf2f8",
    "no_data_color": "#e5e5e5",    # países sem artigos
    "edge_color": "#9e9e9e",
    "edge_width": 0.4,
    "colormap": "Blues",           # escala sequencial
    # Limites inferiores das classes da legenda; a última classe é aberta (ex.: 12+)
    "bins": [1, 2, 3, 5, 8, 12],

}

NATURAL_EARTH_SHP = "data/ne_110m_admin_0_countries.shp"
