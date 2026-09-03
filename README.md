# 🚗 Auto Amorim - Sistema Integrado de Gestão de Oficina

Aplicação desktop nativa desenvolvida em Python para a gestão operacional, técnica e fiscal de oficinas automóveis. O sistema integra base de dados relacional MySQL, geração dinâmica de faturas em PDF e consumo de API REST para envio transacional de e-mails.

---

## 👥 Credenciais de Acesso Padrão

A base de dados é aprovisionada com o seguinte utilizador administrativo:

| Perfil | Utilizador | Palavra-passe | PIN Navbar | Privilégios |
| :--- | :--- | :--- | :--- | :--- |
| **Administrador** | `admin` | `admin123` | `1234` | Acesso total (Faturação, Clientes, Veículos, Contas, Stock) |
| **Mecânico** *(Opcional)* | `mecanico` | `123` | *Sem PIN* | Acesso restrito (Abertura de ordens e requisição de peças) |

---

## ⚙️ Pré-requisitos do Sistema

1. **Servidor MySQL ativo** (via XAMPP, WampServer ou serviço nativo MySQL na porta padrão `3306`).
2. **Utilizador padrão do MySQL:** `root` sem palavra-passe (ou alterar conforme necessário em `database/database.py`).
3. **Python 3.10+** (necessário apenas se for executado a partir do código-fonte).

---

## 🚀 Como Executar a Aplicação

### Opção A: Através do Executável (.EXE)
1. Certifique-se de que o serviço MySQL está ativo.
2. Aceda à pasta `output/AutoAmorim` (ou diretório do executável distribuído).
3. Execute o ficheiro `AutoAmorim.exe`.
4. *A aplicação deteta a ausência da base de dados e executa o provisionamento das tabelas e do administrador automaticamente.*

### Opção B: Através do Código-Fonte (Python)
1. No terminal do projeto, ative o ambiente virtual:
   ```bash
   # Windows:
   .venv\Scripts\activate