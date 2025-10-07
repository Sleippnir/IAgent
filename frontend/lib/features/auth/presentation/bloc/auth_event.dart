import 'package:equatable/equatable.dart';
import '../../../../core/utils/enums.dart';

abstract class AuthEvent extends Equatable {
  @override
  List<Object> get props => [];
}

class LoginRequested extends AuthEvent {
  final String email;
  final String password;

  LoginRequested({
    required this.email,
    required this.password,
  });

  @override
  List<Object> get props => [email, password];
}

class RegisterRequested extends AuthEvent {
  final String email;
  final String password;
  final String firstName;
  final String lastName;
  final UserType userType;

  RegisterRequested({
    required this.email,
    required this.password,
    required this.firstName,
    required this.lastName,
    required this.userType,
  });

  @override
  List<Object> get props => [email, password, firstName, lastName, userType];
}