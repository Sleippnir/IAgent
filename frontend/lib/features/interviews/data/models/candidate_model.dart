class CandidateModel {
  final int? idCandidate;
  final String name;
  final String lastName;
  final String phoneNum;
  final String email;
  final int age;
  final String linkedinUrl;
  final String? resume; // Puede ser null si no se sube archivo
  final String? accessToken; // Token para login
  final DateTime? timestampCreated;

  CandidateModel({
    this.idCandidate,
    required this.name,
    required this.lastName,
    required this.phoneNum,
    required this.email,
    required this.age,
    required this.linkedinUrl,
    this.resume,
    this.accessToken,
    this.timestampCreated,
  });

  factory CandidateModel.fromSupabase(Map<String, dynamic> json) {
    return CandidateModel(
      idCandidate: json['id_candidate'],
      name: json['name'] ?? '',
      lastName: json['last_name'] ?? '',
      phoneNum: json['phone_num'] ?? '',
      email: json['email'] ?? '',
      age: json['age'] ?? 0,
      linkedinUrl: json['linkedin_url'] ?? '',
      resume: json['resume'],
      accessToken: json['access_token'],
      timestampCreated: json['timestamp_created'] != null
          ? DateTime.parse(json['timestamp_created'])
          : null,
    );
  }

  Map<String, dynamic> toSupabase() {
    return {
      'name': name,
      'last_name': lastName,
      'phone_num': phoneNum,
      'email': email,
      'age': age,
      'linkedin_url': linkedinUrl,
      'resume': resume,
      'access_token': accessToken,
      'timestamp_created': timestampCreated?.toIso8601String() ?? DateTime.now().toIso8601String(),
    };
  }

  String get fullName => '$name $lastName';

  // Generar token aleatorio de 6 caracteres
  static String generateAccessToken() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    final random = DateTime.now().millisecondsSinceEpoch;
    String token = '';

    for (int i = 0; i < 6; i++) {
      token += chars[(random + i) % chars.length];
    }

    return token;
  }
}