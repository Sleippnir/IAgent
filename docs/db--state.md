# AI Interviewer Backend - Handover Document

## I. Executive Summary

This document outlines the architecture and current state of the Supabase backend for an automated AI-driven interview platform. The system manages the entire interview lifecycle:

- Defining jobs and associated questions
- Curating interviews for candidates
- Queuing interviews for AI agents
- Queuing completed transcripts for evaluation by AI agents

The database schema is feature-complete with synthetic data. Core workflows are defined through PostgreSQL functions, database triggers, and a planned Supabase Edge Function.

**Key Implementation Note**: The creation of records in the interviewer queue is triggered by calling `public.generate_interview_payload()`. Currently tested manually via SQL scripts, this will be called by a Supabase Edge Function in production.

## II. Detailed Database Schema Structure

### A. Core Entities

#### 1. candidates
Stores candidate information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| candidate_id | uuid | PK, default gen_random_uuid() | Unique identifier |
| first_name | text | | |
| last_name | text | | |
| email | citext | NOT NULL, UNIQUE | Case-insensitive unique contact |
| phone | text | NULLABLE | |
| linkedin_url | text | NULLABLE | |
| resume_path | text | NULLABLE | Path to Supabase Storage file |
| user_id | uuid | FK -> auth.users(id) | Link to Supabase Auth (optional) |

#### 2. jobs
Stores job descriptions and metadata.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| job_id | uuid | PK, default gen_random_uuid() | Unique identifier |
| title | text | NOT NULL | |
| description | text | | |
| required_tags | text[] | NULLABLE | Tags for auto-matching questions |

#### 3. questions
Master bank of interview questions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| question_id | uuid | PK, default gen_random_uuid() | Unique identifier |
| text | citext | NOT NULL, UNIQUE | Question text (case-insensitive) |
| ideal_answer | text | | Answer key for evaluator |
| category | text | | E.g., 'Behavioral', 'Technical' |
| tags | text[] | NULLABLE | Tags for job matching |

#### 4. prompts & prompt_versions
Version-controlled LLM instructions.

**prompts**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| prompt_id | uuid | PK, default gen_random_uuid() | Abstract prompt ID |
| name | text | NOT NULL, UNIQUE | Human-readable name |
| purpose | enum | NOT NULL | 'interviewer' or 'evaluator' |

**prompt_versions**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| prompt_version_id | uuid | PK, default gen_random_uuid() | Specific version ID |
| prompt_id | uuid | FK -> prompts(prompt_id) | Parent prompt link |
| content | text | NOT NULL | Actual prompt text |
| version | integer | NOT NULL, UNIQUE(prompt_id, version) | Version number |

#### 5. rubrics & rubric_versions
Version-controlled evaluation criteria.

**rubrics**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| rubric_id | uuid | PK, default gen_random_uuid() | Abstract rubric ID |
| name | text | NOT NULL, UNIQUE | Human-readable name |

**rubric_versions**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| rubric_version_id | uuid | PK, default gen_random_uuid() | Specific version ID |
| rubric_id | uuid | FK -> rubrics(rubric_id) | Parent rubric link |
| rubric_json | jsonb | NOT NULL | Structured evaluation criteria |
| version | integer | NOT NULL, UNIQUE(rubric_id, version) | Version number |

### B. Workflow & Relationship Tables

#### 6. job_questions
Junction table for approved job questions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| job_id | uuid | PK, FK -> jobs(job_id) | Composite primary key |
| question_id | uuid | PK, FK -> questions(question_id) | Composite primary key |

#### 7. applications
Links candidates to jobs.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| application_id | uuid | PK, default gen_random_uuid() | |
| candidate_id | uuid | FK -> candidates(candidate_id) | |
| job_id | uuid | FK -> jobs(job_id) | UNIQUE(candidate_id, job_id) |

#### 8. interviews
Central workflow table for interview sessions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| interview_id | uuid | PK, default gen_random_uuid() | |
| application_id | uuid | FK -> applications(application_id) | UNIQUE |
| interviewer_prompt_version_id | uuid | FK -> prompt_versions | Locks interviewer prompt |
| evaluator_prompt_version_id | uuid | FK -> prompt_versions | Locks evaluator prompt |
| rubric_version_id | uuid | FK -> rubric_versions | Locks rubric |
| status | enum | NOT NULL | 'scheduled', 'completed', 'evaluated' |
| auth_token | text | NULLABLE, UNIQUE | Single-use JWT for candidate access |
| resume_text_cache | text | NULLABLE | Raw text from resume file |

#### 9. interview_questions
Definitive, ordered script for interviews.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| interview_question_id | uuid | PK, default gen_random_uuid() | |
| interview_id | uuid | FK -> interviews(interview_id) | |
| question_id | uuid | FK -> questions(question_id) | |
| position | smallint | NOT NULL | Question order (1, 2, 3...) |
| asked_text | text | NOT NULL | Snapshot of question text |

