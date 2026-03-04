from smolagents import CodeAgent, DuckDuckGoSearchTool, InferenceClientModel


def main() -> None:
    model = InferenceClientModel()
    agent = CodeAgent(
        tools=[DuckDuckGoSearchTool()],
        model=model,
    )

    result = agent.run("What is the current weather in Paris?")
    print(result)


if __name__ == "__main__":
    main()
