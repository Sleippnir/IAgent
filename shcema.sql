


SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;


CREATE EXTENSION IF NOT EXISTS "pg_cron" WITH SCHEMA "pg_catalog";






COMMENT ON SCHEMA "public" IS 'standard public schema';



CREATE EXTENSION IF NOT EXISTS "citext" WITH SCHEMA "public";






CREATE EXTENSION IF NOT EXISTS "pg_graphql" WITH SCHEMA "graphql";






CREATE EXTENSION IF NOT EXISTS "pg_stat_statements" WITH SCHEMA "extensions";






CREATE EXTENSION IF NOT EXISTS "pgcrypto" WITH SCHEMA "extensions";






CREATE EXTENSION IF NOT EXISTS "supabase_vault" WITH SCHEMA "vault";






CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA "extensions";






CREATE OR REPLACE FUNCTION "public"."_interview_id_from_response"("p_response_id" "uuid") RETURNS "uuid"
    LANGUAGE "sql" STABLE
    AS $$
  select i.interview_id
  from public.responses r
  join public.interview_questions iq on iq.interview_question_id = r.interview_question_id
  join public.interviews i on i.interview_id = iq.interview_id
  where r.response_id = p_response_id
$$;


ALTER FUNCTION "public"."_interview_id_from_response"("p_response_id" "uuid") OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."refresh_cache_evaluator_todo"("p_interview_id" "uuid" DEFAULT NULL::"uuid") RETURNS "void"
    LANGUAGE "plpgsql" SECURITY DEFINER
    AS $$
begin
  if p_interview_id is null then
    delete from public.cache_evaluator_todo;

    with eligible as (
      select i.interview_id
      from public.interviews i
      join public.interview_questions iq on iq.interview_id = i.interview_id
      join public.responses r on r.interview_question_id = iq.interview_question_id
      left join public.evaluations e on e.interview_id = i.interview_id
      where e.interview_id is null
      group by i.interview_id
    ),
    chosen as (
      select
        i.interview_id,
        a.application_id,
        j.job_id,
        j.title as job_title,
        c.candidate_id,
        coalesce(c.first_name,'') || ' ' || coalesce(c.last_name,'') as candidate_name,
        coalesce(i.rubric_version_id, j.default_rubric_version_id,
                 (select rv2.rubric_version_id from public.rubric_versions rv2 order by rv2.version desc limit 1)) as rubric_version_id,
        coalesce(i.evaluator_prompt_version_id, j.default_evaluator_prompt_version_id,
                 (select pv2.prompt_version_id from public.prompt_versions pv2 join public.prompts p2 using (prompt_id)
                  where p2.purpose='evaluator' order by pv2.version desc limit 1)) as evaluator_prompt_version_id
      from public.interviews i
      join eligible el on el.interview_id = i.interview_id
      join public.applications a on a.application_id = i.application_id
      join public.jobs j         on j.job_id = a.job_id
      join public.candidates c   on c.candidate_id = a.candidate_id
    ),
    qai as (
      select
        ch.interview_id,
        iq.position,
        iq.interview_question_id,
        iq.asked_text,
        r.transcript as candidate_answer,
        coalesce(jq.ideal_answer_override, q.ideal_answer) as ideal_answer
      from chosen ch
      left join public.interview_questions iq on iq.interview_id = ch.interview_id
      left join public.responses r            on r.interview_question_id = iq.interview_question_id
      left join public.interviews i           on i.interview_id = ch.interview_id
      left join public.applications a         on a.application_id = i.application_id
      left join public.jobs j                 on j.job_id = a.job_id
      left join public.questions q            on q.question_id = iq.question_id
      left join public.job_questions jq       on jq.job_id = j.job_id and jq.question_id = iq.question_id
    ),
    agg as (
      select
        ch.*,
        pv.content    as evaluator_prompt,
        rv.rubric_json,
        jsonb_agg(
          jsonb_build_object(
            'interview_question_id', qai.interview_question_id,
            'position', qai.position,
            'asked_text', qai.asked_text,
            'candidate_answer', coalesce(qai.candidate_answer,''),
            'ideal_answer',    coalesce(qai.ideal_answer,'')
          ) order by qai.position
        ) as qa_with_ideal
      from chosen ch
      left join qai on qai.interview_id = ch.interview_id
      left join public.prompt_versions pv on pv.prompt_version_id = ch.evaluator_prompt_version_id
      left join public.rubric_versions  rv on rv.rubric_version_id  = ch.rubric_version_id
      group by ch.interview_id, ch.application_id, ch.job_id, ch.job_title,
               ch.candidate_id, ch.candidate_name,
               ch.rubric_version_id, ch.evaluator_prompt_version_id,
               pv.content, rv.rubric_json
    )
    insert into public.cache_evaluator_todo (
      interview_id, application_id, job_id, job_title,
      candidate_id, candidate_name,
      qa_with_ideal,
      transcript_candidate_only,         -- NEW: candidate-only transcript
      rubric_version_id, evaluator_prompt_version_id,
      rubric_json, evaluator_prompt
    )
    select
      a.interview_id, a.application_id, a.job_id, a.job_title,
      a.candidate_id, a.candidate_name,
      a.qa_with_ideal,
      -- Q/A only (no IDEAL in printed transcript)
      string_agg(
        format('Q%s: %s' || E'\n' || 'A: %s',
          (elem->>'position'),
          elem->>'asked_text',
          elem->>'candidate_answer'
        ),
        E'\n\n' order by (elem->>'position')::int
      ),
      a.rubric_version_id, a.evaluator_prompt_version_id,
      a.rubric_json, a.evaluator_prompt
    from agg a
    left join lateral jsonb_array_elements(coalesce(a.qa_with_ideal,'[]'::jsonb)) elem on true
    group by a.interview_id, a.application_id, a.job_id, a.job_title,
             a.candidate_id, a.candidate_name, a.qa_with_ideal,
             a.rubric_version_id, a.evaluator_prompt_version_id,
             a.rubric_json, a.evaluator_prompt;

  else
    delete from public.cache_evaluator_todo where interview_id = p_interview_id;

    with chosen as (
      select
        i.interview_id,
        a.application_id,
        j.job_id,
        j.title as job_title,
        c.candidate_id,
        coalesce(c.first_name,'') || ' ' || coalesce(c.last_name,'') as candidate_name,
        coalesce(i.rubric_version_id, j.default_rubric_version_id,
                 (select rv2.rubric_version_id from public.rubric_versions rv2 order by rv2.version desc limit 1)) as rubric_version_id,
        coalesce(i.evaluator_prompt_version_id, j.default_evaluator_prompt_version_id,
                 (select pv2.prompt_version_id from public.prompt_versions pv2 join public.prompts p2 using (prompt_id)
                  where p2.purpose='evaluator' order by pv2.version desc limit 1)) as evaluator_prompt_version_id
      from public.interviews i
      join public.applications a on a.application_id = i.application_id
      join public.jobs j         on j.job_id = a.job_id
      join public.candidates c   on c.candidate_id = a.candidate_id
      where i.interview_id = p_interview_id
        and exists (
          select 1 from public.interview_questions iq
          join public.responses r on r.interview_question_id = iq.interview_question_id
          where iq.interview_id = i.interview_id
        )
        and not exists (select 1 from public.evaluations e where e.interview_id = i.interview_id)
    ),
    qai as (
      select
        ch.interview_id,
        iq.position,
        iq.interview_question_id,
        iq.asked_text,
        r.transcript as candidate_answer,
        coalesce(jq.ideal_answer_override, q.ideal_answer) as ideal_answer
      from chosen ch
      left join public.interview_questions iq on iq.interview_id = ch.interview_id
      left join public.responses r            on r.interview_question_id = iq.interview_question_id
      left join public.interviews i           on i.interview_id = ch.interview_id
      left join public.applications a         on a.application_id = i.application_id
      left join public.jobs j                 on j.job_id = a.job_id
      left join public.questions q            on q.question_id = iq.question_id
      left join public.job_questions jq       on jq.job_id = j.job_id and jq.question_id = iq.question_id
    ),
    agg as (
      select
        ch.*,
        pv.content    as evaluator_prompt,
        rv.rubric_json,
        jsonb_agg(
          jsonb_build_object(
            'interview_question_id', qai.interview_question_id,
            'position', qai.position,
            'asked_text', qai.asked_text,
            'candidate_answer', coalesce(qai.candidate_answer,''),
            'ideal_answer',    coalesce(qai.ideal_answer,'')
          ) order by qai.position
        ) as qa_with_ideal
      from chosen ch
      left join qai on qai.interview_id = ch.interview_id
      left join public.prompt_versions pv on pv.prompt_version_id = ch.evaluator_prompt_version_id
      left join public.rubric_versions  rv on rv.rubric_version_id  = ch.rubric_version_id
      group by ch.interview_id, ch.application_id, ch.job_id, ch.job_title,
               ch.candidate_id, ch.candidate_name,
               ch.rubric_version_id, ch.evaluator_prompt_version_id,
               pv.content, rv.rubric_json
    )
    insert into public.cache_evaluator_todo (
      interview_id, application_id, job_id, job_title,
      candidate_id, candidate_name,
      qa_with_ideal,
      transcript_candidate_only,         -- NEW: candidate-only transcript
      rubric_version_id, evaluator_prompt_version_id,
      rubric_json, evaluator_prompt
    )
    select
      a.interview_id, a.application_id, a.job_id, a.job_title,
      a.candidate_id, a.candidate_name,
      a.qa_with_ideal,
      string_agg(
        format('Q%s: %s' || E'\n' || 'A: %s',
          (elem->>'position'),
          elem->>'asked_text',
          elem->>'candidate_answer'
        ),
        E'\n\n' order by (elem->>'position')::int
      ),
      a.rubric_version_id, a.evaluator_prompt_version_id,
      a.rubric_json, a.evaluator_prompt
    from agg a
    left join lateral jsonb_array_elements(coalesce(a.qa_with_ideal,'[]'::jsonb)) elem on true
    group by a.interview_id, a.application_id, a.job_id, a.job_title,
             a.candidate_id, a.candidate_name, a.qa_with_ideal,
             a.rubric_version_id, a.evaluator_prompt_version_id,
             a.rubric_json, a.evaluator_prompt;
  end if;
