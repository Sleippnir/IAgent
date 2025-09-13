def send_to_reasoner(model_name: str, payload: dict) -> dict:
    prompt = f"""
EVALUATOR_SYSTEM_PROMPT = 

RUBRIC:
{payload['rubric']}

PINNED CONTEXT (digests):
JD: {payload['pinned_context']['jd_digest']}
CV: {payload['pinned_context']['candidate_digest']}
LinkedIn: {payload['pinned_context']['linkedin_digest']}
