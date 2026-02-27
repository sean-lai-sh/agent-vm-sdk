from __future__ import annotations

import os
from typing import Any

import httpx

from ._mcp import MCPTool
from ._models import VM, VMConfig


class AgentVMClient:
    """Synchronous client for the Agent VM provisioning service."""

    def __init__(
        self,
        service_url: str = "http://localhost:8000",
        access_token: str | None = None,
    ) -> None:
        token = access_token or os.environ.get("AGENT_SERVICE_ACCESS_TOKEN")
        headers = {"Authorization": f"Bearer {token}"} if token else None
        self._http = httpx.Client(base_url=service_url.rstrip("/"), timeout=30.0, headers=headers)

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

    def __exit__(self, *exc: object) -> None:
        self.close()


class AgentVM:
    """
    Minimal wrapper that provisions on construction.

    Example:
        with AgentVM() as vm:
            async with vm.mcp_oai_agent as mcp_server:
                ...
    """

    def __init__(
        self,
        config: VMConfig | None = None,
        *,
        service_url: str = "http://localhost:8000",
        access_token: str | None = None,
    ) -> None:
        self._client = AgentVMClient(service_url=service_url, access_token=access_token)
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

    def __exit__(self, *exc: object) -> None:
        self.destroy()

    def __getattr__(self, name: str) -> Any:
        return getattr(self._vm, name)


def create_vm(
    config: VMConfig | None = None,
    *,
    service_url: str = "http://localhost:8000",
    access_token: str | None = None,
) -> VM:
    """
    Provision and return a managed VM.

    The returned VM owns its internal client and will close it on destroy().
    """
    return AgentVM(config=config, service_url=service_url, access_token=access_token).vm
