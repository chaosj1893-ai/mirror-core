"""End-to-end integration test: distill -> chat -> feedback -> version."""

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

from mirror_core.body import BodyManager
from mirror_core.distill import DistillEngine
from mirror_core.faculty import FacultyManager
from mirror_core.glassbox import GlassBoxEngine
from mirror_core.orchestrator import Orchestrator
from mirror_core.soul import SoulManager
from mirror_core.timeline import TimelineManager


TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def test_full_pipeline(tmp_data_dir):
    """Test the complete flow: distill -> save -> chat -> feedback -> version."""

    # === Phase 1: Distill ===
    engine = DistillEngine(data_dir=tmp_data_dir, templates_dir=TEMPLATES_DIR)

    r1 = engine.process_round_answers(1, {
        "1.1": "AI产品经理，3年",
        "1.2": "技术转产品",
        "1.3": "创业中",
        "1.4": "产品设计、数据分析、AI",
        "1.5": "做好WonderAI",
    })
    assert r1["target"] == "soul"

    r4 = engine.process_round_answers(4, {
        "4.1": "用户→痛点→方案→验证",
        "4.2": "RICE模型",
        "4.3": "WonderAI积分制改造",
        "4.4": "B端审核太松",
        "4.5": "Figma、飞书、数据分析",
        "4.6": "用户第一、数据驱动、快速验证",
    })
    assert r4["target"] == "faculty"

    # === Phase 2: Save to layers ===
    soul_mgr = SoulManager(data_dir=tmp_data_dir)
    soul_mgr.save(
        version="1.0",
        identity={"role": "AI产品经理", "background": "技术转产品"},
        values=["用户第一", "快速迭代"],
        language_style={"tone": "简洁直接"},
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
        content="WonderAI V6.0 从功能墙改为积分消耗制，付费转化率提升",
        type="case",
        domain="product",
        tags=["积分体系", "付费转化"],
        confidence=0.95,
        source="wonderai.md",
        version="v1.0",
    )

    timeline_mgr = TimelineManager(data_dir=tmp_data_dir)
    timeline_mgr.create_version(
        version="1.0",
        soul_snapshot=soul_mgr.get_raw_content(),
        faculty_diff={"product": "初始创建"},
        body_additions=["wonderai case"],
        changelog="初始版本",
    )

    # === Phase 3: Chat ===
    glassbox = GlassBoxEngine(data_dir=tmp_data_dir)

    mock_llm = MagicMock()
    mock_llm.generate.return_value = "说白了，核心是用RICE模型排优先级，先做用户呼声最高的小优化。"

    orch = Orchestrator(
        soul=soul_mgr,
        faculty=faculty_mgr,
        body=body_mgr,
        timeline=timeline_mgr,
        glassbox=glassbox,
        llm=mock_llm,
    )

    resp = orch.process_query("这三个功能该怎么排优先级？")

    assert "RICE" in resp.content
    assert resp.reasoning.confidence_level in ("high", "medium", "low")
    assert len(resp.reasoning.activated_layers) >= 1

    # === Phase 4: Feedback ===
    glassbox.record_feedback(
        query="这三个功能该怎么排优先级？",
        response=resp.content,
        feedback_type="accurate",
        correction=None,
    )
    assert len(glassbox.get_feedback_log()) == 1

    # === Phase 5: Version update ===
    timeline_mgr.create_version(
        version="1.1",
        soul_snapshot=soul_mgr.get_raw_content(),
        faculty_diff={},
        body_additions=[],
        changelog="校准反馈后更新",
    )

    assert timeline_mgr.get_current_version() == "1.1"
    assert len(timeline_mgr.list_versions()) == 2

    diff = timeline_mgr.compare("1.0", "1.1")
    assert diff.v1 == "1.0"
    assert diff.v2 == "1.1"
