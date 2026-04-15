import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from mirror_core.distill import DistillEngine


TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def test_distill_engine_init(tmp_data_dir):
    engine = DistillEngine(data_dir=tmp_data_dir, templates_dir=TEMPLATES_DIR)
    assert engine.questionnaire is not None
    assert len(engine.questionnaire["rounds"]) == 6


def test_get_round_questions(tmp_data_dir):
    engine = DistillEngine(data_dir=tmp_data_dir, templates_dir=TEMPLATES_DIR)

    round_1 = engine.get_round(1)
    assert round_1["name"] == "身份画像"
    assert len(round_1["questions"]) == 5


def test_get_round_invalid(tmp_data_dir):
    engine = DistillEngine(data_dir=tmp_data_dir, templates_dir=TEMPLATES_DIR)
    assert engine.get_round(99) is None


def test_process_soul_answers(tmp_data_dir):
    engine = DistillEngine(data_dir=tmp_data_dir, templates_dir=TEMPLATES_DIR)

    answers = {
        "1.1": "AI产品经理，做了3年",
        "1.2": "技术背景转产品",
        "1.3": "创业中",
        "1.4": "产品设计、数据分析、AI应用",
        "1.5": "短期：做好WonderAI；中期：成为AI产品专家",
    }

    result = engine.process_round_answers(round_id=1, answers=answers)
    assert result["target"] == "soul"
    assert "AI产品经理" in result["raw_text"]


def test_process_faculty_answers(tmp_data_dir):
    engine = DistillEngine(data_dir=tmp_data_dir, templates_dir=TEMPLATES_DIR)

    answers = {
        "4.1": "用户场景→痛点→方案→验证",
        "4.2": "RICE模型",
        "4.3": "WonderAI V6.0 积分制改造，提升了付费转化",
        "4.4": "B端初版审核太松，学到了要做好风控",
        "4.5": "Figma、飞书文档、数据分析",
        "4.6": "用户第一、数据驱动、快速验证",
    }

    result = engine.process_round_answers(round_id=4, answers=answers)
    assert result["target"] == "faculty"
    assert "RICE" in result["raw_text"]


def test_get_total_rounds(tmp_data_dir):
    engine = DistillEngine(data_dir=tmp_data_dir, templates_dir=TEMPLATES_DIR)
    assert engine.get_total_rounds() == 6
