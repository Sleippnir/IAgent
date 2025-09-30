-- Migration: 005_create_rol_user_table
-- Description: Create rol_user table for user roles
-- Author: System Migration
-- Date: 2025-01-27

-- Create rol_user table
CREATE TABLE IF NOT EXISTS public.rol_user (
    id_rol SERIAL PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    timestamp_created TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add comments for documentation
COMMENT ON TABLE public.rol_user IS 'Table storing user roles for the interview system';
COMMENT ON COLUMN public.rol_user.id_rol IS 'Primary key for role identification';
COMMENT ON COLUMN public.rol_user.role_name IS 'Name of the role (admin, candidate, etc.)';
COMMENT ON COLUMN public.rol_user.timestamp_created IS 'Timestamp when the role was created';

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_rol_user_role_name ON public.rol_user(role_name);
CREATE INDEX IF NOT EXISTS idx_rol_user_timestamp ON public.rol_user(timestamp_created);

-- Enable Row Level Security (RLS)
ALTER TABLE public.rol_user ENABLE ROW LEVEL SECURITY;

-- Create policy for admin access
CREATE POLICY "Admin can manage roles" ON public.rol_user
    FOR ALL USING (auth.jwt() ->> 'role' = 'admin');

-- Create policy for read access
CREATE POLICY "Users can view roles" ON public.rol_user
    FOR SELECT USING (true);

-- Grant permissions
GRANT SELECT ON public.rol_user TO anon, authenticated;
GRANT ALL ON public.rol_user TO service_role;
GRANT USAGE, SELECT ON SEQUENCE public.rol_user_id_rol_seq TO anon, authenticated, service_role;