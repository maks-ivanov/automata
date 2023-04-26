"""
    AutomataAgent is an autonomous agent that performs the actual work of the Automata
    system. Automata are responsible for executing instructions and reporting
    the results back to the master.

    Example:

        llm_toolkits = build_llm_toolkits(tools_list, **inputs)

        config_version = AutomataConfigVersion.AUTOMATA_MASTER_PROD
        agent_config = AutomataAgentConfig.load(config_version)
        agent = (AutomataAgentBuilder(agent_config)
            .with_llm_toolkits(llm_toolkits)
            .with_instructions(instructions)
            .with_model(model)
            .build())

        agent.run()

        TODO - Add error checking to ensure that we don't terminate when
               our previous result returned an error

        TODO - Think about approach behind retrieve_completion_message
             - Right now, the job terminates when we get our first completion message
               e.g. return_result_0
               The correct thing to do would be to ensure we complete all tasks
               But before adding this cpability, we need to continue
               polishing the framework

        TODO - Think about how to introduce the starting instructions to configs
"""
import logging
import sqlite3
import textwrap
import uuid
from typing import Dict, Final, List, Optional, Tuple, cast

import openai
from termcolor import colored
from transformers import GPT2Tokenizer

from automata.config import CONVERSATION_DB_NAME, OPENAI_API_KEY
from automata.configs.agent_configs.config_type import AutomataAgentConfig
from automata.core.agents.automata_agent_helpers import (
    ActionExtractor,
    generate_user_observation_message,
    retrieve_completion_message,
)

logger = logging.getLogger(__name__)


