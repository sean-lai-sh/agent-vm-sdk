from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ._mcp import MCPTool

if TYPE_CHECKING:
    from ._client import AgentVMClient


@dataclass
class VMConfig:
    image: str = "agent-vm-base"
    preset_slug: str = "micro"


@dataclass
class VM:
    vm_id: str
    account_id: str
    user_id: str
    image: str
    preset_slug: str
    vcpu: float
    memory_mb: int
    disk_gb: int
    mcp_url: str
    status: str
    created_at: float
    last_active_at: float

    _client: AgentVMClient | None = field(default=None, repr=False, compare=False)
    _owns_client: bool = field(default=False, repr=False, compare=False)

    @property
    def mcp_tool(self) -> MCPTool:
        return MCPTool(url=self.mcp_url)

    @property
    def mcp_oai_agent(self) -> Any:
        return self.mcp_tool.openai_agents()

    @property
    def mcp_claude_config(self) -> dict[str, str]:
        return self.mcp_tool.claude_agent()

    def destroy(self) -> None:
        if self._client:
            self._client.destroy_vm(self.vm_id)
            self.status = "stopped"
            if self._owns_client:
                self._client.close()
                self._client = None

    def __enter__(self) -> VM:
        return self

    def __exit__(self, *exc: object) -> None:
        self.destroy()
