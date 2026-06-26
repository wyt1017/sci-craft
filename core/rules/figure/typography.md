# Figure Typography Rule

## Rule
All figures must use journal-configured typography settings.

## Mandatory rcParams (Python/matplotlib)

```python
plt.rcParams['font.family'] = '{{font_family}}'
plt.rcParams['font.sans-serif'] = {{font_sans_list}}
plt.rcParams['svg.font_type'] = 'none'  # text stays as <text>, not paths
plt.rcParams['font.size'] = 8
plt.rcParams['axes.linewidth'] = 0.5
plt.rcParams['xtick.major.width'] = 0.5
plt.rcParams['ytick.major.width'] = 0.5
plt.rcParams['xtick.major.size'] = 3
plt.rcParams['ytick.major.size'] = 3
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'
plt.rcParams['axes.labelsize'] = 8
plt.rcParams['xtick.labelsize'] = 7
plt.rcParams['ytick.labelsize'] = 7
plt.rcParams['legend.fontsize'] = 7
```

## Font Rules
- Minimum font size: 6pt (axis labels); 5pt (tick labels)
- All text must be editable in SVG (never convert to paths)
- Use only the journal-configured font family
- Bold only for panel labels (a, b, c...), not for axis labels

## Output Rules
- Primary: SVG (vector, editable, text as <text> nodes)
- Secondary: PNG at journal-required DPI
- Never save as JPG for scientific figures
