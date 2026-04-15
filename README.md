<div align="center">

# MirrorCore

### 可成长 / 可解释 / 可蒸馏的个人数字分身系统

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Claude](https://img.shields.io/badge/Claude_Code-Skill-cc785c?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyQzYuNDggMiAyIDYuNDggMiAxMnM0LjQ4IDEwIDEwIDEwIDEwLTQuNDggMTAtMTBTMTcuNTIgMiAxMiAyem0wIDE4Yy00LjQxIDAtOC0zLjU5LTgtOHMzLjU5LTggOC04IDggMy41OSA4IDgtMy41OSA4LTggOHoiLz48L3N2Zz4=&logoColor=white)](https://claude.ai)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Chroma](https://img.shields.io/badge/Chroma-RAG-FF6F61?style=for-the-badge)](https://www.trychroma.com/)

**不只是复刻你的知识，更要复刻你的思维方式**

[快速开始](#-快速开始) · [架构设计](#-架构) · [蒸馏流程](#-蒸馏流程) · [使用示例](#-使用示例)

---

<br>

```
   ┌──────────────────────────────────────────────┐
   │  "用我3个月前的思维方式来分析这个问题"         │
   │  "对比我现在和半年前在产品决策上的差异"         │
   │  "为什么你认为应该先做B功能？推理过程是什么？"   │
   └──────────────────────────────────────────────┘
```

</div>

## 为什么需要 MirrorCore？

现有的人格蒸馏工具（同事.skill、前任.skill）都有同一个问题：**蒸馏完就是死的**。

你的分身永远停留在采集那天的状态 —— 但你自己在成长。三个月后你的方法论升级了、价值观微调了、说话方式变了，你的分身还是"旧的你"。

而且，你问分身一个问题，它给你一个回答，但你不知道它**为什么**这么回答。是基于你说过的话？还是瞎编的？

MirrorCore 解决这两个问题：

| 痛点 | 现有方案 | MirrorCore |
|------|---------|------------|
| 分身不会成长 | 一次蒸馏，永久固定 | **TimeLine** — 版本管理 + 增量更新 + 时间旅行 |
| 回答不可解释 | 黑盒输出，不知道为什么 | **GlassBox** — 推理链路 + 知识溯源 + 置信度 |
| 采集门槛高 | 需要导出聊天记录 | **交互式蒸馏** — 6 轮结构化问答，边聊边采 |
| 架构不可扩展 | 单体 prompt 文件 | **四层架构** — Soul/Faculty/Body/Skill 独立迭代 |

## 🚀 快速开始

### 在 Claude Code 中使用（推荐 / 无需 API Key）

```bash
# 1. 克隆
git clone https://github.com/chaosj1893-ai/mirror-core.git ~/mirror-core

# 2. 安装 skill
mkdir -p ~/.claude/skills/mirror-core
cp ~/mirror-core/skill/mirror-core.skill ~/.claude/skills/mirror-core/SKILL.md

# 3. 重启 Claude Code，输入：
/mirror-core distill
```

### 作为独立 CLI 使用

```bash
cd ~/mirror-core
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pip install -e .
export ANTHROPIC_API_KEY=your_key

python -m mirror_core.cli distill    # 蒸馏
python -m mirror_core.cli chat       # 对话
python -m mirror_core.cli sync       # 同步
python -m mirror_core.cli versions   # 版本
```

## 🏗 架构

```
┌──────────────────────────────────────────────────┐
│                 用户交互层                         │
│          Claude Code Skill  /  CLI                │
├──────────────────────────────────────────────────┤
│                 编排层 Orchestrator                │
│      意图识别 → 领域路由 → Prompt 组装 → 溯源标注  │
├────────┬────────┬────────┬────────┬──────────────┤
│  Soul  │Faculty │  Body  │ Skill  │   TimeLine   │
│  人格  │ 专业   │ 知识库 │  工具  │   版本管理    │
│        │ 能力   │  RAG   │        ├──────────────┤
│ 身份   │ 方法论 │ Chroma │ 搜索   │   GlassBox   │
│ 价值观 │ 框架   │ 向量   │ 对比   │   推理透明    │
│ 风格   │ 案例   │ 检索   │ 解释   │   反馈循环    │
│ 决策   │        │        │        │              │
├────────┴────────┴────────┴────────┴──────────────┤
│                 数据采集层                         │
│           交互式蒸馏引擎（6 轮问答）               │
│         + Obsidian / 文档导入（补充）              │
└──────────────────────────────────────────────────┘
```

### 四层解耦

| 层 | 职责 | 存储 | 更新频率 |
|----|------|------|---------|
| **Soul** | 你是谁 — 身份、价值观、语言风格、决策模式 | Markdown | 每 1-3 月 |
| **Faculty** | 你会什么 — 按领域的方法论和思维框架 | Markdown（按领域） | 新项目后 |
| **Body** | 你知道什么 — 项目案例、笔记、对话记录 | Chroma 向量库 | 随时 |
| **Skill** | 你能做什么 — 搜索记忆、对比版本、解释推理 | Python 函数 | 按需 |

### TimeLine — 你的分身会成长

```
v1.0 (2026-04)          v1.1 (2026-05)          v2.0 (2026-07)
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ PM 新手      │───→│ 新增 RICE    │───→│ Senior PM   │
│ 快速迭代     │    │ 数据驱动     │    │ 系统思维     │
│ 简洁风格     │    │ A/B 测试     │    │ 战略视角     │
└─────────────┘    └─────────────┘    └─────────────┘
                                           ↕ 时间旅行
                                     "用 v1.0 的我来分析"
```

### GlassBox — 每次回答都可追溯

```
你：这三个功能该怎么排优先级？

分身：说白了，核心是用 RICE 模型排优先级，先做用户呼声最高的小优化。

─────────────────────────────────────────
🔍 推理链路
   意图: product_advice
   激活层: soul → faculty_product → body
   
📎 引用
   [faculty] RICE 模型：Reach × Impact × Confidence / Effort
   [case] WonderAI V6.0 积分制改造 (置信度: 0.95)
   
✅ 置信度: 高
─────────────────────────────────────────
```

## 🧬 蒸馏流程

6 轮交互式问答，不需要导出任何聊天记录：

| 轮次 | 主题 | 时长 | 产出 |
|------|------|------|------|
| 1 | 身份画像 | 15 分钟 | Soul 层 |
| 2 | 价值观与决策模式 | 20 分钟 | Soul 层 |
| 3 | 语言风格 | 15 分钟 | Soul 层 |
| 4 | 专业方法论 | 30 分钟 | Faculty 层 |
| 5 | 知识库导入 | 10 分钟 | Body 层 |
| 6 | 验证与校准 | 20 分钟 | 全局校准 |

**问题设计示例（第 2 轮）：**

> 团队提出 3 个需求：A. 老板要的大功能（2个月）B. 用户呼声最高的小优化（1周）C. 技术债务修复。你会优先做哪个？为什么？

> 数据显示功能 A 留存更好，但你直觉认为功能 B 更有长期价值。你怎么决策？

通过两难选择和场景模拟，提取的不是"你说了什么"，而是"你怎么想的"。

## 💡 使用示例

### 蒸馏你的分身

```
> /mirror-core distill

第 1 轮：身份画像（约 15 分钟）
==================================================

1.1. 你目前的职业角色是什么？做了多久？

你的回答> AI 产品经理，做了 3 年，之前是后端开发

1.2. 你的专业背景是什么？是否有转行经历？

你的回答> 计算机专业，毕业后做了 2 年 Java 开发，然后转产品
...
```

### 与分身对话

```
> /mirror-core chat

你> 我们的付费转化率一直上不去，你觉得问题出在哪？

分身> 说白了，付费转化的核心不是功能多不多，是用户有没有在关键节点
感受到价值。之前做 WonderAI 的时候也遇到过类似问题，后来从功能墙
改成积分消耗制，让用户先体验再付费，转化率就上来了。

建议你先看一下用户在哪个环节流失最多，然后在那个节点前设计一个
"啊哈时刻"。

───────────────────────────────────
🔍 意图: product_advice | 激活层: soul, faculty_product, body | 置信度: 高
📎 引用: WonderAI V6.0 积分制改造案例
```

### 时间旅行

```
> /mirror-core chat

你> 用我 v1.0 的思维方式来分析这个问题

分身 (v1.0)> 我觉得应该先做 MVP 验证，别想太多直接上...

你> 现在的我会怎么看？

分身 (v2.0)> 现在我会先用 RICE 模型评估一下，同时考虑技术债务
的长期影响。比起直接上 MVP，我更倾向于先做 2 天的数据分析...
```

## 📂 项目结构

```
mirror-core/
├── skill/mirror-core.skill       # Claude Code Skill 定义
├── templates/
│   ├── questionnaire.json        # 6 轮蒸馏问卷
│   ├── soul_template.md          # Soul 层模板
│   └── faculty_template.md       # Faculty 层模板
├── src/mirror_core/
│   ├── models.py                 # 数据模型
│   ├── soul.py                   # Soul 层：人格管理
│   ├── faculty.py                # Faculty 层：专业能力
│   ├── body.py                   # Body 层：向量检索
│   ├── timeline.py               # TimeLine：版本管理
│   ├── glassbox.py               # GlassBox：推理透明
│   ├── distill.py                # 蒸馏引擎
│   ├── orchestrator.py           # 编排层
│   ├── llm.py                    # Claude API 封装
│   └── cli.py                    # CLI 入口
├── tests/                        # 55 个测试，100% 通过
├── data/                         # 运行时数据（gitignored）
│   ├── soul/                     # 人格数据 + 版本快照
│   ├── faculty/                  # 专业能力
│   ├── body/chroma_db/           # 向量数据库
│   ├── timeline/versions.json    # 版本历史
│   └── feedback/                 # 用户反馈
└── pyproject.toml
```

## 🗺 Roadmap

- [x] **Phase 1** — Claude Code Skill + CLI（当前）
- [ ] **Phase 2** — Web UI（Next.js + FastAPI）
- [ ] **Phase 3** — 多模态（语音风格 / 视觉偏好）
- [ ] **Phase 3** — 情境适配（产品顾问 / 技术导师 / 创业伙伴模式切换）
- [ ] **Phase 3** — 协作网络（分身互联 / 数字团队）

## 参考与致谢

- [OpenPersona](https://github.com/acnlabs/OpenPersona) — 四层架构灵感来源
- [awesome-persona-distill-skills](https://github.com/xixu-me/awesome-persona-distill-skills) — Persona Skill 生态
- [awesome-human-distillation](https://github.com/mliu98/awesome-human-distillation) — 人格蒸馏方法论

## License

[MIT](LICENSE) — 自由使用，欢迎 Fork 和 PR
