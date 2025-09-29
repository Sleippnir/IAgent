from ..domain.entities.interview import Interview
from .config import Settings
from .persistence.supabase.interview_repository import load_interview_from_supabase
import json
import os
from openai import OpenAI
import google.generativeai as genai
import asyncio

# Initialize settings
settings = Settings()

# --- Step 1: Data Loading Function ---

def load_interview_from_source(source_type: str, identifier: str) -> Interview:
    """
    Instantiates and populates an Interview object from a given data source.

    Args:
        source_type (str): The type of the data source. Can be 'file', 'supabase', or 'db'.
        identifier (str): The file path (for 'file') or a record ID (for 'supabase'/'db').

    Returns:
        Interview: A populated instance of the Interview class.
        
    Raises:
        ValueError: If the source_type is not supported.
        FileNotFoundError: If the file is not found for source_type 'file'.
    """
    print(f"Loading interview from {source_type} using identifier: {identifier}")
    
    if source_type == 'file':
        try:
            # Try multiple locations for the file
            possible_paths = [
                identifier,  # Original path
                f"examples/{identifier}",  # Check examples folder
                f"storage/{identifier}",  # Check storage folder
            ]
            
            file_found = False
            for path in possible_paths:
                try:
                    with open(path, 'r') as f:
                        data = json.load(f)
                        file_found = True
                        print(f"Successfully loaded file from: {path}")
                        break
                except FileNotFoundError:
                    continue
            
            if not file_found:
                raise FileNotFoundError(f"File not found at any of these locations: {possible_paths}")
            return Interview.from_dict(data)
        except FileNotFoundError:
            print(f"Error: File not found at {identifier}")
            raise
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {identifier}")
            raise
            
    elif source_type == 'supabase':
        # Use asyncio to run the async function
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        interview = loop.run_until_complete(load_interview_from_supabase(identifier))
        if interview:
            return interview
        else:
            raise ValueError(f"No interview found in Supabase with ID: {identifier}")
            
    elif source_type == 'db':
        # Legacy support - redirect to supabase
        print("'db' source type is deprecated, using 'supabase' instead.")
        return load_interview_from_source('supabase', identifier)
        
    else:
        raise ValueError(f"Unsupported source type: '{source_type}'. Use 'file', 'supabase', or 'db'.")

# --- Step 2: Evaluation Function ---

# --- Actual LLM API call implementations ---
# NOTE: Ensure you have set the following environment variables:
# OPENAI_API_KEY, GOOGLE_API_KEY, OPENROUTER_API_KEY

async def call_openai_gpt5(prompt, rubric, transcript):
    """Calls the OpenAI API to get an interview evaluation using GPT-5."""
    print(f"Calling OpenAI API ({settings.OPENAI_MODEL})...")
    try:
        # Use the API key from settings/environment
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in environment or configuration.")
            
        client = OpenAI(api_key=api_key)
        full_prompt = f"System Prompt: {prompt}\n\nEvaluation Rubric:\n{rubric}\n\nInterview Transcript:\n{transcript}\n\n---\nPlease provide your evaluation."
        
        # Prepare request parameters
        request_params = {
            "model": settings.OPENAI_MODEL,  # Use configured model (GPT-5)
            "messages": [{"role": "user", "content": full_prompt}],
        }
        
        # Handle GPT-5 specific parameters
        if settings.OPENAI_MODEL == "gpt-5":
            request_params["max_completion_tokens"] = settings.DEFAULT_MAX_TOKENS
            # GPT-5 only supports default temperature (1.0)
            # Don't set temperature parameter for GPT-5
        else:
            request_params["max_tokens"] = settings.DEFAULT_MAX_TOKENS
            request_params["temperature"] = settings.DEFAULT_TEMPERATURE
        
        response = client.chat.completions.create(**request_params)
        return response.choices[0].message.content
    except Exception as e:
        error_message = f"Error calling OpenAI API: {e}"
        print(error_message)
        return error_message

