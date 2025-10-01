"""
Interview domain entity for managing interview evaluation data.
"""
import json
from typing import Optional


class Interview:
    """
    A domain entity to store and manage interview data for LLM evaluation.

    This class holds all the necessary components for an interview evaluation task,
    including the system prompt for the LLM, the evaluation rubric, the job
    description, the interview transcript, and placeholders for multiple
    LLM evaluations. It also includes methods for serialization to and from
    dictionaries, which is useful for file or database storage.
    """

    def __init__(self, system_prompt=None, rubric=None, jd=None, full_transcript=None, interview_id=None):
        """
        Initializes the Interview object with mock data or provided values.

        Args:
            system_prompt (str, optional): The system prompt for the LLM.
                                           Defaults to a mock prompt if not provided.
            rubric (str, optional): The evaluation rubric. Defaults to a mock rubric.
            jd (str, optional): The job description. Defaults to a mock JD.
            full_transcript (str, optional): The full interview transcript.
                                             Defaults to a mock transcript.
            interview_id (str, optional): A unique identifier for the interview.
        """
        self.interview_id = interview_id
        self.system_prompt = system_prompt if system_prompt is not None else self._default_system_prompt()
        self.rubric = rubric if rubric is not None else self._default_rubric()
        self.jd = jd if jd is not None else self._default_jd()
        self.full_transcript = full_transcript if full_transcript is not None else self._default_full_transcript()

        # Evaluations are initialized as empty and are meant to be populated by an LLM.
        self.evaluation_1 = None
        self.evaluation_2 = None
        self.evaluation_3 = None

    def _default_system_prompt(self):
        """Returns a default system prompt for the LLM."""
        return (
            "You are an expert technical recruiter and hiring manager. "
            "Your task is to evaluate the provided interview transcript based on the "
            "job description and the rubric. Provide a detailed, constructive, and "
            "unbiased evaluation. Assess the candidate's technical skills, "
            "communication abilities, and overall fit for the role. "
            "Provide scores for each category in the rubric and a final summary."
        )

    def _default_rubric(self):
        """Returns a default evaluation rubric."""
        return (
            "**Evaluation Rubric:**\n\n"
            "1. **Technical Proficiency (1-10):**\n"
            "   - Understanding of core concepts.\n"
            "   - Problem-solving approach.\n"
            "   - Code quality and efficiency.\n\n"
            "2. **Communication Skills (1-10):**\n"
            "   - Clarity of explanations.\n"
            "   - Ability to articulate thought process.\n"
            "   - Professionalism and active listening.\n\n"
            "3. **Cultural Fit (1-10):**\n"
            "   - Alignment with company values (collaboration, innovation).\n"
            "   - Enthusiasm for the role and company.\n"
        )

    def _default_jd(self):
        """Returns a default job description."""
        return (
            "**Job Description: Senior Software Engineer**\n\n"
            "We are looking for a Senior Software Engineer with 5+ years of experience "
            "in Python development. The ideal candidate will have a strong background "
            "in building scalable web applications, working with cloud services (AWS/GCP), "
            "and experience with containerization technologies like Docker. "
            "Responsibilities include designing and implementing new features, mentoring "
            "junior engineers, and contributing to a collaborative team environment."
        )

    def _default_full_transcript(self):
        """Returns a default interview transcript."""
        return (
            "**Interviewer:** 'Hi, thanks for joining. Can you start by telling me about "
            "a challenging project you've worked on?'\n\n"
            "**Candidate:** 'Sure. In my last role, I was tasked with refactoring a monolithic "
            "legacy service into a microservices architecture. The main challenge was "
            "ensuring zero downtime during the migration. We used a strangler fig pattern "
            "to gradually move traffic to the new services. It was complex but ultimately "
            "successful.'\n\n"
            "**Interviewer:** 'That sounds interesting. How would you handle a disagreement "
            "with a colleague about a technical implementation?'\n\n"
            "**Candidate:** 'I believe in open communication. I'd first listen to their "
            "perspective to fully understand their reasoning. Then, I would present my "
            "viewpoint with supporting data or examples. The goal is to find the best "
            "solution for the project, not to 'win' an argument. If we still can't agree, "
            "we could involve a third party, like a tech lead, for a final decision.'"
        )

    def to_dict(self):
        """Serializes the object to a dictionary."""
        return {
            'interview_id': self.interview_id,
            'system_prompt': self.system_prompt,
            'rubric': self.rubric,
            'jd': self.jd,
            'full_transcript': self.full_transcript,
            'evaluation_1': self.evaluation_1,
            'evaluation_2': self.evaluation_2,
            'evaluation_3': self.evaluation_3,
        }

    @classmethod
    def from_dict(cls, data):
        """Creates an Interview object from a dictionary."""
        interview = cls(
            interview_id=data.get('interview_id'),
            system_prompt=data.get('system_prompt'),
            rubric=data.get('rubric'),
            jd=data.get('jd'),
            full_transcript=data.get('full_transcript')
        )
        interview.evaluation_1 = data.get('evaluation_1')
        interview.evaluation_2 = data.get('evaluation_2')
        interview.evaluation_3 = data.get('evaluation_3')
        return interview

    def __repr__(self):
        """Provides a developer-friendly string representation of the object."""
        return (
            f"Interview(id={self.interview_id}, "
            f"eval_1_populated={self.evaluation_1 is not None}, "
            f"eval_2_populated={self.evaluation_2 is not None}, "
            f"eval_3_populated={self.evaluation_3 is not None})"
        )


# Example of how to use the class
if __name__ == '__main__':
    # 1. Create an instance and give it an ID
    interview_case = Interview(interview_id="abc-123")
    interview_case.evaluation_1 = "Candidate shows strong potential."

    print("--- Original Object ---")
    print(interview_case)
    print(f"Evaluation 1: {interview_case.evaluation_1}")

    # 2. Serialize the object to a dictionary (e.g., to save as JSON or in a DB)
    interview_dict = interview_case.to_dict()
    print("\n--- Serialized to Dictionary ---")
    print(json.dumps(interview_dict, indent=2))

    # 3. Deserialize from the dictionary back into a new object
    rehydrated_interview = Interview.from_dict(interview_dict)
    print("\n--- Rehydrated Object from Dictionary ---")
    print(rehydrated_interview)
    print(f"ID: {rehydrated_interview.interview_id}")
    print(f"JD: {rehydrated_interview.jd[:50]}...")
    print(f"Evaluation 1: {rehydrated_interview.evaluation_1}")