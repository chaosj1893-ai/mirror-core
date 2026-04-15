from datetime import datetime
from pathlib import Path

from mirror_core.soul import SoulManager


def test_soul_manager_init(tmp_data_dir):
    mgr = SoulManager(data_dir=tmp_data_dir)
    assert mgr.soul_path == tmp_data_dir / "soul" / "soul.md"


def test_save_and_load_soul(tmp_data_dir):
    mgr = SoulManager(data_dir=tmp_data_dir)

    mgr.save(
        version="1.0",
        identity={"role": "AI产品经理", "background": "技术转产品"},
        values=["用户第一", "数据驱动"],
        language_style={"tone": "简洁直接", "口头禅": "说白了"},
        decision_patterns=["MVP优先", "数据验证"],
    )

    soul = mgr.load()
    assert soul.version == "1.0"
    assert soul.identity["role"] == "AI产品经理"
    assert "用户第一" in soul.values
    assert soul.language_style["tone"] == "简洁直接"


def test_save_creates_version_snapshot(tmp_data_dir):
    mgr = SoulManager(data_dir=tmp_data_dir)

    mgr.save(
        version="1.0",
        identity={"role": "PM"},
        values=["快速迭代"],
        language_style={"tone": "简洁"},
        decision_patterns=["MVP"],
    )

    version_file = tmp_data_dir / "soul" / "versions" / "soul_v1.0.md"
    assert version_file.exists()


def test_load_version(tmp_data_dir):
    mgr = SoulManager(data_dir=tmp_data_dir)

    mgr.save(
        version="1.0",
        identity={"role": "PM"},
        values=["快速迭代"],
        language_style={"tone": "简洁"},
        decision_patterns=["MVP"],
    )
    mgr.save(
        version="2.0",
        identity={"role": "Senior PM"},
        values=["快速迭代", "数据驱动"],
        language_style={"tone": "简洁"},
        decision_patterns=["MVP", "A/B测试"],
    )

    soul_v1 = mgr.load(version="1.0")
    assert soul_v1.identity["role"] == "PM"

    soul_v2 = mgr.load()
    assert soul_v2.identity["role"] == "Senior PM"


def test_get_raw_content(tmp_data_dir):
    mgr = SoulManager(data_dir=tmp_data_dir)
    mgr.save(
        version="1.0",
        identity={"role": "PM"},
        values=["快速迭代"],
        language_style={"tone": "简洁"},
        decision_patterns=["MVP"],
    )

    raw = mgr.get_raw_content()
    assert "# 身份认同" in raw
    assert "PM" in raw


def test_load_nonexistent_returns_none(tmp_data_dir):
    mgr = SoulManager(data_dir=tmp_data_dir)
    assert mgr.load() is None
