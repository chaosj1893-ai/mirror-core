"""CLI entry points for MirrorCore."""

import os
from pathlib import Path

import click

from mirror_core.body import BodyManager
from mirror_core.distill import DistillEngine
from mirror_core.export import ExportManager
from mirror_core.faculty import FacultyManager
from mirror_core.glassbox import GlassBoxEngine
from mirror_core.llm import LLMClient
from mirror_core.orchestrator import Orchestrator
from mirror_core.soul import SoulManager
from mirror_core.timeline import TimelineManager

DEFAULT_DATA_DIR = Path.cwd() / "data"
DEFAULT_TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"


def _get_data_dir(ctx: click.Context) -> Path:
    return Path(ctx.obj.get("data_dir", DEFAULT_DATA_DIR))


@click.group()
@click.option(
    "--data-dir",
    default=str(DEFAULT_DATA_DIR),
    help="Data directory path",
)
@click.pass_context
def main(ctx: click.Context, data_dir: str) -> None:
    """MirrorCore - 可成长、可解释的个人数字分身系统"""
    ctx.ensure_object(dict)
    ctx.obj["data_dir"] = data_dir


@main.command()
@click.option("--round", "round_id", type=int, default=None, help="Run a specific round (1-6)")
@click.pass_context
def distill(ctx: click.Context, round_id: int | None) -> None:
    """启动交互式蒸馏流程，创建你的数字分身"""
    data_dir = _get_data_dir(ctx)
    templates_dir = DEFAULT_TEMPLATES_DIR

    engine = DistillEngine(data_dir=data_dir, templates_dir=templates_dir)

    if round_id:
        rounds_to_run = [round_id]
    else:
        rounds_to_run = list(range(1, engine.get_total_rounds() + 1))

    click.echo(f"开始蒸馏流程，共 {len(rounds_to_run)} 轮\n")

    for rid in rounds_to_run:
        round_def = engine.get_round(rid)
        if not round_def:
            click.echo(f"轮次 {rid} 不存在，跳过")
            continue

        click.echo(f"\n{'='*50}")
        click.echo(f"第 {rid} 轮：{round_def['name']}（约{round_def['duration_minutes']}分钟）")
        click.echo(f"{'='*50}\n")

        answers = {}
        for q in round_def["questions"]:
            click.echo(f"\n{q['id']}. {q['text']}\n")
            answer = click.prompt("你的回答", default="", show_default=False)
            answers[q["id"]] = answer

        result = engine.process_round_answers(round_id=rid, answers=answers)
        click.echo(f"\n第 {rid} 轮完成，数据目标: {result['target']}")

    click.echo("\n蒸馏流程完成！")


@main.command()
@click.pass_context
def chat(ctx: click.Context) -> None:
    """与你的数字分身对话"""
    data_dir = _get_data_dir(ctx)

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        click.echo("错误：请设置 ANTHROPIC_API_KEY 环境变量")
        return

    orch = Orchestrator(
        soul=SoulManager(data_dir=data_dir),
        faculty=FacultyManager(data_dir=data_dir),
        body=BodyManager(data_dir=data_dir),
        timeline=TimelineManager(data_dir=data_dir),
        glassbox=GlassBoxEngine(data_dir=data_dir),
        llm=LLMClient(api_key=api_key),
    )

    click.echo("数字分身已就绪，输入问题开始对话（输入 quit 退出，输入 why 查看上次推理过程）\n")

    last_response = None
    while True:
        query = click.prompt("你", prompt_suffix="> ")
        if query.lower() in ("quit", "exit", "q"):
            click.echo("再见！")
            break

        if query.lower() == "why" and last_response:
            _print_reasoning(last_response)
            continue

        resp = orch.process_query(query)
        last_response = resp

        click.echo(f"\n分身> {resp.content}")
        click.echo(f"  [置信度: {resp.reasoning.confidence_level}]\n")


@main.command()
@click.pass_context
def sync(ctx: click.Context) -> None:
    """同步更新你的数字分身（增量更新）"""
    click.echo("同步更新功能 — 回答以下反思问题来更新你的分身\n")

    questions = [
        "过去这段时间，你的核心价值观有变化吗？如果有，是什么？",
        "你学到了什么新的方法论或框架？",
        "你最近做了什么重要的决策？过程是怎样的？",
        "你的沟通风格有变化吗？",
        "有什么新的项目经验值得记录？",
    ]

    answers = {}
    for i, q in enumerate(questions, 1):
        click.echo(f"\n{i}. {q}\n")
        answer = click.prompt("回答", default="跳过", show_default=False)
        if answer != "跳过":
            answers[str(i)] = answer

    if answers:
        click.echo(f"\n收到 {len(answers)} 条更新，同步完成。")
    else:
        click.echo("\n无更新内容。")


