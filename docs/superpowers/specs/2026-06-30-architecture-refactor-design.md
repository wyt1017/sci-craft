# sci-craft 架构重构设计文档

> **目标**: 对 sci-craft 进行分层重组架构重构，新增工作流编排、Jinja2 模板引擎、双重校验、依赖级缓存四大核心能力。

---

## 一、背景与目标

### 当前问题

sci-craft 现有架构存在以下不足：

1. **Skill 之间无法联动** — 16 个 Skill 是独立的，无法形成流水线
2. **模板引擎过于简单** — 只支持 `{{key}}` 字符串替换，不支持条件、循环等
3. **Validator 校验太浅** — 只检查文件存在性，不校验模板变量完整性、规则引用有效性
4. **每次全量重建** — 没有缓存机制，效率低

### 重构目标

1. **工作流编排** — 项目级 YAML 工作流定义，支持 Skill 串联、条件分支、数据传递
2. **Jinja2 模板引擎** — 支持条件判断 `{% if %}`、循环 `{% for %}`、宏定义
3. **双重校验** — 静态校验（构建前）+ 运行时校验（构建后）
4. **依赖级缓存** — 计算依赖图，只重建变化的 Skill

---

## 二、新架构概览

### 目录结构

```
sci-craft/
├── core/                    # 核心配置层
│   ├── journals/            # 期刊配置（不变）
│   │   ├── _base.yaml
│   │   ├── nature.yaml
│   │   └── science.yaml
│   ├── rules/               # 规则库（不变）
│   │   ├── writing/
│   │   ├── figure/
│   │   └── citation/
│   ├── workflows/           # 新增：项目级工作流定义
│   │   ├── literature-review.yaml
│   │   ├── full-pipeline.yaml
│   │   └── ...
│   └── templates/           # 图表模板（不变）
│
├── skills/                  # Skill 层（不变）
│   ├── _shared/
│   ├── sci-polishing/
│   ├── sci-figure/
│   └── ...（16 个 Skill）
│
├── engine/                  # 新增：执行引擎层
│   ├── __init__.py
│   ├── renderer.py          # Jinja2 模板渲染引擎
│   ├── validator.py         # 静态 + 运行时校验
│   ├── cache.py             # 依赖级缓存
│   ├── workflow.py          # 工作流编排执行
│   └── planner.py           # 构建计划生成
│
├── adapters/                # 适配层（不变）
│   ├── base.py
│   ├── trae.py
│   ├── codex.py
│   └── claude.py
│
├── cli/                     # 新增：CLI 入口层
│   ├── __init__.py
│   ├── build.py             # 构建命令
│   ├── workflow.py          # 工作流命令
│   ├── validate.py          # 校验命令
│   └── cache.py             # 缓存管理命令
│
├── tests/                   # 测试层
│   ├── test_engine/         # 新增：engine 模块测试
│   ├── test_adapters/       # 不变
│   ├── test_cli/            # 新增：cli 模块测试
│   └── ...
│
├── pyproject.toml           # 新增 jinja2 依赖
├── README.md
└── .github/workflows/
```

### 模块职责

| 模块 | 职责 |
|---|---|
| `core/workflows/` | 存放项目级工作流 YAML 定义 |
| `engine/renderer.py` | Jinja2 模板渲染，支持条件、循环、宏 |
| `engine/validator.py` | 静态校验（模板变量完整性、规则引用）+ 运行时校验（残留占位符） |
| `engine/cache.py` | 依赖级缓存，计算依赖图，只重建变化的 Skill |
| `engine/workflow.py` | 工作流执行引擎，解析 YAML、拓扑排序、执行步骤 |
| `engine/planner.py` | 构建计划生成，结合缓存和依赖图 |
| `cli/` | 命令行入口，替代原 scripts/ |

---

## 三、engine/renderer.py — Jinja2 模板渲染引擎

### 接口设计

```python
class Renderer:
    """Jinja2 模板渲染引擎"""
    
    def __init__(self, core_dir: Path):
        self.journals_dir = core_dir / "journals"
        self.rules_dir = core_dir / "rules"
        self._env = Environment(
            loader=FileSystemLoader(str(core_dir)),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )
    
    def render_skill(self, journal: str, skill_dir: Path) -> str:
        """渲染单个 Skill 的 SKILL.md"""
        config = load_journal_config(journal, self.journals_dir)
        template_path = skill_dir / "SKILL.md"
        template = self._env.from_string(template_path.read_text(encoding="utf-8"))
        manifest = self._load_manifest(skill_dir)
        context = self._build_context(config, manifest, skill_dir)
        return template.render(**context)
    
    def _build_context(self, config: dict, manifest: dict, skill_dir: Path) -> dict:
        """构建 Jinja2 渲染上下文"""
        return {
            **flatten_config(config),
            "rules": self._load_rules(manifest.get("rules", []), config),
            "include_rule": lambda name: self._include_rule(name, config),
            "journal_is": lambda j: config.get("name") == j,
        }
```

