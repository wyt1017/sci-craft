# Framework Diagram Patterns

## Pattern 1: Simple Sequential Pipeline

```dot
digraph Pipeline {
  rankdir=LR;
  node [fontname="Arial", fontsize=10, style=filled, penwidth=1];
  edge [fontname="Arial", fontsize=8, penwidth=1.2];

  input [shape=cylinder, fillcolor="#00B945", fontcolor="white", label="Raw Data"];
  preprocess [shape=box, style=rounded, fillcolor="#0C5DA5", fontcolor="white", label="Preprocess"];
  model [shape=box, style=rounded, fillcolor="#0C5DA5", fontcolor="white", label="Model"];
  output [shape=cylinder, fillcolor="#00B945", fontcolor="white", label="Results"];

  input -> preprocess [label="files"];
  preprocess -> model [label="features"];
  model -> output [label="predictions"];
}
```

## Pattern 2: Multi-branch Architecture

Use `rankdir=TB` with branching and merging:

```dot
  input -> branchA;
  input -> branchB;
  branchA -> merge;
  branchB -> merge;
  merge -> output;
```

## Pattern 3: Feedback Loop

```dot
  output -> feedback [label="loss"];
  feedback -> model [label="gradients", style=dashed];
```

## Pattern 4: Nested Modules (Subgraphs)

```dot
  subgraph cluster_encoder {
    label="Encoder";
    style=dashed;
    color="#CCCCCC";
    conv1; conv2; pool;
  }
```
