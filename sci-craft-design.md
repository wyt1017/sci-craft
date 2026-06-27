# sci-craft 设计文档

> 多期刊、多平台兼容的学术写作 Skill 框架

## 1. 项目概述

### 1.1 问题陈述

现有 `nature-skills` 项目存在以下不足：
- 仅覆盖 Nature 系列期刊，不支持 Science、Cell、IEEE 等其他顶级期刊
- 超过 80% 的模块处于 Beta/Draft 状态，质量不稳定
- 无法绘制论文框架图（Framework Diagram），这是 CS/工程类论文的核心需求
- 强依赖单一平台（Codex），安装配置复杂
- 缺乏自动化测试和质量保障
- 中文学术写作支持薄弱
- 项目出现商业化倾向，可能影响开源可持续性

### 1.2 项目目标

构建一个**分层架构的学术写作 Skill 框架**，核心原则：

- **一次编写，多平台运行**：Skill 定义与平台格式解耦，通过适配器自动转换
- **多期刊覆盖**：Nature、Science 等顶级期刊规范内置，可扩展
- **补足短板**：框架图绘制、自动化测试、中文写作支持
- **质量优先**：每个模块必须通过校验才能标记为 Stable

### 1.3 目标用户

- 科研人员（硕士/博士/博后/PI）
- 需要向国际顶级期刊投稿的学术作者
- 有一定技术背景，使用 AI 编程助手辅助科研的用户

### 1.4 非目标

- 不做通用 AI 写作工具（非 ChatGPT 替代品）
- 不做论文代写（强调学术伦理，AI 仅辅助而非替代）
- 不做期刊投稿系统对接（不做 ScholarOne/API 集成）

---

## 2. 架构设计

### 2.1 分层架构

```
┌─────────────────────────────────────────┐
│            用户接口（CLI / 脚本）          │
├─────────────────────────────────────────┤
│              适配层 (adapters/)          │  ← 平台格式转换
├─────────────────────────────────────────┤
│             构建层 (builder/)            │  ← 规则组装 + 校验
├─────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────────┐  │
│  │  Skill 定义  │  │   期刊规范配置    │  │  ← 业务逻辑
│  │  (skills/)   │  │  (core/journals/) │  │
│  └──────┬──────┘  └────────┬─────────┘  │
│         └────────┬─────────┘             │
│            可复用规则库 (core/rules/)     │  ← 原子化规则
├─────────────────────────────────────────┤
│              共享资源 (_shared/)          │  ← 模板、资产
└─────────────────────────────────────────┘
```

### 2.2 数据流

```
输入：用户选择目标期刊 + 目标平台
  ↓
1. 加载 core/journals/<journal>.yaml → 获取期刊规范参数
  ↓
2. 加载 core/rules/**/*.md → 获取规则片段
  ↓
3. builder/assembler.py 组合规则 + 期刊参数 → 生成 SKILL.md
  ↓
4. builder/validator.py 校验完整性 → 通过/拒绝
  ↓
5. adapters/<platform>.py 转换格式 → 平台特有文件
  ↓
6. 输出到 output/<platform>/<skill-name>/
```

### 2.3 目录结构

```
sci-craft/
├── core/                              # 核心层
│   ├── journals/                      # 期刊配置（YAML）
│   │   ├── _base.yaml                 # 通用学术写作基线
│   │   ├── nature.yaml                # Nature 系列规范
│   │   ├── science.yaml               # Science 系列规范
│   │   └── cell.yaml                  # Cell 系列规范（未来）
│   ├── rules/                         # 可复用规则库
│   │   ├── writing/                   # 写作规则
│   │   │   ├── sentence-length.md
│   │   │   ├── hedging.md
│   │   │   ├── tense.md
│   │   │   ├── overclaim-detect.md
│   │   │   └── chinese-academic.md    # 中文学术写作规范
│   │   ├── figure/                    # 图表规则
│   │   │   ├── typography.md
│   │   │   ├── palette-nature.md
│   │   │   ├── palette-science.md
│   │   │   ├── layout.md
│   │   │   └── framework-diagram.md   # 框架图规则
│   │   └── citation/                  # 引文规则
│   │       ├── format-nature.md
│   │       ├── format-science.md
│   │       └── integrity.md
│   └── templates/                     # 通用模板
│       ├── figures/                   # 图表模板脚本
│       ├── responses/                 # 审稿回复模板
│       └── data-statements/           # 数据声明模板
│
├── skills/                            # Skill 定义层
│   ├── _shared/                       # 共享资源
│   │   ├── glossary.md                # 术语表
│   │   └── style-guide.md             # 通用风格指南
│   ├── sci-figure/                    # 科研图表（含框架图）
│   │   ├── SKILL.md
│   │   ├── README.md
│   │   └── references/
│   ├── sci-framework/                 # 框架图绘制（新增）
│   │   ├── SKILL.md
│   │   ├── README.md
│   │   └── references/
│   ├── sci-polishing/                 # 文本润色
│   ├── sci-writing/                   # 论文写作
│   ├── sci-citation/                  # 文献与引文
│   ├── sci-reviewer/                  # 模拟审稿
│   ├── sci-response/                  # 审稿回复
│   ├── sci-reader/                    # 论文阅读
│   ├── sci-paper2ppt/                 # 论文转PPT
│   └── sci-data/                      # 数据声明
│
├── adapters/                          # 适配层
│   ├── base.py                        # 适配器基类
│   ├── trae.py                        # TRAE 适配器
│   ├── codex.py                       # Codex 适配器
│   └── claude.py                      # Claude Code 适配器
│
├── builder/                           # 构建层
│   ├── assembler.py                   # 核心：规则→SKILL.md 组装
│   └── validator.py                   # 校验：Skill 完整性检查
│
├── scripts/                           # 脚本
│   ├── build.py                       # 构建命令入口
│   └── install.py                     # 安装到目标平台
│
├── output/                            # 构建产物（.gitignore）
│
├── tests/                             # 测试
│   ├── test_rules.py
│   ├── test_adapters.py
│   ├── test_assembler.py
│   └── test_validator.py
│
├── .github/                           # CI/CD
│   └── workflows/
│       └── validate.yml               # 自动校验 workflow
│
└── README.md
```

