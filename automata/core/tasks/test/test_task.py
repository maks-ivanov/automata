import os
import shutil
import uuid
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from automata.configs.automata_agent_config_utils import AutomataAgentConfigFactory
from automata.configs.config_enums import AgentConfigName
from automata.core.base.github_manager import RepositoryManager
from automata.core.tasks.automata_task_executor import (
    AutomataExecuteBehavior,
    TaskExecutor,
    TestExecuteBehavior,
)
from automata.core.tasks.automata_task_registry import AutomataTaskRegistry
from automata.core.tasks.task import AutomataTask, TaskStatus


class MockRepositoryManager(RepositoryManager):
    def clone_repository(self, local_path: str):
        pass

    def create_branch(self, branch_name: str):
        pass

    def checkout_branch(self, repo_local_path: str, branch_name: str):
        pass

    def stage_all_changes(self, repo_local_path: str):
        pass

    def commit_and_push_changes(self, repo_local_path: str, branch_name: str, commit_message: str):
        pass

    def create_pull_request(self, branch_name: str, title: str, body: str):
        pass

    def branch_exists(self, branch_name: str) -> bool:
        return False


@pytest.fixture
def task():
    repo_manager = MockRepositoryManager()
    return AutomataTask(
        repo_manager,
        main_config_name=AgentConfigName.TEST.value,
        generate_deterministic_id=False,
        instructions="This is a test.",
    )


@pytest.fixture
def registry(task):
    def mock_get_tasks_by(query, params):
        if params[0] == task.task_id:
            return [task]
        return []

    db = MagicMock()
    repo_manager = MockRepositoryManager()
    db.get_tasks_by.side_effect = mock_get_tasks_by  # Assigning the side_effect attribute
    registry = AutomataTaskRegistry(db, repo_manager)
    return registry


@patch("logging.config.dictConfig")
def test_add_task(task, registry):
    registry._add_task(task)
    assert task.observer is not None


@patch("logging.config.dictConfig", return_value=None)
def test_initialize_task(task, registry):
    registry.initialize_task(task)
    assert task.observer is not None
    assert task.status == TaskStatus.PENDING


@patch.object(AutomataTask, "status", new_callable=PropertyMock)
def test_status_setter(mock_status, task):
    task.status = TaskStatus.RETRYING
    mock_status.assert_called_once_with(TaskStatus.RETRYING)


@patch.object(AutomataTask, "notify_observer")
def test_callback(mock_notify_observer, task, registry):
    registry.initialize_task(task)
    mock_notify_observer.assert_called_once()


class TestURL:
    html_url = "test_url"


def test_commit_task(task, registry, mocker):
    registry.initialize_task(task)
    os.makedirs(task.task_dir, exist_ok=True)
    task.status = TaskStatus.SUCCESS

    registry.github_manager.create_pull_request = MagicMock(return_value=TestURL())
    mocker.spy(registry.github_manager, "create_branch")
    mocker.spy(registry.github_manager, "checkout_branch")
    mocker.spy(registry.github_manager, "stage_all_changes")
    mocker.spy(registry.github_manager, "commit_and_push_changes")
    mocker.spy(registry.github_manager, "create_pull_request")

    registry.commit_task(
        task,
        github_manager=registry.github_manager,
        commit_message="This is a commit message",
        pull_title="This is a test",
        pull_body="I am testing this...",
        pull_branch_name="test_branch__ZZ__",
    )

    registry.github_manager.create_branch.assert_called_once_with("test_branch__ZZ__")
    registry.github_manager.checkout_branch.assert_called_once_with(
        task.task_dir, "test_branch__ZZ__"
    )
    registry.github_manager.stage_all_changes.assert_called_once_with(task.task_dir)
    registry.github_manager.commit_and_push_changes.assert_called_once_with(
        task.task_dir, "test_branch__ZZ__", "This is a commit message"
    )
    registry.github_manager.create_pull_request.assert_called_once_with(
        "test_branch__ZZ__", "This is a test", "I am testing this..."
    )


