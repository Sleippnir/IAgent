import 'package:equatable/equatable.dart';

abstract class InterviewEvent extends Equatable {
  const InterviewEvent();

  @override
  List<Object?> get props => [];
}

class SetPendingCandidate extends InterviewEvent {
  final int candidateId;
  final String candidateName;

  const SetPendingCandidate({
    required this.candidateId,
    required this.candidateName,
  });

  @override
  List<Object?> get props => [candidateId, candidateName];
}

class CreateInterviewForPendingCandidate extends InterviewEvent {
  final int jobId;
  final String jobRole;

  const CreateInterviewForPendingCandidate({
    required this.jobId,
    required this.jobRole,
  });

  @override
  List<Object?> get props => [jobId, jobRole];
}

class ClearPendingCandidate extends InterviewEvent {
  const ClearPendingCandidate();
}