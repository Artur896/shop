import enum


class ListRole(str, enum.Enum):
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"


class MemberStatus(str, enum.Enum):
    ACTIVE = "active"
    REMOVED = "removed"


class InvitationStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class NotificationType(str, enum.Enum):
    LIST_INVITATION = "LIST_INVITATION"
    INVITATION_ACCEPTED = "INVITATION_ACCEPTED"
    LIST_SHARED = "LIST_SHARED"
    MEMBER_ADDED = "MEMBER_ADDED"
    MEMBER_REMOVED = "MEMBER_REMOVED"
    ITEM_ADDED = "ITEM_ADDED"
    ITEM_COMPLETED = "ITEM_COMPLETED"


class AIProvider(str, enum.Enum):
    CHATGPT = "chatgpt"
    CLAUDE = "claude"
    GEMINI = "gemini"


class AIIntegrationStatus(str, enum.Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"


class ActorType(str, enum.Enum):
    USER = "user"
    AI = "ai"
    SYSTEM = "system"


class AuditResult(str, enum.Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    DENIED = "denied"
