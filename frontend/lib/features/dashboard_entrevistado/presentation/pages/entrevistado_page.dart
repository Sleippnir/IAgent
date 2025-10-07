import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../../interviews/data/datasources/candidates_datasource_impl.dart';

import '../../../interviews/presentation/pages/interview_sesion_page.dart';



class EntrevistadoPage extends StatefulWidget {
  const EntrevistadoPage({super.key});

  @override
  State<EntrevistadoPage> createState() => _EntrevistadoPageState();
}

class _EntrevistadoPageState extends State<EntrevistadoPage> {
  final CandidatesDataSourceImpl _candidatesDataSource = CandidatesDataSourceImpl();

  List<Map<String, dynamic>> _interviews = [];
  bool _isLoading = true;
  String _candidateName = '';
  String? _phone;
  String? _token;

  @override
  void initState() {
    super.initState();
    print('🚀 DEBUG [EntrevistadoPage]: initState() llamado');
    _loadCandidateData();
  }

  Future<void> _loadCandidateData() async {
    print('📖 DEBUG [_loadCandidateData]: Iniciando carga de datos del candidato');

    setState(() {
      _isLoading = true;
    });

    try {
      // 📍 DEBUG: Leer credenciales guardadas
      print('🔍 DEBUG: Leyendo credenciales de SharedPreferences...');
      final prefs = await SharedPreferences.getInstance();
      _phone = prefs.getString('candidate_phone');
      _token = prefs.getString('candidate_token');
      final candidateId = prefs.getInt('candidate_id'); // Si se guardó

      print('📱 DEBUG: Credenciales leídas:');
      print('   - candidate_phone: "$_phone"');
      print('   - candidate_token: "$_token"');
      print('   - candidate_id: "$candidateId"');

      // 📍 DEBUG: Verificar credenciales
      if (_phone == null || _token == null) {
        print('❌ DEBUG: Credenciales faltantes - redirigiendo a login');
        print('   - phone es null: ${_phone == null}');
        print('   - token es null: ${_token == null}');

        if (mounted) {
          Navigator.pushReplacementNamed(context, '/candidate-login');
        }
        return;
      }

      print('✅ DEBUG: Credenciales válidas encontradas');
      print('🔍 DEBUG: Llamando getInterviewsByCandidateCredentials...');

      // 📍 DEBUG: Obtener entrevistas del candidato usando JOINs complejos

// POR ESTA SOLUCIÓN:
// 1. Primero obtener el email del usuario autenticado
      final userResponse = await _candidatesDataSource.authenticateCandidate(
        phoneNum: _phone!,
        accessToken: _token!,
      );

      if (userResponse == null) {
        throw Exception('Usuario no encontrado');
      }

      final userEmail = userResponse['email_user'];
      print('📧 DEBUG: Email extraído del usuario: "$userEmail"');

// 2. Usar el método que SÍ funciona
      final interviews = await _candidatesDataSource.getInterviewsByEmail(userEmail);

      print('🎉 DEBUG: Entrevistas obtenidas exitosamente: ${interviews.length}');

      print('📨 DEBUG: Respuesta de getInterviewsByCandidateCredentials:');
      print('   - Tipo: ${interviews.runtimeType}');
      print('   - Cantidad de entrevistas: ${interviews.length}');
      print('   - Datos completos: $interviews');

      // 📍 DEBUG: Procesar respuesta
      setState(() {
        _interviews = interviews;
        _isLoading = false;

        // Extraer nombre del candidato de la primera entrevista
        if (interviews.isNotEmpty) {
          print('🔍 DEBUG: Extrayendo nombre del candidato...');
          final firstInterview = interviews.first;
          print('   - Primera entrevista: $firstInterview');
          print('   - Clave "users": ${firstInterview['users']}');

          try {
            final candidate = firstInterview['users']['candidates'];
            print('   - Datos del candidato: $candidate');
            _candidateName = '${candidate['name']} ${candidate['last_name']}';
            print('✅ DEBUG: Nombre extraído: "$_candidateName"');
          } catch (e) {
            print('💥 DEBUG: Error al extraer nombre del candidato: $e');
            print('💡 DEBUG: Estructura no es la esperada');
          }
        } else {
          print('⚠️ DEBUG: No hay entrevistas para procesar nombre');
        }
      });

      // 📍 DEBUG: Estado final
      print('🎉 DEBUG: Carga completada exitosamente');
      print('   - Total entrevistas cargadas: ${_interviews.length}');
      print('   - Nombre del candidato: "$_candidateName"');

    } catch (e) {
      print('💥 DEBUG [_loadCandidateData]: Error: ${e.toString()}');
      print('💥 DEBUG: Tipo de error: ${e.runtimeType}');
      print('💥 DEBUG: Stack trace: ${StackTrace.current}');

      // 📍 DEBUG: Fallback - intentar método alternativo
      print('🔄 DEBUG: Intentando método alternativo con getInterviewsByEmail...');

      try {
        // Necesitamos el email - intentar extraerlo de algún lado o usar un método diferente
        print('⚠️ DEBUG: No tenemos email guardado para método alternativo');
        print('💡 DEBUG: Posibles soluciones:');
        print('   1. Guardar email en login');
        print('   2. Buscar candidato por phone/token en tabla candidates');
        print('   3. Revisar JOINs en getInterviewsByCandidateCredentials');

      } catch (fallbackError) {
        print('💥 DEBUG: Error en fallback también: $fallbackError');
      }

      setState(() {
        _isLoading = false;
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error al cargar datos: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _logout() async {
    print('🚪 DEBUG [_logout]: Cerrando sesión...');

    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('candidate_phone');
    await prefs.remove('candidate_token');
    await prefs.remove('candidate_id'); // Limpiar ID también

    print('✅ DEBUG: Credenciales limpiadas de SharedPreferences');

    if (mounted) {
      Navigator.pushReplacementNamed(context, '/');
    }
  }

  Color _getStatusColor(bool isComplete) {
    return isComplete ? Colors.green : Colors.orange;
  }

  String _getStatusText(bool isComplete) {
    return isComplete ? 'Completada' : 'Pendiente';
  }

  @override
  Widget build(BuildContext context) {
    print('🎨 DEBUG [build]: Construyendo UI');
    print('   - _isLoading: $_isLoading');
    print('   - _interviews.length: ${_interviews.length}');
    print('   - _candidateName: "$_candidateName"');

    return Scaffold(
      backgroundColor: const Color(0xFFF5F1EB),
      appBar: AppBar(
        title: Text('Dashboard - ${_candidateName.isNotEmpty ? _candidateName : 'Candidato'}'),
        backgroundColor: const Color(0xFF6ECCC4),
        foregroundColor: Colors.white,
        elevation: 0,
        automaticallyImplyLeading: false,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: _logout,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header de bienvenida
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      const Color(0xFF6ECCC4),
                      const Color(0xFF6ECCC4).withOpacity(0.8),
                    ],
                  ),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(
                      Icons.person,
                      color: Colors.white,
                      size: 32,
                    ),
                    const SizedBox(height: 12),
                    Text(
                      'Bienvenido, ${_candidateName.split(' ').first}',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    const Text(
                      'Aquí puedes ver y realizar tus entrevistas',
                      style: TextStyle(
                        color: Colors.white70,
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // Estadísticas rápidas
              Row(
                children: [
                  Expanded(
                    child: _buildStatCard(
                      'Total Entrevistas',
                      _interviews.length.toString(),
                      Icons.quiz,
                      Colors.blue,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: _buildStatCard(
                      'Completadas',
                      _interviews.where((i) => i['is_complete'] == true).length.toString(),
                      Icons.check_circle,
                      Colors.green,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: _buildStatCard(
                      'Pendientes',
                      _interviews.where((i) => i['is_complete'] == false).length.toString(),
                      Icons.schedule,
                      Colors.orange,
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 24),

              // Lista de entrevistas
              Row(
                children: [
                  const Icon(Icons.list_alt, color: Color(0xFF6ECCC4)),
                  const SizedBox(width: 8),
                  const Text(
                    'MIS ENTREVISTAS',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // Lista scrolleable de entrevistas
              Expanded(
                child: _interviews.isEmpty
                    ? _buildNoInterviewsWidget()
                    : ListView.separated(
                  itemCount: _interviews.length,
                  separatorBuilder: (context, index) => const SizedBox(height: 12),
                  itemBuilder: (context, index) {
                    final interview = _interviews[index];
                    print('🃏 DEBUG [ListView]: Construyendo card para entrevista $index: ${interview['id_interview']}');
                    return _buildInterviewCard(interview);
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(icon, size: 24, color: color),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          Text(
            title,
            style: const TextStyle(
              fontSize: 12,
              color: Colors.grey,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildInterviewCard(Map<String, dynamic> interview) {
    print('🃏 DEBUG [_buildInterviewCard]: Procesando entrevista: $interview');

    final job = interview['jobs'];
    final isComplete = interview['is_complete'] ?? false;
    final createdAt = DateTime.parse(interview['timestamp_created']);

    print('   - Job data: $job');
    print('   - Is complete: $isComplete');
    print('   - Created at: $createdAt');

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header con trabajo y estado
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    job['job_role'],
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: _getStatusColor(isComplete),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    _getStatusText(isComplete),
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),

            // Descripción del trabajo
            Text(
              job['description'],
              style: const TextStyle(
                fontSize: 14,
                color: Colors.grey,
              ),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 12),

            // Información adicional
            Row(
              children: [
                Icon(Icons.calendar_today, size: 16, color: Colors.grey[600]),
                const SizedBox(width: 4),
                Text(
                  'Creada: ${createdAt.day}/${createdAt.month}/${createdAt.year}',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                ),
                const Spacer(),
                Text(
                  'ID: #${interview['id_interview']}',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Botón de acción
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: isComplete ? null : () => _startInterview(interview),
                icon: Icon(
                  isComplete ? Icons.check_circle : Icons.play_arrow,
                  size: 16,
                ),
                label: Text(
                  isComplete ? 'Entrevista Completada' : 'Iniciar Entrevista',
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: isComplete ? Colors.grey : const Color(0xFF6ECCC4),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNoInterviewsWidget() {
    print('🚫 DEBUG [_buildNoInterviewsWidget]: Mostrando widget de "no hay entrevistas"');

    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.assignment_outlined,
            size: 64,
            color: Colors.grey[400],
          ),
          const SizedBox(height: 16),
          Text(
            'No tienes entrevistas asignadas',
            style: TextStyle(
              fontSize: 18,
              color: Colors.grey[600],
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Contacta al reclutador para más información',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[500],
            ),
          ),
        ],
      ),
    );
  }

  void _startInterview(Map<String, dynamic> interview) {
    print('🎬 DEBUG [_startInterview]: Iniciando entrevista: ${interview['id_interview']}');

    // Extraer datos de la entrevista
    final interviewId = interview['id_interview'] as int;
    final jobRole = interview['jobs']['job_role'] as String;
    final candidateName = _candidateName.isNotEmpty
        ? _candidateName
        : 'Candidato'; // Fallback si no hay nombre

    print('📝 DEBUG: Datos para InterviewSessionPage:');
    print('   - interviewId: $interviewId');
    print('   - jobRole: "$jobRole"');
    print('   - candidateName: "$candidateName"');

    // Navegar a la página de entrevista
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => InterviewSessionPage(
          interviewId: interviewId,
          jobRole: jobRole,
          candidateName: candidateName,
          interviewData: interview,
        ),
      ),
    );
  }}