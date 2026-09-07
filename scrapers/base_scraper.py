import requests
import time
import random
from abc import ABC, abstractmethod
from datetime import date
from utils.matcher import encontrar_sku

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

class BaseScraper(ABC):
    """
    Classe base abstrata para todos os scrapers de concorrentes.
    Todo scraper novo deve herdar desta classe e implementar os métodos abstratos.
    """

    def __init__(self, nome_concorrente: str, catalogo: list):
        self.nome_concorrente = nome_concorrente
        self.catalogo = catalogo
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def fetch(self, url: str, tentativas: int = 3) -> str | None:
        """Faz a requisição HTTP com retry automático em caso de falha."""
        for tentativa in range(1, tentativas + 1):
            try:
                print(f"  🌐 Tentativa {tentativa}: {url}")
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                time.sleep(random.uniform(1, 3))
                return response.text
            except requests.RequestException as e:
                print(f"  ❌ Erro na tentativa {tentativa}: {e}")
                if tentativa < tentativas:
                    time.sleep(5)  
        return None

    def montar_linha(self, produto_nome: str, preco: float, preco_promo: float = None, url_fonte: str = "") -> list | None:
        """
        Casa o produto com o SKU e monta a linha no formato da planilha.
        Retorna None se não encontrar o SKU correspondente.
        """
        sku = encontrar_sku(produto_nome, self.catalogo)
        if not sku:
            return None

        hoje = date.today().isoformat()
        em_promocao = preco_promo is not None and preco_promo < preco
        concorrente_upper = self.nome_concorrente.upper().replace(" ", "_")[:10]
        id_registro = f"{hoje}_{sku['sku_id']}_{concorrente_upper}"

        return [
            id_registro,
            hoje,
            sku["sku_id"],
            self.nome_concorrente,
            preco,
            preco_promo or "",
            em_promocao,
            "scraping",
            url_fonte,
            "alta"
        ]

    @abstractmethod
    def coletar(self) -> list:
        """
        Método principal de coleta. Deve ser implementado por cada scraper filho.
        Deve retornar uma lista de linhas prontas para inserir na planilha.
        """
        pass
