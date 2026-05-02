import numpy as np
import numpy_financial as npf
import requests
from bs4 import BeautifulSoup

def calcular_indicadores(dados):
    # Premissas de Alavancagem (Foco Caixa/Itaú)
    arremate = dados['valor_arremate']
    entrada = arremate * 0.05  # 5% de entrada
    financiamento = arremate * 0.95
    
    # Custos de Aquisição e Regularização
    itbi_cartorio = arremate * 0.05 
    custo_juridico = 5000 if dados['flag_despejo'] else 0
    buffer_tempo_despejo = 6 if dados['flag_despejo'] else 0
    
    # Capital Total Desembolsado (Skin in the game)
    capital_proprio = entrada + itbi_cartorio + dados['custo_reforma'] + custo_juridico
    
    # Tempo de Ciclo
    prazo_total = dados['tempo_obra'] + dados['tempo_venda'] + buffer_tempo_despejo
    
    # Venda Líquida (Descontando 6% de corretagem)
    venda_liquida = dados['valor_venda_estimado'] * 0.94
    
    # Lucro Real
    lucro_final = venda_liquida - financiamento - capital_proprio
    
    # ROI (Cash-on-Cash)
    roi_percentual = (lucro_final / capital_proprio) * 100 if capital_proprio > 0 else 0
    
    # TIR (Taxa Interna de Retorno)
    # Fluxo de caixa: -capital_proprio no início, + (venda_liquida - financiamento) no final
    cash_flows = [-capital_proprio, venda_liquida - financiamento]
    tir_percentual = npf.irr(cash_flows) * 100 if len(cash_flows) > 1 and capital_proprio > 0 else 0
    
    # Payback (Meses para retornar o capital investido)
    payback = prazo_total if lucro_final > 0 else float('inf')
    
    return {
        "lucro_real": lucro_final,
        "roi_coc": roi_percentual,
        "tir_percentual": tir_percentual,
        "payback_meses": payback,
        "capital_necessario": capital_proprio,
        "status": "VIÁVEL" if roi_percentual > 15 else "RISCO_ALTO"
    }

def extrair_dados_link(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        titulo = soup.title.string if soup.title else "Título não encontrado"
        # Placeholder: ajustar seletores para o site específico (ex: Zuk Leilões)
        # Exemplo: detalhes = soup.find('div', class_='property-details').text
        detalhes = "Implementar parsing específico para extrair: tipo, quartos, banheiros, vaga, localização."
        return {"titulo": titulo, "detalhes": detalhes}
    except Exception as e:
        return {"titulo": "Erro ao acessar o link", "detalhes": str(e)}

import streamlit as st

st.set_page_config(page_title="AuctionDev Partner", layout="wide")

st.sidebar.title("🏗️ Gestão de Ativos < 100k")
st.sidebar.markdown("---")

# Input de Dados
url_imovel = st.sidebar.text_input("Link do Leilão (URL)")
if st.sidebar.button("Extrair Dados do Link"):
    if url_imovel:
        dados_extraidos = extrair_dados_link(url_imovel)
        st.sidebar.write("**Título:**", dados_extraidos["titulo"])
        st.sidebar.write("**Detalhes:**", dados_extraidos["detalhes"])
    else:
        st.sidebar.warning("Insira um link válido.")
val_arremate = st.sidebar.number_input("Valor de Arremate (R$)", max_value=200000, value=80000)
val_venda = st.sidebar.number_input("VGV Estimado (R$)", value=150000)

with st.sidebar.expander("Custos e Prazos", expanded=True):
    reforma = st.number_input("Estimativa Reforma (R$)", value=15000)
    t_obra = st.slider("Tempo de Obra (Meses)", 1, 12, 2)
    t_venda = st.slider("Tempo de Revenda (Meses)", 1, 12, 4)
    despejo = st.checkbox("Imóvel Ocupado (Flag Despejo)")

# Regras de Negócio e Senso Crítico
if val_arremate > 100000:
    st.error("🚨 ESTRATÉGIA VIOLADA: Este ativo excede o teto de R$ 100.000,00.")
else:
    # Processamento
    dados_input = {
        "valor_arremate": val_arremate,
        "valor_venda_estimado": val_venda,
        "custo_reforma": reforma,
        "tempo_obra": t_obra,
        "tempo_venda": t_venda,
        "flag_despejo": despejo
    }
    
    res = calcular_indicadores(dados_input)
    
    # UI de Indicadores
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Lucro Líquido", f"R$ {res['lucro_real']:,.2f}")
    col2.metric("ROI (Cash-on-Cash)", f"{res['roi_coc']:.1f}%")
    col3.metric("TIR", f"{res['tir_percentual']:.1f}%")
    col4.metric("Tempo Ciclo", f"{res['payback_meses']} Meses")
    col5.metric("Desembolso Inicial", f"R$ {res['capital_necessario']:,.2f}")
    
    st.markdown("---")
    
    # Área de Análise Geográfica (Simulação de Scraping)
    st.subheader("📍 Inteligência de Mercado")
    st.info(f"Analisando ativo: {url_imovel}")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("**Busca de Comparativos (Manual Assistida)**")
        if st.button("Buscar Preços na Região"):
            # Aqui simulamos o link de busca automática para facilitar a vida do usuário
            st.write(f"🔍 [Clique aqui para ver imóveis similares no ZAP](https://www.zapimoveis.com.br/venda/imoveis/?onde=,Rio%20de%20Janeiro,Rio%20de%20Janeiro,,,,BR%3ERio%20de%20Janeiro%3ENull%3ERio%20de%20Janeiro,-22.9068,-43.1729&tipo=Apartamento)")
    
    with col_b:
        st.write("**Custos de Prefeitura e RGI**")
        itbi_estimado = val_arremate * 0.02
        st.write(f"ITBI Est. (2%): R$ {itbi_estimado:,.2f}")
        st.write(f"Escritura/Registro Est.: R$ 2.500,00")