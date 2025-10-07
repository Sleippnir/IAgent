import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../../../jobs/presentation/pages/jobs_page.dart';
import '../../data/datasources/candidates_datasource_impl.dart';
import '../../data/models/candidate_model.dart';
import '../bloc/interview_bloc.dart';
import '../bloc/interview_event.dart';

class CreateInterviewPage extends StatefulWidget {
  const CreateInterviewPage({super.key});

  @override
  State<CreateInterviewPage> createState() => _CreateInterviewPageState();
}

class _CreateInterviewPageState extends State<CreateInterviewPage> {
  final _formKey = GlobalKey<FormState>();
  final CandidatesDataSourceImpl _candidatesDataSource = CandidatesDataSourceImpl();

  // Controllers para los campos
  final _nameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _emailController = TextEditingController();
  final _ageController = TextEditingController();
  final _linkedinController = TextEditingController();

  bool _isLoading = false;
  String? _resumeFileName;

  @override
  void dispose() {
    _nameController.dispose();
    _lastNameController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    _ageController.dispose();
    _linkedinController.dispose();
    super.dispose();
  }

  Future<void> _createCandidate() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      // Crear el candidato
      final candidate = await _candidatesDataSource.createCandidate(
        name: _nameController.text.trim(),
        lastName: _lastNameController.text.trim(),
        phoneNum: _phoneController.text.trim(),
        email: _emailController.text.trim(),
        age: int.parse(_ageController.text.trim()),
        linkedinUrl: _linkedinController.text.trim(),
        resume: _resumeFileName,
      );

      // Mostrar mensaje de éxito con token
      if (mounted) {
        // Guardar candidato en BLoC para uso posterior
        context.read<InterviewBloc>().add(SetPendingCandidate(
          candidateId: candidate.idCandidate!,
          candidateName: candidate.fullName,
        ));

        // Mostrar dialog con información de acceso
        showDialog(
          context: context,
          barrierDismissible: false,
          builder: (context) => _buildSuccessDialog(candidate),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final isWeb = screenWidth > 600;

    return Scaffold(
      backgroundColor: const Color(0xFFF5F1EB),
      appBar: AppBar(
        title: const Text('Crear Nueva Entrevista'),
        backgroundColor: const Color(0xFF6ECCC4),
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header
                const Text(
                  'Crear Perfil de Candidato',
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Colors.black87,
                  ),
                ),
                const SizedBox(height: 8),
                const Text(
                  'Complete la información del candidato para crear una nueva entrevista',
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.grey,
                  ),
                ),
                const SizedBox(height: 32),

                // Contenedor principal
                Container(
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
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: isWeb ? _buildWebLayout() : _buildMobileLayout(),
                  ),
                ),

                const SizedBox(height: 24),

                // Botón crear candidato
                SizedBox(
                  width: double.infinity,
                  height: 48,
                  child: ElevatedButton(
                    onPressed: _isLoading ? null : _createCandidate,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF6ECCC4),
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                    child: _isLoading
                        ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                      ),
                    )
                        : const Text(
                      'Crear Candidato y Continuar',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildSuccessDialog(CandidateModel candidate) {
    final accessText = 'Teléfono: ${candidate.phoneNum}\nCódigo: ${candidate.accessToken}';

    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Icono de éxito
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                color: Colors.green.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.check_circle,
                color: Colors.green,
                size: 50,
              ),
            ),
            const SizedBox(height: 16),

            // Título
            Text(
              '¡Candidato Creado Exitosamente!',
              style: const TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),

            // Nombre del candidato
            Text(
              candidate.fullName,
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey[600],
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),

