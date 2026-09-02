"""Metadata about each external AI assistant the app knows how to connect to.

This is the *only* file that should ever need a new entry when a new assistant is
supported (see section 3 of the product brief: the app is the platform, assistants
are interchangeable clients of it). Nothing in lists_service, items_service, or
users_service imports from `app.ai` at all — the dependency only goes one direction.
"""

from dataclasses import dataclass

from app.models.enums import AIProvider


@dataclass(frozen=True)
class ProviderInfo:
    provider: AIProvider
    display_name: str
    connect_method: str  # how a user actually authorizes this provider today


PROVIDERS: dict[AIProvider, ProviderInfo] = {
    AIProvider.CHATGPT: ProviderInfo(
        AIProvider.CHATGPT, "ChatGPT", "Custom GPT Action / MCP connector using an issued AI token"
    ),
    AIProvider.CLAUDE: ProviderInfo(
        AIProvider.CLAUDE, "Claude", "MCP server connection using an issued AI token"
    ),
    AIProvider.GEMINI: ProviderInfo(
        AIProvider.GEMINI, "Gemini", "Extension / function-calling tool using an issued AI token"
    ),
}
