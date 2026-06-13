# ComfyUI RunningHub Integration

A ComfyUI custom node library for [RunningHub](https://www.runninghub.cn) — the cloud-based AI content creation platform. Execute workflows, invoke AI models, and manage cloud resources directly from your local ComfyUI instance.

## Features

- **20 custom nodes** covering workflow execution, AI model invocation, file management, and utilities
- **WebSocket real-time progress** tracking with HTTP polling fallback
- **Dual install support** — git clone or `pip install`
- **Compatible** with both RunningHub China (`runninghub.cn`) and International (`runninghub.ai`)

## Installation

### Method 1: Git Clone (Recommended)

```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/YOUR_USERNAME/ComfyUI-RunningHub.git
cd ComfyUI-RunningHub
pip install -r requirements.txt
```

### Method 2: pip install

```bash
pip install ComfyUI-RunningHub
```

Restart ComfyUI after installation.

## Quick Start

1. **Get your API Key**: Log in to [RunningHub](https://www.runninghub.cn) → User Menu → API Key
2. **Create a Workflow**: Build a workflow on RunningHub and copy its Workflow ID from the URL
3. **Configure**: Add an **RH Settings** node and paste your API Key and Workflow ID
4. **Execute**: Add an **RH Execute Workflow** node, connect Settings → Execute, and queue the prompt

## Nodes

### Configuration

| Node | Description |
|------|-------------|
| **RH Settings** | Configure API Key, Base URL, and Workflow ID |
| **RH Node Info** | Build parameter overrides for workflow nodes |

### Task Execution

| Node | Description |
|------|-------------|
| **RH Execute Workflow** | Submit and execute a ComfyUI workflow on RunningHub |
| **RH Execute AI App** | Submit and execute an AI App |
| **RH Task Status** | Query task execution status |
| **RH Task Cancel** | Cancel a running task |
| **RH Task Outputs** | Retrieve task output results |

### AI Model Invocation

| Node | Description |
|------|-------------|
| **RH Text to Image** | Generate images from text |
| **RH Image to Image** | Transform images with a prompt |
| **RH Image to Video** | Generate video from an image |
| **RH Text to Video** | Generate video from text |
| **RH Text to Audio** | Generate audio from text |

### File Management

| Node | Description |
|------|-------------|
| **RH Upload Image** | Upload an IMAGE tensor to RunningHub |
| **RH Upload File** | Upload a local file to RunningHub |
| **RH Download Image** | Download a URL as IMAGE tensor |
| **RH Download Video** | Download a URL as video file |

### Utilities

| Node | Description |
|------|-------------|
| **RH Any to String** | Convert any value to string |
| **RH Extract Image** | Extract a single image from a batch |
| **RH Batch Images** | Select images by index range |
| **RH Split Output URLs** | Split multi-line URLs into individual outputs |

## Typical Workflow

```
RH Settings → RH Node Info → RH Execute Workflow → RH Download Image
```

1. **RH Settings**: Provide your API Key and Workflow ID
2. **RH Node Info**: Set prompt text, seeds, or other parameters (chain multiple for multi-param)
3. **RH Execute Workflow**: Submit the task and wait for results
4. **RH Download Image**: Convert output URLs to ComfyUI IMAGE tensors for further processing

## Configuration

### Base URLs

- **China**: `https://www.runninghub.cn`
- **International**: `https://www.runninghub.ai`

### GPU Options

The Execute nodes support an optional `use_rtx4090` flag for high-performance GPU execution.

## API Reference

RunningHub API documentation:
- [API Overview](https://www.runninghub.ai/runninghub-api-doc-en/doc-8287463)
- [nodeInfoList Guide](https://www.runninghub.ai/runninghub-api-doc-en/doc-8287464)
- [Integration Examples](https://www.runninghub.ai/runninghub-api-doc-en/doc-8287469)

## Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Build package
python -m build
```

## License

MIT License. See [LICENSE](LICENSE) for details.
