import customtkinter as ctk
from database.database import obter_conexao
from views.dialogs import ConfirmarEliminacaoDialog


class ConsultaView(ctk.CTkFrame):

    def __init__(self, parent, tipo_consulta, callback_voltar):
        super().__init__(parent, corner_radius=0)
        self.parent = parent
        self.tipo_consulta = tipo_consulta
        self.callback_voltar = callback_voltar

        # Topo
        frame_topo = ctk.CTkFrame(self, fg_color="transparent")
        frame_topo.pack(fill="x", padx=15, pady=10)

        ctk.CTkButton(
            frame_topo,
            text="← Voltar",
            width=90,
            fg_color="#555555",
            hover_color="#333333",
            command=self.callback_voltar,
        ).pack(side="left", padx=(0, 15))

        titulos = {
            "Cliente": "📋 Consulta de Clientes",
            "Veiculo": "🚗 Consulta de Veículos",
            "Stock": "📦 Gestão de Stock / Peças",
            "Processo": "⚙️ Gestão de Processos",
            "Contas": "👥 Gestão de Utilizadores e Acessos",
        }
        ctk.CTkLabel(
            frame_topo,
            text=titulos.get(tipo_consulta, tipo_consulta),
            font=("Arial", 18, "bold"),
        ).pack(side="left")

        # Botão para criar Clientes, Veículos ou Contas
        if tipo_consulta in ["Cliente", "Veiculo", "Contas"]:
            txt_btn = (
                "+ Criar Cliente"
                if tipo_consulta == "Cliente"
                else "+ Criar Veículo"
                if tipo_consulta == "Veiculo"
                else "+ Criar Conta"
            )
            btn_novo = ctk.CTkButton(
                frame_topo,
                text=txt_btn,
                fg_color="#27AE60",
                hover_color="#1E8449",
                font=("Arial", 13, "bold"),
                command=self.abrir_modal_criar,
            )
            btn_novo.pack(side="right")

        self.carregar_dados()

    def carregar_dados(self):
        for w in self.winfo_children():
            if w != self.winfo_children()[0]:  # Mantém o topo
                w.destroy()

        conn = obter_conexao()
        if not conn:
            return

        cursor = conn.cursor(dictionary=True)

        # 1. CLIENTES (COM BOTÕES EDITAR E ELIMINAR)
        if self.tipo_consulta == "Cliente":
            self.scroll = ctk.CTkScrollableFrame(self)
            self.scroll.pack(fill="both", expand=True, padx=15, pady=(0, 10))

            cursor.execute("SELECT * FROM clientes ORDER BY nome ASC")
            for cli in cursor.fetchall():
                card = ctk.CTkFrame(self.scroll, fg_color="#2B2B2B", corner_radius=8)
                card.pack(fill="x", padx=5, pady=6)

                f_info = ctk.CTkFrame(card, fg_color="transparent")
                f_info.pack(side="left", padx=15, pady=10)

                ctk.CTkLabel(f_info, text=f"👤 {cli['nome']}", font=("Arial", 14, "bold")).pack(anchor="w")
                detalhes = f"📞 Tel: {cli['telefone'] or '---'}   |   📄 NIF: {cli['nif'] or '---'}   |   ✉️ {cli.get('email') or '---'}"
                ctk.CTkLabel(f_info, text=detalhes, font=("Arial", 12), text_color="#AAAAAA").pack(anchor="w", pady=(2, 0))

                f_botoes = ctk.CTkFrame(card, fg_color="transparent")
                f_botoes.pack(side="right", padx=15)

                ctk.CTkButton(
                    f_botoes,
                    text="Editar",
                    width=70,
                    fg_color="#F39C12",
                    hover_color="#D68910",
                    command=lambda c=cli: self.modal_editar_cliente(c),
                ).pack(side="left", padx=4)

                ctk.CTkButton(
                    f_botoes,
                    text="Eliminar",
                    fg_color="#C0392B",
                    hover_color="#922B21",
                    width=70,
                    command=lambda c=cli: self.eliminar_cliente(c),
                ).pack(side="left", padx=4)

        # 2. VEÍCULOS (COM BOTÕES EDITAR E ELIMINAR)
        elif self.tipo_consulta == "Veiculo":
            self.scroll = ctk.CTkScrollableFrame(self)
            self.scroll.pack(fill="both", expand=True, padx=15, pady=(0, 10))

            query = """
                SELECT v.*, c.nome as nome_cliente 
                FROM veiculos v 
                LEFT JOIN clientes c ON v.cliente_id = c.id
                ORDER BY v.matricula ASC
            """
            cursor.execute(query)
            for veic in cursor.fetchall():
                card = ctk.CTkFrame(self.scroll, fg_color="#2B2B2B", corner_radius=8)
                card.pack(fill="x", padx=5, pady=6)

                f_info = ctk.CTkFrame(card, fg_color="transparent")
                f_info.pack(side="left", padx=15, pady=10)

                mat_upper = veic["matricula"].upper()
                ctk.CTkLabel(
                    f_info,
                    text=f"🚗 {mat_upper} - {veic['marca'].upper()} {veic['modelo'].upper()}",
                    font=("Arial", 14, "bold"),
                    text_color="#3498DB",
                ).pack(anchor="w")

                dono = veic["nome_cliente"] or "Sem Proprietário Associado"
                ctk.CTkLabel(f_info, text=f"👤 Proprietário: {dono}", font=("Arial", 12), text_color="#AAAAAA").pack(anchor="w", pady=(2, 0))

                f_botoes = ctk.CTkFrame(card, fg_color="transparent")
                f_botoes.pack(side="right", padx=15)

                ctk.CTkButton(
                    f_botoes,
                    text="Editar",
                    width=70,
                    fg_color="#F39C12",
                    hover_color="#D68910",
                    command=lambda v=veic: self.modal_editar_veiculo(v),
                ).pack(side="left", padx=4)

                ctk.CTkButton(
                    f_botoes,
                    text="Eliminar",
                    fg_color="#C0392B",
                    hover_color="#922B21",
                    width=70,
                    command=lambda vid=veic["id"]: self.eliminar_veiculo(vid),
                ).pack(side="left", padx=4)

        # 3. PROCESSOS
        elif self.tipo_consulta == "Processo":
            self.scroll = ctk.CTkScrollableFrame(self)
            self.scroll.pack(fill="both", expand=True, padx=15, pady=(0, 10))

            query = """
                SELECT p.*, v.matricula FROM processos p
                JOIN veiculos v ON p.veiculo_id = v.id
                ORDER BY p.id DESC
            """
            cursor.execute(query)
            for proc in cursor.fetchall():
                card = ctk.CTkFrame(self.scroll, fg_color="#2B2B2B", corner_radius=8)
                card.pack(fill="x", padx=5, pady=6)

                f_info = ctk.CTkFrame(card, fg_color="transparent")
                f_info.pack(side="left", padx=15, pady=10)

                cor_estado = (
                    "#3498DB"
                    if proc["estado"] == "em_aberto"
                    else "#F1C40F"
                    if proc["estado"] == "servico_concluido"
                    else "#2ECC71"
                )
                txt_estado = proc["estado"].replace("_", " ").upper()
                mat_upper = proc["matricula"].upper()

                ctk.CTkLabel(
                    f_info,
                    text=f"Processo #{proc['id']}   |   Veículo: {mat_upper}   |   [{txt_estado}]",
                    font=("Arial", 13, "bold"),
                    text_color=cor_estado,
                ).pack(anchor="w")

                solic = proc["solicitacao_cliente"] or "Sem notas de solicitação."
                ctk.CTkLabel(f_info, text=f"📝 Solicitação: {solic}", font=("Arial", 11), text_color="#CCCCCC").pack(anchor="w", pady=(2, 0))

                ctk.CTkButton(
                    card,
                    text="Eliminar",
                    fg_color="#C0392B",
                    hover_color="#922B21",
                    width=80,
                    command=lambda pid=proc["id"]: self.confirmar_eliminar_processo(pid),
                ).pack(side="right", padx=15)

        # 4. STOCK (PESQUISA + ABAS)
        elif self.tipo_consulta == "Stock":
            tabview = ctk.CTkTabview(self)
            tabview.pack(fill="both", expand=True, padx=15, pady=(0, 10))

            tab_pedidos = tabview.add("📦 Pedidos ao Armazém")
            tab_interno = tabview.add("📋 Stock Interno")

            # Barra de Pesquisa
            f_pesquisa = ctk.CTkFrame(tab_pedidos, fg_color="transparent")
            f_pesquisa.pack(fill="x", padx=5, pady=(5, 10))

            ctk.CTkLabel(f_pesquisa, text="🔍 Pesquisar Processo:", font=("Arial", 12, "bold")).pack(side="left", padx=(0, 5))
            entry_pesquisa = ctk.CTkEntry(f_pesquisa, placeholder_text="Nº do Processo", width=150)
            entry_pesquisa.pack(side="left", padx=5)

            scroll_p = ctk.CTkScrollableFrame(tab_pedidos, fg_color="transparent")
            scroll_p.pack(fill="both", expand=True, padx=5, pady=5)

            def filtrar_pedidos():
                termo = entry_pesquisa.get().strip()
                for child in scroll_p.winfo_children():
                    child.destroy()

                conn_f = obter_conexao()
                cursor_f = conn_f.cursor(dictionary=True)

                query_p = "SELECT * FROM solicitacoes_stock"
                params = []
                if termo.isdigit():
                    query_p += " WHERE processo_id = %s"
                    params.append(int(termo))
                query_p += " ORDER BY criado_em DESC"

                cursor_f.execute(query_p, tuple(params))
                pedidos_f = cursor_f.fetchall()
                cursor_f.close()
                conn_f.close()

                if not pedidos_f:
                    ctk.CTkLabel(
                        scroll_p,
                        text="Nenhum pedido encontrado.",
                        text_color="gray",
                        font=("Arial", 14),
                    ).pack(pady=40)
                    return

                for p in pedidos_f:
                    self.renderizar_card_pedido(scroll_p, p)

            ctk.CTkButton(
                f_pesquisa,
                text="Pesquisar",
                width=90,
                fg_color="#3498DB",
                hover_color="#2980B9",
                command=filtrar_pedidos,
            ).pack(side="left", padx=5)

            filtrar_pedidos()

            # ABA 2: STOCK INTERNO
            f_topo_int = ctk.CTkFrame(tab_interno, fg_color="transparent")
            f_topo_int.pack(fill="x", padx=10, pady=10)

            ctk.CTkLabel(f_topo_int, text="Artigos em Inventário", font=("Arial", 16, "bold")).pack(side="left")

            ctk.CTkButton(
                f_topo_int,
                text="+ Adicionar Artigo",
                fg_color="#27AE60",
                hover_color="#1E8449",
                height=35,
                font=("Arial", 13, "bold"),
                command=self.modal_adicionar_stock_interno,
            ).pack(side="right")

            scroll_i = ctk.CTkScrollableFrame(tab_interno, fg_color="transparent")
            scroll_i.pack(fill="both", expand=True, padx=5, pady=(0, 5))

            cursor.execute("SELECT * FROM stock_interno ORDER BY descricao ASC")
            itens_stock = cursor.fetchall()

            if not itens_stock:
                ctk.CTkLabel(
                    scroll_i,
                    text="Nenhum artigo registado no stock interno.",
                    text_color="gray",
                    font=("Arial", 14),
                ).pack(pady=40)

            for item in itens_stock:
                card_i = ctk.CTkFrame(scroll_i, fg_color="#2B2B2B", corner_radius=8)
                card_i.pack(fill="x", pady=5)

                ctk.CTkLabel(card_i, text=item["descricao"], font=("Arial", 14, "bold")).pack(side="left", padx=20, pady=12)

                f_ctrl = ctk.CTkFrame(card_i, fg_color="transparent")
                f_ctrl.pack(side="right", padx=20)

                ctk.CTkButton(
                    f_ctrl,
                    text="-",
                    width=32,
                    height=28,
                    fg_color="#555555",
                    font=("Arial", 14, "bold"),
                    command=lambda iid=item["id"], q=item["quantidade"]: self.atualizar_qtd_stock(iid, q - 1),
                ).pack(side="left", padx=4)

                ctk.CTkLabel(f_ctrl, text=str(item["quantidade"]), font=("Arial", 14, "bold"), width=40, justify="center").pack(side="left", padx=4)

                ctk.CTkButton(
                    f_ctrl,
                    text="+",
                    width=32,
                    height=28,
                    fg_color="#555555",
                    font=("Arial", 14, "bold"),
                    command=lambda iid=item["id"], q=item["quantidade"]: self.atualizar_qtd_stock(iid, q + 1),
                ).pack(side="left", padx=4)

                ctk.CTkButton(
                    f_ctrl,
                    text="🗑️",
                    fg_color="#C0392B",
                    hover_color="#922B21",
                    width=36,
                    height=28,
                    command=lambda iid=item["id"]: self.eliminar_item_stock_interno(iid),
                ).pack(side="left", padx=(20, 0))

        # 5. CONTAS (GESTAO DE UTILIZADORES)
        elif self.tipo_consulta == "Contas":
            self.scroll = ctk.CTkScrollableFrame(self)
            self.scroll.pack(fill="both", expand=True, padx=15, pady=(0, 10))

            cursor.execute("SELECT id, username, nome, tipo_conta, pin_sidebar FROM utilizadores ORDER BY id ASC")
            for u in cursor.fetchall():
                card = ctk.CTkFrame(self.scroll, fg_color="#2B2B2B", corner_radius=8)
                card.pack(fill="x", padx=5, pady=6)

                f_info = ctk.CTkFrame(card, fg_color="transparent")
                f_info.pack(side="left", padx=15, pady=10)

                tag_cor = "#E74C3C" if u["tipo_conta"] == "admin" else "#3498DB"
                ctk.CTkLabel(f_info, text=f"👤 {u['nome']} (@{u['username']})", font=("Arial", 14, "bold")).pack(anchor="w")
                ctk.CTkLabel(f_info, text=f"Tipo de Acesso: {u['tipo_conta'].upper()}", font=("Arial", 11, "bold"), text_color=tag_cor).pack(anchor="w", pady=(2, 0))

                f_acoes = ctk.CTkFrame(card, fg_color="transparent")
                f_acoes.pack(side="right", padx=15)

                ctk.CTkButton(
                    f_acoes,
                    text="Editar",
                    width=70,
                    fg_color="#F39C12",
                    hover_color="#D68910",
                    command=lambda user=u: self.modal_editar_conta(user),
                ).pack(side="left", padx=4)

                if u["username"] != "admin":
                    ctk.CTkButton(
                        f_acoes,
                        text="Eliminar",
                        width=70,
                        fg_color="#C0392B",
                        hover_color="#922B21",
                        command=lambda uid=u["id"]: self.eliminar_conta(uid),
                    ).pack(side="left", padx=4)

        cursor.close()
        conn.close()

    def renderizar_card_pedido(self, parent, p):
        card = ctk.CTkFrame(parent, fg_color="#2B2B2B", corner_radius=8)
        card.pack(fill="x", pady=6)

        cores_estado = {
            "solicitado": ("#3498DB", "Solicitado ao Armazém"),
            "encomendado": ("#E67E22", "Encomendado"),
            "entregue": ("#2ECC71", "Entregue"),
        }
        cor, texto_estado = cores_estado.get(p["estado"], ("#3498DB", "Solicitado ao Armazém"))
        data_hora = p["criado_em"].strftime("%d/%m/%Y %H:%M") if p.get("criado_em") else "---"

        f_info = ctk.CTkFrame(card, fg_color="transparent")
        f_info.pack(side="left", padx=15, pady=12)

        ctk.CTkLabel(
            f_info,
            text=f"Processo #{p['processo_id']}   |   Veículo: {p['matricula'].upper()}   |   {data_hora}",
            font=("Arial", 13, "bold"),
            text_color=cor,
        ).pack(anchor="w")

        ctk.CTkLabel(f_info, text=f"🛠️ Peças Pedidas: {p['descricao_pecas']}", font=("Arial", 12)).pack(anchor="w", pady=(3, 0))
        ctk.CTkLabel(f_info, text=f"Estado: {texto_estado}", font=("Arial", 11, "italic"), text_color=cor).pack(anchor="w", pady=(2, 0))

        f_btns = ctk.CTkFrame(card, fg_color="transparent")
        f_btns.pack(side="right", padx=15)

        ctk.CTkButton(
            f_btns,
            text="Encomendado",
            fg_color="#E67E22",
            hover_color="#D35400",
            width=110,
            height=30,
            command=lambda pid=p["id"]: self.alterar_estado_pedido(pid, "encomendado"),
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            f_btns,
            text="Entregue",
            fg_color="#2ECC71",
            hover_color="#27AE60",
            width=90,
            height=30,
            command=lambda pid=p["id"]: self.alterar_estado_pedido(pid, "entregue"),
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            f_btns,
            text="🗑️",
            fg_color="#C0392B",
            hover_color="#922B21",
            width=38,
            height=30,
            command=lambda pid=p["id"]: self.eliminar_pedido_stock(pid),
        ).pack(side="left", padx=4)

    def alterar_estado_pedido(self, pedido_id, novo_estado):
        conn = obter_conexao()
        cursor = conn.cursor()
        cursor.execute("UPDATE solicitacoes_stock SET estado = %s WHERE id = %s", (novo_estado, pedido_id))
        conn.commit()
        cursor.close()
        conn.close()
        self.carregar_dados()

    def eliminar_pedido_stock(self, pedido_id):
        conn = obter_conexao()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM solicitacoes_stock WHERE id = %s", (pedido_id,))
        conn.commit()
        cursor.close()
        conn.close()
        self.carregar_dados()

    def modal_adicionar_stock_interno(self):
        win = ctk.CTkToplevel(self)
        win.title("Adicionar Artigo ao Stock Interno")
        win.geometry("320x220")
        win.grab_set()

        ctk.CTkLabel(win, text="Novo Artigo de Stock", font=("Arial", 14, "bold")).pack(pady=12)
        e_desc = ctk.CTkEntry(win, placeholder_text="Descrição (ex: Óleo 5W30)")
        e_desc.pack(fill="x", padx=20, pady=5)

        e_qtd = ctk.CTkEntry(win, placeholder_text="Quantidade Inicial")
        e_qtd.pack(fill="x", padx=20, pady=5)
        e_qtd.insert(0, "1")

        def guardar():
            desc = e_desc.get().strip()
            try:
                qtd = int(e_qtd.get().strip())
            except ValueError:
                qtd = 0

            if desc:
                conn = obter_conexao()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO stock_interno (descricao, quantidade) VALUES (%s, %s)", (desc, qtd))
                conn.commit()
                cursor.close()
                conn.close()
                win.destroy()
                self.carregar_dados()

        ctk.CTkButton(win, text="Adicionar", fg_color="#27AE60", command=guardar).pack(pady=15)

    def atualizar_qtd_stock(self, item_id, nova_qtd):
        if nova_qtd < 0:
            nova_qtd = 0
        conn = obter_conexao()
        cursor = conn.cursor()
        cursor.execute("UPDATE stock_interno SET quantidade = %s WHERE id = %s", (nova_qtd, item_id))
        conn.commit()
        cursor.close()
        conn.close()
        self.carregar_dados()

    def eliminar_item_stock_interno(self, item_id):
        conn = obter_conexao()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM stock_interno WHERE id = %s", (item_id,))
        conn.commit()
        cursor.close()
        conn.close()
        self.carregar_dados()

    def abrir_modal_criar(self):
        if self.tipo_consulta == "Cliente":
            self.modal_criar_cliente()
        elif self.tipo_consulta == "Veiculo":
            self.modal_criar_veiculo()
        elif self.tipo_consulta == "Contas":
            self.modal_criar_conta()

    def modal_criar_cliente(self):
        win = ctk.CTkToplevel(self)
        win.title("Criar Novo Cliente")
        win.geometry("380x370")
        win.resizable(False, False)
        win.grab_set()

        ctk.CTkLabel(win, text="👤 Registar Novo Cliente", font=("Arial", 15, "bold")).pack(pady=12)
        entry_nome = ctk.CTkEntry(win, placeholder_text="Nome Completo")
        entry_nome.pack(fill="x", padx=20, pady=4)
        entry_tel = ctk.CTkEntry(win, placeholder_text="Telefone / Telemóvel")
        entry_tel.pack(fill="x", padx=20, pady=4)
        entry_nif = ctk.CTkEntry(win, placeholder_text="NIF")
        entry_nif.pack(fill="x", padx=20, pady=4)
        entry_email = ctk.CTkEntry(win, placeholder_text="E-mail (ex: cliente@email.pt)")
        entry_email.pack(fill="x", padx=20, pady=4)

        lbl_erro = ctk.CTkLabel(win, text="", text_color="red")
        lbl_erro.pack(pady=2)

        def submeter():
            nome = entry_nome.get().strip()
            tel = entry_tel.get().strip()
            nif = entry_nif.get().strip()
            email = entry_email.get().strip()

            if not nome:
                lbl_erro.configure(text="O nome é obrigatório!")
                return

            conn = obter_conexao()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO clientes (nome, telefone, nif, email) VALUES (%s, %s, %s, %s)",
                    (nome, tel or None, nif or None, email or None),
                )
                conn.commit()
                win.destroy()
                self.carregar_dados()
            except Exception:
                lbl_erro.configure(text="Erro ao guardar (NIF duplicado?)")
            finally:
                cursor.close()
                conn.close()

        ctk.CTkButton(win, text="Guardar Cliente", fg_color="#27AE60", command=submeter).pack(pady=10)

    def modal_editar_cliente(self, cliente):
        win = ctk.CTkToplevel(self)
        win.title(f"Editar Cliente - {cliente['nome']}")
        win.geometry("380x370")
        win.resizable(False, False)
        win.grab_set()

        ctk.CTkLabel(win, text="✏️ Editar Dados do Cliente", font=("Arial", 15, "bold")).pack(pady=12)

        entry_nome = ctk.CTkEntry(win, placeholder_text="Nome Completo")
        entry_nome.insert(0, cliente["nome"] or "")
        entry_nome.pack(fill="x", padx=20, pady=4)

        entry_tel = ctk.CTkEntry(win, placeholder_text="Telefone / Telemóvel")
        entry_tel.insert(0, cliente["telefone"] or "")
        entry_tel.pack(fill="x", padx=20, pady=4)

        entry_nif = ctk.CTkEntry(win, placeholder_text="NIF")
        entry_nif.insert(0, cliente["nif"] or "")
        entry_nif.pack(fill="x", padx=20, pady=4)

        entry_email = ctk.CTkEntry(win, placeholder_text="E-mail (ex: cliente@email.pt)")
        entry_email.insert(0, cliente.get("email") or "")
        entry_email.pack(fill="x", padx=20, pady=4)

        lbl_erro = ctk.CTkLabel(win, text="", text_color="red")
        lbl_erro.pack(pady=2)

        def submeter():
            nome = entry_nome.get().strip()
            tel = entry_tel.get().strip()
            nif = entry_nif.get().strip()
            email = entry_email.get().strip()

            if not nome:
                lbl_erro.configure(text="O nome é obrigatório!")
                return

            conn = obter_conexao()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "UPDATE clientes SET nome = %s, telefone = %s, nif = %s, email = %s WHERE id = %s",
                    (nome, tel or None, nif or None, email or None, cliente["id"]),
                )
                conn.commit()
                win.destroy()
                self.carregar_dados()
            except Exception:
                lbl_erro.configure(text="Erro ao atualizar (NIF duplicado?)")
            finally:
                cursor.close()
                conn.close()

        ctk.CTkButton(win, text="Atualizar Cliente", fg_color="#F39C12", hover_color="#D68910", command=submeter).pack(pady=10)

    def modal_criar_veiculo(self):
        conn = obter_conexao()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nome FROM clientes ORDER BY nome ASC")
        clientes = cursor.fetchall()
        cursor.close()
        conn.close()

        win = ctk.CTkToplevel(self)
        win.title("Criar Novo Veículo")
        win.geometry("400x380")
        win.resizable(False, False)
        win.grab_set()

        ctk.CTkLabel(win, text="🚗 Registar Novo Veículo", font=("Arial", 15, "bold")).pack(pady=15)
        entry_mat = ctk.CTkEntry(win, placeholder_text="Matrícula (ex: 00-AA-00)")
        entry_mat.pack(fill="x", padx=20, pady=5)
        entry_marca = ctk.CTkEntry(win, placeholder_text="Marca")
        entry_marca.pack(fill="x", padx=20, pady=5)
        entry_modelo = ctk.CTkEntry(win, placeholder_text="Modelo")
        entry_modelo.pack(fill="x", padx=20, pady=5)

        dict_clientes = {"Nenhum": None}
        opcoes_combo = ["Nenhum"]
        for c in clientes:
            dict_clientes[c["nome"]] = c["id"]
            opcoes_combo.append(c["nome"])

        combo_cliente = ctk.CTkOptionMenu(win, values=opcoes_combo)
        combo_cliente.pack(fill="x", padx=20, pady=5)

        lbl_erro = ctk.CTkLabel(win, text="", text_color="red")
        lbl_erro.pack(pady=2)

        def submeter():
            mat = entry_mat.get().strip().upper()
            marca = entry_marca.get().strip()
            modelo = entry_modelo.get().strip()
            cliente_id = dict_clientes.get(combo_cliente.get())

            if not mat or not marca or not modelo:
                lbl_erro.configure(text="Matrícula, Marca e Modelo são obrigatórios!")
                return

            conn = obter_conexao()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO veiculos (matricula, marca, modelo, cliente_id) VALUES (%s, %s, %s, %s)",
                    (mat, marca, modelo, cliente_id),
                )
                conn.commit()
                win.destroy()
                self.carregar_dados()
            except Exception:
                lbl_erro.configure(text="Erro: Matrícula já existe na BD!")
            finally:
                cursor.close()
                conn.close()

        ctk.CTkButton(win, text="Guardar Veículo", fg_color="#27AE60", command=submeter).pack(pady=15)

    def modal_editar_veiculo(self, veic):
        conn = obter_conexao()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nome FROM clientes ORDER BY nome ASC")
        clientes = cursor.fetchall()
        cursor.close()
        conn.close()

        win = ctk.CTkToplevel(self)
        win.title(f"Editar Veículo - {veic['matricula']}")
        win.geometry("400x380")
        win.resizable(False, False)
        win.grab_set()

        ctk.CTkLabel(win, text="✏️ Editar Dados do Veículo", font=("Arial", 15, "bold")).pack(pady=15)

        entry_mat = ctk.CTkEntry(win, placeholder_text="Matrícula (ex: 00-AA-00)")
        entry_mat.insert(0, veic["matricula"] or "")
        entry_mat.pack(fill="x", padx=20, pady=5)

        entry_marca = ctk.CTkEntry(win, placeholder_text="Marca")
        entry_marca.insert(0, veic["marca"] or "")
        entry_marca.pack(fill="x", padx=20, pady=5)

        entry_modelo = ctk.CTkEntry(win, placeholder_text="Modelo")
        entry_modelo.insert(0, veic["modelo"] or "")
        entry_modelo.pack(fill="x", padx=20, pady=5)

        dict_clientes = {"Nenhum": None}
        opcoes_combo = ["Nenhum"]
        dono_atual = "Nenhum"

        for c in clientes:
            dict_clientes[c["nome"]] = c["id"]
            opcoes_combo.append(c["nome"])
            if c["id"] == veic.get("cliente_id"):
                dono_atual = c["nome"]

        combo_cliente = ctk.CTkOptionMenu(win, values=opcoes_combo)
        combo_cliente.set(dono_atual)
        combo_cliente.pack(fill="x", padx=20, pady=5)

        lbl_erro = ctk.CTkLabel(win, text="", text_color="red")
        lbl_erro.pack(pady=2)

        def submeter():
            mat = entry_mat.get().strip().upper()
            marca = entry_marca.get().strip()
            modelo = entry_modelo.get().strip()
            cliente_id = dict_clientes.get(combo_cliente.get())

            if not mat or not marca or not modelo:
                lbl_erro.configure(text="Matrícula, Marca e Modelo são obrigatórios!")
                return

            conn = obter_conexao()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "UPDATE veiculos SET matricula = %s, marca = %s, modelo = %s, cliente_id = %s WHERE id = %s",
                    (mat, marca, modelo, cliente_id, veic["id"]),
                )
                conn.commit()
                win.destroy()
                self.carregar_dados()
            except Exception:
                lbl_erro.configure(text="Erro ao atualizar (Matrícula duplicada?)")
            finally:
                cursor.close()
                conn.close()

        ctk.CTkButton(win, text="Atualizar Veículo", fg_color="#F39C12", hover_color="#D68910", command=submeter).pack(pady=15)

    def confirmar_eliminar_processo(self, processo_id):
        win_confirm = ctk.CTkToplevel(self)
        win_confirm.title("Confirmar Eliminação")
        win_confirm.geometry("400x180")
        win_confirm.resizable(False, False)
        win_confirm.grab_set()

        ctk.CTkLabel(
            win_confirm,
            text="Tem a certeza que pretende eliminar\neste processo de forma definitiva?",
            font=("Arial", 13, "bold"),
            wraplength=360,
        ).pack(pady=(25, 20))
        f_btns = ctk.CTkFrame(win_confirm, fg_color="transparent")
        f_btns.pack()

        def apagar():
            conn = obter_conexao()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM processos WHERE id = %s", (processo_id,))
            conn.commit()
            cursor.close()
            conn.close()
            win_confirm.destroy()
            self.carregar_dados()

        ctk.CTkButton(f_btns, text="Sim", fg_color="#C0392B", width=90, command=apagar).pack(side="left", padx=10)
        ctk.CTkButton(f_btns, text="Cancelar", fg_color="gray", width=90, command=win_confirm.destroy).pack(side="left", padx=10)

    def eliminar_cliente(self, cliente):
        dialog = ConfirmarEliminacaoDialog(self, cliente["nome"])
        self.wait_window(dialog)
        if not dialog.opcao_escolhida:
            return

        conn = obter_conexao()
        cursor = conn.cursor()
        if dialog.opcao_escolhida == "apagar_cliente":
            cursor.execute("UPDATE veiculos SET cliente_id = NULL WHERE cliente_id = %s", (cliente["id"],))
            cursor.execute("DELETE FROM clientes WHERE id = %s", (cliente["id"],))
        elif dialog.opcao_escolhida == "apagar_tudo":
            cursor.execute("DELETE FROM clientes WHERE id = %s", (cliente["id"],))

        conn.commit()
        cursor.close()
        conn.close()
        self.carregar_dados()

    def eliminar_veiculo(self, veiculo_id):
        conn = obter_conexao()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM veiculos WHERE id = %s", (veiculo_id,))
        conn.commit()
        cursor.close()
        conn.close()
        self.carregar_dados()

    def modal_criar_conta(self):
        win = ctk.CTkToplevel(self)
        win.title("Criar Nova Conta")
        win.geometry("380x420")
        win.resizable(False, False)
        win.grab_set()

        ctk.CTkLabel(win, text="👥 Registar Utilizador", font=("Arial", 15, "bold")).pack(pady=12)
        e_user = ctk.CTkEntry(win, placeholder_text="Username (Único)")
        e_user.pack(fill="x", padx=20, pady=4)
        e_nome = ctk.CTkEntry(win, placeholder_text="Nome Completo")
        e_nome.pack(fill="x", padx=20, pady=4)
        e_pass = ctk.CTkEntry(win, placeholder_text="Palavra-passe de Acesso", show="•")
        e_pass.pack(fill="x", padx=20, pady=4)

        lbl_erro = ctk.CTkLabel(win, text="", text_color="red")
        e_pin = ctk.CTkEntry(win, placeholder_text="PIN Navbar Admin (4 dígitos)", show="•")

        def validar_pin_criar(event):
            if event.keysym in ["BackSpace", "Delete", "Left", "Right", "Tab"]:
                return
            txt = e_pin.get()
            if not txt:
                return
            if not txt.isdigit():
                e_pin.delete(0, "end")
                lbl_erro.configure(text="⚠️ O PIN só aceita números!")
            elif len(txt) > 4:
                e_pin.delete(0, "end")
                lbl_erro.configure(text="⚠️ Limite de 4 dígitos ultrapassado!")
            else:
                lbl_erro.configure(text="")

        e_pin.bind("<KeyRelease>", validar_pin_criar)

        def ao_mudar_tipo(escolha):
            if escolha == "admin":
                e_pin.pack(fill="x", padx=20, pady=4, after=combo_tipo)
            else:
                e_pin.pack_forget()
                e_pin.delete(0, "end")
                lbl_erro.configure(text="")

        combo_tipo = ctk.CTkOptionMenu(win, values=["user", "admin"], command=ao_mudar_tipo)
        combo_tipo.pack(fill="x", padx=20, pady=8)
        lbl_erro.pack(pady=2)

        def submeter():
            u = e_user.get().strip().lower()
            n = e_nome.get().strip()
            p = e_pass.get().strip()
            t = combo_tipo.get()
            pin = e_pin.get().strip() if t == "admin" else None

            if not u or not n or not p:
                lbl_erro.configure(text="Preencha os campos obrigatórios!")
                return
            if t == "admin" and (not pin or len(pin) != 4 or not pin.isdigit()):
                lbl_erro.configure(text="O PIN de Admin tem de ter exatamente 4 números!")
                return

            conn = obter_conexao()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO utilizadores (username, nome, pass, tipo_conta, pin_sidebar) VALUES (%s, %s, %s, %s, %s)",
                    (u, n, p, t, pin),
                )
                conn.commit()
                win.destroy()
                self.carregar_dados()
            except Exception:
                lbl_erro.configure(text="Erro: Username já existe no sistema!")
            finally:
                cursor.close()
                conn.close()

        ctk.CTkButton(win, text="Guardar Conta", fg_color="#27AE60", command=submeter).pack(pady=10)

    def modal_editar_conta(self, user):
        win = ctk.CTkToplevel(self)
        win.title(f"Editar Conta - @{user['username']}")
        win.geometry("380x380")
        win.resizable(False, False)
        win.grab_set()

        ctk.CTkLabel(win, text=f"Editar @{user['username']}", font=("Arial", 15, "bold")).pack(pady=12)
        e_nome = ctk.CTkEntry(win, placeholder_text="Nome Completo")
        e_nome.insert(0, user["nome"])
        e_nome.pack(fill="x", padx=20, pady=4)

        e_pass = ctk.CTkEntry(win, placeholder_text="Nova Palavra-passe (opcional)", show="•")
        e_pass.pack(fill="x", padx=20, pady=4)

        lbl_erro = ctk.CTkLabel(win, text="", text_color="red")
        e_pin = ctk.CTkEntry(win, placeholder_text="Novo PIN Navbar (4 dígitos - opcional)", show="•")

        def validar_pin_editar(event):
            if event.keysym in ["BackSpace", "Delete", "Left", "Right", "Tab"]:
                return
            txt = e_pin.get()
            if not txt:
                return
            if not txt.isdigit():
                e_pin.delete(0, "end")
                lbl_erro.configure(text="⚠️ O PIN só aceita números!")
            elif len(txt) > 4:
                e_pin.delete(0, "end")
                lbl_erro.configure(text="⚠️ Limite de 4 dígitos ultrapassado!")
            else:
                lbl_erro.configure(text="")

        e_pin.bind("<KeyRelease>", validar_pin_editar)

        def ao_mudar_tipo(escolha):
            if escolha == "admin":
                e_pin.pack(fill="x", padx=20, pady=4, after=combo_tipo)
            else:
                e_pin.pack_forget()
                e_pin.delete(0, "end")
                lbl_erro.configure(text="")

        combo_tipo = ctk.CTkOptionMenu(win, values=["user", "admin"], command=ao_mudar_tipo)
        combo_tipo.set(user["tipo_conta"])
        combo_tipo.pack(fill="x", padx=20, pady=8)

        if user["tipo_conta"] == "admin":
            e_pin.pack(fill="x", padx=20, pady=4, after=combo_tipo)

        lbl_erro.pack(pady=2)

        def submeter():
            n = e_nome.get().strip()
            p = e_pass.get().strip()
            pin = e_pin.get().strip()
            t = combo_tipo.get()

            if t == "admin" and pin and (len(pin) != 4 or not pin.isdigit()):
                lbl_erro.configure(text="O PIN deve conter exatamente 4 números!")
                return

            conn = obter_conexao()
            cursor = conn.cursor()
            query = "UPDATE utilizadores SET nome = %s, tipo_conta = %s"
            params = [n, t]

            if p:
                query += ", pass = %s"
                params.append(p)
            if t == "admin" and pin:
                query += ", pin_sidebar = %s"
                params.append(pin)
            elif t == "user":
                query += ", pin_sidebar = NULL"

            query += " WHERE id = %s"
            params.append(user["id"])

            cursor.execute(query, tuple(params))
            conn.commit()
            cursor.close()
            conn.close()
            win.destroy()
            self.carregar_dados()

        ctk.CTkButton(win, text="Atualizar", fg_color="#F39C12", command=submeter).pack(pady=10)

    def eliminar_conta(self, user_id):
        conn = obter_conexao()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM utilizadores WHERE id = %s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        self.carregar_dados()