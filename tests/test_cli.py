import pytest
from click.testing import CliRunner

from mirror_core.cli import main


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_help(runner):
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "MirrorCore" in result.output


def test_cli_distill_help(runner):
    result = runner.invoke(main, ["distill", "--help"])
    assert result.exit_code == 0
    assert "distill" in result.output.lower() or "蒸馏" in result.output


def test_cli_chat_help(runner):
    result = runner.invoke(main, ["chat", "--help"])
    assert result.exit_code == 0


def test_cli_sync_help(runner):
    result = runner.invoke(main, ["sync", "--help"])
    assert result.exit_code == 0


def test_cli_versions_help(runner):
    result = runner.invoke(main, ["versions", "--help"])
    assert result.exit_code == 0
