-- Migración: Crear tabla para almacenar grabaciones de entrevistas
-- Fecha: $(date)
-- Descripción: Tabla para almacenar grabaciones de audio/video de las entrevistas

CREATE TABLE IF NOT EXISTS public.interview_recordings (
    id_recording SERIAL PRIMARY KEY,
    id_interview INTEGER NOT NULL,
    recording_type VARCHAR(20) NOT NULL CHECK (recording_type IN ('audio', 'video', 'screen')),
    file_path TEXT NOT NULL,
    file_size BIGINT,
    duration_seconds INTEGER,
    format VARCHAR(10) NOT NULL,
    quality VARCHAR(20) DEFAULT 'standard',
    is_processed BOOLEAN DEFAULT FALSE,
    processing_status VARCHAR(20) DEFAULT 'pending' CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
    metadata JSONB,
    timestamp_created TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    timestamp_updated TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraint
    CONSTRAINT fk_interview_recording 
        FOREIGN KEY (id_interview) 
        REFERENCES public.interviews(id_interview) 
        ON DELETE CASCADE
);

-- Crear índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_interview_recordings_interview_id ON public.interview_recordings(id_interview);
CREATE INDEX IF NOT EXISTS idx_interview_recordings_type ON public.interview_recordings(recording_type);
CREATE INDEX IF NOT EXISTS idx_interview_recordings_status ON public.interview_recordings(processing_status);
CREATE INDEX IF NOT EXISTS idx_interview_recordings_created ON public.interview_recordings(timestamp_created);

-- Trigger para actualizar timestamp_updated automáticamente
CREATE OR REPLACE FUNCTION update_timestamp_updated()
RETURNS TRIGGER AS $$
BEGIN
    NEW.timestamp_updated = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_interview_recordings_timestamp
    BEFORE UPDATE ON public.interview_recordings
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp_updated();

-- Comentarios para documentación
COMMENT ON TABLE public.interview_recordings IS 'Almacena las grabaciones de audio/video de las entrevistas';
COMMENT ON COLUMN public.interview_recordings.id_recording IS 'Identificador único de la grabación';
COMMENT ON COLUMN public.interview_recordings.id_interview IS 'Referencia a la entrevista';
COMMENT ON COLUMN public.interview_recordings.recording_type IS 'Tipo de grabación: audio, video o screen';
COMMENT ON COLUMN public.interview_recordings.file_path IS 'Ruta del archivo de grabación';
COMMENT ON COLUMN public.interview_recordings.duration_seconds IS 'Duración de la grabación en segundos';
COMMENT ON COLUMN public.interview_recordings.processing_status IS 'Estado del procesamiento de la grabación';
COMMENT ON COLUMN public.interview_recordings.metadata IS 'Metadatos adicionales en formato JSON';