end;
$$;


ALTER FUNCTION "public"."refresh_cache_evaluator_todo"("p_interview_id" "uuid") OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."refresh_cache_interviewer_todo"("p_interview_id" "uuid" DEFAULT NULL::"uuid") RETURNS "void"
    LANGUAGE "plpgsql" SECURITY DEFINER
    AS $$
begin
  if p_interview_id is null then
    -- full rebuild
    delete from public.cache_interviewer_todo;

    insert into public.cache_interviewer_todo (interview_id, application_id, job_id, job_title, candidate_id, candidate_name, started_at, is_complete, questions_json)
    with q as (
      select
        iq.interview_id,
        jsonb_agg(
          jsonb_build_object(
            'interview_question_id', iq.interview_question_id,
            'position', iq.position,
            'asked_text', iq.asked_text
          )
          order by iq.position
        ) as questions_json
      from public.interview_questions iq
      group by iq.interview_id
    ),
    has_resp as (
      select distinct iq.interview_id
      from public.interview_questions iq
      join public.responses r on r.interview_question_id = iq.interview_question_id
    )
    select
      i.interview_id,
      a.application_id,
      j.job_id,
      j.title as job_title,
      c.candidate_id,
      coalesce(c.first_name,'') || ' ' || coalesce(c.last_name,'') as candidate_name,
      i.started_at,
      coalesce(i.is_complete, false),
      q.questions_json
    from public.interviews i
    join public.applications a on a.application_id = i.application_id
    join public.jobs j         on j.job_id = a.job_id
    join public.candidates c   on c.candidate_id = a.candidate_id
    left join q on q.interview_id = i.interview_id
    where q.questions_json is not null
      and not exists (select 1 from has_resp hr where hr.interview_id = i.interview_id)
      and coalesce(i.is_complete, false) = false;

  else
    -- incremental rebuild for one interview_id
    delete from public.cache_interviewer_todo where interview_id = p_interview_id;

    with q as (
      select
        iq.interview_id,
        jsonb_agg(
          jsonb_build_object(
            'interview_question_id', iq.interview_question_id,
            'position', iq.position,
            'asked_text', iq.asked_text
          )
          order by iq.position
        ) as questions_json
      from public.interview_questions iq
      where iq.interview_id = p_interview_id
      group by iq.interview_id
    ),
    has_resp as (
      select 1
      from public.interview_questions iq
      join public.responses r on r.interview_question_id = iq.interview_question_id
      where iq.interview_id = p_interview_id
      limit 1
    )
    insert into public.cache_interviewer_todo (interview_id, application_id, job_id, job_title, candidate_id, candidate_name, started_at, is_complete, questions_json)
    select
      i.interview_id,
      a.application_id,
      j.job_id,
      j.title as job_title,
      c.candidate_id,
      coalesce(c.first_name,'') || ' ' || coalesce(c.last_name,'') as candidate_name,
      i.started_at,
      coalesce(i.is_complete, false),
      q.questions_json
    from public.interviews i
    join public.applications a on a.application_id = i.application_id
    join public.jobs j         on j.job_id = a.job_id
    join public.candidates c   on c.candidate_id = a.candidate_id
    left join q on q.interview_id = i.interview_id
    where i.interview_id = p_interview_id
      and q.questions_json is not null
      and not exists (select 1 from has_resp)
      and coalesce(i.is_complete, false) = false;
  end if;
end;
$$;


ALTER FUNCTION "public"."refresh_cache_interviewer_todo"("p_interview_id" "uuid") OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."trg_after_evaluation_refresh"() RETURNS "trigger"
    LANGUAGE "plpgsql" SECURITY DEFINER
    AS $$
begin
  perform public.refresh_cache_evaluator_todo(NEW.interview_id);
  return null;
end;
$$;


ALTER FUNCTION "public"."trg_after_evaluation_refresh"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."trg_after_response_refresh"() RETURNS "trigger"
    LANGUAGE "plpgsql" SECURITY DEFINER
    AS $$
declare
  v_interview_id uuid;
begin
  v_interview_id := public._interview_id_from_response(NEW.response_id);
  perform public.refresh_cache_interviewer_todo(v_interview_id);
  perform public.refresh_cache_evaluator_todo(v_interview_id);
  return null;
end;
$$;


ALTER FUNCTION "public"."trg_after_response_refresh"() OWNER TO "postgres";


CREATE OR REPLACE FUNCTION "public"."trg_after_snapshot_refresh"() RETURNS "trigger"
    LANGUAGE "plpgsql" SECURITY DEFINER
    AS $$
declare
  rec record;
begin
  for rec in
    select distinct interview_id from new_rows
  loop
    perform public.refresh_cache_interviewer_todo(rec.interview_id);
  end loop;
  return null;
end;
$$;


ALTER FUNCTION "public"."trg_after_snapshot_refresh"() OWNER TO "postgres";

SET default_tablespace = '';

SET default_table_access_method = "heap";


CREATE TABLE IF NOT EXISTS "public"."applications" (
    "application_id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "candidate_id" "uuid" NOT NULL,
    "job_id" "uuid" NOT NULL,
    "status" "text" DEFAULT 'applied'::"text" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"(),
    CONSTRAINT "applications_status_check" CHECK (("status" = ANY (ARRAY['applied'::"text", 'screening'::"text", 'interview_scheduled'::"text", 'interviewed'::"text", 'offer'::"text", 'rejected'::"text", 'withdrawn'::"text"])))
);


ALTER TABLE "public"."applications" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."cache_evaluator_todo" (
    "interview_id" "uuid" NOT NULL,
    "application_id" "uuid" NOT NULL,
    "job_id" "uuid" NOT NULL,
    "job_title" "text" NOT NULL,
    "candidate_id" "uuid" NOT NULL,
    "candidate_name" "text" NOT NULL,
    "qa_with_ideal" "jsonb" NOT NULL,
    "rubric_version_id" "uuid",
    "evaluator_prompt_version_id" "uuid",
    "rubric_json" "jsonb",
    "evaluator_prompt" "text",
    "transcript_candidate_only" "text"
);


ALTER TABLE "public"."cache_evaluator_todo" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."cache_interviewer_todo" (
    "interview_id" "uuid" NOT NULL,
    "application_id" "uuid" NOT NULL,
    "job_id" "uuid" NOT NULL,
    "job_title" "text" NOT NULL,
    "candidate_id" "uuid" NOT NULL,
    "candidate_name" "text" NOT NULL,
    "started_at" timestamp with time zone,
    "is_complete" boolean DEFAULT false NOT NULL,
    "questions_json" "jsonb" NOT NULL
);


