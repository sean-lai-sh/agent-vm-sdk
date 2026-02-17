from __future__ import annotations

import os
from dataclasses import dataclass

import httpx


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

    _client: AgentVMClient | None = None

    def destroy(self) -> None:
        if self._client:
            self._client.destroy_vm(self.vm_id)
            self.status = "stopped"

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
    def _vm_from_json(data: dict, client: AgentVMClient) -> VM:
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