async def call_google_gemini(prompt, rubric, transcript):
    """Calls the Google Gemini API to get an interview evaluation."""
    print(f"Calling Google Gemini API ({settings.GEMINI_MODEL})...")
    try:
        api_key = settings.GOOGLE_API_KEY
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not set in environment or configuration.")
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel(settings.GEMINI_MODEL)  # Use configured model
        full_prompt = f"System Prompt: {prompt}\n\nEvaluation Rubric:\n{rubric}\n\nInterview Transcript:\n{transcript}\n\n---\nPlease provide your evaluation."
        
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        error_message = f"Error calling Google Gemini API: {e}"
        print(error_message)
        return error_message

async def call_openrouter_deepseek(prompt, rubric, transcript):
    """Calls DeepSeek via the OpenRouter API."""
    print(f"Calling OpenRouter API ({settings.DEEPSEEK_MODEL})...")
    try:
        api_key = settings.OPENROUTER_API_KEY
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not set in environment or configuration.")
            
        client = OpenAI(
            base_url=settings.OPENROUTER_BASE_URL,
            api_key=api_key,
        )
        full_prompt = f"System Prompt: {prompt}\n\nEvaluation Rubric:\n{rubric}\n\nInterview Transcript:\n{transcript}\n\n---\nPlease provide your evaluation."

        response = client.chat.completions.create(
            model=settings.DEEPSEEK_MODEL,  # Use configured model
            messages=[{"role": "user", "content": full_prompt}],
            max_tokens=settings.DEFAULT_MAX_TOKENS,
            temperature=settings.DEFAULT_TEMPERATURE
        )
        return response.choices[0].message.content
    except Exception as e:
        error_message = f"Error calling OpenRouter API: {e}"
        print(error_message)
        return error_message

async def run_evaluations(interview: Interview) -> Interview:
    """
    Populates the evaluation fields of an Interview object by calling LLMs.

    Args:
        interview (Interview): The interview object to be evaluated.

    Returns:
        Interview: The same interview object with evaluation fields populated.
    """
    print(f"\nRunning evaluations for interview ID: {interview.interview_id}")
    
    # Each LLM call uses the data from the interview object - properly await async calls
    interview.evaluation_1 = await call_openai_gpt5(
        interview.system_prompt, interview.rubric, interview.full_transcript
    )
    
    interview.evaluation_2 = await call_google_gemini(
        interview.system_prompt, interview.rubric, interview.full_transcript
    )
    
    interview.evaluation_3 = await call_openrouter_deepseek(
        interview.system_prompt, interview.rubric, interview.full_transcript
    )
    
    print("Evaluations completed.")
    return interview

