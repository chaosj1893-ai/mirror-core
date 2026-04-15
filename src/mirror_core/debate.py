"""Debate module: multi-persona debate on a given topic."""

from pathlib import Path

from mirror_core.faculty import FacultyManager
from mirror_core.llm import LLMClient
from mirror_core.models import DebateResult
from mirror_core.soul import SoulManager


class DebateEngine:
    """Runs a structured debate between two personas."""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def run_debate(
        self,
        persona1_dir: Path,
        persona2_dir: Path,
        topic: str,
        rounds: int = 3,
    ) -> DebateResult:
        """Execute a multi-round debate between two personas."""
        soul1 = SoulManager(data_dir=persona1_dir)
        soul2 = SoulManager(data_dir=persona2_dir)
        faculty1 = FacultyManager(data_dir=persona1_dir)
        faculty2 = FacultyManager(data_dir=persona2_dir)

        name1 = self._get_name(soul1)
        name2 = self._get_name(soul2)

        profile1 = self._build_profile(soul1, faculty1)
        profile2 = self._build_profile(soul2, faculty2)

        history = []
        debate_rounds = []

        for i in range(rounds * 2):
            is_persona1 = i % 2 == 0
            current_name = name1 if is_persona1 else name2
            current_profile = profile1 if is_persona1 else profile2

            system_prompt = (
                f"你是 {current_name}，以下是你的人格和专业能力：\n\n"
                f"{current_profile}\n\n"
                f"---\n"
                f"你正在与另一个人辩论以下话题：{topic}\n\n"
            )

            if history:
                system_prompt += "之前的对话：\n"
                for h in history:
                    system_prompt += f"[{h['persona']}]: {h['position']}\n\n"
                system_prompt += "请回应对方的观点，表达你的立场。用你自己的说话风格。"
            else:
                system_prompt += "请先表达你对这个话题的立场和理由。用你自己的说话风格。"

            response = self.llm.generate(
                system_prompt=system_prompt,
                user_message=f"话题：{topic}",
            )

            entry = {"persona": current_name, "position": response, "round": i // 2 + 1}
            history.append(entry)
            debate_rounds.append(entry)

        # Summarize
        summary = self._summarize(name1, name2, topic, history)

        return DebateResult(
            topic=topic,
            rounds=debate_rounds,
            consensus=summary["consensus"],
            disagreements=summary["disagreements"],
            summary=summary["text"],
        )

    def _get_name(self, soul: SoulManager) -> str:
        data = soul.load()
        if data and data.identity.get("role"):
            return data.identity.get("role", "未知")
        return "未知"

    def _build_profile(self, soul: SoulManager, faculty: FacultyManager) -> str:
        parts = []
        raw = soul.get_raw_content()
        if raw:
            parts.append(raw)
        for domain in faculty.list_domains():
            content = faculty.get_raw_content(domain)
            if content:
                parts.append(content)
        return "\n\n".join(parts)

    def _summarize(self, name1: str, name2: str, topic: str, history: list[dict]) -> dict:
        debate_text = ""
        for h in history:
            debate_text += f"[{h['persona']}]: {h['position']}\n\n"

        system_prompt = (
            f"你是一个中立的辩论总结者。以下是 {name1} 和 {name2} 关于\"{topic}\"的辩论。\n"
            f"请总结：\n"
            f"1. 双方的核心分歧点（列表）\n"
            f"2. 双方的共识点（列表）\n"
            f"3. 简要总结（2-3句话）\n\n"
            f"用以下格式回答：\n"
            f"分歧：\n- xxx\n- xxx\n\n共识：\n- xxx\n\n总结：xxx"
        )

        result = self.llm.generate(system_prompt=system_prompt, user_message=debate_text)

        # Parse the structured response
        consensus = []
        disagreements = []
        current = None
        for line in result.split("\n"):
            line = line.strip()
            if line.startswith("分歧") or line.startswith("disagreement"):
                current = "disagree"
            elif line.startswith("共识") or line.startswith("consensus"):
                current = "agree"
            elif line.startswith("总结") or line.startswith("summary"):
                current = None
            elif line.startswith("- ") and current == "disagree":
                disagreements.append(line[2:])
            elif line.startswith("- ") and current == "agree":
                consensus.append(line[2:])

        return {
            "consensus": consensus,
            "disagreements": disagreements,
            "text": result,
        }
