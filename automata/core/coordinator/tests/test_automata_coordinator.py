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
    master_agent = coordinator.master_agent_instance
    master_agent.set_coordinator(coordinator)
    coordinator.add_agent_instance(agent_instance)

    assert len(coordinator.agent_instances) == 1


def test_build_agent_message(coordinator):
    agent_builder = AutomataAgentBuilder(config=None)
    agent_instance = AgentInstance(
        name="agent_0", builder=agent_builder, description="This is a test agent."
    )
    master_agent = coordinator.master_agent_instance
    master_agent.set_coordinator(coordinator)
    coordinator.add_agent_instance(agent_instance)
    assert coordinator._build_agent_message() == "Agents:\n\nagent_0: This is a test agent.\n"