async def get_structured_evaluation(interview):
    """
    Generate structured evaluation using rubric schema
    Returns structured JSON response based on the defined rubric
    """
    import json
    from datetime import datetime
    
    # Load the evaluation prompt template
    prompt_template = """
You are an expert technical/behavioral interviewer. Analyze this interview and provide a structured evaluation.

You MUST respond with valid JSON that follows this exact structure for {interview_type} interview:

{schema_example}

**Job Description:**
{job_description}

**Interview Transcript:**
{transcript}

Analyze carefully and provide structured evaluation in valid JSON format only. No additional text.
"""
    
    # Determine interview type based on content
    interview_type = "technical" if "algorithm" in interview.full_transcript.lower() or "code" in interview.full_transcript.lower() else "behavioral"
    
    # Create schema example based on interview type
    if interview_type == "technical":
        schema_example = """{
  "interview_type": "technical",
  "technical_evaluation": {
    "problem_understanding": {"score": "strong", "rationale": "explanation", "evidence": ["example1"]},
    "technical_skills": {"score": "very_strong", "rationale": "explanation", "evidence": ["example1"]},
    "rationale": {"score": "strong", "rationale": "explanation", "evidence": ["example1"]},
    "communication": {"score": "very_strong", "rationale": "explanation", "evidence": ["example1"]}
  },
  "overall_assessment": {
    "quantitative_score": 87.5,
    "score_calculation": "explanation",
    "recommendation": "hire",
    "key_strengths": ["strength1"],
    "areas_for_improvement": ["area1"],
    "summary": "summary"
  },
  "metadata": {
    "evaluator": "GPT-5",
    "evaluation_timestamp": "2025-09-29T10:30:00Z",
    "rubric_version": "v1.0"
  }
}"""
    else:
        schema_example = """{
  "interview_type": "behavioral",
  "behavioral_evaluation": {
    "question_understanding": {"score": "strong", "rationale": "explanation", "evidence": ["example1"]},
    "experience_competence": {"score": "strong", "rationale": "explanation", "evidence": ["example1"]},
    "self_awareness": {"score": "very_strong", "rationale": "explanation", "evidence": ["example1"]},
    "communication": {"score": "strong", "rationale": "explanation", "evidence": ["example1"]}
  },
  "overall_assessment": {
    "quantitative_score": 82.5,
    "score_calculation": "explanation",
    "recommendation": "hire",
    "key_strengths": ["strength1"],
    "areas_for_improvement": ["area1"],
    "summary": "summary"
  },
  "metadata": {
    "evaluator": "GPT-5",
    "evaluation_timestamp": "2025-09-29T10:30:00Z",
    "rubric_version": "v1.0"
  }
}"""
    
    # Format the prompt
    formatted_prompt = prompt_template.format(
        interview_type=interview_type,
        schema_example=schema_example,
        job_description=interview.jd,
        transcript=interview.full_transcript
    )
    
    try:
        # Call GPT-5 for structured evaluation
        response = await call_openai_gpt5(formatted_prompt, interview.rubric, "")
        
        # Parse JSON response
        evaluation_data = json.loads(response)
        
        # Add metadata if missing
        if "metadata" not in evaluation_data:
            evaluation_data["metadata"] = {
                "evaluator": "GPT-5",
                "evaluation_timestamp": datetime.now().isoformat() + "Z",
                "rubric_version": "v1.0"
            }
        
        return evaluation_data
        
    except json.JSONDecodeError as e:
        # If JSON parsing fails, return a structured error response
        return {
            "interview_type": interview_type,
            "overall_assessment": {
                "quantitative_score": 0,
                "score_calculation": "Error in evaluation process",
                "recommendation": "no_hire",
                "key_strengths": [],
                "areas_for_improvement": ["Evaluation could not be completed"],
                "summary": f"Structured evaluation failed: {str(e)}"
            },
            "metadata": {
                "evaluator": "GPT-5",
                "evaluation_timestamp": datetime.now().isoformat() + "Z",
                "rubric_version": "v1.0"
            }
        }
    except Exception as e:
        # Generic error handling
        return {
            "interview_type": interview_type,
            "overall_assessment": {
                "quantitative_score": 0,
                "score_calculation": "Error in evaluation process",
                "recommendation": "no_hire", 
                "key_strengths": [],
                "areas_for_improvement": ["Evaluation could not be completed"],
                "summary": f"Evaluation failed: {str(e)}"
            },
            "metadata": {
                "evaluator": "GPT-5",
                "evaluation_timestamp": datetime.now().isoformat() + "Z",
                "rubric_version": "v1.0"
            }
        }

async def get_mixed_evaluation_experimental(interview, custom_prompt=None, custom_schema=None):
    """
    EXPERIMENTAL: Generate structured evaluation for mixed interviews
    This is a separate function for testing mixed interview support
    Parameters can be passed externally to customize behavior
    """
    import json
    import re
    from datetime import datetime
    
    # Use custom prompt if provided, otherwise use default
    if custom_prompt is None:
        # Analyze transcript to determine interview type and content
        transcript_lower = interview.full_transcript.lower()
        
        # Technical indicators
        technical_keywords = [
            'algorithm', 'code', 'coding', 'implement', 'function', 'class', 
            'data structure', 'complexity', 'big o', 'debug', 'test case',
            'programming', 'software', 'technical problem', 'solution'
        ]
        
        # Behavioral indicators  
        behavioral_keywords = [
            'tell me about a time', 'describe a situation', 'how did you handle',
            'leadership', 'conflict', 'teamwork', 'challenge', 'failure',
            'star method', 'experience', 'example', 'situation', 'task', 'action', 'result'
        ]
        
        # Count occurrences
        technical_score = sum(1 for keyword in technical_keywords if keyword in transcript_lower)
        behavioral_score = sum(1 for keyword in behavioral_keywords if keyword in transcript_lower)
        
        # Determine interview type
        if technical_score > 0 and behavioral_score > 0:
            interview_type = "mixed"
            tech_weight = technical_score / (technical_score + behavioral_score)
            behavioral_weight = 1 - tech_weight
        elif technical_score > behavioral_score:
            interview_type = "technical"
            tech_weight = 1.0
            behavioral_weight = 0.0
        elif behavioral_score > technical_score:
            interview_type = "behavioral"
            tech_weight = 0.0
            behavioral_weight = 1.0
        else:
            # Default to mixed if unclear
            interview_type = "mixed"
            tech_weight = 0.5
            behavioral_weight = 0.5
        
        # Default prompt template
        custom_prompt = f"""
You are an expert interviewer analyzing a {interview_type} interview.

**Job Description:** {interview.jd}
**Rubric:** {interview.rubric}
**Interview Transcript:** {interview.full_transcript}

Provide structured evaluation in JSON format.
"""
    
    try:
        # Call GPT-5 for structured evaluation
        response = await call_openai_gpt5(custom_prompt, "", "")
        
        # If custom schema provided, validate against it
        # Otherwise use default parsing
        evaluation_data = json.loads(response)
        
        return evaluation_data
        
    except Exception as e:
        return {
            "error": f"Experimental evaluation failed: {str(e)}",
            "interview_type": "unknown",
            "metadata": {
                "evaluator": "GPT-5-Experimental",
                "evaluation_timestamp": datetime.now().isoformat() + "Z",
                "note": "This is an experimental function"
            }
        }

