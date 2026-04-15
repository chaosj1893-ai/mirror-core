import json
from datetime import datetime

from mirror_core.timeline import TimelineManager


def test_timeline_init(tmp_data_dir):
    mgr = TimelineManager(data_dir=tmp_data_dir)
    assert mgr.versions_file.exists()


def test_create_version(tmp_data_dir):
    mgr = TimelineManager(data_dir=tmp_data_dir)
    pv = mgr.create_version(
        version="1.0",
        soul_snapshot="# Soul v1.0\nrole: PM",
        faculty_diff={"product": "初始创建"},
        body_additions=["wonderai case"],
        changelog="初始版本",
    )
    assert pv.version == "1.0"
    assert pv.changelog == "初始版本"


def test_list_versions(tmp_data_dir):
    mgr = TimelineManager(data_dir=tmp_data_dir)
    mgr.create_version("1.0", "soul v1", {}, [], "v1")
    mgr.create_version("2.0", "soul v2", {"product": "added RICE"}, ["new case"], "v2")

    versions = mgr.list_versions()
    assert len(versions) == 2
    assert versions[0].version == "1.0"
    assert versions[1].version == "2.0"


def test_get_current_version(tmp_data_dir):
    mgr = TimelineManager(data_dir=tmp_data_dir)
    mgr.create_version("1.0", "soul v1", {}, [], "v1")
    mgr.create_version("2.0", "soul v2", {}, [], "v2")

    assert mgr.get_current_version() == "2.0"


def test_compare_versions(tmp_data_dir):
    mgr = TimelineManager(data_dir=tmp_data_dir)
    mgr.create_version("1.0", "role: PM\nvalues: 快速迭代", {}, [], "v1")
    mgr.create_version("2.0", "role: Senior PM\nvalues: 快速迭代, 数据驱动", {"product": "added RICE"}, ["case1"], "v2")

    diff = mgr.compare("1.0", "2.0")
    assert diff.v1 == "1.0"
    assert diff.v2 == "2.0"
    assert diff.body_changes_count == 1


def test_get_current_version_empty(tmp_data_dir):
    mgr = TimelineManager(data_dir=tmp_data_dir)
    assert mgr.get_current_version() is None
