from typing import Optional, Tuple

import pytest

from automata.core.base.base_tool import BaseTool


class MockTool(BaseTool):
    def _run(self, tool_input: Tuple[Optional[str], ...]) -> str:
        return "MockTool response"

    async def _arun(self, tool_input: Tuple[Optional[str], ...]) -> str:
        return "MockTool async response"


@pytest.fixture
def mock_tool():
    return MockTool(name="MockTool", description="A mock tool for testing purposes")


def test_base_tool_instantiation(mock_tool):
    assert mock_tool.name == "MockTool"
    assert mock_tool.description == "A mock tool for testing purposes"
    assert mock_tool.return_direct is False
    assert mock_tool.verbose is False


def test_base_tool_run(mock_tool):
    tool_input = ("test",)
    response = mock_tool.run(tool_input)
    assert response == "MockTool response"


@pytest.mark.asyncio
async def test_base_tool_arun(mock_tool):
    tool_input = ("test",)
    response = await mock_tool.arun(tool_input)
    assert response == "MockTool async response"


def test_base_tool_call(mock_tool):
    tool_input = ("test",)
    response = mock_tool(tool_input)
    assert response == "MockTool response"
