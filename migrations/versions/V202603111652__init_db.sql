CREATE TYPE "TipoUsuario" AS ENUM(
    'DOCENTE',
    'EXTERNO',
    'DESENVOLVEDOR'
);

CREATE TABLE "usuario"(
    "id" uuid NOT NULL,
    "login" VARCHAR(255) UNIQUE NOT NULL,
    "email" VARCHAR(255) UNIQUE NOT NULL,
    "nome" VARCHAR(255)  NOT NULL,
    "senha" VARCHAR(255) NOT NULL,
    "tipo" "TipoUsuario" NOT NULL,
    "criado_em" timestamp NOT NULL DEFAULT current_timestamp,
    "atualizado_em" timestamp NOT NULL DEFAULT current_timestamp,
    PRIMARY KEY ("id")
);