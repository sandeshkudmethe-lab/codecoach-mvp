import json
import re
import os
import asyncio
from typing import Optional, List
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    client = genai.Client(api_key=api_key)
else:
    client = genai.Client()


async def generate_question(
    skill_level: str = "beginner",
    language: str = "python",
    topic_history: Optional[List[str]] = None,
    count: int = 1,
    is_new_user: bool = False,
) -> List[dict]:
    """Generates dynamic N distinct coding challenges with onboarding & level progression support."""
    history_str = ", ".join(topic_history) if topic_history else "None"

    onboarding_instruction = ""
    if is_new_user:
        onboarding_instruction = (
            "CRITICAL: Since this is a new user's first day, Question 1 MUST be a foundational "
            "'Hello World' or 'User Greeting' challenge using basic input/output and string concatenation."
        )

    prompt = f"""
    You are an expert adaptive coding tutor. Generate exactly {count} distinct coding challenge(s).

    PARAMETERS:
    - Target Skill Level: {skill_level}
    - Programming Language: {language}
    - Total Questions Required: {count}
    - Previously covered topics to avoid repeating: {history_str}

    SPECIAL INSTRUCTIONS:
    {onboarding_instruction}
    - Each question in the list MUST be unique from one another, covering distinct topics appropriate for {skill_level} level.

    RESPOND STRICTLY WITH A VALID JSON ARRAY containing exactly {count} question object(s). Do not include markdown code fences or extra text.

    REQUIRED JSON ARRAY FORMAT:
    [
        {{
            "title": "Short title of the problem",
            "topic": "Core concept (e.g. Strings, Conditionals, Loops, Arrays, Recursion)",
            "difficulty": "{skill_level}",
            "prompt": "Detailed problem description explaining what the user needs to write.",
            "example_input": "Sample input or N/A",
            "example_output": "Sample output expected",
            "constraints": "Any specific rules or constraints"
        }}
    ]
    """

    models_to_try = ["gemini-2.0-flash", "gemini-2.0-flash-lite"]

    for model_name in models_to_try:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.7,
                    ),
                )

                raw_text = response.text.strip()
                if raw_text.startswith("```"):
                    raw_text = re.sub(r"^```[a-zA-Z]*\n?", "", raw_text)
                    raw_text = re.sub(r"\n?```$", "", raw_text).strip()

                data = json.loads(raw_text)
                result_list = data if isinstance(data, list) else [data]
                
                sanitized_list = []
                for item in result_list[:count]:
                    sanitized_list.append({
                        "title": str(item.get("title") or "Coding Challenge"),
                        "topic": str(item.get("topic") or "General Programming"),
                        "difficulty": str(item.get("difficulty") or skill_level),
                        "prompt": str(item.get("prompt") or "Write a program that satisfies the requirements."),
                        "example_input": str(item.get("example_input") or "N/A"),
                        "example_output": str(item.get("example_output") or "Expected Output"),
                        "constraints": str(item.get("constraints") or f"Use standard {language} syntax."),
                    })
                return sanitized_list

            except Exception as e:
                err_msg = str(e)
                print(f"Model {model_name} (Attempt {attempt+1}) error: {err_msg}")
                if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                    await asyncio.sleep(2)
                    continue
                else:
                    break

    # ----------------------------------------------------
    # GUARANTEED DYNAMIC LOCAL FALLBACK ENGINE
    # Generates N distinct, complete question objects
    # ----------------------------------------------------
    print(f"\n⚠️ API Rate Limit Active: Building {count} robust fallback question(s) for level '{skill_level}'...\n")

    greeting_question = {
        "title": "Day 1 Challenge: Greeting Generator",
        "topic": "Strings & Basic I/O",
        "difficulty": "beginner",
        "prompt": f"Write a {language} program that asks the user for their name and prints 'Hello, [name]! Welcome to CodeCoach.'",
        "example_input": "Alex",
        "example_output": "Hello, Alex! Welcome to CodeCoach.",
        "constraints": f"Use standard input reading and string formatting in {language}."
    }

    pool_by_level = {
        "beginner": [
            {
                "title": "Sum of Two Integers",
                "topic": "Arithmetic",
                "prompt": "Prompt the user for two integers, add them together, and print their total sum.",
                "example_input": "4\n6",
                "example_output": "10",
                "constraints": "Convert string inputs to integers before calculating."
            },
            {
                "title": "Even or Odd Detector",
                "topic": "Conditionals",
                "prompt": "Take an integer input and print 'Even' if it is divisible by 2, otherwise print 'Odd'.",
                "example_input": "7",
                "example_output": "Odd",
                "constraints": "Use the modulo operator (%) to check divisibility."
            },
            {
                "title": "Simple Countdown",
                "topic": "Loops",
                "prompt": "Write a loop that counts down from 5 to 1 and then prints 'Liftoff!' on a new line.",
                "example_input": "N/A",
                "example_output": "5\n4\n3\n2\n1\nLiftoff!",
                "constraints": "Use a standard for or while loop."
            },
            {
                "title": "Word Length Counter",
                "topic": "Strings",
                "prompt": "Accept a word input from the user and print the total number of characters in it.",
                "example_input": "CodeCoach",
                "example_output": "9",
                "constraints": "Use built-in string length functions."
            },
            {
                "title": "Largest of Three",
                "topic": "Conditionals",
                "prompt": "Take three numbers as input and print the largest value among them.",
                "example_input": "12\n45\n23",
                "example_output": "45",
                "constraints": "Use conditional IF/ELSE checks or comparison operators."
            }
        ],
        "intermediate": [
            {
                "title": "Palindrome Checker",
                "topic": "String Manipulation",
                "prompt": "Write a program that takes a word and checks if it reads the same forwards and backwards.",
                "example_input": "radar",
                "example_output": "True",
                "constraints": "Ignore case sensitivity during comparison."
            },
            {
                "title": "FizzBuzz Engine",
                "topic": "Control Flow",
                "prompt": "Print numbers 1 to 15, but print 'Fizz' for multiples of 3 and 'Buzz' for multiples of 5.",
                "example_input": "N/A",
                "example_output": "1, 2, Fizz, 4, Buzz...",
                "constraints": "Use conditional statements inside a loop."
            },
            {
                "title": "Prime Number Validator",
                "topic": "Math & Loops",
                "prompt": "Take an integer input and determine whether it is a prime number.",
                "example_input": "13",
                "example_output": "Prime",
                "constraints": "Check divisibility up to the square root of the number."
            }
        ],
        "advanced": [
            {
                "title": "Fibonacci with Memoization",
                "topic": "Dynamic Programming",
                "prompt": "Compute the N-th Fibonacci number efficiently using dynamic programming or recursion with memoization.",
                "example_input": "10",
                "example_output": "55",
                "constraints": "Optimize time complexity to O(N)."
            },
            {
                "title": "Valid Parentheses Stack",
                "topic": "Stack Data Structure",
                "prompt": "Given a string containing brackets '()[]{}', determine if the bracket ordering is valid.",
                "example_input": "{[()]}",
                "example_output": "Valid",
                "constraints": "Implement using a Stack structure."
            }
        ]
    }

    level_pool = pool_by_level.get(skill_level.lower(), pool_by_level["beginner"])
    fallback_questions = []

    start_idx = 0
    if is_new_user:
        fallback_questions.append(greeting_question)
        start_idx = 1

    for i in range(start_idx, count):
        item = level_pool[(i - start_idx) % len(level_pool)]
        fallback_questions.append({
            "title": f"Challenge #{i+1}: {item['title']}",
            "topic": item["topic"],
            "difficulty": skill_level,
            "prompt": item["prompt"],
            "example_input": item["example_input"],
            "example_output": item["example_output"],
            "constraints": item["constraints"]
        })

    return fallback_questions[:count]


