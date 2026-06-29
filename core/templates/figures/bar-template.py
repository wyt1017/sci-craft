"""Bar chart template for journal-quality figures."""
import matplotlib.pyplot as plt
import numpy as np

# Default palettes per journal
DEFAULT_PALETTES = {
    "nature": ["#0C5DA5", "#00B945", "#FF2C00", "#FF9500", "#845B97", "#474747"],
    "science": ["#0072B2", "#D59E00", "#009E73", "#CC7722", "#984EA3", "#A0A0A0"],
}

DEFAULT_FONTS = {
    "nature": ["Arial", "DejaVu Sans", "Liberation Sans"],
    "science": ["Helvetica", "Arial"],
}


def create_bar_chart(
    data: dict[str, list[float]],
    labels: list[str],
    ylabel: str = "",
    title: str = "",
    palette: list[str] | None = None,
    fonts: list[str] | None = None,
    output_path: str = "bar_chart",
    journal_dpi: int = 300,
    group_spacing: float = 0.2,
    figsize: tuple[float, float] | None = None,
):
    """Create a grouped bar chart.

    Args:
        data: Series name -> list of values, one per label group.
        labels: X-axis group labels.
        ylabel: Y-axis label.
        title: Optional panel title.
        palette: List of hex color strings. Falls back to Nature palette if not provided.
        fonts: List of font names for sans-serif family.
        output_path: File path without extension.
        journal_dpi: Raster DPI for PNG output.
        group_spacing: Spacing between label groups.
        figsize: Figure size as (width, height) tuple.
    """
    if palette is None:
        palette = DEFAULT_PALETTES["nature"]
    if fonts is None:
        fonts = DEFAULT_FONTS["nature"]
    if figsize is None:
        figsize = (3.5, 2.5)

    # Mandatory rcParams
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = fonts
    plt.rcParams["svg.font_type"] = "none"
    plt.rcParams["font.size"] = 8
    plt.rcParams["axes.linewidth"] = 0.5

    n_series = len(data)
    n_groups = len(labels)
    x = np.arange(n_groups)
    width = (1 - group_spacing) / n_series

    fig, ax = plt.subplots(figsize=figsize)
    for i, (series_name, values) in enumerate(data.items()):
        offset = (i - n_series / 2 + 0.5) * width
        ax.bar(
            x + offset, values, width, label=series_name,
            color=palette[i % len(palette)],
            linewidth=0.5, edgecolor="white",
        )

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel(ylabel)
    if title:
        ax.set_title(title, fontsize=9, fontweight="bold", loc="left")
    ax.legend(frameon=False, fontsize=7)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.savefig(f"{output_path}.svg", format="svg", bbox_inches="tight")
    fig.savefig(f"{output_path}.png", dpi=journal_dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {output_path}.svg, {output_path}.png")


if __name__ == "__main__":
    create_bar_chart(
        data={"Method A": [85, 72, 90], "Method B": [78, 81, 85]},
        labels=["Dataset 1", "Dataset 2", "Dataset 3"],
        ylabel="Accuracy (%)",
    )
