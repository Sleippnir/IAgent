import '../../domain/entities/user.dart';
import '../../domain/repositories/auth_repository.dart';
import '../datasources/auth_datasource.dart';
import '../../../../core/utils/enums.dart';

class AuthRepositoryImpl implements AuthRepository {
  final AuthDataSource dataSource;

  AuthRepositoryImpl(this.dataSource);

  @override
  Future<User> login({
    required String email,
    required String password,
  }) async {
    return await dataSource.login(
      email: email,
      password: password,
    );
  }

  @override
  Future<User> register({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
    required UserType userType,
  }) async {
    return await dataSource.register(
      email: email,
      password: password,
      firstName: firstName,
      lastName: lastName,
      userType: userType,
    );
  }

  @override
  Future<void> logout() async {
    return await dataSource.logout();
  }
}