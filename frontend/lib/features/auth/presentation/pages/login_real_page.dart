import 'package:flutter/material.dart';
import '../../data/datasources/auth_datasource_impl.dart';
import '../../../../shared/widgets/custom_button.dart';
import '../../../../shared/widgets/custom_textfield.dart';

class LoginRealPage extends StatefulWidget {
  final String userTypeIntent;

  const LoginRealPage({super.key, required this.userTypeIntent});

  @override
  State<LoginRealPage> createState() => _LoginRealPageState();
}

class _LoginRealPageState extends State<LoginRealPage> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(
        title: Text(_getTitle()),
        backgroundColor: Theme.of(context).colorScheme.primary,
        foregroundColor: Colors.white,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            children: [
              const SizedBox(height: 40),

              // Header
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.primary,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Column(
                  children: [
                    Icon(
                      _getIcon(),
                      size: 48,
                      color: Colors.white,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      _getTitle(),
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Ingresa tus credenciales para continuar',
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.9),
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 32),

              // Form
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
                child: Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      CustomTextField(
                        label: 'Email',
                        controller: _emailController,
                        validator: (value) {
                          if (value?.isEmpty ?? true) {
                            return 'El email es requerido';
                          }
                          return null;
                        },
                      ),
                      const SizedBox(height: 16),

                      CustomTextField(
                        label: 'Contraseña',
                        controller: _passwordController,
                        obscureText: true,
                        validator: (value) {
                          if (value?.isEmpty ?? true) {
                            return 'La contraseña es requerida';
                          }
                          return null;
                        },
                      ),
                      const SizedBox(height: 24),

                      CustomButton(
                        text: 'Iniciar Sesión',
                        isLoading: _isLoading,
                        onPressed: _handleLogin,
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _getTitle() {
    return widget.userTypeIntent == 'entrevistado'
        ? 'Acceso Entrevistado'
        : 'Acceso Administrador';
  }

  IconData _getIcon() {
    return widget.userTypeIntent == 'entrevistado'
        ? Icons.person
        : Icons.admin_panel_settings;
  }

  Future<void> _handleLogin() async {
    if (_formKey.currentState?.validate() ?? false) {
      setState(() {
        _isLoading = true;
      });

      try {
        final authDataSource = AuthDataSourceImpl();
        final user = await authDataSource.login(
          email: _emailController.text.trim(),
          password: _passwordController.text.trim(),
        );

        // Verificar que el rol coincida con la intención
        if (_validateRole(user.roleName)) {
          _navigateToCorrectDashboard();
        } else {
          throw Exception('Tu cuenta no tiene permisos para este tipo de acceso');
        }

      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(e.toString().replaceAll('Exception: ', '')),
            backgroundColor: Colors.red,
          ),
        );
      } finally {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  bool _validateRole(String roleName) {
    if (widget.userTypeIntent == 'entrevistado') {
      return roleName.toLowerCase().contains('candidate') ||
          roleName.toLowerCase().contains('entrevistado');
    } else {
      return roleName.toLowerCase().contains('admin') ||
          roleName.toLowerCase().contains('recruiter') ||
          roleName.toLowerCase().contains('reclutador');
    }
  }

  void _navigateToCorrectDashboard() {
    if (widget.userTypeIntent == 'entrevistado') {
      Navigator.pushReplacementNamed(context, '/entrevistado');
    } else {
      Navigator.pushReplacementNamed(context, '/admin');
    }
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }
}