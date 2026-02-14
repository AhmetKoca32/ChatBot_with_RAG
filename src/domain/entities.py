"""Domain entities - pure business objects."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Role(str, Enum):
    """Message role in a conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass(frozen=True)
class Message:
    """Immutable message entity."""
    content: str
    role: Role
    created_at: datetime | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "created_at", self.created_at or datetime.utcnow())


@dataclass
class ConversationTurn:
    """Single turn in a conversation (user input + agent response)."""
    user_message: Message
    assistant_message: Message | None = None
