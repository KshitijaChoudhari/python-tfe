"""Task Stage models for python-tfe.

This module contains models related to task stages in Terraform Cloud/Enterprise.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from .policy_evaluation import PolicyEvaluation
    from .run import Run
    from .task_result import TaskResult


class Stage(str, Enum):
    """Enum representing possible run stages for run tasks."""
    
    PRE_PLAN = "pre-plan"
    POST_PLAN = "post-plan"
    PRE_APPLY = "pre-apply"
    POST_APPLY = "post-apply"


class TaskStageStatus(str, Enum):
    """Enum representing all possible statuses for a task stage."""
    
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    AWAITING_OVERRIDE = "awaiting_override"
    CANCELED = "canceled"
    ERRORED = "errored"
    UNREACHABLE = "unreachable"


class Permissions(BaseModel):
    """Permission types for overriding a task stage."""
    
    can_override_policy: bool | None = Field(default=None, alias="can-override-policy")
    can_override_tasks: bool | None = Field(default=None, alias="can-override-tasks")
    can_override: bool | None = Field(default=None, alias="can-override")
    
    model_config = ConfigDict(populate_by_name=True)


class Actions(BaseModel):
    """Task stage actions."""
    
    is_overridable: bool | None = Field(default=None, alias="is-overridable")
    
    model_config = ConfigDict(populate_by_name=True)


class TaskStageStatusTimestamps(BaseModel):
    """Timestamps recorded for a task stage."""
    
    errored_at: datetime | None = Field(default=None, alias="errored-at")
    running_at: datetime | None = Field(default=None, alias="running-at")
    canceled_at: datetime | None = Field(default=None, alias="canceled-at")
    failed_at: datetime | None = Field(default=None, alias="failed-at")
    passed_at: datetime | None = Field(default=None, alias="passed-at")
    
    model_config = ConfigDict(populate_by_name=True)


class TaskStage(BaseModel):
    """Represents a HCP Terraform or Terraform Enterprise run's task stage.
    
    Task stages are where run tasks can occur during a run lifecycle.
    
    API Documentation:
        https://developer.hashicorp.com/terraform/cloud-docs/api-docs/task-stages
    """
    
    id: str
    stage: Stage
    status: TaskStageStatus
    status_timestamps: TaskStageStatusTimestamps = Field(alias="status-timestamps")
    created_at: datetime = Field(alias="created-at")
    updated_at: datetime = Field(alias="updated-at")
    permissions: Permissions | None = None
    actions: Actions | None = None
    
    # Relationships
    run: Run | None = None
    task_results: list[TaskResult] = Field(default_factory=list, alias="task-results")
    policy_evaluations: list[PolicyEvaluation] = Field(
        default_factory=list, 
        alias="policy-evaluations"
    )
    
    model_config = ConfigDict(populate_by_name=True)


class TaskStageOverrideOptions(BaseModel):
    """Options for overriding a task stage."""
    
    comment: str | None = None


class TaskStageReadOptions(BaseModel):
    """Options for reading a task stage."""
    
    include: list[str] | None = None


class TaskStageListOptions(BaseModel):
    """Options for listing task stages."""
    
    page_number: int | None = Field(default=None, alias="page[number]")
    page_size: int | None = Field(default=None, alias="page[size]")
    
    model_config = ConfigDict(populate_by_name=True)
