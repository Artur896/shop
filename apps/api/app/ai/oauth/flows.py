"""Extension point for a real OAuth2 authorization-code flow between this app and an
AI provider (e.g. an MCP connector that wants to do a standard `/authorize` +
`/token` dance instead of a user manually issuing a token from the Integrations
screen).

Not implemented yet: none of ChatGPT/Claude/Gemini currently offer a public
"connect a third-party app to my chat account" OAuth flow to build against, so
`app.services.integrations_service.connect_integration` issues a scoped AI token
directly (the "Conectar" button in the Integrations screen). When a provider does
expose one, it plugs in here as `begin_authorization(provider, user) -> redirect_url`
and `complete_authorization(provider, code) -> AIToken`, reusing the same
`ai_tokens` table and `app.ai.permissions.scopes` scope set.
"""
