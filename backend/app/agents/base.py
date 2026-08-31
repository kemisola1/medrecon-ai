"""
Shared agent framework for MedRecon AI.

Why this module exists:
    MedRecon AI uses multiple specialized agents rather than one large
    undifferentiated reasoning step.

    Each agent performs a narrow medication-reconciliation responsibility
    and produces observable structured outputs.

    A shared base framework gives all agents consistent behavior for:
        execution
        status reporting
        trajectory logging
        errors
        timestamps
        structured outputs

Important:
    Agent trajectories store observable decisions, tool calls, outputs,
    verification results, retries, and human-review checkpoints.

    They must never store or expose hidden chain-of-thought reasoning.

Safety:
    Agents may analyze medication information and surface findings for
    qualified human review.

    Agents must not prescribe medications, discontinue medications,
    change medication orders, diagnose conditions, or autonomously take
    clinical action.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class AgentExecutionStatus(str, Enum):
    """
    High-level execution state for an agent run.
    """

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"


class AgentStepType(str, Enum):
    """
    Types of observable trajectory events.

    These describe what happened without exposing private internal
    reasoning.
    """

    INPUT_RECEIVED = "input_received"
    DECISION = "decision"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    VALIDATION = "validation"
    RETRY = "retry"
    OUTPUT_CREATED = "output_created"
    HUMAN_CHECKPOINT = "human_checkpoint"
    ERROR = "error"


class AgentStep(BaseModel):
    """
    One observable step in an agent trajectory.

    Why:
        The hackathon requires representative trajectories showing
        instructions, tool responses, retries, and human checkpoints.

    Important:
        The message should describe concise observable behavior only.
        It must not contain hidden chain-of-thought.
    """

    step_id: str = Field(
        default_factory=lambda: str(
            uuid4()
        )
    )

    step_type: AgentStepType

    message: str

    data: dict[str, Any] = Field(
        default_factory=dict
    )

    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )


class AgentResult(BaseModel):
    """
    Standard result returned by every MedRecon agent.

    Attributes:
        agent_name:
            Human-readable agent identifier.

        run_id:
            Unique execution identifier.

        status:
            Final execution status.

        output:
            Structured agent result.

        steps:
            Observable trajectory events.

        error:
            Safe error description when execution fails.

        started_at:
            Agent start time.

        completed_at:
            Agent completion time.
    """

    agent_name: str

    run_id: str

    status: AgentExecutionStatus

    output: dict[str, Any] = Field(
        default_factory=dict
    )

    steps: list[AgentStep] = Field(
        default_factory=list
    )

    error: str | None = None

    started_at: datetime

    completed_at: datetime | None = None


class BaseAgent(ABC):
    """
    Abstract base class for all MedRecon AI agents.

    Why:
        Every specialized agent should follow the same observable execution
        pattern so orchestration, evaluation, debugging, and trajectory
        recording remain consistent.

    Subclasses implement:
        agent_name
        process()

    The public run() method handles:
        run creation
        trajectory initialization
        execution
        completion
        safe error handling
    """

    agent_name: str = "base_agent"

    def __init__(self) -> None:
        """
        Initialize a new agent instance.
        """
        self._steps: list[
            AgentStep
        ] = []

        self._run_id: str = ""

    def record_step(
        self,
        step_type: AgentStepType,
        message: str,
        data: dict[str, Any] | None = None,
    ) -> None:
        """
        Record an observable trajectory event.

        Args:
            step_type:
                Category of the event.

            message:
                Concise explanation of what happened.

            data:
                Optional structured metadata.

        Safety:
            Do not place private reasoning or hidden chain-of-thought in
            trajectory messages or metadata.
        """
        step = AgentStep(
            step_type=step_type,
            message=message,
            data=data or {},
        )

        self._steps.append(
            step
        )

    @abstractmethod
    def process(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute the specialized agent task.

        Args:
            payload:
                Structured input provided by the orchestrator.

        Returns:
            Structured output dictionary.

        Subclasses must implement this method.
        """
        raise NotImplementedError

    def run(
        self,
        payload: dict[str, Any],
    ) -> AgentResult:
        """
        Execute the agent and return a standardized result.

        Args:
            payload:
                Structured agent input.

        Returns:
            AgentResult containing output and trajectory.

        Failure behavior:
            Exceptions are captured and returned as a FAILED result rather
            than silently ignored.

            The orchestrator can later decide whether a retry or human
            review is appropriate.
        """
        self._run_id = str(
            uuid4()
        )

        self._steps = []

        started_at = datetime.now(
            timezone.utc
        )

        self.record_step(
            AgentStepType.INPUT_RECEIVED,
            "Agent input received.",
            {
                "input_keys": list(
                    payload.keys()
                )
            },
        )

        try:
            self.record_step(
                AgentStepType.DECISION,
                (
                    f"{self.agent_name} started its "
                    "specialized processing task."
                ),
            )

            output = self.process(
                payload
            )

            self.record_step(
                AgentStepType.OUTPUT_CREATED,
                "Agent produced structured output.",
                {
                    "output_keys": list(
                        output.keys()
                    )
                },
            )

            completed_at = datetime.now(
                timezone.utc
            )

            return AgentResult(
                agent_name=self.agent_name,
                run_id=self._run_id,
                status=(
                    AgentExecutionStatus.COMPLETED
                ),
                output=output,
                steps=self._steps,
                started_at=started_at,
                completed_at=completed_at,
            )

        except Exception as exc:
            self.record_step(
                AgentStepType.ERROR,
                "Agent execution failed.",
                {
                    "error_type": (
                        type(exc).__name__
                    )
                },
            )

            completed_at = datetime.now(
                timezone.utc
            )

            return AgentResult(
                agent_name=self.agent_name,
                run_id=self._run_id,
                status=(
                    AgentExecutionStatus.FAILED
                ),
                output={},
                steps=self._steps,
                error=str(
                    exc
                ),
                started_at=started_at,
                completed_at=completed_at,
            )
