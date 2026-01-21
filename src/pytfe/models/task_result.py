"""Task Result models for python-tfe.

This module contains models related to task results in Terraform Cloud/Enterprise.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from .task_stages import TaskStage


class TaskResultStatus(str, Enum):
    """Task result status enum."""

    PASSED = "passed"
    FAILED = "failed"
    PENDING = "pending"
    RUNNING = "running"
    UNREACHABLE = "unreachable"
    ERRORED = "errored"


class TaskEnforcementLevel(str, Enum):
    """Task enforcement level enum."""

    ADVISORY = "advisory"
    MANDATORY = "mandatory"


class TaskResultStatusTimestamps(BaseModel):
    """Timestamps recorded for a task result."""

    errored_at: datetime | None = Field(default=None, alias="errored-at")
    running_at: datetime | None = Field(default=None, alias="running-at")
    canceled_at: datetime | None = Field(default=None, alias="canceled-at")
    failed_at: datetime | None = Field(default=None, alias="failed-at")
    passed_at: datetime | None = Field(default=None, alias="passed-at")

    model_config = ConfigDict(populate_by_name=True)


class TaskResult(BaseModel):
    """Represents a HCP Terraform or Terraform Enterprise run task result.

    API Documentation:
        https://developer.hashicorp.com/terraform/cloud-docs/api-docs/task-results
    """

    id: str
    status: TaskResultStatus
    message: str
    status_timestamps: TaskResultStatusTimestamps = Field(alias="status-timestamps")
    url: str
    created_at: datetime = Field(alias="created-at")
    updated_at: datetime = Field(alias="updated-at")
    task_id: str = Field(alias="task-id")
    task_name: str = Field(alias="task-name")
    task_url: str = Field(alias="task-url")
    workspace_task_id: str = Field(alias="workspace-task-id")
    workspace_task_enforcement_level: TaskEnforcementLevel = Field(
        alias="workspace-task-enforcement-level"
    )
    agent_pool_id: str | None = Field(default=None, alias="agent-pool-id")

    # Relationships
    task_stage: TaskStage | None = Field(default=None, alias="task-stage")

    model_config = ConfigDict(populate_by_name=True)
