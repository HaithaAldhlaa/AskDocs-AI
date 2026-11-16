
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

load_dotenv()


# Define the evaluation result
class FaithfulnessEvaluation(BaseModel):

    is_faithful: bool = Field(
        description="Whether the answer is fully supported by the context"
    )

    reason: str = Field(
        description="Explanation of the evaluation result"
    )

    unsupported_claims: list[str] = Field(
        description="Claims in the answer that are not supported by the context"
    )


# Initialize the LLM Judge
llm_judge = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    max_tokens=1024,
)

# Initialize the output parser
parser = PydanticOutputParser(
    pydantic_object=FaithfulnessEvaluation
)


judge_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are an expert evaluator for RAG systems.

        Your task is to evaluate the faithfulness of an answer
        based ONLY on the provided context.

        Evaluation rules:

        1. Check every factual claim in the answer.
        2. A claim is supported only if the context provides
           sufficient evidence for it.
        3. Do not use your general knowledge.
        4. Do not assume information that is not in the context.
        5. If all claims are supported, is_faithful must be True.
        6. If any claim is unsupported or contradicts the context,
           is_faithful must be False.
        7. List every unsupported claim.

        {format_instructions}
        """
    ),
    (
        "human",
        """
        Retrieved Context:
        {context}

        Generated Answer:
        {answer}
        """
    ),
])


judge_chain = (judge_prompt | llm_judge | parser)


test_cases = [
    {
        "context": "Employees receive 21 days of annual leave.",
        "answer": "Employees receive 21 days of annual leave.",
        "expected_faithfulness": True,
    },
    {
        "context": "Employees receive 21 days of annual leave.",
        "answer": "Employees receive 30 days of annual leave.",
        "expected_faithfulness": False,
    },
    {
        "context": "Employees receive 21 days of annual leave.",
        "answer": """
        Employees receive 21 days of annual leave.
        They also receive 10 days of sick leave.
        """,
        "expected_faithfulness": False,
    },
]

for index, test_case in enumerate(test_cases, start=1):

    print("\n" + "=" * 50)
    print(f"Test Case: {index}")

    result = judge_chain.invoke({
        "context": test_case["context"],
        "answer": test_case["answer"],
        "format_instructions": parser.get_format_instructions(),
    })

    expected = test_case["expected_faithfulness"]

    actual = result.is_faithful

    print("\nContext:")
    print(test_case["context"])

    print("\nAnswer:")
    print(test_case["answer"])

    print("\nLLM Judge Result:")
    print(actual)

    print("\nReason:")
    print(result.reason)

    print("\nUnsupported Claims:")
    print(result.unsupported_claims)

    print("\nExpected Result:")
    print(expected)

    print("\nEvaluation:")
    print("PASS" if actual == expected else "FAIL")
