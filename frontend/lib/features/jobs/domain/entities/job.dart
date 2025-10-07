import 'package:equatable/equatable.dart';

class Job extends Equatable {
  final int idJob;
  final String jobRole;
  final String description;
  final DateTime timestampCreated;

  const Job({
    required this.idJob,
    required this.jobRole,
    required this.description,
    required this.timestampCreated,
  });

  @override
  List<Object> get props => [idJob, jobRole, description, timestampCreated];
}