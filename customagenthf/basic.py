from smolagents import CodeAgent, InferenceClientModel

DEFAULT_TASK = "Calculate the sum of numbers from 1 to 10"


def build_minimal_agent(model: InferenceClientModel | None = None) -> CodeAgent:
    selected_model = model or InferenceClientModel()
    return CodeAgent(tools=[], model=selected_model)


def run_minimal_task(task: str = DEFAULT_TASK, model: InferenceClientModel | None = None) -> str:
    agent = build_minimal_agent(model=model)
    return str(agent.run(task))


def main() -> None:
    print(run_minimal_task())


if __name__ == "__main__":
    main()
