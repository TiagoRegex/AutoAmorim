import os
import sys
import tempfile
from tkinter import filedialog
import customtkinter as ctk
from database.database import obter_conexao
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from services.email_service import enviar_fatura_email


def obter_caminho_logo_fatura():
    """
    Procura exclusivamente pela imagem dedicada para faturas: 'logo_AutoAmorim_Fatura.png'.
    Caso não exista, retorna None (deixando o espaço sem imagem no PDF).
    """
    nome_ficheiro = "logo_AutoAmorim_Fatura.png"
    locais_pesquisa = []

    # Compatibilidade com executável PyInstaller (.exe)
    if hasattr(sys, "_MEIPASS"):
        locais_pesquisa.append(sys._MEIPASS)
        locais_pesquisa.append(os.path.join(sys._MEIPASS, "assets"))

    # Diretório raiz do projeto e pasta assets
    dir_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    locais_pesquisa.extend(
        [
            os.path.join(dir_raiz, "assets"),
            dir_raiz,
            "assets",
            ".",
        ]
    )

    for local in locais_pesquisa:
        caminho_completo = os.path.join(local, nome_ficheiro)
        if os.path.exists(caminho_completo):
            return os.path.abspath(caminho_completo)

    return None


class FaturacaoView(ctk.CTkFrame):

    def __init__(self, parent, callback_sair):
        super().__init__(parent, corner_radius=0)
        self.callback_sair = callback_sair
        self.processo_atual = None
        self.linhas_itens = []
        self.ultimo_pdf_gerado = None

        # Topo
        f_topo = ctk.CTkFrame(self, fg_color="transparent")
        f_topo.pack(fill="x", padx=15, pady=10)

        ctk.CTkButton(
            f_topo,
            text="← Voltar",
            width=90,
            fg_color="#555555",
            command=self.callback_sair,
        ).pack(side="left")
        ctk.CTkLabel(
            f_topo, text="🧾 Ecrã de Faturação", font=("Arial", 18, "bold")
        ).pack(side="left", padx=15)

        # 1. Pesquisa
        f_pesq = ctk.CTkFrame(self, fg_color="#2B2B2B", corner_radius=8)
        f_pesq.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(
            f_pesq, text="Nº Processo:", font=("Arial", 13, "bold")
        ).pack(side="left", padx=15, pady=10)
        self.entry_proc_id = ctk.CTkEntry(
            f_pesq, placeholder_text="Ex: 1", width=120
        )
        self.entry_proc_id.pack(side="left", padx=5)

        ctk.CTkButton(
            f_pesq,
            text="Carregar Processo",
            fg_color="#3498DB",
            hover_color="#2980B9",
            command=self.carregar_processo,
        ).pack(side="left", padx=10)
        self.lbl_erro = ctk.CTkLabel(f_pesq, text="", font=("Arial", 12))
        self.lbl_erro.pack(side="left", padx=10)

        # 2. Detalhes
        self.f_info = ctk.CTkFrame(self, fg_color="#2B2B2B", corner_radius=8)
        self.f_info.pack(fill="x", padx=15, pady=5)

        self.lbl_detalhes = ctk.CTkLabel(
            self.f_info,
            text="Introduza o número de um processo para carregar os dados.",
            font=("Arial", 12),
            text_color="gray",
        )
        self.lbl_detalhes.pack(anchor="w", padx=15, pady=10)

        # 3. Configurações Fiscais e Email do Cliente
        self.f_conteudo = ctk.CTkFrame(self, fg_color="transparent")
        self.f_conteudo.pack(fill="both", expand=True, padx=15, pady=5)

        f_fiscal = ctk.CTkFrame(self.f_conteudo, fg_color="#2B2B2B", corner_radius=8)
        f_fiscal.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            f_fiscal, text="NIF na Fatura:", font=("Arial", 12, "bold")
        ).pack(side="left", padx=(15, 5), pady=8)
        self.entry_nif_fatura = ctk.CTkEntry(
            f_fiscal, placeholder_text="NIF do Cliente", width=130
        )
        self.entry_nif_fatura.pack(side="left", padx=5, pady=8)

        ctk.CTkLabel(
            f_fiscal, text="E-mail Cliente:", font=("Arial", 12, "bold")
        ).pack(side="left", padx=(15, 5), pady=8)
        self.entry_email_fatura = ctk.CTkEntry(
            f_fiscal, placeholder_text="email@cliente.pt", width=200
        )
        self.entry_email_fatura.pack(side="left", padx=5, pady=8)

        ctk.CTkLabel(f_fiscal, text="IVA:", font=("Arial", 12, "bold")).pack(
            side="left", padx=(15, 5), pady=8
        )
        self.combo_iva = ctk.CTkOptionMenu(
            f_fiscal, values=["23%", "0%"], width=80
        )
        self.combo_iva.set("23%")
        self.combo_iva.pack(side="left", padx=5, pady=8)

        # Grelha
        f_grelha_hdr = ctk.CTkFrame(self.f_conteudo, fg_color="#333333", height=30)
        f_grelha_hdr.pack(fill="x")

        ctk.CTkLabel(
            f_grelha_hdr,
            text="Descrição do Serviço / Peça",
            font=("Arial", 11, "bold"),
            width=350,
            anchor="w",
        ).pack(side="left", padx=10)
        ctk.CTkLabel(
            f_grelha_hdr, text="Qtd", font=("Arial", 11, "bold"), width=80
        ).pack(side="left", padx=5)
        ctk.CTkLabel(
            f_grelha_hdr,
            text="Preço Unit (€)",
            font=("Arial", 11, "bold"),
            width=120,
        ).pack(side="left", padx=5)
        ctk.CTkLabel(
            f_grelha_hdr, text="Total (€)", font=("Arial", 11, "bold"), width=120
        ).pack(side="left", padx=5)

        self.scroll_itens = ctk.CTkScrollableFrame(
            self.f_conteudo, fg_color="transparent", height=180
        )
        self.scroll_itens.pack(fill="both", expand=True, pady=5)

        # Rodapé
        f_rodape = ctk.CTkFrame(self, fg_color="transparent")
        f_rodape.pack(fill="x", padx=15, pady=10)

        ctk.CTkButton(
            f_rodape,
            text="+ Adicionar Linha",
            fg_color="#27AE60",
            hover_color="#1E8449",
            command=self.adicionar_linha_item,
        ).pack(side="left", padx=(0, 10))
        ctk.CTkButton(
            f_rodape,
            text="💾 Guardar Dados",
            fg_color="#3498DB",
            hover_color="#2980B9",
            command=self.acao_guardar_apenas,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            f_rodape,
            text="📧 Enviar por E-mail",
            font=("Arial", 13, "bold"),
            fg_color="#8E44AD",
            hover_color="#732D91",
            height=40,
            command=self.acao_enviar_email,
        ).pack(side="right", padx=(10, 0))
        ctk.CTkButton(
            f_rodape,
            text="📄 Gerar Fatura PDF",
            font=("Arial", 13, "bold"),
            fg_color="#E67E22",
            hover_color="#D35400",
            height=40,
            command=self.gerar_fatura_pdf,
        ).pack(side="right")

    def carregar_processo(self):
        pid = self.entry_proc_id.get().strip()
        if not pid.isdigit():
            self.lbl_erro.configure(text="ID inválido!", text_color="red")
            return

        conn = obter_conexao()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT p.*, v.matricula, v.marca, v.modelo, c.nome as cliente_nome, c.nif as cliente_nif, c.email as cliente_email
        FROM processos p
        JOIN veiculos v ON p.veiculo_id = v.id
        LEFT JOIN clientes c ON v.cliente_id = c.id
        WHERE p.id = %s
        """
        cursor.execute(query, (int(pid),))
        proc = cursor.fetchone()

        if not proc:
            self.lbl_erro.configure(
                text="Processo não encontrado!", text_color="red"
            )
            cursor.close()
            conn.close()
            return

        self.processo_atual = proc
        self.lbl_erro.configure(text="")

        cursor.execute(
            "SELECT descricao_pecas FROM solicitacoes_stock WHERE processo_id = %s",
            (int(pid),),
        )
        pecas = cursor.fetchall()
        qtd_pecas = len(pecas)
        desc_pecas = (
            ", ".join([p["descricao_pecas"] for p in pecas])
            if pecas
            else "Nenhuma peça solicitada."
        )

        texto_detalhes = (
            f"🚗 Veículo: {proc['matricula'].upper()} ({proc['marca']} {proc['modelo']}) | "
            f"👤 Cliente: {proc['cliente_nome'] or 'Consumidor Final'}\n"
            f"📝 Solicitação: {proc['solicitacao_cliente'] or '---'}\n"
            f"📦 Peças Stock ({qtd_pecas} pedido(s)): {desc_pecas}"
        )
        self.lbl_detalhes.configure(text=texto_detalhes, text_color="white")

        self.entry_nif_fatura.delete(0, "end")
        if proc.get("cliente_nif"):
            self.entry_nif_fatura.insert(0, proc["cliente_nif"])

        self.entry_email_fatura.delete(0, "end")
        if proc.get("cliente_email"):
            self.entry_email_fatura.insert(0, proc["cliente_email"])

        cursor.execute(
            "SELECT * FROM itens_fatura WHERE processo_id = %s", (int(pid),)
        )
        itens_bd = cursor.fetchall()
        cursor.close()
        conn.close()

        for frame in self.linhas_itens:
            frame["container"].destroy()
        self.linhas_itens.clear()

        if itens_bd:
            for item in itens_bd:
                self.adicionar_linha_item(
                    item["descricao"],
                    str(item["quantidade"]),
                    str(item["preco_unidade"]),
                )
        else:
            self.adicionar_linha_item(
                "Mão de Obra / Serviço Técnico", "1", "30.00"
            )

    def adicionar_linha_item(self, desc="", qtd="1", preco="0.00"):
        f_linha = ctk.CTkFrame(
            self.scroll_itens, fg_color="#2B2B2B", corner_radius=4
        )
        f_linha.pack(fill="x", pady=2)

        e_desc = ctk.CTkEntry(f_linha, width=340)
        e_desc.insert(0, desc)
        e_desc.pack(side="left", padx=5, pady=5)

        e_qtd = ctk.CTkEntry(f_linha, width=70)
        e_qtd.insert(0, qtd)
        e_qtd.pack(side="left", padx=5)

        e_preco = ctk.CTkEntry(f_linha, width=110)
        e_preco.insert(0, preco)
        e_preco.pack(side="left", padx=5)

        lbl_tot = ctk.CTkLabel(
            f_linha, text="0.00 €", width=110, font=("Arial", 12, "bold")
        )
        lbl_tot.pack(side="left", padx=5)

        def recat_total(*args):
            try:
                q = float(e_qtd.get().replace(",", "."))
                p = float(e_preco.get().replace(",", "."))
                lbl_tot.configure(text=f"{q * p:.2f} €")
            except ValueError:
                lbl_tot.configure(text="0.00 €")

        e_qtd.bind("<KeyRelease>", recat_total)
        e_preco.bind("<KeyRelease>", recat_total)
        recat_total()

        btn_del = ctk.CTkButton(
            f_linha,
            text="🗑️",
            width=30,
            fg_color="#C0392B",
            hover_color="#922B21",
            command=lambda: self.remover_linha(f_linha),
        )
        btn_del.pack(side="right", padx=5)

        self.linhas_itens.append(
            {
                "container": f_linha,
                "desc": e_desc,
                "qtd": e_qtd,
                "preco": e_preco,
                "lbl_total": lbl_tot,
            }
        )

    def remover_linha(self, f_linha):
        f_linha.destroy()
        self.linhas_itens = [
            item for item in self.linhas_itens if item["container"] != f_linha
        ]

    def acao_guardar_apenas(self):
        if not self.processo_atual:
            self.lbl_erro.configure(
                text="Carregue um processo primeiro!", text_color="red"
            )
            return
        self.guardar_itens_bd()
        self.lbl_erro.configure(
            text="✅ Alterações gravadas com sucesso!", text_color="#2ECC71"
        )

    def guardar_itens_bd(self):
        if not self.processo_atual:
            return

        pid = self.processo_atual["id"]
        conn = obter_conexao()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM itens_fatura WHERE processo_id = %s", (pid,))

        for item in self.linhas_itens:
            desc = item["desc"].get().strip()
            try:
                q = float(item["qtd"].get().replace(",", "."))
                p = float(item["preco"].get().replace(",", "."))
            except ValueError:
                continue

            if desc:
                tot = q * p
                cursor.execute(
                    "INSERT INTO itens_fatura (processo_id, quantidade, descricao, preco_unidade, preco_final) VALUES (%s, %s, %s, %s, %s)",
                    (pid, q, desc, p, tot),
                )

        conn.commit()
        cursor.close()
        conn.close()

    def construir_pdf_em_disco(self, caminho_pdf):
        pid = self.processo_atual["id"]
        c = canvas.Canvas(caminho_pdf, pagesize=A4)
        largura, altura = A4

        # Busca exclusivamente pela imagem de fatura (logo_AutoAmorim_Fatura.png)
        logo_path = obter_caminho_logo_fatura()
        if logo_path and os.path.exists(logo_path):
            try:
                c.drawImage(
                    logo_path,
                    50,
                    altura - 85,
                    width=130,
                    height=45,
                    preserveAspectRatio=True,
                    mask="auto",
                )
                x_texto = 190
            except Exception:
                x_texto = 50
        else:
            # Caso não exista a imagem específica de fatura, não desenha imagem e inicia o texto no início da margem
            x_texto = 50

        c.setFont("Helvetica-Bold", 16)
        c.drawString(x_texto, altura - 45, "AUTO AMORIM - OFICINA AUTOMÓVEL")
        c.setFont("Helvetica", 10)
        c.drawString(x_texto, altura - 60, "Travessa Aradas, Nº 32 - Lobão")
        c.drawString(x_texto, altura - 73, "Tel: +351 912 899 726 | Email: geral@autoamorim.pt")

        c.setLineWidth(1)
        c.line(50, altura - 95, largura - 50, altura - 95)

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, altura - 118, f"FATURA Nº: PROC-{pid}")
        c.setFont("Helvetica", 10)

        dono = self.processo_atual["cliente_nome"] or "Consumidor Final"
        nif_final = (
            self.entry_nif_fatura.get().strip() or "Consumidor Final (Sem NIF)"
        )

        c.drawString(50, altura - 138, f"Cliente: {dono}")
        c.drawString(50, altura - 153, f"NIF: {nif_final}")
        c.drawString(
            350, altura - 138, f"Matrícula: {self.processo_atual['matricula'].upper()}"
        )
        c.drawString(
            350,
            altura - 153,
            f"Veículo: {self.processo_atual['marca']} {self.processo_atual['modelo']}",
        )

        y = altura - 190
        c.setFillColorRGB(0.2, 0.2, 0.2)
        c.rect(50, y, largura - 100, 20, fill=True, stroke=False)
        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(60, y + 6, "Descrição")
        c.drawString(320, y + 6, "Qtd")
        c.drawString(380, y + 6, "Preço Unit.")
        c.drawString(480, y + 6, "Total")

        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica", 10)
        y -= 20

        subtotal = 0.0
        for item in self.linhas_itens:
            desc = item["desc"].get().strip()
            try:
                q = float(item["qtd"].get().replace(",", "."))
                p = float(item["preco"].get().replace(",", "."))
                tot = q * p
            except ValueError:
                continue

            if desc:
                subtotal += tot
                c.drawString(60, y, desc[:45])
                c.drawString(320, y, f"{q:.1f}")
                c.drawString(380, y, f"{p:.2f} €")
                c.drawString(480, y, f"{tot:.2f} €")
                y -= 18

        c.line(50, y - 5, largura - 50, y - 5)
        y -= 25

        taxa_iva = 0.23 if self.combo_iva.get() == "23%" else 0.0
        iva = subtotal * taxa_iva
        total_final = subtotal + iva

        c.drawString(360, y, "Subtotal:")
        c.drawString(480, y, f"{subtotal:.2f} €")

        c.drawString(360, y - 15, f"IVA ({self.combo_iva.get()}):")
        c.drawString(480, y - 15, f"{iva:.2f} €")

        c.setFont("Helvetica-Bold", 12)
        c.drawString(360, y - 35, "TOTAL FATURA:")
        c.drawString(480, y - 35, f"{total_final:.2f} €")

        c.save()

    def gerar_fatura_pdf(self):
        if not self.processo_atual:
            self.lbl_erro.configure(
                text="Carregue um processo primeiro!", text_color="red"
            )
            return

        self.guardar_itens_bd()

        pid = self.processo_atual["id"]
        caminho_pdf = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=f"Fatura_Processo_{pid}.pdf",
            filetypes=[("PDF Document", "*.pdf")],
        )

        if not caminho_pdf:
            return

        self.construir_pdf_em_disco(caminho_pdf)
        self.ultimo_pdf_gerado = caminho_pdf

        conn = obter_conexao()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE processos SET estado = 'faturado' WHERE id = %s", (pid,)
        )
        conn.commit()
        cursor.close()
        conn.close()

        self.lbl_erro.configure(
            text="✅ Fatura gravada com sucesso!", text_color="#2ECC71"
        )

    def acao_enviar_email(self):
        if not self.processo_atual:
            self.lbl_erro.configure(
                text="Carregue um processo primeiro!", text_color="red"
            )
            return

        email_dest = self.entry_email_fatura.get().strip()
        if not email_dest or "@" not in email_dest:
            self.lbl_erro.configure(
                text="Indique um e-mail válido!", text_color="red"
            )
            return

        self.guardar_itens_bd()
        pid = self.processo_atual["id"]

        caminho_envio = self.ultimo_pdf_gerado
        if not caminho_envio or not os.path.exists(caminho_envio):
            caminho_envio = os.path.join(
                tempfile.gettempdir(), f"Fatura_Processo_{pid}.pdf"
            )
            self.construir_pdf_em_disco(caminho_envio)

        self.lbl_erro.configure(
            text="A enviar e-mail via API...", text_color="#3498DB"
        )
        self.update_idletasks()

        cliente_nome = self.processo_atual["cliente_nome"] or "Cliente"
        sucesso, msg = enviar_fatura_email(
            destinatario_email=email_dest,
            nome_cliente=cliente_nome,
            matricula=self.processo_atual["matricula"],
            caminho_pdf=caminho_envio,
        )

        if sucesso:
            conn = obter_conexao()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE processos SET estado = 'faturado' WHERE id = %s", (pid,)
            )
            conn.commit()
            cursor.close()
            conn.close()
            self.lbl_erro.configure(text=f"✅ {msg}", text_color="#2ECC71")
        else:
            self.lbl_erro.configure(text=f"❌ {msg}", text_color="red")
