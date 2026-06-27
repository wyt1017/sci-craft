# sci-craft Phase 1 实施计划

> 四层分层架构——核心层（期刊配置+规则库）、Skill 层（功能模块）、构建层（组装+校验）、适配层（多平台转换）

**Tech Stack:** Python 3.10+, YAML, Markdown, matplotlib, Graphviz, pytest, argparse

## File Structure

| File | Responsibility |
|------|----------------|
| `core/journals/_base.yaml` | 通用学术写作基线配置 |
| `core/journals/nature.yaml` | Nature 期刊规范 |
| `core/journals/science.yaml` | Science 期刊规范 |
| `core/rules/writing/sentence-length.md` | 句子长度规则 |
| `core/rules/writing/hedging.md` | 模糊表达规则 |
| `core/rules/writing/tense.md` | 时态规则 |
| `core/rules/writing/overclaim-detect.md` | 过度宣称检测规则 |
| `core/rules/writing/chinese-academic.md` | 中文学术写作规范 |
| `core/rules/figure/typography.md` | 图表字体规则 |
| `core/rules/figure/palette-nature.md` | Nature 配色方案 |
| `core/rules/figure/palette-science.md` | Science 配色方案 |
| `core/rules/figure/layout.md` | 图表布局规则 |
| `core/rules/figure/framework-diagram.md` | 框架图规则 |
| `core/rules/citation/format-nature.md` | Nature 引文格式规则 |
| `core/rules/citation/format-science.md` | Science 引文格式规则 |
| `core/rules/citation/integrity.md` | 引文完整性规则 |
| `core/templates/figures/bar-template.py` | 柱状图模板 |
| `core/templates/figures/line-template.py` | 折线图模板 |
| `core/templates/figures/heatmap-template.py` | 热力图模板 |
| `core/templates/figures/framework-template.py` | 框架图模板 |
| `skills/_shared/glossary.md` | 术语表 |
| `skills/_shared/style-guide.md` | 通用风格指南 |
| `skills/sci-figure/SKILL.md` | 科研图表 Skill 指令 |
| `skills/sci-framework/SKILL.md` | 框架图 Skill 指令 |
| `skills/sci-polishing/SKILL.md` | 文本润色 Skill 指令 |
| `skills/sci-writing/SKILL.md` | 论文写作 Skill 指令 |
| `skills/sci-citation/SKILL.md` | 文献引文 Skill 指令 |
| `skills/sci-reviewer/SKILL.md` | 模拟审稿 Skill 指令 |
| `skills/sci-response/SKILL.md` | 审稿回复 Skill 指令 |
| `skills/sci-reader/SKILL.md` | 论文阅读 Skill 指令 |
| `skills/sci-paper2ppt/SKILL.md` | 论文转PPT Skill 指令 |
| `skills/sci-data/SKILL.md` | 数据声明 Skill 指令 |
| `skills/bibliometrics-analyzer/SKILL.md` | 文献计量分析 Skill 指令 |
| `skills/literature-search/SKILL.md` | 文献检索 Skill 指令 |
| `skills/literature-summarizer/SKILL.md` | 文献摘要 Skill 指令 |
| `skills/research-gap-finder/SKILL.md` | 研究空白识别 Skill 指令 |
| `skills/research-ideation/SKILL.md` | 研究课题生成 Skill 指令 |
| `skills/systematic-review/SKILL.md` | 系统综述 Skill 指令 |
| `adapters/base.py` | 适配器基类 |
| `adapters/trae.py` | TRAE 适配器 |
| `adapters/codex.py` | Codex 适配器 |
| `adapters/claude.py` | Claude Code 适配器 |
| `builder/assembler.py` | 规则组装器 |
| `builder/validator.py` | Skill 校验器 |
| `scripts/build.py` | 构建命令入口 |
| `scripts/install.py` | 安装命令 |
| `tests/test_assembler.py` | 组装器测试 |
| `tests/test_validator.py` | 校验器测试 |
| `tests/test_adapters.py` | 适配器测试 |
| `.github/workflows/validate.yml` | CI 自动校验 |

## 开发路线

### Phase 1：核心框架 + 3 个 P0 Skill
- 搭建 core/ 目录结构和期刊配置
- 实现 builder/assembler.py 和 builder/validator.py
- 实现 sci-figure（Stable）
- 实现 sci-framework（Stable）
- 实现 sci-polishing（Stable）
- 实现 trae 适配器
- 编写测试

### Phase 2：写作链 + Codex/Claude 适配
- 实现 sci-writing（Beta）
- 实现 sci-citation（Beta）
- 实现 sci-reviewer（Beta）
- 实现 sci-response（Beta）
- 实现 codex 和 claude 适配器
- 增加 Science 期刊配置

### Phase 3：投稿链 + 完善
- 实现 sci-reader、sci-paper2ppt、sci-data
- 实现文献研究系列 Skill（bibliometrics-analyzer、literature-search 等）
- 中文写作规则
- CI 集成
