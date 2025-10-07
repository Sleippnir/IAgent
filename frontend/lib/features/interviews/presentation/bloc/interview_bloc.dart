import 'package:flutter_bloc/flutter_bloc.dart';
import '../../data/datasources/candidates_datasource_impl.dart';
import 'interview_event.dart';
import 'interview_state.dart';

class InterviewBloc extends Bloc<InterviewEvent, InterviewState> {
  final CandidatesDataSourceImpl _candidatesDataSource;

  InterviewBloc({
    required CandidatesDataSourceImpl candidatesDataSource,
  })  : _candidatesDataSource = candidatesDataSource,
        super(const InterviewInitial()) {

    print('🔧 DEBUG [InterviewBloc]: Inicializando BLoC');

    on<SetPendingCandidate>(_onSetPendingCandidate);
    on<CreateInterviewForPendingCandidate>(_onCreateInterviewForPendingCandidate);
    on<ClearPendingCandidate>(_onClearPendingCandidate);
  }

  void _onSetPendingCandidate(
      SetPendingCandidate event,
      Emitter<InterviewState> emit,
      ) {
    print('📝 DEBUG [_onSetPendingCandidate]: Estableciendo candidato pendiente');
    print('   - candidateId: ${event.candidateId}');
    print('   - candidateName: "${event.candidateName}"');

    emit(InterviewWithPendingCandidate(
      candidateId: event.candidateId,
      candidateName: event.candidateName,
    ));

    print('✅ DEBUG: Estado cambiado a InterviewWithPendingCandidate');
  }

  void _onCreateInterviewForPendingCandidate(
      CreateInterviewForPendingCandidate event,
      Emitter<InterviewState> emit,
      ) async {
    print('🚀 DEBUG [_onCreateInterviewForPendingCandidate]: Iniciando creación de entrevista');
    print('   - jobId: ${event.jobId}');
    print('   - jobRole: "${event.jobRole}"');
    print('   - Estado actual: ${state.runtimeType}');

    // Verificar que hay un candidato pendiente
    if (state is! InterviewWithPendingCandidate) {
      print('❌ DEBUG: No hay candidato pendiente');
      print('   - Estado actual: ${state.runtimeType}');
      emit(const InterviewError(message: 'No hay candidato pendiente para crear entrevista'));
      return;
    }

    final currentState = state as InterviewWithPendingCandidate;
    print('✅ DEBUG: Candidato pendiente encontrado:');
    print('   - candidateId: ${currentState.candidateId}');
    print('   - candidateName: "${currentState.candidateName}"');

    // Emitir estado de carga
    print('⏳ DEBUG: Emitiendo estado de carga...');
    emit(InterviewCreating(
      candidateId: currentState.candidateId,
      candidateName: currentState.candidateName,
    ));

    try {
      // Crear la entrevista en la base de datos
      const adminUserId = 1; // Hardcoded por ahora

      print('🔍 DEBUG: Llamando createInterview con:');
      print('   - idCandidate: ${currentState.candidateId}');
      print('   - idJob: ${event.jobId}');
      print('   - idUser: $adminUserId (hardcoded)');

      final interview = await _candidatesDataSource.createInterview(
        idCandidate: currentState.candidateId,
        idJob: event.jobId,
        idUser: adminUserId,
      );

      print('📨 DEBUG: Respuesta de createInterview:');
      print('   - Tipo: ${interview.runtimeType}');
      print('   - interviewId: ${interview.idInterview}');
      print('   - Datos completos: $interview');

      // Emitir estado de éxito
      print('🎉 DEBUG: Emitiendo estado de éxito...');
      emit(InterviewCreated(
        interviewId: interview.idInterview!,
        candidateName: currentState.candidateName,
        jobRole: event.jobRole,
      ));

      print('✅ DEBUG: Entrevista creada exitosamente');
      print('   - ID de entrevista: ${interview.idInterview}');
      print('   - Para candidato: "${currentState.candidateName}"');
      print('   - Trabajo: "${event.jobRole}"');

      // Limpiar estado después de un tiempo
      print('⏰ DEBUG: Esperando 3 segundos antes de limpiar estado...');
      await Future.delayed(const Duration(seconds: 3));

      print('🧹 DEBUG: Limpiando estado - volviendo a InterviewInitial');
      emit(const InterviewInitial());

    } catch (e) {
      print('💥 DEBUG [_onCreateInterviewForPendingCandidate]: Error: ${e.toString()}');
      print('💥 DEBUG: Tipo de error: ${e.runtimeType}');
      print('💥 DEBUG: Stack trace: ${StackTrace.current}');

      emit(InterviewError(message: 'Error al crear entrevista: ${e.toString()}'));
    }
  }

  void _onClearPendingCandidate(
      ClearPendingCandidate event,
      Emitter<InterviewState> emit,
      ) {
    print('🧹 DEBUG [_onClearPendingCandidate]: Limpiando candidato pendiente');
    print('   - Estado anterior: ${state.runtimeType}');

    emit(const InterviewInitial());

    print('✅ DEBUG: Estado limpiado - volviendo a InterviewInitial');
  }
}