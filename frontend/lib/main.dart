import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'core/config/supabase_config.dart';
import 'core/dependency_injection/injection.dart';
import 'features/auth/presentation/pages/login_page.dart';
import 'features/auth/presentation/pages/register_page.dart';
import 'features/dashboard_entrevistado/presentation/pages/entrevistado_page.dart';
import 'features/dashboard_admin/presentation/pages/admin_page.dart';
import 'features/interviews/presentation/pages/candidate_login_page.dart';
import 'features/interviews/presentation/bloc/interview_bloc.dart';
import 'features/interviews/data/datasources/candidates_datasource_impl.dart';
import 'app/theme/app_theme.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Inicializar Supabase
  await Supabase.initialize(
    url: SupabaseConfig.url,
    anonKey: SupabaseConfig.anonKey,
  );

  setupDependencies();
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => InterviewBloc(
        candidatesDataSource: CandidatesDataSourceImpl(),
      ),
      child: MaterialApp(
        title: 'Entrevistador Virtual - Supabase',
        theme: AppTheme.lightTheme,
        debugShowCheckedModeBanner: false,
        initialRoute: '/',
        routes: {
          '/': (context) => const LoginPage(),
          '/register': (context) => const RegisterPage(),
          '/entrevistado': (context) => const EntrevistadoPage(),
          '/admin': (context) => const AdminPage(),
          '/candidate-login': (context) => const CandidateLoginPage(),
        },
      ),
    );
  }
}