ALTER TABLE "public"."cache_interviewer_todo" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."candidates" (
    "candidate_id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "user_id" "uuid",
    "first_name" "text",
    "last_name" "text",
    "email" "public"."citext" NOT NULL,
    "phone" "text",
    "linkedin_url" "text",
    "resume_key" "text",
    "created_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."candidates" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."evaluation_items" (
    "evaluation_item_id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "evaluation_id" "uuid" NOT NULL,
    "interview_question_id" "uuid",
    "position" integer NOT NULL,
    "question_id" "uuid",
    "asked_text" "text",
    "candidate_answer" "text",
    "ideal_answer" "text",
    "rubric_fragment" "jsonb",
    "score" numeric(5,2),
    "reasoning" "text"
);


ALTER TABLE "public"."evaluation_items" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."evaluations" (
    "evaluation_id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "interview_id" "uuid" NOT NULL,
    "rubric_version_id" "uuid" NOT NULL,
    "evaluator_prompt_version_id" "uuid" NOT NULL,
    "llm_model" "text" NOT NULL,
    "llm_params" "jsonb" DEFAULT '{}'::"jsonb" NOT NULL,
    "score" numeric(5,2),
    "notes" "text",
    "result_json" "jsonb",
    "created_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."evaluations" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."interview_questions" (
    "interview_question_id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "interview_id" "uuid" NOT NULL,
    "question_id" "uuid",
    "asked_text" "text" NOT NULL,
    "position" smallint NOT NULL,
    "job_question_id" "uuid"
);


ALTER TABLE "public"."interview_questions" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."interviews" (
    "interview_id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "application_id" "uuid" NOT NULL,
    "interviewer_prompt_version_id" "uuid" NOT NULL,
    "llm_model" "text" NOT NULL,
    "llm_params" "jsonb" DEFAULT '{}'::"jsonb" NOT NULL,
    "started_at" timestamp with time zone,
    "ended_at" timestamp with time zone,
    "is_complete" boolean DEFAULT false NOT NULL,
    "rubric_version_id" "uuid",
    "evaluator_prompt_version_id" "uuid"
);


ALTER TABLE "public"."interviews" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."job_questions" (
    "job_id" "uuid" NOT NULL,
    "question_id" "uuid" NOT NULL,
    "position" smallint,
    "job_question_id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "ideal_answer_override" "text",
    "rubric_override" "jsonb"
);


ALTER TABLE "public"."job_questions" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."jobs" (
    "job_id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "title" "text" NOT NULL,
    "description" "text",
    "requirements" "text",
    "created_by" "uuid",
    "created_at" timestamp with time zone DEFAULT "now"(),
    "default_rubric_version_id" "uuid",
    "default_evaluator_prompt_version_id" "uuid"
);


ALTER TABLE "public"."jobs" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."profiles" (
    "user_id" "uuid" NOT NULL,
    "role" "text" NOT NULL,
    "display_name" "text",
    "created_at" timestamp with time zone DEFAULT "now"(),
    CONSTRAINT "profiles_role_check" CHECK (("role" = ANY (ARRAY['admin'::"text", 'recruiter'::"text", 'interviewer'::"text", 'candidate'::"text"])))
);


