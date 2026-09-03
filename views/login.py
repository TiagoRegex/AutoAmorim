import customtkinter as ctk
from database.database import obter_conexao
from views.main import MainWindow

class LoginWindow(ctk.CTk):
    """Janela de Autenticação com Username e Palavra-passe"""
    def __init__(self):
        super().__init__()

        self.title("Auto Amorim - Login")

        largura, altura = 400, 450
        pos_x = (self.winfo_screenwidth() // 2) - (largura // 2)
        pos_y = (self.winfo_screenheight() // 2) - (altura // 2)

        self.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")
        self.resizable(False, False)

        self.lbl_titulo = ctk.CTkLabel(self, text="AUTO AMORIM", font=("Arial", 22, "bold"))
        self.lbl_titulo.pack(pady=(40, 20))

        # Inputs alterados para Username
        self.entry_user = ctk.CTkEntry(self, placeholder_text="Nome de Utilizador (Username)", width=280, height=40)
        self.entry_user.pack(pady=10)

        self.entry_password = ctk.CTkEntry(self, placeholder_text="Password", show="•", width=280, height=40)
        self.entry_password.pack(pady=10)

        self.lbl_mensagem = ctk.CTkLabel(self, text="", text_color="red")
        self.lbl_mensagem.pack(pady=5)

        self.btn_login = ctk.CTkButton(self, text="Entrar", command=self.efetuar_login, width=280, height=40)
        self.btn_login.pack(pady=20)

    def efetuar_login(self):
        user_digitado = self.entry_user.get().strip()
        pass_digitada = self.entry_password.get().strip()

        if not user_digitado or not pass_digitada:
            self.lbl_mensagem.configure(text="Preencha o utilizador e a palavra-passe!", text_color="red")
            return

        conn = obter_conexao()
        if not conn:
            self.lbl_mensagem.configure(text="Erro ao ligar à Base de Dados!", text_color="red")
            return

        try:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM utilizadores WHERE username = %s AND pass = %s"
            cursor.execute(query, (user_digitado, pass_digitada))
            utilizador = cursor.fetchone()

            if utilizador:
                self.withdraw()
                # Passa o objeto completo do utilizador para gerir permissões
                homepage = MainWindow(self, utilizador)
                homepage.focus()
            else:
                self.lbl_mensagem.configure(text="Utilizador ou palavra-passe incorretos.", text_color="red")
        except Exception as e:
            self.lbl_mensagem.configure(text=f"Erro de execução: {e}", text_color="red")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            conn.close()