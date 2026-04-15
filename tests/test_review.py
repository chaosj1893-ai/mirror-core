from pathlib import Path
from unittest.mock import MagicMock

from mirror_core.faculty import FacultyManager
from mirror_core.review import ReviewEngine
from mirror_core.soul import SoulManager


def test_review_text(tmp_data_dir):
    soul_mgr = SoulManager(data_dir=tmp_data_dir)
    soul_mgr.save(
        version="1.0",
        identity={"role": "PM"},
        values=["用户第一"],
        language_style={"tone": "简洁"},
        decision_patterns=["MVP优先"],
    )

    faculty_mgr = FacultyManager(data_dir=tmp_data_dir)
    faculty_mgr.save(domain="product", version="1.0", frameworks={"需求分析": "框架"}, case_refs=[])

    mock_llm = MagicMock()
    mock_llm.generate.return_value = "这份文档缺少数据支撑，建议加上用户调研结果。"

    engine = ReviewEngine(soul=soul_mgr, faculty=faculty_mgr, llm=mock_llm)
    result = engine.review_text("这是一份产品需求文档...")

    assert "数据支撑" in result
    mock_llm.generate.assert_called_once()
    call_kwargs = mock_llm.generate.call_args[1]
    assert "审视" in call_kwargs["system_prompt"]
    assert "产品需求文档" in call_kwargs["user_message"]


def test_review_file(tmp_data_dir, tmp_path):
    soul_mgr = SoulManager(data_dir=tmp_data_dir)
    soul_mgr.save(
        version="1.0",
        identity={"role": "PM"},
        values=["用户第一"],
        language_style={"tone": "简洁"},
        decision_patterns=["MVP优先"],
    )

    faculty_mgr = FacultyManager(data_dir=tmp_data_dir)

    mock_llm = MagicMock()
    mock_llm.generate.return_value = "审视结果"

    engine = ReviewEngine(soul=soul_mgr, faculty=faculty_mgr, llm=mock_llm)

    test_file = tmp_path / "spec.md"
    test_file.write_text("# 产品规格\n功能A：...")

    result = engine.review_file(test_file)
    assert result == "审视结果"


def test_build_review_prompt(tmp_data_dir):
    soul_mgr = SoulManager(data_dir=tmp_data_dir)
    soul_mgr.save(
        version="1.0",
        identity={"role": "PM"},
        values=["用户第一"],
        language_style={"tone": "简洁"},
        decision_patterns=["MVP优先"],
    )

    faculty_mgr = FacultyManager(data_dir=tmp_data_dir)
    faculty_mgr.save(domain="product", version="1.0", frameworks={"a": "b"}, case_refs=[])

    mock_llm = MagicMock()
    engine = ReviewEngine(soul=soul_mgr, faculty=faculty_mgr, llm=mock_llm)

    system_prompt, user_msg = engine.build_review_prompt("测试内容", "test.md")
    assert "人格核心" in system_prompt
    assert "test.md" in user_msg
