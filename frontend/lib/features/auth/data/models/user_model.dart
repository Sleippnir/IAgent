import '../../domain/entities/user.dart';
import '../../../../core/utils/enums.dart';

class UserModel extends User {
  const UserModel({
    required super.idUser,
    required super.idRol,
    required super.nameUser,
    required super.emailUser,
    required super.roleName,
    required super.timestampCreated,
  });

  factory UserModel.fromSupabase(Map<String, dynamic> userData, String roleName) {
    return UserModel(
      idUser: userData['id_user'],
      idRol: userData['id_rol'],
      nameUser: userData['name_user'],
      emailUser: userData['email_user'],
      roleName: roleName,
      timestampCreated: DateTime.parse(userData['timestamp_created']),
    );
  }

  // Método legacy para mantener compatibilidad
  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      idUser: json['id_user'] ?? 0,
      idRol: json['id_rol'] ?? 0,
      nameUser: json['name_user'] ?? '',
      emailUser: json['email_user'] ?? '',
      roleName: json['role_name'] ?? '',
      timestampCreated: DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id_user': idUser,
      'id_rol': idRol,
      'name_user': nameUser,
      'email_user': emailUser,
      'role_name': roleName,
      'timestamp_created': timestampCreated.toIso8601String(),
    };
  }
}