# agent-os-sdk

Python SDK for provisioning and managing Agent VMs.

## Installation

```bash
pip install agent-os-sdk
```

Using `uv`:

```bash
uv pip install agent-os-sdk
```

## Usage

```python
from agent_os_sdk import AgentVMClient, VMConfig

with AgentVMClient("http://localhost:8000", access_token="your-supabase-access-token") as client:
    vm = client.provision_vm(VMConfig(image="agent-os-base", preset_slug="micro"))
    print(vm.vm_id, vm.mcp_url)
```

## Build (uv)

```bash
uv build
```
