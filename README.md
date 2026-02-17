# agent-vm-sdk

Python SDK for provisioning and managing Agent VMs.

## Installation

```bash
pip install agent-vm-sdk
```

Using `uv`:

```bash
uv pip install agent-vm-sdk
```

## Usage

```python
from agent_vm_sdk import AgentVMClient, VMConfig

with AgentVMClient("http://localhost:8000", access_token="your-supabase-access-token") as client:
    vm = client.provision_vm(VMConfig(image="agent-vm-base", preset_slug="micro"))
    print(vm.vm_id, vm.mcp_url)
```

## Build (uv)

```bash
uv build
```
