from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    AIMessage,
    BaseMessage
)

# Consts

MODEL = "llama-3.1-8b-instant"
TEMP = 0.0

# Load envvars

load_dotenv()

# Load LLM

llm = ChatGroq(
    model=MODEL,
    temperature=TEMP,
)

# System Prompt

messages: list[BaseMessage] = [
    SystemMessage(
        content="You are a helpful assistant. Be concise."
    )
]

print("Chatbot ready. Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")

    if user_input.lower() in ["exit", "quit"]:
        break

    messages.append(
        HumanMessage(content=user_input)
    )

    print("Bot: ", end="", flush=True)

    full_response = ""

    for chunk in llm.stream(messages):
        content = str(chunk.content or "")

        print(content, end="", flush=True)

        full_response += content

    print("\n")

    messages.append(
        AIMessage(content=full_response)
    )
