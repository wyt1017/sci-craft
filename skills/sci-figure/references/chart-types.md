# Supported Chart Types

| Type | Use for | Key parameters |
|------|---------|----------------|
| Grouped bar | Comparing categories across groups | `group_spacing=0.2` |
| Stacked bar | Part-to-whole within categories | `stack_spacing=0` |
| Horizontal bar | Comparing long category names | Swap x/y |
| Line/trend | Temporal or sequential data | `markers`, `error_bands` |
| Heatmap | Matrix data, correlations | `colormap='coolwarm'` |
| Scatter/bubble | Two-variable relationships | `s=size`, `c=color` |
| Radar/polar | Multi-dimensional comparison | `theta`, `r` |
| Fill-between | Range or uncertainty | `alpha=0.15` |
| Forest/interval | Effect sizes with confidence | `horizontal lines` |
| Area/stacked | Cumulative composition | `stacked=True` |

## Chart Selection Guide

- Comparing quantities → bar
- Showing change over time → line
- Showing relationship → scatter
- Showing distribution → histogram/violin/box
- Showing composition → stacked bar / pie (rarely)
- Showing correlation matrix → heatmap
