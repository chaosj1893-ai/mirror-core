"""Distill engine: interactive questionnaire for persona extraction."""

import json
from pathlib import Path
from typing import Optional


class DistillEngine:
    """Manages the 6-round distillation questionnaire."""

    ROUND_TARGETS = {
        1: "soul",
        2: "soul",
        3: "soul",
        4: "faculty",
        5: "body",
        6: "calibration",
    }

    def __init__(self, data_dir: Path, templates_dir: Path):
        self.data_dir = data_dir
        self.templates_dir = templates_dir
        questionnaire_path = templates_dir / "questionnaire.json"
        with open(questionnaire_path, encoding="utf-8") as f:
            self.questionnaire = json.load(f)

    def get_total_rounds(self) -> int:
        """Return the total number of distillation rounds."""
        return len(self.questionnaire["rounds"])

    def get_round(self, round_id: int) -> Optional[dict]:
        """Get a specific round's definition."""
        for r in self.questionnaire["rounds"]:
            if r["id"] == round_id:
                return r
        return None

    def process_round_answers(
        self,
        round_id: int,
        answers: dict[str, str],
    ) -> dict:
        """Process answers for a single round.

        Returns a dict with:
        - target: which layer this data feeds ("soul", "faculty", "body", "calibration")
        - raw_text: concatenated Q&A text for downstream processing
        - answers: the original answers dict
        """
        round_def = self.get_round(round_id)
        if not round_def:
            raise ValueError(f"Round {round_id} not found")

        target = self.ROUND_TARGETS.get(round_id, "unknown")

        lines = []
        for q in round_def["questions"]:
            qid = q["id"]
            answer = answers.get(qid, "")
            lines.append(f"Q: {q['text']}")
            lines.append(f"A: {answer}")
            lines.append("")

        return {
            "target": target,
            "round_id": round_id,
            "round_name": round_def["name"],
            "raw_text": "\n".join(lines),
            "answers": answers,
        }
