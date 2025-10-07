import 'package:supabase_flutter/supabase_flutter.dart';
import '../models/job_model.dart';
import '../models/job_question_model.dart';
import 'jobs_datasource.dart';

class JobsDataSourceImpl implements JobsDataSource {
  final SupabaseClient _supabase = Supabase.instance.client;

  @override
  Future<List<JobModel>> getAllJobs() async {
    try {
      final response = await _supabase
          .from('jobs')
          .select('*')
          .order('timestamp_created', ascending: false);

      return (response as List)
          .map((json) => JobModel.fromSupabase(json))
          .toList();
    } catch (e) {
      throw Exception('Error al obtener jobs: ${e.toString()}');
    }
  }

  @override
  Future<List<JobQuestionModel>> getJobQuestions(String jobRole) async {
    try {
      final response = await _supabase.rpc('get_job_questions', params: {
        'job_role_param': jobRole,
      });

      return (response as List)
          .map((json) => JobQuestionModel.fromSupabase(json))
          .toList();
    } catch (e) {
      // Si la función RPC no existe, usar query manual
      try {
        final response = await _supabase
            .from('jobs')
            .select('''
              job_role,
              description,
              technical_questions_answers_jobs!inner(
                technical_questions_answers!inner(
                  question,
                  answer
                )
              )
            ''')
            .eq('job_role', jobRole);

        List<JobQuestionModel> questions = [];

        for (var jobData in response) {
          final relations = jobData['technical_questions_answers_jobs'] as List;
          for (var relation in relations) {
            final questionData = relation['technical_questions_answers'];
            questions.add(JobQuestionModel(
              jobRole: jobData['job_role'],
              description: jobData['description'],
              question: questionData['question'],
              answer: questionData['answer'],
            ));
          }
        }

        return questions;
      } catch (e2) {
        throw Exception('Error al obtener preguntas: ${e2.toString()}');
      }
    }
  }

  @override
  Future<JobModel> createJob({
    required String jobRole,
    required String description,
  }) async {
    try {
      final response = await _supabase
          .from('jobs')
          .insert({
        'job_role': jobRole,
        'description': description,
        'timestamp_created': DateTime.now().toIso8601String(),
      })
          .select()
          .single();

      return JobModel.fromSupabase(response);
    } catch (e) {
      throw Exception('Error al crear job: ${e.toString()}');
    }
  }

  @override
  Future<void> deleteJob(int jobId) async {
    try {
      await _supabase.from('jobs').delete().eq('id_job', jobId);
    } catch (e) {
      throw Exception('Error al eliminar job: ${e.toString()}');
    }
  }
}