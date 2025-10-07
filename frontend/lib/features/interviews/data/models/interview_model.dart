class InterviewModel {
  final int? idInterview;
  final int idCandidate;
  final int idJob;
  final int idUser;
  final bool isComplete;
  final DateTime? interviewStartTime;
  final DateTime? timestampCreated;

  InterviewModel({
    this.idInterview,
    required this.idCandidate,
    required this.idJob,
    required this.idUser,
    this.isComplete = false,
    this.interviewStartTime,
    this.timestampCreated,
  });

  factory InterviewModel.fromSupabase(Map<String, dynamic> json) {
    return InterviewModel(
      idInterview: json['id_interview'],
      idCandidate: json['id_candidate'],
      idJob: json['id_job'],
      idUser: json['id_user'],
      isComplete: json['is_complete'] ?? false,
      interviewStartTime: json['interview_start_time'] != null
          ? DateTime.parse(json['interview_start_time'])
          : null,
      timestampCreated: json['timestamp_created'] != null
          ? DateTime.parse(json['timestamp_created'])
          : null,
    );
  }

  Map<String, dynamic> toSupabase() {
    return {
      'id_candidate': idCandidate,
      'id_job': idJob,
      'id_user': idUser,
      'is_complete': isComplete,
      'interview_start_time': interviewStartTime?.toIso8601String(),
      'timestamp_created': timestampCreated?.toIso8601String() ?? DateTime.now().toIso8601String(),
    };
  }
}