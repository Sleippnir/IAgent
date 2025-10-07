import 'package:supabase_flutter/supabase_flutter.dart';
import '../models/candidate_model.dart';
import '../models/interview_model.dart';
import 'candidates_datasource.dart';
import 'dart:math';

class CandidatesDataSourceImpl implements CandidatesDataSource {
  final SupabaseClient supabase = Supabase.instance.client;

  // Método para autenticar candidato con phone + token
  @override
  Future<Map<String, dynamic>?> authenticateCandidate({
    required String phoneNum,
    required String accessToken,
  }) async {
    try {
      print('🔍 DEBUG [authenticateCandidate]: Iniciando autenticación');
      print('   📱 phoneNum recibido: "$phoneNum"');
      print('   🔑 accessToken recibido: "$accessToken"');

      // 📍 DEBUG: Query que se va a ejecutar
      print('🔍 DEBUG: Ejecutando query en tabla users:');
      print('   - SELECT: id_user, name_user, email_user, phone_user, access_token, rol_user!inner(role_name)');
      print('   - WHERE: phone_user = "$phoneNum" AND access_token = "$accessToken" AND rol_user.role_name = "candidate"');

      final response = await supabase
          .from('users')
          .select('''
            id_user,
            name_user,
            email_user,
            phone_user,
            access_token,
            rol_user!inner(role_name)
          ''')
          .eq('phone_user', phoneNum)
          .eq('access_token', accessToken)
          .eq('rol_user.role_name', 'candidate')
          .maybeSingle();

      // 📍 DEBUG: Respuesta de Supabase
      print('📨 DEBUG [authenticateCandidate]: Respuesta de Supabase:');
      print('   - Tipo: ${response.runtimeType}');
      print('   - Contenido: $response');

      if (response != null) {
        print('✅ DEBUG: Usuario encontrado en tabla users');
        print('   - id_user: ${response['id_user']}');
        print('   - name_user: ${response['name_user']}');
        print('   - email_user: ${response['email_user']}');
        print('   - phone_user: ${response['phone_user']}');
        print('   - access_token: ${response['access_token']}');
        print('   - rol_user: ${response['rol_user']}');
        print('⚠️ DEBUG: NOTA - Este método devuelve datos de tabla USERS, no CANDIDATES');
      } else {
        print('❌ DEBUG: No se encontró usuario con estas credenciales');
        print('   - Verificar si existe en tabla users');
        print('   - Verificar si el role es candidate');
        print('   - Verificar phone_user y access_token exactos');
      }

      return response;
    } catch (e) {
      print('💥 DEBUG [authenticateCandidate]: Error: ${e.toString()}');
      print('💥 DEBUG: Tipo de error: ${e.runtimeType}');
      throw Exception('Error en autenticación: ${e.toString()}');
    }
  }

