import os
import pandas as pd
import streamlit as st

# Configuração da página
st.set_page_config(page_title="Simulador de Compras da Família", page_icon="🛒", layout="wide")

st.title("🛒 Simulador e Comparador de Compras de Supermercado")
st.markdown("Compare preços de supermercados locais, descubra onde a compra total fica mais barata e veja quanto economiza dividindo a lista.")

# Painel Lateral
st.sidebar.header("⚙️ Opções e Dados")
arquivo_enviado = st.sidebar.file_uploader("Carregar arquivo de preços (CSV/Excel)", type=["csv", "xlsx"])

st.sidebar.markdown("---")
st.sidebar.header("🔥 Destaques da Semana")
st.sidebar.info("**Mercado A:** Quarta do Hortifrúti (até 30% desc.)\n\n**Mercado B:** Sexta da Carne e Laticínios\n\n**Mercado C:** Fim de semana da Limpeza")

# Dados Padrão
dados_iniciais = {
    "Item": ["Arroz Tipo 1 5kg", "Feijão Carioca 1kg", "Leite Integral 1L", "Óleo de Soja 900ml", "Café Torrado 500g", "Detergente Líquido 500ml", "Sabão em Pó 1kg"],
    "Categoria": ["Grãos", "Grãos", "Laticínios", "Óleos", "Matinais", "Limpeza", "Limpeza"],
    "Quantidade": [2, 4, 12, 3, 2, 6, 2],
    "Mercado A (R$)": [24.90, 7.50, 4.89, 6.20, 18.90, 2.20, 14.50],
    "Mercado B (R$)": [26.50, 6.90, 4.50, 6.50, 17.50, 1.99, 15.20],
    "Mercado C (R$)": [23.90, 7.20, 4.79, 5.99, 19.00, 2.10, 13.90]
}

# Carregamento dos dados
if arquivo_enviado is not None:
    try:
        if arquivo_enviado.name.endswith(".csv"):
            df_base = pd.read_csv(arquivo_enviado)
        else:
            df_base = pd.read_excel(arquivo_enviado)
        st.sidebar.success("Ficheiro personalizado carregado!")
    except Exception as e:
        st.sidebar.error(f"Erro ao ler arquivo: {e}")
        df_base = pd.DataFrame(dados_iniciais)
elif os.path.exists("precos_atualizados.csv"):
    df_base = pd.read_csv("precos_atualizados.csv")
    st.sidebar.success("🤖 Dados do robô (`precos_atualizados.csv`) carregados!")
else:
    df_base = pd.DataFrame(dados_iniciais)
    st.sidebar.info("Usando lista de preços padrão.")

st.subheader("1. Tabela de Preços e Quantidades (Interativa)")
st.caption("Pode editar valores, adicionar novos produtos ou alterar quantidades diretamente na tabela abaixo.")

df_editado = st.data_editor(df_base, num_rows="dynamic", use_container_width=True)

# Processamento e Cálculos
if not df_editado.empty:
    colunas_mercado = [c for c in df_editado.columns if "(R$)" in c]
    if not colunas_mercado:
        colunas_mercado = [c for c in df_editado.columns if c not in ["Item", "Categoria", "Quantidade"]]

    if "Quantidade" in df_editado.columns:
        df_editado["Quantidade"] = pd.to_numeric(df_editado["Quantidade"], errors="coerce").fillna(1).astype(float)
    else:
        df_editado["Quantidade"] = 1.0

    for col in colunas_mercado:
        df_editado[col] = pd.to_numeric(df_editado[col], errors="coerce").fillna(0).astype(float)

    df_editado["Menor Preço Unid."] = df_editado[colunas_mercado].min(axis=1)

    def qual_melhor_mercado(row):
        menor = row["Menor Preço Unid."]
        if menor == 0:
            return "Sem dados"
        melhores = [col for col in colunas_mercado if row[col] == menor]
        return ", ".join(melhores).replace(" (R$)", "")

    df_editado["Melhor Opção"] = df_editado.apply(qual_melhor_mercado, axis=1)
    df_editado["Subtotal Otimizado (R$)"] = df_editado["Quantidade"] * df_editado["Menor Preço Unid."]

    # Totais Globais
    totais_mercados = {}
    for col in colunas_mercado:
        nome_limpo = col.replace(" (R$)", "")
        totais_mercados[nome_limpo] = (df_editado["Quantidade"] * df_editado[col]).sum()

    total_otimizado = df_editado["Subtotal Otimizado (R$)"].sum()
    totais_validos = [v for v in totais_mercados.values() if v > 0]
    menor_total_unico = min(totais_validos) if totais_validos else 0
    economia = (menor_total_unico - total_otimizado) if menor_total_unico > total_otimizado else 0.0

    # Resumo visual (KPIs)
    st.subheader("2. Resumo Comparativo")
    cols = st.columns(len(totais_mercados) + 1)
    
    idx = 0
    for mercado, total in totais_mercados.items():
        cols[idx].metric(label=f"Total no {mercado}", value=f"R$ {total:.2f}")
        idx += 1
        
    delta_txt = f"-R$ {economia:.2f} de Poupança" if economia > 0 else "0.00"
    cols[-1].metric(label="Total Dividido (Economia Máxima)", value=f"R$ {total_otimizado:.2f}", delta=delta_txt, delta_color="normal")

    # Gráfico Comparativo
    st.subheader("3. Gráfico de Custos Totais")
    dados_grafico = {
        "Mercado": list(totais_mercados.keys()) + ["Compra Dividida"],
        "Custo Total (R$)": list(totais_mercados.values()) + [total_otimizado]
    }
    df_chart = pd.DataFrame(dados_grafico).set_index("Mercado")
    st.bar_chart(df_chart)

    # Guia de Compras
    st.subheader("4. Guia Detalhado de Onde Comprar Cada Item")
    colunas_exibicao = ["Item", "Quantidade", "Melhor Opção", "Menor Preço Unid.", "Subtotal Otimizado (R$)"]
    if "Categoria" in df_editado.columns:
        colunas_
