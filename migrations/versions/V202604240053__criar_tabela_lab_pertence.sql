ALTER TYPE tipo_usuario ADD VALUE 'SIND';

ALTER TABLE usuario ADD COLUMN data_nascimento DATE;

CREATE TABLE "lab_pertence"(
    "id" uuid PRIMARY KEY,
    "usuario_id" uuid NOT NULL,
    "laboratorio_id" uuid NOT NULL, 
    CONSTRAINT fk_usuario FOREIGN KEY ("usuario_id") REFERENCES "usuario" ("id"),
    CONSTRAINT fk_laboratorio FOREIGN KEY ("laboratorio_id") REFERENCES "laboratorio" ("id") 
);