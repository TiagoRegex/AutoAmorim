import base64
import os
import requests

# API Key da Resend
# Conta gratuita em resend.com para obter uma chave
RESEND_API_KEY = "re_INSIRA_A_SUA_CHAVE_AQUI"

def enviar_fatura_email(destinatario_email, nome_cliente, matricula, caminho_pdf):
    """
    Envia a fatura gerada por email através da API REST da Resend.
    """
    if not os.path.exists(caminho_pdf):
        return False, "Ficheiro PDF não encontrado para envio."

    if not destinatario_email or "@" not in destinatario_email:
        return False, "Endereço de e-mail do cliente inválido."

    # 1. Lê o PDF e converte para Base64 para enviar na API
    try:
        with open(caminho_pdf, "rb") as f:
            pdf_base64 = base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        return False, f"Erro ao ler PDF: {e}"

    nome_ficheiro = os.path.basename(caminho_pdf)

    # 2. Configura o payload JSON para a API REST
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }
    
    corpo_html = f"""
    <h2>Auto Amorim - Oficina Automóvel</h2>
    <p>Olá <strong>{nome_cliente}</strong>,</p>
    <p>A intervenção na sua viatura com a matrícula <strong>{matricula.upper()}</strong> foi concluída.</p>
    <p>Junto enviamos a fatura detalhada em formato PDF.</p>
    <br>
    <p>Obrigado pela sua preferência!<br><em>Auto Amorim</em></p>
    """

    payload = {
        "from": "Auto Amorim <onboarding@resend.dev>", # Domínio de testes gratuito da Resend
        "to": [destinatario_email],
        "subject": f"Fatura de Reparação - Veículo {matricula.upper()}",
        "html": corpo_html,
        "attachments": [
            {
                "filename": nome_ficheiro,
                "content": pdf_base64
            }
        ]
    }

    # 3. Disparo do pedido HTTP POST para a API externa
    try:
        resposta = requests.post(url, json=payload, headers=headers, timeout=10)
        if resposta.status_code in [200, 201]:
            return True, "E-mail com fatura enviado com sucesso!"
        else:
            return False, f"Erro da API ({resposta.status_code}): {resposta.text}"
    except Exception as ex:
        return False, f"Falha de conexão com a API de e-mail: {ex}"