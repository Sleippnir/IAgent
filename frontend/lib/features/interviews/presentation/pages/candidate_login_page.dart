import 'package:flutter/material.dart';
import '../../../interviews/data/datasources/candidates_datasource_impl.dart';
import 'package:shared_preferences/shared_preferences.dart';

class CandidateLoginPage extends StatefulWidget {
  const CandidateLoginPage({super.key});

  @override
  State<CandidateLoginPage> createState() => _CandidateLoginPageState();
}

class _CandidateLoginPageState extends State<CandidateLoginPage> {
  final _formKey = GlobalKey<FormState>();
  final CandidatesDataSourceImpl _candidatesDataSource = CandidatesDataSourceImpl();

  final _phoneController = TextEditingController();
  final _tokenController = TextEditingController();

  bool _isLoading = false;

  @override
  void dispose() {
    _phoneController.dispose();
    _tokenController.dispose();
    super.dispose();
  }

  Future<void> _authenticateCandidate() async {
    print('🚀 DEBUG: Iniciando autenticación de candidato');

    if (!_formKey.currentState!.validate()) {
      print('❌ DEBUG: Validación de formulario falló');
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      final phone = _phoneController.text.trim();
      final token = _tokenController.text.trim().toUpperCase();

      // 📍 DEBUG: Variables de entrada
      print('📱 DEBUG: Phone ingresado: "$phone"');
      print('🔑 DEBUG: Token ingresado: "$token"');
      print('📏 DEBUG: Longitud del token: ${token.length}');

      // 📍 DEBUG: Antes de la llamada al datasource
      print('🔍 DEBUG: Llamando authenticateCandidate con:');
      print('   - phoneNum: "$phone"');
      print('   - accessToken: "$token"');

      final user = await _candidatesDataSource.authenticateCandidate(
        phoneNum: phone,
        accessToken: token,
      );

      // 📍 DEBUG: Respuesta del datasource
      print('📨 DEBUG: Respuesta de authenticateCandidate:');
      print('📨 DEBUG: Tipo de respuesta: ${user.runtimeType}');

      if (user != null) {
        print('✅ DEBUG: Usuario encontrado (Map):');
        print('   - Contenido completo: $user');
        print('   - ID: ${user['id_candidate']}');
        print('   - Nombre: ${user['name']}');
        print('   - Email: ${user['email']}');
        print('   - Teléfono: ${user['phone_num']}');
        print('   - Token: ${user['access_token']}');
      } else {
        print('❌ DEBUG: Usuario es NULL - credenciales incorrectas');
      }

      if (user != null) {
        // 📍 DEBUG: Antes de guardar en SharedPreferences
        final candidateId = user['id_candidate'];
        print('💾 DEBUG: Guardando en SharedPreferences:');
        print('   - candidate_phone: "$phone"');
        print('   - candidate_token: "$token"');
        print('   - candidate_id: "$candidateId"');

        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('candidate_phone', phone);
        await prefs.setString('candidate_token', token);
        // ⭐ CRÍTICO: También guardamos el ID del candidato
        await prefs.setInt('candidate_id', candidateId ?? 0);

        // 📍 DEBUG: Verificar que se guardó correctamente
        final savedPhone = prefs.getString('candidate_phone');
        final savedToken = prefs.getString('candidate_token');
        final savedId = prefs.getInt('candidate_id');

        print('✅ DEBUG: Verificación de guardado en SharedPreferences:');
        print('   - candidate_phone guardado: "$savedPhone"');
        print('   - candidate_token guardado: "$savedToken"');
        print('   - candidate_id guardado: "$savedId"');

        if (mounted) {
          print('🧭 DEBUG: Navegando a /entrevistado');
          Navigator.pushReplacementNamed(context, '/entrevistado');
        }
      } else {
        if (mounted) {
          print('⚠️ DEBUG: Mostrando SnackBar de error - credenciales incorrectas');
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Teléfono o código incorrecto'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    } catch (e) {
      print('💥 DEBUG: Error en autenticación: ${e.toString()}');
      print('💥 DEBUG: Tipo de error: ${e.runtimeType}');

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      print('🏁 DEBUG: Finalizando autenticación (isLoading = false)');
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F1EB),
      appBar: AppBar(
        title: const Text('Acceso Candidato'),
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
              children: [
                const SizedBox(height: 40),

                // Logo/Icono
                Container(
                  width: 100,
                  height: 100,
                  decoration: BoxDecoration(
                    color: const Color(0xFF6ECCC4).withOpacity(0.1),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Icons.person,
                    size: 50,
                    color: Color(0xFF6ECCC4),
                  ),
                ),
                const SizedBox(height: 24),

                // Título
                const Text(
                  'Acceso de Candidato',
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: Colors.black87,
                  ),
                ),
                const SizedBox(height: 8),

                // Subtítulo
                Text(
                  'Ingresa tu teléfono y código de acceso',
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.grey[600],
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 40),

                // Contenedor del formulario
                Container(
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
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
                    child: Column(
                      children: [
                        // Campo teléfono
                        TextFormField(
                          controller: _phoneController,
                          keyboardType: TextInputType.phone,
                          decoration: InputDecoration(
                            labelText: 'Número de Teléfono',
                            hintText: 'Ej: +593-999-123456',
                            prefixIcon: const Icon(Icons.phone, color: Color(0xFF6ECCC4)),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                              borderSide: BorderSide(color: Colors.grey.shade300),
                            ),
                            focusedBorder: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                              borderSide: const BorderSide(color: Color(0xFF6ECCC4), width: 2),
                            ),
                            contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
                          ),
                          validator: (value) {
                            if (value == null || value.trim().isEmpty) {
                              return 'El teléfono es requerido';
                            }
                            return null;
                          },
                        ),
                        const SizedBox(height: 20),

                        // Campo código
                        TextFormField(
                          controller: _tokenController,
                          textCapitalization: TextCapitalization.characters,
                          decoration: InputDecoration(
                            labelText: 'Código de Acceso',
                            hintText: 'Ej: AB7X9M',
                            prefixIcon: const Icon(Icons.vpn_key, color: Color(0xFF6ECCC4)),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                              borderSide: BorderSide(color: Colors.grey.shade300),
                            ),
                            focusedBorder: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                              borderSide: const BorderSide(color: Color(0xFF6ECCC4), width: 2),
                            ),
                            contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
                          ),
                          validator: (value) {
                            if (value == null || value.trim().isEmpty) {
                              return 'El código es requerido';
                            }
                            if (value.trim().length != 6) {
                              return 'El código debe tener 6 caracteres';
                            }
                            return null;
                          },
                        ),
                        const SizedBox(height: 24),

                        // Botón ingresar
                        SizedBox(
                          width: double.infinity,
                          height: 48,
                          child: ElevatedButton(
                            onPressed: _isLoading ? null : _authenticateCandidate,
                            style: ElevatedButton.styleFrom(
                              backgroundColor: const Color(0xFF6ECCC4),
                              foregroundColor: Colors.white,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(12),
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
                              'INGRESAR',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w600,
                                letterSpacing: 1,
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 24),

                // Información adicional
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.blue.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: Colors.blue.withOpacity(0.3)),
                  ),
                  child: Column(
                    children: [
                      const Icon(Icons.info_outline, color: Colors.blue),
                      const SizedBox(height: 8),
                      const Text(
                        '¿No tienes credenciales?',
                        style: TextStyle(
                          fontWeight: FontWeight.w600,
                          color: Colors.blue,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Contacta al reclutador que te envió la invitación para obtener tu teléfono y código de acceso.',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.blue.shade700,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 20),

                // Botón volver
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text(
                    'Volver al inicio',
                    style: TextStyle(
                      color: Color(0xFF6ECCC4),
                      fontWeight: FontWeight.w600,
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
}