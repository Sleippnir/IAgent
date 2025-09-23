-- Migration: 006_create_users_table
-- Description: Create users table for system users
-- Author: System Migration
-- Date: 2025-01-27
-- Dependencies: 005_create_rol_user_table.sql

-- Create users table
CREATE TABLE IF NOT EXISTS public.users (
    id_user SERIAL PRIMARY KEY,
    id_rol INTEGER NOT NULL,
    name_user VARCHAR(100) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email_user VARCHAR(255) NOT NULL UNIQUE,
    timestamp_created TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraint
    CONSTRAINT fk_users_rol_user 
        FOREIGN KEY (id_rol) 
        REFERENCES public.rol_user(id_rol) 
        ON DELETE RESTRICT 
        ON UPDATE CASCADE
);

-- Add comments for documentation
COMMENT ON TABLE public.users IS 'Table storing system users for the interview platform';
COMMENT ON COLUMN public.users.id_user IS 'Primary key for user identification';
COMMENT ON COLUMN public.users.id_rol IS 'Foreign key referencing rol_user table';
COMMENT ON COLUMN public.users.name_user IS 'Full name of the user';
COMMENT ON COLUMN public.users.password IS 'Encrypted password for user authentication';
COMMENT ON COLUMN public.users.email_user IS 'Unique email address for user identification';
COMMENT ON COLUMN public.users.timestamp_created IS 'Timestamp when the user was created';

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email_user);
CREATE INDEX IF NOT EXISTS idx_users_rol ON public.users(id_rol);
CREATE INDEX IF NOT EXISTS idx_users_timestamp ON public.users(timestamp_created);
CREATE INDEX IF NOT EXISTS idx_users_name ON public.users(name_user);

-- Enable Row Level Security (RLS)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;

-- Create policy for users to access their own data
CREATE POLICY "Users can view own profile" ON public.users
    FOR SELECT USING (auth.jwt() ->> 'user_id'::text = id_user::text);

-- Create policy for admin access
CREATE POLICY "Admin can manage users" ON public.users
    FOR ALL USING (auth.jwt() ->> 'role' = 'admin');

-- Create policy for user registration
CREATE POLICY "Allow user registration" ON public.users
    FOR INSERT WITH CHECK (true);

-- Grant permissions
GRANT SELECT ON public.users TO anon, authenticated;
GRANT INSERT ON public.users TO anon;
GRANT ALL ON public.users TO service_role;
GRANT USAGE, SELECT ON SEQUENCE public.users_id_user_seq TO anon, authenticated, service_role;