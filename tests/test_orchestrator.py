from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

from mirror_core.models import Memory, ReasoningTrace, Response
from mirror_core.orchestrator import Orchestrator


def _make_test_orchestrator(tmp_data_dir: Path) -> Orchestrator:
    """Build an Orchestrator with real Soul/Faculty/Body/Timeline/GlassBox managers."""
    from mirror_core.body import BodyManager
    from mirror_core.faculty import FacultyManager
    from mirror_core.glassbox import GlassBoxEngine
    from mirror_core.soul import SoulManager
    from mirror_core.timeline import TimelineManager

    soul_mgr = SoulManager(data_dir=tmp_data_dir)
    soul_mgr.save(
        version="1.0",
        identity={"role": "AI产品经理"},
        values=["用户第一", "快速迭代"],
        language_style={"tone": "简洁直接", "口头禅": "说白了"},
        decision_patterns=["MVP优先"],
    )

    faculty_mgr = FacultyManager(data_dir=tmp_data_dir)
    faculty_mgr.save(
        domain="product",
        version="1.0",
        frameworks={"需求分析": "用户→痛点→方案→验证", "优先级": "RICE模型"},
        case_refs=[],
    )

    body_mgr = BodyManager(data_dir=tmp_data_dir)
    body_mgr.ingest(
        content="WonderAI V6.0 从功能墙改为积分消耗制",
        type="case",
        domain="product",
        tags=["积分体系"],
        confidence=0.95,
        source="wonderai.md",
        version="v1.0",
    )

    timeline_mgr = TimelineManager(data_dir=tmp_data_dir)
    glassbox = GlassBoxEngine(data_dir=tmp_data_dir)

    mock_llm = MagicMock()
    mock_llm.generate.return_value = "建议先用RICE模型评估优先级，然后做MVP验证。"

    return Orchestrator(
        soul=soul_mgr,
        faculty=faculty_mgr,
        body=body_mgr,
        timeline=timeline_mgr,
        glassbox=glassbox,
        llm=mock_llm,
    )


def test_orchestrator_init(tmp_data_dir):
    orch = _make_test_orchestrator(tmp_data_dir)
    assert orch is not None


def test_classify_intent():
    assert Orchestrator.classify_intent("对比我v1和v2的变化") == "version_compare"
    assert Orchestrator.classify_intent("这个功能该怎么做") == "product_advice"
    assert Orchestrator.classify_intent("回顾一下我的决策逻辑") == "self_reflection"
    assert Orchestrator.classify_intent("什么是RICE模型") == "knowledge_query"


def test_process_query(tmp_data_dir):
    orch = _make_test_orchestrator(tmp_data_dir)

    resp = orch.process_query("这个功能该怎么排优先级？")

    assert isinstance(resp, Response)
    assert resp.content != ""
    assert resp.reasoning.intent in (
        "product_advice",
        "knowledge_query",
        "self_reflection",
        "version_compare",
    )
    assert len(resp.reasoning.activated_layers) >= 1


def test_build_prompt(tmp_data_dir):
    orch = _make_test_orchestrator(tmp_data_dir)

    memories = [
        Memory(
            content="WonderAI case",
            type="case",
            domain="product",
            timestamp=datetime(2026, 4, 7),
            version="v1.0",
            tags=["test"],
            confidence=0.9,
            source="test.md",
        )
    ]

    system_prompt, user_msg = orch.build_prompt(
        intent="product_advice",
        domain="product",
        memories=memories,
        user_query="怎么排优先级？",
    )

    assert "身份认同" in system_prompt or "产品" in system_prompt
    assert "怎么排优先级" in user_msg
