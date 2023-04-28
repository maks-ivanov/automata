import textwrap
from unittest.mock import MagicMock, patch

import pytest

from automata.core.agents.automata_agent import MasterAutomataAgent
from automata.core.agents.automata_agent_builder import AutomataAgentBuilder
from automata.core.agents.tests.conftest import automata_agent as automata_agent_fixture  # noqa
from automata.core.coordinator.agent_coordinator import AgentCoordinator, AgentInstance


@pytest.fixture
def coordinator(automata_agent_fixture):  # noqa
    master_agent = MasterAutomataAgent.from_agent(automata_agent_fixture)
    coordinator = AgentCoordinator(master_agent)
    return coordinator


def test_initialize_coordinator(coordinator):
    assert isinstance(coordinator, AgentCoordinator)


def test_add_agent(coordinator):
    agent_builder = AutomataAgentBuilder(config=None)
    agent_instance = AgentInstance(name="agent_0", builder=agent_builder)

    coordinator.add_agent_instance(agent_instance)
    assert len(coordinator.agent_instances) == 1


def test_cannot_add_agent_twice(coordinator):
    agent_builder = AutomataAgentBuilder(config=None)
    agent_instance = AgentInstance(name="agent_0", builder=agent_builder)

    coordinator.add_agent_instance(agent_instance)

    with pytest.raises(ValueError):
        coordinator.add_agent_instance(agent_instance)


def test_remove_agent(coordinator):
    agent_builder = AutomataAgentBuilder(config=None)
    agent_instance = AgentInstance(name="agent_0", builder=agent_builder)

    coordinator.add_agent_instance(agent_instance)
    coordinator.remove_agent_instance("agent_0")
    assert len(coordinator.agent_instances) == 0


def test_cannot_remove_missing_agent(coordinator):
    agent_builder = AutomataAgentBuilder(config=None)
    agent_instance = AgentInstance(name="agent_0", builder=agent_builder)

    coordinator.add_agent_instance(agent_instance)
    with pytest.raises(ValueError):
        coordinator.remove_agent_instance("agent_1")


def test_add_agent_set_coordinator(coordinator):
    agent_builder = AutomataAgentBuilder(config=None)
    agent_instance = AgentInstance(name="agent_0", builder=agent_builder)
    master_agent = coordinator.master_agent
    master_agent.set_coordinator(coordinator)
    coordinator.add_agent_instance(agent_instance)

    assert len(coordinator.agent_instances) == 1


def test_build_agent_message(coordinator):
    master_agent = coordinator.master_agent
    master_agent.set_coordinator(coordinator)
    master_agent.iter_task()


def mock_openai_response_with_completion_message():
    return {
        "choices": [
            {
                "message": {
                    "content": textwrap.dedent(
                        """
                        - thoughts
                        - I can retrieve this information directly with the python indexer.
                        - actions
                        - tool_query_0
                            - tool_name
                                - python-indexer-retrieve-docstring
                            - tool_args
                                - core.utils
                                - calculate_similarity
                        - tool_query_1
                            - tool_name
                                - python-indexer-retrieve-code
                            - tool_args
                                - core.utils
                                - calculate_similarity
                        - agent_query_0
                            - agent_name
                                - agent_0
                            - agent_instruction
                                - Begin
                        """
                    )
                }
            }
        ]
    }


def mocked_execute_agent(_):
    response = textwrap.dedent(
        '''
        - thoughts
            - Having successfully written the output file, I can now return the result.
        - actions
            - return_result_0
                - This is a mock return result
        """
        '''
    )
    return response


@pytest.mark.parametrize("api_response", [mock_openai_response_with_completion_message()])
@patch("openai.ChatCompletion.create")
def test_iter_task_with_completion_message(
    mock_openai_chatcompletion_create, api_response, coordinator
):
    mock_openai_chatcompletion_create.return_value = api_response
    master_agent = coordinator.master_agent

    master_agent._execute_agent = MagicMock(side_effect=mocked_execute_agent)

    master_agent.iter_task()

    completion_message = master_agent.messages[-1]["content"]
    assert "- agent_0_result_0" in completion_message
    assert "- This is a mock return " in completion_message
