# Framework Diagram Rule

## Rule
Framework diagrams must be generated using Graphviz dot + matplotlib, producing editable SVG output.

## Supported Types
1. **Model Architecture**: Neural network / model structure
2. **System Pipeline**: End-to-end processing flow
3. **Experimental Setup**: Data collection and analysis flow
4. **Data Flow**: Information flow between modules

## Generation Rules

### Component Rules
- Every component must have a clear label and at least one input/output
- Use rounded rectangles for processing modules
- Use cylinders for data stores
- Use parallelograms for I/O
- Use diamonds for decision points

### Connection Rules
- Arrows must use `->` (forward direction)
- No bidirectional arrows — use two separate arrows
- Arrow labels must describe the data/signal flowing
- No crossing arrows — restructure layout if needed

### Style Rules
- Font: Arial/Helvetica, minimum 8pt
- Stroke width: 1pt for borders, 1.5pt for arrows
- Colors from journal palette (primary for modules, secondary for data)
- Background: white, no gradients
- SVG text must remain as `<text>` nodes

### Output
- Primary: SVG (editable in Inkscape/Illustrator)
- Secondary: dot source file (for regeneration)
- The dot source file must be saved alongside the SVG
