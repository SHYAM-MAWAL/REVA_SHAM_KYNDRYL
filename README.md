# LangChain Academy Sessions — Annotated Notebooks

Annotated Jupyter notebooks from the **Introduction to LangChain (Python)** sessions. Each notebook includes Markdown explanations of the workflow, implementation notes, and key learnings, plus clarifying comments in the code cells.

Based on [LangChain Academy — Introduction to LangChain](https://academy.langchain.com/courses/foundation-introduction-to-langchain-python) ([upstream repo](https://github.com/langchain-ai/lca-lc-foundations)). Original course materials are MIT-licensed © LangChain, Inc.

---

## Notebook map

### Module 1 — Create Agent

| Notebook | Topic |
|---|---|
| `notebooks/module-1/1.1_foundational_models.ipynb` | Init models & agents, providers, streaming |
| `notebooks/module-1/1.1_prompting.ipynb` | System prompts, few-shot, structured output |
| `notebooks/module-1/1.2_tools.ipynb` | Defining tools and wiring them into agents |
| `notebooks/module-1/1.2_web_search.ipynb` | Tavily web search tool |
| `notebooks/module-1/1.3_memory.ipynb` | Short-term memory with checkpointers |
| `notebooks/module-1/1.4_multimodal_messages.ipynb` | Text, image, and audio inputs |
| `notebooks/module-1/1.5_personal_chef.ipynb` | Project: leftover-ingredient chef agent |

### Module 2 — Advanced Agent

| Notebook | Topic |
|---|---|
| `notebooks/module-2/2.1_mcp.ipynb` | Model Context Protocol (local + community servers) |
| `notebooks/module-2/2.1_travel_agent.ipynb` | Travel agent via remote MCP |
| `notebooks/module-2/2.2_runtime_context.ipynb` | Read-only runtime context |
| `notebooks/module-2/2.2_state.ipynb` | Mutable agent state |
| `notebooks/module-2/2.3_multi_agent.ipynb` | Multi-agent systems |
| `notebooks/module-2/2.4_wedding_planners.ipynb` | Project: wedding planner team |
| `notebooks/module-2/bonus_rag.ipynb` | Bonus: RAG |
| `notebooks/module-2/bonus_sql.ipynb` | Bonus: SQL agent |

### Module 3 — Production-Ready Agent

| Notebook | Topic |
|---|---|
| `notebooks/module-3/3.2_managing_messages.ipynb` | Summarisation & message trimming middleware |
| `notebooks/module-3/3.3_hitl.ipynb` | Human-in-the-loop approve / reject / edit |
| `notebooks/module-3/3.4_dynamic_models.ipynb` | Swap models from state |
| `notebooks/module-3/3.4_dynamic_prompts.ipynb` | Dynamic system prompts from context |
| `notebooks/module-3/3.4_dynamic_tools.ipynb` | Role-based tool gating |
| `notebooks/module-3/3.5_email_agent.ipynb` | Project: authenticated email agent + HITL |

---

## Setup

**Prerequisites:** Python >=3.12, <3.14 · [uv](https://docs.astral.sh/uv/) recommended · Chrome recommended

```bash
git clone https://github.com/SHYAM-MAWAL/langchain-academy-sessions.git
cd langchain-academy-sessions
cp example.env .env
# Edit .env with your API keys (OpenAI required; Tavily, Anthropic, Google, LangSmith optional)
uv sync
uv run jupyter lab
```

Or with pip:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter lab
```

Verify the environment:

```bash
uv run python env_utils.py
```

Required in `.env`:

- `OPENAI_API_KEY`
- `TAVILY_API_KEY` (web search / chef / some Module 2–3 labs)

Optional: `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, `LANGSMITH_API_KEY`

---

## Notes

- Notebook outputs were cleared for a clean diff-friendly repo — re-run cells locally.
- Do **not** commit `.env`; `example.env` is the template.
- Course middleware / API names follow LangChain’s current agent APIs (`create_agent`, middleware decorators, etc.).

## License

MIT — see `LICENSE`. Upstream copyright: LangChain, Inc. Annotations and session packaging in this repository are shared under the same license.
