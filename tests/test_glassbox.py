import json
from datetime import datetime

from mirror_core.glassbox import GlassBoxEngine
from mirror_core.models import Memory, ReasoningTrace


def test_glassbox_init(tmp_data_dir):
    engine = GlassBoxEngine(data_dir=tmp_data_dir)
    assert engine.feedback_file.exists()


def test_trace_reasoning():
    memories = [
        Memory(
            content="WonderAI 用积分制提升付费转化",
            type="case",
            domain="product",
            timestamp=datetime(2026, 4, 7),
            version="v1.0",
            tags=["付费转化"],
            confidence=0.95,
            source="obsidian/wonderai.md",
        ),
    ]

    engine = GlassBoxEngine.__new__(GlassBoxEngine)
    engine.feedback_log = []

    trace = engine.trace(
        intent="product_advice",
        activated_layers=["soul", "faculty_product", "body"],
        memories_used=memories,
        response_text="建议用积分制",
    )

    assert isinstance(trace, ReasoningTrace)
    assert trace.intent == "product_advice"
    assert len(trace.sources) == 1
    assert trace.sources[0]["confidence"] == 0.95
    assert trace.confidence_level == "high"


def test_trace_low_confidence():
    engine = GlassBoxEngine.__new__(GlassBoxEngine)
    engine.feedback_log = []

    trace = engine.trace(
        intent="product_advice",
        activated_layers=["soul"],
        memories_used=[],
        response_text="我猜可以这样做",
    )

    assert trace.confidence_level == "low"


def test_record_feedback(tmp_data_dir):
    engine = GlassBoxEngine(data_dir=tmp_data_dir)

    engine.record_feedback(
        query="怎么做功能优先级",
        response="用RICE模型",
        feedback_type="accurate",
        correction=None,
    )

    log = engine.get_feedback_log()
    assert len(log) == 1
    assert log[0]["feedback_type"] == "accurate"


def test_record_feedback_not_me(tmp_data_dir):
    engine = GlassBoxEngine(data_dir=tmp_data_dir)

    engine.record_feedback(
        query="怎么做功能优先级",
        response="用RICE模型",
        feedback_type="not_me",
        correction="我更倾向用ICE模型",
    )

    log = engine.get_feedback_log()
    assert len(log) == 1
    assert log[0]["correction"] == "我更倾向用ICE模型"


def test_get_negative_feedback_count(tmp_data_dir):
    engine = GlassBoxEngine(data_dir=tmp_data_dir)
    engine.record_feedback("q1", "r1", "accurate", None)
    engine.record_feedback("q2", "r2", "not_me", "wrong")
    engine.record_feedback("q3", "r3", "partially", "half right")

    assert engine.get_negative_feedback_count() == 2
