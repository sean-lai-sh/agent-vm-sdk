from __future__ import annotations

import os

import httpx

from ._models import VM, VMConfig


class AsyncAgentVMClient:
    """Async client for the Agent VM provisioning service."""

    def __init__(
        self,
        service_url: str = "http://localhost:8000",
        access_token: str | None = None,
    ) -> None:
        token = access_token or os.environ.get("AGENT_SERVICE_ACCESS_TOKEN")
        headers = {"Authorization": f"Bearer {token}"} if token else None
        self._http = httpx.AsyncClient(base_url=service_url.rstrip("/"), timeout=30.0, headers=headers)

    @staticmethod
    def _vm_from_json(data: dict) -> VM:
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
        )

    async def provision_vm(self, config: VMConfig | None = None) -> VM:
        config = config or VMConfig()
        resp = await self._http.post("/vms", json={"image": config.image, "preset_slug": config.preset_slug})
        resp.raise_for_status()
        return self._vm_from_json(resp.json())

    async def get_vm(self, vm_id: str) -> VM:
        resp = await self._http.get(f"/vms/{vm_id}")
        resp.raise_for_status()
        return self._vm_from_json(resp.json())

    async def list_vms(self) -> list[VM]:
        resp = await self._http.get("/vms")
        resp.raise_for_status()
        return [self._vm_from_json(d) for d in resp.json()]

    async def destroy_vm(self, vm_id: str) -> None:
        resp = await self._http.delete(f"/vms/{vm_id}")
        resp.raise_for_status()

    async def aclose(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> AsyncAgentVMClient:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()


async def async_create_vm(
    config: VMConfig | None = None,
    *,
    service_url: str = "http://localhost:8000",
    access_token: str | None = None,
) -> VM:
    """
    Provision and return a VM using the async client.

    Note: the returned VM has no client reference — use AsyncAgentVMClient
    directly if you need to destroy the VM later.
    """
    async with AsyncAgentVMClient(service_url=service_url, access_token=access_token) as client:
        return await client.provision_vm(config or VMConfig())
