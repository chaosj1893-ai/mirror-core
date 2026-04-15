from pathlib import Path
from unittest.mock import MagicMock, call

from mirror_core.debate import DebateEngine
from mirror_core.faculty import FacultyManager
from mirror_core.models import DebateResult
from mirror_core.soul import SoulManager


def _seed_persona(data_dir: Path, role: str, values: list[str]):
    soul = SoulManager(data_dir=data_dir)
    soul.save(
        version="1.0",
        identity={"role": role},
        values=values,
        language_style={"tone": "简洁"},
        decision_patterns=["数据驱动"],
    )
    faculty = FacultyManager(data_dir=data_dir)
    faculty.save(domain="product", version="1.0", frameworks={"方法": "框架"}, case_refs=[])


def test_run_debate(tmp_path):
    p1_dir = tmp_path / "persona1"
    p2_dir = tmp_path / "persona2"
    for d in [p1_dir, p2_dir]:
        for sub in ["soul/versions", "faculty", "timeline"]:
            (d / sub).mkdir(parents=True)

    _seed_persona(p1_dir, "产品经理", ["用户第一"])
    _seed_persona(p2_dir, "技术负责人", ["技术卓越"])

    mock_llm = MagicMock()
    mock_llm.generate.side_effect = [
        "我认为应该先做用户体验优化",
        "我觉得应该先还技术债",
        "用户体验是核心竞争力",
        "技术债会拖慢所有后续开发",
        "可以折中，先做影响用户的技术债",
        "同意，但要确保有技术债清单",
        "分歧：\n- 优先级排序方法不同\n\n共识：\n- 都认为技术债需要处理\n\n总结：双方都认可问题，但在优先级上有分歧",
    ]

    engine = DebateEngine(llm=mock_llm)
    result = engine.run_debate(
        persona1_dir=p1_dir,
        persona2_dir=p2_dir,
        topic="要不要先还技术债",
        rounds=3,
    )

    assert isinstance(result, DebateResult)
    assert result.topic == "要不要先还技术债"
    assert len(result.rounds) == 6  # 3 rounds × 2 personas
    assert result.rounds[0]["persona"] == "产品经理"
    assert result.rounds[1]["persona"] == "技术负责人"


def test_debate_result_structure(tmp_path):
    p1_dir = tmp_path / "p1"
    p2_dir = tmp_path / "p2"
    for d in [p1_dir, p2_dir]:
        for sub in ["soul/versions", "faculty", "timeline"]:
            (d / sub).mkdir(parents=True)

    _seed_persona(p1_dir, "PM", ["快速迭代"])
    _seed_persona(p2_dir, "CTO", ["稳定性"])

    mock_llm = MagicMock()
    mock_llm.generate.side_effect = [
        "观点A",
        "观点B",
        "分歧：\n- 速度 vs 稳定\n\n共识：\n- 都想做好产品\n\n总结：核心分歧在节奏",
    ]

    engine = DebateEngine(llm=mock_llm)
    result = engine.run_debate(p1_dir, p2_dir, "发布节奏", rounds=1)

    assert len(result.rounds) == 2
    assert "都想做好产品" in result.consensus
    assert "速度 vs 稳定" in result.disagreements
