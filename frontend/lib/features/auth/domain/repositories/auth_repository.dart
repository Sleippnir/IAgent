import '../entities/user.dart';
import '../../../../core/utils/enums.dart';

abstract class AuthRepository {
  Future<User> login({
    required String email,
    required String password,
  });

  Future<User> register({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
    required UserType userType,
  });

  Future<void> logout();
}