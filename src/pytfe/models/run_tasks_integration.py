"""Run Tasks Integration models for python-tfe.

This module contains models for run tasks integration callback functionality.
"""

from __future__ import annotations

from typing import Any

from .task_result import TaskResultStatus


class TaskResultTag:
    """Tag to enrich outcomes display in TFC/TFE.

    API Documentation:
        https://developer.hashicorp.com/terraform/enterprise/api-docs/run-tasks/run-tasks-integration#severity-and-status-tags
    """

    def __init__(self, label: str, level: str | None = None):
        """Initialize a task result tag.

        Args:
            label: The label for the tag
            level: Optional severity level (error, warning, info)
        """
        self.label = label
        self.level = level

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {"label": self.label}
        if self.level:
            result["level"] = self.level
        return result


class TaskResultOutcome:
    """Detailed run task outcome for improved visibility in TFC/TFE UI.

    API Documentation:
        https://developer.hashicorp.com/terraform/enterprise/api-docs/run-tasks/run-tasks-integration#outcomes-payload-body
    """

    def __init__(
        self,
        outcome_id: str | None = None,
        description: str | None = None,
        body: str | None = None,
        url: str | None = None,
        tags: dict[str, list[TaskResultTag]] | None = None,
    ):
        """Initialize a task result outcome.

        Args:
            outcome_id: Unique identifier for the outcome
            description: Brief description of the outcome
            body: Detailed body content (supports markdown)
            url: URL to view more details
            tags: Dictionary of tag categories to lists of tags
        """
        self.outcome_id = outcome_id
        self.description = description
        self.body = body
        self.url = url
        self.tags = tags or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON:API serialization."""
        result: dict[str, Any] = {"type": "task-result-outcomes", "attributes": {}}

        if self.outcome_id:
            result["attributes"]["outcome-id"] = self.outcome_id
        if self.description:
            result["attributes"]["description"] = self.description
        if self.body:
            result["attributes"]["body"] = self.body
        if self.url:
            result["attributes"]["url"] = self.url
        if self.tags:
            result["attributes"]["tags"] = {
                key: [tag.to_dict() for tag in tags] for key, tags in self.tags.items()
            }

        return result


class TaskResultCallbackOptions:
    """Options for sending task result callback to TFC/TFE.

    API Documentation:
        https://developer.hashicorp.com/terraform/enterprise/api-docs/run-tasks/run-tasks-integration#request-body-1
    """

    def __init__(
        self,
        status: str,
        message: str | None = None,
        url: str | None = None,
        outcomes: list[TaskResultOutcome] | None = None,
    ):
        """Initialize callback options.

        Args:
            status: Task result status (passed, failed, running)
            message: Optional message about the task result
            url: Optional URL to view detailed results
            outcomes: Optional list of detailed outcomes
        """
        self.status = status
        self.message = message
        self.url = url
        self.outcomes = outcomes or []

    def validate(self) -> None:
        """Validate the callback options.

        Only passed, failed, and running statuses are allowed for callbacks.
        pending and errored are not valid callback statuses per TFC/TFE API.

        Raises:
            InvalidTaskResultsCallbackStatus: If status is not valid for callbacks
        """
        from ..errors import InvalidTaskResultsCallbackStatus

        valid_statuses = [
            TaskResultStatus.PASSED.value,
            TaskResultStatus.FAILED.value,
            TaskResultStatus.RUNNING.value,
        ]
        if self.status not in valid_statuses:
            raise InvalidTaskResultsCallbackStatus(
                f"Invalid task result status: {self.status}. "
                f"Must be one of: {', '.join(valid_statuses)}"
            )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON:API format."""
        data: dict[str, Any] = {
            "type": "task-results",
            "attributes": {
                "status": self.status,
            },
        }

        if self.message:
            data["attributes"]["message"] = self.message
        if self.url:
            data["attributes"]["url"] = self.url

        if self.outcomes:
            data["relationships"] = {
                "outcomes": {"data": [outcome.to_dict() for outcome in self.outcomes]}
            }

        return {"data": data}
