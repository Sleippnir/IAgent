# Migraciones y Seeders - Sistema de Entrevistas

## Descripción General

Este directorio contiene todas las migraciones y seeders necesarios para configurar la base de datos del sistema de entrevistas. Las migraciones están numeradas secuencialmente para garantizar el orden correcto de ejecución y evitar conflictos de dependencias.

## Orden de Ejecución

### Migraciones de Estructura (001-012)

Las migraciones deben ejecutarse en el siguiente orden estricto:

1. **001_create_rol_user_table.sql** - Tabla de roles de usuario (independiente)
2. **006_create_users_table.sql** - Tabla de usuarios (depende de rol_user)
3. **007_create_jobs_table.sql** - Tabla de trabajos (independiente)
4. **008_create_candidates_table.sql** - Tabla de candidatos (depende de users y jobs)
5. **009_create_interviews_table.sql** - Tabla de entrevistas (depende de candidates)
6. **010_create_general_questions_answers_table.sql** - Preguntas generales (independiente)
7. **011_create_technical_questions_answers_table.sql** - Preguntas técnicas (independiente)
8. **012_create_technical_questions_answers_jobs_table.sql** - Relación preguntas-trabajos (depende de jobs y technical_questions_answers)

## Dependencias entre Tablas

```
rol_user (independiente)
├── users (FK: id_rol_user)

jobs (independiente)
├── candidates (FK: id_job)
│   └── interviews (FK: id_candidate)
├── technical_questions_answers_jobs (FK: id_job)

general_questions_answers (independiente)

technical_questions_answers (independiente)
├── technical_questions_answers_jobs (FK: id_tech_question_answer)
```

## Características de Seguridad

Todas las tablas incluyen:
- **Row Level Security (RLS)** habilitado
- **Políticas de seguridad** específicas por tabla
- **Permisos granulares** para diferentes roles
- **Índices optimizados** para consultas frecuentes

## Ejecución de Migraciones

### Usando Supabase CLI
```bash
# Ejecutar todas las migraciones en orden
supabase db reset

# O ejecutar individualmente
supabase db push
```

### Usando psql directamente
```bash
# Ejecutar en orden secuencial (ajustar números según archivos existentes)
psql -d your_database -f 001_create_rol_user_table.sql
psql -d your_database -f 006_create_users_table.sql
psql -d your_database -f 007_create_jobs_table.sql
psql -d your_database -f 008_create_candidates_table.sql
psql -d your_database -f 009_create_interviews_table.sql
psql -d your_database -f 010_create_general_questions_answers_table.sql
psql -d your_database -f 011_create_technical_questions_answers_table.sql
psql -d your_database -f 012_create_technical_questions_answers_jobs_table.sql
psql -d your_database -f 013_seed_rol_user.sql
psql -d your_database -f 014_seed_users.sql
psql -d your_database -f 015_seed_jobs.sql
psql -d your_database -f 016_seed_general_questions_answers.sql
psql -d your_database -f 017_seed_technical_questions_answers.sql
psql -d your_database -f 018_seed_technical_questions_answers_jobs.sql
```

## Verificación de Integridad

Después de ejecutar todas las migraciones y seeders, verificar:

```sql
-- Verificar conteos de registros
SELECT 'rol_user' as tabla, COUNT(*) as registros FROM rol_user
UNION ALL
SELECT 'users', COUNT(*) FROM users
UNION ALL
SELECT 'jobs', COUNT(*) FROM jobs
UNION ALL
SELECT 'candidates', COUNT(*) FROM candidates
UNION ALL
SELECT 'interviews', COUNT(*) FROM interviews
UNION ALL
SELECT 'general_questions_answers', COUNT(*) FROM general_questions_answers
UNION ALL
SELECT 'technical_questions_answers', COUNT(*) FROM technical_questions_answers
UNION ALL
SELECT 'technical_questions_answers_jobs', COUNT(*) FROM technical_questions_answers_jobs;

-- Verificar integridad referencial
SELECT 
  conname as constraint_name,
  conrelid::regclass as table_name,
  confrelid::regclass as referenced_table
FROM pg_constraint 
WHERE contype = 'f'
ORDER BY conrelid::regclass::text;
```

## Rollback

Para revertir las migraciones (en orden inverso):

```sql
-- Eliminar en orden inverso de dependencias
DROP TABLE IF EXISTS technical_questions_answers_jobs CASCADE;
DROP TABLE IF EXISTS interviews CASCADE;
DROP TABLE IF EXISTS candidates CASCADE;
DROP TABLE IF EXISTS technical_questions_answers CASCADE;
DROP TABLE IF EXISTS general_questions_answers CASCADE;
DROP TABLE IF EXISTS jobs CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS rol_user CASCADE;
```

## Conteos Esperados

Después de ejecutar todos los seeders, los conteos esperados son:
- **rol_user**: 2 registros (admin, candidate)
- **users**: 2 registros (1 admin, 1 candidate)
- **jobs**: 31 registros
- **candidates**: 0 registros (tabla vacía inicialmente)
- **interviews**: 0 registros (tabla vacía inicialmente)
- **general_questions_answers**: 28 registros
- **technical_questions_answers**: 3205 registros
- **technical_questions_answers_jobs**: 3205 registros

## Notas Importantes

1. **Orden Crítico**: Las migraciones DEBEN ejecutarse en el orden especificado
2. **Datos de Producción**: Los seeders contienen datos reales de la base de datos existente
3. **Performance**: Los seeders incluyen optimizaciones para grandes volúmenes de datos
4. **Seguridad**: Todas las tablas tienen RLS habilitado por defecto
5. **Mantenimiento**: Las secuencias se actualizan automáticamente después de los seeders
6. **Triggers**: Se deshabilitan temporalmente durante los seeders para mejor rendimiento

## Estructura de Archivos

```
migrations/
├── 001_create_rol_user_table.sql
├── 006_create_users_table.sql
├── 007_create_jobs_table.sql
├── 008_create_candidates_table.sql
├── 009_create_interviews_table.sql
├── 010_create_general_questions_answers_table.sql
├── 011_create_technical_questions_answers_table.sql
├── 012_create_technical_questions_answers_jobs_table.sql
└── README.md (este archivo)
```

## Contacto

Para preguntas sobre las migraciones, contactar al equipo de desarrollo.