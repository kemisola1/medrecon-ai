"""
Database models for MedRecon AI agent execution records.

AgentRun stores one execution of an agent within a reconciliation case.
AgentStep stores observable execution milestones such as tool calls,
tool results, decisions, verification outcomes, retries, and human
checkpoints.

These records are intended for reproducibility and auditability.
They must not store hidden chain-of-thought.
"""

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum as SqlEnum
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class AgentRunStatus(str, Enum):
    """
    Lifecycle states for an agent execution.
    """

    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentStepType(str, Enum):
    """
    Observable step categories recorded during agent execution.

    TOOL_CALL:
        The agent requested an external or internal tool.

    TOOL_RESULT:
        A tool returned a result.

    DECISION:
        A concise structured decision or rationale.

    VERIFICATION:
        A verification outcome was recorded.

    RETRY:
        The agent retried after a recoverable problem.

    HUMAN_CHECKPOINT:
        The workflow reached a point requiring human review.
    """

    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    DECISION = "decision"
    VERIFICATION = "verification"
    RETRY = "retry"
    HUMAN_CHECKPOINT = "human_checkpoint"


class AgentRun(TimestampMixin, Base):
    """
    Store one execution of a MedRecon agent.

    Why this exists:
        MedRecon AI uses multiple specialized agents. Each execution
        should be traceable so developers and reviewers can determine
        what ran, whether it succeeded, and what artifacts it produced.

    Fields:
        id:
            Unique execution identifier.

        case_id:
            Reconciliation case associated with the execution.

        agent_name:
            Human-readable name of the agent.

        status:
            Current execution status.

        started_at:
            Timestamp when execution began.

        completed_at:
            Timestamp when execution finished, when applicable.

        input_reference:
            Optional reference to structured input or stored artifact.

        output_reference:
            Optional reference to structured output or stored artifact.

        retry_count:
            Number of retry attempts performed.

    Safety:
        AgentRun is an audit record only. It must not store secret keys,
        raw credentials, or hidden model chain-of-thought.
    """

    __tablename__ = "agent_runs"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    case_id: Mapped[UUID] = mapped_column(
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    agent_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )

    status: Mapped[AgentRunStatus] = mapped_column(
        SqlEnum(
            AgentRunStatus,
            name="agent_run_status",
            native_enum=False,
        ),
        default=AgentRunStatus.RUNNING,
        nullable=False,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    input_reference: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    output_reference: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )


class AgentStep(TimestampMixin, Base):
    """
    Store one observable execution step inside an AgentRun.

    Why this exists:
        A single success/failure record is not enough for reproducibility.
        MedRecon needs a safe trajectory showing important workflow events.

    Important:
        This table stores concise observable actions and outcomes only.
        It must not store hidden chain-of-thought or unrestricted internal
        reasoning text.

    Fields:
        id:
            Unique step identifier.

        run_id:
            AgentRun this step belongs to.

        step_type:
            Category of observable execution event.

        action:
            Concise description of what happened.

        result:
            Optional structured or concise result summary.

        sequence_number:
            Order of this step within the run.
    """

    __tablename__ = "agent_steps"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    run_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    step_type: Mapped[AgentStepType] = mapped_column(
        SqlEnum(
            AgentStepType,
            name="agent_step_type",
            native_enum=False,
        ),
        nullable=False,
    )

    action: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    result: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    sequence_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )