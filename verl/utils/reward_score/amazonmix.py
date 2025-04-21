import re


def extract_solution(solution_str, method):
    # First, try to match Format 1 (single letter followed by colon)
    format1_match = re.search(r"####\s+([A-Z]):", solution_str)
    if format1_match:
        return format1_match.group(1)  # Return just the letter
    
    # For other formats, extract everything after ####
    general_match = re.search(r"####\s+(.*?)(?=\n|$)", solution_str)
    if general_match:
        return general_match.group(1).strip()
    
    return None


def compute_score(solution_str, ground_truth, method='strict', format_score=0.1, score=1.):
    """The scoring function for GSM8k.
    Args:
        solution_str: the solution text
        ground_truth: the ground truth
        method: the method to extract the solution, choices are 'strict' and 'flexible'
        format_score: the score for the format
        score: the score for the correct answer
    """
    answer = extract_solution(solution_str=solution_str, method=method)
    if answer is None:
        return 0
    else:
        if answer == ground_truth:
            return 1.0
        else:
            return 0