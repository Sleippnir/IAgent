import '../models/candidate_model.dart';
import '../models/interview_model.dart';

abstract class CandidatesDataSource {
  Future<CandidateModel> createCandidate({
    required String name,
    required String lastName,
    required String phoneNum,
    required String email,
    required int age,
    required String linkedinUrl,
    String? resume,
  });

  Future<InterviewModel> createInterview({
    required int idCandidate,
    required int idJob,
    required int idUser,
  });

  Future<Map<String, dynamic>?> authenticateCandidate({
    required String phoneNum,
    required String accessToken,
  });

  // AGREGAR ESTOS MÉTODOS NUEVOS:
  Future<Map<String, dynamic>?> findCandidateByEmail(String email);

  Future<bool> validateCandidateCredentials({
    required String email,
    required String phoneNum,
    required String accessToken,
  });

  Future<List<Map<String, dynamic>>> getInterviewsByEmail(String email);

  Future<List<CandidateModel>> getAllCandidates();

  Future<List<InterviewModel>> getAllInterviews();

  Future<void> deleteCandidate(int candidateId);
}