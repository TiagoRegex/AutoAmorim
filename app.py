import customtkinter as ctk
from database.database import inicializar_bd
from views.login import LoginWindow

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

ctk.set_widget_scaling(1.2) # Tamanho de todo o software

def main():
    # 1. Executa a criação/atualização das tabelas na Base de Dados
    inicializar_bd()

    # 2. Inicia a janela de Login diretamente
    app = LoginWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
