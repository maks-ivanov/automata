import textwrap

from automata.core.agents.automata_agent_helpers import (
    ActionExtractor,
    generate_user_observation_message,
    retrieve_completion_message,
)


def test_extract_actions_0():
    input_text = textwrap.dedent(
        """
        - thoughts
            - I will use the automata-indexer-retrieve-code tool to retrieve the code for the "run" function from the Automata agent.
        - actions
            - tool_query_0
                - tool_name
                    - automata-indexer-retrieve-code
                - tool_args
                    - Retrieve the raw code for the function 'run' from the Automata agent, including all necessary imports and docstrings.
        """
    )

    result = ActionExtractor.extract_actions(input_text)
    assert result[0].tool_name == "automata-indexer-retrieve-code"
    assert (
        result[0].tool_args[0]
        == "Retrieve the raw code for the function 'run' from the Automata agent, including all necessary imports and docstrings."
    )


def test_extract_actions_1():
    input_text = textwrap.dedent(
        """
        - thoughts
            - I will use the automata-indexer-retrieve-code tool to retrieve the code for the "run" function from the Automata agent.
        - actions
            - tool_query_0
                - tool_name
                    - automata-indexer-retrieve-code
                - tool_args
                    - Retrieve the raw code for the function 'run' from the Automata agent, including all necessary imports and docstrings.
            - tool_query_1
                - tool_name
                    - automata-writer-modify-module
                - tool_args
                    - Modify the code in the Automata agent.
                    - A dummy input....
        """
    )

    result = ActionExtractor.extract_actions(input_text)
    assert result[0].tool_name == "automata-indexer-retrieve-code"
    assert (
        result[0].tool_args[0]
        == "Retrieve the raw code for the function 'run' from the Automata agent, including all necessary imports and docstrings."
    )

    assert result[1].tool_name == "automata-writer-modify-module"
    assert result[1].tool_args[0] == "Modify the code in the Automata agent."

    assert result[1].tool_args[1] == "A dummy input...."


def test_extract_actions_2():
    input_text = textwrap.dedent(
        """
        - thoughts
            - I will use the automata-indexer-retrieve-code tool to retrieve the code for the "run" function from the Automata agent.
        - actions
            - tool_query_0
                - tool_name
                    - automata-indexer-retrieve-code
                - tool_args
                    - Retrieve the raw code for the function 'run' from the Automata agent, including all necessary imports and docstrings.
            - tool_query_1
                - tool_name
                    - automata-writer-modify-module
                - tool_args
                    - Modify the code in the Automata agent.
                    - python
                    ```
                    def f(x: int) -> int:
                        return 0
                    ```
        """
    )

    result = ActionExtractor.extract_actions(input_text)
    assert result[0].tool_name == "automata-indexer-retrieve-code"
    assert (
        result[0].tool_args[0]
        == "Retrieve the raw code for the function 'run' from the Automata agent, including all necessary imports and docstrings."
    )

    assert result[1].tool_name == "automata-writer-modify-module"
    assert result[1].tool_args[0] == "Modify the code in the Automata agent."

    assert result[1].tool_args[1] == "def f(x: int) -> int:\n    return 0\n"


def test_extract_actions_3():
    text = textwrap.dedent(
        """
        *Assistant*
            - thoughts
                - Having successfully written the output file, I can now return the result.
            - actions
                - return_result_0
                    - Function 'run' has been added to core.tests.sample_code.test.
        """
    )

    extractor = ActionExtractor()
    result = extractor.extract_actions(text)

    assert result[0].result_name == "return_result_0"
    assert (
        result[0].result_outputs[0]
        == "Function 'run' has been added to core.tests.sample_code.test."
    )


def test_extract_actions_4():
    text = textwrap.dedent(
        """
        *Assistant*
            - thoughts
                - Having successfully written the output file, I can now return the result.
            - actions
                - tool_query_0
                    - tool_name
                        - automata-indexer-retrieve-code
                    - tool_args
                        - Retrieve the raw code for the function 'run' from the Automata agent, including all necessary imports and docstrings.

                - return_result_0
                    - Function 'run' has been added to core.tests.sample_code.test.
        """
    )

    extractor = ActionExtractor()
    results = extractor.extract_actions(text)
    assert results[0].tool_name == "automata-indexer-retrieve-code"
    assert (
        results[0].tool_args[0]
        == "Retrieve the raw code for the function 'run' from the Automata agent, including all necessary imports and docstrings."
    )
    assert results[1].result_name == "return_result_0"
    assert (
        results[1].result_outputs[0]
        == "Function 'run' has been added to core.tests.sample_code.test."
    )


def test_extract_actions_5(automata_agent):
    text = textwrap.dedent(
        """
        - thoughts
            - Having successfully written the output file, I can now return the result.
        - actions
            - tool_query_0
                - tool_name
                    - automata-indexer-retrieve-code
                - tool_args
                    - Retrieve the raw code for the function 'run' from the Automata agent, including all necessary imports and docstrings.

            - return_result_0
                - Function 'run' has been added to core.tests.sample_code.test.
        """
    )
    processed_input = automata_agent._generate_observations(text)
    assert (
        processed_input["tool_output_0"]
        == """Error: Tool 'automata-indexer-retrieve-code' not found."""
    )
    assert (
        processed_input["return_result_0"]
        == """Function 'run' has been added to core.tests.sample_code.test."""
    )


