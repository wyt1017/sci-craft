# Graphviz Dot Syntax Reference

## Basic Structure

```dot
digraph DiagramName {
  rankdir=TB;        // TB=top-bottom, LR=left-right
  node [attributes];
  edge [attributes];

  NodeA -> NodeB;
}
```

## Node Shapes

| Shape | Use for |
|-------|---------|
| `box,style=rounded` | Processing modules |
| `cylinder` | Data stores |
| `parallelogram` | I/O |
| `diamond` | Decision points |
| `ellipse` | Start/end |
| `record` | Structured data |

## Node Attributes

```dot
nodeA [label="Display Label", shape=box, style=filled, fillcolor="#0C5DA5", fontcolor="white", fontsize=10, fontname="Arial", penwidth=1];
```

## Edge Attributes

```dot
nodeA -> nodeB [label="data flow", fontsize=8, penwidth=1.2, arrowsize=0.8, color="#474747"];
```

## Subgraphs (grouping)

```dot
subgraph cluster_0 {
  label="Module A";
  style=dashed;
  color="#CCCCCC";
  node1; node2;
}
```
