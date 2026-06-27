# sci-craft vs nature-skills 对比分析

## 核心差异

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

## 功能覆盖

### nature-skills 现有功能
- nature-figure（稳定）
- nature-polishing（稳定）
- nature-writing
- nature-citation
- nature-reviewer
- nature-response
- nature-reader
- nature-paper2ppt
- nature-data

### sci-craft 新增/增强功能
- sci-figure（Nature + Science 双配色）
- sci-framework（**框架图绘制** — nature-skills 最大短板）
- sci-polishing（12步工作流）
- sci-writing（分节写作指南）
- sci-citation（引文格式自动适配）
- sci-reviewer（3份独立报告）
- sci-response（逐条回复信）
- sci-reader（双语阅读）
- sci-paper2ppt（PPT生成）
- sci-data（数据声明）
- 文献研究系列（6个Skill）

## 技术架构差异

### nature-skills
- 扁平结构，每个 Skill 独立
- 无构建层，无适配层
- 无自动化测试
- 期刊规范硬编码

### sci-craft
- 四层分层架构
  - 核心层：期刊配置 + 规则库
  - Skill 层：功能模块
  - 构建层：组装 + 校验
  - 适配层：多平台转换
- 自动化测试 + CI
- YAML 配置驱动，可扩展

## 总结

sci-craft 在以下方面优于 nature-skills：
1. **框架图绘制** — 填补 nature-skills 最大空白
2. **多期刊支持** — Nature + Science 一键切换
3. **多平台兼容** — TRAE / Codex / Claude Code 一次编写
4. **质量保障** — validator 校验 + 自动化测试
5. **中文支持** — 专门的中文学术写作规则
6. **文献研究** — 6个额外 Skill 覆盖完整研究流程