#### 10. transcripts
Stores completed interview output.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| interview_id | uuid | PK, FK -> interviews(interview_id) | One-to-one relationship |
| full_text | text | | |
| transcript_json | jsonb | | |

#### 11. evaluations
Stores evaluator LLM results.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| evaluation_id | uuid | PK, default gen_random_uuid() | |
| interview_id | uuid | FK -> interviews(interview_id) | Multiple rows per interview |
| evaluator_llm_model | text | NOT NULL | e.g., 'gpt-4-turbo' |
| score | numeric(5,2) | | |
| reasoning | text | | |
| raw_llm_response | jsonb | | Full JSON response for auditing |

### C. Performance / Queue Tables

#### 12. interviewer_queue
"To-do" list for interviewer AI.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| interview_id | uuid | PK, FK -> interviews(interview_id) | |
| auth_token | text | NOT NULL, UNIQUE | Candidate access token for fast lookup |
| payload | jsonb | NOT NULL | Pre-computed data for AI |

#### 13. evaluator_queue
"To-do" list for evaluator AIs.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| interview_id | uuid | PK, FK -> interviews(interview_id) | |
| payload | jsonb | NOT NULL | Pre-computed data for AI |

## III. Implemented Workflows, Automations, and Functions

### 1. Interview Scheduling & Queuing (Orchestrated by Edge Function)

**Triggering Event**: Frontend user action (e.g., recruiter clicking "Schedule Interview")

**Orchestrator**: Supabase Edge Function (to be built)

**Workflow Steps**:
1. Edge Function receives `application_id`, curated `question_ids`, and `resume_path`
2. Downloads resume from Storage and parses to text
3. INSERTs new record into `interviews` table with `resume_text_cache`
4. INSERTs curated questions into `interview_questions` table
5. Calls `public.generate_interview_payload()` via RPC to populate `interviewer_queue`

### 2. Evaluation Queuing (Fully Automated in DB)

**Triggering Event**: UPDATE to `interviews` where status changes to 'completed'

**Automation**: `on_interview_completed` database trigger

**Workflow Steps**:
1. Trigger executes `public.generate_evaluator_payload()`
2. Function assembles JSON payload and INSERTs into `evaluator_queue`

### 3. Queue Cleanup (Fully Automated in DB)

**Triggering Event**: INSERT into `evaluations` table

**Automation**: `on_evaluation_created` database trigger

**Workflow Steps**:
1. Trigger executes `public.cleanup_evaluator_queue()`
2. Function DELETE corresponding task from `evaluator_queue`

## IV. Key Enhancements & Design Decisions

- **Metadata-Driven Question Matching**: Robust tag-based system replacing brittle keyword matching
- **Resume Text Caching**: Solved resume context problem by caching parsed text in interviews table
- **Orchestration over Automation**: Moved complex logic from database triggers to Edge Function to resolve race conditions

## V. To-Do List for Full Implementation

### Backend Development (High Priority)
- Build Interview Orchestration Edge Function
- Build Evaluator Backend Agent (polling service for evaluator queue)

### Frontend Development
- Build Recruiter UI (job/candidate management, interview builder)
- Build Results Dashboard (evaluation viewing)

### Security Hardening
- Implement Comprehensive RLS policies
- Secure Storage Bucket for resumes with strict RLS

## VI. Backend Function Signatures & API Contracts

### A. Supabase Edge Functions (To Be Built)

#### 1. Interview Orchestration Edge Function

```
Endpoint: POST /functions/v1/schedule-interview
Authorization: User access_token with recruiter-level permissions

Request Body:
{
  "application_id": "uuid",
  "question_ids": ["uuid", "uuid", ...],
  "resume_path": "string"
}
```

#### 2. Evaluator Backend Agent
- Background worker (scheduled Edge Function or separate server)
- Polls evaluator queue, sends payloads to LLMs, inserts results

### B. PostgreSQL RPC Functions (Implemented)

#### 1. generate_interview_payload(p_interview_id uuid)
- Called by: Interview Orchestration Edge Function
- Arguments: `p_interview_id uuid`
- Returns: void
- Description: Assembles and inserts payload into interviewer_queue

#### 2. generate_evaluator_payload()
- Called by: `on_interview_completed` trigger
- Arguments: None (uses trigger context)
- Returns: trigger
- Description: Assembles and inserts payload into evaluator_queue

#### 3. cleanup_evaluator_queue()
- Called by: `on_evaluation_created` trigger
- Arguments: None (uses trigger context)
- Returns: trigger
- Description: Cleans up evaluator_queue after evaluation save