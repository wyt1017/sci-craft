"""Heatmap template for journal-quality figures."""
import matplotlib.pyplot as plt
import numpy as np


def create_heatmap(
    data: list[list[float]],
    row_labels: list[str],
    col_labels: list[str],
    title: str = "",
    colormap: str = "coolwarm",
    output_path: str = "heatmap",
    journal_dpi: int = 300,
    annotate: bool = True,
    fmt: str = ".2f",
):
    """Create a heatmap with optional cell annotations.

    Args:
        data: 2D array of values.
        row_labels: Row labels.
        col_labels: Column labels.
        title: Optional panel title.
        colormap: Matplotlib colormap name.
        output_path: File path without extension.
        journal_dpi: Raster DPI for PNG output.
        annotate: Whether to show values in cells.
        fmt: Number format for annotations.
    """
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Liberation Sans"]
    plt.rcParams["svg.font_type"] = "none"
    plt.rcParams["font.size"] = 8
    plt.rcParams["axes.linewidth"] = 0.5

    fig, ax = plt.subplots(figsize=(4, 3))
    im = ax.imshow(data, cmap=colormap, aspect="auto")

    ax.set_xticks(range(len(col_labels)))
    ax.set_yticks(range(len(row_labels)))
    ax.set_xticklabels(col_labels, rotation=45, ha="right")
    ax.set_yticklabels(row_labels)

    if annotate:
        for i in range(len(row_labels)):
            for j in range(len(col_labels)):
                ax.text(j, i, format(data[i][j], fmt), ha="center", va="center", fontsize=6, color="black" if abs(data[i][j]) < 0.5 else "white")

    if title:
        ax.set_title(title, fontsize=9, fontweight="bold", loc="left")

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=6)

    fig.savefig(f"{output_path}.svg", format="svg", bbox_inches="tight")
    fig.savefig(f"{output_path}.png", dpi=journal_dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {output_path}.svg, {output_path}.png")


if __name__ == "__main__":
    data = [[0.8, 0.3, -0.5], [0.3, 0.9, 0.1], [-0.5, 0.1, 0.7]]
    create_heatmap(data, ["Gene A", "Gene B", "Gene C"], ["Cond 1", "Cond 2", "Cond 3"], title="Correlation matrix")
