import customtkinter as ctk
from database.database import obter_conexao


class ProcessoView(ctk.CTkFrame):

    def __init__(self, parent, processo_id, matricula, e_novo, callback_sair):
        super().__init__(parent, corner_radius=0)
        self.processo_id = processo_id
        self.matricula = matricula
        self.e_novo = e_novo
        self.callback_sair = callback_sair

        # Header com botão Sair e ID do Processo
        frame_header = ctk.CTkFrame(self, fg_color="transparent")
        frame_header.pack(fill="x", padx=15, pady=10)

        ctk.CTkButton(
            frame_header,
            text="← Sair do Serviço",
            width=120,
            fg_color="gray",
            hover_color="#555555",
            command=self.sair_e_guardar_rascunho,
        ).pack(side="left")

        ctk.CTkLabel(
            frame_header,
            text=f"PROCESSO Nº: #{self.processo_id}   |   VEÍCULO: {self.matricula.upper()}",
            font=("Arial", 16, "bold"),
        ).pack(side="right")

        # Scroll para as 3 Caixas de Texto
        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=15, pady=5)

        # 1. Solicitação do Cliente
        ctk.CTkLabel(
            scroll, text="1. Solicitação do Cliente:", font=("Arial", 13, "bold")
        ).pack(anchor="w", pady=(10, 2))
        self.txt_solicitacao = ctk.CTkTextbox(scroll, height=80)
        self.txt_solicitacao.pack(fill="x", pady=5)
        self.txt_solicitacao.bind("<KeyRelease>", lambda e: self.guardar_progresso_bd())

        # 2. Peças + Botão Solicitar ao Stock
        frame_pecas_lbl = ctk.CTkFrame(scroll, fg_color="transparent")
        frame_pecas_lbl.pack(fill="x", pady=(15, 2))
        ctk.CTkLabel(
            frame_pecas_lbl, text="2. Peças para Encomendar:", font=("Arial", 13, "bold")
        ).pack(side="left")

        btn_solicitar = ctk.CTkButton(
            frame_pecas_lbl,
            text="📦 Solicitar a Stock",
            fg_color="#E67E22",
            hover_color="#D35400",
            height=26,
            command=self.solicitar_pecas_stock,
        )
        btn_solicitar.pack(side="right")

        self.txt_pecas = ctk.CTkTextbox(scroll, height=80)
        self.txt_pecas.pack(fill="x", pady=5)

        # 3. Relatório Técnico
        ctk.CTkLabel(
            scroll, text="3. Relatório Técnico:", font=("Arial", 13, "bold")
        ).pack(anchor="w", pady=(15, 2))
        self.txt_relatorio = ctk.CTkTextbox(scroll, height=120)
        self.txt_relatorio.pack(fill="x", pady=5)
        self.txt_relatorio.bind("<KeyRelease>", lambda e: self.guardar_progresso_bd())

        # Carregar dados existentes na BD
        self.carregar_dados_processo()

        if not self.e_novo:
            self.txt_solicitacao.configure(state="disabled")

        self.lbl_status = ctk.CTkLabel(self, text="", font=("Arial", 11))
        self.lbl_status.pack()

        # Botão Concluir Serviço
        btn_concluir = ctk.CTkButton(
            self,
            text="✔ Serviço Concluído",
            font=("Arial", 15, "bold"),
            fg_color="#27AE60",
            hover_color="#1E8449",
            height=45,
            command=self.concluir_servico,
        )
        btn_concluir.pack(pady=15)

    def carregar_dados_processo(self):
        conn = obter_conexao()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT solicitacao_cliente, relatorio FROM processos WHERE id = %s",
            (self.processo_id,),
        )
        p = cursor.fetchone()
        cursor.close()
        conn.close()

        if p:
            if p["solicitacao_cliente"]:
                self.txt_solicitacao.delete("1.0", "end")
                self.txt_solicitacao.insert("1.0", p["solicitacao_cliente"])
            if p["relatorio"]:
                self.txt_relatorio.delete("1.0", "end")
                self.txt_relatorio.insert("1.0", p["relatorio"])

    def guardar_progresso_bd(self):
        """Guarda as alterações em tempo real sem alterar o estado do processo."""
        sol = self.txt_solicitacao.get("1.0", "end-1c").strip()
        rel = self.txt_relatorio.get("1.0", "end-1c").strip()

        conn = obter_conexao()
        if not conn:
            return
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE processos SET solicitacao_cliente = %s, relatorio = %s WHERE id = %s",
            (sol, rel, self.processo_id),
        )
        conn.commit()
        cursor.close()
        conn.close()

    def solicitar_pecas_stock(self):
        texto_pecas = self.txt_pecas.get("1.0", "end-1c").strip()
        if not texto_pecas:
            self.lbl_status.configure(
                text="Escreva as peças antes de solicitar!", text_color="red"
            )
            return

        conn = obter_conexao()
        if not conn:
            return
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO solicitacoes_stock (processo_id, matricula, descricao_pecas) VALUES (%s, %s, %s)",
            (self.processo_id, self.matricula.upper(), texto_pecas),
        )
        conn.commit()
        cursor.close()
        conn.close()

        self.lbl_status.configure(
            text="✅ Pedido enviado para Consulta/Stock com sucesso!",
            text_color="#2ECC71",
        )

    def sair_e_guardar_rascunho(self):
        self.guardar_progresso_bd()
        self.callback_sair()

    def concluir_servico(self):
        self.guardar_progresso_bd()

        conn = obter_conexao()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE processos SET estado = 'servico_concluido' WHERE id = %s",
            (self.processo_id,),
        )
        conn.commit()
        cursor.close()
        conn.close()

        self.callback_sair()