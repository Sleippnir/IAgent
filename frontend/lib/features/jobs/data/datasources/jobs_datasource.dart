import '../models/job_model.dart';
import '../models/job_question_model.dart';

abstract class JobsDataSource {
  Future<List<JobModel>> getAllJobs();
  Future<JobModel> createJob({
    required String jobRole,
    required String description,
  });
  Future<void> deleteJob(int jobId);
  Future<List<JobQuestionModel>> getJobQuestions(String jobRole);
}