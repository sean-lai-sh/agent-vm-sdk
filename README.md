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

## Quick Start

```python
from agent_vm_sdk import AgentVMClient, VMConfig

# Connect to your Agent VM service
with AgentVMClient("http://localhost:8000", access_token="your-supabase-token") as client:
    # Provision a new VM
    vm = client.provision_vm(VMConfig(
        image="agent-vm-base",
        preset_slug="micro"
    ))

    print(f"VM ID: {vm.vm_id}")
    print(f"MCP URL: {vm.mcp_url}")
    print(f"Status: {vm.status}")

    # VM will be automatically destroyed on context exit

# Or manage manually
client = AgentVMClient("http://localhost:8000")
vm = client.provision_vm()
# ... use the VM ...
vm.destroy()
```

## API Reference

### `AgentVMClient`

The main client for interacting with the Agent VM provisioning service.

**Constructor**:
```python
AgentVMClient(base_url: str = "http://localhost:8000", access_token: str | None = None)
```

**Methods**:
- `provision_vm(config: VMConfig | None = None) -> VM` - Provision a new VM
- `get_vm(vm_id: str) -> VM` - Get VM details by ID
- `list_vms() -> list[VM]` - List all your VMs
- `destroy_vm(vm_id: str) -> None` - Destroy a VM
- `close() -> None` - Close the HTTP client

### `VMConfig`

Configuration for provisioning a VM.

```python
@dataclass
class VMConfig:
    image: str = "agent-vm-base"
    preset_slug: str = "micro"
```

### `VM`

Represents a provisioned VM.

**Attributes**:
- `vm_id: str` - Unique VM identifier
- `account_id: str` - Account owner
- `user_id: str` - User owner
- `image: str` - Docker image name
- `preset_slug: str` - Resource preset
- `vcpu: float` - Virtual CPU allocation
- `memory_mb: int` - Memory in MB
- `disk_gb: int` - Disk space in GB
- `mcp_url: str` - MCP endpoint URL
- `status: str` - VM status
- `created_at: float` - Creation timestamp
- `last_active_at: float` - Last activity timestamp

**Methods**:
- `destroy() -> None` - Destroy this VM

## Development

```bash
# Install in editable mode
pip install -e .

# Build distribution
uv build
```

## Links

- [Agent VM Container Runtime](https://github.com/sean-lai-sh/agent-vm)
- [Model Context Protocol](https://modelcontextprotocol.io/)

## License

MIT
