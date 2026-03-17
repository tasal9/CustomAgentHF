# smolagents Starter Workspace

This workspace contains a minimal, runnable setup for building agents with `smolagents`, now organized as a reusable Python package.

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

### 2. Install the package and dependencies

```bash
pip install -r requirements.txt
```

This installs the project in editable mode via `requirements.txt`, so both the reusable package and the example scripts work from the repository checkout.

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

You can also run the package directly:

```bash
python -m customagenthf minimal
python -m customagenthf search
python -m customagenthf backends --backend hf
python -m customagenthf zeerak --list-features
python -m customagenthf zeerak --list-features --max-width 80
python -m customagenthf zeerak --search-features curriculum
python -m customagenthf zeerak --search-features curriculum --output json
python -m customagenthf zeerak --feature auto --task "Help me write a junior developer CV"
```

## File Layout

- `customagenthf/basic.py`: reusable minimal `CodeAgent` helpers.
- `customagenthf/search.py`: reusable search-enabled agent helpers.
- `customagenthf/backends.py`: model backend runners for HF, LiteLLM, and Transformers.
- `customagenthf/zeerak/`: Zeerak subpackage split into config, routing, policy, execution, and CLI modules.
- `customagenthf/zeerak/prompts/*.txt`: prompt content stored as editable text assets instead of embedded Python strings.
- `customagenthf/cli.py`: package CLI exposed through `python -m customagenthf` and `customagenthf`.
- `examples/01_minimal_code_agent.py`: thin wrapper for the minimal package entry point.
- `examples/02_search_tool_agent.py`: thin wrapper for the search package entry point.
- `examples/03_model_backends.py`: thin wrapper for the backend package entry point.
- `examples/04_zeerak_feature_agents.py`: thin wrapper for the Zeerak package entry point.
- `requirements.txt`: editable install for the package.
- `pyproject.toml`: package metadata and optional extras for backend-specific installs.
- `.env.example`: sample environment variables.

## Package Usage

Import the reusable helpers directly in your own code:

```python
from customagenthf.basic import run_minimal_task
from customagenthf.search import run_search_task
from customagenthf.zeerak import list_features, render_feature_json, render_feature_table, run_feature, search_features

print(run_minimal_task("Sum the numbers from 1 to 20"))
print(run_search_task("What is the weather in Kabul today?"))
print([feature.name for feature in list_features(include_auto=False)])
print([feature.name for feature in search_features("curriculum")])
print(render_feature_table(search_features("curriculum")))
print(render_feature_json(search_features("curriculum")))
print(run_feature("codekhana", "Explain Python functions with two short exercises"))
```

Example JSON payload from `python -m customagenthf zeerak --search-features curriculum --output json`:

```json
[
	{
		"name": "education",
		"overview": "Curriculum-aligned tutoring for Afghan classes 6-12.",
		"default_model_id": "Qwen/Qwen2.5-72B-Instruct",
		"search_enabled": true,
		"tool_calling_enabled": true,
		"capabilities": [
			"search",
			"tool-calling"
		]
	}
]
```

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

## Recommended Models Per Feature

Default model mapping in `examples/04_zeerak_feature_agents.py`:

- `chat`: `CohereForAI/aya-expanse-32b` (strong multilingual behavior for regional language support).
- `zamvision`: `Qwen/Qwen2.5-VL-72B-Instruct` (vision-capable for OCR/image reasoning workflows).
- `codekhana`: `Qwen/Qwen2.5-Coder-32B-Instruct` (coding-focused instruction model).
- `dehqan`: `meta-llama/Llama-3.3-70B-Instruct` (strong general reasoning for agriculture guidance).
- `tabib`: `microsoft/Phi-4` (concise clinical-style reasoning with policy guardrails in script).
- `hunar`: `meta-llama/Llama-3.1-70B-Instruct` (good structured writing for CV/interview content).
- `education`: `Qwen/Qwen2.5-72B-Instruct` (strong tutoring/explainer quality).

Override any default via environment variables in `.env`:

```bash
ZEERAK_MODEL_CHAT=
ZEERAK_MODEL_ZAMVISION=
ZEERAK_MODEL_CODEKHANA=
ZEERAK_MODEL_DEHQAN=
ZEERAK_MODEL_TABIB=
ZEERAK_MODEL_HUNAR=
ZEERAK_MODEL_EDUCATION=
ZEERAK_MODEL_FALLBACK=
```

Fallback behavior:

- If your selected feature model is blocked by provider permissions (for example 403/provider-not-enabled), the launcher retries automatically with `ZEERAK_MODEL_FALLBACK`.

## Notes

- Some examples require valid API keys and network access.
- Local model usage with Transformers can be resource-intensive.
