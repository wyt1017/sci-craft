# sci-craft — 多期刊、多平台兼容的学术写作 Skill 框架

> 分层架构的学术写作 Skill 框架，一次编写，多平台运行

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/wyt1017/sci-craft/actions/workflows/validate.yml/badge.svg)](https://github.com/wyt1017/sci-craft/actions)

## 概述

sci-craft 是一个面向科研写作的 Skill 框架，支持 **Nature** 和 **Science** 两大顶级期刊的写作规范，并兼容 **TRAE**、**Codex** 和 **Claude Code** 三个 AI 编程平台。

### 核心特性

- **多期刊支持**：Nature（30 词/句、英式英语、3 级模糊度）与 Science（25 词/句、美式英语、4 级模糊度）一键切换
- **多平台兼容**：同一套 Skill 通过适配器自动转换为不同平台的格式
- **框架图绘制**：使用 Graphviz dot 语言生成可编辑 SVG 框架图（填补主流工具空白）
- **16 个 Skill**：覆盖文献检索→阅读→摘要→空白识别→课题生成→写作→润色→投稿全流程（3 Stable + 10 Beta + 3 Draft）
- **自动化测试**：26 个单元测试 + CI 自动校验

## 快速开始

### 安装到 TRAE

```bash
# 构建并安装（Nature 期刊）
python scripts/build.py --journal nature --platform trae
python scripts/install.py --journal nature --platform trae

# 或一步到位
python scripts/build.py --journal nature --platform trae --install
```

### 安装到 Codex

```bash
python scripts/build.py --journal nature --platform codex
python scripts/install.py --journal nature --platform codex
```

### 安装到 Claude Code

```bash
python scripts/build.py --journal nature --platform claude
python scripts/install.py --journal nature --platform claude
```

## 架构设计

```
sci-craft/
├── core/                    # 核心层
│   ├── journals/            # 期刊配置（YAML）
│   │   ├── _base.yaml       # 通用基线
│   │   ├── nature.yaml      # Nature 规范
│   │   └── science.yaml     # Science 规范
│   ├── rules/               # 规则库
│   │   ├── writing/         # 写作规则
│   │   ├── figure/          # 图表规则
│   │   └── citation/        # 引文规则
│   ├── templates/           # 图表模板脚本
│   └── skills/              # 预置 Skill 模板
├── skills/                  # Skill 层（16 个）
│   ├── _shared/             # 共享资源
│   ├── sci-figure/          # 科研图表（Stable）
│   ├── sci-framework/       # 框架图绘制（Stable）
│   ├── sci-polishing/       # 文本润色（Stable）
│   ├── sci-writing/         # 论文写作（Beta）
│   ├── sci-citation/        # 文献引文（Beta）
│   ├── sci-reviewer/        # 模拟审稿（Beta）
│   ├── sci-response/        # 审稿回复（Beta）
│   ├── sci-reader/          # 论文阅读（Draft）
│   ├── sci-paper2ppt/       # 论文转PPT（Draft）
│   ├── sci-data/            # 数据声明（Draft）
│   ├── bibliometrics-analyzer/
│   ├── literature-search/
│   ├── literature-summarizer/
│   ├── research-gap-finder/
│   ├── research-ideation/
│   └── systematic-review/
├── builder/                 # 构建层
│   ├── assembler.py         # 规则组装器
│   └── validator.py         # Skill 校验器
├── adapters/                # 适配层
│   ├── base.py              # 适配器基类
│   ├── trae.py              # TRAE 适配器
│   ├── codex.py             # Codex 适配器
│   └── claude.py            # Claude Code 适配器
├── scripts/                 # 构建脚本
│   ├── build.py             # 构建入口
│   └── install.py           # 安装脚本
├── tests/                   # 测试（26 个）
└── .github/workflows/       # CI 配置
```

## Skill 清单

### Stable（稳定版）

| Skill | 描述 | 期刊感知 |
|-------|------|---------|
| `sci-figure` | Nature/Science 双配色科研图表 | ✅ |
| `sci-framework` | Graphviz 框架图绘制（核心差异化） | ✅ |
| `sci-polishing` | 12步学术润色工作流 | ✅ |

### Beta（测试版）

| Skill | 描述 | 期刊感知 |
|-------|------|---------|
| `sci-writing` | 论文各章节撰写 | ✅ |
| `sci-citation` | 文献检索与引文管理 | ✅ |
| `sci-reviewer` | 生成3份独立审稿报告 | ✅ |
| `sci-response` | 逐条审稿回复信撰写 | ✅ |
| `bibliometrics-analyzer` | 文献计量分析 | ❌ |
| `literature-search` | PICO/SPIDER 文献检索 | ❌ |
| `literature-summarizer` | 四层分层摘要 | ❌ |
| `research-gap-finder` | 五维空白矩阵 | ❌ |
| `research-ideation` | 空白→课题转化 | ❌ |
| `systematic-review` | PRISMA 系统综述 | ❌ |

### Draft（草稿版）

| Skill | 描述 | 期刊感知 |
|-------|------|---------|
| `sci-reader` | 双语论文阅读器 | ❌ |
| `sci-paper2ppt` | 论文转中文PPT | ❌ |
| `sci-data` | 数据可用性声明 | ✅ |

## 期刊配置

### Nature
- 句子长度：≤ 30 词
- 英语变体：英式
- 模糊度：3 级
- 图表 DPI：300
- 配色：Nature Blue/Green/Red/Orange/Purple/Gray

### Science
- 句子长度：≤ 25 词
- 英语变体：美式
- 模糊度：4 级
- 图表 DPI：600
- 配色：Science Teal/Vermilion/Green/Gold/Violet/Gray

## 多平台适配

| 平台 | 适配器 | 安装路径 | 特殊处理 |
|------|--------|---------|---------|
| TRAE | `adapters/trae.py` | `~/.trae/skills/` | 完整复制 |
| Codex | `adapters/codex.py` | `~/.codex/skills/` | 移除 manifest.yaml |
| Claude Code | `adapters/claude.py` | 项目根目录 | 重命名 SKILL.md → CLAUDE.md，内联 _shared |

## 开发

### 运行测试

```bash
python -m pytest tests/ -v
```

### 验证 Skill

```bash
python scripts/build.py --validate-only
```

### 构建单个 Skill

```bash
python scripts/build.py --journal nature --skill sci-polishing
```

## License

MIT License

## Contributing & Feedback

We welcome bug reports and feature suggestions!

- **Report a Bug**: [GitHub Issues - Bug Report](https://github.com/wyt1017/sci-craft/issues/new?template=bug-report.md)
- **Request a Feature**: [GitHub Issues - Feature Request](https://github.com/wyt1017/sci-craft/issues/new?template=feature-request.md)
- **General Feedback**: [GitHub Issues - Skill Feedback](https://github.com/wyt1017/sci-craft/issues/new?template=skill-feedback.md). See [LICENSE](LICENSE) for details.

## 项目文档

- [设计文档](docs/superpowers/specs/2026-06-26-sci-craft-design.md)
- [实施计划](docs/superpowers/plans/2026-06-26-sci-craft-phase1.md)
