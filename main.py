import sys
from datetime import datetime
from utils.gsheets_client import get_sku_catalog, append_prices, get_spreadsheet
from scrapers.atacadao_scraper import AtacadaoScraper
from scrapers.assai_scraper import AssaiScraper

def registrar_log(status: str, registros: int, detalhes: str):
    """Salva o resultado da execução na aba log_execucoes."""
    try:
        ss = get_spreadsheet()
        for sheet in ss.worksheets():
            if "log" in sheet.title.lower():
                agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sheet.append_row([agora, "scraping", status, registros, detalhes])
                return
    except Exception as e:
        print(f"⚠️  Não foi possível salvar o log: {e}")

def main():
    print("=" * 50)
    print("🚀 RADAR DE PREÇOS — Iniciando coleta automatizada")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    print("\n📋 Carregando catálogo de SKUs...")
    try:
        catalogo = get_sku_catalog()
        print(f"   {len(catalogo)} SKU(s) encontrado(s) no catálogo.")
    except Exception as e:
        print(f"❌ Erro ao carregar catálogo: {e}")
        registrar_log("erro", 0, f"Falha ao carregar catálogo: {e}")
        sys.exit(1)

    scrapers = [
        AtacadaoScraper(nome_concorrente="Atacadão", catalogo=catalogo),
        AssaiScraper(nome_concorrente="Assaí",       catalogo=catalogo),
    ]

    todas_as_linhas = []
    for scraper in scrapers:
        try:
            linhas = scraper.coletar()
            todas_as_linhas.extend(linhas)
        except Exception as e:
            print(f"❌ Erro no scraper {scraper.nome_concorrente}: {e}")

    if todas_as_linhas:
        print(f"\n💾 Salvando {len(todas_as_linhas)} registro(s) na planilha...")
        try:
            append_prices(todas_as_linhas)
            registrar_log("sucesso", len(todas_as_linhas), "Coleta concluída com sucesso.")
        except Exception as e:
            print(f"❌ Erro ao salvar na planilha: {e}")
            registrar_log("erro", 0, f"Falha ao salvar: {e}")
            sys.exit(1)
    else:
        msg = "Nenhum dado coletado."
        print(f"\n⚠️  {msg}")
        registrar_log("aviso", 0, msg)

    print("\n✅ Coleta finalizada com sucesso!")
    print("=" * 50)

if __name__ == "__main__":
    main()
