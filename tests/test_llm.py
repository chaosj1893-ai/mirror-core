from unittest.mock import MagicMock, patch

from mirror_core.llm import LLMClient


def test_llm_client_init():
    client = LLMClient(api_key="test-key")
    assert client.model == "claude-sonnet-4-20250514"


def test_llm_client_init_custom_model():
    client = LLMClient(api_key="test-key", model="claude-opus-4-20250514")
    assert client.model == "claude-opus-4-20250514"


@patch("mirror_core.llm.anthropic.Anthropic")
def test_llm_generate(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client

    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="我建议先做MVP验证")]
    mock_client.messages.create.return_value = mock_response

    client = LLMClient(api_key="test-key")
    result = client.generate(
        system_prompt="你是JC的数字分身",
        user_message="这个功能该怎么做？",
    )

    assert result == "我建议先做MVP验证"
    mock_client.messages.create.assert_called_once()
    call_kwargs = mock_client.messages.create.call_args[1]
    assert call_kwargs["system"] == "你是JC的数字分身"
    assert call_kwargs["messages"][0]["content"] == "这个功能该怎么做？"


@patch("mirror_core.llm.anthropic.Anthropic")
def test_llm_generate_with_max_tokens(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client

    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="回答")]
    mock_client.messages.create.return_value = mock_response

    client = LLMClient(api_key="test-key")
    client.generate(
        system_prompt="test",
        user_message="test",
        max_tokens=500,
    )

    call_kwargs = mock_client.messages.create.call_args[1]
    assert call_kwargs["max_tokens"] == 500
