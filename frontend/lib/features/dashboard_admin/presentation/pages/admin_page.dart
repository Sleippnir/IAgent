import 'package:flutter/material.dart';
import '../../../jobs/presentation/pages/jobs_page.dart';
import '../../../interviews/presentation/pages/create_interview_page.dart';
import '../../../interviews/data/datasources/candidates_datasource_impl.dart';


class AdminPage extends StatefulWidget {
  const AdminPage({super.key});

  @override
  State<AdminPage> createState() => _AdminPageState();
}

class _AdminPageState extends State<AdminPage> {
  final CandidatesDataSourceImpl _dataSource = CandidatesDataSourceImpl();
  bool _isLoadingStats = true;
  Map<String, int> _stats = {
    'candidates': 0,
    'interviews': 0,
    'completed': 0,
    'pending': 0,
  };

  @override
  void initState() {
    super.initState();
    _loadStats();
  }

  Future<void> _loadStats() async {
    try {
      final candidates = await _dataSource.getAllCandidates();
      final interviews = await _dataSource.getAllInterviews();

      final completed = interviews.where((i) => i.isComplete).length;
      final pending = interviews.length - completed;

      setState(() {
        _stats = {
          'candidates': candidates.length,
          'interviews': interviews.length,
          'completed': completed,
          'pending': pending,
        };
        _isLoadingStats = false;
      });
    } catch (e) {
      setState(() {
        _isLoadingStats = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final screenHeight = MediaQuery.of(context).size.height;
    final screenWidth = MediaQuery.of(context).size.width;
    final availableHeight = screenHeight - MediaQuery.of(context).padding.top - kToolbarHeight;

    final headerHeight = availableHeight * 0.08;
    final statsHeight = availableHeight * 0.16;
    final gridHeight = availableHeight * 0.66;
    final actionsHeight = availableHeight * 0.10;

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(
        title: Text(
          'Dashboard - Admin/Reclutador',
          style: TextStyle(fontSize: screenWidth < 600 ? 16 : 18),
        ),
        backgroundColor: Theme.of(context).colorScheme.primary,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadStats,
            tooltip: 'Actualizar estadísticas',
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => Navigator.pushReplacementNamed(context, '/'),
          ),
        ],
      ),
      body: SafeArea(
        child: Padding(
          padding: EdgeInsets.all(screenWidth * 0.02),
          child: Column(
            children: [
              // Header mejorado
              SizedBox(
                height: headerHeight,
                child: Container(
                  width: double.infinity,
                  padding: EdgeInsets.symmetric(
                    horizontal: screenWidth * 0.03,
                    vertical: headerHeight * 0.15,
                  ),
                  decoration: BoxDecoration(
                    gradient: LinearGradient(
                      colors: [
                        Theme.of(context).colorScheme.primary,
                        Theme.of(context).colorScheme.primary.withOpacity(0.8),
                      ],
                    ),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        Icons.admin_panel_settings,
                        color: Colors.white,
                        size: headerHeight * 0.5,
                      ),
                      SizedBox(width: screenWidth * 0.03),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(
                              'Panel de Control - Entrevistador Virtual',
                              style: TextStyle(
                                color: Colors.white,
                                fontSize: headerHeight * 0.28,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            Text(
                              'Gestiona candidatos, entrevistas y análisis',
                              style: TextStyle(
                                color: Colors.white70,
                                fontSize: headerHeight * 0.20,
                              ),
                            ),
                          ],
                        ),
                      ),
                      Container(
                        padding: EdgeInsets.symmetric(
                          horizontal: screenWidth * 0.02,
                          vertical: headerHeight * 0.05,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          'v1.0',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: headerHeight * 0.18,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              SizedBox(height: screenWidth * 0.02),

              // Estadísticas mejoradas
              SizedBox(
                height: statsHeight,
                child: _isLoadingStats
                    ? const Center(child: CircularProgressIndicator())
                    : Row(
                  children: [
                    Expanded(
                      child: _buildStatCard(
                        'Candidatos\nRegistrados',
                        '${_stats['candidates']}',
                        Icons.people,
                        Colors.blue,
                        statsHeight,
                        screenWidth,
                      ),
                    ),
                    SizedBox(width: screenWidth * 0.015),
                    Expanded(
                      child: _buildStatCard(
                        'Entrevistas\nCreadas',
                        '${_stats['interviews']}',
                        Icons.quiz,
                        Colors.green,
                        statsHeight,
                        screenWidth,
                      ),
                    ),
                    SizedBox(width: screenWidth * 0.015),
                    Expanded(
                      child: _buildStatCard(
                        'Completadas',
                        '${_stats['completed']}',
                        Icons.check_circle,
                        Colors.orange,
                        statsHeight,
                        screenWidth,
                      ),
                    ),
                    SizedBox(width: screenWidth * 0.015),
                    Expanded(
                      child: _buildStatCard(
                        'Pendientes',
                        '${_stats['pending']}',
                        Icons.schedule,
                        Colors.purple,
                        statsHeight,
                        screenWidth,
                      ),
                    ),
                  ],
                ),
              ),

              SizedBox(height: screenWidth * 0.02),

              // GridView mejorado
              SizedBox(
                height: gridHeight,
                child: GridView.count(
                  physics: const NeverScrollableScrollPhysics(),
                  crossAxisCount: screenWidth < 600 ? 2 : 3,
                  mainAxisSpacing: gridHeight * 0.03,
                  crossAxisSpacing: screenWidth * 0.015,
                  childAspectRatio: screenWidth < 600 ? 2.2 : 2.5,
                  children: [
                    _buildActionCard(
                      context,
                      'Gestionar\nPreguntas',
                      Icons.work_outline,
                      Colors.blue,
                      gridHeight,
                          () => Navigator.push(
                        context,
                        MaterialPageRoute(builder: (context) => const JobsPage()),
                      ),
                      isActive: true,
                    ),
                    _buildActionCard(
                      context,
                      'Crear\nEntrevista',
                      Icons.quiz,
                      Colors.green,
                      gridHeight,
                          () => Navigator.push(
                        context,
                        MaterialPageRoute(builder: (context) => const CreateInterviewPage()),
                      ),
                      isActive: true,
                    ),
                    _buildActionCard(
                      context,
                      'Ver\nCandidatos',
                      Icons.people,
                      Colors.orange,
                      gridHeight,
                          () => _navigateToCandidates(context),
                      isActive: true,
                    ),
                    _buildActionCard(
                      context,
                      'Gestión de\nEntrevistas',
                      Icons.video_call,
                      Colors.purple,
                      gridHeight,
                          () => _navigateToInterviews(context),
                      isActive: true,
                    ),
                    _buildActionCard(
                      context,
                      'Análisis y\nReportes',
                      Icons.analytics,
                      Colors.indigo,
                      gridHeight,
                          () => _showAnalytics(context),
                      isActive: true,
                    ),
                    _buildActionCard(
                      context,
                      'Configuración',
                      Icons.settings,
                      Colors.grey,
                      gridHeight,
                          () => _showSettings(context),
                      isActive: false,
                    ),
                  ],
                ),
              ),

              // Acciones rápidas mejoradas
              SizedBox(
                height: actionsHeight,
                child: Row(
                  children: [
                    Expanded(
                      child: SizedBox(
                        height: actionsHeight,
                        child: ElevatedButton.icon(
                          onPressed: () => Navigator.push(
                            context,
                            MaterialPageRoute(builder: (context) => const CreateInterviewPage()),
                          ),
                          icon: Icon(Icons.add, size: actionsHeight * 0.3),
                          label: Text(
                            'Nueva Entrevista',
                            style: TextStyle(fontSize: actionsHeight * 0.25),
                          ),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Theme.of(context).colorScheme.primary,
                            foregroundColor: Colors.white,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                          ),
                        ),
                      ),
                    ),
                    SizedBox(width: screenWidth * 0.015),
                    Expanded(
                      child: SizedBox(
                        height: actionsHeight,
                        child: OutlinedButton.icon(
                          onPressed: () => _showAnalytics(context),
                          icon: Icon(Icons.analytics, size: actionsHeight * 0.3),
                          label: Text(
                            'Ver Análisis',
                            style: TextStyle(fontSize: actionsHeight * 0.25),
                          ),
                          style: OutlinedButton.styleFrom(
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildActionCard(
      BuildContext context,
      String title,
      IconData icon,
      Color color,
      double gridHeight,
      VoidCallback onTap, {
        bool isActive = false,
      }) {
    final cardHeight = gridHeight / 6;

    return Card(
      elevation: isActive ? 3 : 1,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
        side: isActive
            ? BorderSide(color: color.withOpacity(0.3), width: 1)
            : BorderSide.none,
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(8),
        child: Container(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(8),
            gradient: isActive
                ? LinearGradient(
              colors: [color.withOpacity(0.05), Colors.white],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            )
                : null,
          ),
          child: Padding(
            padding: EdgeInsets.all(cardHeight * 0.15),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  icon,
                  size: cardHeight * 0.45,
                  color: isActive ? color : Colors.grey,
                ),
                SizedBox(height: cardHeight * 0.1),
                Text(
                  title,
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: cardHeight * 0.22,
                    fontWeight: isActive ? FontWeight.w600 : FontWeight.w500,
                    color: isActive ? Colors.black87 : Colors.grey[600],
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
                if (!isActive) ...[
                  SizedBox(height: cardHeight * 0.05),
                  Container(
                    padding: EdgeInsets.symmetric(
                      horizontal: cardHeight * 0.1,
                      vertical: cardHeight * 0.02,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.grey[100],
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      'Próximamente',
                      style: TextStyle(
                        fontSize: cardHeight * 0.12,
                        color: Colors.grey[600],
                      ),
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildStatCard(String label, String value, IconData icon, Color color, double statsHeight, double screenWidth) {
    return Container(
      height: statsHeight,
      padding: EdgeInsets.all(statsHeight * 0.08),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
        boxShadow: [
          BoxShadow(
            color: color.withOpacity(0.1),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: statsHeight * 0.25, color: color),
          SizedBox(height: statsHeight * 0.05),
          Text(
            value,
            style: TextStyle(
              fontSize: statsHeight * 0.22,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          Text(
            label,
            style: TextStyle(
              fontSize: statsHeight * 0.12,
              color: Colors.grey[700],
              fontWeight: FontWeight.w500,
            ),
            textAlign: TextAlign.center,
            maxLines: 2,
          ),
        ],
      ),
    );
  }

  void _navigateToCandidates(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const AdminCandidatesPage(),
      ),
    );
  }

  void _navigateToInterviews(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const AdminInterviewsPage(),
      ),
    );
  }

  void _showAnalytics(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => AdminAnalyticsPage(stats: _stats),
      ),
    );
  }

  void _showSettings(BuildContext context) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Configuración - Próximamente disponible'),
        backgroundColor: Colors.orange,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }
}

// Páginas adicionales simples para la demo
class AdminCandidatesPage extends StatelessWidget {
  const AdminCandidatesPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Gestión de Candidatos'),
        backgroundColor: Colors.orange,
        foregroundColor: Colors.white,
      ),
      body: const Center(
        child: Padding(
          padding: EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.people, size: 64, color: Colors.orange),
              SizedBox(height: 16),
              Text(
                'Gestión de Candidatos',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
              SizedBox(height: 8),
              Text(
                'Visualiza y administra todos los candidatos registrados',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 16, color: Colors.grey),
              ),
              SizedBox(height: 24),
              Text(
                'Funcionalidades disponibles:\n• Lista de candidatos\n• Filtros y búsqueda\n• Historial de entrevistas\n• Estados y evaluaciones',
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class AdminInterviewsPage extends StatefulWidget {
  const AdminInterviewsPage({super.key});

  @override
  State<AdminInterviewsPage> createState() => _AdminInterviewsPageState();
}

class _AdminInterviewsPageState extends State<AdminInterviewsPage> {
  final CandidatesDataSourceImpl _dataSource = CandidatesDataSourceImpl();
  List<Map<String, dynamic>> _interviews = [];
  List<Map<String, dynamic>> _filteredInterviews = [];
  Set<int> _selectedRows = {};
  bool _isLoading = true;
  String _searchText = '';
  List<String> _activeFilters = ['In Progress', 'Complete'];

  @override
  void initState() {
    super.initState();
    _loadRealInterviews();
  }

  Future<void> _loadRealInterviews() async {
    setState(() {
      _isLoading = true;
    });

    try {
      // Usar el método que ya existe para obtener datos reales
      final realInterviews = await _dataSource.getAllInterviews();

      List<Map<String, dynamic>> interviewsWithDetails = [];

      // Para cada entrevista, obtener los datos relacionados con consultas separadas
      for (var interview in realInterviews) {
        try {
          // Obtener datos del candidato
          final candidates = await _dataSource.getAllCandidates();
          final candidate = candidates.firstWhere(
                (c) => c.idCandidate == interview.idCandidate,
            orElse: () => throw Exception('Candidato no encontrado'),
          );

          // Obtener datos del trabajo (necesitarías un método en el datasource)

          // Obtener el job role real
          String jobRole = 'Job Role'; // Fallback
          try {
            final jobResponse = await _dataSource.supabase
                .from('jobs')
                .select('job_role')
                .eq('id_job', interview.idJob)
                .single();
            jobRole = jobResponse['job_role'] as String;
          } catch (e) {
            print('Error obteniendo job role: $e');
          }

          // Calcular tiempo desde creación
// Calcular tiempo desde creación
          final now = DateTime.now();
          final createdDate = interview.timestampCreated ?? DateTime.now();
          final timeDifference = now.difference(createdDate);
          String timeAgo;
          if (timeDifference.inHours < 24) {
            timeAgo = '${timeDifference.inHours}h ago';
          } else {
            timeAgo = '${timeDifference.inDays}d ago';
          }
          interviewsWithDetails.add({
            'id_interview': interview.idInterview,
            'job_role': jobRole, // Aquí necesitas hacer JOIN con jobs
            'is_status': interview.isComplete ? 'Complete' : 'In Progress',
            'interview_start_time': timeAgo,
            'candidate_name': '${candidate.name} ${candidate.lastName}',
            'interview_complete': interview.isComplete,
            'created_date': interview.timestampCreated,
            'id_candidate': interview.idCandidate,
            'id_job': interview.idJob,
            'id_user': interview.idUser,
          });
        } catch (e) {
          print('Error procesando entrevista ${interview.idInterview}: $e');
          // Continuar con la siguiente entrevista
        }
      }

      setState(() {
        _interviews = interviewsWithDetails;
        _filteredInterviews = interviewsWithDetails;
        _isLoading = false;
      });
    } catch (e) {
      print('Error cargando entrevistas: $e');
      setState(() {
        _isLoading = false;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error al cargar entrevistas: ${e.toString()}'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  void _filterInterviews() {
    setState(() {
      _filteredInterviews = _interviews.where((interview) {
        final matchesSearch = _searchText.isEmpty ||
            interview['job_role'].toLowerCase().contains(_searchText.toLowerCase()) ||
            interview['candidate_name'].toLowerCase().contains(_searchText.toLowerCase());

        final matchesFilter = _activeFilters.contains(interview['is_status']);

        return matchesSearch && matchesFilter;
      }).toList();
    });
  }

  void _toggleRowSelection(int interviewId) {
    setState(() {
      if (_selectedRows.contains(interviewId)) {
        _selectedRows.remove(interviewId);
      } else {
        _selectedRows.add(interviewId);
      }
    });
  }

  void _toggleFilter(String filter) {
    setState(() {
      if (_activeFilters.contains(filter)) {
        _activeFilters.remove(filter);
      } else {
        _activeFilters.add(filter);
      }
      _filterInterviews();
    });
  }

  void _changeInterviewStatus(int interviewId, String newStatus) {
    setState(() {
      final interviewIndex = _interviews.indexWhere((i) => i['id_interview'] == interviewId);
      if (interviewIndex != -1) {
        _interviews[interviewIndex]['is_status'] = newStatus;
        _interviews[interviewIndex]['interview_complete'] = newStatus == 'Complete';
      }
      _filterInterviews();
    });

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Estado actualizado a: $newStatus'),
        backgroundColor: Colors.green,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F1EB),
      appBar: AppBar(
        title: const Text('Gestión de Entrevistas'),
        backgroundColor: Colors.purple,
        foregroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadRealInterviews,
            tooltip: 'Recargar datos',
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Padding(
        padding: const EdgeInsets.all(24.0),
        child: Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(12),
            boxShadow: [
              BoxShadow(
                color: Colors.grey.withOpacity(0.1),
                spreadRadius: 1,
                blurRadius: 10,
                offset: const Offset(0, 1),
              ),
            ],
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header con título y controles
              Padding(
                padding: const EdgeInsets.all(20),
                child: Row(
                  children: [
                    const Text(
                      'Interviews',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(width: 16),
                    // Filtros activos
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.grey[100],
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          const Icon(Icons.filter_alt, size: 16, color: Colors.grey),
                          const SizedBox(width: 4),
                          Text(
                            '${_activeFilters.length} Filters',
                            style: const TextStyle(fontSize: 12),
                          ),
                          const SizedBox(width: 4),
                          GestureDetector(
                            onTap: () {
                              setState(() {
                                _activeFilters.clear();
                                _filterInterviews();
                              });
                            },
                            child: const Icon(Icons.close, size: 16, color: Colors.red),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 16),
                    // Filtros disponibles
                    ...['In Progress', 'Complete', 'Pending'].map((filter) {
                      final isActive = _activeFilters.contains(filter);
                      return Padding(
                        padding: const EdgeInsets.only(right: 8),
                        child: GestureDetector(
                          onTap: () => _toggleFilter(filter),
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                            decoration: BoxDecoration(
                              color: isActive ? Colors.blue : Colors.grey[200],
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Text(
                              filter,
                              style: TextStyle(
                                color: isActive ? Colors.white : Colors.grey[700],
                                fontSize: 12,
                              ),
                            ),
                          ),
                        ),
                      );
                    }).toList(),
                    const Spacer(),
                    // Campo de búsqueda
                    SizedBox(
                      width: 200,
                      child: TextField(
                        decoration: InputDecoration(
                          hintText: 'Buscar...',
                          prefixIcon: const Icon(Icons.search, size: 18),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(8),
                            borderSide: BorderSide(color: Colors.grey[300]!),
                          ),
                          contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                        ),
                        onChanged: (value) {
                          _searchText = value;
                          _filterInterviews();
                        },
                      ),
                    ),
                  ],
                ),
              ),
              const Divider(height: 1),
              // Headers de la tabla
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                color: Colors.grey[50],
                child: const Row(
                  children: [
                    SizedBox(width: 40), // Espacio para checkbox
                    Expanded(flex: 2, child: Text('JOB_ROLE', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 12))),
                    Expanded(flex: 1, child: Text('IS_STATUS', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 12))),
                    Expanded(flex: 1, child: Text('INTERVIEW_START_TIME', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 12))),
                    Expanded(flex: 1, child: Text('NAME', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 12))),
                    SizedBox(width: 100, child: Text('ACTIONS', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 12))),
                  ],
                ),
              ),
              // Filas de datos
              Expanded(
                child: _filteredInterviews.isEmpty
                    ? const Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.inbox, size: 64, color: Colors.grey),
                      SizedBox(height: 16),
                      Text(
                        'No hay entrevistas que coincidan con los filtros',
                        style: TextStyle(color: Colors.grey, fontSize: 16),
                      ),
                    ],
                  ),
                )
                    : ListView.builder(
                  itemCount: _filteredInterviews.length,
                  itemBuilder: (context, index) {
                    final interview = _filteredInterviews[index];
                    final isSelected = _selectedRows.contains(interview['id_interview']);

                    return Container(
                      color: isSelected ? Colors.blue.withOpacity(0.1) : null,
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                        child: Row(
                          children: [
                            // Checkbox
                            SizedBox(
                              width: 40,
                              child: Checkbox(
                                value: isSelected,
                                onChanged: (value) => _toggleRowSelection(interview['id_interview']),
                              ),
                            ),
                            // Job Role
                            Expanded(
                              flex: 2,
                              child: Text(
                                interview['job_role'],
                                style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
                              ),
                            ),
                            // Status
                            Expanded(
                              flex: 1,
                              child: Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                decoration: BoxDecoration(
                                  color: interview['is_status'] == 'Complete' ? Colors.green : Colors.orange,
                                  borderRadius: BorderRadius.circular(4),
                                ),
                                child: Text(
                                  interview['is_status'],
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontSize: 12,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ),
                            ),
                            // Interview Start Time
                            Expanded(
                              flex: 1,
                              child: Text(
                                interview['interview_start_time'],
                                style: const TextStyle(fontSize: 14),
                              ),
                            ),
                            // Name with avatar
                            Expanded(
                              flex: 1,
                              child: Row(
                                children: [
                                  const CircleAvatar(
                                    radius: 12,
                                    backgroundColor: Colors.green,
                                    child: Icon(Icons.person, size: 16, color: Colors.white),
                                  ),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      interview['candidate_name'],
                                      style: const TextStyle(fontSize: 14),
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            // Actions
                            SizedBox(
                              width: 100,
                              child: PopupMenuButton<String>(
                                onSelected: (value) => _changeInterviewStatus(interview['id_interview'], value),
                                itemBuilder: (BuildContext context) => <PopupMenuEntry<String>>[
                                  const PopupMenuItem<String>(
                                    value: 'In Progress',
                                    child: Text('En Progreso'),
                                  ),
                                  const PopupMenuItem<String>(
                                    value: 'Complete',
                                    child: Text('Completada'),
                                  ),
                                  const PopupMenuItem<String>(
                                    value: 'Pending',
                                    child: Text('Pendiente'),
                                  ),
                                ],
                                child: const Icon(Icons.more_vert),
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
              ),
              // Footer con estadísticas
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.grey[50],
                  borderRadius: const BorderRadius.only(
                    bottomLeft: Radius.circular(12),
                    bottomRight: Radius.circular(12),
                  ),
                ),
                child: Row(
                  children: [
                    Text(
                      'Total: ${_filteredInterviews.length} entrevistas',
                      style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
                    ),
                    const SizedBox(width: 16),
                    Text(
                      'Seleccionadas: ${_selectedRows.length}',
                      style: const TextStyle(fontSize: 14, color: Colors.grey),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}


class AdminAnalyticsPage extends StatelessWidget {
  final Map<String, int> stats;

  const AdminAnalyticsPage({super.key, required this.stats});

  @override
  Widget build(BuildContext context) {
    final successRate = stats['interviews']! > 0
        ? (stats['completed']! / stats['interviews']! * 100).round()
        : 0;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Análisis y Reportes'),
        backgroundColor: Colors.indigo,
        foregroundColor: Colors.white,
      ),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Métricas del Sistema',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 24),
            Row(
              children: [
                Expanded(
                  child: _buildMetricCard(
                    'Tasa de Finalización',
                    '$successRate%',
                    Icons.trending_up,
                    Colors.green,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _buildMetricCard(
                    'Promedio Candidatos/Día',
                    '${(stats['candidates']! / 7).toStringAsFixed(1)}',
                    Icons.person_add,
                    Colors.blue,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
            const Text(
              'Resumen de Actividad',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 16),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.grey[50],
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.grey[300]!),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('• ${stats['candidates']} candidatos registrados'),
                  Text('• ${stats['interviews']} entrevistas programadas'),
                  Text('• ${stats['completed']} entrevistas completadas'),
                  Text('• ${stats['pending']} entrevistas pendientes'),
                  const SizedBox(height: 12),
                  const Text(
                    'El sistema está funcionando correctamente con un flujo constante de candidatos y entrevistas.',
                    style: TextStyle(fontStyle: FontStyle.italic, color: Colors.grey),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMetricCard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(icon, size: 32, color: color),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          Text(
            title,
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 14, color: Colors.grey),
          ),
        ],
      ),
    );
  }
}