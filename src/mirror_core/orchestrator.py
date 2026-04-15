"""Orchestrator: routes queries through the four-layer persona system."""

from mirror_core.body import BodyManager
from mirror_core.faculty import FacultyManager
from mirror_core.glassbox import GlassBoxEngine
from mirror_core.llm import LLMClient
from mirror_core.models import Memory, Response
from mirror_core.soul import SoulManager
from mirror_core.timeline import TimelineManager

_VERSION_KEYWORDS = ["对比", "版本", "变化", "成长", "演进", "之前的我", "过去的我"]
_REFLECTION_KEYWORDS = ["回顾", "反思", "复盘", "审视", "盲点", "第二大脑"]
_KNOWLEDGE_KEYWORDS = ["什么是", "解释", "定义", "介绍", "是什么"]

_DOMAIN_KEYWORDS = {
    "product": ["产品", "需求", "功能", "优先级", "用户", "迭代", "MVP"],
    "ai": ["AI", "模型", "大模型", "GPT", "Claude", "提示词", "prompt"],
    "business": ["商业", "定价", "变现", "收入", "利润", "市场"],
}


class Orchestrator:
    """Routes queries through Soul/Faculty/Body layers and assembles responses."""

    def __init__(
        self,
        soul: SoulManager,
        faculty: FacultyManager,
        body: BodyManager,
        timeline: TimelineManager,
        glassbox: GlassBoxEngine,
        llm: LLMClient,
    ):
        self.soul = soul
        self.faculty = faculty
        self.body = body
        self.timeline = timeline
        self.glassbox = glassbox
        self.llm = llm

    def process_query(self, user_query: str) -> Response:
        """Full query processing pipeline."""
        intent = self.classify_intent(user_query)
        domain = self._detect_domain(user_query)
        memories = self.body.search(query=user_query, top_k=5, domain=domain)

        system_prompt, user_msg = self.build_prompt(
            intent=intent,
            domain=domain,
            memories=memories,
            user_query=user_query,
        )

        response_text = self.llm.generate(
            system_prompt=system_prompt,
            user_message=user_msg,
        )

        activated = ["soul"]
        if domain and self.faculty.load(domain):
            activated.append(f"faculty_{domain}")
        if memories:
            activated.append("body")

        reasoning = self.glassbox.trace(
            intent=intent,
            activated_layers=activated,
            memories_used=memories,
            response_text=response_text,
        )

        return Response(content=response_text, reasoning=reasoning)

    @staticmethod
    def classify_intent(query: str) -> str:
        """Classify the user's intent based on keywords."""
        q = query.lower()
        if any(kw in q for kw in _VERSION_KEYWORDS):
            return "version_compare"
        if any(kw in q for kw in _REFLECTION_KEYWORDS):
            return "self_reflection"
        if any(kw in q for kw in _KNOWLEDGE_KEYWORDS):
            return "knowledge_query"
        return "product_advice"

    def build_prompt(
        self,
        intent: str,
        domain: str | None,
        memories: list[Memory],
        user_query: str,
    ) -> tuple[str, str]:
        """Build system prompt and user message."""
        soul_content = self.soul.get_raw_content() or ""

        faculty_content = ""
        if domain:
            faculty_content = self.faculty.get_raw_content(domain) or ""

        memory_lines = []
        for i, mem in enumerate(memories, 1):
            memory_lines.append(
                f"记忆{i}:\n{mem.content}\n"
                f"来源: {mem.source} | 时间: {mem.timestamp.strftime('%Y-%m-%d')} | "
                f"置信度: {mem.confidence}"
            )
        memory_section = "\n\n".join(memory_lines) if memory_lines else "无相关记忆"

        system_prompt = (
            f"你是用户的数字分身，基于以下信息回答问题。\n\n"
            f"# 人格核心（Soul）\n{soul_content}\n\n"
            f"# 专业能力（Faculty）\n{faculty_content}\n\n"
            f"# 相关记忆（Body）\n{memory_section}\n\n"
            f"---\n"
            f"回答要求：\n"
            f"1. 用本人的语言风格和思维方式\n"
            f"2. 优先引用相关记忆中的案例\n"
            f"3. 如果记忆中没有直接答案，基于方法论推理，并标注'这是推测'\n"
            f"4. 保持简洁，核心观点先行"
        )

        return system_prompt, user_query

    def _detect_domain(self, query: str) -> str | None:
        """Detect which professional domain a query belongs to."""
        q = query.lower()
        for domain, keywords in _DOMAIN_KEYWORDS.items():
            if any(kw.lower() in q for kw in keywords):
                return domain
        return None
