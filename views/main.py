import os
import sys
import customtkinter as ctk
from PIL import Image
from database.database import obter_conexao
from views.consultas import ConsultaView


def obter_caminho_logo():
    """
    Procura prioritariamente pelo logótipo oficial 'logo_AutoAmorim.png'.
    Caso não exista, utiliza como fallback 'AUTO.ico'.
    Compatível com desenvolvimento e distribuição PyInstaller (.exe).
    """
    ficheiros_prioritarios = ["logo_AutoAmorim.png", "AUTO.ico"]

    locais_pesquisa = []
    # Se estiver a correr empacotado pelo PyInstaller
    if hasattr(sys, "_MEIPASS"):
        locais_pesquisa.append(sys._MEIPASS)
        locais_pesquisa.append(os.path.join(sys._MEIPASS, "assets"))

    # Diretório raiz do projeto
    dir_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    locais_pesquisa.extend(
        [
            os.path.join(dir_raiz, "assets"),
            dir_raiz,
            "assets",
            ".",
        ]
    )

    for nome in ficheiros_prioritarios:
        for local in locais_pesquisa:
            caminho_completo = os.path.join(local, nome)
            if os.path.exists(caminho_completo):
                return os.path.abspath(caminho_completo)

    return None


class MainWindow(ctk.CTkToplevel):

    def __init__(self, parent, utilizador):
        super().__init__(parent)
        self.parent = parent
        self.utilizador = utilizador
        self.nome_usuario = utilizador["nome"]
        self.tipo_conta = utilizador["tipo_conta"]
        self.PIN_CORRETO = str(utilizador.get("pin_sidebar") or "1234")
        self.sidebar_aberta = False

        self.title("Auto Amorim - Sistema de Gestão")
        self.state("zoomed")

        # Layout Grelha Principal
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        # -------------------------------------------------------------------
        # TOPBAR
        # -------------------------------------------------------------------
        self.topbar = ctk.CTkFrame(self, height=55, corner_radius=0)
        self.topbar.grid(row=0, column=0, columnspan=2, sticky="ew")

        # 1. Obtenção do Logótipo (Prioridade: logo_AutoAmorim.png -> Fallback: AUTO.ico)
        path_logo = obter_caminho_logo()

        if path_logo and os.path.exists(path_logo):
            try:
                img_pil = Image.open(path_logo)
                # Altura definida para 45px com largura proporcional
                largura_calc = int(img_pil.width * (45.0 / img_pil.height))
                largura_calc = max(45, min(largura_calc, 180))

                self.img_logo = ctk.CTkImage(
                    light_image=img_pil,
                    dark_image=img_pil,
                    size=(largura_calc, 45),
                )
                self.btn_logo = ctk.CTkButton(
                    self.topbar,
                    image=self.img_logo,
                    text="",
                    fg_color="transparent",
                    hover_color="#2B2B2B",
                    cursor="hand2",
                    command=self.voltar_homepage,
                )
            except Exception:
                self.btn_logo = ctk.CTkButton(
                    self.topbar,
                    text="🚗 Auto Amorim",
                    fg_color="transparent",
                    hover_color="#2B2B2B",
                    font=("Arial", 14, "bold"),
                    command=self.voltar_homepage,
                )
        else:
            self.btn_logo = ctk.CTkButton(
                self.topbar,
                text="🚗 Auto Amorim",
                fg_color="transparent",
                hover_color="#2B2B2B",
                font=("Arial", 14, "bold"),
                command=self.voltar_homepage,
            )

        self.btn_logo.pack(side="left", padx=10, pady=5)

        tag_cargo = " [ADMIN]" if self.tipo_conta == "admin" else " [MECÂNICO]"
        self.lbl_user = ctk.CTkLabel(
            self.topbar,
            text=f"Utilizador: {self.nome_usuario}{tag_cargo}",
            font=("Arial", 12, "bold"),
        )
        self.lbl_user.pack(side="left", padx=10)

        self.btn_sair = ctk.CTkButton(
            self.topbar,
            text="Sair",
            fg_color="#C0392B",
            hover_color="#922B21",
            width=65,
            height=28,
            command=self.sair,
        )
        self.btn_sair.pack(side="right", padx=15, pady=5)

        # -------------------------------------------------------------------
        # ÁREA DE CONTEÚDO PRINCIPAL
        # -------------------------------------------------------------------
        self.main_content = ctk.CTkFrame(self, corner_radius=0)
        self.main_content.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # -------------------------------------------------------------------
        # SIDEBAR DIREITA (Apenas para Administradores)
        # -------------------------------------------------------------------
        if self.tipo_conta == "admin":
            self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
            ctk.CTkLabel(
                self.sidebar,
                text="Menu / Consultas",
                font=("Arial", 16, "bold"),
            ).pack(pady=(20, 15))

            opcoes = [
                "Cliente",
                "Faturação",
                "Processo",
                "Veiculo",
                "Stock",
                "Contas",
            ]
            for opcao in opcoes:
                ctk.CTkButton(
                    self.sidebar,
                    text=opcao,
                    anchor="w",
                    fg_color="transparent",
                    command=lambda opt=opcao: self.navegar_para(opt),
                ).pack(fill="x", padx=10, pady=4)

        self.mostrar_homepage_inicial()
        self.protocol("WM_DELETE_WINDOW", self.sair)

    def guardar_tela_atual_se_necessario(self):
        """Grava rascunhos de processos antes de trocar de janela."""
        for widget in self.main_content.winfo_children():
            if hasattr(widget, "guardar_progresso_bd"):
                widget.guardar_progresso_bd()

    def mostrar_homepage_inicial(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

        self.frame_topo_homepage = ctk.CTkFrame(
            self.main_content, fg_color="transparent"
        )
        self.frame_topo_homepage.pack(fill="x", padx=10, pady=5)

        if self.tipo_conta == "admin":
            self.btn_toggle_sidebar = ctk.CTkButton(
                self.frame_topo_homepage,
                text="|<",
                width=45,
                height=26,
                command=self.clique_toggle_sidebar,
            )
            self.btn_toggle_sidebar.pack(side="right")

            self.frame_pin_inline = ctk.CTkFrame(
                self.frame_topo_homepage, fg_color="transparent"
            )
            ctk.CTkLabel(
                self.frame_pin_inline,
                text="PIN Admin:",
                font=("Arial", 12, "bold"),
            ).pack(side="left", padx=(0, 5))
            self.entry_pin = ctk.CTkEntry(
                self.frame_pin_inline,
                width=65,
                height=26,
                show="•",
                justify="center",
            )
            self.entry_pin.pack(side="left", padx=5)
            self.entry_pin.bind("<KeyRelease>", self.verificar_pin_automatico)

        if not self.sidebar_aberta and hasattr(self, "btn_toggle_sidebar"):
            self.btn_toggle_sidebar.configure(text="|<")

        # Caixa de Pesquisa
        frame_busca = ctk.CTkFrame(self.main_content, fg_color="transparent")
        frame_busca.pack(pady=(120, 10))

        ctk.CTkLabel(
            frame_busca,
            text="Introduza a Matrícula do Veículo:",
            font=("Arial", 18, "bold"),
        ).pack(pady=5)

        self.entry_matricula = ctk.CTkEntry(
            frame_busca,
            width=280,
            height=35,
            placeholder_text="ex: 00-AA-00",
            justify="center",
        )
        self.entry_matricula.pack(pady=5)
        self.entry_matricula.bind("<KeyRelease>", self.ao_digitar_matricula)

        self.lbl_sugestoes = ctk.CTkLabel(
            frame_busca, text="", font=("Arial", 11), text_color="gray"
        )
        self.lbl_sugestoes.pack()

        self.lbl_msg_home = ctk.CTkLabel(
            self.main_content, text="", font=("Arial", 12, "bold")
        )
        self.lbl_msg_home.pack(pady=5)

        # Botões Principais de Ação
        frame_botoes = ctk.CTkFrame(self.main_content, fg_color="transparent")
        frame_botoes.pack(pady=20)

        self.btn_novo = ctk.CTkButton(
            frame_botoes,
            text="+ Novo serviço",
            font=("Arial", 15, "bold"),
            width=220,
            height=60,
            command=self.acao_novo_servico,
        )
        self.btn_novo.pack(side="left", padx=15)

        self.btn_continuar = ctk.CTkButton(
            frame_botoes,
            text="▶ Continuar Serviço",
            font=("Arial", 15, "bold"),
            width=220,
            height=60,
            command=self.acao_continuar_servico,
        )
        self.btn_continuar.pack(side="left", padx=15)

    def clique_toggle_sidebar(self):
        if self.sidebar_aberta:
            self.fechar_sidebar()
        else:
            if self.frame_pin_inline.winfo_ismapped():
                self.ocultar_tira_pin()
            else:
                self.frame_pin_inline.pack(side="right", padx=5)
                self.entry_pin.delete(0, "end")
                self.entry_pin.focus()

    def verificar_pin_automatico(self, event):
        if len(self.entry_pin.get().strip()) == 4:
            if self.entry_pin.get().strip() == self.PIN_CORRETO:
                self.ocultar_tira_pin()
                self.abrir_sidebar()
            else:
                self.entry_pin.delete(0, "end")

    def abrir_sidebar(self):
        self.sidebar.grid(row=1, column=1, sticky="nsew")
        self.sidebar_aberta = True
        if hasattr(self, "btn_toggle_sidebar"):
            self.btn_toggle_sidebar.configure(text=">|")

    def fechar_sidebar(self):
        if hasattr(self, "sidebar"):
            self.sidebar.grid_forget()
        self.sidebar_aberta = False
        if hasattr(self, "btn_toggle_sidebar"):
            self.btn_toggle_sidebar.configure(text="|<")

    def ocultar_tira_pin(self):
        if hasattr(self, "frame_pin_inline"):
            self.frame_pin_inline.pack_forget()

    def voltar_homepage(self):
        """Ao clicar no logótipo: fecha menus, guarda dados e força o retorno à homepage inicial."""
        self.guardar_tela_atual_se_necessario()
        self.fechar_sidebar()
        self.ocultar_tira_pin()
        self.mostrar_homepage_inicial()

    def navegar_para(self, opcao):
        self.guardar_tela_atual_se_necessario()
        for widget in self.main_content.winfo_children():
            widget.destroy()

        if opcao == "Faturação":
            from views.faturacao import FaturacaoView

            view = FaturacaoView(
                self.main_content, callback_sair=self.mostrar_homepage_inicial
            )
            view.pack(fill="both", expand=True)
        else:
            view = ConsultaView(
                self.main_content,
                tipo_consulta=opcao,
                callback_voltar=self.mostrar_homepage_inicial,
            )
            view.pack(fill="both", expand=True)

    def ao_digitar_matricula(self, event):
        texto = self.entry_matricula.get().strip().upper()
        if not texto:
            self.lbl_sugestoes.configure(text="")
            return

        conn = obter_conexao()
        if not conn:
            return
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT matricula FROM veiculos WHERE matricula LIKE %s LIMIT 3",
            (f"%{texto}%",),
        )
        res = cursor.fetchall()
        cursor.close()
        conn.close()

        if res:
            sugestoes = " | ".join([r["matricula"] for r in res])
            self.lbl_sugestoes.configure(text=f"Sugestões: {sugestoes}")
        else:
            self.lbl_sugestoes.configure(text="Matrícula não encontrada na BD")

    def acao_novo_servico(self):
        mat = self.entry_matricula.get().strip().upper()
        if not mat:
            self.lbl_msg_home.configure(
                text="Erro: Introduza uma matrícula válida!", text_color="red"
            )
            return

        conn = obter_conexao()
        if not conn:
            return

        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id FROM veiculos WHERE UPPER(matricula) = %s", (mat,)
        )
        veic = cursor.fetchone()

        if not veic:
            self.lbl_msg_home.configure(
                text="Erro: O veículo não consta na base de dados!",
                text_color="red",
            )
            cursor.close()
            conn.close()
            return

        query_verificacao = """
        SELECT id, estado FROM processos
        WHERE veiculo_id = %s AND estado IN ('em_aberto', 'servico_concluido')
        LIMIT 1
        """
        cursor.execute(query_verificacao, (veic["id"],))
        processo_pendente = cursor.fetchone()

        if processo_pendente:
            if processo_pendente["estado"] == "em_aberto":
                msg_erro = f"Erro: O veículo {mat} já tem o Processo #{processo_pendente['id']} EM ABERTO!\nUtilize 'Continuar Serviço'."
            else:
                msg_erro = f"Erro: O Processo #{processo_pendente['id']} está concluído mas pendente de Faturação!"

            self.lbl_msg_home.configure(text=msg_erro, text_color="#E67E22")
            cursor.close()
            conn.close()
            return

        cursor.execute(
            "INSERT INTO processos (veiculo_id, estado) VALUES (%s, 'em_aberto')",
            (veic["id"],),
        )
        processo_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()

        self.lbl_msg_home.configure(text="")
        self.abrir_ecran_processo(processo_id, mat, e_novo=True)

    def acao_continuar_servico(self):
        mat = self.entry_matricula.get().strip().upper()
        conn = obter_conexao()
        if not conn:
            return

        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT p.id FROM processos p
        JOIN veiculos v ON p.veiculo_id = v.id
        WHERE UPPER(v.matricula) = %s AND p.estado = 'em_aberto'
        ORDER BY p.id DESC LIMIT 1
        """
        cursor.execute(query, (mat,))
        proc = cursor.fetchone()
        cursor.close()
        conn.close()

        if not proc:
            self.lbl_msg_home.configure(
                text="Erro: Não existe nenhum processo EM ABERTO para esta matrícula!",
                text_color="red",
            )
            return

        self.abrir_ecran_processo(proc["id"], mat, e_novo=False)

    def abrir_ecran_processo(self, processo_id, matricula, e_novo=True):
        for widget in self.main_content.winfo_children():
            widget.destroy()

        from views.processos import ProcessoView

        view = ProcessoView(
            self.main_content,
            processo_id=processo_id,
            matricula=matricula,
            e_novo=e_novo,
            callback_sair=self.mostrar_homepage_inicial,
        )
        view.pack(fill="both", expand=True)

    def sair(self):
        self.guardar_tela_atual_se_necessario()
        self.parent.destroy()