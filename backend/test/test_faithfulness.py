
test_cases = [
    {
        "context": """
        Employees receive 21 days of annual leave.
        """,
        "answer": "Employees receive 21 days of annual leave.",
        "expected_faithfulness": True,
    },
    {
        "context": """
        Employees receive 21 days of annual leave.
        """,
        "answer": "Employees receive 30 days of annual leave.",
        "expected_faithfulness": False,
    },
    {
        "context": """
        Employees receive 21 days of annual leave.
        """,
        "answer": """
        Employees receive 21 days of annual leave.
        They also receive 10 days of sick leave.
        """,
        "expected_faithfulness": False,
    },
]


def evaluate_faithfulness(context, answer):

    context_words = set(context.lower().split())

    answer_words = set(answer.lower().split())

    unsupported_words = answer_words - context_words

    return unsupported_words


for test_case in test_cases:

    context = test_case["context"]
    answer = test_case["answer"]
    expected = test_case["expected_faithfulness"]

    unsupported_words = evaluate_faithfulness(
        context,
        answer
    )

    actual = len(unsupported_words) == 0

    print("\n" + "=" * 50)

    print("Answer:")
    print(answer)

    print("\nUnsupported Words:")
    print(unsupported_words)

    print("\nExpected Faithfulness:")
    print(expected)

    print("\nActual Faithfulness:")
    print(actual)

    print("\nEvaluation:")
    print("PASS" if actual == expected else "FAIL")
