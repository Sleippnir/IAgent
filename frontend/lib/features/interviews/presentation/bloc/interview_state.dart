import 'package:equatable/equatable.dart';

abstract class InterviewState extends Equatable {
  const InterviewState();

  @override
  List<Object?> get props => [];
}

class InterviewInitial extends InterviewState {
  const InterviewInitial();
}

class InterviewWithPendingCandidate extends InterviewState {
  final int candidateId;
  final String candidateName;

  const InterviewWithPendingCandidate({
    required this.candidateId,
    required this.candidateName,
  });

  @override
  List<Object?> get props => [candidateId, candidateName];
}

class InterviewCreating extends InterviewState {
  final int candidateId;
  final String candidateName;

  const InterviewCreating({
    required this.candidateId,
    required this.candidateName,
  });

  @override
  List<Object?> get props => [candidateId, candidateName];
}

class InterviewCreated extends InterviewState {
  final int interviewId;
  final String candidateName;
  final String jobRole;

  const InterviewCreated({
    required this.interviewId,
    required this.candidateName,
    required this.jobRole,
  });

  @override
  List<Object?> get props => [interviewId, candidateName, jobRole];
}

class InterviewError extends InterviewState {
  final String message;

  const InterviewError({required this.message});

  @override
  List<Object?> get props => [message];
}