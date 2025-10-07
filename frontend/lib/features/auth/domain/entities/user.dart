import 'package:equatable/equatable.dart';

class User extends Equatable {
  final int idUser;
  final int idRol;
  final String nameUser;
  final String emailUser;
  final String roleName;
  final DateTime timestampCreated;

  const User({
    required this.idUser,
    required this.idRol,
    required this.nameUser,
    required this.emailUser,
    required this.roleName,
    required this.timestampCreated,
  });

  @override
  List<Object> get props => [idUser, idRol, nameUser, emailUser, roleName, timestampCreated];
}