def test_deterministic_task_id():
    task_1 = AutomataTask(
        test1="arg1",
        test2="arg2",
        priority=5,
        generate_deterministic_id=True,
        main_config=AutomataAgentConfigFactory.create_config(
            main_config_name=AgentConfigName.TEST.value
        ),
        helper_agent_names="test",
        instructions="test1",
    )

    task_2 = AutomataTask(
        test1="arg1",
        test2="arg2",
        priority=5,
        generate_deterministic_id=True,
        main_config=AutomataAgentConfigFactory.create_config(
            main_config_name=AgentConfigName.TEST.value
        ),
        helper_agent_names="test",
        instructions="test1",
    )

    task_3 = AutomataTask(
        test1="arg1",
        test2="arg3",
        priority=5,
        generate_deterministic_id=True,
        main_config=AutomataAgentConfigFactory.create_config(
            main_config_name=AgentConfigName.TEST.value
        ),
        helper_agent_names="test",
        instructions="test1",
    )

    task_4 = AutomataTask(
        test1="arg1",
        test2="arg2",
        priority=5,
        generate_deterministic_id=False,
        main_config=AutomataAgentConfigFactory.create_config(
            main_config_name=AgentConfigName.TEST.value
        ),
        helper_agent_names="test",
        instructions="test1",
    )

    assert task_1.task_id == task_2.task_id
    assert task_1.task_id != task_3.task_id
    assert task_1.task_id != task_4.task_id
    assert isinstance(task_4.task_id, uuid.UUID)


def test_deterministic_vs_non_deterministic_task_id():
    task_1 = AutomataTask(
        MockRepositoryManager(),
        test1="arg1",
        test2="arg2",
        priority=5,
        generate_deterministic_id=True,
        main_config_name=AgentConfigName.TEST.value,
        instructions="test1",
    )

    task_2 = AutomataTask(
        MockRepositoryManager(),
        test1="arg1",
        test2="arg2",
        priority=5,
        generate_deterministic_id=False,
        main_config_name=AgentConfigName.TEST.value,
        instructions="test1",
    )
    assert task_1.task_id != task_2.task_id


@patch("logging.config.dictConfig", return_value=None)
def test_execute_automata_task_success(task, registry):
    registry.initialize_task(task)
    execute_behavior = AutomataExecuteBehavior()
    task_registry = MagicMock()
    task_executor = TaskExecutor(execute_behavior, task_registry)

    task_executor.initialize_task(task)
    task.build_agent_manager.return_value.run.return_value = "Success"

    result = task_executor.execute(task)

    assert task.status == TaskStatus.SUCCESS
    assert task.result == "Success"
    assert result is None


@patch("logging.config.dictConfig", return_value=None)
def test_execute_test_task_success(task):
    execute_behavior = TestExecuteBehavior()
    task_registry = MagicMock()
    task_executor = TaskExecutor(execute_behavior, task_registry)

    task_executor.initialize_task(task)
    task.status = TaskStatus.PENDING
    task.path_to_root_py = "test_path"
    result = task_executor.execute(task)

    assert task.status == TaskStatus.SUCCESS
    assert result is None


@patch("logging.config.dictConfig", return_value=None)
def test_execute_automata_task_fail(task):
    execute_behavior = AutomataExecuteBehavior()
    task_registry = MagicMock()
    task_executor = TaskExecutor(execute_behavior, task_registry)

    task_executor.initialize_task(task)
    task.status = TaskStatus.PENDING
    task.build_agent_manager.return_value.run.side_effect = Exception("Execution failed")
    task.max_retries = 2

    with pytest.raises(Exception, match="Execution failed"):
        task_executor.execute(task)

    assert task.status == TaskStatus.RETRYING
    assert task.error == "Execution failed"
