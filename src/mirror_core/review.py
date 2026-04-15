"""Review module: review documents through the persona's lens."""

from pathlib import Path

from mirror_core.faculty import FacultyManager
from mirror_core.llm import LLMClient
from mirror_core.soul import SoulManager


class ReviewEngine:
    """Reviews files using the persona's standards and perspective."""

    def __init__(self, soul: SoulManager, faculty: FacultyManager, llm: LLMClient):
        self.soul = soul
        self.faculty = faculty
        self.llm = llm

    def review_file(self, file_path: Path) -> str:
        """Read a file and review it from the persona's perspective."""
        content = file_path.read_text(encoding="utf-8")
        return self.review_text(content, file_path.name)

    def review_text(self, content: str, source_name: str = "文档") -> str:
        """Review text content from the persona's perspective."""
        soul_content = self.soul.get_raw_content() or ""

        # Gather all faculty domains
        faculty_parts = []
        for domain in self.faculty.list_domains():
            raw = self.faculty.get_raw_content(domain)
            if raw:
                faculty_parts.append(raw)
        faculty_content = "\n\n".join(faculty_parts)

        system_prompt = (
            f"你是用户的数字分身，以下是你的人格和专业能力。\n\n"
            f"# 人格核心\n{soul_content}\n\n"
            f"# 专业能力\n{faculty_content}\n\n"
            f"---\n"
            f"你现在要用自己的标准审视一份文档。请从以下角度给出反馈：\n"
            f"1. 逻辑是否自洽\n"
            f"2. 有没有遗漏的重要考虑点\n"
            f"3. 哪些地方你觉得不够好，为什么\n"
            f"4. 你会怎么改进\n\n"
            f"用你平时的说话风格回答。"
        )

        user_message = f"请审视以下文档（{source_name}）：\n\n{content}"

        return self.llm.generate(system_prompt=system_prompt, user_message=user_message)

    def build_review_prompt(self, content: str, source_name: str = "文档") -> tuple[str, str]:
        """Build the review prompt without calling LLM. For Claude Code skill use."""
        soul_content = self.soul.get_raw_content() or ""

        faculty_parts = []
        for domain in self.faculty.list_domains():
            raw = self.faculty.get_raw_content(domain)
            if raw:
                faculty_parts.append(raw)
        faculty_content = "\n\n".join(faculty_parts)

        system_prompt = (
            f"你是用户的数字分身，以下是你的人格和专业能力。\n\n"
            f"# 人格核心\n{soul_content}\n\n"
            f"# 专业能力\n{faculty_content}\n\n"
            f"---\n"
            f"你现在要用自己的标准审视一份文档。请从以下角度给出反馈：\n"
            f"1. 逻辑是否自洽\n"
            f"2. 有没有遗漏的重要考虑点\n"
            f"3. 哪些地方你觉得不够好，为什么\n"
            f"4. 你会怎么改进\n\n"
            f"用你平时的说话风格回答。"
        )

        user_message = f"请审视以下文档（{source_name}）：\n\n{content}"

        return system_prompt, user_message
