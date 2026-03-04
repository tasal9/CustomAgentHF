# smolagents Starter Workspace

This workspace contains a minimal, runnable setup for building agents with `smolagents`.

## What is smolagents?

`smolagents` is an open-source Python library for building and running LLM agents with very little code.

Key strengths:

- Simplicity: lightweight abstractions and small core.
- Code-first agents: `CodeAgent` writes executable Python actions.
- Tool-calling support: `ToolCallingAgent` for JSON/text style function calling.
- Model-agnostic: supports Hugging Face Inference, LiteLLM providers, Transformers, and more.
- Tool-agnostic: can integrate MCP tools, LangChain tools, and Hub Spaces.
- Multimodal support: text, vision, video, and audio use cases.

## Quickstart

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables (optional but recommended)

```bash
cp .env.example .env
```

Set values in `.env` as needed:

- `HF_TOKEN` for Hugging Face inference access.
- `OPENAI_API_KEY` for LiteLLM/OpenAI usage.
- `ANTHROPIC_API_KEY` for LiteLLM/Anthropic usage.

### 4. Run examples

```bash
python examples/01_minimal_code_agent.py
python examples/02_search_tool_agent.py
python examples/03_model_backends.py
python examples/04_zeerak_feature_agents.py --feature codekhana --task "Teach me Python loops with 3 exercises"
```

## File Layout

- `examples/01_minimal_code_agent.py`: minimal `CodeAgent` with no tools.
- `examples/02_search_tool_agent.py`: `CodeAgent` with `DuckDuckGoSearchTool`.
- `examples/03_model_backends.py`: model backend examples (HF, LiteLLM, Transformers).
- `examples/04_zeerak_feature_agents.py`: Zeerak feature-focused agent launcher.
- `requirements.txt`: base install plus optional extras for common backends.
- `.env.example`: sample environment variables.

## Zeerak Feature Agents

Use the Zeerak launcher with one of these `--feature` values:

- `auto`: route user input to the best feature automatically.
- `chat`: multilingual conversation support.
- `zamvision`: OCR/translation/object-recognition guidance workflow.
- `codekhana`: Python and web development mentorship.
- `dehqan`: farming support and crop advice.
- `tabib`: symptom triage guidance with emergency escalation templates.
- `hunar`: skills roadmap and CV builder.
- `education`: class 6-12 tutoring support.

Examples:

```bash
python examples/04_zeerak_feature_agents.py --feature auto --task "I need help writing a CV for a junior developer role"
python examples/04_zeerak_feature_agents.py --feature chat --task "Respond in Dari and introduce yourself"
python examples/04_zeerak_feature_agents.py --feature dehqan --task "Wheat pest control in Nangarhar this month"
python examples/04_zeerak_feature_agents.py --feature hunar --task "Build a CV summary for junior web developer"
```

Tabib safety note:

- If urgent keywords are detected (for example chest pain, breathing difficulty, severe bleeding, stroke, self-harm), the script returns an immediate emergency escalation template without calling the model.

## Notes

- Some examples require valid API keys and network access.
- Local model usage with Transformers can be resource-intensive.
