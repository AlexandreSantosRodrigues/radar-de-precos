import random
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper

class AtacadaoScraper(BaseScraper):
    """
    Scraper para coleta de preços do Atacadão.
    Tenta coletar dados reais via HTTP. Em caso de bloqueio ou erro,
    usa dados simulados para garantir continuidade do pipeline.
    """

    BASE_URL = "https://www.atacadao.com.br"

    PRODUTOS_ALVO = [
        ("Arroz Tipo 1 Camil 5kg",   f"{BASE_URL}/arroz-branco-tipo-1-camil-5kg"),
        ("Feijão Preto Combrasil 1kg", f"{BASE_URL}/feijao-preto-combrasil-1kg"),
        ("Óleo de Soja Soya 900ml",   f"{BASE_URL}/oleo-de-soja-soya-900ml"),
        ("Leite Integral Italac 1L",  f"{BASE_URL}/leite-integral-italac-12l"),
        ("Açúcar Refinado União 1kg", f"{BASE_URL}/acucar-refinado-uniao-1kg"),
        ("Café Torrado e Moído Pilão 500g", f"{BASE_URL}/cafe-pilao-500g"),
    ]

    def _parse_preco(self, texto: str) -> float | None:
        """Converte texto de preço (ex: 'R$ 22,90') para float (22.90)."""
        try:
            texto = texto.replace("R$", "").replace(".", "").replace(",", ".").strip()
            return float(texto)
        except (ValueError, AttributeError):
            return None

    def coletar_produto(self, nome: str, url: str) -> list | None:
        """Tenta coletar o preço de um produto específico."""
        html = self.fetch(url)
        if not html:
            return None

        soup = BeautifulSoup(html, "lxml")

        
        seletores_preco = [
            "span.price",
            "span.product-price",
            "div.price-box span.price",
            "[data-price-type='finalPrice'] span.price",
            "span.special-price .price",
        ]

        preco = None
        for seletor in seletores_preco:
            elemento = soup.select_one(seletor)
            if elemento:
                preco = self._parse_preco(elemento.get_text())
                if preco:
                    break

        if not preco:
            print(f"  ⚠️  Não encontrei preço para '{nome}' em {url}")
            return None

        return self.montar_linha(nome, preco, url_fonte=url)

    def _gerar_dados_simulados(self) -> list:
        """
        Gera dados simulados realistas para demonstração do pipeline.
        Usado quando o site bloqueia o scraping ou está indisponível.
        Os preços são baseados em variações realistas de mercado.
        """
        print("  🎲 Usando dados simulados para o Atacadão (modo portfólio)")

        precos_base = {
            "Arroz Tipo 1 Camil 5kg":         (21.90, 19.90),
            "Feijão Preto Combrasil 1kg":      (7.90,  None),
            "Óleo de Soja Soya 900ml":         (5.49,  None),
            "Leite Integral Italac 1L":        (3.99,  None),
            "Açúcar Refinado União 1kg":       (3.89,  None),
            "Café Torrado e Moído Pilão 500g": (17.90, 15.90),
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
        """Método principal: tenta scraping real, fallback para simulado."""
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
