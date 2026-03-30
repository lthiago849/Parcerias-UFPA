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

CREATE TYPE tipo_status_email AS ENUM (
  'ATIVO',
  'ENCERRADO'
);

CREATE TYPE tipo_funcao AS ENUM (
  'COORDENADOR/COORDENADORA',
  'PESQUISADOR/PESQUISADORA',
  'COLOBORADOR/COLOBORADORA'
);

CREATE TABLE "usuario" (
  "id" uuid PRIMARY KEY,
  "login" VARCHAR(255) UNIQUE NOT NULL,
  "email" VARCHAR(255) UNIQUE NOT NULL,
  "nome" VARCHAR(255) NOT NULL,
  "senha" VARCHAR(255) NOT NULL,
  "tipo" tipo_usuario NOT NULL,
  "siape" VARCHAR(20) UNIQUE,
  "telefone" VARCHAR(20),
  "cpf" VARCHAR(14) UNIQUE,
  "cnpj" VARCHAR(18) UNIQUE,
  "endereco" VARCHAR(255),
  "cidade" VARCHAR(100),
  "estado" VARCHAR(50),
  "pais" VARCHAR(50),
  "cep" VARCHAR(10),
  "nacionalidade" VARCHAR(50),
  "instituicao" VARCHAR(255),
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
  "palavras_chave" VARCHAR(255) NOT NULL,
  "criado_em" timestamp NOT NULL DEFAULT current_timestamp,
  "atualizado_em" timestamp NOT NULL DEFAULT current_timestamp
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
  "unidade_academica_id" uuid NOT NULL,
  "nome" VARCHAR(255) NOT NULL,
  "sigla" VARCHAR(10) UNIQUE NOT NULL,
  "descricao" TEXT,
  "areas_linhas_pesquisa" TEXT,
  "servicos_disponiveis" TEXT,
  "equipamentos" TEXT,
  "site" VARCHAR(255),
  "email" VARCHAR(500),
  "telefone" VARCHAR(20),
  "endereco" VARCHAR(255),
  "cidade" VARCHAR(100),
  "estado" VARCHAR(50),
  "cep" VARCHAR(10),
  "latitude" DECIMAL(10, 8),
  "longitude" DECIMAL(11, 8),
  "atualizado_em" timestamp NOT NULL DEFAULT current_timestamp,
  "atualizado_por" uuid,
  "aprovado" bool NOT NULL DEFAULT false,
  CONSTRAINT fk_laboratorio_unidades_academicas FOREIGN KEY ("unidade_academica_id") REFERENCES "unidades_academicas" ("id"),
  CONSTRAINT fk_usuario FOREIGN KEY ("atualizado_por") REFERENCES "usuario" ("id")
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


CREATE TABLE email (
    id UUID PRIMARY KEY,
    interesse_id UUID,
    assunto_principal VARCHAR(255) NOT NULL,
    status tipo_status_email NOT NULL DEFAULT 'ATIVO',
    criado_em TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    
    CONSTRAINT fk_email_interesse FOREIGN KEY (interesse_id) REFERENCES interesse(id)
);

CREATE TABLE mensagem (
    id UUID PRIMARY KEY,
    email_id UUID NOT NULL,
    remetente VARCHAR(255) NOT NULL,
    destinatario VARCHAR(255) NOT NULL,
    corpo TEXT NOT NULL,
    enviado_em TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    
    CONSTRAINT fk_mensagem_email FOREIGN KEY (email_id) REFERENCES email(id) ON DELETE CASCADE
);

CREATE TABLE equipe (
  id UUID PRIMARY KEY,
  laboratorio_id UUID NOT NULL,
  nome VARCHAR(255),
  funcao tipo_funcao,
  email VARCHAR(500),
  lattes VARCHAR(50),
  
  CONSTRAINT fk_equipe_laboratorio FOREIGN KEY (laboratorio_id) REFERENCES laboratorio(id) ON DELETE CASCADE
);