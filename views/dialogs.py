import customtkinter as ctk


class ConfirmarEliminacaoDialog(ctk.CTkToplevel):

    def __init__(self, parent, nome_cliente):
        super().__init__(parent)
        self.parent = parent
        self.opcao_escolhida = (
            None  # Guardará: 'apagar_cliente', 'apagar_tudo' ou None
        )

        self.title("Confirmar Eliminação")
        self.geometry("420x220")
        self.resizable(False, False)
        self.grab_set()  # Torna a janela modal (impede clicar atrás)

        # Mensagem
        lbl_msg = ctk.CTkLabel(
            self,
            text=f"Como deseja proceder com a eliminação de:\n'{nome_cliente}'?",
            font=("Arial", 14, "bold"),
            wraplength=380,
        )
        lbl_msg.pack(pady=(25, 20))

        # Contentor dos Botões
        frame_botoes = ctk.CTkFrame(self, fg_color="transparent")
        frame_botoes.pack(pady=10)

        # 1. Apagar Apenas Cliente
        btn_apagar_cliente = ctk.CTkButton(
            frame_botoes,
            text="Apagar Cliente",
            fg_color="#E67E22",
            hover_color="#D35400",
            width=110,
            command=lambda: self.definir_opcao("apagar_cliente"),
        )
        btn_apagar_cliente.pack(side="left", padx=5)

        # 2. Apagar Cliente + Veículos
        btn_apagar_tudo = ctk.CTkButton(
            frame_botoes,
            text="Cliente + Veículos",
            fg_color="#C0392B",
            hover_color="#922B21",
            width=130,
            command=lambda: self.definir_opcao("apagar_tudo"),
        )
        btn_apagar_tudo.pack(side="left", padx=5)

        # 3. Cancelar
        btn_cancelar = ctk.CTkButton(
            frame_botoes,
            text="Cancelar",
            fg_color="gray",
            hover_color="#555555",
            width=90,
            command=self.destroy,
        )
        btn_cancelar.pack(side="left", padx=5)

    def definir_opcao(self, opcao):
        self.opcao_escolhida = opcao
        self.destroy()