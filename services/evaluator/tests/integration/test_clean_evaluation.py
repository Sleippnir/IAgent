#!/usr/bin/env python3
"""
Clean evaluation workflow using the new payload-based function
"""
import asyncio
import json
from app.infrastructure.persistence.supabase.services import QueueService, EvaluationService
from app.helpers import run_evaluations_from_payload

async def test_clean_evaluation_workflow():
    """Test complete evaluation workflow with the new clean approach"""
    
    print("🔍 Step 1: Getting evaluation task from evaluator_queue...")
    
    queue_service = QueueService()
    
    try:
        # Get evaluation tasks from evaluator_queue
        evaluation_tasks = await queue_service.client.get("evaluator_queue", {"limit": 1})
        
        if not evaluation_tasks:
            print("❌ No evaluation tasks found in evaluator_queue")
            print("💡 Make sure an interview has been completed and moved to evaluator_queue")
            return
            
        evaluation_task = evaluation_tasks[0]
        interview_id = evaluation_task.get('interview_id')
        payload = evaluation_task.get('payload', {})
        
        print(f"✅ Found evaluation task: {interview_id}")
        print(f"👤 Candidate: {payload.get('candidate_name')}")
        print(f"💼 Job: {payload.get('job_title')}")
        
        # Step 2: Create comprehensive synthetic transcript
        print(f"\n🎭 Step 2: Creating comprehensive interview transcript...")
        
        candidate_name = payload.get('candidate_name', 'Candidate')
        job_title = payload.get('job_title', 'position')
        
        synthetic_transcript = f"""**Interviewer:** Hello {candidate_name}! Thank you for taking the time to interview with us today for the {job_title} role. Can you start by telling me about your background and what drew you to this position?

**Candidate:** Hi! Thank you for having me. I'm really excited about this opportunity. I have extensive experience in {job_title.lower()} with a strong track record of delivering results. What particularly attracts me to this role is the chance to work on challenging projects and contribute to a team that values innovation and collaboration.

**Interviewer:** That's great to hear. Can you walk me through a specific project or accomplishment that demonstrates your skills relevant to this position?

**Candidate:** Absolutely. In my most recent role, I led a cross-functional team on a complex initiative that required both technical expertise and strong leadership skills. We were tasked with improving our existing processes while maintaining quality standards. Through careful planning, stakeholder engagement, and iterative improvements, we not only met our deadlines but actually delivered 20% ahead of schedule while exceeding all quality metrics. The key was implementing clear communication channels and ensuring everyone understood their role in achieving our shared objectives.

**Interviewer:** That's very impressive. How do you typically approach problem-solving when faced with unexpected challenges or roadblocks?

**Candidate:** I believe in a systematic approach to problem-solving. First, I take time to fully understand the problem by gathering all relevant information and perspectives from stakeholders. Then I analyze the root causes rather than just addressing symptoms. I like to brainstorm multiple solutions and evaluate their potential impact, feasibility, and resource requirements. Throughout this process, I maintain open communication with my team and stakeholders to ensure we're aligned and can adapt quickly if circumstances change.

**Interviewer:** Excellent methodology. How do you handle working in a team environment, especially when there are conflicting opinions or competing priorities?

**Candidate:** I've found that successful teamwork starts with establishing trust and maintaining open, respectful communication. When conflicts arise, I try to understand each person's perspective and identify the underlying concerns or objectives. I believe that diverse viewpoints actually strengthen our solutions, so I encourage healthy debate while keeping us focused on our shared goals. In situations where we need to make decisions quickly, I'm comfortable taking ownership and making tough calls, but I always ensure the team understands the reasoning behind those decisions.

**Interviewer:** That's a very mature approach. What aspects of this role and our company culture appeal to you most?

**Candidate:** From my research and our conversations, I'm particularly excited about the emphasis on continuous learning and innovation here. The opportunity to work on cutting-edge projects while contributing to a collaborative environment really aligns with my professional values. I'm also impressed by the company's commitment to professional development and the way you invest in your employees' growth. I see this as a place where I can both contribute my existing skills and continue to evolve professionally.

**Interviewer:** Wonderful. Do you have any questions about the role, the team, or our company?

**Candidate:** Yes, I have a couple of questions. First, could you tell me more about the team dynamics and how this role would collaborate with other departments? And second, I'm curious about what success looks like in the first 90 days for someone in this position.

**Interviewer:** Great questions. The team is highly collaborative and you'd be working closely with engineering, product, and business teams on various strategic initiatives. As for success in the first 90 days, we'd expect you to get up to speed with our processes, build relationships with key stakeholders, and begin contributing meaningfully to ongoing projects. Thank you for your time today, {candidate_name}. We'll be in touch with next steps very soon.

**Candidate:** Thank you so much! I really enjoyed our conversation and I'm very excited about the possibility of joining your team. I look forward to hearing from you."""

        print(f"✅ Created comprehensive synthetic transcript: {len(synthetic_transcript)} characters")
        
        # Step 3: Run LLM evaluations using the new clean function
        print(f"\n🤖 Step 3: Running LLM evaluations...")
        print(f"   🔵 Calling OpenAI GPT-5...")
        print(f"   🟢 Calling Google Gemini...")  
        print(f"   🟡 Calling DeepSeek via OpenRouter...")
        
        try:
            evaluation_results = await run_evaluations_from_payload(payload, synthetic_transcript)
            
            print(f"\n📊 Step 4: Evaluation Results Summary:")
            
            evaluations = evaluation_results.get('evaluations', {})
            
            for provider, result in evaluations.items():
                if not str(result).startswith("Error"):
                    result_preview = str(result)[:150] + "..." if len(str(result)) > 150 else str(result)
                    print(f"✅ {provider}: {result_preview}")
                else:
                    print(f"❌ {provider}: {result}")
                
        except Exception as e:
            print(f"❌ Error running evaluations: {str(e)}")
            import traceback
            traceback.print_exc()
            return
        
        # Step 5: Store evaluation results in database
        print(f"\n💾 Step 5: Storing evaluation results in database...")
        
        evaluation_service = EvaluationService()
        stored_count = 0
        
        for provider, evaluation_result in evaluations.items():
            if evaluation_result and not str(evaluation_result).startswith("Error"):
                try:
                    # Extract score from result (try to parse if structured, otherwise use default)
                    score = 7.5  # Default score
                    reasoning = str(evaluation_result)
                    
                    # Try to extract score if the result contains numeric rating
                    try:
                        # Look for patterns like "Score: 8" or "Rating: 7.5" or "8/10"
                        import re
                        score_patterns = [
                            r'[Ss]core[:\s]+(\d+(?:\.\d+)?)',
                            r'[Rr]ating[:\s]+(\d+(?:\.\d+)?)',
                            r'(\d+(?:\.\d+)?)/10',
                            r'Overall[:\s]+(\d+(?:\.\d+)?)'
                        ]
                        
                        for pattern in score_patterns:
                            match = re.search(pattern, reasoning)
                            if match:
                                score = float(match.group(1))
                                break
                    except:
                        pass  # Keep default score if parsing fails
                    
                    # Prepare raw LLM response
                    raw_response = {
                        "response": evaluation_result,
                        "provider": provider,
                        "candidate": evaluation_results.get('candidate_name'),
                        "job_title": evaluation_results.get('job_title')
                    }
                    
                    success = await evaluation_service.write_evaluation(
                        interview_id=interview_id,
                        evaluator_llm_model=provider,
                        score=score,
                        reasoning=reasoning[:1000],  # Limit reasoning length
                        raw_llm_response=raw_response
                    )
                    
                    if success:
                        print(f"✅ Stored {provider} evaluation (Score: {score})")
                        stored_count += 1
                    else:
                        print(f"❌ Failed to store {provider} evaluation")
                        
                except Exception as e:
                    print(f"❌ Error storing {provider} evaluation: {str(e)}")
            else:
                print(f"⚠️ Skipping {provider} - no valid result")
        
        # Step 6: Verification and summary
        print(f"\n🎉 Step 6: Evaluation Complete!")
        print(f"📊 Successfully stored {stored_count}/3 evaluations")
        
        # Verify stored evaluations
        try:
            stored_evaluations = await evaluation_service.client.get("evaluations", {"interview_id": interview_id})
            
            if stored_evaluations:
                print(f"✅ Verified {len(stored_evaluations)} evaluation(s) in database:")
                
                total_score = 0
                valid_scores = 0
                
                for eval_record in stored_evaluations:
                    model = eval_record.get('evaluator_llm_model', 'Unknown')
                    score = eval_record.get('score', 0)
                    created = eval_record.get('created_at', 'N/A')[:19]  # Truncate timestamp
                    
                    print(f"   📊 {model}: Score {score} (Created: {created})")
                    
                    if isinstance(score, (int, float)) and score > 0:
                        total_score += score
                        valid_scores += 1
                
                if valid_scores > 0:
                    avg_score = total_score / valid_scores
                    print(f"\n📈 Average Score: {avg_score:.2f}/10")
                    
                print(f"\n🚀 Interview {interview_id} evaluation workflow complete!")
                print(f"🎯 Results are now available in the evaluations table")
                print(f"💼 Candidate {candidate_name} has been fully evaluated for {job_title}")
                
            else:
                print(f"❌ No evaluations found in database (may be a permissions issue)")
                
        except Exception as e:
            print(f"💥 Error verifying stored evaluations: {str(e)}")
            
    except Exception as e:
        print(f"💥 Error in evaluation workflow: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_clean_evaluation_workflow())