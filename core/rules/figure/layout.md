# Figure Layout Rule

## Rule
Multi-panel figures must follow a three-level information hierarchy.

## Hierarchy Levels
1. **Overview panel**: Shows the big picture / main result
2. **Deviation panel**: Shows exceptions, comparisons, or breakdowns
3. **Relationship panel**: Shows correlations, mechanisms, or connections

## Layout Rules
- No two panels may answer the same scientific question
- Panel labels: lowercase bold letters in top-left corner (a, b, c...)
- Panel label size: 12pt, bold, using journal font
- Inter-panel spacing: 0.15 inches minimum
- Figure width: single column = 89mm, double column = 183mm (Nature); 55mm / 170mm (Science)

## GridSpec Template
```python
import matplotlib.gridspec as gridspec

fig = plt.figure(figsize=(7, 5))
gs = gridspec.GridSpec(2, 3, figure=fig, wspace=0.35, hspace=0.4)
ax1 = fig.add_subplot(gs[0, :2])   # overview (wide)
ax2 = fig.add_subplot(gs[0, 2])    # deviation
ax3 = fig.add_subplot(gs[1, :])    # relationship (full width)
```

## Anti-Redundancy
- If two panels show the same trend with different visualization, merge them
- If a panel has no unique scientific question, remove it
- Each panel caption must state what question it answers