  Future<List<Map<String, dynamic>>> getInterviewsByEmail(String email) async {
    try {
      print('🔍 DEBUG [getInterviewsByEmail]: Iniciando consulta de entrevistas');
      print('   📧 email recibido: "$email"');

      // Paso 1: Obtener candidato por email
      print('🔍 DEBUG: Paso 1 - Buscando candidato por email en tabla candidates');
      final candidate = await supabase
          .from('candidates')
          .select('id_candidate, name, last_name')
          .eq('email', email)
          .single();

      print('📨 DEBUG: Candidato encontrado:');
      print('   - id_candidate: ${candidate['id_candidate']}');
      print('   - name: ${candidate['name']}');
      print('   - last_name: ${candidate['last_name']}');

      // Paso 2: Obtener entrevistas SIN JOIN complejo
      print('🔍 DEBUG: Paso 2 - Buscando entrevistas para id_candidate: ${candidate['id_candidate']}');
      final interviews = await supabase
          .from('interviews')
          .select('*')
          .eq('id_candidate', candidate['id_candidate'])
          .order('timestamp_created', ascending: false);

      print('📨 DEBUG: Entrevistas encontradas:');
      print('   - Cantidad: ${interviews.length}');
      print('   - Datos brutos: $interviews');

      // Paso 3: Para cada entrevista, obtener info del trabajo
      List<Map<String, dynamic>> result = [];
      print('🔍 DEBUG: Paso 3 - Obteniendo info de trabajos para cada entrevista');

      for (int i = 0; i < interviews.length; i++) {
        var interview = interviews[i];
        print('🔍 DEBUG: Procesando entrevista ${i + 1}/${interviews.length}:');
        print('   - id_interview: ${interview['id_interview']}');
        print('   - id_job: ${interview['id_job']}');
        print('   - is_complete: ${interview['is_complete']}');

        final job = await supabase
            .from('jobs')
            .select('job_role, description')
            .eq('id_job', interview['id_job'])
            .single();

        print('📨 DEBUG: Job encontrado para id_job ${interview['id_job']}:');
        print('   - job_role: ${job['job_role']}');
        print('   - description length: ${job['description']?.length ?? 0} chars');

        final processedInterview = {
          ...Map<String, dynamic>.from(interview),
          'jobs': job,
          'candidate_info': {
            'name': candidate['name'],
            'last_name': candidate['last_name'],
            'full_name': '${candidate['name']} ${candidate['last_name']}',
          }
        };

        result.add(processedInterview);
        print('✅ DEBUG: Entrevista procesada y agregada al resultado');
      }

      print('🎉 DEBUG [getInterviewsByEmail]: Resultado final:');
      print('   - Total entrevistas procesadas: ${result.length}');
      print('   - Estructura de primera entrevista: ${result.isNotEmpty ? result[0].keys.toList() : 'N/A'}');

      return result;

    } catch (e) {
      print('💥 DEBUG [getInterviewsByEmail]: Error: ${e.toString()}');
      print('💥 DEBUG: Tipo de error: ${e.runtimeType}');
      throw Exception('Error al obtener entrevistas: ${e.toString()}');
    }
  }

  // Método para obtener entrevistas de un candidato específico
  Future<List<Map<String, dynamic>>> getInterviewsByCandidateCredentials({
    required String phoneNum,
    required String accessToken,
  }) async {
    try {
      print('🔍 DEBUG [getInterviewsByCandidateCredentials]: Iniciando consulta compleja');
      print('   📱 phoneNum: "$phoneNum"');
      print('   🔑 accessToken: "$accessToken"');

      print('🔍 DEBUG: Ejecutando query con JOINs complejos...');
      final response = await supabase
          .from('interviews')
          .select('''
          id_interview,
          is_complete,
          interview_start_time,
          timestamp_created,
          jobs!inner(job_role, description),
          users!inner(
            phone_user,
            access_token,
            candidates!inner(name, last_name)
          )
        ''')
          .eq('users.phone_user', phoneNum)
          .eq('users.access_token', accessToken)
          .order('timestamp_created', ascending: false);

      print('📨 DEBUG: Respuesta de query compleja:');
      print('   - Cantidad: ${response.length}');
      print('   - Datos: $response');

      return List<Map<String, dynamic>>.from(response);
    } catch (e) {
      print('💥 DEBUG [getInterviewsByCandidateCredentials]: Error: ${e.toString()}');
      throw Exception('Error al obtener entrevistas: ${e.toString()}');
    }
  }

