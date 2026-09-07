import random
from scrapers.base_scraper import BaseScraper


class AssaiScraper(BaseScraper):

    BASE_URL = "https://www.assai.com.br"

    def _gerar_dados_simulados(self) -> list:
        print("  🎲 Usando dados simulados para o Assaí (modo portfólio)")
        linhas = []
        for sku in self.catalogo:
            nome = sku.get("produto", "")
            preco_proprio = float(str(sku.get("preco_proprio", 0)).replace(",", ".") or 0)
            if not nome or preco_proprio == 0:
                continue
            fator = random.uniform(0.80, 1.00)
            preco_concorrente = round(preco_proprio * fator, 2)
            linha = self.montar_linha(nome, preco_concorrente, url_fonte=self.BASE_URL)
            if linha:
                linhas.append(linha)
        return linhas

    def coletar(self) -> list:
        print(f"\n🛒 Iniciando coleta: {self.nome_concorrente}")
        linhas = self._gerar_dados_simulados()
        print(f"  📦 Total coletado: {len(linhas)} produto(s)")
        return linhas
