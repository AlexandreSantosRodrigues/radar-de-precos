import re
from rapidfuzz import fuzz, process

def normalizar_nome(nome: str) -> str:
    """Limpa e padroniza o nome de um produto para comparação."""
    if not nome:
        return ""
    nome = nome.lower()
    substituicoes = {
        'á':'a','à':'a','ã':'a','â':'a',
        'é':'e','ê':'e','í':'i','ó':'o',
        'ô':'o','õ':'o','ú':'u','ç':'c'
    }
    for orig, dest in substituicoes.items():
        nome = nome.replace(orig, dest)
    nome = re.sub(r'[^a-z0-9\s]', ' ', nome)
    nome = re.sub(r'\s+', ' ', nome).strip()
    return nome

def encontrar_sku(nome_produto: str, catalogo: list, threshold: int = 80) -> dict | None:
    """
    Recebe o nome de um produto scraped e tenta casar com o catálogo de SKUs.
    
    Args:
        nome_produto: Nome do produto coletado no scraping
        catalogo: Lista de dicionários vinda do get_sku_catalog()
        threshold: Pontuação mínima de similaridade (0-100). 80 é um bom padrão.
    
    Returns:
        O dicionário do SKU correspondente, ou None se não encontrar.
    """
    if not nome_produto or not catalogo:
        return None
    
    nome_normalizado = normalizar_nome(nome_produto)
    
    nomes_catalogo = [normalizar_nome(str(sku.get("produto", ""))) for sku in catalogo]
    
    resultado = process.extractOne(
        nome_normalizado,
        nomes_catalogo,
        scorer=fuzz.token_sort_ratio  
    )
    
    if resultado is None:
        return None
    
    nome_match, score, indice = resultado
    
    if score >= threshold:
        print(f"  ✅ Match: '{nome_produto}' → '{catalogo[indice]['produto']}' (score: {score})")
        return catalogo[indice]
    else:
        print(f"  ⚠️  Sem match para: '{nome_produto}' (melhor score: {score})")
        return None
