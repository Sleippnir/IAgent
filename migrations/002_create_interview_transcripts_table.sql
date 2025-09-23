-- Migración: Crear tabla para almacenar transcripciones de entrevistas
-- Fecha: $(date)
-- Descripción: Tabla para almacenar transcripciones de texto de las grabaciones de entrevistas

CREATE TABLE IF NOT EXISTS public.interview_transcripts (
    id_transcript SERIAL PRIMARY KEY,
    id_recording INTEGER NOT NULL,
    id_interview INTEGER NOT NULL,
    transcript_text TEXT NOT NULL,
    language VARCHAR(10) DEFAULT 'es',
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    word_count INTEGER,
    processing_engine VARCHAR(50) DEFAULT 'whisper',
    processing_time_seconds INTEGER,
    is_reviewed BOOLEAN DEFAULT FALSE,
    reviewed_by INTEGER,
    review_notes TEXT,
    metadata JSONB,
    timestamp_created TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    timestamp_updated TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    CONSTRAINT fk_transcript_recording 
        FOREIGN KEY (id_recording) 
        REFERENCES public.interview_recordings(id_recording) 
        ON DELETE CASCADE,
    
    CONSTRAINT fk_transcript_interview 
        FOREIGN KEY (id_interview) 
        REFERENCES public.interviews(id_interview) 
        ON DELETE CASCADE,
        
    CONSTRAINT fk_transcript_reviewer 
        FOREIGN KEY (reviewed_by) 
        REFERENCES public.users(id_user) 
        ON DELETE SET NULL
);

-- Crear índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_interview_transcripts_recording_id ON public.interview_transcripts(id_recording);
CREATE INDEX IF NOT EXISTS idx_interview_transcripts_interview_id ON public.interview_transcripts(id_interview);
CREATE INDEX IF NOT EXISTS idx_interview_transcripts_language ON public.interview_transcripts(language);
CREATE INDEX IF NOT EXISTS idx_interview_transcripts_reviewed ON public.interview_transcripts(is_reviewed);
CREATE INDEX IF NOT EXISTS idx_interview_transcripts_created ON public.interview_transcripts(timestamp_created);

-- Índice de texto completo para búsquedas en el contenido de la transcripción
CREATE INDEX IF NOT EXISTS idx_interview_transcripts_text_search 
    ON public.interview_transcripts 
    USING gin(to_tsvector('spanish', transcript_text));

-- Trigger para actualizar timestamp_updated automáticamente
CREATE TRIGGER trigger_update_interview_transcripts_timestamp
    BEFORE UPDATE ON public.interview_transcripts
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp_updated();

-- Comentarios para documentación
COMMENT ON TABLE public.interview_transcripts IS 'Almacena las transcripciones de texto de las grabaciones de entrevistas';
COMMENT ON COLUMN public.interview_transcripts.id_transcript IS 'Identificador único de la transcripción';
COMMENT ON COLUMN public.interview_transcripts.id_recording IS 'Referencia a la grabación';
COMMENT ON COLUMN public.interview_transcripts.id_interview IS 'Referencia a la entrevista';
COMMENT ON COLUMN public.interview_transcripts.transcript_text IS 'Texto completo de la transcripción';
COMMENT ON COLUMN public.interview_transcripts.confidence_score IS 'Puntuación de confianza de la transcripción (0-1)';
COMMENT ON COLUMN public.interview_transcripts.processing_engine IS 'Motor de procesamiento utilizado (whisper, etc.)';
COMMENT ON COLUMN public.interview_transcripts.is_reviewed IS 'Indica si la transcripción ha sido revisada manualmente';
COMMENT ON COLUMN public.interview_transcripts.reviewed_by IS 'Usuario que revisó la transcripción';
COMMENT ON COLUMN public.interview_transcripts.metadata IS 'Metadatos adicionales en formato JSON';