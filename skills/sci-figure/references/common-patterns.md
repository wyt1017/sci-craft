# Common Figure Patterns

## Ultra-wide panel (full width)
```python
gs = gridspec.GridSpec(2, 3, figure=fig)
ax_wide = fig.add_subplot(gs[0, :])  # spans all columns
```

## Legend as separate axis
```python
# Reserve a thin column for the legend
gs = gridspec.GridSpec(1, 2, width_ratios=[5, 1], figure=fig)
ax_main = fig.add_subplot(gs[0, 0])
ax_legend = fig.add_subplot(gs[0, 1])
ax_legend.axis('off')
handles, labels = ax_main.get_legend_handles_labels()
ax_legend.legend(handles, labels, loc='center', frameon=False)
```

## Print-safe bars (hatching for grayscale)
```python
hatches = ['///', '...', '\\\\\\', 'xxx', '+++']
for i, bar in enumerate(ax.containers[0]):
    bar.set_hatch(hatches[i % len(hatches)])
```

## Inward ticks (Nature/Science standard)
```python
plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'
```
