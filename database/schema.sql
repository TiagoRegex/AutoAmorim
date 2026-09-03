CREATE DATABASE IF NOT EXISTS autoamorim_db;
USE autoamorim_db;

-- 1. Tabela LogIn / Utilizadores
CREATE TABLE IF NOT EXISTS utilizadores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL,
    pass VARCHAR(255) NOT NULL,
    tipo_conta ENUM('admin', 'user') DEFAULT 'user',
    pin_sidebar VARCHAR(10) NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabela de Clientes
CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    telefone VARCHAR(20),
    nif VARCHAR(20) UNIQUE,
    email VARCHAR(100),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Tabela de Veículos
CREATE TABLE IF NOT EXISTS veiculos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NULL,
    matricula VARCHAR(20) NOT NULL UNIQUE,
    marca VARCHAR(50) NOT NULL,
    modelo VARCHAR(50) NOT NULL,
    ano INT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
);

-- 4. Tabela de Processos
CREATE TABLE IF NOT EXISTS processos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    veiculo_id INT NOT NULL,
    solicitacao_cliente TEXT,
    relatorio TEXT,
    com_contribuinte VARCHAR(10) DEFAULT 'nao',
    estado ENUM('em_aberto', 'servico_concluido', 'faturado') DEFAULT 'em_aberto',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (veiculo_id) REFERENCES veiculos(id) ON DELETE CASCADE
);

-- 5. Tabela de Solicitações de Stock
CREATE TABLE IF NOT EXISTS solicitacoes_stock (
    id INT AUTO_INCREMENT PRIMARY KEY,
    processo_id INT NOT NULL,
    matricula VARCHAR(20) NOT NULL,
    descricao_pecas TEXT NOT NULL,
    estado ENUM('solicitado', 'encomendado', 'entregue') DEFAULT 'solicitado',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (processo_id) REFERENCES processos(id) ON DELETE CASCADE
);

-- 6. Tabela de Itens de Faturação
CREATE TABLE IF NOT EXISTS itens_fatura (
    id INT AUTO_INCREMENT PRIMARY KEY,
    processo_id INT NOT NULL,
    quantidade DECIMAL(10,2) NOT NULL DEFAULT 1,
    descricao VARCHAR(255) NOT NULL,
    preco_unidade DECIMAL(10,2) NOT NULL,
    preco_final DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (processo_id) REFERENCES processos(id) ON DELETE CASCADE
);

-- 7. Tabela para o Stock Interno
CREATE TABLE IF NOT EXISTS stock_interno (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR(255) NOT NULL,
    quantidade INT NOT NULL DEFAULT 0,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. Utilizador Administrador Padrão (Criado Automaticamente)
INSERT IGNORE INTO utilizadores (username, nome, pass, tipo_conta, pin_sidebar)
VALUES ('admin', 'Administrador Principal', 'admin123', 'admin', '1234');