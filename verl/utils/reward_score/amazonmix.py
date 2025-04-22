import re
from typing import Dict, Tuple, Optional

def extract_solution(solution_str, method):
    # Split response to isolate assistant output
    if "Assistant:" in solution_str:
        processed_str = solution_str.split("Assistant:", 1)[1]
    elif "<|im_start|>assistant" in solution_str:
        processed_str = solution_str.split("<|im_start|>assistant", 1)[1]
    else:
        print("[Error] Failed to locate model response header")
        return None, solution_str

    # Extract final answer using XML-style tags
    answer_pattern = r'<answer>(.*?)</answer>'
    matches = list(re.finditer(answer_pattern, processed_str)) #, re.DOTALL

    if not matches:
        print("[Error] No valid answer tags found")
        return None, processed_str

    final_answer = matches[-1].group(1).strip()

    format1_match = re.search(r"([A-Z]):", final_answer)
    if format1_match:
        return format1_match.group(1).strip(), processed_str
    
    return final_answer, processed_str


def validate_response_structure(processed_str: str) -> bool:
    """Performs comprehensive validation of response structure.
    
    Args:
        processed_str: Processed response string from the model
        
    Returns:
        Boolean indicating whether all formatting requirements are met
    """
    print("\n[Structure Validation]")
    validation_passed = True

    # Check required tags
    tags = {
        'think_start': ('<think>', 1),
        'think_end': ('</think>', 1),
        'answer_start': ('<answer>', 1),
        'answer_end': ('</answer>', 1)
    }

    positions = {}
    for tag_name, (tag_str, expected_count) in tags.items():
        count = processed_str.count(tag_str)
        positions[tag_name] = pos = processed_str.find(tag_str)
        
        print(f"  {tag_str}: count={count}, position={pos}")
        
        if count != expected_count:
            print(f"  [Error] {tag_str} appears {count} times (expected {expected_count})")
            validation_passed = False

    # Verify tag order
    if (positions['think_start'] > positions['think_end'] or
        positions['think_end'] > positions['answer_start'] or
        positions['answer_start'] > positions['answer_end']):
        print("  [Error] Incorrect tag order: Expected <think>...</think><answer>...</answer>")
        validation_passed = False
    else:
        print("   Tag sequence validation passed")

    return validation_passed

def compute_score(solution_str: str, ground_truth: str, method='strict', format_reward: int = 1, answer_reward: float = 1.0):
    """Computes comprehensive score for model response.
    
    Args:
        solution_str: Raw model response string
        ground_truth: Dictionary containing ground truth data
        method: the method to extract the solution, choices are 'strict' and 'flexible'
        format_reward: Points awarded/deducted for format correctness
        answer_reward: Points awarded/deducted for answer correctness
        
    Returns:
        Total score (sum of format and answer rewards)
    """
    print("\n" + "="*80)
    print(" Processing New Sample ".center(80, '='))
    print(f"[Ground Truth]: {ground_truth}")

    # Extract model answer
    answer_text, processed_str= extract_solution(solution_str=solution_str, method=method)
    print(f"\n[Model Response]\n{processed_str}")
    print(f"\n[Processed Model Response]\n{answer_text}")

    # Validate response structure
    format_correct = validate_response_structure(processed_str)
    format_score = format_reward if format_correct else -abs(format_reward)
    print(f"\n  Format validation: {'PASS' if format_correct else 'FAIL'}")
    print(f"  Format score: {format_score}")

    # Validate answer content
    answer_score = 0
    if format_correct and answer_text:
        print(f"\n[Content Validation]")
        print(f"  Expected: {ground_truth}")
        print(f"  Predicted: {answer_text}")
        if answer_text == ground_truth:
            answer_score = 2       
            print("  Content validation: FULL MATCH")
        else:
            answer_score = -1.5
            print("  Content validation: MISMATCH")
    else:
        answer_score = -2
        print("\n[Content Validation] Skipped due to format errors or missing answer")

    total_score = format_score + answer_score
    print("\n" + "-"*80)
    print(f" Final Score ".center(80, '-'))
    print(f"  Format: {format_score}")
    print(f"  Answer: {answer_score}")
    print(f"  Total: {total_score}")
    print("="*80 + "\n")

    return total_score
