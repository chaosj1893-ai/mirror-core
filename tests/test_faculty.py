from mirror_core.faculty import FacultyManager


def test_faculty_manager_init(tmp_data_dir):
    mgr = FacultyManager(data_dir=tmp_data_dir)
    assert mgr.faculty_dir == tmp_data_dir / "faculty"


def test_save_and_load_faculty(tmp_data_dir):
    mgr = FacultyManager(data_dir=tmp_data_dir)
    mgr.save(
        domain="product",
        version="1.0",
        frameworks={"需求分析": "用户→痛点→方案", "优先级": "RICE模型"},
        case_refs=["body/cases/wonderai.md"],
    )

    faculty = mgr.load("product")
    assert faculty.domain == "product"
    assert "需求分析" in faculty.frameworks
    assert len(faculty.case_refs) == 1


def test_load_nonexistent_returns_none(tmp_data_dir):
    mgr = FacultyManager(data_dir=tmp_data_dir)
    assert mgr.load("nonexistent") is None


def test_list_domains(tmp_data_dir):
    mgr = FacultyManager(data_dir=tmp_data_dir)
    mgr.save(domain="product", version="1.0", frameworks={"a": "b"}, case_refs=[])
    mgr.save(domain="ai", version="1.0", frameworks={"c": "d"}, case_refs=[])

    domains = mgr.list_domains()
    assert set(domains) == {"product", "ai"}


def test_get_raw_content(tmp_data_dir):
    mgr = FacultyManager(data_dir=tmp_data_dir)
    mgr.save(domain="product", version="1.0", frameworks={"需求分析": "框架"}, case_refs=[])

    raw = mgr.get_raw_content("product")
    assert "# 方法论" in raw
    assert "需求分析" in raw