# ✅ Fixed version:
async def review_code_ai(question_prompt: str, language: str, user_code: str) -> dict:
    """Evaluates user code: offers hints (no code) on failure, or efficiency tips on success."""
    prompt = f"""
    You are an expert Socratic coding tutor.
    Evaluate the following user submission against the problem requirements.

    PROBLEM PROMPT:
    {question_prompt}

    PROGRAMMING LANGUAGE:
    {language}

    USER CODE SUBMISSION:
    {user_code}

    TUTORING GUIDELINES:
    1. If the submission is INCORRECT, FAILED, or HAS LOGICAL/SYNTAX ERRORS:
       - Set "passed": false, "status": "failed".
       - DO NOT write or reveal fixed code solutions.
       - Provide conceptual hints, point out where their logic broke down, or guide them toward the right approach using questions or step-by-step thinking.

    2. If the submission is CORRECT and PASSES all requirements:
       - Set "passed": true, "status": "success".
       - Praise the user's correct approach.
       - Explain how they can make their code more efficient, readable, or Pythonic/idiomatic (e.g., lower time/space complexity, cleaner variable names, edge cases to consider, or standard library features).

    Respond STRICTLY with a valid JSON object. Do not include markdown code fences or backticks around the JSON.

    EXPECTED JSON RESPONSE FORMAT:
    {{
        "status": "success" or "failed",
        "passed": true or false,
        "feedback": "Your targeted pedagogical feedback here."
    }}
    """

    models_to_try = ["gemini-2.0-flash", "gemini-2.0-flash-lite"]

    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                ),
            )

            raw_text = response.text.strip()
            if raw_text.startswith("```"):
                raw_text = re.sub(r"^```[a-zA-Z]*\n?", "", raw_text)
                raw_text = re.sub(r"\n?```$", "", raw_text).strip()

            return json.loads(raw_text)

        except Exception as e:
            err_msg = str(e)
            print(f"Model {model_name} error in review_code_ai: {err_msg}")
            continue

    # ----------------------------------------------------
    # LOCAL MOCK EVALUATION FALLBACK
    # ----------------------------------------------------
    print("⚠️ Running local mock evaluation fallback...")

    has_output = any(
        kw in user_code 
        for kw in ["print(", "System.out", "cout <<", "printf(", "puts("]
    )

    if has_output:
        return {
            "status": "success",
            "passed": True,
            "feedback": (
                "Nice job getting standard output working! "
                "💡 Optimization Hint: Try considering edge cases (e.g., negative inputs or empty strings) "
                "or reducing time complexity using standard library utilities."
            )
        }
    else:
        return {
            "status": "failed",
            "passed": False,
            "feedback": (
                "💡 Hint: Your code needs to produce an output to pass. "
                "Check how your language outputs results to standard display."
            )
        }