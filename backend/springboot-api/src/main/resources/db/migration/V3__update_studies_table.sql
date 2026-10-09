-- Modificar tabla studies para incluir fecha de estudio y modalidad
-- También hacemos image_path opcional temporalmente hasta implementar la subida de imágenes

ALTER TABLE studies ADD COLUMN IF NOT EXISTS study_date TIMESTAMP;
ALTER TABLE studies ADD COLUMN IF NOT EXISTS modality VARCHAR(50);
ALTER TABLE studies ALTER COLUMN image_path DROP NOT NULL;
