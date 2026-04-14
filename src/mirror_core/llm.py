"""Claude API wrapper for MirrorCore."""

import anthropic


class LLMClient:
    """Thin wrapper around the Anthropic Claude API."""

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-20250514",
    ):
        self.model = model
        self._client = anthropic.Anthropic(api_key=api_key)

    def generate(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 4096,
    ) -> str:
        """Generate a response from Claude."""
        response = self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text
