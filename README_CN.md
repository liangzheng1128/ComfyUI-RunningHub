# ComfyUI RunningHub 节点库

[RunningHub](https://www.runninghub.cn) 云端 AI 内容创作平台的 ComfyUI 自定义节点库。在本地 ComfyUI 中直接执行云端工作流、调用 AI 模型、管理云端资源。

## 功能特性

- **20 个自定义节点**：覆盖工作流执行、AI 模型调用、文件管理、工具类
- **WebSocket 实时进度**追踪，自动回退 HTTP 轮询
- **双安装方式**：支持 git clone 或 pip install
- **兼容国内版**（`runninghub.cn`）和**国际版**（`runninghub.ai`）

## 安装

### 方式一：Git Clone（推荐）

```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/YOUR_USERNAME/ComfyUI-RunningHub.git
cd ComfyUI-RunningHub
pip install -r requirements.txt
```

### 方式二：pip 安装

```bash
pip install ComfyUI-RunningHub
```

安装后重启 ComfyUI 即可。

## 快速开始

1. **获取 API Key**：登录 [RunningHub](https://www.runninghub.cn) → 用户菜单 → API Key
2. **创建工作流**：在 RunningHub 上构建工作流，从 URL 中复制 Workflow ID
3. **配置**：添加 **RH Settings** 节点，填入 API Key 和 Workflow ID
4. **执行**：添加 **RH Execute Workflow** 节点，连接 Settings → Execute，点击执行

## 节点列表

### 配置类

| 节点 | 说明 |
|------|------|
| **RH Settings** | 配置 API Key、Base URL 和 Workflow ID |
| **RH Node Info** | 构建工作流节点参数覆盖（可链式连接多个） |

### 任务执行类

| 节点 | 说明 |
|------|------|
| **RH Execute Workflow** | 提交并执行 ComfyUI 工作流 |
| **RH Execute AI App** | 提交并执行 AI 应用 |
| **RH Task Status** | 查询任务执行状态 |
| **RH Task Cancel** | 取消运行中的任务 |
| **RH Task Outputs** | 获取任务输出结果 |

### AI 模型调用类

| 节点 | 说明 |
|------|------|
| **RH Text to Image** | 文本生成图片 |
| **RH Image to Image** | 图片+提示词生成图片 |
| **RH Image to Video** | 图片生成视频 |
| **RH Text to Video** | 文本生成视频 |
| **RH Text to Audio** | 文本生成音频 |

### 文件管理类

| 节点 | 说明 |
|------|------|
| **RH Upload Image** | 上传 IMAGE 张量到 RunningHub |
| **RH Upload File** | 上传本地文件到 RunningHub |
| **RH Download Image** | 从 URL 下载图片为 IMAGE 张量 |
| **RH Download Video** | 从 URL 下载视频 |

### 工具类

| 节点 | 说明 |
|------|------|
| **RH Any to String** | 任意类型转字符串 |
| **RH Extract Image** | 从批次中提取单张图片 |
| **RH Batch Images** | 按索引范围选择图片 |
| **RH Split Output URLs** | 拆分多行 URL 为独立输出 |

## 典型工作流

```
RH Settings → RH Node Info → RH Execute Workflow → RH Download Image
```

1. **RH Settings**：填入 API Key 和 Workflow ID
2. **RH Node Info**：设置提示词文本、种子等参数（可链接多个）
3. **RH Execute Workflow**：提交任务并等待结果
4. **RH Download Image**：将输出 URL 转换为 ComfyUI IMAGE 张量

## 配置说明

### Base URL

- **国内版**：`https://www.runninghub.cn`
- **国际版**：`https://www.runninghub.ai`

### GPU 选项

执行节点支持 `use_rtx4090` 选项，可选择 RTX 4090 高性能 GPU 执行。

## API 参考

RunningHub API 文档：
- [API 概览](https://www.runninghub.cn/runninghub-api-doc-cn/doc-8287463)
- [nodeInfoList 使用指南](https://www.runninghub.cn/runninghub-api-doc-cn/doc-8287464)
- [集成示例](https://www.runninghub.cn/runninghub-api-doc-cn/doc-8287469)

## 开发

```bash
# 开发模式安装
pip install -e ".[dev]"

# 运行测试
pytest tests/ -v

# 构建包
python -m build
```

## 许可证

MIT License。详见 [LICENSE](LICENSE)。