### 新增 Jinja2 语法示例

在 SKILL.md 中可以这样写：

```markdown
# {{name}} Style Guide

{% if journal_is("Nature") %}
## British English Rules
- Use "signalling" not "signaling"
{% elif journal_is("Science") %}
## American English Rules
- Use "signaling" not "signalling"
{% endif %}

Max sentence length: {{writing.max_sentence_words}} words

{% for rule in rules %}
---
{{ rule }}
{% endfor %}
```

---

## 四、engine/validator.py — 双重校验

### 静态校验（构建前）

```python
class StaticValidation:
    """静态校验 — 构建前"""
    
    def validate_manifest(self, skill_dir: Path) -> list[Error]:
        """校验 manifest.yaml 结构"""
        # 必填字段、版本格式、status 合法值、triggers 非空
        
    def validate_rules_refs(self, skill_dir: Path, rules_dir: Path) -> list[Error]:
        """校验 rules 引用路径是否存在"""
        
    def validate_template_variables(self, skill_dir: Path, journals_dir: Path, journal: str) -> list[Error]:
        """校验 SKILL.md 中模板变量都在 config 中存在"""
        
    def validate_references(self, skill_dir: Path) -> list[Error]:
        """校验 references 文件存在性"""
```

### 运行时校验（构建后）

```python
class RuntimeValidation:
    """运行时校验 — 构建后"""
    
    def validate_rendered_output(self, rendered_content: str) -> list[Error]:
        """校验无残留占位符 {{...}}"""
        
    def validate_rule_injection(self, rendered_content: str, manifest: dict, rules_dir: Path) -> list[Error]:
        """校验规则注入正确"""
```

### 校验流程

```
静态校验 → 构建渲染 → 运行时校验 → 输出到 build/
```

---

## 五、engine/cache.py — 依赖级缓存

### 接口设计

```python
class DependencyCache:
    """依赖级缓存管理器"""
    
    CACHE_FILE = Path(".sci_craft_cache.json")
    
    def compute_dependency_graph(self, skills_dir: Path) -> dict[str, DepNode]:
        """计算 Skill 的依赖图"""
        # 每个 Skill 依赖：manifest.yaml、SKILL.md、rules、references、journal config
        
    def compute_cache_hash(self, skill_name: str, dep_node: DepNode, journal: str) -> str:
        """计算输入参数哈希值"""
        
    def should_rebuild(self, skill_name: str, journal: str, dep_node: DepNode) -> bool:
        """判断是否需要重建"""
        
    def update_cache(self, skill_name: str, dep_node: DepNode, journal: str, hash_val: str) -> None:
        """更新缓存记录"""
```

### 缓存数据结构

```json
{
  "skills": {
    "sci-polishing": {
      "nature": {
        "hash": "a1b2c3d4...",
        "timestamp": "2026-06-28T10:30:00Z",
        "deps": {
          "manifest": "abc123...",
          "skill_md": "def456...",
          "rules": ["writing/sentence-length.md", ...],
          "references": ["phrasebank.md", ...]
        }
      }
    }
  }
}
```

---

## 六、engine/workflow.py — 工作流编排引擎

### 工作流 YAML 格式

```yaml
# core/workflows/literature-review.yaml
name: literature-review
description: 文献检索 → 阅读 → 摘要 → 空白识别 全流程
steps:
  - id: step1
    skill: literature-search
    journal: nature
    platform: trae
    config:
      query: "deep learning medical imaging"
      
  - id: step2
    skill: literature-summarizer
    journal: nature
    platform: trae
    depends_on: [step1]
    config:
      depth: full
      
  - id: step3
    skill: research-gap-finder
    journal: nature
    platform: trae
    depends_on: [step2]
```

### 接口设计

```python
class WorkflowEngine:
    """工作流执行引擎"""
    
    def load_workflow(self, workflow_name: str) -> WorkflowDef:
        """加载工作流定义"""
        
    def execute(self, workflow_def: WorkflowDef, dry_run: bool = False) -> WorkflowResult:
        """执行工作流"""
        # 1. 解析依赖图（拓扑排序）
        # 2. 按依赖顺序执行每个 step
        # 3. 收集输出
        
    def resolve_dependencies(self, steps: list[StepDef]) -> list[list[str]]:
        """解析步骤依赖关系，返回执行顺序"""
        
    def validate_workflow(self, workflow_def: WorkflowDef) -> list[Error]:
        """校验工作流定义合法性"""
        # skill 存在性、依赖环检测、config 合法性
```