class AutomataAgent:
    """
    AutomataAgent is an autonomous agent that performs the actual work of the Automata
    system. Automata are responsible for executing instructions and reporting
    the results back to the master.
    """

    CONTINUE_MESSAGE: Final = "Continue, and return a result JSON when finished."
    NUM_DEFAULT_MESSAGES: Final = 3  # Prompt + Assistant Initialization + User Task
    INITIALIZER_DUMMY_TOOL: Final = "automata-initializer"
    ERROR_DUMMY_TOOL: Final = "error-reporter"

    def __init__(self, config: Optional[AutomataAgentConfig] = None):
        """
        Args:
            config_version (Optional[AutomataAgentConfig]): The config_version of the agent to use.
        Methods:
            iter_task(instructions: List[Dict[str, str]]) -> Dict[str, str]: Iterates through the instructions and returns the next instruction.
            modify_last_instruction(new_instruction: str) -> None
            replay_messages() -> List[Dict[str, str]]: Replays agent messages buffer.
            run() -> str: Runs the agent.
        """
        if config is None:
            config = AutomataAgentConfig()
        self.initial_payload = config.initial_payload
        self.llm_toolkits = config.llm_toolkits
        self.instructions = config.instructions
        self.config_version = config.config_version
        self.instruction_template = config.instruction_template
        self.instruction_input_variables = config.instruction_input_variables
        self.model = config.model
        self.stream = config.stream
        self.verbose = config.verbose
        self.max_iters = config.max_iters
        self.temperature = config.temperature
        self.session_id = config.session_id
        self.completed = False
        self.name = config.name

    def __del__(self):
        """Close the connection to the agent."""
        if hasattr(self, "conn"):
            self.conn.close()

    def run(self) -> str:
        latest_responses = self.iter_task()
        while latest_responses is not None:
            # Each iteration adds two messages, one from the assistant and one from the user
            # If we have equal to or more than 2 * max_iters messages (less the default messages),
            # then we have exceeded the max_iters
            if len(self.messages) - AutomataAgent.NUM_DEFAULT_MESSAGES >= self.max_iters * 2:
                return "Result was not found before iterations exceeded max limit."
            latest_responses = self.iter_task()
        return self.messages[-1]["content"]

    def iter_task(self) -> Optional[Tuple[Dict[str, str], Dict[str, str]]]:
        """Run the test and report the tool outputs back to the master."""
        if self.completed:
            raise ValueError("Cannot run an agent that has already completed.")
        context_length = sum(
            [
                len(
                    self.tokenizer.encode(message["content"], max_length=1024 * 8, truncation=True)
                )
                for message in self.messages
            ]
        )
        logger.debug("Chat Context length: %s", context_length)
        logger.debug("-" * 60)
        # logger.info("Running instruction...")
        response_summary = openai.ChatCompletion.create(
            model=self.model,
            messages=self.messages,
            temperature=0.01,
            stream=self.stream,
        )
        if self.stream:
            print(colored(f"\n>>> {self.name} Agent:", "green"))
            latest_accumulation = ""
            stream_separator = " "
            response_text = ""
            for chunk in response_summary:
                if "content" in chunk["choices"][0]["delta"]:
                    chunk_content = chunk["choices"][0]["delta"]["content"]
                    latest_accumulation += chunk_content
                    response_text += chunk_content
                    latest_accumulation = latest_accumulation.replace("\\n", "\n")
                if stream_separator in latest_accumulation:
                    words = latest_accumulation.split(stream_separator)
                    for word in words[:-1]:
                        attrs = (
                            ["bold"]
                            if any(
                                keyword in word
                                for keyword in ["thoughts", "actions", "observations"]
                            )
                            else []
                        )
                        print(colored(word, "green", attrs=attrs), end=" ", flush=True)
                    latest_accumulation = words[-1]
            print(colored(str(latest_accumulation), "green"))
        else:
            response_text = response_summary["choices"][0]["message"]["content"]
        logger.debug("OpenAI Response:\n%s\n" % response_text)
        assistant_message = {"role": "assistant", "content": response_text}

        responses: List[Dict[str, str]] = []
        responses.append(assistant_message)
        self._save_interaction(assistant_message)

        observations = self._generate_observations(response_text)
        completion_message = retrieve_completion_message(observations)

        if completion_message:
            self.completed = True
            self._save_interaction({"role": "assistant", "content": completion_message})
            return None
        if len(observations) > 0:
            user_observation_message = generate_user_observation_message(observations)
            user_message = {"role": "user", "content": user_observation_message}
            logger.debug("Synthetic User Message:\n%s\n" % user_observation_message)
        else:
            user_message = {"role": "user", "content": AutomataAgent.CONTINUE_MESSAGE}
            logger.debug("Synthetic User Message:\n%s\n" % AutomataAgent.CONTINUE_MESSAGE)
        responses.append(user_message)
        self._save_interaction(user_message)
        return (assistant_message, user_message)

    def replay_messages(self) -> str:
        """Replay the messages in the conversation."""
        if len(self.messages) == 0:
            logger.debug("No messages to replay.")
            return "No messages to replay."
        for message in self.messages[1:]:
            observations = self._generate_observations(message["content"])
            completion_message = retrieve_completion_message(observations)
            if completion_message:
                return completion_message
            logger.debug("Role:\n%s\n\nMessage:\n%s\n" % (message["role"], message["content"]))
            logger.debug("Processing message content =  %s" % message["content"])
            logger.debug("\nProcessed Outputs:\n%s\n" % observations)
            logger.debug("-" * 60)
        return "No completion message found."

    def modify_last_instruction(self, new_instruction: str) -> None:
        """Extend the last instructions with a new message."""
        previous_message = self.messages[-1]
        self.messages[-1] = {"role": previous_message["role"], "content": f"{new_instruction}"}

    def _setup(self):
        """Setup the agent."""
        openai.api_key = OPENAI_API_KEY
        self.messages = []
        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        if "tools" in self.instruction_input_variables:
            self.initial_payload["tools"] = self._build_tool_message()

        prompt = self._load_prompt()
        self._init_database()
        if self.session_id:
            self._load_previous_interactions()
        else:
            self.session_id = str(uuid.uuid4())
            self._save_interaction({"role": "system", "content": prompt})
            initial_messages = [
                {
                    "role": "assistant",
                    "content": textwrap.dedent(
                        """
                        - thoughts
                          - I will begin by initializing myself.
                            - actions
                              - tool_query_0
                                - tool_name
                                  - {AutomataAgent.INITIALIZER_DUMMY_TOOL}
                                - tool_args
                                  - Hello, I am Automata, OpenAI's most skilled coding system. How may I assist you today?
                        """
                    ),
                },
                {
                    "role": "user",
                    "content": textwrap.dedent(
                        f"""
                        - observation:
                          - task_0                            
                            - Please carry out the following instruction {self.instructions}.
                        """
                    ),
                },
            ]
            for message in initial_messages:
                self._save_interaction(message)
        logger.debug("Initializing with Prompt:%s\n" % prompt)
        logger.debug("-" * 60)
        if set(self.instruction_input_variables) != set(list(self.initial_payload.keys())):
            raise ValueError(f"Initial payload does not match instruction_input_variables.")
        logger.debug("Session ID: %s" % self.session_id)
        logger.debug("-" * 60)

    def _load_prompt(self) -> str:
        """Load the prompt from a config_version specified at initialization."""
        prompt = self.instruction_template
        for arg in self.instruction_input_variables:
            prompt = prompt.replace(f"{{{arg}}}", self.initial_payload[arg])
        return prompt

    def _generate_observations(self, response_text: str) -> Dict[str, str]:
        """Process the messages in the conversation."""
        actions = ActionExtractor.extract_actions(response_text)
        logger.debug("Actions: %s" % actions)
        outputs = {}
        (result_counter, tool_counter) = (0, 0)
        for action_request in actions:
            (tool_name, tool_input) = (
                action_request[ActionExtractor.TOOL_NAME_FIELD],
                action_request[ActionExtractor.TOOL_ARGS_FIELD] or "",
            )
            if tool_name == AutomataAgent.INITIALIZER_DUMMY_TOOL:
                continue
            if ActionExtractor.RETURN_RESULT_INDICATOR in tool_name:
                outputs[
                    "%s_%i" % (ActionExtractor.RETURN_RESULT_INDICATOR, result_counter)
                ] = "\n".join(tool_input)
                result_counter += 1
                continue
            if tool_name == AutomataAgent.ERROR_DUMMY_TOOL:
                tool_output = tool_input
                outputs["%s_%i" % ("output", tool_counter)] = cast(str, tool_output)
                tool_counter += 1
            else:
                tool_found = False
                for toolkit in self.llm_toolkits.values():
                    for tool in toolkit.tools:
                        if tool.name == tool_name:
                            processed_tool_input = [
                                ele if ele != "None" else None for ele in tool_input
                            ]
                            tool_output = tool.run(tuple(processed_tool_input), verbose=False)
                            outputs["%s_%i" % ("output", tool_counter)] = cast(str, tool_output)
                            tool_counter += 1
                            tool_found = True
                            break
                    if tool_found:
                        break
                if not tool_found:
                    error_message = f"Error: Tool '{tool_name}' not found."
                    outputs["%s_%i" % ("output", tool_counter)] = error_message
                    tool_counter += 1
        return outputs

    def _init_database(self):
        """Initialize the database connection."""
        self.conn = sqlite3.connect(CONVERSATION_DB_NAME)
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "\n            CREATE TABLE IF NOT EXISTS interactions (\n                session_id INTEGER,\n                interaction_id INTEGER,\n                role TEXT,\n                content TEXT,\n                PRIMARY KEY (session_id, interaction_id)\n            )\n            "
        )
        self.conn.commit()

    def _save_interaction(self, interaction: Dict[str, str]):
        """Save the interaction to the database."""
        interaction_id = len(self.messages)
        role = interaction["role"]
        content = interaction["content"]
        self.cursor.execute(
            "INSERT INTO interactions (session_id, interaction_id, role, content) VALUES (?, ?, ?, ?)",
            (self.session_id, interaction_id, role, content),
        )
        self.conn.commit()
        self.messages.append(interaction)

    def _load_previous_interactions(self):
        """Load the previous interactions from the database."""
        self.cursor.execute(
            "SELECT role, content FROM interactions WHERE session_id = ? ORDER BY interaction_id ASC",
            (self.session_id,),
        )
        self.messages = [
            {"role": role, "content": content} for (role, content) in self.cursor.fetchall()
        ]

    def _build_tool_message(self):
        """Builds a message containing all tools and their descriptions."""
        return "".join(
            [
                f"\n{tool.name}: {tool.description}\n"
                for toolkit in self.llm_toolkits.values()
                for tool in toolkit.tools
            ]
        )
