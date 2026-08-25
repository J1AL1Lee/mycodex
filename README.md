# mycodex

一个用于学习 Codex 工作原理的最小实现。

当前版本已经跑通以下流程：

```text
用户输入
  ↓
调用 DeepSeek 模型
  ↓
模型返回 shell 工具调用
  ↓
校验并执行工具
  ↓
将工具结果放回消息历史
  ↓
再次调用模型
  ↓
模型返回最终文本
```

## 已实现

- `ModelClient` 抽象接口
- `FakeModelClient` 测试客户端
- DeepSeek Responses API 客户端
- Agent Loop
- Tool Registry
- shell 工具及参数校验
- 工具输出与 `call_id` 配对
- cwd、超时和输出大小限制

## 尚未实现

- `apply_patch`
- shell 沙箱和执行审批
- 交互式、后台 shell 会话
- 完整异常处理和自动化测试

## 安装

需要 Python 3.11 或更高版本。

```powershell
python -m pip install openai
```

## 配置

在 PowerShell 中设置 DeepSeek API Key：

```powershell
$env:DEEPSEEK_API_KEY = "你的 API Key"
```

不要把 API Key 写进代码或提交到 Git。

## 运行

仓库目录名应为 `mycodex`。进入仓库的父目录运行：

```powershell
cd path\to\parent
python -m mycodex.test
```

示例输入会要求模型调用 shell 执行：

```text
echo Hello World
```

## 目录结构

```text
mycodex/
├── agents/
│   └── agent.py          # Agent Loop
├── llm/
│   ├── base.py           # ModelClient 抽象接口
│   ├── deepseek.py       # DeepSeek 客户端
│   └── tests/fake.py     # 假模型客户端
├── tools/
│   ├── registry.py       # 工具注册与分发
│   └── shell.py          # shell 工具
├── types.py              # 消息、工具调用和上下文类型
└── test.py               # 端到端运行示例
```

## 安全说明

当前 shell 工具使用 `subprocess` 直接执行模型生成的命令，尚未实现沙箱和人工审批。只应在可控的学习环境中运行，不要用于生产环境或包含重要数据的目录。

