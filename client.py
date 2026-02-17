from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class VMConfig:
    image: str = "agent-vm-base"
    preset_slug: str = "micro"


@dataclass(frozen=True)
class MCPTool:
    """Framework adapters for this VM's MCP endpoint."""

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
        except ImportError as exc:  # pragma: no cover - depends on runtime extras
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

        This is intentionally transport-level and can be mapped to specific SDK
        config shapes if needed.
        """
        return {
            "name": name,
            "type": "url",
            "url": self.url,
        }


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

    _client: AgentVMClient | None = None
    _owns_client: bool = False

    @property
    def mcp_tool(self) -> MCPTool:
        return MCPTool(url=self.mcp_url)

    @property
    def mcp_oai_agent(self) -> Any:
        """Direct OpenAI Agents SDK adapter."""
        return self.mcp_tool.openai_agents()

    @property
    def mcp_claude_config(self) -> dict[str, str]:
        """Direct Claude-style remote MCP config."""
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

    def __exit__(self, *exc) -> None:
        self.destroy()


class AgentVMClient:
    """Client for the Agent VM provisioning service."""

    def __init__(self, base_url: str = "http://localhost:8000", access_token: str | None = None) -> None:
        self._base_url = base_url.rstrip("/")
        token = access_token or os.environ.get("AGENT_SERVICE_ACCESS_TOKEN")
        headers = {"Authorization": f"Bearer {token}"} if token else None
        self._http = httpx.Client(base_url=self._base_url, timeout=30.0, headers=headers)

    @staticmethod
    def _vm_from_json(data: dict, client: AgentVMClient, owns_client: bool = False) -> VM:
        return VM(
            vm_id=data["vm_id"],
            account_id=data["account_id"],
            user_id=data["user_id"],
            image=data["image"],
            preset_slug=data["preset_slug"],
            vcpu=data["vcpu"],
            memory_mb=data["memory_mb"],
            disk_gb=data["disk_gb"],
            mcp_url=data["mcp_url"],
            status=data["status"],
            created_at=data["created_at"],
            last_active_at=data["last_active_at"],
            _client=client,
            _owns_client=owns_client,
        )

    def provision_vm(self, config: VMConfig | None = None) -> VM:
        config = config or VMConfig()
        resp = self._http.post("/vms", json={"image": config.image, "preset_slug": config.preset_slug})
        resp.raise_for_status()
        return self._vm_from_json(resp.json(), self)

    def get_vm(self, vm_id: str) -> VM:
        resp = self._http.get(f"/vms/{vm_id}")
        resp.raise_for_status()
        return self._vm_from_json(resp.json(), self)

    def list_vms(self) -> list[VM]:
        resp = self._http.get("/vms")
        resp.raise_for_status()
        return [self._vm_from_json(d, self) for d in resp.json()]

    def destroy_vm(self, vm_id: str) -> None:
        resp = self._http.delete(f"/vms/{vm_id}")
        resp.raise_for_status()

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> AgentVMClient:
        return self

    def __exit__(self, *exc) -> None:
        self.close()


class AgentVM:
    """
    Minimal wrapper that provisions on construction.

    Example:
        vm = AgentVM(VMConfig())
        async with vm.mcp_oai_agent as mcp_server:
            ...
        vm.destroy()
    """

    def __init__(
        self,
        config: VMConfig | None = None,
        *,
        base_url: str = "http://localhost:8000",
        access_token: str | None = None,
    ) -> None:
        self._client = AgentVMClient(base_url=base_url, access_token=access_token)
        self._vm = self._client.provision_vm(config or VMConfig())
        self._vm._owns_client = True

    @property
    def vm(self) -> VM:
        return self._vm

    @property
    def mcp_oai_agent(self) -> Any:
        return self._vm.mcp_oai_agent

    @property
    def mcp_tool(self) -> MCPTool:
        return self._vm.mcp_tool

    def destroy(self) -> None:
        self._vm.destroy()

    def __enter__(self) -> AgentVM:
        return self

    def __exit__(self, *exc) -> None:
        self.destroy()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._vm, name)


def create_vm(
    config: VMConfig | None = None,
    *,
    base_url: str = "http://localhost:8000",
    access_token: str | None = None,
) -> VM:
    """
    Minimal entry point: provision and return a managed VM directly.

    The returned VM owns its internal client and will close it on destroy.
    """
    return AgentVM(config=config, base_url=base_url, access_token=access_token).vm
