import '../entities/user.dart';
import '../repositories/auth_repository.dart';
import '../../../../core/utils/enums.dart';

class RegisterUser {
  final AuthRepository repository;

  RegisterUser(this.repository);

  Future<User> call({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
    required UserType userType,
  }) async {
    return await repository.register(
      email: email,
      password: password,
      firstName: firstName,
      lastName: lastName,
      userType: userType,
    );
  }
}