  // Generar token aleatorio de 6 caracteres
  String _generateAccessToken() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    final random = Random();
    return String.fromCharCodes(Iterable.generate(
        6, (_) => chars.codeUnitAt(random.nextInt(chars.length))));
  }

  @override
  Future<CandidateModel> createCandidate({
    required String name,
    required String lastName,
    required String phoneNum,
    required String email,
    required int age,
    required String linkedinUrl,
    String? resume,
  }) async {
    try {
      // Generar token único
      final accessToken = _generateAccessToken();

      // Crear candidato en tabla 'candidates'
      final candidateResponse = await supabase
          .from('candidates')
          .insert({
        'name': name,
        'last_name': lastName,
        'phone_num': phoneNum,
        'email': email,
        'age': age,
        'linkedin_url': linkedinUrl,
        'resume': resume,
        'access_token': accessToken,
        'timestamp_created': DateTime.now().toIso8601String(),
      })
          .select()
          .single();

      // Obtener id_rol para candidato
      final rolResponse = await supabase
          .from('rol_user')
          .select('id_rol')
          .eq('role_name', 'candidate')
          .single();

      // Crear usuario para login con token
      await supabase
          .from('users')
          .insert({
        'id_rol': rolResponse['id_rol'],
        'name_user': '$name $lastName',
        'email_user': email,
        'password': accessToken, // Usar token como password
        'phone_user': phoneNum,
        'access_token': accessToken,
        'timestamp_created': DateTime.now().toIso8601String(),
      });

      return CandidateModel.fromSupabase(candidateResponse);
    } catch (e) {
      throw Exception('Error al crear candidato: ${e.toString()}');
    }
  }

  // Método para buscar candidato por email (Paso 1)
  Future<Map<String, dynamic>?> findCandidateByEmail(String email) async {
    try {
      final response = await supabase
          .from('candidates')
          .select('id_candidate, name, last_name, phone_num, email, access_token')
          .eq('email', email)
          .maybeSingle();

      return response;
    } catch (e) {
      throw Exception('Error al buscar candidato: ${e.toString()}');
    }
  }

  // Agregar este método en candidates_datasource_impl.dart
  Future<String> getJobRoleById(int jobId) async {
    try {
      final response = await supabase
          .from('jobs')
          .select('job_role')
          .eq('id_job', jobId)
          .single();

      return response['job_role'] as String;
    } catch (e) {
      return 'Job Role'; // Fallback
    }
  }


  // Método para validar phone + token del candidato (Paso 2)
  Future<bool> validateCandidateCredentials({
    required String email,
    required String phoneNum,
    required String accessToken,
  }) async {
    try {
      final response = await supabase
          .from('candidates')
          .select('id_candidate')
          .eq('email', email)
          .eq('phone_num', phoneNum)
          .eq('access_token', accessToken)
          .maybeSingle();

      return response != null;
    } catch (e) {
      throw Exception('Error al validar credenciales: ${e.toString()}');
    }
  }

  @override
  Future<InterviewModel> createInterview({
    required int idCandidate,
    required int idJob,
    required int idUser,
  }) async {
    try {
      final response = await supabase
          .from('interviews')
          .insert({
        'id_candidate': idCandidate,
        'id_job': idJob,
        'id_user': idUser,
        'is_complete': false,
        'timestamp_created': DateTime.now().toIso8601String(),
      })
          .select()
          .single();

      return InterviewModel.fromSupabase(response);
    } catch (e) {
      throw Exception('Error al crear entrevista: ${e.toString()}');
    }
  }

  @override
  Future<List<CandidateModel>> getAllCandidates() async {
    try {
      final response = await supabase
          .from('candidates')
          .select('*')
          .order('timestamp_created', ascending: false);

      return (response as List)
          .map((json) => CandidateModel.fromSupabase(json))
          .toList();
    } catch (e) {
      throw Exception('Error al obtener candidatos: ${e.toString()}');
    }
  }

  @override
  Future<List<InterviewModel>> getAllInterviews() async {
    try {
      final response = await supabase
          .from('interviews')
          .select('*')
          .order('timestamp_created', ascending: false);

      return (response as List)
          .map((json) => InterviewModel.fromSupabase(json))
          .toList();
    } catch (e) {
      throw Exception('Error al obtener entrevistas: ${e.toString()}');
    }
  }

  @override
  Future<void> deleteCandidate(int candidateId) async {
    try {
      await supabase.from('candidates').delete().eq('id_candidate', candidateId);
    } catch (e) {
      throw Exception('Error al eliminar candidato: ${e.toString()}');
    }
  }
}