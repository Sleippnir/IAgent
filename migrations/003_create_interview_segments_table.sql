-- Migración: Crear tabla para almacenar segmentos de transcripciones
-- Fecha: $(date)
-- Descripción: Tabla para almacenar segmentos específicos de las transcripciones (preguntas, respuestas, pausas)

CREATE TABLE IF NOT EXISTS public.interview_segments (
    id_segment SERIAL PRIMARY KEY,
    id_transcript INTEGER NOT NULL,
    id_interview INTEGER NOT NULL,
    segment_type VARCHAR(20) NOT NULL CHECK (segment_type IN ('question', 'answer', 'pause', 'interruption', 'other')),
    speaker VARCHAR(20) NOT NULL CHECK (speaker IN ('interviewer', 'candidate', 'system', 'unknown')),
    segment_text TEXT NOT NULL,
    start_time_seconds DECIMAL(10,3) NOT NULL,
    end_time_seconds DECIMAL(10,3) NOT NULL,
    duration_seconds DECIMAL(10,3) GENERATED ALWAYS AS (end_time_seconds - start_time_seconds) STORED,
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),
    word_count INTEGER,
    sentiment_score DECIMAL(3,2) CHECK (sentiment_score >= -1 AND sentiment_score <= 1),
    emotion_detected VARCHAR(20),
    keywords TEXT[],
    is_important BOOLEAN DEFAULT FALSE,
    notes TEXT,
    metadata JSONB,
    timestamp_created TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    timestamp_updated TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    CONSTRAINT fk_segment_transcript 
        FOREIGN KEY (id_transcript) 
        REFERENCES public.interview_transcripts(id_transcript) 
        ON DELETE CASCADE,
    
    CONSTRAINT fk_segment_interview 
        FOREIGN KEY (id_interview) 
        REFERENCES public.interviews(id_interview) 
        ON DELETE CASCADE,
        
    -- Constraint para validar que end_time > start_time
    CONSTRAINT chk_segment_time_order 
        CHECK (end_time_seconds > start_time_seconds)
);

-- Crear índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_interview_segments_transcript_id ON public.interview_segments(id_transcript);
CREATE INDEX IF NOT EXISTS idx_interview_segments_interview_id ON public.interview_segments(id_interview);
CREATE INDEX IF NOT EXISTS idx_interview_segments_type ON public.interview_segments(segment_type);
CREATE INDEX IF NOT EXISTS idx_interview_segments_speaker ON public.interview_segments(speaker);
CREATE INDEX IF NOT EXISTS idx_interview_segments_start_time ON public.interview_segments(start_time_seconds);
CREATE INDEX IF NOT EXISTS idx_interview_segments_important ON public.interview_segments(is_important);
CREATE INDEX IF NOT EXISTS idx_interview_segments_created ON public.interview_segments(timestamp_created);

-- Índice de texto completo para búsquedas en el contenido del segmento
CREATE INDEX IF NOT EXISTS idx_interview_segments_text_search 
    ON public.interview_segments 
    USING gin(to_tsvector('spanish', segment_text));

-- Índice para búsquedas por keywords
CREATE INDEX IF NOT EXISTS idx_interview_segments_keywords 
    ON public.interview_segments 
    USING gin(keywords);

-- Trigger para actualizar timestamp_updated automáticamente
CREATE TRIGGER trigger_update_interview_segments_timestamp
    BEFORE UPDATE ON public.interview_segments
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp_updated();

-- Comentarios para documentación
COMMENT ON TABLE public.interview_segments IS 'Almacena segmentos específicos de las transcripciones de entrevistas';
COMMENT ON COLUMN public.interview_segments.id_segment IS 'Identificador único del segmento';
COMMENT ON COLUMN public.interview_segments.id_transcript IS 'Referencia a la transcripción';
COMMENT ON COLUMN public.interview_segments.id_interview IS 'Referencia a la entrevista';
COMMENT ON COLUMN public.interview_segments.segment_type IS 'Tipo de segmento: question, answer, pause, interruption, other';
COMMENT ON COLUMN public.interview_segments.speaker IS 'Quién habla: interviewer, candidate, system, unknown';
COMMENT ON COLUMN public.interview_segments.segment_text IS 'Texto del segmento';
COMMENT ON COLUMN public.interview_segments.start_time_seconds IS 'Tiempo de inicio del segmento en segundos';
COMMENT ON COLUMN public.interview_segments.end_time_seconds IS 'Tiempo de fin del segmento en segundos';
COMMENT ON COLUMN public.interview_segments.duration_seconds IS 'Duración calculada del segmento';
COMMENT ON COLUMN public.interview_segments.sentiment_score IS 'Puntuación de sentimiento (-1 a 1)';
COMMENT ON COLUMN public.interview_segments.emotion_detected IS 'Emoción detectada en el segmento';
COMMENT ON COLUMN public.interview_segments.keywords IS 'Palabras clave extraídas del segmento';
COMMENT ON COLUMN public.interview_segments.is_important IS 'Marca si el segmento es importante para análisis';
COMMENT ON COLUMN public.interview_segments.metadata IS 'Metadatos adicionales en formato JSON';