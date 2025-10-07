import '../models/user_model.dart';
import '../../../../core/utils/enums.dart';

abstract class AuthDataSource {
  Future<UserModel> login({
    required String email,
    required String password,
  });

  Future<UserModel> register({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
    required UserType userType,
  });

  Future<void> logout();
}