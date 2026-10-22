# Aurora 研学管家

一个本地运行的深度学习与 Agent 学习工作台。用 Markdown 保存知识，用 Vue 看板组织学习，用可配置的 AI 助手辅助复习。

## 功能

- **知识管理**：知识框架树、关系图、Markdown 笔记编辑、数学公式与代码高亮。
- **学习闭环**：四级掌握度、自测题、速查词典、学习路线与日记记录。
- **双知识库**：内置深度学习与 Agent 学习笔记；CV 入口为前端工作区。
- **AI 助手**：基于 LangGraph 的工具调用，可读取笔记、更新掌握度和记录日记。
- **模型配置**：支持兼容 OpenAI 接口的模型服务和本地 Ollama；MCP 工具为可选功能。

核心看板无需配置模型密钥即可使用；AI 对话需要另行配置模型服务。

## 快速开始

需要 Python 3.11+、Node.js 22.12+ 或 Node.js 24，以及 npm。以下从仓库根目录运行。

```sh
git clone https://github.com/sheen17689-max/aurora-study.git
cd aurora-study
python -m venv .venv
```

Windows PowerShell 激活虚拟环境：

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS / Linux 激活虚拟环境：

```sh
source .venv/bin/activate
```

安装依赖并构建看板：

```sh
python -m pip install -r requirements.txt
cd dashboard
npm ci
npm run build
cd ..
python app.py
```

浏览器访问 <http://127.0.0.1:8899>，API 文档位于 <http://127.0.0.1:8899/docs>。当前书架演示口令均为 `12345`。

开发时在一个终端运行 `python app.py`，另一个终端进入 `dashboard` 后运行 `npm run dev`，访问 <http://127.0.0.1:5173>；Vite 将 `/api` 代理到后端。

Windows 用户安装前后端依赖后，可运行 `python launch_app.pyw` 启动开发模式；可选运行 `python create_desktop_shortcut.py` 创建快捷方式。

## AI 配置

可以在界面设置中填写模型服务地址、模型名和 API Key。也可将 `agent_config.example.json` 复制为 `agent_config.json` 后填写配置；该本地文件已加入 Git 忽略列表。配置文件中的字段会覆盖同名环境变量。

兼容接口的环境变量为 `OPENAI_API_KEY`、`OPENAI_BASE_URL`、`OPENAI_MODEL`。不要将密钥写入源代码或提交到 GitHub。

本地 Ollama 示例：先安装 Ollama 并拉取所选模型，然后设置 `base_url` 为 `http://localhost:11434/v1`、`model` 为已安装的模型名、`api_key` 为 `ollama`。

可选 MCP 支持安装命令：`python -m pip install -r requirements-mcp.txt`。在本地配置的 `mcp_servers` 中声明工具，工具服务需要自行安装和启动。

## 数据与运行范围

笔记、知识框架、词典、日记均存储为本地 Markdown。修改掌握度或编辑笔记会直接写回对应文件，建议定期备份。

发布副本保留代码及知识笔记，未包含原作者的个人日记、简报、本地模型配置、令牌文件及旧 Git 历史。运行时创建的日记与简报默认不纳入版本管理。

本项目面向个人本机使用，后端默认监听 `127.0.0.1`。书架口令仅为前端交互，不提供服务端身份认证；部分 API 可写入笔记、修改模型配置或关闭服务。请勿直接暴露到公网，也不要将其作为多用户服务部署。

## 目录

```text
aurora-study/
├── app.py                      后端启动入口
├── server/                     FastAPI 接口、内容解析与 AI 工具
├── dashboard/                  Vue + Vite 前端
├── 00-知识框架.md               深度学习知识框架
├── 00-速查词典.md
├── 学习路线.md
├── 知识点/                     深度学习笔记
├── agent/                      Agent 学习知识库
├── 日记/                       本地运行时生成
└── 简报/                       本地运行时生成
```

后端接口见 `server/api.py`，框架解析见 `server/framework.py`，内容聚合见 `server/content.py`，界面入口见 `dashboard/src/App.vue`。

## 贡献与许可

欢迎通过 Issue 和 Pull Request 改进项目，详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

项目采用 [MIT License](LICENSE)。第三方依赖保留各自的许可，学习笔记中的外部引用保留原出处及权利。
