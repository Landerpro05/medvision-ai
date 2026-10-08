CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,

    enabled BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE user_roles (
    user_id UUID NOT NULL,
    role_id UUID NOT NULL,

    PRIMARY KEY (user_id, role_id),

    CONSTRAINT fk_user_roles_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_user_roles_role
        FOREIGN KEY (role_id)
        REFERENCES roles(id)
        ON DELETE CASCADE
);

CREATE TABLE studies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL,

    image_path VARCHAR(500) NOT NULL,

    status VARCHAR(30) NOT NULL DEFAULT 'PENDING',

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_studies_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT chk_studies_status
        CHECK (status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED'))
);

CREATE TABLE models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    name VARCHAR(100) NOT NULL,
    version VARCHAR(50) NOT NULL,
    architecture VARCHAR(100) NOT NULL,

    description TEXT,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    active BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT uq_models_name_version
        UNIQUE (name, version)
);

CREATE TABLE analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    study_id UUID NOT NULL,
    model_id UUID NOT NULL,

    prediction VARCHAR(100) NOT NULL,
    probability NUMERIC(5,4) NOT NULL,

    processing_time_ms BIGINT,

    explanation_path VARCHAR(500),

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_analyses_study
        FOREIGN KEY (study_id)
        REFERENCES studies(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_analyses_model
        FOREIGN KEY (model_id)
        REFERENCES models(id),

    CONSTRAINT chk_analyses_probability
        CHECK (probability >= 0 AND probability <= 1)
);

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID,

    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100),
    entity_id UUID,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_audit_logs_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE SET NULL
);