---

## 3. 模块详细设计

### 3.1 期刊配置 (core/journals/)

每个期刊一个 YAML 文件，定义该期刊的规范参数：

```yaml
# core/journals/nature.yaml 示例
name: Nature
family: CNS
publisher: Springer Nature
writing:
  max_sentence_words: 30
  english_variant: british
  hedging_levels: 3
  tense_rules:
    results: past
    discussion: present_hedged
  forbidden_words: [prove, establish, breakthrough]
figure:
  font_family: sans-serif
  font_sans: [Arial, DejaVu Sans, Liberation Sans]
  output_format:
    primary: svg
    secondary: png@300dpi
  palette: nature-primary
  min_dpi: 300
  framework_diagram:
    enabled: true
    tool: graphviz+matplotlib
    style: minimal-flat
citation:
  style: nature-numbered
  export_formats: [enw, ris, zotero-rdf]
  max_authors_display: 5
submission:
  cover_letter_required: true
  data_availability_required: true
  competing_interests_required: true
```

```yaml
# core/journals/science.yaml 示例
name: Science
family: AAAS
publisher: AAAS
writing:
  max_sentence_words: 25
  english_variant: american          # 美式英语，与 Nature 不同
  hedging_levels: 4
  tense_rules:
    results: past
    discussion: present_hedged
  forbidden_words: [prove, demonstrate conclusively]
figure:
  font_family: sans-serif
  font_sans: [Helvetica, Arial]
  output_format:
    primary: svg
    secondary: png@600dpi            # Science 要求更高 DPI
  palette: science-primary
  min_dpi: 600
  framework_diagram:
    enabled: true
    tool: graphviz+matplotlib
    style: structured-blocks
citation:
  style: science-numbered
  export_formats: [enw, ris, bibtex]
  max_authors_display: 10
submission:
  cover_letter_required: true
  data_availability_required: true
  competing_interests_required: true
```

`_base.yaml` 定义所有期刊共享的基线规范，子配置继承并覆盖。

### 3.2 Skill 模块 (skills/)

每个 skill 目录包含：

| 文件 | 用途 | 必须 |
|------|------|------|
| `SKILL.md` | Skill 主指令文件 | 是 |
| `README.md` | 使用说明 | 是 |
| `manifest.yaml` | 元数据和路由信息 | 是 |
| `references/` | 参考规则文件 | 按需 |
| `static/` | 静态资源 | 按需 |

#### Skill 模块清单

| Skill | 优先级 | 状态 | 期刊感知 | 描述 |
|-------|--------|------|----------|------|
| `sci-figure` | P0 | Stable | 是 | 科研图表生成（matplotlib/R），支持 Nature/Science 双配色 |
| `sci-framework` | P0 | Stable | 是 | **框架图绘制**（graphviz + matplotlib），补足 nature-skills 短板 |
| `sci-polishing` | P0 | Stable | 是 | 学术文本润色，自动匹配目标期刊规范 |
| `sci-writing` | P1 | Beta | 是 | 论文各章节撰写 |
| `sci-citation` | P1 | Beta | 是 | 文献检索与引文管理，支持多种引文格式 |
| `sci-reviewer` | P1 | Beta | 是 | 模拟审稿，生成审稿报告 |
| `sci-response` | P1 | Beta | 是 | 审稿回复信撰写 |
| `sci-reader` | P2 | Draft | 否 | 双语论文阅读器 |
| `sci-paper2ppt` | P2 | Draft | 否 | 论文转PPT |
| `sci-data` | P2 | Draft | 是 | 数据可用性声明 |

#### 框架图 Skill 设计（sci-framework）—— 核心差异化

这是 nature-skills 明确表示无法实现的功能。解决方案：

1. **输入**：用户用自然语言描述框架结构
2. **解析**：AI 将自然语言转换为结构化的组件关系描述（JSON）
3. **渲染**：使用 Graphviz（dot 语言）+ matplotlib 生成可编辑 SVG
4. **输出**：SVG 文件 + 可编辑的 dot 源文件

