import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../data/datasources/jobs_datasource_impl.dart';
import '../../data/models/job_model.dart';
import '../../data/models/job_question_model.dart';
import '../../../interviews/presentation/bloc/interview_bloc.dart';
import '../../../interviews/presentation/bloc/interview_state.dart';
import '../../../interviews/presentation/bloc/interview_event.dart';

class JobsPage extends StatefulWidget {
  const JobsPage({super.key});

  @override
  State<JobsPage> createState() => _JobsPageState();
}

class _JobsPageState extends State<JobsPage> {
  final JobsDataSourceImpl _jobsDataSource = JobsDataSourceImpl();
  List<JobModel> _jobs = [];
  List<JobQuestionModel> _questions = [];
  JobModel? _selectedJob;
  bool _isLoading = true;
  bool _isLoadingQuestions = false;

  @override
  void initState() {
    super.initState();
    _loadJobs();
  }

  Future<void> _loadJobs() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final jobs = await _jobsDataSource.getAllJobs();
      setState(() {
        _jobs = jobs;
        _isLoading = false;
        if (jobs.isNotEmpty) {
          _selectedJob = jobs.first;
        }
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(e.toString()),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _generateQuestions() async {
    if (_selectedJob == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Selecciona un trabajo primero'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    setState(() {
      _isLoadingQuestions = true;
      _questions = [];
    });

    try {
      // Generar preguntas técnicas (funcionalidad original)
      final questions = await _jobsDataSource.getJobQuestions(_selectedJob!.jobRole);
      setState(() {
        _questions = questions;
        _isLoadingQuestions = false;
      });

      // Si hay candidato pendiente, crear entrevista
      final interviewState = context.read<InterviewBloc>().state;
      if (interviewState is InterviewWithPendingCandidate) {
        context.read<InterviewBloc>().add(CreateInterviewForPendingCandidate(
          jobId: _selectedJob!.idJob,
          jobRole: _selectedJob!.jobRole,
        ));
      } else {
        // Mostrar mensaje normal si no hay candidato
        if (questions.isEmpty) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('No se encontraron preguntas para ${_selectedJob!.jobRole}'),
              backgroundColor: Colors.orange,
            ),
          );
        }
      }
    } catch (e) {
      setState(() {
        _isLoadingQuestions = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error: ${e.toString()}'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return BlocListener<InterviewBloc, InterviewState>(
      listener: (context, state) {
        if (state is InterviewCreated) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                  'Entrevista creada exitosamente para ${state.candidateName}\n'
                      'Trabajo: ${state.jobRole} - ${_questions.length} preguntas generadas'
              ),
              backgroundColor: Colors.green,
              duration: const Duration(seconds: 4),
            ),
          );
        } else if (state is InterviewError) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Error: ${state.message}'),
              backgroundColor: Colors.red,
            ),
          );
        }
      },
      child: Scaffold(
        backgroundColor: const Color(0xFFF5F1EB),
        appBar: AppBar(
          title: const Text('Jobs'),
          backgroundColor: Colors.white,
          foregroundColor: Colors.black,
          elevation: 0,
          actions: [
            IconButton(
              onPressed: () {},
              icon: const Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.sort, size: 16),
                  SizedBox(width: 4),
                  Text('Sort', style: TextStyle(fontSize: 12)),
                ],
              ),
            ),
            IconButton(
              onPressed: () {},
              icon: const Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.view_column, size: 16),
                  SizedBox(width: 4),
                  Text('Columns', style: TextStyle(fontSize: 12)),
                ],
              ),
            ),
            IconButton(
              onPressed: () {},
              icon: const Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.filter_alt, size: 16),
                  SizedBox(width: 4),
                  Text('Filter', style: TextStyle(fontSize: 12)),
                ],
              ),
            ),
          ],
        ),
        body: Column(
          children: [
            // Banner de candidato usando BlocBuilder
            BlocBuilder<InterviewBloc, InterviewState>(
              builder: (context, state) {
                if (state is InterviewWithPendingCandidate || state is InterviewCreating) {
                  final candidateName = state is InterviewWithPendingCandidate
                      ? state.candidateName
                      : (state as InterviewCreating).candidateName;
                  final isCreating = state is InterviewCreating;

                  return Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(16),
                    margin: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.blue.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.blue.withOpacity(0.3)),
                    ),
                    child: Row(
                      children: [
                        Icon(
                            isCreating ? Icons.sync : Icons.person_add,
                            color: Colors.blue
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                isCreating ? 'CREANDO ENTREVISTA...' : 'CANDIDATO PENDIENTE:',
                                style: const TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.w600,
                                  color: Colors.grey,
                                  letterSpacing: 1,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                candidateName,
                                style: const TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.blue,
                                ),
                              ),
                            ],
                          ),
                        ),
                        if (isCreating)
                          const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          ),
                      ],
                    ),
                  );
                }
                return const SizedBox.shrink();
              },
            ),

            // Contenido principal (original)
            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : SingleChildScrollView(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  children: [
                    // Contenedor principal (código original)
                    Container(
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: const Color(0xFF6ECCC4), width: 2),
                      ),
                      child: Column(
                        children: [
                          // Header
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                            decoration: const BoxDecoration(
                              border: Border(
                                bottom: BorderSide(color: Color(0xFF6ECCC4), width: 1),
                              ),
                            ),
                            child: Row(
                              children: [
                                Expanded(
                                  flex: 1,
                                  child: Text(
                                    'JOB_ROLE',
                                    style: TextStyle(
                                      fontWeight: FontWeight.w600,
                                      color: Colors.grey[600],
                                      fontSize: 12,
                                    ),
                                  ),
                                ),
                                Expanded(
                                  flex: 2,
                                  child: Text(
                                    'DESCRIPTION',
                                    style: TextStyle(
                                      fontWeight: FontWeight.w600,
                                      color: Colors.grey[600],
                                      fontSize: 12,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),

                          // Contenido principal
                          Container(
                            height: 400,
                            padding: const EdgeInsets.all(16),
                            child: Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                // Columna JOB_ROLE
                                Expanded(
                                  flex: 1,
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      DropdownButtonFormField<JobModel>(
                                        value: _selectedJob,
                                        decoration: InputDecoration(
                                          border: OutlineInputBorder(
                                            borderRadius: BorderRadius.circular(4),
                                            borderSide: BorderSide(color: Colors.grey[300]!),
                                          ),
                                          contentPadding: const EdgeInsets.symmetric(
                                            horizontal: 12,
                                            vertical: 8,
                                          ),
                                        ),
                                        hint: const Text('Select job role'),
                                        items: _jobs.map((job) {
                                          return DropdownMenuItem<JobModel>(
                                            value: job,
                                            child: Text(
                                              job.jobRole,
                                              style: const TextStyle(fontSize: 14),
                                            ),
                                          );
                                        }).toList(),
                                        onChanged: (JobModel? value) {
                                          setState(() {
                                            _selectedJob = value;
                                            _questions = [];
                                          });
                                        },
                                        isExpanded: true,
                                      ),

                                      const SizedBox(height: 8),

                                      // Lista scrolleable de jobs
                                      Expanded(
                                        child: Container(
                                          decoration: BoxDecoration(
                                            border: Border.all(color: Colors.grey[300]!),
                                            borderRadius: BorderRadius.circular(4),
                                          ),
                                          child: ListView.builder(
                                            itemCount: _jobs.length,
                                            itemBuilder: (context, index) {
                                              final job = _jobs[index];
                                              final isSelected = _selectedJob?.idJob == job.idJob;

                                              return Container(
                                                color: isSelected
                                                    ? const Color(0xFF6ECCC4).withOpacity(0.1)
                                                    : null,
                                                child: ListTile(
                                                  title: Text(
                                                    job.jobRole,
                                                    style: TextStyle(
                                                      fontSize: 14,
                                                      fontWeight: isSelected
                                                          ? FontWeight.w600
                                                          : FontWeight.normal,
                                                    ),
                                                  ),
                                                  onTap: () {
                                                    setState(() {
                                                      _selectedJob = job;
                                                      _questions = [];
                                                    });
                                                  },
                                                  dense: true,
                                                ),
                                              );
                                            },
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),

                                const SizedBox(width: 24),

                                // Columna DESCRIPTION
                                Expanded(
                                  flex: 2,
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      // Descripción
                                      if (_selectedJob != null) ...[
                                        Container(
                                          width: double.infinity,
                                          height: 200,
                                          padding: const EdgeInsets.all(12),
                                          decoration: BoxDecoration(
                                            border: Border.all(color: Colors.grey[300]!),
                                            borderRadius: BorderRadius.circular(4),
                                          ),
                                          child: Scrollbar(
                                            child: SingleChildScrollView(
                                              child: Text(
                                                _selectedJob!.description,
                                                style: const TextStyle(fontSize: 14),
                                              ),
                                            ),
                                          ),
                                        ),
                                        const SizedBox(height: 16),

                                        // Botón generate questions con estado dinámico
                                        BlocBuilder<InterviewBloc, InterviewState>(
                                          builder: (context, state) {
                                            final hasPendingCandidate = state is InterviewWithPendingCandidate;
                                            final isCreatingInterview = state is InterviewCreating;

                                            return SizedBox(
                                              width: double.infinity,
                                              child: ElevatedButton.icon(
                                                onPressed: (_isLoadingQuestions || isCreatingInterview) ? null : _generateQuestions,
                                                icon: (_isLoadingQuestions || isCreatingInterview)
                                                    ? const SizedBox(
                                                  width: 16,
                                                  height: 16,
                                                  child: CircularProgressIndicator(strokeWidth: 2),
                                                )
                                                    : const Icon(Icons.auto_awesome, size: 16),
                                                label: Text(
                                                    (_isLoadingQuestions || isCreatingInterview)
                                                        ? 'Loading...'
                                                        : hasPendingCandidate
                                                        ? 'Generate Questions & Create Interview'
                                                        : 'generate questions'
                                                ),
                                                style: ElevatedButton.styleFrom(
                                                  backgroundColor: const Color(0xFF6ECCC4),
                                                  foregroundColor: Colors.white,
                                                  shape: RoundedRectangleBorder(
                                                    borderRadius: BorderRadius.circular(6),
                                                  ),
                                                  padding: const EdgeInsets.symmetric(vertical: 12),
                                                ),
                                              ),
                                            );
                                          },
                                        ),
                                      ] else ...[
                                        Container(
                                          width: double.infinity,
                                          padding: const EdgeInsets.all(12),
                                          decoration: BoxDecoration(
                                            border: Border.all(color: Colors.grey[300]!),
                                            borderRadius: BorderRadius.circular(4),
                                          ),
                                          child: Text(
                                            'Select a job role to see description',
                                            style: TextStyle(
                                              fontSize: 14,
                                              color: Colors.grey[500],
                                              fontStyle: FontStyle.italic,
                                            ),
                                          ),
                                        ),
                                      ],
                                    ],
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),

                    // Sección de preguntas generadas (código original)
                    if (_questions.isNotEmpty) ...[
                      const SizedBox(height: 24),
                      Container(
                        width: double.infinity,
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: const Color(0xFF6ECCC4), width: 2),
                        ),
                        child: Column(
                          children: [
                            // Header de preguntas
                            Container(
                              padding: const EdgeInsets.all(16),
                              decoration: BoxDecoration(
                                color: const Color(0xFF6ECCC4).withOpacity(0.1),
                                borderRadius: const BorderRadius.vertical(top: Radius.circular(6)),
                              ),
                              child: Row(
                                children: [
                                  const Icon(Icons.quiz, color: Color(0xFF6ECCC4)),
                                  const SizedBox(width: 8),
                                  Text(
                                    'Generated Questions for ${_selectedJob?.jobRole}',
                                    style: const TextStyle(
                                      fontWeight: FontWeight.bold,
                                      fontSize: 16,
                                    ),
                                  ),
                                  const Spacer(),
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                    decoration: BoxDecoration(
                                      color: const Color(0xFF6ECCC4),
                                      borderRadius: BorderRadius.circular(12),
                                    ),
                                    child: Text(
                                      '${_questions.length} questions',
                                      style: const TextStyle(
                                        color: Colors.white,
                                        fontSize: 12,
                                        fontWeight: FontWeight.w600,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),

                            // Lista de preguntas con scroll
                            Container(
                              constraints: const BoxConstraints(maxHeight: 400),
                              child: ListView.separated(
                                shrinkWrap: true,
                                padding: const EdgeInsets.all(16),
                                itemCount: _questions.length,
                                separatorBuilder: (context, index) => const SizedBox(height: 12),
                                itemBuilder: (context, index) {
                                  final question = _questions[index];
                                  return Card(
                                    elevation: 1,
                                    child: ExpansionTile(
                                      title: Text(
                                        'Question ${index + 1}',
                                        style: const TextStyle(
                                          fontWeight: FontWeight.w600,
                                          fontSize: 14,
                                        ),
                                      ),
                                      subtitle: Text(
                                        question.question,
                                        style: const TextStyle(fontSize: 13),
                                        maxLines: 2,
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                      children: [
                                        Padding(
                                          padding: const EdgeInsets.all(16),
                                          child: Column(
                                            crossAxisAlignment: CrossAxisAlignment.start,
                                            children: [
                                              Text(
                                                'Question:',
                                                style: TextStyle(
                                                  fontWeight: FontWeight.w600,
                                                  color: Colors.grey[700],
                                                ),
                                              ),
                                              const SizedBox(height: 4),
                                              Text(question.question),
                                              const SizedBox(height: 12),
                                              Text(
                                                'Answer:',
                                                style: TextStyle(
                                                  fontWeight: FontWeight.w600,
                                                  color: Colors.grey[700],
                                                ),
                                              ),
                                              const SizedBox(height: 4),
                                              Text(question.answer),
                                            ],
                                          ),
                                        ),
                                      ],
                                    ),
                                  );
                                },
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}