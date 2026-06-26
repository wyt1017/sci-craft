"""Line chart template for journal-quality figures."""
import matplotlib.pyplot as plt
import numpy as np


def create_line_chart(
    x_data: list[float],
    y_series: dict[str, list[float]],
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    palette: list[str] | None = None,
    output_path: str = "line_chart",
    journal_dpi: int = 300,
    markers: list[str] | None = None,
    show_error: bool = False,
    error_bands: dict[str, tuple[list[float], list[float]]] | None = None,
):
    """Create a line chart with optional error bands.

    Args:
        x_data: X-axis values.
        y_series: Series name -> Y-axis values.
        xlabel: X-axis label.
        ylabel: Y-axis label.
        title: Optional panel title.
        palette: List of hex color strings.
        output_path: File path without extension.
        journal_dpi: Raster DPI for PNG output.
        markers: Marker styles per series.
        show_error: Whether to show error bands.
        error_bands: Series name -> (lower, upper) for shaded error.
    """
    if palette is None:
        palette = ["#0C5DA5", "#00B945", "#FF2C00", "#FF9500", "#845B97"]
    if markers is None:
        markers = ["o", "s", "^", "D", "v"]

    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Arial", "DejaVu Sans", "Liberation Sans"]
    plt.rcParams["svg.font_type"] = "none"
    plt.rcParams["font.size"] = 8
    plt.rcParams["axes.linewidth"] = 0.5

    fig, ax = plt.subplots(figsize=(3.5, 2.5))
    for i, (name, y_vals) in enumerate(y_series.items()):
        ax.plot(x_data, y_vals, marker=markers[i % len(markers)], markersize=4, linewidth=1.2, label=name, color=palette[i % len(palette)])
        if show_error and error_bands and name in error_bands:
            lower, upper = error_bands[name]
            ax.fill_between(x_data, lower, upper, alpha=0.15, color=palette[i % len(palette)])

    ax.set_xlabel(xlabel)
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
    x = [1, 2, 3, 4, 5]
    create_line_chart(
        x_data=x,
        y_series={"Model A": [0.6, 0.72, 0.81, 0.88, 0.92], "Model B": [0.55, 0.65, 0.74, 0.79, 0.83]},
        xlabel="Epoch", ylabel="Accuracy",
    )
