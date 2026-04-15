# MirrorCore

> 可成长、可解释的个人数字分身系统 — A Growable, Explainable Personal Digital Persona

基于 OpenPersona 四层架构（Soul / Faculty / Body / Skill），通过交互式蒸馏复刻你的专业能力和人格特征。

## 核心差异化

| 特性 | 同事.skill 等 | MirrorCore |
|------|-------------|------------|
| 人格模型 | 静态快照 | **可成长**（TimeLine 版本管理） |
| 回答透明度 | 黑盒 | **可解释**（GlassBox 推理链路） |
| 数据采集 | 依赖平台数据导出 | **交互式蒸馏**（6 轮结构化问答） |
| 扩展性 | 单体 skill | **四层架构**，可独立升级 |

## 快速开始

### 方式 1：作为 Claude Code Skill 使用（推荐，无需 API Key）

```bash
# 克隆项目
git clone https://github.com/YOUR_USERNAME/mirror-core.git ~/mirror-core

# 安装 skill
mkdir -p ~/.claude/skills/mirror-core
cp ~/mirror-core/skill/mirror-core.skill ~/.claude/skills/mirror-core/SKILL.md
```

重启 Claude Code 后，输入 `/mirror-core` 即可使用：

```
/mirror-core distill      # 启动蒸馏，创建你的数字分身
/mirror-core chat         # 与分身对话
/mirror-core sync         # 同步更新分身
/mirror-core versions     # 查看版本历史
```

### 方式 2：作为独立 CLI 使用（需要 API Key）

```bash
cd mirror-core
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
export ANTHROPIC_API_KEY=your_key_here

# 启动蒸馏
python -m mirror_core.cli distill

# 与分身对话
python -m mirror_core.cli chat
```

## 架构

```
┌─────────────────────────────────────────────┐
│              用户交互层                       │
│   Claude Code Skill / CLI                    │
├─────────────────────────────────────────────┤
│              编排层 (Orchestrator)            │
│   意图识别 → 情境路由 → 响应组装 → 溯源标注   │
├──────┬──────┬──────┬──────┬─────────────────┤
│ Soul │ Fac- │ Body │ Skill│  创新模块        │
│ 人格 │ ulty │ 知识 │ 工具 │                  │
│ 核心 │ 专业 │  库  │  层  │  TimeLine       │
│      │ 能力 │      │      │  GlassBox       │
├──────┴──────┴──────┴──────┴─────────────────┤
│              数据采集层                       │
│   交互式蒸馏引擎（6 轮问答）                  │
└─────────────────────────────────────────────┘
```

### 四层结构

- **Soul**（人格核心）：身份认同、价值观、语言风格、决策模式
- **Faculty**（专业能力）：按领域分类的方法论和思维框架
- **Body**（知识库）：向量数据库存储的项目案例和知识切片
- **Skill**（工具层）：记忆搜索、版本对比、推理解释

### 创新模块

- **TimeLine**：分身可随你成长而演进，支持版本管理、对比、回溯
- **GlassBox**：每次回答展示推理链路、知识溯源和置信度

## 蒸馏流程

6 轮交互式问答，约 2 小时：

1. **身份画像**（15 分钟）— 职业角色、背景、技能
2. **价值观与决策模式**（20 分钟）— 通过场景题提取
3. **语言风格**（15 分钟）— 口头禅、表达偏好
4. **专业方法论**（30 分钟）— 框架、案例、原则
5. **知识库导入**（10 分钟）— Obsidian/文档导入
6. **验证与校准**（20 分钟）— 测试问答 + 反馈调优

## 技术栈

- Python 3.11+
- Claude API (Anthropic SDK)
- Chroma (向量数据库)
- Click (CLI)

## 参考与致谢

- [OpenPersona](https://github.com/acnlabs/OpenPersona) — 四层架构灵感
- [awesome-persona-distill-skills](https://github.com/xixu-me/awesome-persona-distill-skills) — Skill 生态
- [awesome-human-distillation](https://github.com/mliu98/awesome-human-distillation) — 人格蒸馏方法

## License

MIT
