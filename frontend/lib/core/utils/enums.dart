enum UserType {
  entrevistado('entrevistado'),
  administrador('administrador'),
  reclutador('reclutador');

  const UserType(this.value);
  final String value;

  static UserType fromString(String value) {
    return UserType.values.firstWhere(
          (e) => e.value == value,
      orElse: () => UserType.entrevistado,
    );
  }

  String get displayName {
    switch (this) {
      case UserType.entrevistado:
        return 'Entrevistado';
      case UserType.administrador:
        return 'Administrador';
      case UserType.reclutador:
        return 'Reclutador';
    }
  }
}