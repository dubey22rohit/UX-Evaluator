from typing import List
from models.evaluation import AIResponse

from google.generativeai.types import GenerateContentResponse
import json

def convert_ai_response_to_json(response: GenerateContentResponse) -> List[AIResponse]:
    """
    Converts a GenerateContentResponse object (specifically for accessibility issues) to a JSON string.

    Args:
        response: The GenerateContentResponse object containing accessibility issues.

    Returns:
        A JSON dictionary representation of the issues.
    """

    # Assuming the issues are in the first candidate's text part
    try:
        issues_text = response.candidates[0].content.parts[0].text
        issues_data = json.loads(issues_text)  # Parse the JSON string
    except (IndexError, json.JSONDecodeError) as e:
        return json.loads("\"error\": f\"Could not extract or parse issues data: {e}\"")

    return issues_data