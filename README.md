# agent-vm-sdk

Python SDK for provisioning and managing Agent VMs.

## Installation

```bash
pip install agent-vm-sdk
```

With OpenAI Agents SDK support:

```bash
pip install "agent-vm-sdk[openai-agents]"
```

## Quick Start

### OpenAI Agents SDK

Provision a VM and plug it directly into an OpenAI Agents SDK agent:

```python
import asyncio
from agents import Agent, Runner
from agent_vm_sdk import AgentVM, VMConfig

async def main():
    with AgentVM(VMConfig(), service_url="https://your-agent-service") as vm:
        async with vm.mcp_tool.openai_agents() as mcp_server:
            agent = Agent(
                name="code-agent",
                instructions="You are a code execution agent.",
                mcp_servers=[mcp_server],
            )
            result = await Runner.run(agent, "How many r's are in strawberries?")
            print(result.final_output)

asyncio.run(main())
```

### Claude / Generic MCP Config

```python
from agent_vm_sdk import AgentVM

with AgentVM(service_url="https://your-agent-service") as vm:
    config = vm.mcp_tool.claude_agent(name="my-vm")
    # {"name": "my-vm", "type": "url", "url": "http://..."}
    print(config)
```

## Usage

### `AgentVM` — provision and go

`AgentVM` provisions a VM on construction and tears it down on exit:

```python
from agent_vm_sdk import AgentVM, VMConfig

vm = AgentVM(
    VMConfig(image="agent-vm-base", preset_slug="micro"),
    service_url="https://your-agent-service",
    access_token="your-access-token",  # or set AGENT_SERVICE_ACCESS_TOKEN
)

print(vm.mcp_url)   # e.g. http://10.0.0.5:7777/mcp
vm.destroy()
```

### `AgentVMClient` — full lifecycle control

```python
from agent_vm_sdk import AgentVMClient, VMConfig

with AgentVMClient(
    service_url="https://your-agent-service",
    access_token="your-access-token",
) as client:
    vm = client.provision_vm(VMConfig(preset_slug="micro"))
    print(vm.vm_id, vm.mcp_url)

    vms = client.list_vms()
    same_vm = client.get_vm(vm.vm_id)

    client.destroy_vm(vm.vm_id)
```

### `AsyncAgentVMClient` — async lifecycle control

```python
import asyncio
from agent_vm_sdk import AsyncAgentVMClient, VMConfig

async def main():
    async with AsyncAgentVMClient(
        service_url="https://your-agent-service",
        access_token="your-access-token",
    ) as client:
        vm = await client.provision_vm(VMConfig(preset_slug="micro"))
        print(vm.vm_id, vm.mcp_url)
        await client.destroy_vm(vm.vm_id)

asyncio.run(main())
```

### MCP adapters

| Adapter | Returns | Use with |
|---|---|---|
| `vm.mcp_tool.openai_agents()` | `MCPServerStreamableHttp` context manager | OpenAI Agents SDK |
| `vm.mcp_tool.claude_agent()` | `{"name", "type", "url"}` dict | Claude / generic HTTP MCP clients |

## Configuration

| Parameter | Env var | Default | Description |
|---|---|---|---|
| `service_url` | — | `http://localhost:8000` | URL of the agent provisioning service |
| `access_token` | `AGENT_SERVICE_ACCESS_TOKEN` | `None` | Bearer token for the service |

## Build

```bash
uv build
```
