CREATE TYPE "tipo_usuario" AS ENUM (
  'SERVIDOR',
  'EXTERNO', 
  'DEV'
  );

CREATE TYPE "tipo_registro" AS ENUM (
  'PATENTE_INVENCAO', 
  'MODELO_UTILIDADE', 
  'CERTIFICADO_ADICAO', 
  'MARCA', 
  'DESENHO_INDUSTRIAL', 
  'PROGRAMA_COMPUTADOR', 
  'DIREITO_AUTORAL', 
  'CULTIVAR', 
  'TOPOGRAFIA_CIRCUITO', 
  'INDICACAO_GEOGRAFICA'
  );

CREATE TYPE "categoria_pi" AS ENUM (
  'CIENCIAS_AGRARIAS', 
  'CIENCIAS_BIOLOGICAS', 
  'CIENCIAS_DA_SAUDE', 
  'CIENCIAS_EXATAS_E_TERRA', 
  'ENGENHARIAS', 
  'CIENCIAS_HUMANAS', 
  'CIENCIAS_SOCIAIS_APLICADAS', 
  'LINGUISTICA_LETRAS_E_ARTES', 
  'MULTIDISCIPLINAR', 
  'OUTROS'
  );

CREATE TYPE "tipo_interesse" AS ENUM (
  'FINANCIAR', 
  'COMPRA', 
  'ASSINATURA'
  );

CREATE TABLE "usuario" (
  "id" uuid PRIMARY KEY,
  "login" VARCHAR(255) UNIQUE NOT NULL,
  "email" VARCHAR(255) UNIQUE NOT NULL,
  "nome" VARCHAR(255) NOT NULL,
  "senha" VARCHAR(255) NOT NULL,
  "tipo" tipo_usuario NOT NULL,
  "criado_em" timestamp NOT NULL DEFAULT current_timestamp,
  "atualizado_em" timestamp NOT NULL DEFAULT current_timestamp
);

CREATE TABLE "propriedade_intelectual" (
  "id" uuid PRIMARY KEY,
  "titulo" VARCHAR(255) UNIQUE NOT NULL,
  "resumo" TEXT NOT NULL,
  "tipo" tipo_registro NOT NULL,
  "categoria" categoria_pi NOT NULL,
  "titulares" VARCHAR(500) NOT NULL,
  "imagens" JSONB DEFAULT '[]',
  "inventores" VARCHAR(1000) NOT NULL,
  "unidade_orgao" VARCHAR(255) NOT NULL,
  "palavras_chave" VARCHAR(255) NOT NULL,
  "criado_em" timestamp NOT NULL DEFAULT current_timestamp,
  "atualizado_em" timestamp NOT NULL DEFAULT current_timestamp,
  "aprovada" bool NOT NULL DEFAULT false
);

CREATE TABLE "universidade" (
  "id" uuid PRIMARY KEY,
  "nome" VARCHAR(255) UNIQUE NOT NULL,
  "sigla" VARCHAR(10) UNIQUE NOT NULL,
  "campus" VARCHAR(255) NOT NULL
);

CREATE TABLE "unidades_academicas" (
  "id" uuid PRIMARY KEY,
  "nome" VARCHAR(255) NOT NULL,
  "sigla" VARCHAR(10) UNIQUE NOT NULL,
  "universidade_id" uuid NOT NULL,
  CONSTRAINT fk_unidades_academicas_universidade FOREIGN KEY ("universidade_id") REFERENCES "universidade" ("id")
);

CREATE TABLE "laboratorio" (
  "id" uuid PRIMARY KEY,
  "nome" VARCHAR(255) NOT NULL,
  "sigla" VARCHAR(10) UNIQUE NOT NULL,
  "unidade_academica_id" uuid NOT NULL,
  "aprovado" bool NOT NULL DEFAULT false,
  CONSTRAINT fk_laboratorio_unidades_academicas FOREIGN KEY ("unidade_academica_id") REFERENCES "unidades_academicas" ("id")
);

CREATE TABLE "pi_pertence" (
  "id" uuid PRIMARY KEY,
  "propriedade_intelectual_id" uuid NOT NULL,
  "laboratorio_id" uuid NOT NULL,
  CONSTRAINT fk_pi FOREIGN KEY ("propriedade_intelectual_id") REFERENCES "propriedade_intelectual" ("id"),
  CONSTRAINT fk_lab_pi FOREIGN KEY ("laboratorio_id") REFERENCES "laboratorio" ("id")
);

CREATE TABLE "lab_pertence" (
  "id" uuid PRIMARY KEY,
  "usuario_id" uuid NOT NULL,
  "siape" int UNIQUE NOT NULL,
  "email_institucional" VARCHAR(255) UNIQUE NOT NULL,
  "cpf" VARCHAR(40) UNIQUE NOT NULL,
  "laboratorio_id" uuid NOT NULL,
  CONSTRAINT fk_usuario_lab FOREIGN KEY ("usuario_id") REFERENCES "usuario" ("id"),
  CONSTRAINT fk_lab_usuario FOREIGN KEY ("laboratorio_id") REFERENCES "laboratorio" ("id")
);

CREATE TABLE "interesse" (
  "id" uuid PRIMARY KEY,
  "usuario_id" uuid NOT NULL,
  "propriedade_intelectual_id" uuid NOT NULL,
  "tipo" tipo_interesse NOT NULL,
  CONSTRAINT fk_usuario_interesse FOREIGN KEY ("usuario_id") REFERENCES "usuario" ("id"),
  CONSTRAINT fk_pi_interesse FOREIGN KEY ("propriedade_intelectual_id") REFERENCES "propriedade_intelectual" ("id")
);

CREATE TABLE "email_log" (
  "id" uuid PRIMARY KEY,
  "interesse_id" uuid NOT NULL,
  "remetente" VARCHAR(255) NOT NULL,
  "destinatario" VARCHAR(255) NOT NULL,
  "assunto" VARCHAR(255) NOT NULL,
  "corpo" TEXT NOT NULL,
  "enviado_em" timestamp NOT NULL DEFAULT current_timestamp,
  CONSTRAINT fk_email_interesse FOREIGN KEY ("interesse_id") REFERENCES "interesse" ("id") ON DELETE CASCADE
);