@main.command()
@click.pass_context
def versions(ctx: click.Context) -> None:
    """查看分身版本历史"""
    data_dir = _get_data_dir(ctx)
    timeline = TimelineManager(data_dir=data_dir)

    version_list = timeline.list_versions()
    if not version_list:
        click.echo("暂无版本记录")
        return

    click.echo(f"共 {len(version_list)} 个版本:\n")
    for pv in version_list:
        click.echo(f"  v{pv.version}  {pv.timestamp.strftime('%Y-%m-%d %H:%M')}  {pv.changelog}")


def _print_reasoning(resp) -> None:
    """Print the reasoning trace for the last response."""
    r = resp.reasoning
    click.echo("\n--- 推理过程 ---")
    click.echo(f"意图: {r.intent}")
    click.echo(f"激活层: {', '.join(r.activated_layers)}")
    click.echo(f"置信度: {r.confidence_level}")
    click.echo("\n思考过程:")
    for step in r.thinking_process:
        click.echo(f"  - {step}")
    if r.sources:
        click.echo("\n引用来源:")
        for s in r.sources:
            click.echo(f"  [{s['type']}] {s['content'][:100]}... (置信度: {s['confidence']})")
    if r.speculation_parts:
        click.echo("\n推测部分:")
        for sp in r.speculation_parts:
            click.echo(f"  ⚠ {sp}")
    click.echo("--- 推理结束 ---\n")


@main.command(name="export")
@click.option("--name", required=True, help="分身名称，如 jc")
@click.option("--output", default=None, help="输出目录，默认 ~/{name}-persona")
@click.option("--include-knowledge", is_flag=True, help="是否包含知识库（Body层）")
@click.pass_context
def export_cmd(ctx: click.Context, name: str, output: str | None, include_knowledge: bool) -> None:
    """导出分身为独立 Git 仓库，可分享给别人"""
    data_dir = _get_data_dir(ctx)
    output_dir = Path(output) if output else Path.home() / f"{name}-persona"

    mgr = ExportManager()
    click.echo(f"正在导出 {name} 的分身到 {output_dir}...\n")

    mgr.export(
        data_dir=data_dir,
        output_dir=output_dir,
        name=name,
        include_knowledge=include_knowledge,
    )

    git_ok = mgr.init_git(output_dir, name)
    if git_ok:
        click.echo(f"Git 仓库已初始化并提交\n")
    else:
        click.echo(f"Git 初始化跳过（可手动执行 git init）\n")

    click.echo(f"导出完成！目录：{output_dir}")
    click.echo(f"\n推送到 GitHub：")
    click.echo(f"  cd {output_dir}")
    click.echo(f"  gh repo create {name}-persona --public --source . --push")


@main.command()
@click.argument("file_path")
@click.pass_context
def review(ctx: click.Context, file_path: str) -> None:
    """用分身的视角审视文档"""
    data_dir = _get_data_dir(ctx)

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        click.echo("错误：CLI review 需要 ANTHROPIC_API_KEY（在 Claude Code 中使用 /mirror-core review 无需此设置）")
        return

    from mirror_core.review import ReviewEngine

    engine = ReviewEngine(
        soul=SoulManager(data_dir=data_dir),
        faculty=FacultyManager(data_dir=data_dir),
        llm=LLMClient(api_key=api_key),
    )

    target = Path(file_path)
    if not target.exists():
        click.echo(f"错误：文件 {file_path} 不存在")
        return

    click.echo(f"正在用分身视角审视 {target.name}...\n")
    result = engine.review_file(target)
    click.echo(result)


@main.command()
@click.argument("persona1_dir")
@click.argument("persona2_dir")
@click.argument("topic")
@click.option("--rounds", default=3, help="辩论轮数")
@click.pass_context
def debate(ctx: click.Context, persona1_dir: str, persona2_dir: str, topic: str, rounds: int) -> None:
    """让两个分身就某个话题辩论"""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        click.echo("错误：CLI debate 需要 ANTHROPIC_API_KEY（在 Claude Code 中使用 /mirror-core debate 无需此设置）")
        return

    from mirror_core.debate import DebateEngine

    engine = DebateEngine(llm=LLMClient(api_key=api_key))

    click.echo(f"辩题：{topic}")
    click.echo(f"分身 A：{persona1_dir}")
    click.echo(f"分身 B：{persona2_dir}")
    click.echo(f"轮数：{rounds}\n")

    result = engine.run_debate(
        persona1_dir=Path(persona1_dir),
        persona2_dir=Path(persona2_dir),
        topic=topic,
        rounds=rounds,
    )

    for r in result.rounds:
        click.echo(f"\n{'='*50}")
        click.echo(f"[{r['persona']}]")
        click.echo(f"{'='*50}")
        click.echo(r["position"])

    click.echo(f"\n{'='*50}")
    click.echo("总结")
    click.echo(f"{'='*50}")
    click.echo(result.summary)
    if result.consensus:
        click.echo(f"\n共识：")
        for c in result.consensus:
            click.echo(f"  - {c}")
    if result.disagreements:
        click.echo(f"\n分歧：")
        for d in result.disagreements:
            click.echo(f"  - {d}")