支持的框架图类型：
- 模型架构图（Model Architecture）
- 系统流程图（System Pipeline）
- 实验设计图（Experimental Setup）
- 数据流图（Data Flow Diagram）

关键规则：
- 每个组件必须有明确的输入/输出标签
- 颜色使用期刊配色方案
- 文字使用 Arial/Helvetica，最小 8pt
- 箭头使用 > 方向，不使用圆圈箭头
- 输出 SVG 中文字必须保留为 `<text>` 节点，不转路径

### 3.3 适配层 (adapters/)

适配器负责将统一的 Skill 格式转换为各平台特有格式。

#### 适配器基类接口

```python
class BaseAdapter(ABC):
    platform_name: str

    @abstractmethod
    def adapt_skill(self, skill_dir: Path, output_dir: Path, journal: str) -> None:
        """将 skill 目录适配到目标平台格式"""
        pass

    @abstractmethod
    def get_install_path(self) -> Path:
        """返回目标平台的 Skill 安装路径"""
        pass
```

#### 各平台差异

| 特性 | TRAE | Codex | Claude Code |
|------|------|-------|-------------|
| 指令文件 | SKILL.md | SKILL.md | CLAUDE.md |
| 元数据 | manifest.yaml | 无 | 无 |
| 安装路径 | `.trae/skills/` | `~/.codex/skills/` | 项目根目录 |
| 触发方式 | 自动关键词 | 自动关键词 | 斜杠命令 |
| 共享资源 | `skills/_shared/` | `skills/_shared/` | 直接内联 |

### 3.4 构建层 (builder/)

#### assembler.py

核心逻辑：
1. 读取目标期刊 YAML 配置
2. 加载 skill 的 SKILL.md 模板
3. 根据期刊参数填充模板变量（如 `{{max_sentence_words}}` → `30`）
4. 根据 skill 需要加载对应 rules/ 下的规则片段
5. 组装为完整的 SKILL.md

#### validator.py

校验项：
- SKILL.md 是否存在且非空
- 必需的 frontmatter 字段是否完整
- references/ 中引用的文件是否都存在
- manifest.yaml 格式是否正确
- 图表规则是否包含必需的 rcParams
- 写作规则是否包含期刊参数

只有通过全部校验的 skill 才能标记为 Stable。

### 3.5 构建命令

```bash
# 构建所有 skill，输出到 output/
python scripts/build.py --journal nature --platform trae

# 构建单个 skill
python scripts/build.py --journal science --platform codex --skill sci-figure

# 一键安装到目标平台
python scripts/install.py --journal nature --platform trae

# 校验所有 skill
python scripts/build.py --validate-only
```

---

## 4. 与 nature-skills 的差异化对比

| 维度 | nature-skills | sci-craft |
|------|--------------|-----------|
| 期刊覆盖 | 仅 Nature 系列 | Nature + Science + 可扩展 |
| 框架图 | 不支持 | sci-framework 支持 |
| 多平台 | 手动复制 | 适配器自动转换 |
| 模块稳定性 | 82% Beta/Draft | 必须通过 validator 才能标记 Stable |
| 自动化测试 | 无 | tests/ + CI |
| 中文支持 | 弱 | core/rules/writing/chinese-academic.md |
| 期刊规范 | 硬编码在 SKILL.md 中 | YAML 配置文件，可扩展 |
| 安装方式 | 手动 git clone + cp | scripts/install.py 一键安装 |

---

## 5. 技术栈

| 组件 | 技术选型 | 理由 |
|------|---------|------|
| 规则定义 | Markdown + YAML | 人类可读，AI 可直接消费 |
| 期刊配置 | YAML | 结构化、可继承 |
| 适配器 | Python | 跨平台，科研社区主流 |
| 图表生成 | matplotlib + Graphviz | matplotlib 做数据图，Graphviz 做框架图 |
| 构建工具 | Python CLI | 轻量，无额外依赖 |
| 测试 | pytest | Python 标准测试框架 |
| CI | GitHub Actions | 自动校验 |

---

## 6. 开发路线

### Phase 1：核心框架 + 2 个 P0 Skill
- 搭建 core/ 目录结构和期刊配置
- 实现 builder/assembler.py 和 builder/validator.py
- 实现 sci-figure（Stable）
- 实现 sci-framework（Stable）
- 实现 trae 适配器
- 编写测试

### Phase 2：写作链 + Codex/Claude 适配
- 实现 sci-polishing（Stable）
- 实现 sci-writing（Beta）
- 实现 sci-citation（Beta）
- 实现 codex 和 claude 适配器
- 增加 Science 期刊配置

### Phase 3：投稿链 + 完善
- 实现 sci-reviewer、sci-response、sci-reader
- 实现 sci-paper2ppt、sci-data
- 中文写作规则
- CI 集成

---

## 7. 开源策略

- MIT 许可证
- 不在 README 中投放商业招募信息
- Issue 和 PR 模板规范化
- 语义化版本号管理
