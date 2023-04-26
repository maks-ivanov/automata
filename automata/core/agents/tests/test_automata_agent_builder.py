import pytest

from automata.configs.agent_configs.config_type import AutomataAgentConfig, AutomataConfigVersion
from automata.core.agents.automata_agent import AutomataAgent
from automata.core.agents.automata_agent_builder import AutomataAgentBuilder
from automata.tool_management.tool_management_utils import build_llm_toolkits


def test_automata_agent_init(automata_agent):
    assert automata_agent is not None
    assert automata_agent.model == "gpt-4"
    assert automata_agent.session_id is not None
    tool_list = ["python_indexer", "python_writer", "codebase_oracle"]
    build_llm_toolkits(tool_list)

    assert len(automata_agent.llm_toolkits.keys()) > 0


def test_automata_agent_iter_task(
    automata_agent,
):
    assert len(automata_agent.messages) == 3


def test_builder_default_config(automata_agent_builder):
    agent = automata_agent_builder.build()

    assert agent.model == "gpt-4"
    assert agent.stream is False
    assert agent.verbose is False
    assert agent.max_iters == 1_000_000
    assert agent.temperature == 0.0
    assert agent.session_id is not None  # session id defaults if not set


def test_builder_provided_parameters_override_defaults(automata_agent_builder):
    agent = (
        automata_agent_builder.with_model("gpt-3.5-turbo")
        .with_stream(True)
        .with_verbose(True)
        .with_max_iters(500)
        .with_temperature(0.5)
        .with_session_id("test-session-id")
        .build()
    )

    assert agent.model == "gpt-3.5-turbo"
    assert agent.stream is True
    assert agent.verbose is True
    assert agent.max_iters == 500
    assert agent.temperature == 0.5
    assert agent.session_id == "test-session-id"


def test_builder_accepts_all_fields(automata_agent_builder):
    tool_list = ["python_indexer", "python_writer", "codebase_oracle"]
    mock_llm_toolkits = build_llm_toolkits(tool_list)
    instructions = "Test instructions."

    agent = (
        automata_agent_builder.with_llm_toolkits(mock_llm_toolkits)
        .with_instructions(instructions)
        .with_model("gpt-3.5-turbo")
        .with_stream(True)
        .with_verbose(True)
        .with_max_iters(500)
        .with_temperature(0.5)
        .with_session_id("test-session-id")
        .build()
    )
    assert agent.initial_payload == {}
    assert agent.llm_toolkits == mock_llm_toolkits
    assert agent.instructions == instructions
    assert agent.model == "gpt-3.5-turbo"
    assert agent.stream is True
    assert agent.verbose is True
    assert agent.max_iters == 500
    assert agent.temperature == 0.5
    assert agent.session_id == "test-session-id"


def test_builder_creates_proper_instance(automata_agent_builder):
    agent = automata_agent_builder.build()

    assert isinstance(agent, AutomataAgent)


def test_builder_invalid_input_types(automata_agent_builder):
    with pytest.raises(ValueError):
        automata_agent_builder.with_model(123)

    with pytest.raises(ValueError):
        automata_agent_builder.with_stream("True")

    with pytest.raises(ValueError):
        automata_agent_builder.with_verbose("True")

    with pytest.raises(ValueError):
        automata_agent_builder.with_max_iters("500")

    with pytest.raises(ValueError):
        automata_agent_builder.with_temperature("0.5")

    with pytest.raises(ValueError):
        automata_agent_builder.with_session_id(12345)


def test_config_loading_different_versions():
    for config_version in AutomataConfigVersion:
        agent_config = AutomataAgentConfig.load(config_version)
        assert isinstance(agent_config, AutomataAgentConfig)


def test_builder_gets_default_params_from_test_config():
    config_version = AutomataConfigVersion.TEST
    agent_config = AutomataAgentConfig.load(config_version)
    agent = AutomataAgentBuilder(agent_config).build()

    assert agent.instructions == "Test instructions."
    assert agent.model == "gpt-4"
    assert agent.stream is False
    assert agent.verbose is True
    assert agent.max_iters == 100
    assert agent.temperature == 0.8
    assert agent.session_id == "test-session-id"
