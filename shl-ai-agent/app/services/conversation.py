"""Stateless conversation orchestration."""

import re

from app.models.catalog import Assessment
from app.models.chat import ChatRequest, ChatResponse, Recommendation
from app.prompts.templates import comparison_prompt, recommendation_prompt
from app.services.gemini import GeminiClient
from app.services.retrieval import HybridRetriever, SearchResult


DOMAIN_TERMS = {
    "hire", "hiring", "candidate", "assessment", "test", "role", "developer", "engineer",
    "manager", "sales", "support", "java", "python", "cognitive", "personality", "skill",
    "skills", "technical", "non-technical", "graduate", "entry", "senior", "lead",
}
OFF_TOPIC_TERMS = {"legal advice", "medical advice", "weather", "recipe", "stock", "politics"}
INJECTION_PATTERNS = (
    "ignore previous",
    "ignore all previous",
    "system prompt",
    "developer message",
    "reveal prompt",
    "jailbreak",
    "api key",
)


class ConversationService:
    """Coordinates intent checks, retrieval, Gemini text, and response validation."""

    def __init__(self) -> None:
        self.retriever = HybridRetriever()
        self.gemini = GeminiClient()

    def respond(self, request: ChatRequest) -> ChatResponse:
        """Produce a response for a stateless chat history."""
        messages = request.messages[-16:]
        user_messages = [message.content for message in messages if message.role == "user"]
        latest = user_messages[-1]
        context = "\n".join(user_messages[-8:])

        if self._is_injection(latest):
            return ChatResponse(
                reply="I can only help with SHL assessment selection and cannot follow prompt override requests.",
                recommendations=[],
                end_of_conversation=False,
            )
        if self._has_explicit_off_topic(latest):
            return ChatResponse(
                reply="I can help only with SHL assessment recommendations, comparisons, and refinements.",
                recommendations=[],
                end_of_conversation=False,
            )
        if self._needs_clarification(context):
            return ChatResponse(
                reply=(
                    "Could you share the target role, seniority, and whether you need technical skills, "
                    "cognitive ability, personality, or a combination?"
                ),
                recommendations=[],
                end_of_conversation=False,
            )
        if self._is_off_topic(latest, context):
            return ChatResponse(
                reply="I can help only with SHL assessment recommendations, comparisons, and refinements.",
                recommendations=[],
                end_of_conversation=False,
            )

        results = self.retriever.search(context, top_k=10)
        if not results:
            return ChatResponse(
                reply="I could not find a matching SHL assessment in the catalog. Could you add the role or skill area?",
                recommendations=[],
                end_of_conversation=False,
            )

        if self._is_comparison(latest):
            selected = self._select_for_comparison(latest, results)
            reply = self._comparison_reply(context, selected)
            return ChatResponse(reply=reply, recommendations=[], end_of_conversation=False)

        selected = [result.assessment for result in results[: min(10, len(results))]]
        reply = self._recommendation_reply(context, selected)
        recommendations = [
            Recommendation(name=item.name, url=item.url, test_type=item.test_type)
            for item in selected
        ]
        return ChatResponse(reply=reply, recommendations=recommendations, end_of_conversation=False)

    def _is_injection(self, latest: str) -> bool:
        """Detect prompt injection attempts."""
        lowered = latest.lower()
        return any(pattern in lowered for pattern in INJECTION_PATTERNS)

    def _is_off_topic(self, latest: str, context: str) -> bool:
        """Detect clearly unrelated requests."""
        lowered_context = context.lower()
        tokens = set(re.findall(r"[a-zA-Z][a-zA-Z+#.]{1,}", lowered_context))
        return not bool(tokens & DOMAIN_TERMS)

    def _has_explicit_off_topic(self, latest: str) -> bool:
        """Return whether a request names a clearly unrelated topic."""
        lowered = latest.lower()
        return any(term in lowered for term in OFF_TOPIC_TERMS)

    def _needs_clarification(self, context: str) -> bool:
        """Return whether the accumulated context is too vague to retrieve safely."""
        lowered = context.lower()
        if len(lowered.split()) <= 3 and not any(term in lowered for term in ("java", "python", ".net", "sales")):
            return True
        has_role_signal = any(term in lowered for term in ("developer", "engineer", "manager", "sales", "support", "analyst", "graduate", "candidate"))
        has_skill_signal = any(term in lowered for term in ("java", "python", ".net", "sql", "cognitive", "personality", "technical", "leadership", "coding", "excel"))
        has_assessment_signal = "assessment" in lowered or "test" in lowered
        return not (has_role_signal or has_skill_signal or has_assessment_signal)

    def _is_comparison(self, latest: str) -> bool:
        """Return whether the user is asking for a comparison."""
        lowered = latest.lower()
        return any(term in lowered for term in ("compare", "difference", "differences", " versus ", " vs ", "which is better"))

    def _select_for_comparison(self, latest: str, results: list[SearchResult]) -> list[Assessment]:
        """Select likely comparison items from retrieved results."""
        lowered = latest.lower()
        named = [result.assessment for result in results if result.assessment.name.lower() in lowered]
        if len(named) >= 2:
            return named[:4]
        return [result.assessment for result in results[:3]]

    def _catalog_context(self, assessments: list[Assessment]) -> str:
        """Format catalog facts for prompts."""
        lines: list[str] = []
        for item in assessments:
            facts = [
                f"Name: {item.name}",
                f"URL: {item.url}",
                f"Type: {item.test_type}",
                f"Job levels: {', '.join(item.job_levels) or 'Not specified'}",
                f"Duration: {item.duration or 'Not specified'}",
                f"Remote: {item.remote or 'Not specified'}",
                f"Adaptive: {item.adaptive or 'Not specified'}",
                f"Description: {item.description}",
            ]
            lines.append(" | ".join(facts))
        return "\n".join(lines)

    def _recommendation_reply(self, context: str, assessments: list[Assessment]) -> str:
        """Generate recommendation prose."""
        prompt = recommendation_prompt(context, self._catalog_context(assessments))
        generated = self.gemini.generate(prompt)
        if generated:
            return generated
        names = ", ".join(item.name for item in assessments[:5])
        return f"Based on the SHL catalog, the strongest matches are {names}. I prioritized role and skill overlap from the assessment descriptions and categories."

    def _comparison_reply(self, context: str, assessments: list[Assessment]) -> str:
        """Generate comparison prose."""
        prompt = comparison_prompt(context, self._catalog_context(assessments))
        generated = self.gemini.generate(prompt)
        if generated:
            return generated
        parts = [
            f"{item.name}: {item.test_type}; {item.duration or 'duration not specified'}; {item.description[:180]}"
            for item in assessments
        ]
        return "Here is the catalog-grounded comparison. " + " ".join(parts)