# --- Main Execution Block: Example Workflow ---

if __name__ == '__main__':
    # Example 1: Using file-based storage
    print("=== File-based Example ===")
    
    # Create a dummy JSON file to act as our data source
    dummy_data = {
        "interview_id": "file-xyz-789",
        "system_prompt": "You are a hiring manager.",
        "rubric": "Score technical skills from 1-5.",
        "jd": "Senior Python Developer role.",
        "full_transcript": "Interviewer: Tell me about a time... Candidate: Sure, there was a project where..."
    }
    file_path = os.path.join(settings.STORAGE_PATH, "interviews", settings.SAMPLE_INTERVIEW_FILE)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w') as f:
        json.dump(dummy_data, f, indent=2)

    # 1. Load the interview object from the file
    try:
        my_interview = load_interview_from_source(source_type='file', identifier=file_path)
        print("\n--- Interview Object Loaded from File ---")
        print(my_interview)
        print(f"Job Description: {my_interview.jd}")

        # 2. Run the evaluations on the loaded object
        evaluated_interview = run_evaluations(my_interview)

        # 3. Display the final object with evaluations filled in
        print("\n--- Interview Object After Evaluation ---")
        print(evaluated_interview)
        print(f"Evaluation 1: {evaluated_interview.evaluation_1}")
        print(f"Evaluation 2: {evaluated_interview.evaluation_2}")
        print(f"Evaluation 3: {evaluated_interview.evaluation_3}")

    except (ValueError, FileNotFoundError) as e:
        print(f"File workflow failed: {e}")
    
    # Example 2: Using Supabase storage (commented out - requires valid API keys)
    """
    print("\n=== Supabase Example ===")
    
    try:
        # Create a sample interview for Supabase
        sample_interview = Interview(
            interview_id="supabase-abc-123",
            system_prompt="You are a technical interviewer.",
            rubric="Evaluate on technical skills, communication, and culture fit.",
            jd="Senior Software Engineer - Python/FastAPI",
            full_transcript="Detailed interview transcript here..."
        )
        
        # Save to Supabase
        from .persistence.supabase.interview_repository import save_interview_to_supabase
        import asyncio
        
        loop = asyncio.get_event_loop()
        saved_interview = loop.run_until_complete(save_interview_to_supabase(sample_interview))
        print(f"Saved interview to Supabase: {saved_interview.interview_id}")
        
        # Load from Supabase
        loaded_interview = load_interview_from_source('supabase', 'supabase-abc-123')
        print(f"Loaded interview from Supabase: {loaded_interview.interview_id}")
        
        # Run evaluations
        evaluated_interview = run_evaluations(loaded_interview)
        
        # Save the evaluated interview back to Supabase
        final_interview = loop.run_until_complete(save_interview_to_supabase(evaluated_interview))
        print(f"Saved evaluated interview to Supabase: {final_interview.interview_id}")
        
    except Exception as e:
        print(f"Supabase workflow failed: {e}")
    """

