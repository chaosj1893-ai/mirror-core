"""Data models for MirrorCore persona system."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class SoulData:
    """Soul layer: who I am."""

    version: str
    created_at: datetime
    updated_at: datetime
    identity: dict[str, str]
    values: list[str]
    language_style: dict[str, str]
    decision_patterns: list[str]


@dataclass
class FacultyData:
    """Faculty layer: what I know how to do."""

    domain: str
    version: str
    last_updated: datetime
    frameworks: dict[str, str]
    case_refs: list[str] = field(default_factory=list)


@dataclass
class Memory:
    """A single knowledge chunk in the Body layer."""

    content: str
    type: str  # "case" | "document" | "conversation"
    domain: str
    timestamp: datetime
    version: str
    tags: list[str]
    confidence: float
    source: str


@dataclass
class PersonaVersion:
    """A snapshot of the persona at a point in time."""

    version: str
    timestamp: datetime
    soul_snapshot: str
    faculty_diff: dict[str, str]
    body_additions: list[str]
    changelog: str


@dataclass
class VersionDiff:
    """Diff between two persona versions."""

    v1: str
    v2: str
    soul_changes: list[str]
    faculty_changes: dict[str, list[str]]
    body_changes_count: int
    summary: str


@dataclass
class ReasoningTrace:
    """GlassBox reasoning trace for a single response."""

    intent: str
    activated_layers: list[str]
    thinking_process: list[str]
    sources: list[dict[str, Any]]
    confidence_level: str  # "high" | "medium" | "low"
    speculation_parts: list[str]


@dataclass
class Response:
    """Structured response with reasoning trace."""

    content: str
    reasoning: ReasoningTrace
