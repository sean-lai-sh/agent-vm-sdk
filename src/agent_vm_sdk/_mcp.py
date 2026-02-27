from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MCPTool:
    """Framework adapters for a VM's MCP endpoint."""

    url: str

    def openai_agents(
        self,
        *,
        name: str = "agent-vm-mcp",
        cache_tools_list: bool = True,
        max_retry_attempts: int = 3,
    ) -> Any:
        """
        Return an MCP server object usable with the OpenAI Agents SDK.

        Example:
            async with vm.mcp_tool.openai_agents() as mcp_server:
                ...
        """
        try:
            from agents.mcp import MCPServerStreamableHttp
        except ImportError as exc:
            raise RuntimeError(
                "OpenAI Agents SDK is not installed. Install with: pip install openai-agents"
            ) from exc

        return MCPServerStreamableHttp(
            name=name,
            params={"url": self.url},
            cache_tools_list=cache_tools_list,
            max_retry_attempts=max_retry_attempts,
        )

    def oai_agent(self, **kwargs: Any) -> Any:
        """Alias for openai_agents()."""
        return self.openai_agents(**kwargs)

    def claude_agent(self, *, name: str = "agent-vm-mcp") -> dict[str, str]:
        """
        Return a generic remote MCP config for Claude Agent style clients.
        """
        return {
            "name": name,
            "type": "url",
            "url": self.url,
        }
