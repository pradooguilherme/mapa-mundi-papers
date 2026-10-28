"""Gera o mapa-múndi de concentração de papers por país, em PDF vetorial."""
import sys

import geopandas as gpd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

import settings as cfg

CSV_PATH = "output/paises_por_artigo.csv"

# Projeção Robinson (ESRI:54030) para um mapa-múndi equilibrado
PROJECTIONS = {
    "Robinson": "ESRI:54030",
    "PlateCarree": "EPSG:4326",
}


def load_counts(csv_path: str) -> dict:
    """Conta, para cada país, em quantos artigos ele aparece (uma vez por artigo)."""
    df = pd.read_csv(csv_path)
    counts = {}
    for entry in df["Países"].fillna(""):
        for iso in set(filter(None, (p.strip() for p in entry.split(";")))):
            counts[iso] = counts.get(iso, 0) + 1
    return counts


def make_classes(bins):
    """Faixas da legenda a partir dos limites inferiores em cfg.FIGURE['bins']."""
    labels = []
    for i, lo in enumerate(bins):
        if i == len(bins) - 1:
            labels.append(f"{lo}+")
        elif bins[i + 1] - lo == 1:
            labels.append(f"{lo}")
        else:
            labels.append(f"{lo}–{bins[i + 1] - 1}")
    return labels


def classify(value: int, bins) -> int:
    """Índice da classe (0..len(bins)-1) para um valor >= 1."""
    return int(np.searchsorted(bins, value, side="right") - 1)


def main() -> int:
    fig_cfg = cfg.FIGURE
    counts = load_counts(CSV_PATH)
    if not counts:
        print("Nenhum país encontrado em", CSV_PATH)
        return 1

    world = gpd.read_file(cfg.NATURAL_EARTH_SHP)
    iso_col = "ADM0_A3"
    missing = set(counts) - set(world[iso_col])
    if missing:
        print("Aviso: códigos sem geometria no shapefile:", sorted(missing))

    world["papers"] = world[iso_col].map(counts).fillna(0).astype(int)

    # Cores: classes discretas a partir da colormap configurada
    bins = fig_cfg["bins"]
    cmap = mpl.colormaps[fig_cfg["colormap"]]
    class_colors = [cmap(x) for x in np.linspace(0.35, 0.95, len(bins))]
    labels = make_classes(bins)

    def color_for(n):
        if n == 0:
            return fig_cfg["no_data_color"]
        return class_colors[classify(n, bins)]

    world["color"] = world["papers"].apply(color_for)

    crs = PROJECTIONS.get(fig_cfg["projection"], "ESRI:54030")
    world = world.to_crs(crs)

    mpl.rcParams["pdf.fonttype"] = 42        # texto editável no PDF
    mpl.rcParams["svg.fonttype"] = "none"
    mpl.rcParams["font.family"] = fig_cfg["font_family"]

    fig, ax = plt.subplots(figsize=fig_cfg["figsize"], facecolor=fig_cfg["background_color"])
    ax.set_facecolor(fig_cfg["ocean_color"])
    world.plot(ax=ax, color=world["color"], edgecolor=fig_cfg["edge_color"],
               linewidth=fig_cfg["edge_width"])

    # Rótulo com a contagem em cada país com papers
    for _, row in world[world["papers"] > 0].iterrows():
        pt = row.geometry.representative_point()
        ax.annotate(str(row["papers"]), xy=(pt.x, pt.y), ha="center", va="center",
                    fontsize=fig_cfg["label_fontsize"], color="black", weight="bold")

    ax.set_axis_off()
    # Título no topo da figura; o mapa ocupa o espaço restante
    fig.text(0.5, 0.955, fig_cfg["title"], ha="center", va="top",
             fontsize=fig_cfg["title_fontsize"], fontweight=fig_cfg["title_fontweight"])
    fig.subplots_adjust(left=0, right=1, top=0.90, bottom=0)

    handles = [Patch(facecolor=fig_cfg["no_data_color"], edgecolor=fig_cfg["edge_color"],
                     label="0")]
    handles += [Patch(facecolor=c, edgecolor=fig_cfg["edge_color"], label=lab)
                for c, lab in zip(class_colors, labels)]
    ax.legend(handles=handles, title=fig_cfg["legend_title"], loc="lower left",
              frameon=False, fontsize=fig_cfg["label_fontsize"])

    fig.savefig(fig_cfg["output_path"], format=fig_cfg["output_format"],
                bbox_inches="tight", pad_inches=0.02, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Figura salva em {fig_cfg['output_path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
