from smolagents import CodeAgent, DuckDuckGoSearchTool, InferenceClientModel

DEFAULT_TASK = "What is the current weather in Paris?"


def build_search_agent(model: InferenceClientModel | None = None) -> CodeAgent:
    selected_model = model or InferenceClientModel()
    return CodeAgent(
        tools=[DuckDuckGoSearchTool()],
        model=selected_model,
    )


def run_search_task(task: str = DEFAULT_TASK, model: InferenceClientModel | None = None) -> str:
    agent = build_search_agent(model=model)
    return str(agent.run(task))


def main() -> None:
    print(run_search_task())


if __name__ == "__main__":
    main()
