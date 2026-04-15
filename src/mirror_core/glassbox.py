"""GlassBox module: reasoning transparency and feedback collection."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from mirror_core.models import Memory, ReasoningTrace


class GlassBoxEngine:
    """Traces reasoning and collects user feedback."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.feedback_dir = data_dir / "feedback"
        self.feedback_dir.mkdir(parents=True, exist_ok=True)
        self.feedback_file = self.feedback_dir / "feedback_log.json"
        if not self.feedback_file.exists():
            self.feedback_file.write_text("[]", encoding="utf-8")
        self.feedback_log = self._load_feedback()

    def trace(
        self,
        intent: str,
        activated_layers: list[str],
        memories_used: list[Memory],
        response_text: str,
    ) -> ReasoningTrace:
        """Build a reasoning trace for a response."""
        sources = []
        for mem in memories_used:
            sources.append(
                {
                    "type": mem.type,
                    "content": mem.content[:200],
                    "domain": mem.domain,
                    "timestamp": mem.timestamp.isoformat(),
                    "confidence": mem.confidence,
                    "source": mem.source,
                }
            )

        confidence_level = self._assess_confidence(memories_used, activated_layers)

        thinking_process = self._build_thinking_process(
            intent, activated_layers, memories_used
        )

        speculation_parts = []
        if confidence_level in ("low", "medium"):
            speculation_parts.append(
                "部分回答基于推理而非直接记忆，可能与本人实际想法存在差异"
            )

        return ReasoningTrace(
            intent=intent,
            activated_layers=activated_layers,
            thinking_process=thinking_process,
            sources=sources,
            confidence_level=confidence_level,
            speculation_parts=speculation_parts,
        )

    def record_feedback(
        self,
        query: str,
        response: str,
        feedback_type: str,
        correction: Optional[str],
    ) -> None:
        """Record user feedback on a response."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response[:500],
            "feedback_type": feedback_type,
            "correction": correction,
        }
        self.feedback_log.append(entry)
        self._save_feedback()

    def get_feedback_log(self) -> list[dict]:
        """Return all feedback entries."""
        return self.feedback_log

    def get_negative_feedback_count(self) -> int:
        """Count feedback entries that indicate the response was wrong."""
        return sum(
            1
            for f in self.feedback_log
            if f["feedback_type"] in ("not_me", "partially")
        )

    def _assess_confidence(
        self,
        memories: list[Memory],
        layers: list[str],
    ) -> str:
        if not memories:
            return "low"
        avg_conf = sum(m.confidence for m in memories) / len(memories)
        if avg_conf >= 0.85 and len(layers) >= 2:
            return "high"
        elif avg_conf >= 0.6:
            return "medium"
        return "low"

    def _build_thinking_process(
        self,
        intent: str,
        layers: list[str],
        memories: list[Memory],
    ) -> list[str]:
        steps = [f"识别用户意图为: {intent}"]
        for layer in layers:
            steps.append(f"激活 {layer} 层")
        if memories:
            steps.append(f"检索到 {len(memories)} 条相关记忆")
            top = memories[0]
            steps.append(f"最相关记忆来自: {top.source} (置信度: {top.confidence})")
        else:
            steps.append("未检索到相关记忆，基于通用方法论推理")
        return steps

    def _load_feedback(self) -> list[dict]:
        text = self.feedback_file.read_text(encoding="utf-8")
        return json.loads(text) if text.strip() else []

    def _save_feedback(self) -> None:
        self.feedback_file.write_text(
            json.dumps(self.feedback_log, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