---

## 七、engine/planner.py — 构建计划生成

### 接口设计

```python
class BuildPlanner:
    """构建计划生成器"""
    
    def plan(self, journal: str, platform: str, skills: list[str],
             cache: DependencyCache, dep_graph: dict) -> BuildPlan:
        """生成构建计划
        
        返回：
        BuildPlan {
            rebuild: [skill_a, skill_c],  # 需要重建
            skip: [skill_b, skill_d],      # 缓存命中
            order: [...],                   # 执行顺序
        }
        """
```

---

## 八、cli/ — 命令行入口

### 命令设计

```bash
# 构建单个 skill
python -m cli build --journal nature --skill sci-polishing

# 构建所有 skill
python -m cli build --journal nature --platform trae

# 增量构建
python -m cli build --journal nature --incremental

# 执行工作流
python -m cli workflow run literature-review

# 校验所有 skill
python -m cli validate

# 查看缓存状态
python -m cli cache stats

# 清除缓存
python -m cli cache clear
```

---

## 九、迁移方案

### 阶段一：基础搭建（Week 1）

1. 创建 `engine/` 目录和基础模块
2. 创建 `cli/` 目录和基础命令
3. 创建 `core/workflows/` 目录和示例工作流
4. 更新 `pyproject.toml` 新增 jinja2 依赖

### 阶段二：模板引擎替换（Week 2）

1. 实现 `engine/renderer.py`
2. 将现有 Skill 的 SKILL.md 迁移到 Jinja2 语法（可选，向后兼容）
3. 测试渲染功能

### 阶段三：校验增强（Week 3）

1. 实现 `engine/validator.py` 静态校验
2. 实现运行时校验
3. 集成到构建流程

### 阶段四：缓存机制（Week 4）

1. 实现 `engine/cache.py`
2. 实现 `engine/planner.py`
3. 集成到 CLI build 命令

### 阶段五：工作流引擎（Week 5）

1. 实现 `engine/workflow.py`
2. 创建示例工作流 YAML
3. 实现 CLI workflow 命令

### 阶段六：清理与文档（Week 6）

1. 移除旧 `scripts/` 目录（保留兼容性调用）
2. 移除旧 `builder/` 目录
3. 更新 README 和文档
4. 完善 CI 配置

---

## 十、依赖变更

```toml
[project.dependencies]
pyyaml = ">=6.0"
jinja2 = ">=3.0"  # 新增

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "ruff>=0.4.0",
]
```

---

## 十一、测试策略

| 模块 | 测试重点 |
|---|---|
| `engine/renderer.py` | Jinja2 模板渲染正确性、条件分支、循环展开 |
| `engine/validator.py` | 静态校验覆盖率、运行时校验边界情况 |
| `engine/cache.py` | 依赖图计算正确性、缓存命中/失效逻辑 |
| `engine/workflow.py` | 工作流解析、拓扑排序、环检测 |
| `engine/planner.py` | 构建计划生成逻辑 |
| `cli/` | 命令行参数解析、输出格式 |

---

## 十二、向后兼容性

1. **现有 Skill 不需要改动** — Jinja2 兼容现有 `{{key}}` 语法
2. **scripts/build.py 保留** — 作为兼容入口，内部调用 cli/build.py
3. **builder/ 目录保留** — 作为兼容入口，内部调用 engine/
4. **现有 tests 不变** — 只新增 test_engine/ 和 test_cli/

---

## 十三、风险与应对

| 风险 | 应对策略 |
|---|---|
| Jinja2 性能问题 | 模板编译缓存，预热常用模板 |
| 依赖图计算复杂 | 使用 DAG 算法，限制依赖深度 |
| 工作流环检测遗漏 | 拓扑排序前强制校验，拒绝执行 |
| 迁移过程中 CI 失败 | 分阶段提交，每阶段独立验证 |

---

## 十四、验收标准

1. **工作流执行成功** — 能运行 literature-review.yaml 并输出正确结果
2. **Jinja2 模板渲染** — 支持 `{% if %}` 和 `{% for %}`，无残留占位符
3. **双重校验生效** — 错误的 Skill 能被静态校验拦截，渲染失败能被运行时校验发现
4. **缓存命中** — 第二次构建相同 Skill 能跳过（输出 "SKIP"）
5. **所有测试通过** — pytest 覆盖率 > 80%