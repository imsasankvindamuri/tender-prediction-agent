from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    AIMessage,
    BaseMessage
)

from utils import extract_pdf_text

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
        content="""
You are an AI assistant that helps users analyze Indian tender documents.

Your responsibilities:
- Summarize tender documents clearly.
- Extract important information accurately.
- Help users understand requirements, deadlines, costs, and risks.
- Answer questions ONLY using the provided tender context.
- If information is missing, explicitly say so.
- Do not hallucinate details that are not present in the tender.

When summarizing a tender, focus on:
- Tender title
- Tender reference number
- Department/organization
- Scope of work
- Estimated project cost
- EMD/security deposit
- Eligibility criteria
- Important deadlines
- Completion period
- Technical requirements
- Financial requirements
- Risks, penalties, or SLA clauses

Be concise, structured, and professional.
"""
    )
]

tender_text = extract_pdf_text(input("Enter path to tender PDF: "))

messages.append(
    HumanMessage(
        content=f"""
Here is the tender document context:

{tender_text}

Return the following sections:

1. Critical Information
- Tender reference number
- Important dates
- Submission deadlines
- EMD
- Tender fees

2. Qualification Criteria
- Eligibility requirements
- Financial turnover requirements
- Certifications required
- Prior experience requirements

3. Technical Proposal Requirements
- Technical specifications
- Deliverables
- Timeline expectations

4. SLA and Commercial Terms
- Penalties
- Payment terms
- Commercial clauses
- Risky or unusual conditions

5. Risks and Red Flags
- Missing information
- Strict qualification barriers
- High penalties
- Ambiguous clauses

Only use information explicitly present in the tender. If information is unavailable, state so clearly.
Return the output in structured markdown.
"""
    )
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
