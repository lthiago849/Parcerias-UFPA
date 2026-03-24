DROP TABLE IF EXISTS email_log;

CREATE TYPE tipo_status AS ENUM (
  'ATIVO',
  'ENCERRADO'
);

CREATE TABLE email (
    id UUID PRIMARY KEY,
    interesse_id UUID,
    assunto_principal VARCHAR(255) NOT NULL,
    status tipo_status NOT NULL DEFAULT 'ATIVO',
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