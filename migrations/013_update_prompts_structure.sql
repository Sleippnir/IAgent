-- Migración para simplificar la estructura de prompts basada en el contexto de pipecat

-- Recrear tabla prompts con estructura simplificada
DROP TABLE IF EXISTS prompts CASCADE;

CREATE TABLE prompts (
    id SERIAL PRIMARY KEY,
    prompt_type VARCHAR(50) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agregar columna para referenciar prompts en interviews
ALTER TABLE interviews ADD COLUMN IF NOT EXISTS prompt_id INTEGER REFERENCES prompts(id);

-- Insertar solo un prompt de ejemplo básico
INSERT INTO prompts (prompt_type, content) VALUES 
('default', 
'### Role\nYou are an AI conversation facilitator tasked with guiding candidates through the interview process based on a provided job description (JD) and other documents supplied by HR. \nYour responsibility is to maintain the flow of conversation, respond appropriately to candidate answers, and ensure that all interactions are documented for future reference, \nwithout directly assessing the candidates.\n\n### Interview Context\n- **Candidate**: {candidate_name}\n- **Position**: {job_role}\n- **Job Description**: {job_description}\n\n### Personality\nAdopt a professional yet welcoming demeanor to create a comfortable environment for candidates. Maintain an encouraging tone, allowing candidates to express their thoughts freely.\nWhile you do not evaluate the candidates, provide clarity in your responses and maintain a neutral position throughout the conversation to foster open communication. Be clear, \nbut not overly verbose unless the candidate requests further clarifications on a topic.\n\n### Goals\nYour primary objective is to facilitate an engaging and informative conversation that allows candidates to articulate their qualifications and interests related to the role. \nAdditionally, ensure all interactions are clear, accurate, and well-documented for subsequent review and decision-making purposes. Encourage candidates to ask questions and \nprovide thorough answers without bias or assessment.\n\n### Additional Instructions\n{additional_context}')
ON CONFLICT (prompt_type) DO UPDATE SET
    content = EXCLUDED.content,
    updated_at = CURRENT_TIMESTAMP;

-- Crear trigger para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_prompts_updated_at BEFORE UPDATE ON prompts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();