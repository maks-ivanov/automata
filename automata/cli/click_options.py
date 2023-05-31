import click

from automata.configs.config_enums import AgentConfigName


def common_options(command: click.Command, *args, **kwargs) -> click.Command:
    options = [
        click.option("--instructions", type=str, help="The initial instructions for the agent."),
        click.option(
            "--model", type=str, default="gpt-4", help="What model to use across the framework?"
        ),
        click.option("--session_id", type=str, help="The session id for the agent."),
        click.option(
            "--llm_toolkits",
            type=str,
            default="python_retriever,python_writer",
            help="Comma-separated list of toolkits to be used main agent.",
        ),
        click.option(
            "--main_config_name",
            type=str,
            default=AgentConfigName.AUTOMATA_MAIN_DEV.value,
            help="The config version of the agent.",
        ),
        click.option(
            "--helper_agent_names",
            type=str,
            default=f"{AgentConfigName.AUTOMATA_INDEXER_DEV.value},{AgentConfigName.AUTOMATA_WRITER_DEV.value}",
            help="The config version of the agent.",
        ),
        click.option("--stream", type=bool, default=True, help="Should we stream the responses?"),
        click.option(
            "-v",
            "--verbose",
            type=bool,
            is_flag=True,
            help="Execute script in verbose mode?",
        ),
    ]
    for option in reversed(options):
        command = option(command)
    return command
