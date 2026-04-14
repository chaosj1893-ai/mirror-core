from datetime import datetime

from mirror_core.models import (
    FacultyData,
    Memory,
    PersonaVersion,
    ReasoningTrace,
    Response,
    SoulData,
    VersionDiff,
)


def test_soul_data_creation():
    soul = SoulData(
        version="1.0",
        created_at=datetime(2026, 4, 14),
        updated_at=datetime(2026, 4, 14),
        identity={"role": "AI产品经理"},
        values=["用户第一"],
        language_style={"tone": "简洁直接"},
        decision_patterns=["MVP优先"],
    )
    assert soul.version == "1.0"
    assert soul.identity["role"] == "AI产品经理"


def test_faculty_data_creation():
    faculty = FacultyData(
        domain="product",
        version="1.0",
        last_updated=datetime(2026, 4, 14),
        frameworks={"需求分析": "用户场景→痛点→方案→验证"},
        case_refs=["body/cases/wonderai.md"],
    )
    assert faculty.domain == "product"
    assert len(faculty.case_refs) == 1


def test_memory_creation():
    mem = Memory(
        content="WonderAI V6.0 积分制改造",
        type="case",
        domain="product",
        timestamp=datetime(2026, 4, 7),
        version="v1.0",
        tags=["付费转化", "积分体系"],
        confidence=0.95,
        source="obsidian/wonderai.md",
    )
    assert mem.confidence == 0.95
    assert "积分体系" in mem.tags


def test_persona_version_creation():
    pv = PersonaVersion(
        version="1.0",
        timestamp=datetime(2026, 4, 14),
        soul_snapshot="# Soul v1.0\n...",
        faculty_diff={"product": "added RICE model"},
        body_additions=["wonderai case"],
        changelog="初始版本创建",
    )
    assert pv.changelog == "初始版本创建"


def test_version_diff():
    diff = VersionDiff(
        v1="1.0",
        v2="2.0",
        soul_changes=["价值观新增: 数据驱动"],
        faculty_changes={"product": ["新增RICE模型"]},
        body_changes_count=3,
        summary="新增产品方法论，价值观更新",
    )
    assert diff.body_changes_count == 3


def test_reasoning_trace():
    trace = ReasoningTrace(
        intent="product_advice",
        activated_layers=["soul", "faculty_product", "body"],
        thinking_process=["识别到功能优先级问题", "调用RICE模型"],
        sources=[
            {
                "type": "faculty",
                "content": "RICE模型",
                "confidence": 0.95,
            }
        ],
        confidence_level="high",
        speculation_parts=[],
    )
    assert trace.confidence_level == "high"
    assert len(trace.sources) == 1


def test_response_creation():
    trace = ReasoningTrace(
        intent="product_advice",
        activated_layers=["soul"],
        thinking_process=["test"],
        sources=[],
        confidence_level="medium",
        speculation_parts=[],
    )
    resp = Response(
        content="建议先做MVP验证",
        reasoning=trace,
    )
    assert resp.content == "建议先做MVP验证"
    assert resp.reasoning.intent == "product_advice"
