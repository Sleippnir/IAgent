class JobQuestionModel {
  final String jobRole;
  final String description;
  final String question;
  final String answer;

  const JobQuestionModel({
    required this.jobRole,
    required this.description,
    required this.question,
    required this.answer,
  });

  factory JobQuestionModel.fromSupabase(Map<String, dynamic> json) {
    return JobQuestionModel(
      jobRole: json['job_role'] ?? '',
      description: json['description'] ?? '',
      question: json['question'] ?? '',
      answer: json['answer'] ?? '',
    );
  }
}