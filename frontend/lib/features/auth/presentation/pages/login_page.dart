import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import '../../../interviews/presentation/pages/candidate_login_page.dart';
import 'login_real_page.dart';

class LoginPage extends StatelessWidget {
  const LoginPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Header
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(32),
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.primary,
                  borderRadius: BorderRadius.circular(24),
                ),
                child: Column(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: const Icon(
                        Icons.psychology,
                        size: 48,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      'Entrevistador Virtual',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Potenciado por IA',
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.9),
                        fontSize: 16,
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 40),

              // Test de conexión Supabase
              // Container(
              //   padding: const EdgeInsets.all(16),
              //   decoration: BoxDecoration(
              //     color: Colors.white,
              //     borderRadius: BorderRadius.circular(12),
              //     border: Border.all(color: Colors.orange),
              //   ),
              //   // child: Column(
              //   //   children: [
              //   //     const Text(
              //   //       'Test de Conexión Supabase',
              //   //       style: TextStyle(fontWeight: FontWeight.bold),
              //   //     ),
              //   //     const SizedBox(height: 8),
              //   //     ElevatedButton(
              //   //       onPressed: () => _testSupabaseConnection(context),
              //   //       child: const Text('Probar Conexión'),
              //   //     ),
              //   //   ],
              //   // ),
              // ),

              const SizedBox(height: 20),

              // Botones de acceso
              Container(
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 20,
                      offset: const Offset(0, 10),
                    ),
                  ],
                ),
                child: Column(
                  children: [
                    const Text(
                      'Acceso Demo',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'Selecciona tu tipo de usuario:',
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey,
                      ),
                    ),
                    const SizedBox(height: 24),

                    _buildUserTypeButton(
                      context,
                      'Entrevistado',
                      Icons.person,
                          () => Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => const LoginRealPage(userTypeIntent: 'entrevistado'),
                        ),
                      ),
                    ),

                    _buildUserTypeButton(
                      context,
                      'Administrador/Reclutador',
                      Icons.admin_panel_settings,
                          () => Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => const LoginRealPage(userTypeIntent: 'admin'),
                        ),
                      ),
                    ),
                    const SizedBox(height: 12),

                    // Botón actualizado para candidatos con token
                    _buildCandidateTokenButton(context),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // FUNCIÓN MOVIDA DENTRO DE LA CLASE
  Future<void> _testSupabaseConnection(BuildContext context) async {
    try {
      final client = Supabase.instance.client;
      await client.from('prompts').select('count').limit(1);

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('✅ Conexión a Supabase exitosa!'),
          backgroundColor: Colors.green,
        ),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('❌ Error de conexión: ${e.toString()}'),
          backgroundColor: Colors.red,
          duration: const Duration(seconds: 5),
        ),
      );
    }
  }

  Widget _buildUserTypeButton(
      BuildContext context,
      String text,
      IconData icon,
      VoidCallback onPressed,
      ) {
    return SizedBox(
      width: double.infinity,
      height: 50,
      child: ElevatedButton.icon(
        onPressed: onPressed,
        icon: Icon(icon),
        label: Text(text),
        style: ElevatedButton.styleFrom(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
    );
  }

  // Nuevo botón especializado para candidatos con token
  Widget _buildCandidateTokenButton(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      height: 50,
      child: OutlinedButton.icon(
        onPressed: () => Navigator.push(
          context,
          MaterialPageRoute(builder: (context) => const CandidateLoginPage()),
        ),
        icon: const Icon(Icons.vpn_key),
        label: const Text('Acceso con Código de Candidato'),
        style: OutlinedButton.styleFrom(
          foregroundColor: const Color(0xFF6ECCC4),
          side: const BorderSide(color: Color(0xFF6ECCC4), width: 2),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
    );
  }
}