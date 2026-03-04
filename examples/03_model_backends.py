"""Demonstrates multiple model backends for smolagents.

Uncomment the block you want to run and ensure required dependencies
and environment variables are configured.
"""

from smolagents import CodeAgent, InferenceClientModel


def run_with_hf_inference() -> None:
    model = InferenceClientModel(model_id="meta-llama/Llama-2-70b-chat-hf")
    agent = CodeAgent(tools=[], model=model)
    print(agent.run("Write a one-line summary of smolagents."))


# Requires: smolagents[litellm] and provider API key env vars.
# from smolagents import LiteLLMModel
#
#
# def run_with_litellm() -> None:
#     model = LiteLLMModel(model_id="gpt-4")
#     agent = CodeAgent(tools=[], model=model)
#     print(agent.run("Write a one-line summary of smolagents."))


# Requires: smolagents[transformers] and local compute resources.
# from smolagents import TransformersModel
#
#
# def run_with_transformers() -> None:
#     model = TransformersModel(model_id="meta-llama/Llama-2-7b-chat-hf")
#     agent = CodeAgent(tools=[], model=model)
#     print(agent.run("Write a one-line summary of smolagents."))


def main() -> None:
    run_with_hf_inference()


if __name__ == "__main__":
    main()
