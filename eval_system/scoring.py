import json
from rapidfuzz import fuzz, utils
from openai_client import get_client
from prompts import construct_rel_lang_prompt, construct_llm_judge_prompt
from scoring_weights import SCORING_WEIGHTS


def score_relevant_language(testcase, model_response):

    client = get_client()
    
    model_rel_lang_str = " ".join(model_response["relevant_language"])
    rel_lang_str = " ".join(testcase.assertions.required_phrases)
    
    fuzz_score = fuzz.WRatio(model_rel_lang_str, rel_lang_str, processor=utils.default_process)

    if fuzz_score >= 0.9:
        return {
            "passed": True,
            "score": 5,
            "method": "fuzzy matching",
            "model_relevant_language": model_response["relevant_language"],
            "relevant_language": testcase.assertions.required_phrases,
            "explanation": "Fuzzy matching scored high enough for automatic pass."
        }        

    user_prompt = construct_rel_lang_prompt(testcase=testcase, model_response=model_response, fuzz_result=fuzz_score) 

    system_prompt = """
        You are a strict contract-review evaluation judge. Your only job is to determine whether the model 
        response cited required contract language with sufficient fidelity. Do not evaluate the overall legal
        analysis, recommendation, severity, or writing quality. Be conservative. Return only valid JSON matching 
        the requested schema.
        """

    response = client.responses.create(
        model="gpt-5.2",
        instructions=system_prompt,
        input=user_prompt,
        tools=None,
    )

    return json.loads(response)


def score_severity(model_severity, expected_severity):
    if model_severity == expected_severity:
        return {
            "passed": True,
            "score": 5,
            "model_severity": model_severity,
            "expected_severity": expected_severity,
            "explanation": "Model severity exactly matched expected severity."
        } 
    
    return {
        "passed": False,
        "score": 0,
        "model_severity": model_severity,
        "expected_severity": expected_severity,
        "explanation": "Model severity did NOT exactly match expected severity."
    }


def call_llm_judge(test_case, model_response, deterministic_check_results):

    client = get_client()

    system_prompt = f"""
You are a strict contract-review evaluation judge.
Evaluate the model response only against the provided test case, deterministic check results, and scoring instructions.
Do not use outside facts, assume missing context, or reward generic advice that does not address the specific test case.
Be conservative when evaluating hard gates. Return only valid JSON matching the requested schema, with no markdown,
commentary, or text outside the JSON.
"""

    user_prompt = construct_llm_judge_prompt(test_case=test_case,
                                             model_response=model_response,
                                             deterministic_check_results=deterministic_check_results)
    
    response = client.responses.create(model="gpt-5.2",
                                       instructions=system_prompt,
                                       input=user_prompt,
                                       tools=None)
    
    return json.loads(response.output_text)


def calculate_overall_score(current_test, llm_judge_response):
    primary_skill_tested = current_test.primary_skill_tested
    primary_skill_tested = primary_skill_tested.partition("/")[0].rstrip()

    weights = SCORING_WEIGHTS[primary_skill_tested] 

    scores = {
        "relevant_language": llm_judge_response["deterministic_checks"]["relevant_language_results"]["score"],
        "severity": llm_judge_response["deterministic_checks"]["severity_results"]["score"],
        "finding": llm_judge_response["dimension_scores"]["finding"]["score"],
        "explanation": llm_judge_response["dimension_scores"]["explanation"]["score"],
        "recommendation": llm_judge_response["dimension_scores"]["recommendation"]["score"]
    }

    overall_score = (
    sum(scores[key] * weights[key] for key in scores)
    / sum(weights[key] for key in scores))

    if overall_score >= llm_judge_response["pass_threshold"] and not llm_judge_response["triggered_fail_conditions"] and not llm_judge_response["failed_hard_gates"]:
        passed = True
    else:
        passed = False

    return overall_score, passed


def score_response(current_test, model_response):
    rel_lang_results = score_relevant_language(testcase=current_test, model_response=model_response)
                                             
    severity_results = score_severity(model_severity=model_response["severity"],
                                      expected_severity=current_test.expected.severity)
    
    deterministic_check_results = {"relevant_language_results": rel_lang_results,
                                   "severity_results": severity_results}
    
    llm_judge_response = call_llm_judge(test_case=current_test,
                                        model_response=model_response,
                                        deterministic_check_results=deterministic_check_results)
    
    llm_judge_response["deterministic_checks"] = deterministic_check_results

    overall_score, passed = calculate_overall_score(current_test=current_test, llm_judge_response=llm_judge_response)

    llm_judge_response["final_score"] = overall_score
    llm_judge_response["passed"] = passed

    return llm_judge_response


