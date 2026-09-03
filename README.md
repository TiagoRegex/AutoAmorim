# 🚗 Auto Amorim - Sistema Integrado de Gestão de Oficina

Aplicação desktop nativa desenvolvida em Python para a gestão operacional, técnica e fiscal de oficinas automóveis. O sistema integra base de dados relacional MySQL, geração dinâmica de faturas em PDF e consumo de API REST para envio transacional de e-mails.

---

## 👥 Credenciais de Acesso Padrão

A base de dados é aprovisionada com o seguinte utilizador administrativo automático:

| Perfil | Utilizador | Palavra-passe | PIN Navbar | Privilégios |
| :--- | :--- | :--- | :--- | :--- |
| **Administrador** | `admin` | `admin123` | `1234` | Acesso total (Faturação, Clientes, Veículos, Contas, Stock) |
| **Mecânico** *(Opcional)* | `mecanico` | `123` | *Sem PIN* | Acesso restrito (Abertura de ordens e requisição de peças) |

---

## 🔑 Configuração da API de E-mail (Resend)

Por motivos de segurança e conformidade com as boas práticas do GitHub, a chave privada de API da Resend foi removida do código-fonte público.

Para testar o envio transacional de faturas em PDF por e-mail:
1. Crie uma conta gratuita em [Resend.com](https://resend.com) e obtenha uma API Key (formato `re_...`).
2. Abra o ficheiro `services/email_service.py`.
3. Substitua o valor da variável `RESEND_API_KEY` pela sua chave:

```python
RESEND_API_KEY = "re_SUA_CHAVE_AQUI"
```

---

## ⚙️ Pré-requisitos do Sistema

1. **Servidor MySQL ativo** (via XAMPP, WampServer ou serviço nativo MySQL na porta padrão `3306`).
2. **Utilizador padrão do MySQL:** `root` com a palavra-passe `123qwe` ou sem palavra-passe (o sistema tenta ambas automaticamente).
3. **Python 3.10+** (necessário apenas se for executado a partir do código-fonte).

---

## 🚀 Como Executar a Aplicação

### Opção A: Através do Executável (.EXE)
1. Certifique-se de que o serviço MySQL está ativo.
2. Aceda à pasta `output/AutoAmorim` (ou diretório do executável distribuído).
3. Execute o ficheiro `AutoAmorim.exe`.
*Nota: A aplicação deteta e provisiona automaticamente a base de dados `autoamorim_db`, as tabelas e o utilizador `admin` no primeiro arranque.*

### Opção B: Através do Código-Fonte (Python)
1. No terminal do projeto, ative o ambiente virtual:
   ```bash
   # Windows:
   .venv\Scripts\activate
   ```
2. Instale as dependências essenciais:
   ```bash
   pip install -r requirements.txt
   ```
   *(Dependências essenciais: customtkinter, mysql-connector-python, reportlab, requests, pillow)*

3. Inicie o sistema:
   ```bash
   python app.py
   ```

---

## 🛠️ Tecnologias e Arquitetura

* **Interface Gráfica (GUI):** CustomTkinter (Dark Theme profissional e responsivo).
* **Base de Dados:** MySQL (Integridade referencial e 3ª Forma Normal).
* **Geração de Documentação Fiscal:** ReportLab (Desenho vetorial A4 com cálculo de IVA a 0% e 23%).
* **Integração de Serviços Externos:** API REST Resend (Envio transacional do PDF codificado em Base64 via HTTP POST).
* **Distribuição:** PyInstaller (Binário em modo One-Directory com runtime hooks para dependências).

---

## 📂 Estrutura de Diretórios

```plaintext
AutoAmorimV6/
├── app.py                      # Ponto de entrada do sistema
├── assets/                     # Recursos visuais (Logótipos, ícones e temas)
│   ├── logo_AutoAmorim.png     # Logótipo da Topbar
│   ├── logo_AutoAmorim_Fatura.png # Logótipo com fundo escuro para a fatura PDF
│   └── AUTO.ico                # Ícone do executável
├── database/                   # Camada de persistência
│   ├── database.py             # Conexão MySQL (com use_pure=True e reconexão)
│   └── schema.sql              # Estrutura DDL e utilizador inicial
├── services/                   # Serviços e integrações externas
│   └── email_service.py        # Módulo de envio de e-mails via API REST
├── views/                      # Camada de interface gráfica (MVC)
│   ├── login.py                # Ecrã de autenticação
│   ├── main.py                 # Navbar, Sidebar protegida por PIN e Router
│   ├── processos.py            # Ordem de trabalho com auto-save contínuo
│   ├── faturacao.py            # Emissão e envio de faturas comerciais
│   └── consultas.py            # Gestão CRUD de entidades
└── README.md                   # Manual de instalação e execução
```

---

## 🔒 Destaques Técnicos e Segurança

* **Conformidade com RGPD:** Separação de perfis técnicos e administrativos. Acesso a dados financeiros e de clientes blindado por PIN de 4 dígitos.
* **Mecanismo Anti-Perda (Auto-Save):** Gravação em tempo real no evento `<KeyRelease>` e salvamento preventivo nas transições de janela.
* **Resiliência a Dependências em C:** Conector MySQL configurado com `use_pure=True` para garantir compatibilidade em ambientes empacotados.