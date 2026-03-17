"""Helpers for running smolagents with different model backends."""

from smolagents import CodeAgent, InferenceClientModel

DEFAULT_TASK = "Write a one-line summary of smolagents."


def _run_with_model(model: object, task: str) -> str:
    agent = CodeAgent(tools=[], model=model)
    return str(agent.run(task))


def run_with_hf_inference(
    task: str = DEFAULT_TASK,
    model_id: str = "meta-llama/Llama-2-70b-chat-hf",
) -> str:
    model = InferenceClientModel(model_id=model_id)
    return _run_with_model(model, task)


def run_with_litellm(task: str = DEFAULT_TASK, model_id: str = "gpt-4") -> str:
    try:
        from smolagents import LiteLLMModel
    except ImportError as exc:
        raise RuntimeError(
            "LiteLLM support is not installed. Install the project with the 'litellm' extra."
        ) from exc

    model = LiteLLMModel(model_id=model_id)
    return _run_with_model(model, task)


def run_with_transformers(
    task: str = DEFAULT_TASK,
    model_id: str = "meta-llama/Llama-2-7b-chat-hf",
) -> str:
    try:
        from smolagents import TransformersModel
    except ImportError as exc:
        raise RuntimeError(
            "Transformers support is not installed. Install the project with the 'transformers' extra."
        ) from exc

    model = TransformersModel(model_id=model_id)
    return _run_with_model(model, task)


def main() -> None:
    print(run_with_hf_inference())


if __name__ == "__main__":
    main()