ALTER TABLE "public"."profiles" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."prompt_versions" (
    "prompt_version_id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "prompt_id" "uuid" NOT NULL,
    "version" integer NOT NULL,
    "content" "text" NOT NULL,
    "content_sha256" "text" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."prompt_versions" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."prompts" (
    "prompt_id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "name" "text" NOT NULL,
    "purpose" "text" NOT NULL,
    CONSTRAINT "prompts_purpose_check" CHECK (("purpose" = ANY (ARRAY['interviewer'::"text", 'evaluator'::"text"])))
);


ALTER TABLE "public"."prompts" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."questions" (
    "question_id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "text" "text" NOT NULL,
    "category" "text",
    "tags" "text"[],
    "ideal_answer" "text",
    "ideal_answer_json" "jsonb"
);


ALTER TABLE "public"."questions" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."responses" (
    "response_id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "interview_question_id" "uuid" NOT NULL,
    "transcript" "text" NOT NULL,
    "transcript_json" "jsonb",
    "audio_key" "text",
    "started_at" timestamp with time zone,
    "ended_at" timestamp with time zone
);


ALTER TABLE "public"."responses" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."revoked_jti" (
    "jti" "uuid" NOT NULL,
    "user_id" "uuid",
    "reason" "text",
    "revoked_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."revoked_jti" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."rubric_versions" (
    "rubric_version_id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "rubric_id" "uuid" NOT NULL,
    "version" integer NOT NULL,
    "rubric_json" "jsonb" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"()
);


ALTER TABLE "public"."rubric_versions" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."rubrics" (
    "rubric_id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "name" "text" NOT NULL
);


ALTER TABLE "public"."rubrics" OWNER TO "postgres";


CREATE TABLE IF NOT EXISTS "public"."transcripts" (
    "interview_id" "uuid" NOT NULL,
    "text" "text" NOT NULL,
    "json" "jsonb",
    "audio_mixdown_key" "text"
);


ALTER TABLE "public"."transcripts" OWNER TO "postgres";


ALTER TABLE ONLY "public"."applications"
    ADD CONSTRAINT "applications_candidate_id_job_id_key" UNIQUE ("candidate_id", "job_id");



ALTER TABLE ONLY "public"."applications"
    ADD CONSTRAINT "applications_candidate_job_uniq" UNIQUE ("candidate_id", "job_id");



ALTER TABLE ONLY "public"."applications"
    ADD CONSTRAINT "applications_pkey" PRIMARY KEY ("application_id");



ALTER TABLE ONLY "public"."cache_evaluator_todo"
    ADD CONSTRAINT "cache_evaluator_todo_pkey" PRIMARY KEY ("interview_id");



ALTER TABLE ONLY "public"."cache_interviewer_todo"
    ADD CONSTRAINT "cache_interviewer_todo_pkey" PRIMARY KEY ("interview_id");



ALTER TABLE ONLY "public"."candidates"
    ADD CONSTRAINT "candidates_pkey" PRIMARY KEY ("candidate_id");



ALTER TABLE ONLY "public"."candidates"
    ADD CONSTRAINT "candidates_user_id_key" UNIQUE ("user_id");



ALTER TABLE ONLY "public"."evaluation_items"
    ADD CONSTRAINT "evaluation_items_pkey" PRIMARY KEY ("evaluation_item_id");



ALTER TABLE ONLY "public"."evaluations"
    ADD CONSTRAINT "evaluations_pkey" PRIMARY KEY ("evaluation_id");



ALTER TABLE ONLY "public"."interview_questions"
    ADD CONSTRAINT "interview_questions_pkey" PRIMARY KEY ("interview_question_id");



ALTER TABLE ONLY "public"."interviews"
    ADD CONSTRAINT "interviews_pkey" PRIMARY KEY ("interview_id");



ALTER TABLE ONLY "public"."job_questions"
    ADD CONSTRAINT "job_questions_job_question_id_uniq" UNIQUE ("job_question_id");



ALTER TABLE ONLY "public"."job_questions"
    ADD CONSTRAINT "job_questions_job_question_uniq" UNIQUE ("job_id", "question_id");



ALTER TABLE ONLY "public"."job_questions"
    ADD CONSTRAINT "job_questions_pkey" PRIMARY KEY ("job_id", "question_id");



ALTER TABLE ONLY "public"."job_questions"
    ADD CONSTRAINT "job_questions_position_uniq" UNIQUE ("job_id", "position");



ALTER TABLE ONLY "public"."jobs"
    ADD CONSTRAINT "jobs_pkey" PRIMARY KEY ("job_id");



ALTER TABLE ONLY "public"."profiles"
    ADD CONSTRAINT "profiles_pkey" PRIMARY KEY ("user_id");



ALTER TABLE ONLY "public"."prompt_versions"
    ADD CONSTRAINT "prompt_versions_pkey" PRIMARY KEY ("prompt_version_id");



ALTER TABLE ONLY "public"."prompt_versions"
    ADD CONSTRAINT "prompt_versions_prompt_id_version_key" UNIQUE ("prompt_id", "version");



ALTER TABLE ONLY "public"."prompt_versions"
    ADD CONSTRAINT "prompt_versions_prompt_version_uniq" UNIQUE ("prompt_id", "version");



ALTER TABLE ONLY "public"."prompts"
    ADD CONSTRAINT "prompts_pkey" PRIMARY KEY ("prompt_id");



ALTER TABLE ONLY "public"."questions"
    ADD CONSTRAINT "questions_pkey" PRIMARY KEY ("question_id");



ALTER TABLE ONLY "public"."responses"
    ADD CONSTRAINT "responses_pkey" PRIMARY KEY ("response_id");



ALTER TABLE ONLY "public"."revoked_jti"
    ADD CONSTRAINT "revoked_jti_pkey" PRIMARY KEY ("jti");



ALTER TABLE ONLY "public"."rubric_versions"
    ADD CONSTRAINT "rubric_versions_pkey" PRIMARY KEY ("rubric_version_id");



ALTER TABLE ONLY "public"."rubric_versions"
    ADD CONSTRAINT "rubric_versions_rubric_id_version_key" UNIQUE ("rubric_id", "version");



ALTER TABLE ONLY "public"."rubric_versions"
    ADD CONSTRAINT "rubric_versions_rubric_version_uniq" UNIQUE ("rubric_id", "version");



ALTER TABLE ONLY "public"."rubrics"
    ADD CONSTRAINT "rubrics_pkey" PRIMARY KEY ("rubric_id");



ALTER TABLE ONLY "public"."transcripts"
    ADD CONSTRAINT "transcripts_pkey" PRIMARY KEY ("interview_id");



CREATE INDEX "applications_job_id_status_idx" ON "public"."applications" USING "btree" ("job_id", "status");



CREATE INDEX "applications_job_status_idx" ON "public"."applications" USING "btree" ("job_id", "status");



CREATE INDEX "cache_eval_job_idx" ON "public"."cache_evaluator_todo" USING "btree" ("job_id");



CREATE INDEX "cache_interviewer_job_idx" ON "public"."cache_interviewer_todo" USING "btree" ("job_id");



CREATE INDEX "cache_interviewer_started_idx" ON "public"."cache_interviewer_todo" USING "btree" ("started_at");



CREATE INDEX "candidates_email_idx" ON "public"."candidates" USING "btree" ("email");



CREATE INDEX "evaluation_items_eval_idx" ON "public"."evaluation_items" USING "btree" ("evaluation_id", "position");



CREATE INDEX "evaluations_interview_id_idx" ON "public"."evaluations" USING "btree" ("interview_id");



CREATE INDEX "evaluations_interview_idx" ON "public"."evaluations" USING "btree" ("interview_id");



CREATE INDEX "interview_questions_interview_pos_idx" ON "public"."interview_questions" USING "btree" ("interview_id", "position");



CREATE INDEX "interview_questions_jq_idx" ON "public"."interview_questions" USING "btree" ("job_question_id");



CREATE INDEX "interview_questions_pos_idx" ON "public"."interview_questions" USING "btree" ("interview_id", "position");



CREATE INDEX "interviews_app_started_idx" ON "public"."interviews" USING "btree" ("application_id", "started_at");



CREATE INDEX "interviews_application_id_started_at_idx" ON "public"."interviews" USING "btree" ("application_id", "started_at");



CREATE INDEX "job_questions_job_pos_idx" ON "public"."job_questions" USING "btree" ("job_id", "position");



CREATE INDEX "questions_tags_gin" ON "public"."questions" USING "gin" ("tags");



CREATE INDEX "responses_interview_question_id_idx" ON "public"."responses" USING "btree" ("interview_question_id");



CREATE INDEX "responses_iq_idx" ON "public"."responses" USING "btree" ("interview_question_id");



CREATE OR REPLACE TRIGGER "trg_evaluation_refresh" AFTER INSERT ON "public"."evaluations" FOR EACH ROW EXECUTE FUNCTION "public"."trg_after_evaluation_refresh"();



CREATE OR REPLACE TRIGGER "trg_response_refresh" AFTER INSERT ON "public"."responses" FOR EACH ROW EXECUTE FUNCTION "public"."trg_after_response_refresh"();



CREATE OR REPLACE TRIGGER "trg_snapshot_refresh" AFTER INSERT ON "public"."interview_questions" REFERENCING NEW TABLE AS "new_rows" FOR EACH STATEMENT EXECUTE FUNCTION "public"."trg_after_snapshot_refresh"();



ALTER TABLE ONLY "public"."applications"
    ADD CONSTRAINT "applications_candidate_id_fkey" FOREIGN KEY ("candidate_id") REFERENCES "public"."candidates"("candidate_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."applications"
    ADD CONSTRAINT "applications_job_id_fkey" FOREIGN KEY ("job_id") REFERENCES "public"."jobs"("job_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."candidates"
    ADD CONSTRAINT "candidates_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."evaluation_items"
    ADD CONSTRAINT "evaluation_items_evaluation_id_fkey" FOREIGN KEY ("evaluation_id") REFERENCES "public"."evaluations"("evaluation_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."evaluation_items"
    ADD CONSTRAINT "evaluation_items_interview_question_id_fkey" FOREIGN KEY ("interview_question_id") REFERENCES "public"."interview_questions"("interview_question_id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."evaluation_items"
    ADD CONSTRAINT "evaluation_items_question_id_fkey" FOREIGN KEY ("question_id") REFERENCES "public"."questions"("question_id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."evaluations"
    ADD CONSTRAINT "evaluations_evaluator_prompt_version_id_fkey" FOREIGN KEY ("evaluator_prompt_version_id") REFERENCES "public"."prompt_versions"("prompt_version_id");



ALTER TABLE ONLY "public"."evaluations"
    ADD CONSTRAINT "evaluations_interview_id_fkey" FOREIGN KEY ("interview_id") REFERENCES "public"."interviews"("interview_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."evaluations"
    ADD CONSTRAINT "evaluations_rubric_version_id_fkey" FOREIGN KEY ("rubric_version_id") REFERENCES "public"."rubric_versions"("rubric_version_id");



ALTER TABLE ONLY "public"."interview_questions"
    ADD CONSTRAINT "interview_questions_interview_id_fkey" FOREIGN KEY ("interview_id") REFERENCES "public"."interviews"("interview_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."interview_questions"
    ADD CONSTRAINT "interview_questions_job_question_fk" FOREIGN KEY ("job_question_id") REFERENCES "public"."job_questions"("job_question_id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."interview_questions"
    ADD CONSTRAINT "interview_questions_question_id_fkey" FOREIGN KEY ("question_id") REFERENCES "public"."questions"("question_id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."interviews"
    ADD CONSTRAINT "interviews_application_id_fkey" FOREIGN KEY ("application_id") REFERENCES "public"."applications"("application_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."interviews"
    ADD CONSTRAINT "interviews_evaluator_prompt_version_id_fkey" FOREIGN KEY ("evaluator_prompt_version_id") REFERENCES "public"."prompt_versions"("prompt_version_id");



ALTER TABLE ONLY "public"."interviews"
    ADD CONSTRAINT "interviews_interviewer_prompt_version_id_fkey" FOREIGN KEY ("interviewer_prompt_version_id") REFERENCES "public"."prompt_versions"("prompt_version_id");



ALTER TABLE ONLY "public"."interviews"
    ADD CONSTRAINT "interviews_rubric_version_id_fkey" FOREIGN KEY ("rubric_version_id") REFERENCES "public"."rubric_versions"("rubric_version_id");



ALTER TABLE ONLY "public"."job_questions"
    ADD CONSTRAINT "job_questions_job_id_fkey" FOREIGN KEY ("job_id") REFERENCES "public"."jobs"("job_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."job_questions"
    ADD CONSTRAINT "job_questions_question_id_fkey" FOREIGN KEY ("question_id") REFERENCES "public"."questions"("question_id") ON DELETE RESTRICT;



ALTER TABLE ONLY "public"."jobs"
    ADD CONSTRAINT "jobs_created_by_fk" FOREIGN KEY ("created_by") REFERENCES "auth"."users"("id") ON DELETE SET NULL;



ALTER TABLE ONLY "public"."jobs"
    ADD CONSTRAINT "jobs_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "auth"."users"("id");



ALTER TABLE ONLY "public"."jobs"
    ADD CONSTRAINT "jobs_default_evaluator_prompt_version_id_fkey" FOREIGN KEY ("default_evaluator_prompt_version_id") REFERENCES "public"."prompt_versions"("prompt_version_id");



ALTER TABLE ONLY "public"."jobs"
    ADD CONSTRAINT "jobs_default_rubric_version_id_fkey" FOREIGN KEY ("default_rubric_version_id") REFERENCES "public"."rubric_versions"("rubric_version_id");



ALTER TABLE ONLY "public"."profiles"
    ADD CONSTRAINT "profiles_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."prompt_versions"
    ADD CONSTRAINT "prompt_versions_prompt_id_fkey" FOREIGN KEY ("prompt_id") REFERENCES "public"."prompts"("prompt_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."responses"
    ADD CONSTRAINT "responses_interview_question_id_fkey" FOREIGN KEY ("interview_question_id") REFERENCES "public"."interview_questions"("interview_question_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."revoked_jti"
    ADD CONSTRAINT "revoked_jti_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."rubric_versions"
    ADD CONSTRAINT "rubric_versions_rubric_id_fkey" FOREIGN KEY ("rubric_id") REFERENCES "public"."rubrics"("rubric_id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."transcripts"
    ADD CONSTRAINT "transcripts_interview_id_fkey" FOREIGN KEY ("interview_id") REFERENCES "public"."interviews"("interview_id") ON DELETE CASCADE;



ALTER TABLE "public"."applications" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "applications_read_owner_or_staff" ON "public"."applications" FOR SELECT USING ((("candidate_id" IN ( SELECT "c"."candidate_id"
   FROM "public"."candidates" "c"
  WHERE ("c"."user_id" = "auth"."uid"()))) OR (EXISTS ( SELECT 1
   FROM "public"."profiles" "p"
  WHERE (("p"."user_id" = "auth"."uid"()) AND ("p"."role" = ANY (ARRAY['admin'::"text", 'recruiter'::"text"])))))));



CREATE POLICY "cache_evaluator_read_owner_or_staff" ON "public"."cache_evaluator_todo" FOR SELECT USING ((EXISTS ( SELECT 1
   FROM (("public"."interviews" "i"
     JOIN "public"."applications" "a" ON (("a"."application_id" = "i"."application_id")))
     JOIN "public"."candidates" "c" ON (("c"."candidate_id" = "a"."candidate_id")))
  WHERE (("i"."interview_id" = "cache_evaluator_todo"."interview_id") AND (("c"."user_id" = "auth"."uid"()) OR (EXISTS ( SELECT 1
           FROM "public"."profiles" "p"
          WHERE (("p"."user_id" = "auth"."uid"()) AND ("p"."role" = ANY (ARRAY['admin'::"text", 'recruiter'::"text", 'interviewer'::"text"]))))))))));



ALTER TABLE "public"."cache_evaluator_todo" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "cache_interviewer_read_owner_or_staff" ON "public"."cache_interviewer_todo" FOR SELECT USING ((EXISTS ( SELECT 1
   FROM (("public"."interviews" "i"
     JOIN "public"."applications" "a" ON (("a"."application_id" = "i"."application_id")))
     JOIN "public"."candidates" "c" ON (("c"."candidate_id" = "a"."candidate_id")))
  WHERE (("i"."interview_id" = "cache_interviewer_todo"."interview_id") AND (("c"."user_id" = "auth"."uid"()) OR (EXISTS ( SELECT 1
           FROM "public"."profiles" "p"
          WHERE (("p"."user_id" = "auth"."uid"()) AND ("p"."role" = ANY (ARRAY['admin'::"text", 'recruiter'::"text", 'interviewer'::"text"]))))))))));



ALTER TABLE "public"."cache_interviewer_todo" ENABLE ROW LEVEL SECURITY;


ALTER TABLE "public"."candidates" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "candidates_read_self_or_staff" ON "public"."candidates" FOR SELECT USING ((("user_id" = "auth"."uid"()) OR (EXISTS ( SELECT 1
   FROM "public"."profiles" "p"
  WHERE (("p"."user_id" = "auth"."uid"()) AND ("p"."role" = ANY (ARRAY['admin'::"text", 'recruiter'::"text"])))))));



ALTER TABLE "public"."evaluations" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "evaluations_read_owner_or_staff" ON "public"."evaluations" FOR SELECT USING ((EXISTS ( SELECT 1
   FROM (("public"."interviews" "i"
     JOIN "public"."applications" "a" ON (("a"."application_id" = "i"."application_id")))
     JOIN "public"."candidates" "c" ON (("c"."candidate_id" = "a"."candidate_id")))
  WHERE (("i"."interview_id" = "evaluations"."interview_id") AND (("c"."user_id" = "auth"."uid"()) OR (EXISTS ( SELECT 1
           FROM "public"."profiles" "p"
          WHERE (("p"."user_id" = "auth"."uid"()) AND ("p"."role" = ANY (ARRAY['admin'::"text", 'recruiter'::"text"]))))))))));



ALTER TABLE "public"."interviews" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "interviews_read_owner_or_staff" ON "public"."interviews" FOR SELECT USING ((EXISTS ( SELECT 1
   FROM ("public"."applications" "a"
     JOIN "public"."candidates" "c" ON (("c"."candidate_id" = "a"."candidate_id")))
  WHERE (("a"."application_id" = "interviews"."application_id") AND (("c"."user_id" = "auth"."uid"()) OR (EXISTS ( SELECT 1
           FROM "public"."profiles" "p"
          WHERE (("p"."user_id" = "auth"."uid"()) AND ("p"."role" = ANY (ARRAY['admin'::"text", 'recruiter'::"text", 'interviewer'::"text"]))))))))));



ALTER TABLE "public"."prompt_versions" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "pv_block_write" ON "public"."prompt_versions" USING (false) WITH CHECK (false);



CREATE POLICY "pv_read" ON "public"."prompt_versions" FOR SELECT USING (true);



ALTER TABLE "public"."responses" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "responses_read_owner_or_staff" ON "public"."responses" FOR SELECT USING ((EXISTS ( SELECT 1
   FROM ((("public"."interview_questions" "iq"
     JOIN "public"."interviews" "i" ON (("i"."interview_id" = "iq"."interview_id")))
     JOIN "public"."applications" "a" ON (("a"."application_id" = "i"."application_id")))
     JOIN "public"."candidates" "c" ON (("c"."candidate_id" = "a"."candidate_id")))
  WHERE (("iq"."interview_question_id" = "responses"."interview_question_id") AND (("c"."user_id" = "auth"."uid"()) OR (EXISTS ( SELECT 1
           FROM "public"."profiles" "p"
          WHERE (("p"."user_id" = "auth"."uid"()) AND ("p"."role" = ANY (ARRAY['admin'::"text", 'recruiter'::"text", 'interviewer'::"text"]))))))))));



ALTER TABLE "public"."rubric_versions" ENABLE ROW LEVEL SECURITY;


CREATE POLICY "rv_block_write" ON "public"."rubric_versions" USING (false) WITH CHECK (false);



CREATE POLICY "rv_read" ON "public"."rubric_versions" FOR SELECT USING (true);





ALTER PUBLICATION "supabase_realtime" OWNER TO "postgres";





GRANT USAGE ON SCHEMA "public" TO "postgres";
GRANT USAGE ON SCHEMA "public" TO "anon";
GRANT USAGE ON SCHEMA "public" TO "authenticated";
GRANT USAGE ON SCHEMA "public" TO "service_role";



GRANT ALL ON FUNCTION "public"."citextin"("cstring") TO "postgres";
GRANT ALL ON FUNCTION "public"."citextin"("cstring") TO "anon";
GRANT ALL ON FUNCTION "public"."citextin"("cstring") TO "authenticated";
GRANT ALL ON FUNCTION "public"."citextin"("cstring") TO "service_role";



GRANT ALL ON FUNCTION "public"."citextout"("public"."citext") TO "postgres";
GRANT ALL ON FUNCTION "public"."citextout"("public"."citext") TO "anon";
GRANT ALL ON FUNCTION "public"."citextout"("public"."citext") TO "authenticated";
GRANT ALL ON FUNCTION "public"."citextout"("public"."citext") TO "service_role";



GRANT ALL ON FUNCTION "public"."citextrecv"("internal") TO "postgres";
GRANT ALL ON FUNCTION "public"."citextrecv"("internal") TO "anon";
GRANT ALL ON FUNCTION "public"."citextrecv"("internal") TO "authenticated";
GRANT ALL ON FUNCTION "public"."citextrecv"("internal") TO "service_role";



GRANT ALL ON FUNCTION "public"."citextsend"("public"."citext") TO "postgres";
GRANT ALL ON FUNCTION "public"."citextsend"("public"."citext") TO "anon";
GRANT ALL ON FUNCTION "public"."citextsend"("public"."citext") TO "authenticated";
GRANT ALL ON FUNCTION "public"."citextsend"("public"."citext") TO "service_role";



GRANT ALL ON FUNCTION "public"."citext"(boolean) TO "postgres";
GRANT ALL ON FUNCTION "public"."citext"(boolean) TO "anon";
GRANT ALL ON FUNCTION "public"."citext"(boolean) TO "authenticated";
GRANT ALL ON FUNCTION "public"."citext"(boolean) TO "service_role";



GRANT ALL ON FUNCTION "public"."citext"(character) TO "postgres";
GRANT ALL ON FUNCTION "public"."citext"(character) TO "anon";
GRANT ALL ON FUNCTION "public"."citext"(character) TO "authenticated";
GRANT ALL ON FUNCTION "public"."citext"(character) TO "service_role";



GRANT ALL ON FUNCTION "public"."citext"("inet") TO "postgres";
GRANT ALL ON FUNCTION "public"."citext"("inet") TO "anon";
GRANT ALL ON FUNCTION "public"."citext"("inet") TO "authenticated";
GRANT ALL ON FUNCTION "public"."citext"("inet") TO "service_role";














































































































































































GRANT ALL ON FUNCTION "public"."_interview_id_from_response"("p_response_id" "uuid") TO "anon";
GRANT ALL ON FUNCTION "public"."_interview_id_from_response"("p_response_id" "uuid") TO "authenticated";
GRANT ALL ON FUNCTION "public"."_interview_id_from_response"("p_response_id" "uuid") TO "service_role";



GRANT ALL ON FUNCTION "public"."citext_cmp"("public"."citext", "public"."citext") TO "postgres";
GRANT ALL ON FUNCTION "public"."citext_cmp"("public"."citext", "public"."citext") TO "anon";
GRANT ALL ON FUNCTION "public"."citext_cmp"("public"."citext", "public"."citext") TO "authenticated";
GRANT ALL ON FUNCTION "public"."citext_cmp"("public"."citext", "public"."citext") TO "service_role";



GRANT ALL ON FUNCTION "public"."citext_eq"("public"."citext", "public"."citext") TO "postgres";
GRANT ALL ON FUNCTION "public"."citext_eq"("public"."citext", "public"."citext") TO "anon";
GRANT ALL ON FUNCTION "public"."citext_eq"("public"."citext", "public"."citext") TO "authenticated";
GRANT ALL ON FUNCTION "public"."citext_eq"("public"."citext", "public"."citext") TO "service_role";



GRANT ALL ON FUNCTION "public"."citext_ge"("public"."citext", "public"."citext") TO "postgres";
GRANT ALL ON FUNCTION "public"."citext_ge"("public"."citext", "public"."citext") TO "anon";
GRANT ALL ON FUNCTION "public"."citext_ge"("public"."citext", "public"."citext") TO "authenticated";
GRANT ALL ON FUNCTION "public"."citext_ge"("public"."citext", "public"."citext") TO "service_role";



GRANT ALL ON FUNCTION "public"."citext_gt"("public"."citext", "public"."citext") TO "postgres";
GRANT ALL ON FUNCTION "public"."citext_gt"("public"."citext", "public"."citext") TO "anon";
GRANT ALL ON FUNCTION "public"."citext_gt"("public"."citext", "public"."citext") TO "authenticated";
GRANT ALL ON FUNCTION "public"."citext_gt"("public"."citext", "public"."citext") TO "service_role";



GRANT ALL ON FUNCTION "public"."citext_hash"("public"."citext") TO "postgres";
GRANT ALL ON FUNCTION "public"."citext_hash"("public"."citext") TO "anon";
GRANT ALL ON FUNCTION "public"."citext_hash"("public"."citext") TO "authenticated";
GRANT ALL ON FUNCTION "public"."citext_hash"("public"."citext") TO "service_role";



GRANT ALL ON FUNCTION "public"."citext_hash_extended"("public"."citext", bigint) TO "postgres";
GRANT ALL ON FUNCTION "public"."citext_hash_extended"("public"."citext", bigint) TO "anon";
GRANT ALL ON FUNCTION "public"."citext_hash_extended"("public"."citext", bigint) TO "authenticated";
GRANT ALL ON FUNCTION "public"."citext_hash_extended"("public"."citext", bigint) TO "service_role";



GRANT ALL ON FUNCTION "public"."citext_larger"("public"."citext", "public"."citext") TO "postgres";
GRANT ALL ON FUNCTION "public"."citext_larger"("public"."citext", "public"."citext") TO "anon";
GRANT ALL ON FUNCTION "public"."citext_larger"("public"."citext", "public"."citext") TO "authenticated";
GRANT ALL ON FUNCTION "public"."citext_larger"("public"."citext", "public"."citext") TO "service_role";



GRANT ALL ON FUNCTION "public"."citext_le"("public"."citext", "public"."citext") TO "postgres";
GRANT ALL ON FUNCTION "public"."citext_le"("public"."citext", "public"."citext") TO "anon";
GRANT ALL ON FUNCTION "public"."citext_le"("public"."citext", "public"."citext") TO "authenticated";
GRANT ALL ON FUNCTION "public"."citext_le"("public"."citext", "public"."citext") TO "service_role";



GRANT ALL ON FUNCTION "public"."citext_lt"("public"."citext", "public"."citext") TO "postgres";
GRANT ALL ON FUNCTION "public"."citext_lt"("public"."citext", "public"."citext") TO "anon";
GRANT ALL ON FUNCTION "public"."citext_lt"("public"."citext", "public"."citext") TO "authenticated";
GRANT ALL ON FUNCTION "public"."citext_lt"("public"."citext", "public"."citext") TO "service_role";



GRANT ALL ON FUNCTION "public"."citext_ne"("public"."citext", "public"."citext") TO "postgres";
GRANT ALL ON FUNCTION "public"."citext_ne"("public"."citext", "public"."citext") TO "anon";
GRANT ALL ON FUNCTION "public"."citext_ne"("public"."citext", "public"."citext") TO "authenticated";
GRANT ALL ON FUNCTION "public"."citext_ne"("public"."citext", "public"."citext") TO "service_role";



GRANT ALL ON FUNCTION "public"."citext_pattern_cmp"("public"."citext", "public"."citext") TO "postgres";
GRANT ALL ON FUNCTION "public"."citext_pattern_cmp"("public"."citext", "public"."citext") TO "anon";
GRANT ALL ON FUNCTION "public"."citext_pattern_cmp"("public"."citext", "public"."citext") TO "authenticated";
GRANT ALL ON FUNCTION "public"."citext_pattern_cmp"("public"."citext", "public"."citext") TO "service_role";



GRANT ALL ON FUNCTION "public"."citext_pattern_ge"("public"."citext", "public"."citext") TO "postgres";
GRANT ALL ON FUNCTION "public"."citext_pattern_ge"("public"."citext", "public"."citext") TO "anon";
GRANT ALL ON FUNCTION "public"."citext_pattern_ge"("public"."citext", "public"."citext") TO "authenticated";
GRANT ALL ON FUNCTION "public"."citext_pattern_ge"("public"."citext", "public"."citext") TO "service_role";



GRANT ALL ON FUNCTION "public"."citext_pattern_gt"("public"."citext", "public"."citext") TO "postgres";
GRANT ALL ON FUNCTION "public"."citext_pattern_gt"("public"."citext", "public"."citext") TO "anon";
GRANT ALL ON FUNCTION "public"."citext_pattern_gt"("public"."citext", "public"."citext") TO "authenticated";
GRANT ALL ON FUNCTION "public"."citext_pattern_gt"("public"."citext", "public"."citext") TO "service_role";



GRANT ALL ON FUNCTION "public"."citext_pattern_le"("public"."citext", "public"."citext") TO "postgres";
GRANT ALL ON FUNCTION "public"."citext_pattern_le"("public"."citext", "public"."citext") TO "anon";
GRANT ALL ON FUNCTION "public"."citext_pattern_le"("public"."citext", "public"."citext") TO "authenticated";
GRANT ALL ON FUNCTION "public"."citext_pattern_le"("public"."citext", "public"."citext") TO "service_role";



GRANT ALL ON FUNCTION "public"."citext_pattern_lt"("public"."citext", "public"."citext") TO "postgres";
GRANT ALL ON FUNCTION "public"."citext_pattern_lt"("public"."citext", "public"."citext") TO "anon";
GRANT ALL ON FUNCTION "public"."citext_pattern_lt"("public"."citext", "public"."citext") TO "authenticated";
GRANT ALL ON FUNCTION "public"."citext_pattern_lt"("public"."citext", "public"."citext") TO "service_role";



GRANT ALL ON FUNCTION "public"."citext_smaller"("public"."citext", "public"."citext") TO "postgres";
GRANT ALL ON FUNCTION "public"."citext_smaller"("public"."citext", "public"."citext") TO "anon";
GRANT ALL ON FUNCTION "public"."citext_smaller"("public"."citext", "public"."citext") TO "authenticated";
GRANT ALL ON FUNCTION "public"."citext_smaller"("public"."citext", "public"."citext") TO "service_role";



GRANT ALL ON FUNCTION "public"."refresh_cache_evaluator_todo"("p_interview_id" "uuid") TO "anon";
GRANT ALL ON FUNCTION "public"."refresh_cache_evaluator_todo"("p_interview_id" "uuid") TO "authenticated";
GRANT ALL ON FUNCTION "public"."refresh_cache_evaluator_todo"("p_interview_id" "uuid") TO "service_role";



GRANT ALL ON FUNCTION "public"."refresh_cache_interviewer_todo"("p_interview_id" "uuid") TO "anon";
GRANT ALL ON FUNCTION "public"."refresh_cache_interviewer_todo"("p_interview_id" "uuid") TO "authenticated";
GRANT ALL ON FUNCTION "public"."refresh_cache_interviewer_todo"("p_interview_id" "uuid") TO "service_role";



GRANT ALL ON FUNCTION "public"."regexp_match"("public"."citext", "public"."citext") TO "postgres";
GRANT ALL ON FUNCTION "public"."regexp_match"("public"."citext", "public"."citext") TO "anon";
GRANT ALL ON FUNCTION "public"."regexp_match"("public"."citext", "public"."citext") TO "authenticated";
GRANT ALL ON FUNCTION "public"."regexp_match"("public"."citext", "public"."citext") TO "service_role";



GRANT ALL ON FUNCTION "public"."regexp_match"("public"."citext", "public"."citext", "text") TO "postgres";
GRANT ALL ON FUNCTION "public"."regexp_match"("public"."citext", "public"."citext", "text") TO "anon";
GRANT ALL ON FUNCTION "public"."regexp_match"("public"."citext", "public"."citext", "text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."regexp_match"("public"."citext", "public"."citext", "text") TO "service_role";



GRANT ALL ON FUNCTION "public"."regexp_matches"("public"."citext", "public"."citext") TO "postgres";
GRANT ALL ON FUNCTION "public"."regexp_matches"("public"."citext", "public"."citext") TO "anon";
GRANT ALL ON FUNCTION "public"."regexp_matches"("public"."citext", "public"."citext") TO "authenticated";
GRANT ALL ON FUNCTION "public"."regexp_matches"("public"."citext", "public"."citext") TO "service_role";



GRANT ALL ON FUNCTION "public"."regexp_matches"("public"."citext", "public"."citext", "text") TO "postgres";
GRANT ALL ON FUNCTION "public"."regexp_matches"("public"."citext", "public"."citext", "text") TO "anon";
GRANT ALL ON FUNCTION "public"."regexp_matches"("public"."citext", "public"."citext", "text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."regexp_matches"("public"."citext", "public"."citext", "text") TO "service_role";



GRANT ALL ON FUNCTION "public"."regexp_replace"("public"."citext", "public"."citext", "text") TO "postgres";
GRANT ALL ON FUNCTION "public"."regexp_replace"("public"."citext", "public"."citext", "text") TO "anon";
GRANT ALL ON FUNCTION "public"."regexp_replace"("public"."citext", "public"."citext", "text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."regexp_replace"("public"."citext", "public"."citext", "text") TO "service_role";



GRANT ALL ON FUNCTION "public"."regexp_replace"("public"."citext", "public"."citext", "text", "text") TO "postgres";
GRANT ALL ON FUNCTION "public"."regexp_replace"("public"."citext", "public"."citext", "text", "text") TO "anon";
GRANT ALL ON FUNCTION "public"."regexp_replace"("public"."citext", "public"."citext", "text", "text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."regexp_replace"("public"."citext", "public"."citext", "text", "text") TO "service_role";



GRANT ALL ON FUNCTION "public"."regexp_split_to_array"("public"."citext", "public"."citext") TO "postgres";
GRANT ALL ON FUNCTION "public"."regexp_split_to_array"("public"."citext", "public"."citext") TO "anon";
GRANT ALL ON FUNCTION "public"."regexp_split_to_array"("public"."citext", "public"."citext") TO "authenticated";
GRANT ALL ON FUNCTION "public"."regexp_split_to_array"("public"."citext", "public"."citext") TO "service_role";



GRANT ALL ON FUNCTION "public"."regexp_split_to_array"("public"."citext", "public"."citext", "text") TO "postgres";
GRANT ALL ON FUNCTION "public"."regexp_split_to_array"("public"."citext", "public"."citext", "text") TO "anon";
GRANT ALL ON FUNCTION "public"."regexp_split_to_array"("public"."citext", "public"."citext", "text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."regexp_split_to_array"("public"."citext", "public"."citext", "text") TO "service_role";



GRANT ALL ON FUNCTION "public"."regexp_split_to_table"("public"."citext", "public"."citext") TO "postgres";
GRANT ALL ON FUNCTION "public"."regexp_split_to_table"("public"."citext", "public"."citext") TO "anon";
GRANT ALL ON FUNCTION "public"."regexp_split_to_table"("public"."citext", "public"."citext") TO "authenticated";
GRANT ALL ON FUNCTION "public"."regexp_split_to_table"("public"."citext", "public"."citext") TO "service_role";



GRANT ALL ON FUNCTION "public"."regexp_split_to_table"("public"."citext", "public"."citext", "text") TO "postgres";
GRANT ALL ON FUNCTION "public"."regexp_split_to_table"("public"."citext", "public"."citext", "text") TO "anon";
GRANT ALL ON FUNCTION "public"."regexp_split_to_table"("public"."citext", "public"."citext", "text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."regexp_split_to_table"("public"."citext", "public"."citext", "text") TO "service_role";



GRANT ALL ON FUNCTION "public"."replace"("public"."citext", "public"."citext", "public"."citext") TO "postgres";
GRANT ALL ON FUNCTION "public"."replace"("public"."citext", "public"."citext", "public"."citext") TO "anon";
GRANT ALL ON FUNCTION "public"."replace"("public"."citext", "public"."citext", "public"."citext") TO "authenticated";
GRANT ALL ON FUNCTION "public"."replace"("public"."citext", "public"."citext", "public"."citext") TO "service_role";



GRANT ALL ON FUNCTION "public"."split_part"("public"."citext", "public"."citext", integer) TO "postgres";
GRANT ALL ON FUNCTION "public"."split_part"("public"."citext", "public"."citext", integer) TO "anon";
GRANT ALL ON FUNCTION "public"."split_part"("public"."citext", "public"."citext", integer) TO "authenticated";
GRANT ALL ON FUNCTION "public"."split_part"("public"."citext", "public"."citext", integer) TO "service_role";



GRANT ALL ON FUNCTION "public"."strpos"("public"."citext", "public"."citext") TO "postgres";
GRANT ALL ON FUNCTION "public"."strpos"("public"."citext", "public"."citext") TO "anon";
GRANT ALL ON FUNCTION "public"."strpos"("public"."citext", "public"."citext") TO "authenticated";
GRANT ALL ON FUNCTION "public"."strpos"("public"."citext", "public"."citext") TO "service_role";



GRANT ALL ON FUNCTION "public"."texticlike"("public"."citext", "text") TO "postgres";
GRANT ALL ON FUNCTION "public"."texticlike"("public"."citext", "text") TO "anon";
GRANT ALL ON FUNCTION "public"."texticlike"("public"."citext", "text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."texticlike"("public"."citext", "text") TO "service_role";



GRANT ALL ON FUNCTION "public"."texticlike"("public"."citext", "public"."citext") TO "postgres";
GRANT ALL ON FUNCTION "public"."texticlike"("public"."citext", "public"."citext") TO "anon";
GRANT ALL ON FUNCTION "public"."texticlike"("public"."citext", "public"."citext") TO "authenticated";
GRANT ALL ON FUNCTION "public"."texticlike"("public"."citext", "public"."citext") TO "service_role";



GRANT ALL ON FUNCTION "public"."texticnlike"("public"."citext", "text") TO "postgres";
GRANT ALL ON FUNCTION "public"."texticnlike"("public"."citext", "text") TO "anon";
GRANT ALL ON FUNCTION "public"."texticnlike"("public"."citext", "text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."texticnlike"("public"."citext", "text") TO "service_role";



GRANT ALL ON FUNCTION "public"."texticnlike"("public"."citext", "public"."citext") TO "postgres";
GRANT ALL ON FUNCTION "public"."texticnlike"("public"."citext", "public"."citext") TO "anon";
GRANT ALL ON FUNCTION "public"."texticnlike"("public"."citext", "public"."citext") TO "authenticated";
GRANT ALL ON FUNCTION "public"."texticnlike"("public"."citext", "public"."citext") TO "service_role";



GRANT ALL ON FUNCTION "public"."texticregexeq"("public"."citext", "text") TO "postgres";
GRANT ALL ON FUNCTION "public"."texticregexeq"("public"."citext", "text") TO "anon";
GRANT ALL ON FUNCTION "public"."texticregexeq"("public"."citext", "text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."texticregexeq"("public"."citext", "text") TO "service_role";



GRANT ALL ON FUNCTION "public"."texticregexeq"("public"."citext", "public"."citext") TO "postgres";
GRANT ALL ON FUNCTION "public"."texticregexeq"("public"."citext", "public"."citext") TO "anon";
GRANT ALL ON FUNCTION "public"."texticregexeq"("public"."citext", "public"."citext") TO "authenticated";
GRANT ALL ON FUNCTION "public"."texticregexeq"("public"."citext", "public"."citext") TO "service_role";



GRANT ALL ON FUNCTION "public"."texticregexne"("public"."citext", "text") TO "postgres";
GRANT ALL ON FUNCTION "public"."texticregexne"("public"."citext", "text") TO "anon";
GRANT ALL ON FUNCTION "public"."texticregexne"("public"."citext", "text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."texticregexne"("public"."citext", "text") TO "service_role";



GRANT ALL ON FUNCTION "public"."texticregexne"("public"."citext", "public"."citext") TO "postgres";
GRANT ALL ON FUNCTION "public"."texticregexne"("public"."citext", "public"."citext") TO "anon";
GRANT ALL ON FUNCTION "public"."texticregexne"("public"."citext", "public"."citext") TO "authenticated";
GRANT ALL ON FUNCTION "public"."texticregexne"("public"."citext", "public"."citext") TO "service_role";



GRANT ALL ON FUNCTION "public"."translate"("public"."citext", "public"."citext", "text") TO "postgres";
GRANT ALL ON FUNCTION "public"."translate"("public"."citext", "public"."citext", "text") TO "anon";
GRANT ALL ON FUNCTION "public"."translate"("public"."citext", "public"."citext", "text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."translate"("public"."citext", "public"."citext", "text") TO "service_role";



GRANT ALL ON FUNCTION "public"."trg_after_evaluation_refresh"() TO "anon";
GRANT ALL ON FUNCTION "public"."trg_after_evaluation_refresh"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."trg_after_evaluation_refresh"() TO "service_role";



GRANT ALL ON FUNCTION "public"."trg_after_response_refresh"() TO "anon";
GRANT ALL ON FUNCTION "public"."trg_after_response_refresh"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."trg_after_response_refresh"() TO "service_role";



GRANT ALL ON FUNCTION "public"."trg_after_snapshot_refresh"() TO "anon";
GRANT ALL ON FUNCTION "public"."trg_after_snapshot_refresh"() TO "authenticated";
GRANT ALL ON FUNCTION "public"."trg_after_snapshot_refresh"() TO "service_role";












GRANT ALL ON FUNCTION "public"."max"("public"."citext") TO "postgres";
GRANT ALL ON FUNCTION "public"."max"("public"."citext") TO "anon";
GRANT ALL ON FUNCTION "public"."max"("public"."citext") TO "authenticated";
GRANT ALL ON FUNCTION "public"."max"("public"."citext") TO "service_role";



GRANT ALL ON FUNCTION "public"."min"("public"."citext") TO "postgres";
GRANT ALL ON FUNCTION "public"."min"("public"."citext") TO "anon";
GRANT ALL ON FUNCTION "public"."min"("public"."citext") TO "authenticated";
GRANT ALL ON FUNCTION "public"."min"("public"."citext") TO "service_role";















GRANT ALL ON TABLE "public"."applications" TO "anon";
GRANT ALL ON TABLE "public"."applications" TO "authenticated";
GRANT ALL ON TABLE "public"."applications" TO "service_role";



GRANT ALL ON TABLE "public"."cache_evaluator_todo" TO "anon";
GRANT ALL ON TABLE "public"."cache_evaluator_todo" TO "authenticated";
GRANT ALL ON TABLE "public"."cache_evaluator_todo" TO "service_role";



GRANT ALL ON TABLE "public"."cache_interviewer_todo" TO "anon";
GRANT ALL ON TABLE "public"."cache_interviewer_todo" TO "authenticated";
GRANT ALL ON TABLE "public"."cache_interviewer_todo" TO "service_role";



GRANT ALL ON TABLE "public"."candidates" TO "anon";
GRANT ALL ON TABLE "public"."candidates" TO "authenticated";
GRANT ALL ON TABLE "public"."candidates" TO "service_role";



GRANT ALL ON TABLE "public"."evaluation_items" TO "anon";
GRANT ALL ON TABLE "public"."evaluation_items" TO "authenticated";
GRANT ALL ON TABLE "public"."evaluation_items" TO "service_role";



GRANT ALL ON TABLE "public"."evaluations" TO "anon";
GRANT ALL ON TABLE "public"."evaluations" TO "authenticated";
GRANT ALL ON TABLE "public"."evaluations" TO "service_role";



GRANT ALL ON TABLE "public"."interview_questions" TO "anon";
GRANT ALL ON TABLE "public"."interview_questions" TO "authenticated";
GRANT ALL ON TABLE "public"."interview_questions" TO "service_role";



GRANT ALL ON TABLE "public"."interviews" TO "anon";
GRANT ALL ON TABLE "public"."interviews" TO "authenticated";
GRANT ALL ON TABLE "public"."interviews" TO "service_role";



GRANT ALL ON TABLE "public"."job_questions" TO "anon";
GRANT ALL ON TABLE "public"."job_questions" TO "authenticated";
GRANT ALL ON TABLE "public"."job_questions" TO "service_role";



GRANT ALL ON TABLE "public"."jobs" TO "anon";
GRANT ALL ON TABLE "public"."jobs" TO "authenticated";
GRANT ALL ON TABLE "public"."jobs" TO "service_role";



GRANT ALL ON TABLE "public"."profiles" TO "anon";
GRANT ALL ON TABLE "public"."profiles" TO "authenticated";
GRANT ALL ON TABLE "public"."profiles" TO "service_role";



GRANT ALL ON TABLE "public"."prompt_versions" TO "anon";
GRANT ALL ON TABLE "public"."prompt_versions" TO "authenticated";
GRANT ALL ON TABLE "public"."prompt_versions" TO "service_role";



GRANT ALL ON TABLE "public"."prompts" TO "anon";
GRANT ALL ON TABLE "public"."prompts" TO "authenticated";
GRANT ALL ON TABLE "public"."prompts" TO "service_role";



GRANT ALL ON TABLE "public"."questions" TO "anon";
GRANT ALL ON TABLE "public"."questions" TO "authenticated";
GRANT ALL ON TABLE "public"."questions" TO "service_role";



GRANT ALL ON TABLE "public"."responses" TO "anon";
GRANT ALL ON TABLE "public"."responses" TO "authenticated";
GRANT ALL ON TABLE "public"."responses" TO "service_role";



GRANT ALL ON TABLE "public"."revoked_jti" TO "anon";
GRANT ALL ON TABLE "public"."revoked_jti" TO "authenticated";
GRANT ALL ON TABLE "public"."revoked_jti" TO "service_role";



GRANT ALL ON TABLE "public"."rubric_versions" TO "anon";
GRANT ALL ON TABLE "public"."rubric_versions" TO "authenticated";
GRANT ALL ON TABLE "public"."rubric_versions" TO "service_role";



GRANT ALL ON TABLE "public"."rubrics" TO "anon";
GRANT ALL ON TABLE "public"."rubrics" TO "authenticated";
GRANT ALL ON TABLE "public"."rubrics" TO "service_role";



GRANT ALL ON TABLE "public"."transcripts" TO "anon";
GRANT ALL ON TABLE "public"."transcripts" TO "authenticated";
GRANT ALL ON TABLE "public"."transcripts" TO "service_role";









ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES TO "service_role";






ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS TO "service_role";






ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES TO "service_role";































RESET ALL;
