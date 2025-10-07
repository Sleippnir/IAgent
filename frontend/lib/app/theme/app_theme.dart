import 'package:flutter/material.dart';

class AppTheme {
  // Colores basados en la referencia
  static const Color primaryTurquoise = Color(0xFF6ECCC4);
  static const Color lightTurquoise = Color(0xFF7DD3CC);
  static const Color backgroundBeige = Color(0xFFF5F1EB);
  static const Color darkTurquoise = Color(0xFF5BB5AD);
  static const Color textDark = Color(0xFF2C3E50);
  static const Color textMedium = Color(0xFF5D6D7E);
  static const Color chipBackground = Color(0xFFE8E8E8);

  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.light(
        primary: primaryTurquoise,
        secondary: lightTurquoise,
        surface: Colors.white,
        onPrimary: Colors.white,
        onSecondary: Colors.white,
        onSurface: textDark,
      ),
      scaffoldBackgroundColor: backgroundBeige,

      // AppBar Theme
      appBarTheme: const AppBarTheme(
        backgroundColor: primaryTurquoise,
        foregroundColor: Colors.white,
        elevation: 0,
        centerTitle: true,
      ),

      // Card Theme - CORREGIDO
      cardTheme: CardThemeData(
        color: Colors.white,
        elevation: 2,
        shadowColor: Colors.black12,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
      ),

      // ElevatedButton Theme
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryTurquoise,
          foregroundColor: Colors.white,
          elevation: 2,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
    );
  }
}