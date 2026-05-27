import yaml
import json
from pathlib import Path
from test_case import Testcase, ExpectedResult, Assertions
from prompts import construct_test_prompt
from openai_client import generate_response
from vector_store import get_or_create_vector_store
from scoring import score_response


def run_workflow(assistant_key):
    assistant_path = Path(f"..\\assistants\\{assistant_key}.yaml")

    with open(assistant_path, encoding="utf-8", mode="r") as read_file:
        assistant_contents = yaml.safe_load(read_file)

    system_prompt_path = Path(f"..\\system_prompts\\{assistant_key}.txt")
    with open(system_prompt_path, "r", encoding="utf-8") as f:
        system_prompt = f.read()

    vector_store_id = get_or_create_vector_store(assistant_key=assistant_key)

    test_dir = Path("..\\test_cases\\contract_review")
    test_files = sorted(test_dir.glob("GEN-*.yaml"))

    results = []

    for test_file in test_files:
        print(f"Running test {test_file.name}")
        
        with open(f"{test_dir}\\{test_file.name}", encoding="utf-8", mode='r') as read_file:
            test_case_contents = yaml.safe_load(read_file)

        current_test_expected = ExpectedResult(
            finding=test_case_contents["expected"]["finding"],
            explanation=test_case_contents["expected"]["explanation"],
            severity=test_case_contents["expected"]["severity"],
            recommendation=test_case_contents["expected"]["recommendation"]
        )
        
        current_test_assertions = Assertions(
            required_phrases=test_case_contents["assertions"]["required_phrases"],
            required_concepts=test_case_contents["assertions"]["required_concepts"],
            prohibited_phrases=test_case_contents["assertions"]["prohibited_phrases"],
            prohibited_concepts=test_case_contents["assertions"]["prohibited_concepts"]
        )

        current_test = Testcase(
            id=test_case_contents["id"],
            name=test_case_contents["name"],
            category=test_case_contents["category"],
            contract_type=test_case_contents["contract_type"],
            reviewer_perspective=test_case_contents["reviewer_perspective"],
            primary_skill_tested=test_case_contents["primary_skill_tested"],
            input_type=test_case_contents["input_type"],
            input_text=test_case_contents["input_text"],
            expected=current_test_expected,
            assertions=current_test_assertions,
            must_have_output_elements=test_case_contents["must_have_output_elements"],
            should_not_say_avoid=test_case_contents["should_not_say_avoid"],
            fail_conditions=test_case_contents["fail_conditions"],
            scoring_rubric=test_case_contents["scoring_rubric"],
            pass_threshold=test_case_contents["pass_threshold"],
            evaluator_notes=test_case_contents["evaluator_notes"]
        )

        test_prompt = construct_test_prompt(testcase=current_test)
        
        response = generate_response(
            model=assistant_contents["model"],
            system_prompt=system_prompt,
            user_prompt=test_prompt,
            vector_store_id=vector_store_id
        )

        response_dict = json.loads(response)

        test_result = score_response(current_test=current_test, model_response=response_dict)

        test_result["name"] = current_test.name
        
        results.append(test_result)

    return results
