# sci-craft

> Multi-journal, multi-platform academic writing Skill framework

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform: TRAE](https://img.shields.io/badge/platform-TRAE-green.svg)](https://www.trae.cn)
[![Platform: Codex](https://img.shields.io/badge/platform-Codex-orange.svg)](https://openai.com/index/introducing-codex-cli/)
[![Platform: Claude Code](https://img.shields.io/badge/platform-Claude_Code-purple.svg)](https://docs.anthropic.com/en/docs/claude-code/overview)

## Overview

sci-craft is a layered architecture for academic writing Skills that supports **Nature** and **Science** journals natively, with adapters for **TRAE**, **Codex**, and **Claude Code** platforms.

Once written, a Skill automatically adapts to different platforms and journal requirements.

## Architecture

Four-layer design:

1. **Core Layer** — Journal configurations (YAML) + Rules library (Markdown)
2. **Skill Layer** — 16 functional modules covering the full research workflow
3. **Builder Layer** — Assembler (config merging + rule injection) + Validator (completeness checks)
4. **Adapter Layer** — Platform converters (TRAE, Codex, Claude Code)

```
┌─────────────────────────────────────┐
│           Adapter Layer             │  ← TRAE / Codex / Claude Code
├─────────────────────────────────────┤
│            Skill Layer              │  ← 16 Skills
├─────────────────────────────────────┤
│          Builder Layer              │  ← Assembler + Validator
├─────────────────────────────────────┤
│            Core Layer               │  ← Journals + Rules + Templates
└─────────────────────────────────────┘
```

## Skills

### Stable (Production-ready)

| Skill | Description | Journal-aware |
|-------|-------------|---------------|
| `sci-figure` | Journal-quality scientific figures with Nature/Science palettes | Yes |
| `sci-framework` | Graphviz-based framework diagrams (core differentiator) | Yes |
| `sci-polishing` | 12-step academic prose polishing workflow | Yes |

### Beta (Testing)

| Skill | Description | Journal-aware |
|-------|-------------|---------------|
| `sci-writing` | Section-by-section manuscript drafting | Yes |
| `sci-citation` | Literature search and citation management | Yes |
| `sci-reviewer` | Simulated peer review (3 independent reports) | Yes |
| `sci-response` | Point-by-point reviewer response letters | Yes |
| `bibliometrics-analyzer` | Co-occurrence, burst detection, collaboration networks | No |
| `literature-search` | PICO/SPIDER framework, multi-database search | No |
| `literature-summarizer` | Four-layer summarization, knowledge graphs | No |
| `research-gap-finder` | Five-dimensional gap matrix, contradiction analysis | No |
| `research-ideation` | Gap-to-idea conversion, priority ranking | No |
| `systematic-review` | PRISMA workflow, meta-analysis support | No |

### Draft (Development)

| Skill | Description |
|-------|-------------|
| `sci-reader` | Bilingual paper reader with source anchors |
| `sci-paper2ppt` | Paper-to-PPTX generation |
| `sci-data` | Data availability statements, FAIR compliance |

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/wyt1017/sci-craft.git
cd sci-craft

# Install dependencies
pip install pyyaml pytest

# Build for Nature journal on TRAE
python scripts/build.py --journal nature --platform trae

# Install to TRAE skills directory
python scripts/install.py --journal nature --platform trae
```

### Usage in TRAE

Once installed, trigger a skill by saying:
- "Polish this abstract to Nature style"
- "Draw a model architecture diagram"
- "Write an introduction for a paper about [topic]"

## Platform Support

| Platform | Adapter | Install Path |
|----------|---------|--------------|
| TRAE | `adapters/trae.py` | `~/.trae/skills/` |
| Codex | `adapters/codex.py` | `~/.codex/skills/` |
| Claude Code | `adapters/claude.py` | Project root |

## Journal Support

| Journal | Config | Citation Style | Max Sentence | DPI |
|---------|--------|----------------|--------------|-----|
| Nature | `core/journals/nature.yaml` | Numbered superscript | 30 words | 300 |
| Science | `core/journals/science.yaml` | Superscript numbers | 25 words | 600 |

## Key Differentiators vs nature-skills

| Feature | nature-skills | sci-craft |
|---------|---------------|-----------|
| Framework diagrams | No | Yes (sci-framework) |
| Multi-journal | Nature only | Nature + Science |
| Multi-platform | Manual copy | Auto-adapt via adapters |
| Quality assurance | None | Validator + CI + tests |
| Chinese support | Weak | Dedicated rules |
| Research workflow | Limited | 16 skills covering full pipeline |

## Project Structure

```
sci-craft/
├── core/                    # Core layer
│   ├── journals/            # Journal YAML configs
│   ├── rules/               # Markdown rules (writing/figure/citation)
│   └── templates/           # Python template scripts
├── skills/                  # Skill layer
│   ├── _shared/             # Shared resources
│   ├── sci-figure/          # Scientific figures
│   ├── sci-framework/       # Framework diagrams
│   ├── sci-polishing/       # Text polishing
│   └── ...                  # 13 more skills
├── builder/                 # Builder layer
│   ├── assembler.py         # Config merging + rule injection
│   └── validator.py         # Completeness checks
├── adapters/                # Adapter layer
│   ├── base.py              # Base adapter interface
│   ├── trae.py              # TRAE adapter
│   ├── codex.py             # Codex adapter
│   └── claude.py            # Claude Code adapter
├── scripts/                 # Build and install scripts
│   ├── build.py
│   └── install.py
├── tests/                   # pytest test suite
├── docs/                    # Design specs and plans
└── .github/workflows/       # CI validation
```

## Development

```bash
# Run all tests
python -m pytest tests/ -v

# Validate all skills
python scripts/build.py --validate-only

# Build for Science journal
python scripts/build.py --journal science --platform trae

# Build for all platforms
python scripts/build.py --journal nature --platform trae
python scripts/build.py --journal nature --platform codex
python scripts/build.py --journal nature --platform claude
```

## License

MIT License
