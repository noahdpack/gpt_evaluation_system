import json


def construct_test_prompt(testcase):
    output_structure = {
        "issue_title": "",
        "finding": "",
        "relevant_language": [],
        "explanation": "",
        "severity": "Low",
        "recommendation": "",
        "reviewer_perspective_applied": ""
    }

    no_issue_structure = {
        "issue_title": "",
        "finding": "",
        "relevant_language": [],
        "explanation": "",
        "severity": None,
        "recommendation": "",
        "reviewer_perspective_applied": ""
    }

    return f"""
You are reviewing contract material for legal, commercial, operational, and drafting issues.

Reviewer perspective: {testcase.reviewer_perspective}
Contract type: {testcase.contract_type}
Input type: {testcase.input_type}

Task:
Review the provided contract material and identify the primary contract review issue that matters from the stated reviewer perspective.

Focus only on the issue supported by the provided material. Do not invent facts, assume missing context, or rely on outside information.

If no contract review issue is present, return a JSON object with all substantive fields empty and severity set to null.

Return only valid JSON matching this structure:

{json.dumps(output_structure, indent=2)}

Field requirements:

- issue_title:
  A short, specific title for the primary issue. It should identify the actual contract concern, not use a generic label.
  Good: "Inconsistent Legal Entity Names"
  Bad: "Drafting Issue"

- finding:
  A concise statement of the issue found in the contract material. State what is problematic, missing, inconsistent, ambiguous, or risky.

- relevant_language:
  An array of exact quotes from the provided material that support the finding. Each quote must appear verbatim in the provided material. Do not paraphrase. Do not quote language that is not in the text. Include only the language necessary to support the issue.

- explanation:
  Explain why the issue matters legally, commercially, operationally, or from a drafting perspective. Tie the explanation to the reviewer perspective and the quoted language. Do not overstate the consequence.

- severity:
  Assign one of: "Low", "Medium", "High", or "Critical".
  Use:
  - "Low" for minor drafting, clarity, or low-impact issues.
  - "Medium" for meaningful negotiation, operational, or commercial risk that is manageable.
  - "High" for significant legal, financial, compliance, or business risk.
  - "Critical" only for severe risk that could create major exposure, block execution, or require escalation before signing.
  If no issue is present, use null.

- recommendation:
  Give a practical next step from the reviewer perspective. This may include revising language, asking for clarification, negotiating a limitation, escalating internally, accepting the risk, or confirming business intent. The recommendation must address the specific issue found.

- reviewer_perspective_applied:
  Explain how the issue affects the stated reviewer perspective. Do not merely repeat the perspective label. The substance of the analysis must reflect the correct side of the contract.

Important rules:
- Return only valid JSON.
- Do not include markdown, comments, or explanatory text outside the JSON.
- Identify only the primary contract review issue.
- Do not return an array of issues.
- Quote only language that appears in the provided material.
- Do not assume missing facts.
- Do not identify risks that only affect the counterparty unless they also matter to the stated reviewer perspective.
- Do not overstate legal consequences, such as saying language is automatically unenforceable unless that is directly supported.
- Do not give generic advice. Recommendations should be specific to the issue.
- If multiple related facts support the same issue, combine them into one finding.
- If there are several possible issues, choose the most important issue supported by the provided material.

If no issue is present, return exactly:

{json.dumps(no_issue_structure, indent=2)}

Provided material:
{testcase.input_text}
"""


