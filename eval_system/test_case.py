from pydantic import BaseModel, Field
from typing import List, Dict, Literal
import textwrap

Severity = Literal["Low", "Medium", "High", "Critical"]
Pass_threshold = Literal[0, 1, 2, 3, 4, 5]


def field(name, value, width=88, indent="   "):
    label = f"{indent}{name}="

    if isinstance(value, list):
        if not value:
            return f"{label}[]"
                 
        lines = [f"{label}["]

        for item in value:
            lines.append(f"{indent}   {repr(item)}")

            lines.append(f"{indent}]")
            return "\n".join(lines)
            
    if isinstance(value, dict):
        if not value:
            return f"{label}{{}}"
                 
        lines = [f"{label}{{"]

        for key, item in value.items():
            item_label = f"{indent}   {key!r}"
            item_text = repr(item)
                    
            wrapped = textwrap.fill(
                item_text,
                width=width,
                initial_indent=item_label,
                subsequent_indent=" " * len(item_label),
            )
                     
            lines.append(wrapped + ",")

        lines.append(f"{indent}}}")
        return "\n".join(lines)
                 
    text = repr(value)

    if "\n" in text:
        return label + textwrap.indent(text, " " * len(label)).lstrip()
            
    wrapped = textwrap.fill(
        text,
        width=width,
        subsequent_indent=" " * len(label),
    )

    return label + wrapped


class ExpectedResult(BaseModel):
    finding: str
    explanation: str
    severity: Severity
    recommendation: str


    def __repr__(self):
        return "\n".join([
            "ExpectedResult(",
            field("finding", self.finding),
            field("explanation", self.explanation),
            field("severity", self.severity),
            field("recommendation", self.recommendation),
            ")",
        ])


class Assertions(BaseModel):
    required_phrases: List[str] = Field(default_factory=list)
    required_concepts: List[str] = Field(default_factory=list)
    prohibited_phrases: List[str] = Field(default_factory=list)
    prohibited_concepts: List[str] = Field(default_factory=list)
        

    def __repr__(self):
        return "\n".join([
            "Assertion(",
            field("required_phrases", self.required_phrases),
            field("required_concepts", self.required_concepts),
            field("prohibited_phrases", self.prohibited_phrases),
            field("prohibited_concepts", self.prohibited_concepts),
            ")",
        ])


class Testcase(BaseModel):
    id: str
    name: str
    category: str
    contract_type: str
    reviewer_perspective: str
    primary_skill_tested: str
    input_type: str
    input_text: str
    expected: ExpectedResult
    assertions: Assertions
    must_have_output_elements: List[str]
    should_not_say_avoid: List[str]
    fail_conditions: List[str]
    scoring_rubric: Dict[str, str]
    pass_threshold: int = 4
    evaluator_notes: str = ""


    def __repr__(self):
        return "\n".join([
            "Testcase(",
            field("id", self.id),
            field("name", self.name),
            field("category", self.category),
            field("contract_type", self.contract_type),
            field("reviewer_perspective", self.reviewer_perspective),
            field("primary_skill_tested", self.primary_skill_tested),
            field("input_type", self.input_type),
            field("input_text", self.input_text),
            field("expected", self.expected),
            field("assertions", self.assertions),
            field("must_have_output_elements", self.must_have_output_elements),
            field("should_not_say_avoid", self.should_not_say_avoid),
            field("fail_conditions", self.fail_conditions),
            field("scoring_rubric", self.scoring_rubric),
            field("pass_threshold", self.pass_threshold),
            field("evaluator_notes", self.evaluator_notes),
            ")",
        ])
    