            // Información de acceso
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF6ECCC4).withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFF6ECCC4).withOpacity(0.3)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.key, color: Color(0xFF6ECCC4), size: 20),
                      const SizedBox(width: 8),
                      const Text(
                        'CREDENCIALES DE ACCESO',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: Colors.grey,
                          letterSpacing: 1,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),

                  // Teléfono
                  Row(
                    children: [
                      const Icon(Icons.phone, color: Color(0xFF6ECCC4), size: 18),
                      const SizedBox(width: 8),
                      Text(
                        'Teléfono: ${candidate.phoneNum}',
                        style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),

                  // Token
                  Row(
                    children: [
                      const Icon(Icons.vpn_key, color: Color(0xFF6ECCC4), size: 18),
                      const SizedBox(width: 8),
                      Text(
                        'Código: ${candidate.accessToken}',
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF6ECCC4),
                          letterSpacing: 2,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Botón copiar
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: () {
                  // TODO: Implementar copia al portapapeles
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Credenciales copiadas al portapapeles'),
                      backgroundColor: Colors.green,
                    ),
                  );
                },
                icon: const Icon(Icons.copy),
                label: const Text('Copiar Credenciales'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: const Color(0xFF6ECCC4),
                  side: const BorderSide(color: Color(0xFF6ECCC4)),
                  padding: const EdgeInsets.symmetric(vertical: 12),
                ),
              ),
            ),
            const SizedBox(height: 12),

            // Botón continuar
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {
                  Navigator.of(context).pop(); // Cerrar dialog
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => const JobsPage(),
                    ),
                  );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF6ECCC4),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
                child: const Text(
                  'Continuar con Entrevista',
                  style: TextStyle(fontWeight: FontWeight.w600),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildWebLayout() {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Columna izquierda - Formulario
        Expanded(
          flex: 2,
          child: _buildFormFields(),
        ),
        const SizedBox(width: 32),
        // Columna derecha - Resume upload
        Expanded(
          flex: 1,
          child: _buildResumeUpload(),
        ),
      ],
    );
  }

  Widget _buildMobileLayout() {
    return Column(
      children: [
        _buildFormFields(),
        const SizedBox(height: 24),
        _buildResumeUpload(),
      ],
    );
  }

  Widget _buildFormFields() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Información del candidato
        Row(
          children: [
            const Icon(Icons.person, color: Color(0xFF6ECCC4)),
            const SizedBox(width: 8),
            const Text(
              'CANDIDATE',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: Colors.grey,
                letterSpacing: 1,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),

        // Nombre y Apellido
        Row(
          children: [
            Expanded(
              child: _buildTextField(
                controller: _nameController,
                label: 'Nombre',
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return 'El nombre es requerido';
                  }
                  return null;
                },
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildTextField(
                controller: _lastNameController,
                label: 'Apellido',
                validator: (value) {
                  if (value == null || value.trim().isEmpty) {
                    return 'El apellido es requerido';
                  }
                  return null;
                },
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),

        // Teléfono
        _buildTextField(
          controller: _phoneController,
          label: 'Teléfono',
          keyboardType: TextInputType.phone,
          validator: (value) {
            if (value == null || value.trim().isEmpty) {
              return 'El teléfono es requerido';
            }
            return null;
          },
        ),
        const SizedBox(height: 16),

        // Email
        _buildTextField(
          controller: _emailController,
          label: 'Email',
          keyboardType: TextInputType.emailAddress,
          validator: (value) {
            if (value == null || value.trim().isEmpty) {
              return 'El email es requerido';
            }
            if (!value.contains('@')) {
              return 'Ingrese un email válido';
            }
            return null;
          },
        ),
        const SizedBox(height: 16),

        // Edad
        _buildTextField(
          controller: _ageController,
          label: 'Edad',
          keyboardType: TextInputType.number,
          validator: (value) {
            if (value == null || value.trim().isEmpty) {
              return 'La edad es requerida';
            }
            final age = int.tryParse(value);
            if (age == null || age < 18 || age > 80) {
              return 'Ingrese una edad válida (18-80)';
            }
            return null;
          },
        ),
        const SizedBox(height: 16),

        // LinkedIn URL
        _buildTextField(
          controller: _linkedinController,
          label: 'LinkedIn URL',
          validator: (value) {
            if (value == null || value.trim().isEmpty) {
              return 'La URL de LinkedIn es requerida';
            }
            if (!value.contains('linkedin.com')) {
              return 'Ingrese una URL válida de LinkedIn';
            }
            return null;
          },
        ),
      ],
    );
  }

  Widget _buildTextField({
    required TextEditingController controller,
    required String label,
    TextInputType? keyboardType,
    String? Function(String?)? validator,
  }) {
    return TextFormField(
      controller: controller,
      keyboardType: keyboardType,
      validator: validator,
      decoration: InputDecoration(
        labelText: label,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide(color: Colors.grey.shade300),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: Color(0xFF6ECCC4), width: 2),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      ),
    );
  }

  Widget _buildResumeUpload() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Icon(Icons.description, color: Color(0xFF6ECCC4)),
            const SizedBox(width: 8),
            const Text(
              'RESUME',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: Colors.grey,
                letterSpacing: 1,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),

        // Área de drag & drop
        Container(
          width: double.infinity,
          height: 200,
          decoration: BoxDecoration(
            border: Border.all(
              color: Colors.grey.shade300,
              style: BorderStyle.solid,
              width: 2,
            ),
            borderRadius: BorderRadius.circular(8),
          ),
          child: InkWell(
            onTap: () {
              // TODO: Implementar selección de archivo
              setState(() {
                _resumeFileName = 'resume_ejemplo.pdf';
              });
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Funcionalidad de carga de archivos próximamente'),
                  backgroundColor: Colors.orange,
                ),
              );
            },
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.cloud_upload,
                  size: 48,
                  color: Colors.grey.shade400,
                ),
                const SizedBox(height: 16),
                Text(
                  _resumeFileName ?? 'Drag & drop file',
                  style: TextStyle(
                    fontSize: 16,
                    color: _resumeFileName != null ? const Color(0xFF6ECCC4) : Colors.grey.shade600,
                    fontWeight: _resumeFileName != null ? FontWeight.w600 : FontWeight.normal,
                  ),
                ),
                if (_resumeFileName == null) ...[
                  const SizedBox(height: 8),
                  Text(
                    'O haz clic para seleccionar',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey.shade500,
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ],
    );
  }
}