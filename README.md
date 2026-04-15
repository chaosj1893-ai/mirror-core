# MirrorCore

可成长、可解释的个人数字分身系统。

## 核心特性

- **四层架构**：Soul（人格）/ Faculty（专业能力）/ Body（知识库）/ Skill（工具）
- **TimeLine**：分身可随你成长而演进，支持版本管理和时间旅行
- **GlassBox**：每次回答可溯源，展示推理链路和置信度

## 快速开始

### 安装

```bash
cd mirror-core
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
export ANTHROPIC_API_KEY=your_key_here
```

### 创建你的分身

```bash
source .venv/bin/activate
python -m mirror_core.cli distill
```

按照 6 轮问答完成蒸馏（约 2 小时）。

### 与分身对话

```bash
python -m mirror_core.cli chat
```

输入 `why` 查看推理过程，输入 `quit` 退出。

### 同步更新

```bash
python -m mirror_core.cli sync
```

### 查看版本历史

```bash
python -m mirror_core.cli versions
```

## Claude Code 集成

将 `skill/mirror-core.skill` 复制到你的 Claude Code skills 目录即可使用 `/mirror` 命令。

## 技术栈

- Python 3.11+
- Claude API (Anthropic SDK)
- Chroma (向量数据库)
- Click (CLI)

## License

MIT
