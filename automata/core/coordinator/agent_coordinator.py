from typing import Dict, List, Optional

from pydantic import BaseModel

from automata.configs.config_types import AutomataAgentConfig
from automata.core.agents.automata_agent import MasterAutomataAgent
from automata.core.agents.automata_agent_builder import AutomataAgentBuilder
from automata.core.agents.automata_agent_helpers import AgentAction
from automata.core.base.tool import Toolkit, ToolkitType


class AgentInstance(BaseModel):
    name: str = ""
    description: str = ""
    config: AutomataAgentConfig = AutomataAgentConfig()
    builder: AutomataAgentBuilder = AutomataAgentBuilder(config=config)
    llm_toolkits: Optional[Dict[ToolkitType, Toolkit]] = None

    def run(self, instructions):
        agent = self.builder(config=self.config)
        if self.llm_toolkits:
            agent = agent.with_llm_toolkits(self.llm_toolkits)
        agent = agent.with_instructions(instructions).build()
        result = agent.run()
        del agent
        return result

    class Config:
        arbitrary_types_allowed = True


class AgentCoordinator:
    def __init__(self):
        self.agent_instances: List[AgentInstance] = []

    def add_agent_instance(self, agent_instance):
        # Check agent has not already been added via name field
        if agent_instance.name in [ele.name for ele in self.agent_instances]:
            raise ValueError("Agent already exists.")
        self.agent_instances.append(agent_instance)

    def remove_agent_instance(self, agent_name):
        # Check agent has already been added via name field
        if agent_name not in [ele.name for ele in self.agent_instances]:
            raise ValueError("Agent does not exist.")
        self.agent_instances = [
            instance for instance in self.agent_instances if instance.name != agent_name
        ]

    def set_master_agent(self, master_agent: MasterAutomataAgent):
        self.master_agent = master_agent

    def run_agent(self, action: AgentAction) -> str:
        # Run the selected agent and return the result
        try:
            agent_instance = self._select_agent_instance(action.agent_name)
            return agent_instance.run(action.agent_instruction)
        except Exception as e:
            return str("Execution fail with error: " + str(e))

    def build_agent_message(self) -> str:
        """Builds a message containing all agents and their descriptions."""
        return "".join(
            [f"\n{agent.name}: {agent.description}\n" for agent in self.agent_instances]
        )

    def _select_agent_instance(self, agent_name) -> AgentInstance:
        """Selects an agent instance by name."""
        for agent in self.agent_instances:
            if agent.name == agent_name:
                return agent
        raise ValueError("Agent does not exist.")
