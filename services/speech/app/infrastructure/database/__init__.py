"""Adaptadores de base de datos para el servicio de speech.

Contiene las implementaciones concretas para la conexión
y operaciones con Supabase.
"""

from .supabase_connection import SupabaseConnection, get_supabase_client, initialize_supabase

__all__ = ['SupabaseConnection', 'get_supabase_client', 'initialize_supabase']