def construct_rel_lang_prompt(testcase, model_response, fuzz_result):
    output_structure = {
        "passed": True,
        "score": 5,
        "model_relevant_language": [],
        "required_language": "",
        "method": "LLM judge fallback",
        "explanation": ""
    }

    return f"""
You are evaluating whether a contract review response sufficiently cited required contract language.

Your task is narrow:
Decide whether the model response cited, quoted, or clearly identified language from the provided contract material that is materially equivalent to the required language.

You are NOT scoring the overall answer.
You are NOT evaluating the legal analysis.
You are NOT deciding whether the finding, explanation, severity, or recommendation is correct.
Only evaluate whether the required language requirement is satisfied.

Inputs:

Reviewer perspective:
{testcase.reviewer_perspective}

Contract type:
{testcase.contract_type}

Input material:
{testcase.input_text}

Required language:
{json.dumps(testcase.assertions.rel_lang, indent=2)}

Model response relevant_language field:
{json.dumps(model_response.get("relevant_language", []), indent=2)}

Optional full model response for context:
{json.dumps(model_response, indent=2)}

Deterministic match result:
{json.dumps(fuzz_result, indent=2, default=str)}

Evaluation rules:

1. The required language passes if the response quotes or identifies contract language that is materially the same as the required language.

2. The response does not need to reproduce the required language perfectly. Minor differences are acceptable, including:
   - punctuation differences
   - capitalization differences
   - omitted nonessential words
   - line break or whitespace differences
   - singular/plural differences
   - shortened quote that still captures the legally or commercially important language
   - quote split across multiple entries in the relevant_language array

3. The response fails if:
   - it does not cite the required language at all
   - it only paraphrases the concept without pointing to the contract language
   - it cites unrelated language
   - it omits the key legally or commercially important words
   - it changes the meaning of the required language
   - it quotes language that does not appear in the input material
   - it relies on facts or language outside the provided material

4. Be stricter when the required language contains:
   - party names
   - defined terms
   - dollar amounts
   - dates or deadlines
   - notice periods
   - liability caps
   - exclusions
   - exceptions
   - conditions
   - remedies
   - governing standards
   - words like “sole,” “exclusive,” “unlimited,” “reasonable,” “material,” “may,” “shall,” “must,” or “including”

5. A paraphrase alone should usually fail. This check is about whether the response cited the relevant contract language, not merely whether it understood the concept.

6. If the response includes a quote that is close but omits a critical qualifier, condition, exception, party, amount, or deadline, mark it as failed.

Return only valid JSON.
Do not include markdown.
Do not include code fences.
Do not include commentary before or after the JSON.

Return JSON matching this exact structure:

{json.dumps(output_structure, indent=2)}
"""


def construct_llm_judge_prompt(test_case, model_response, deterministic_check_results):
    output_structure = {
        "id": test_case.id,
        "dimension_scores": {
            "finding": {
                "score": 0,
                "model_response": "",
                "explanation": ""
            },
            "explanation": {
                "score": 0,
                "model_response": "",
                "explanation": ""
            },
            "recommendation": {
                "score": 0,
                "model_response": "",
                "explanation": ""
            }
        },
        "hard_gates": {
            "reviewer_perspective": {
                "passed": True,
                "explanation": "",
                "detected_perspective": ""
            },
            "material_hallucination": {
                "passed": True,
                "explanation": "",
                "invented_or_unsupported_items": []
            },
            "primary_issue": {
                "passed": True,
                "explanation": ""
            },
            "harmful_recommendation": {
                "passed": True,
                "explanation": "",
                "harmful_recommendation_items": []
            },
            "prohibited_concepts": {
                "passed": True,
                "explanation": "",
                "triggered_items": []
            }
        },
        "required_concepts_assessment": {
            "satisfied_concepts": [],
            "missing_concepts": [],
            "explanation": ""
        },
        "must_have_output_elements_assessment": {
            "satisfied_elements": [],
            "missing_elements": [],
            "explanation": ""
        },
        "triggered_fail_conditions": [],
        "failed_hard_gates": [],
        "pass_threshold": test_case.pass_threshold,
        "overall_judge_explanation": "",
        "judge_confidence": "high"
    }

    return f"""
You are evaluating a contract review model response for one test case.

You are not reviewing the contract from scratch. You are judging whether the model response satisfies the provided test case.

INPUTS

Test case:
{test_case}

Model response:
{json.dumps(model_response, indent=2)}

Deterministic check results:
{json.dumps(deterministic_check_results, indent=2)}

SCORING TASK

Score only these weighted dimensions:
- finding
- explanation
- recommendation

Do not score relevant_language or severity. Those are handled by deterministic checks.

Do not score reviewer perspective, hallucination control, harmful recommendation, primary issue, or prohibited concepts as weighted dimensions. They are hard gates.

Use the test case's expected answer, assertions, must-have output elements, should-not-say/avoid items, fail conditions, scoring rubric, reviewer perspective, and evaluator notes when judging the response.

Each weighted dimension must receive an integer score from 0 to 5.

For each dimension_scores item:
- score should be your score from 0 to 5.
- model_response should copy the relevant text from the model response for that dimension.
- explanation should explain why you gave that score.

Return only valid JSON.
Do not include markdown.
Do not include code fences.
Do not include commentary before or after the JSON.

Return JSON matching this exact structure:

{json.dumps(output_structure, indent=2)}
"""
   