def test_extract_actions_6(automata_agent):
    text = textwrap.dedent(
        """
        - thoughts
            - Having successfully written the output file, I can now return the result.
        - actions
            - tool_query_0
                - tool_name
                    - automata-indexer-retrieve-code
                - tool_args
                    - Retrieve the raw code for the function 'run' from the Automata agent, including all necessary imports and docstrings.

            - return_result_0
                - Function 'run' has been added to core.tests.sample_code.test.
        """
    )
    observations = automata_agent._generate_observations(text)
    is_return_result = retrieve_completion_message(observations)

    user_observation_message = generate_user_observation_message(observations)
    assert is_return_result
    expected_observations = textwrap.dedent(
        """-  observations
    - tool_output_0
      - Error: Tool 'automata-indexer-retrieve-code' not found.
    - return_result_0
      - Function 'run' has been added to core.tests.sample_code.test.
        """
    )
    assert user_observation_message.strip() == expected_observations.strip()


def test_extract_actions_7():
    text = textwrap.dedent(
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
        """
    )
    actions = ActionExtractor.extract_actions(text)
    assert actions[0].tool_name == "python-indexer-retrieve-docstring"
    assert actions[0].tool_args == ["core.utils", "calculate_similarity"]

    assert actions[1].tool_name == "python-indexer-retrieve-code"
    assert actions[1].tool_args == ["core.utils", "calculate_similarity"]


def test_generate_observations_0(automata_agent):
    response = textwrap.dedent(
        '''
        Here is the code for the MasterAutomataAgent class, including all necessary imports, docstrings, and comments: class MasterAutomataAgent(AutomataAgent):
            """A master automata agent that works with the coordinater to manipulate other automata agents."""

            def __init__(self, agent_config, *args, **kwargs):
                """Initialize the master automata agent."""
                super().__init__(agent_config, *args, **kwargs)
                self.coordinator = None

            def _setup(self, *args, **kwargs):
                super()._setup(*args, **kwargs)

            def set_coordinator(self, coordinator: 'AgentCoordinator'):
                """Set the coordinator."""
                self.coordinator = coordinator

            def iter_task(self) -> Optional[Tuple[Dict[str, str], Dict[str, str]]]:
                result = super().iter_task()
                lookback_index = -2 if not self.completed else -3
                latest_message = self.messages[lookback_index + 1]
                actions = ActionExtractor.extract_actions(self.messages[lookback_index]['content'])
                observations: Dict[str, str] = {}
                for agent_action in actions:
                    if isinstance(agent_action, AgentAction):
                        if agent_action.agent_name == AutomataAgent.INITIALIZER_DUMMY:
                            continue
                        agent_results = self._execute_agent(agent_action)
                        agent_observations = self._generate_observations(agent_results)
                        self._add_agent_observation(observations, agent_observations, agent_action)
                if len(self.latest_observations) > 0:
                    latest_message['content'] += generate_user_observation_message(observations, include_prefix=False)
                else:
                    latest_message['content'] = generate_user_observation_message(observations, include_prefix=True)
                if self.completed:
                    self._parse_completion_message(latest_message['content'])
                return result

            def _execute_agent(self, agent_action) -> str:
                """Generate the agent result."""
                return self.coordinator.run_agent(agent_action)

            def _add_agent_observation(self, observations: Dict[str, str], agent_observations: Dict[str, str], agent_action: AgentAction) -> None:
                """Generate the agent observations."""
                for observation in agent_observations:
                    agent_observation = observation.replace('return_result_0', agent_action.agent_query.replace('query', 'output'))
                    observations[agent_observation] = agent_observations[observation]

            def _parse_completion_message(self, completion_message: str) -> str:
                """Parse the completion message and replace the tool outputs."""
                super()._parse_completion_message(completion_message)
                outputs = {}
                for message in self.messages:
                    pattern = '-\\s(agent_output_\\d+)\\s+-\\s(.*?)(?=-\\s(agent_output_\\d+)|$)'
                    matches = re.finditer(pattern, message['content'], re.DOTALL)
                    for match in matches:
                        (agent_name, agent_output) = (match.group(1), match.group(2).strip())
                        outputs[agent_name] = agent_output
                for output_name in outputs:
                    completion_message = completion_message.replace(f'{{{output_name}}}', outputs[output_name])
                return completion_message

            @classmethod
            def from_agent(cls, agent: AutomataAgent) -> 'MasterAutomataAgent':
                """Create a master automata agent from an automata agent."""
                master_agent = cls(None)
                master_agent.llm_toolkits = agent.llm_toolkits
                master_agent.instructions = agent.instructions
                master_agent.model = agent.model
                master_agent.initial_payload = agent.initial_payload
                master_agent.config_version = agent.config_version
                master_agent.system_instruction_template = agent.system_instruction_template
                master_agent.instruction_input_variables = agent.instruction_input_variables
                master_agent.stream = agent.stream
                master_agent.verbose = agent.verbose
                master_agent.max_iters = agent.max_iters
                master_agent.temperature = agent.temperature
                master_agent.session_id = agent.session_id
                master_agent.completed = False
                master_agent._setup()
                return master_agent
                
                '''
    )
    observations = automata_agent._generate_observations(response)
    print("observations = ", observations)
    assert False
    # automata_agent = MasterAutomataAgent.from_agent(
    #     automata_agent_builder.with_instruction_version("agent_introduction_dev").build()
    # )

    # # Mock the API response
    # mock_openai_chatcompletion_create.return_value = api_response
    # automata_agent.iter_task()
    # completion_message = automata_agent.messages[-1]["content"]
    # stripped_completion_message = [ele.strip() for ele in completion_message.split("\n")]
    # assert stripped_completion_message[0] == "{agent_query_0}"
