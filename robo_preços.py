import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Lista de produtos que a sua família quer monitorizar
LISTA_DE_COMPRAS = [
    "Arroz 5kg",
    "Feijão Carioca 1kg",
    "Leite Integral 1L",
    "Óleo de Soja 900ml",
    "Café 500g",
    "Detergente 500ml",
    "Sabão em Pó 1kg"
]

# Função para procurar preços num e-commerce de supermercado (Exemplo genérico)
def buscar_preco_mercado(produto, url_busca, seletor_nome, seletor_preco):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, AppleWebKit/537.36) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # Monta a URL de pesquisa com o nome do produto
    url = f"{url_busca}{produto}"
    
    try:
        resposta = requests.get(url, headers=headers, timeout=10)
        if resposta.status_code == 200:
            soup = BeautifulSoup(resposta.content, "html.parser")
            
            # Encontra o primeiro item correspondente na página
            item_nome = soup.select_one(seletor_nome)
            item_preco = soup.select_one(seletor_preco)
            
            if item_nome and item_preco:
                # Limpa o texto do preço e converte para número decimal
                preco_texto = item_preco.get_text().replace("R$", "").replace(".", "").replace(",", ".").strip()
                return float(preco_texto)
    except Exception as e:
        print(f"Erro ao buscar {produto}: {e}")
        
    return None

def executar_robo():
    print("🤖 Robô iniciando a coleta de preços nos supermercados...")
    
    resultados = []
    
    for item in LISTA_DE_COMPRAS:
        print(f"Pesquisando: {item}...")
        
        # Exemplo de configuração de busca para diferentes sites
        # Nota: Os seletores CSS (seletor_nome e seletor_preco) mudam conforme o site de cada mercado
        preco_mercado_a = buscar_preco_mercado(
            produto=item, 
            url_busca="https://exemplo-mercado-a.com.br/busca?q=", 
            seletor_nome=".product-title", 
            seletor_preco=".product-price"
        )
        
        preco_mercado_b = buscar_preco_mercado(
            produto=item, 
            url_busca="https://exemplo-mercado-b.com.br/search?term=", 
            seletor_nome=".item-name", 
            seletor_preco=".price-value"
        )
        
        # Adiciona pausa curta para não sobrecarregar os servidores dos mercados
        time.sleep(1)
        
        resultados.append({
            "Item": item,
            "Mercado A (R$)": preco_mercado_a if preco_mercado_a else 0.0,
            "Mercado B (R$)": preco_mercado_b if preco_mercado_b else 0.0
        })
    
    # Salva o resultado num arquivo CSV
    df = pd.DataFrame(resultados)
    df.to_csv("precos_atualizados.csv", index=False)
    print("✅ Pesquisa concluída! Ficheiro 'precos_atualizados.csv' gerado com sucesso.")

if __name__ == "__main__":
    executar_robo()
