"""Framework diagram template using Graphviz dot."""
import subprocess
import tempfile
from pathlib import Path


def create_framework_diagram(
    dot_source: str,
    output_path: str = "framework_diagram",
    engine: str = "dot",
):
    """Generate a framework diagram from Graphviz dot source.

    Args:
        dot_source: Valid Graphviz dot language string.
        output_path: File path without extension.
        engine: Graphviz layout engine (dot, neato, fdp, etc.).
    """
    dot_path = Path(f"{output_path}.dot")
    svg_path = Path(f"{output_path}.svg")
    png_path = Path(f"{output_path}.png")

    # Save dot source for editability
    dot_path.write_text(dot_source, encoding="utf-8")

    # Generate SVG
    result = subprocess.run(
        [engine, "-Tsvg", "-o", str(svg_path), str(dot_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Graphviz error: {result.stderr}")

    # Generate PNG at 300dpi
    subprocess.run(
        [engine, "-Tpng", "-Gdpi=300", "-o", str(png_path), str(dot_path)],
        capture_output=True, text=True,
    )

    print(f"Saved: {svg_path}, {png_path}, {dot_path}")


# --- Dot source builders for common patterns ---

def model_architecture_dot(
    layers: list[dict[str, str]],
    palette: dict[str, str] | None = None,
) -> str:
    """Build dot source for a model architecture diagram.

    Args:
        layers: List of {"name": str, "type": str, "label": str}.
            type: "process" | "data" | "decision"
        palette: Optional color overrides.
    """
    if palette is None:
        palette = {"process": "#0C5DA5", "data": "#00B945", "decision": "#FF9500"}

    shape_map = {"process": "box,style=rounded", "data": "cylinder", "decision": "diamond"}
    lines = [
        'digraph ModelArchitecture {',
        '  rankdir=TB;',
        '  fontname="Arial";',
        '  node [fontname="Arial", fontsize=10, style=filled, penwidth=1];',
        '  edge [fontname="Arial", fontsize=8, penwidth=1.2, arrowsize=0.8];',
        '',
    ]

    for i, layer in enumerate(layers):
        shape = shape_map.get(layer["type"], "box,style=rounded")
        color = palette.get(layer["type"], "#0C5DA5")
        lines.append(f'  node{i} [label="{layer["label"]}", shape={shape}, fillcolor="{color}", fontcolor="white"];')

    lines.append('')
    for i in range(len(layers) - 1):
        lines.append(f'  node{i} -> node{i+1};')

    lines.append('}')
    return '\n'.join(lines)


def pipeline_dot(
    stages: list[dict[str, str]],
    connections: list[tuple[int, int, str]] | None = None,
    palette: dict[str, str] | None = None,
) -> str:
    """Build dot source for a system pipeline diagram.

    Args:
        stages: List of {"name": str, "type": str, "label": str}.
        connections: List of (from_idx, to_idx, label) tuples.
            Default is sequential.
        palette: Optional color overrides.
    """
    if palette is None:
        palette = {"process": "#0C5DA5", "data": "#00B945", "io": "#845B97"}
    if connections is None:
        connections = [(i, i + 1, "") for i in range(len(stages) - 1)]

    shape_map = {"process": "box,style=rounded", "data": "cylinder", "io": "parallelogram"}
    lines = [
        'digraph SystemPipeline {',
        '  rankdir=LR;',
        '  fontname="Arial";',
        '  node [fontname="Arial", fontsize=10, style=filled, penwidth=1];',
        '  edge [fontname="Arial", fontsize=8, penwidth=1.2, arrowsize=0.8];',
        '',
    ]

    for i, stage in enumerate(stages):
        shape = shape_map.get(stage["type"], "box,style=rounded")
        color = palette.get(stage["type"], "#0C5DA5")
        lines.append(f'  stage{i} [label="{stage["label"]}", shape={shape}, fillcolor="{color}", fontcolor="white"];')

    lines.append('')
    for src, dst, label in connections:
        lbl = f' [label="{label}"]' if label else ""
        lines.append(f'  stage{src} -> stage{dst}{lbl};')

    lines.append('}')
    return '\n'.join(lines)


if __name__ == "__main__":
    # Example: model architecture
    layers = [
        {"name": "input", "type": "data", "label": "Input\nImages"},
        {"name": "conv1", "type": "process", "label": "Conv Block 1"},
        {"name": "conv2", "type": "process", "label": "Conv Block 2"},
        {"name": "pool", "type": "process", "label": "Global\nPooling"},
        {"name": "fc", "type": "process", "label": "FC Layer"},
        {"name": "output", "type": "data", "label": "Predictions"},
    ]
    dot = model_architecture_dot(layers)
    create_framework_diagram(dot, "example_model_architecture")
