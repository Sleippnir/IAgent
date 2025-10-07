import '../../domain/entities/job.dart';

class JobModel extends Job {
  const JobModel({
    required super.idJob,
    required super.jobRole,
    required super.description,
    required super.timestampCreated,
  });

  factory JobModel.fromSupabase(Map<String, dynamic> json) {
    return JobModel(
      idJob: json['id_job'],
      jobRole: json['job_role'],
      description: json['description'],
      timestampCreated: DateTime.parse(json['timestamp_created']),
    );
  }

  Map<String, dynamic> toSupabase() {
    return {
      'job_role': jobRole,
      'description': description,
      'timestamp_created': timestampCreated.toIso8601String(),
    };
  }
}