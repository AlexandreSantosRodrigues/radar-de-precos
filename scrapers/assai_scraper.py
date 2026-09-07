import random
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper

class AssaiScraper(BaseScraper):
    """
    Scraper para coleta de preços do Assaí Atacadista.
    """

    BASE_URL = "https://www.assai.com.br"

    PRODUTOS_ALVO = [
        ("Arroz Tipo 1 Camil 5kg",          f"{BASE_URL}/arroz-agulhinha-tipo-1-camil-5kg"),
        ("Feijão Preto Combrasil 1kg",       f"{BASE_URL}/feijao-preto-combrasil-1kg"),
        ("Óleo de Soja Soya 900ml",          f"{BASE_URL}/oleo-composto-soya-900ml"),
        ("Leite Integral Italac 1L",         f"{BASE_URL}/leite-uht-integral-italac-1l"),
        ("Açúcar Refinado União 1kg",        f"{BASE_URL}/acucar-refinado-uniao-1kg"),
        ("Café Torrado e Moído Pilão 500g",  f"{BASE_URL}/cafe-torrado-e-moido-pilao-500g"),
        ("Macarrão Espaguete Piraquê 500g",  f"{BASE_URL}/macarrao-espaguete-piraque-500g"),
    ]

    def _parse_preco(self, texto: str) -> float | None:
        try:
            texto = texto.replace("R$", "").replace(".", "").replace(",", ".").strip()
            return float(texto)
        except (ValueError, AttributeError):
            return None

    def coletar_produto(self, nome: str, url: str) -> list | None:
        html = self.fetch(url)
        if not html:
            return None

        soup = BeautifulSoup(html, "lxml")

        seletores_preco = [
            "span.price",
            "div.product-price span",
            "span.sales span.value",
            "div.price-sales span",
            "[itemprop='price']",
        ]

        preco = None
        for seletor in seletores_preco:
            elemento = soup.select_one(seletor)
            if elemento:
                preco = self._parse_preco(elemento.get_text())
                if preco:
                    break

        if not preco:
            print(f"  ⚠️  Não encontrei preço para '{nome}'")
            return None

        return self.montar_linha(nome, preco, url_fonte=url)

    def _gerar_dados_simulados(self) -> list:
        """
        Assaí geralmente pratica preços levemente menores que Atacadão
        por ter maior escala. Isso é refletido nos preços base abaixo.
        """
        print("  🎲 Usando dados simulados para o Assaí (modo portfólio)")

        precos_base = {
            "Arroz Tipo 1 Camil 5kg":          (20.90, 18.90),
            "Feijão Preto Combrasil 1kg":       (7.49,  None),
            "Óleo de Soja Soya 900ml":          (5.29,  None),
            "Leite Integral Italac 1L":         (3.79,  None),
            "Açúcar Refinado União 1kg":        (3.69,  None),
            "Café Torrado e Moído Pilão 500g":  (16.90, None),
            "Macarrão Espaguete Piraquê 500g":  (4.49,  None),
        }

        linhas = []
        for nome, (preco_reg, preco_promo) in precos_base.items():
            variacao = random.uniform(0.95, 1.05)
            preco_final = round(preco_reg * variacao, 2)
            promo_final = round(preco_promo * variacao, 2) if preco_promo else None

            linha = self.montar_linha(nome, preco_final, promo_final, url_fonte=self.BASE_URL)
            if linha:
                linhas.append(linha)

        return linhas

    def coletar(self) -> list:
        print(f"\n🛒 Iniciando coleta: {self.nome_concorrente}")
        linhas = []

        for nome, url in self.PRODUTOS_ALVO:
            print(f"  🔍 Buscando: {nome}")
            linha = self.coletar_produto(nome, url)
            if linha:
                linhas.append(linha)

        if not linhas:
            print("  ⚠️  Coleta real falhou. Ativando modo simulado...")
            linhas = self._gerar_dados_simulados()

        print(f"  📦 Total coletado: {len(linhas)} produto(s)")
        return linhas
