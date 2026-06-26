# sci-framework

Generate editable SVG framework diagrams from natural language descriptions, following Nature or Science journal standards.

## Key Differentiator

This is the skill that nature-skills explicitly said it **cannot** do. Framework diagrams are essential for CS/engineering papers, and sci-framework fills this gap using Graphviz.

## Features
- Natural language → structured diagram
- Graphviz dot source generation
- Editable SVG output + dot source for regeneration
- Journal-specific color palettes
- Multiple diagram types: model architecture, system pipeline, experimental setup, data flow

## Usage

> "Draw a model architecture: Input images → Conv Block 1 → Conv Block 2 → Global Pooling → FC Layer → Predictions"

> "Create a system pipeline diagram for a recommendation system for Science journal"

## Triggers
- "framework diagram", "architecture diagram", "model architecture"
- "system pipeline", "experimental setup diagram", "data flow diagram"
