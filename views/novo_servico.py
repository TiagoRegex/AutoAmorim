import customtkinter as ctk
from database.database import obter_conexao


class NovoServicoWindow(ctk.CTkToplevel):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.title("Auto Amorim - Novo Serviço")
        self.geometry("600x600")
        self.grab_set()

        lbl_titulo = ctk.CTkLabel(
            self, text="➕ Registar Novo Serviço", font=("Arial", 20, "bold")
        )
        lbl_titulo.pack(pady=15)

        # --- SECÇÃO: DADOS DO CLIENTE ---
        frame_cliente = ctk.CTkFrame(self)
        frame_cliente.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            frame_cliente,
            text="Dados do Cliente",
            font=("Arial", 14, "bold"),
        ).pack(anchor="w", padx=10, pady=5)

        self.entry_nome = ctk.CTkEntry(
            frame_cliente, placeholder_text="Nome Completo"
        )
        self.entry_nome.pack(fill="x", padx=10, pady=4)

        self.entry_telefone = ctk.CTkEntry(
            frame_cliente, placeholder_text="Telefone / Telemóvel"
        )
        self.entry_telefone.pack(fill="x", padx=10, pady=4)

        self.entry_nif = ctk.CTkEntry(frame_cliente, placeholder_text="NIF")
        self.entry_nif.pack(fill="x", padx=10, pady=4)

        self.entry_email = ctk.CTkEntry(frame_cliente, placeholder_text="E-mail (ex: cliente@email.pt)")
        self.entry_email.pack(fill="x", padx=10, pady=4)

        # --- SECÇÃO: DADOS DO VEÍCULO ---
        frame_veiculo = ctk.CTkFrame(self)
        frame_veiculo.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(
            frame_veiculo,
            text="Dados do Veículo",
            font=("Arial", 14, "bold"),
        ).pack(anchor="w", padx=10, pady=5)

        self.entry_matricula = ctk.CTkEntry(
            frame_veiculo, placeholder_text="Matrícula (ex: AA-00-AA)"
        )
        self.entry_matricula.pack(fill="x", padx=10, pady=4)

        self.entry_marca = ctk.CTkEntry(
            frame_veiculo, placeholder_text="Marca (ex: Renault)"
        )
        self.entry_marca.pack(fill="x", padx=10, pady=4)

        self.entry_modelo = ctk.CTkEntry(
            frame_veiculo, placeholder_text="Modelo (ex: Clio)"
        )
        self.entry_modelo.pack(fill="x", padx=10, pady=4)

        # Label Feedback
        self.lbl_status = ctk.CTkLabel(self, text="", font=("Arial", 12))
        self.lbl_status.pack(pady=5)

        btn_guardar = ctk.CTkButton(
            self,
            text="Guardar Serviço",
            font=("Arial", 14, "bold"),
            fg_color="#27AE60",
            hover_color="#1E8449",
            height=40,
            command=self.guardar_servico,
        )
        btn_guardar.pack(pady=10)

    def guardar_servico(self):
        nome = self.entry_nome.get().strip()
        telefone = self.entry_telefone.get().strip()
        nif = self.entry_nif.get().strip()
        email = self.entry_email.get().strip()
        matricula = self.entry_matricula.get().strip().upper()
        marca = self.entry_marca.get().strip()
        modelo = self.entry_modelo.get().strip()

        if not nome or not matricula:
            self.lbl_status.configure(
                text="Preencha pelo menos o Nome e a Matrícula!", text_color="red"
            )
            return

        conexao = obter_conexao()
        if not conexao:
            self.lbl_status.configure(
                text="Erro de ligação à BD!", text_color="red"
            )
            return

        try:
            cursor = conexao.cursor()

            # 1. Inserir Cliente com E-mail
            query_cliente = "INSERT INTO clientes (nome, telefone, nif, email) VALUES (%s, %s, %s, %s)"
            cursor.execute(query_cliente, (nome, telefone or None, nif or None, email or None))
            cliente_id = cursor.lastrowid

            # 2. Inserir Veículo associado ao Cliente
            query_veiculo = "INSERT INTO veiculos (cliente_id, matricula, marca, modelo) VALUES (%s, %s, %s, %s)"
            cursor.execute(
                query_veiculo, (cliente_id, matricula, marca, modelo)
            )

            conexao.commit()
            cursor.close()
            conexao.close()

            self.lbl_status.configure(
                text="Serviço registado com sucesso!", text_color="green"
            )
            self.after(1500, self.destroy)

        except Exception as err:
            self.lbl_status.configure(
                text=f"Erro ao guardar: {err}", text_color="red"
            )