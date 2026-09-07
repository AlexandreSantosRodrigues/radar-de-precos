import gspread
import json
import os
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_client():
    """Autentica e retorna o cliente do Google Sheets."""
    creds_json = os.environ.get("GOOGLE_CREDENTIALS")
    if not creds_json:
        raise ValueError("Variável GOOGLE_CREDENTIALS não encontrada!")
    
    creds_dict = json.loads(creds_json)
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)

def get_spreadsheet():
    """Retorna a planilha principal."""
    client = get_client()
    spreadsheet_id = os.environ.get("SPREADSHEET_ID")
    if not spreadsheet_id:
        raise ValueError("Variável SPREADSHEET_ID não encontrada!")
    return client.open_by_key(spreadsheet_id)

def get_sku_catalog():
    """Lê o catálogo de SKUs da planilha e retorna uma lista de dicionários."""
    ss = get_spreadsheet()
    
    # Busca a aba dinamicamente
    for sheet in ss.worksheets():
        if "cadastro" in sheet.title.lower() or "sku" in sheet.title.lower():
            records = sheet.get_all_records()
            return records
    
    raise ValueError("Aba de cadastro de SKUs não encontrada!")

def append_prices(rows: list):
    """Adiciona linhas novas na aba de preços dos concorrentes."""
    ss = get_spreadsheet()
    
    # Busca a aba dinamicamente
    for sheet in ss.worksheets():
        if "concorrente" in sheet.title.lower() or "preco" in sheet.title.lower():
            sheet.append_rows(rows, value_input_option="USER_ENTERED")
            print(f"✅ {len(rows)} linha(s) inserida(s) com sucesso!")
            return
    
    raise ValueError("Aba precos_concorrentes não encontrada!")
