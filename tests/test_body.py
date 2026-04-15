from datetime import datetime

from mirror_core.body import BodyManager
from mirror_core.models import Memory


def test_body_manager_init(tmp_data_dir):
    mgr = BodyManager(data_dir=tmp_data_dir)
    assert mgr.collection is not None


def test_ingest_and_search(tmp_data_dir):
    mgr = BodyManager(data_dir=tmp_data_dir)

    mgr.ingest(
        content="WonderAI V6.0 从功能墙改为积分消耗制，提升付费转化率",
        type="case",
        domain="product",
        tags=["付费转化", "积分体系"],
        confidence=0.95,
        source="obsidian/wonderai.md",
        version="v1.0",
    )

    results = mgr.search("积分制改造付费", top_k=3)
    assert len(results) >= 1
    assert "积分" in results[0].content


def test_search_with_domain_filter(tmp_data_dir):
    mgr = BodyManager(data_dir=tmp_data_dir)

    mgr.ingest(
        content="RICE模型用于产品功能优先级排序",
        type="document",
        domain="product",
        tags=["方法论"],
        confidence=0.9,
        source="notes/rice.md",
        version="v1.0",
    )
    mgr.ingest(
        content="Transformer架构是大模型的基础",
        type="document",
        domain="ai",
        tags=["技术"],
        confidence=0.9,
        source="notes/transformer.md",
        version="v1.0",
    )

    results = mgr.search("模型架构", top_k=5, domain="ai")
    domains = [r.domain for r in results]
    assert all(d == "ai" for d in domains)


def test_search_empty_collection(tmp_data_dir):
    mgr = BodyManager(data_dir=tmp_data_dir)
    results = mgr.search("anything", top_k=3)
    assert results == []


def test_ingest_batch(tmp_data_dir):
    mgr = BodyManager(data_dir=tmp_data_dir)

    items = [
        {
            "content": f"文档内容 {i}",
            "type": "document",
            "domain": "product",
            "tags": ["test"],
            "confidence": 0.8,
            "source": f"doc_{i}.md",
            "version": "v1.0",
        }
        for i in range(5)
    ]
    mgr.ingest_batch(items)

    results = mgr.search("文档内容", top_k=10)
    assert len(results) == 5
