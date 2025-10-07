import 'package:supabase_flutter/supabase_flutter.dart';
import '../models/user_model.dart';
import '../../../../core/utils/enums.dart';
import 'auth_datasource.dart';

class AuthDataSourceImpl implements AuthDataSource {
  final SupabaseClient _supabase = Supabase.instance.client;

  @override
  Future<UserModel> login({
    required String email,
    required String password,
  }) async {
    try {
      // 1. Buscar usuario por email y password
      final userResponse = await _supabase
          .from('users')
          .select('*')
          .eq('email_user', email)
          .eq('password', password)
          .single();

      // 2. Obtener rol del usuario
      final roleResponse = await _supabase
          .from('rol_user')
          .select('role_name')
          .eq('id_rol', userResponse['id_rol'])
          .single();

      // 3. Crear UserModel con datos completos
      return UserModel.fromSupabase(
        userResponse,
        roleResponse['role_name'],
      );

    } catch (e) {
      if (e.toString().contains('No rows found')) {
        throw Exception('Credenciales incorrectas');
      }
      throw Exception('Error de conexión: ${e.toString()}');
    }
  }

  @override
  Future<UserModel> register({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
    required UserType userType,
  }) async {
    throw UnimplementedError('Registro aún no implementado');
  }

  @override
  Future<void> logout() async {
    // No hay tokens que limpiar por ahora
  }
}