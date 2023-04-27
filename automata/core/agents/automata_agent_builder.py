from typing import Dict, Optional

from automata.configs.agent_configs.config_type import AutomataAgentConfig
from automata.core.base.tool import Toolkit, ToolkitType

from .automata_agent import AutomataAgent


class AutomataAgentBuilder:
    def __init__(self, config: AutomataAgentConfig):
        self._instance = AutomataAgent(config)

    def with_initial_payload(self, initial_payload: Dict[str, str]):
        self._instance.initial_payload = initial_payload
        return self

    def with_llm_toolkits(self, llm_toolkits: Dict[ToolkitType, Toolkit]):
        self._instance.llm_toolkits = llm_toolkits
        return self

    def with_instructions(self, instructions: str):
        self._instance.instructions = instructions
        return self

    def with_model(self, model: str):
        self._instance.model = model
        if model not in AutomataAgentConfig.Config.SUPPORTED_MDOELS:
            raise ValueError(f"Model {model} not found in Supported OpenAI list of models.")
        return self

    def with_stream(self, stream: bool):
        if not isinstance(stream, bool):
            raise ValueError("Stream must be a boolean.")
        self._instance.stream = stream
        return self

    def with_verbose(self, verbose: bool):
        if not isinstance(verbose, bool):
            raise ValueError("Verbose must be a boolean.")
        self._instance.verbose = verbose
        return self

    def with_max_iters(self, max_iters: int):
        if not isinstance(max_iters, int):
            raise ValueError("Max iters must be an integer.")
        self._instance.max_iters = max_iters
        return self

    def with_temperature(self, temperature: float):
        if not isinstance(temperature, float):
            raise ValueError("Temperature iters must be a float.")
        self._instance.temperature = temperature
        return self

    def with_session_id(self, session_id: Optional[str]):
        if session_id and (not isinstance(session_id, str)):
            raise ValueError("Session Id must be a str.")
        self._instance.session_id = session_id
        return self

    def build(self):
        self._instance._setup()
        return self._instance