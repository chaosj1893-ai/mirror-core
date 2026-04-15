from pathlib import Path

from mirror_core.export import ExportManager
from mirror_core.faculty import FacultyManager
from mirror_core.soul import SoulManager


def test_export_creates_directory(tmp_data_dir, tmp_path):
    _seed_data(tmp_data_dir)
    mgr = ExportManager()
    output = tmp_path / "jc-persona"
    mgr.export(data_dir=tmp_data_dir, output_dir=output, name="jc")

    assert output.exists()
    assert (output / "soul" / "soul.md").exists()
    assert (output / "faculty" / "product.md").exists()
    assert (output / "timeline").exists()
    assert (output / "README.md").exists()
    assert (output / "INSTALL.md").exists()


def test_export_excludes_body_by_default(tmp_data_dir, tmp_path):
    _seed_data(tmp_data_dir)
    mgr = ExportManager()
    output = tmp_path / "jc-persona"
    mgr.export(data_dir=tmp_data_dir, output_dir=output, name="jc")

    assert not (output / "body").exists()


def test_export_includes_body_when_flag_set(tmp_data_dir, tmp_path):
    _seed_data(tmp_data_dir)
    # Create a dummy body file
    body_dir = tmp_data_dir / "body"
    body_dir.mkdir(parents=True, exist_ok=True)
    (body_dir / "test.txt").write_text("knowledge data")

    mgr = ExportManager()
    output = tmp_path / "jc-persona"
    mgr.export(data_dir=tmp_data_dir, output_dir=output, name="jc", include_knowledge=True)

    assert (output / "body" / "test.txt").exists()


def test_generate_readme_includes_personality_tags(tmp_data_dir):
    _seed_data(tmp_data_dir)
    soul_mgr = SoulManager(data_dir=tmp_data_dir)
    soul_data = soul_mgr.load()

    mgr = ExportManager()
    readme = mgr.generate_readme("jc", soul_data, ["product", "ai"])

    assert "jc" in readme
    assert "INTJ" in readme
    assert "天蝎座" in readme
    assert "product" in readme


def test_generate_readme_without_tags(tmp_data_dir):
    soul_mgr = SoulManager(data_dir=tmp_data_dir)
    soul_mgr.save(
        version="1.0",
        identity={"role": "PM"},
        values=["快速迭代"],
        language_style={"tone": "简洁"},
        decision_patterns=["MVP"],
    )
    soul_data = soul_mgr.load()

    mgr = ExportManager()
    readme = mgr.generate_readme("someone", soul_data, [])

    assert "someone" in readme
    assert "MirrorCore" in readme


def test_init_git(tmp_data_dir, tmp_path):
    _seed_data(tmp_data_dir)
    mgr = ExportManager()
    output = tmp_path / "jc-persona"
    mgr.export(data_dir=tmp_data_dir, output_dir=output, name="jc")
    result = mgr.init_git(output, "jc")

    assert result is True
    assert (output / ".git").exists()


def _seed_data(data_dir: Path):
    """Create sample soul + faculty data for export tests."""
    soul_mgr = SoulManager(data_dir=data_dir)
    soul_mgr.save(
        version="1.0",
        identity={"role": "AI产品经理", "background": "技术转产品"},
        values=["用户第一", "快速迭代"],
        language_style={"tone": "简洁直接"},
        decision_patterns=["MVP优先"],
        personality_tags={"MBTI": "INTJ", "星座": "天蝎座", "核心特质": "理性"},
    )

    faculty_mgr = FacultyManager(data_dir=data_dir)
    faculty_mgr.save(
        domain="product",
        version="1.0",
        frameworks={"需求分析": "用户→痛点→方案"},
        case_refs=[],
    )

    # Create timeline
    timeline_dir = data_dir / "timeline"
    timeline_dir.mkdir(parents=True, exist_ok=True)
    (timeline_dir / "versions.json").write_text("[]", encoding="utf-8")
