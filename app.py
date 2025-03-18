import streamlit as st
import pandas as pd
import numpy as np
import os
import datetime
import json
import boto3
import gspread
import traceback
from oauth2client.service_account import ServiceAccountCredentials
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
from io import BytesIO
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

# Configurações da página
st.set_page_config(
    page_title="METAS 2025 - Innovatis",
    page_icon="📈",
    layout="wide"
)

# Importa a fonte Poppins do Google Fonts
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
        
        /* Aplica a fonte Poppins a todos os componentes */
        [class^=st-emotion] {
            font-family: 'Poppins', sans-serif !important;
        }

        /* Se necessário, você pode especificar um estilo diferente para o corpo */
        body * {
            font-family: 'Poppins', sans-serif !important;
        }
        
        /* Centralizar o rodapé */
        footer {
            text-align: center !important;
        }
        
        /* Estilo para o rodapé personalizado */
        .footer-custom {
            text-align: center;
            padding: 10px;
            font-size: 14px;
            color: #666;
            margin-top: 30px;
        }
        
        /* Container para os cards - ajustado para largura máxima */
        .metrics-container {
            display: flex;
            flex-direction: row;
            justify-content: flex-start;
            gap: 15px;  /* Reduzido o gap entre cards */
            margin-bottom: 20px;
            max-width: 800px;  /* Largura máxima do container */
            margin-left: auto;
            margin-right: auto;
        }
        
        /* Estilo para os cards de métricas - ajustado tamanho */
        .metric-card {
            background-color: white;
            padding: 15px;  /* Padding padrão */
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            flex: 1;
            min-width: 200px;  /* Aumentar largura mínima */
            max-width: 250px;  /* Aumentar largura máxima */
            display: flex;      /* Flexbox para alinhamento */
            flex-direction: column; /* Coluna para título e valor */
        }
        
        /* Estilo para o título da métrica */
        .metric-title {
            color: #333333;
            font-size: 14px;
            margin-bottom: 5px;
            font-weight: 400;
        }
        
        /* Ajuste para o valor principal */
        .metric-value {
            font-size: 2em;  /* Tamanho da fonte */
            color: #333;
            font-weight: 500;
            margin-right: 8px;
            display: inline-block;
            align-self: flex-start; /* Alinhamento à esquerda */
        }
        
        /* Ajuste para a variação */
        .metric-variation {
            font-size: 1.5em;  /* Tamanho da fonte */
            font-weight: bold;
            display: inline-block;
            padding: 4px 8px;
            border-radius: 5px;
            margin-left: 8px;
            align-self: flex-end; /* Alinhamento à direita */
        }
        
        .variation-positive {
            color: #2E8B57;
            background-color: #E8F5E9;
        }
        
        .variation-negative {
            color: #B71C1C;
            background-color: #FFEBEE;
        }
        
        /* Ajuste para as seções */
        .section-title {
            font-size: 1.5em;
            color: #333;
            margin: 20px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
            max-width: 800px;  /* Largura máxima igual ao container */
            margin-left: auto;
            margin-right: auto;
        }
        
        /* Container principal para centralizar todo o conteúdo */
        .content-container {
            max-width: 1000px;
            margin-left: auto;
            margin-right: auto;
            padding: 0 20px;
        }
            

    </style>
""", unsafe_allow_html=True)

# Configurações de cores
COLORS = {
    "fundacoes": "#FFD966",  # Amarelo
    "ifes": "#9BC2E6",       # Azul claro
    "oportunidades": "#FFD966",  # Amarelo
    "funil_vendas": "#9BC2E6",   # Azul claro
    "instagram": "#FFD966",      # Amarelo
    "website": "#9BC2E6",        # Azul claro
    "meta": "#7030A0",           # Roxo
    "variacao_positiva": "#70AD47",  # Verde
    "variacao_negativa": "#C00000",  # Vermelho
    "background": "#FFFFFF",     # Branco
    "text": "#000000"            # Preto
}

# Importar arquivo de configuração
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Criar o objeto de autenticação
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

authenticator.login()

# Verificação do status da autenticação
if st.session_state["authentication_status"]:
    # Removendo a mensagem de boas-vindas e o botão de logout daqui
    pass  # Adicionando pass para manter a estrutura do bloco if
elif st.session_state["authentication_status"] is False:
    st.error('Usuário/Senha inválido')
elif st.session_state["authentication_status"] is None:
    st.markdown("""
        <style>
        div[data-testid="stAppViewContainer"] {
            max-width: 600px;
            margin: auto;
        }
        </style>
    """, unsafe_allow_html=True)
    st.warning('Por Favor, utilize seu usuário e senha!')

# O resto do código só executa se autenticado
if st.session_state["authentication_status"]:


    # Configuração do AWS S3
    s3 = boto3.resource(
        service_name='s3',
        region_name='us-east-2',
        aws_access_key_id='AKIA47GB733YQT2N7HNC',
        aws_secret_access_key='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'
    )

    # Função para carregar o logo da empresa
    @st.cache_data
    def load_logo():
        try:
            logo_obj = s3.Bucket('jsoninnovatis').Object('Logo.png').get()
            logo_data = logo_obj['Body'].read()
            return Image.open(BytesIO(logo_data))
        except Exception as e:
            st.error(f"Erro ao carregar o logo: {str(e)}")
            return None

    # Função para carregar dados da planilha
    @st.cache_data(ttl=3600)  # Cache por 1 hora
    def carregar_planilha():
        try:
            # Baixar o arquivo JSON diretamente do S3
            obj = s3.Bucket('jsoninnovatis').Object('chave2.json').get()
            # Ler o conteúdo do objeto e decodificar para string, em seguida converter para dict
            creds_json = json.loads(obj['Body'].read().decode('utf-8'))
            # Definir o escopo de acesso para Google Sheets e Google Drive
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            # Criar as credenciais a partir do JSON baixado
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
            client = gspread.authorize(creds)
            # Acessar a planilha do Google
            planilha = client.open("INDICADORES DE CRESCIMENTO").worksheet("INDICADORES")
            
            # Obtenha todos os valores da planilha (incluindo cabeçalhos)
            valores = planilha.get_all_values()
            
            if not valores:
                st.error("A planilha está vazia!")
                return {}
            
            # Extrair as diferentes seções da planilha conforme o anexo
            
            # Nova seção: Meta de Faturamento (Linhas 23-24)
            if len(valores) >= 24:
                # Linha 23 (índice 22) contém os cabeçalhos: META DE FATURAMENTO, ATUAL, META 1 2025, META 2 2025, META 3 2025
                faturamento_headers = valores[22][1:6]  # Colunas B-F
                
                # Linha 24 (índice 23) contém os dados: FATURAMENTO e valores
                faturamento_data = []
                faturamento_data.append(valores[23][1:6])  # Colunas B-F
                
                # Criar DataFrame com os nomes das colunas corretos
                df_faturamento = pd.DataFrame(faturamento_data, 
                                        columns=['META DE FATURAMENTO', 'ATUAL', 'META 1 2025', 'META 2 2025', 'META 3 2025'])
                
                # Converter colunas numéricas
                for col in df_faturamento.columns:
                    if col != 'META DE FATURAMENTO':  # Não converter a coluna de nomes
                        # Remover R$ e converter para numérico
                        df_faturamento[col] = df_faturamento[col].apply(
                            lambda x: float(str(x).replace('R$', '').replace('.', '').replace(',', '.').strip()) if isinstance(x, str) and x else 0)
            else:
                df_faturamento = pd.DataFrame()
            
            # Nova seção: Funil de Vendas (Linhas 26-32)
            if len(valores) >= 32:
                # Linha 26 (índice 25) contém os cabeçalhos: FUNIL, Qtd., Taxa de Conversão, Tempo médio
                funil_headers = valores[25][1:5]  # Colunas B-E
                
                # Linhas 27-32 (índices 26-31) contêm os dados das etapas do funil
                funil_data = []
                for i in range(26, 32):
                    # Colunas B-E contêm os valores
                    funil_data.append(valores[i][1:5])
                
                # Criar DataFrame com os nomes das colunas corretos
                df_funil = pd.DataFrame(funil_data, 
                                    columns=['Etapa', 'Quantidade', 'Taxa de Conversão', 'Tempo médio'])
                
                # Converter colunas numéricas
                df_funil['Quantidade'] = pd.to_numeric(df_funil['Quantidade'], errors='coerce').fillna(0).astype(int)
                
                # Converter taxa de conversão para formato decimal
                df_funil['Taxa de Conversão'] = df_funil['Taxa de Conversão'].apply(
                    lambda x: float(str(x).replace('%', '').strip()) / 100 if isinstance(x, str) and x and x != '-' else x
                )
                
                # Converter tempo médio para numérico
                df_funil['Tempo médio'] = pd.to_numeric(df_funil['Tempo médio'], errors='coerce').fillna(0).astype(int)
            else:
                df_funil = pd.DataFrame()
            
            # Seção 1: Métricas de Parceiros (Linhas 3-5)
            if len(valores) >= 5:
                # Linha 3 (índice 2) contém os cabeçalhos: Métricas de Parceiros, Qtd. 2024, Qtd. 2025, META 2025
                metricas_parceiros_headers = valores[2][1:5]  # Colunas B-E
                
                # Linhas 4-5 (índices 3-4) contêm os dados: FUNDAÇÕES e IFES
                metricas_parceiros_data = []
                for i in range(3, 5):
                    # Primeira coluna (B) contém o nome, colunas C-E contêm os valores
                    row_data = [valores[i][1]]  # Nome (coluna B)
                    row_values = valores[i][2:5]  # Valores (colunas C-E)
                    metricas_parceiros_data.append(row_data + row_values)
                
                # Criar DataFrame com os nomes das colunas corretos
                df_metricas = pd.DataFrame(metricas_parceiros_data, 
                                        columns=['Métricas de Parceiros', 'Qtd. 2024', 'Qtd. 2025', 'META 2025'])
                
                # Converter colunas numéricas
                for col in df_metricas.columns:
                    if col != 'Métricas de Parceiros':  # Não converter a coluna de nomes
                        df_metricas[col] = pd.to_numeric(df_metricas[col], errors='ignore')
            else:
                df_metricas = pd.DataFrame()
            
            # Seção 2: Desenvolvimento de Plataformas (Linhas 7-10)
            if len(valores) >= 12:
                plataformas_headers = ['Desenvolvimento de plataformas', 'Andamento (%)', 'Feedback']
                plataformas_data = []
                for i in range(7, 12):  # Certifique-se de que o índice está correto
                    plataformas_data.append([valores[i][1], valores[i][2], valores[i][3]])  # Add feedback column
                
                df_plataformas = pd.DataFrame(plataformas_data, columns=plataformas_headers)
                
                if 'Andamento (%)' in df_plataformas.columns:
                    df_plataformas['Andamento (%)'] = df_plataformas['Andamento (%)'].apply(
                        lambda x: float(str(x).replace('%', '').strip()) / 100 if isinstance(x, str) and x else 0
                    )
            else:
                df_plataformas = pd.DataFrame()
            
            # Seção 3: Captação Digital (Linhas 11-13)
            if len(valores) >= 16:
                # Linha 13 (índice 13) contém os cabeçalhos para a nova estrutura
                captacao_headers = valores[13][1:9]  # Colunas B-I (8 colunas)
                
                # Linhas 14-16 (índices 14-15) contêm os dados: INSTAGRAM (atual e passado)
                captacao_data = []
                for i in range(14, 16):
                    # Coluna B contém o nome, colunas C-I contêm os valores
                    captacao_data.append(valores[i][1:9])
                
                # Criar DataFrame com os nomes das colunas corretos - nova estrutura
                df_captacao = pd.DataFrame(captacao_data, 
                                        columns=['Captação Digital', 'Impressões', 'Alcance', 
                                               'Visitas no Perfil', 'Cliques no link da bio', 
                                               'Taxa de engajamento', 'Top conteudo 1', 'Top conteudo 2'])
                
                # Converter colunas numéricas e porcentagens
                for col in df_captacao.columns:
                    if col == 'Taxa de engajamento':
                        df_captacao[col] = df_captacao[col].apply(
                            lambda x: float(str(x).replace('%', '').strip()) / 100 if isinstance(x, str) and x and x != '-' else 0
                        )
                    elif col not in ['Captação Digital', 'Top conteudo 1', 'Top conteudo 2']:  # Não converter colunas de texto
                        df_captacao[col] = pd.to_numeric(df_captacao[col], errors='coerce')
                        # Substituir NaN por 0
                        df_captacao[col] = df_captacao[col].fillna(0)
            else:
                df_captacao = pd.DataFrame()
            
            st.success("Dados carregados com sucesso!")
            
            # Retornar um dicionário com os DataFrames
            return {
                'faturamento': df_faturamento,
                'funil': df_funil,
                'metricas_parceiros': df_metricas,
                'desenvolvimento_plataformas': df_plataformas,
                'captacao_digital': df_captacao
            }
        
        except Exception as e:
            st.error(f"Erro ao carregar planilha: {str(e)}")
            st.error("Detalhes do erro:")
            st.code(traceback.format_exc())
            return {}

    # Funções de visualização
    def create_metric_card(title, value, previous_value=None, meta=None, is_percentage=False, color=None):
        """
        Cria um card de métrica com título, valor atual e variação.
        """
        # Formatar valor
        if is_percentage:
            formatted_value = f"{value:.1%}"
        else:
            formatted_value = f"{value:,}".replace(",", ".")
        
        # Calcular variação
        if previous_value is not None and previous_value != 0:
            delta = ((value - previous_value) / previous_value) * 100
            delta_text = f"{delta:.1f}%"
        else:
            delta_text = None
        
        # Criar card
        st.metric(
            label=title,
            value=formatted_value,
            delta=delta_text,
            delta_color="normal"
        )
        
        # Adicionar meta se fornecida
        if meta is not None:
            if is_percentage:
                formatted_meta = f"Meta: {meta:.1%}"
            else:
                formatted_meta = f"Meta: {meta:,}".replace(",", ".")
            
            st.caption(formatted_meta)

    def create_progress_bar(title, value, max_value, color=None):
        """
        Cria uma barra de progresso.
        """
        # Calcular porcentagem
        if max_value > 0:
            percent = min(value / max_value, 1.0)
        else:
            percent = 0
        
        # Criar título com valor e meta
        st.caption(f"{title}: {value} de {max_value} ({percent:.1%})")
        
        # Criar barra de progresso
        st.progress(percent)

    def create_gauge_chart(title, value, min_value=0, max_value=100, is_percentage=True, color=None):
        """
        Cria um gráfico de medidor (gauge) com estilo minimalista.
        """
        # Formatar valor para exibição
        if is_percentage:
            display_value = value * 100 if value <= 1 else value
            text_value = f"{display_value:.1f}%"
        else:
            display_value = value
            text_value = f"{value:,}".replace(",", ".")
        
        # Definir cor baseado no valor atual
        if display_value < 33.4:
            gauge_color = '#FF4B4B'  # Vermelho
        elif display_value < 66.7:
            gauge_color = '#FFA500'  # Laranja
        else:
            gauge_color = '#2E8B57'  # Verde mais natural (Sea Green)
        
        # Criar gráfico
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=display_value,
            domain={'x': [0.1, 0.9], 'y': [0.15, 0.85]},
            title={
                'text': title,
                'font': {'size': 16, 'color': '#333333'},
                'align': 'left'
            },
            gauge={
                'axis': {
                    'range': [min_value, max_value],
                    'tickwidth': 0,
                    'tickcolor': "rgba(0,0,0,0)",
                    'ticktext': ['0%', '100%'],
                    'tickvals': [0, 100],
                    'tickmode': 'array',
                    'tickfont': {'size': 12, 'color': '#333333'},
                    'tickangle': 0,
                    'showticklabels': True,
                    'visible': True
                },
                'bar': {
                    'color': gauge_color,
                    'thickness': 0.6
                },
                'bgcolor': "white",
                'borderwidth': 0,
                'steps': [
                    {'range': [0, max_value], 'color': 'rgba(0, 0, 0, 0.1)'}
                ]
            },
            number={
                'font': {'size': 50, 'color': '#333333', 'family': 'Arial'},
                'suffix': "%",
            }
        ))
        
        fig.update_layout(
            height=385,
            margin=dict(l=40, r=40, t=30, b=20),
            paper_bgcolor="white",
            plot_bgcolor="white",
            showlegend=False,
            xaxis={'showgrid': False, 'zeroline': False},
            yaxis={'showgrid': False, 'zeroline': False}
        )
        
        st.plotly_chart(fig, use_container_width=True)

    def create_comparison_chart(title, categories, values_2024, values_2025, metas_2025=None, color_2024=None, color_2025=None, color_meta=None):
        """
        Cria um gráfico de barras para comparação entre anos.
        """
        if color_2024 is None:
            color_2024 = "#1F77B4"  # Azul
        if color_2025 is None:
            color_2025 = "#FF7F0E"  # Laranja
        if color_meta is None:
            color_meta = COLORS.get("meta", "#7030A0")  # Roxo
        
        fig = go.Figure()
        
        # Adicionar barras para 2024
        fig.add_trace(go.Bar(
            x=categories,
            y=values_2024,
            name="2024",
            marker_color=color_2024
        ))
        
        # Adicionar barras para 2025
        fig.add_trace(go.Bar(
            x=categories,
            y=values_2025,
            name="2025",
            marker_color=color_2025
        ))
        
        # Adicionar linha para metas de 2025, se fornecidas
        if metas_2025 is not None:
            fig.add_trace(go.Scatter(
                x=categories,
                y=metas_2025,
                mode="lines+markers",
                name="Meta 2025",
                marker=dict(color=color_meta, size=10),
                line=dict(color=color_meta, width=2, dash="dot")
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Categoria",
            yaxis_title="Quantidade",
            barmode="group",
            height=400,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=10, r=10, t=50, b=10),
            font={'family': "Poppins"}
        )
        
        st.plotly_chart(fig, use_container_width=True)

    def create_variation_chart(title, categories, values, variations, color_positive=None, color_negative=None):
        """
        Cria um gráfico de barras com variações.
        """
        if color_positive is None:
            color_positive = COLORS.get("variacao_positiva", "#70AD47")  # Verde
        if color_negative is None:
            color_negative = COLORS.get("variacao_negativa", "#C00000")  # Vermelho
        
        colors = [color_positive if var >= 0 else color_negative for var in variations]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=categories,
            y=values,
            marker_color=colors,
            text=[f"{v:,}<br>({var:.1%})" for v, var in zip(values, variations)],
            textposition="auto"
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Categoria",
            yaxis_title="Valor",
            height=400,
            margin=dict(l=10, r=10, t=50, b=10),
            font={'family': "Poppins"}
        )
        
        st.plotly_chart(fig, use_container_width=True)

    def create_circular_progress_chart(value, max_value=1, key=None):
        # Calcular porcentagem
        percent = (value / max_value) * 100

        # Definir cor baseado no valor atual
        if percent < 33.4:
            color = '#FF4B4B'  # Vermelho
        elif percent < 71:
            color = '#FFA500'  # Laranja
        else:
            color = '#2E8B57'  # Verde atual

        fig = go.Figure(go.Pie(
            values=[percent, 100 - percent],
            hole=0.7,
            marker_colors=[color, 'rgba(0, 0, 0, 0.1)'],
            textinfo='none',
            hoverinfo='skip'
        ))

        fig.add_annotation(
            text=f"{percent:.0f}%",
            x=0.5, y=0.5,
            font_size=65,
            showarrow=False
        )

        fig.update_layout(
            showlegend=False,
            margin=dict(l=20, r=20, t=20, b=20),
            height=300
        )

        st.plotly_chart(fig, use_container_width=True, key=key)

    def create_funnel_chart(title, stages, values, conversion_rates, avg_times, color_stages=None):
        """
        Cria um gráfico de funil de vendas com taxas de conversão e tempos médios.
        
        Args:
            title (str): Título do gráfico
            stages (list): Lista com os nomes das etapas do funil
            values (list): Lista com os valores (quantidades) de cada etapa
            conversion_rates (list): Lista com as taxas de conversão entre etapas
            avg_times (list): Lista com os tempos médios de cada etapa
            color_stages (list, optional): Lista de cores para cada etapa
        """
        if color_stages is None:
            # Esquema de cores mais suave e agradável à visão
            color_stages = [
                '#8ECAE6',  # Azul claro suave
                '#219EBC',  # Azul médio
                '#A8DADC',  # Azul pastel
                '#457B9D',  # Azul petróleo
                '#E9C46A',  # Amarelo pastel
                '#F4A261'   # Laranja pastel
            ]
        
        # Criar figura
        fig = go.Figure()
        
        # Adicionar o funil principal com estilo mais moderno e elegante
        fig.add_trace(go.Funnel(
            name='Quantidade',
            y=stages,
            x=values,
            textposition="inside",
            textinfo="value",  # Mostrar apenas o valor, sem percentual
            textfont=dict(size=14, family="Poppins", color="white", weight="bold"),
            opacity=0.85,  # Reduzir opacidade para cores mais suaves
            marker={
                "color": color_stages,
                "line": {"width": [1, 1, 1, 1, 1, 1], "color": ["white", "white", "white", "white", "white", "white"]}
            },
            connector={"line": {"color": "rgba(0,0,0,0.1)", "width": 1, "dash": "dot"}}
        ))
        
        # Adicionar informações diretamente nas etapas do funil
        for i in range(len(stages)):
            # Adicionar tempo médio à direita do funil com estilo moderno e elegante
            fig.add_annotation(
                x=1.05,
                y=i,
                xref="paper",
                yref="y",
                text=f"<b>{avg_times[i]} dias</b>",
                showarrow=False,
                font=dict(size=13, family="Poppins", color="#555"),
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="#ddd",
                borderwidth=1,
                borderpad=6,
                align="left"
            )
        
        # Adicionar setas indicando o fluxo entre etapas com design mais elegante
        for i in range(len(stages) - 1):
            # Calcular a taxa de conversão entre etapas consecutivas
            if i < len(stages) - 1 and values[i] > 0 and values[i+1] > 0:
                conversion = values[i+1] / values[i]
                conversion_percent = f"{conversion:.0%}"
                
                # Adicionar seta e taxa de conversão entre etapas com estilo mais elegante
                fig.add_annotation(
                    x=0.5,  # Centro do funil
                    y=i + 0.5,  # Entre as etapas
                    xref="paper",
                    yref="y",
                    text=f"↓ <b>Conversão: {conversion_percent}</b>",
                    showarrow=False,
                    font=dict(size=13, color="#555", family="Poppins"),
                    bgcolor="rgba(255,255,255,0.9)",
                    bordercolor="#ddd",
                    borderwidth=1,
                    borderpad=6,
                    align="center"
                )
        
        # Configurar layout com estilo mais moderno, elegante e compacto
        fig.update_layout(
            title={
                'text': f"<b>{title}</b>",
                'y': 0.98,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': dict(size=22, family="Poppins", color="#444")
            },
            font=dict(family="Poppins", size=13, color="#555"),
            height=550,  # Altura ligeiramente aumentada para melhor visualização
            margin=dict(l=80, r=150, t=80, b=40),  # Margens ajustadas
            funnelmode="stack",
            showlegend=False,
            plot_bgcolor='rgba(255,255,255,0)',
            paper_bgcolor='rgba(255,255,255,0)'
        )
        
        # Adicionar uma legenda explicativa com estilo mais elegante
        fig.add_annotation(
            x=1.0,
            y=-0.15,
            xref="paper",
            yref="paper",
            text="<i>As setas indicam a taxa de conversão entre etapas</i>",
            showarrow=False,
            font=dict(size=11, color="#777", family="Poppins"),
            align="right"
        )
        
        # Adicionar legenda para tempo médio com estilo mais elegante
        fig.add_annotation(
            x=1.05,
            y=1.05,
            xref="paper",
            yref="paper",
            text="<i>Tempo médio</i>",
            showarrow=False,
            font=dict(size=12, color="#777", family="Poppins", weight="bold"),
            align="left"
        )
        
        # Adicionar efeitos de sombra e gradiente ao layout
        fig.update_layout(
            shapes=[
                # Sombra sutil para o funil
                dict(
                    type="rect",
                    xref="paper",
                    yref="paper",
                    x0=0.05,
                    y0=0.05,
                    x1=0.95,
                    y1=0.95,
                    fillcolor="rgba(0,0,0,0)",
                    line=dict(width=0),
                    layer="below"
                )
            ]
        )
        
        return fig

    # Adicionar div container ao redor do conteúdo principal
    st.markdown('<div class="content-container">', unsafe_allow_html=True)

    # Carregar o logo
    logo = load_logo()

    # Criar layout de cabeçalho com logo
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if logo:
            st.markdown('<div style="margin-top: -100px;">', unsafe_allow_html=True)  # Reduzir espaço acima do logo
            st.image(logo, width=350)
            st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <h1 style="white-space: nowrap; margin-top: -20px;">Indicadores de Crescimento - Metas 2025 📈</h1>
        """, unsafe_allow_html=True)
        st.caption(f"Última atualização: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        # Adicionar mensagem de boas-vindas e botão de logout abaixo da última atualização
        st.write(f"Bem-vindo, {st.session_state['name']}!")
        authenticator.logout("Logout", "main", key="logout_sidebar")

    # Carregar dados
    with st.spinner("Carregando dados..."):
        data = carregar_planilha()

    # Verificar se há dados válidos
    if not data or not all(key in data for key in ['faturamento', 'funil', 'metricas_parceiros', 'desenvolvimento_plataformas', 'captacao_digital']):
        st.warning("Não foi possível carregar dados válidos. Verifique as configurações e a estrutura da planilha.")
        st.stop()

    st.markdown("---")

    # Nova Seção: Meta de Faturamento Anual
    st.header("Meta de Faturamento Anual")

    df_faturamento = data["faturamento"]

    if df_faturamento.empty:
        st.warning("Não há dados disponíveis para Meta de Faturamento Anual.")
    else:
        faturamento_row = df_faturamento[df_faturamento['META DE FATURAMENTO'] == 'FATURAMENTO']
        
        if not faturamento_row.empty:
            faturamento = {
                "atual": float(faturamento_row['ATUAL'].values[0]),
                "meta1_2025": float(faturamento_row['META 1 2025'].values[0]),
                "meta2_2025": float(faturamento_row['META 2 2025'].values[0]),
                "meta3_2025": float(faturamento_row['META 3 2025'].values[0])
            }
            
            # Calcula % de cada meta
            progresso_meta1 = min((faturamento['atual'] / faturamento['meta1_2025']) * 100, 100)
            progresso_meta2 = min((faturamento['atual'] / faturamento['meta2_2025']) * 100, 100)
            progresso_meta3 = min((faturamento['atual'] / faturamento['meta3_2025']) * 100, 100)
            
            # Formatando os valores de progresso para o formato brasileiro
            progresso_meta1_br = f"{progresso_meta1:.1f}".replace(".", ",")
            progresso_meta2_br = f"{progresso_meta2:.1f}".replace(".", ",")
            progresso_meta3_br = f"{progresso_meta3:.1f}".replace(".", ",")
            
            # Formatando os valores monetários para o formato brasileiro
            meta1_br = f"{faturamento['meta1_2025']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            meta2_br = f"{faturamento['meta2_2025']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            meta3_br = f"{faturamento['meta3_2025']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
            # Cards das metas
            st.markdown("""
            <style>
            .meta-card {
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                padding: 20px;
                margin-bottom: 20px;
                position: relative;
                overflow: hidden;
            }
            .meta-card h3 {
                margin-top: 0;
                color: #333;
                font-size: 1.3em;
            }
            .meta-card .value {
                font-size: 1.8em;
                font-weight: 600;
                color: #333;
                margin: 10px 0;
            }
            .meta-card .progress-container {
                width: 100%;
                background-color: #f0f0f0;
                border-radius: 5px;
                margin: 15px 0;
            }
            .meta-card .progress-bar {
                height: 10px;
                border-radius: 5px;
            }
            .meta-card .progress-text {
                text-align: right;
                font-size: 0.9em;
                margin-top: 5px;
            }
            .meta-card .benefit {
                margin-top: 15px;
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 5px;
                font-size: 0.9em;
            }
            .meta-card .benefit-icon {
                font-size: 1.2em;
                margin-right: 5px;
            }
            .meta-card .corner-ribbon {
                position: absolute;
                top: 0;
                right: 0;
                width: 150px;
                height: 30px;
                margin-right: -50px;
                margin-top: 15px;
                transform: rotate(45deg);
                background-color: #70AD47;
                color: white;
                text-align: center;
                line-height: 30px;
                font-weight: bold;
                font-size: 0.8em;
            }
            </style>
            """, unsafe_allow_html=True)
                
            # ================== AQUI ESTÃO AS ALTERAÇÕES DA BARRA DE PROGRESSO ===================
            # Calcular o percentual de progresso (até a meta final de 50M, por exemplo)
            percentual_progresso = min((faturamento['atual'] / faturamento['meta3_2025']) * 100, 100)

            # Card de faturamento atual com design melhorado
            formatted_value = f"{faturamento['atual']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            formatted_percent = f"{percentual_progresso:.1f}".replace(".", ",")
            st.markdown(f"""
                <div style='text-align: center; padding: 12px; background: linear-gradient(135deg, #2196F3, #0D47A1); color: white; border-radius: 15px; box-shadow: 0 8px 16px rgba(33, 150, 243, 0.3); margin: 15px auto 20px auto; max-width: 500px;'>
                    <p style='color: white; font-size: 16px; margin-bottom: 5px; opacity: 0.9;'>Faturamento Atual:</p>
                    <p style='color: white; font-size: 32px; font-weight: 700; margin: 0; text-shadow: 0 2px 4px rgba(0,0,0,0.2);'>
                        R$ {formatted_value}
                    </p>
                    <p style='color: white; margin-top: 5px; font-size: 17px; opacity: 0.9;'>
                        {formatted_percent}% da Meta Final
                    </p>
                </div>
            """, unsafe_allow_html=True)

            # Estilo da barra de progresso com animação
            # Primeiro, definimos a animação CSS separadamente
            st.markdown("""
            <style>
                @keyframes shine {
                    0% { background-position: -100% 0; }
                    100% { background-position: 200% 0; }
                }
            </style>
            """, unsafe_allow_html=True)
            
            # Depois, definimos o restante dos estilos com as variáveis dinâmicas
            st.markdown(f"""
            <style>
                .custom-progress {{
                    height: 35px;
                    background-color: #f0f0f0;
                    border-radius: 10px 10px 0 0;
                    margin: 10px 0 0 0;
                    position: relative;
                    box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
                    width: 96%; /* Reduzindo a largura total em 4% */
                    margin-left: auto;
                    margin-right: auto;
                    overflow: hidden;
                }}
                .custom-progress-bar {{
                    height: 100%;
                    background: linear-gradient(90deg, #1E88E5 0%, #42A5F5 100%);
                    border-radius: 10px 10px 0 0;
                    width: {percentual_progresso}%;
                    position: absolute;
                    top: 0; left: 0;
                    transition: width 1s ease-in-out;
                    box-shadow: 0 1px 5px rgba(0,0,0,0.1);
                    position: relative;
                }}
                
                .custom-progress-bar::after {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(90deg, 
                        rgba(255,255,255,0) 0%, 
                        rgba(255,255,255,0.4) 50%, 
                        rgba(255,255,255,0) 100%);
                    background-size: 200% 100%;
                    animation: shine 5s infinite linear;
                }}
                
                .custom-progress-text {{
                    position: absolute;
                    top: 50%;
                    left: {max(percentual_progresso/2, 3)}%;
                    transform: translate(-50%, -50%);
                    color: white;
                    font-weight: bold;
                    font-size: 16px;
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
                    z-index: 10;
                }}
                .marker-line {{
                    height: 2px;
                    background-color: #ccc;
                    margin: 0;
                    position: relative;
                    top: -1px;
                    width: 96%; /* Reduzindo a largura para corresponder à barra de progresso */
                    margin-left: auto;
                    margin-right: auto;
                }}
            </style>
            """, unsafe_allow_html=True)
            
            # Barra de progresso
            progress_html = f"""
            <div class="custom-progress">
                <div class="custom-progress-bar"></div>
                <div class="custom-progress-text">{formatted_percent}%</div>
            </div>
            <div class="marker-line"></div>
            """
            st.markdown(progress_html, unsafe_allow_html=True)
            
            # Abordagem completamente nova: usando uma tabela HTML simples para os marcadores
            # Isso deve evitar problemas de renderização
            markers_table = f"""
                    <style>
                .milestone-container {{
                    position: relative;
                    width: 100%;
                    margin-top: 5px;
                    padding-top: 10px;
                }}
                .milestone-line {{
                    position: absolute;
                    top: 72px;
                    left: 2.5%;
                    width: 94%;
                    height: 3px;
                    background-color: #ddd;
                    z-index: 1;
                }}
                .milestone {{
                    position: relative;
                    display: inline-block;
                    text-align: center;
                    z-index: 2;
                }}
                .milestone-icon {{
                    font-size: 24px;
                    margin-bottom: 5px;
                }}
                .milestone-status {{
                    font-size: 20px;
                    margin-bottom: 8px;
                    position: relative;
                    z-index: 3;
                }}
                .milestone-value {{
                    font-weight: 600;
                    font-size: 14px;
                }}
                .milestone-label {{
                    font-size: 13px;
                }}
            </style>
            <div class="milestone-container">
                <div class="milestone-line"></div>
                <table style="width: 100%; border-collapse: collapse; border: none; position: relative; z-index: 2;">
                    <tr style="border: none;">
                        <td style="width: 5%; text-align: center; vertical-align: top; border: none;">
                            <div class="milestone">
                                <div class="milestone-icon">🏁</div>
                                <div class="milestone-status">{"🔵" if percentual_progresso >= 0 else "⚪"}</div>
                                <div class="milestone-value" style="color: #2196F3;">R$ 0,00</div>
                                <div class="milestone-label" style="color: #2196F3;">Início</div>
                            </div>
                        </td>
                        <td style="width: 45%; text-align: center; vertical-align: top; border: none;"></td>
                        <td style="width: 22%; text-align: center; vertical-align: top; border: none;">
                            <div class="milestone">
                                <div class="milestone-icon">🥉</div>
                                <div class="milestone-status">{"🔵" if percentual_progresso >= 60 else "⚪"}</div>
                                <div class="milestone-value" style="color: #FF6B6B;">R$ 30.000.000</div>
                                <div class="milestone-label" style="color: #FF6B6B;">1ª Meta • 60%</div>
                            </div>
                        </td>
                        <td style="width: 3%; text-align: center; vertical-align: top; border: none;"></td>
                        <td style="width: 14%; text-align: center; vertical-align: top; border: none;">
                            <div class="milestone">
                                <div class="milestone-icon">🥈</div>
                                <div class="milestone-status">{"🔵" if percentual_progresso >= 80 else "⚪"}</div>
                                <div class="milestone-value" style="color: #FF6B6B;">R$ 40.000.000</div>
                                <div class="milestone-label" style="color: #FF6B6B;">2ª Meta • 80%</div>                           
                            </div>
                        </td>
                        <td style="width: 3%; text-align: center; vertical-align: top; border: none;"></td>
                        <td style="width: 100%; text-align: center; vertical-align: top; border: none;">
                            <div class="milestone">
                                <div class="milestone-icon">🥇</div>
                                <div class="milestone-status">{"🔵" if percentual_progresso >= 100 else "⚪"}</div>
                                <div class="milestone-value" style="color: #FF6B6B;">R$ 50.000.000</div>
                                <div class="milestone-label" style="color: #FF6B6B;">3ª Meta • 100%</div>                           
                            </div>
                        </td>
                    </tr>
                </table>
            </div>
            </table>
            """
                
            # Dividindo a tabela em partes menores para evitar problemas de renderização
            st.markdown(markers_table, unsafe_allow_html=True)
                
            # Espaçamento após os marcadores
            st.markdown("<div style='margin-bottom: 5px;'></div>", unsafe_allow_html=True)

            # Programa de Reconhecimento
            st.markdown("---")
            st.subheader("Programa de Reconhecimento")
            st.markdown("#### INNOVASTAR ⭐", unsafe_allow_html=True)
            
            # Movendo os cards para depois da seção de Programa de Reconhecimento
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.markdown(f"""
                <div class="meta-card">
                    <h3>1ª Meta - 50% da viagem</h3>
                    <div class="value">R$ {meta1_br}</div>
                    <div class="progress-container">
                        <div class="progress-bar" style="width: {progresso_meta1}%; background-color: {'#70AD47' if progresso_meta1 >= 100 else '#FFA500'};"></div>
                    </div>
                    <div class="progress-text">{progresso_meta1_br}% concluído</div>
                    <div class="benefit">
                        <span class="benefit-icon">✈️</span> <strong>Benefício:</strong> 50% de uma viagem para a Europa, América do Sul ou Fernando de Noronha custeada pela empresa
                    </div>
                    {f'<div class="corner-ribbon">META ATINGIDA!</div>' if progresso_meta1 >= 100 else ''}
                </div>
                """, unsafe_allow_html=True)
            
            with col_b:
                st.markdown(f"""
                <div class="meta-card">
                    <h3>2ª Meta - 75% da viagem</h3>
                    <div class="value">R$ {meta2_br}</div>
                    <div class="progress-container">
                        <div class="progress-bar" style="width: {progresso_meta2}%; background-color: {'#70AD47' if progresso_meta2 >= 100 else '#FFA500'};"></div>
                    </div>
                    <div class="progress-text">{progresso_meta2_br}% concluído</div>
                    <div class="benefit">
                        <span class="benefit-icon">⛰️</span> <strong>Benefício:</strong> 75% de uma viagem para a Europa, América do Sul ou Fernando de Noronha custeada pela empresa
                    </div>
                    {f'<div class="corner-ribbon">META ATINGIDA!</div>' if progresso_meta2 >= 100 else ''}
                </div>
                """, unsafe_allow_html=True)
            
            with col_c:
                st.markdown(f"""
                <div class="meta-card">
                    <h3>3ª Meta - 100% da viagem</h3>
                    <div class="value">R$ {meta3_br}</div>
                    <div class="progress-container">
                        <div class="progress-bar" style="width: {progresso_meta3}%; background-color: {'#70AD47' if progresso_meta3 >= 100 else '#FFA500'};"></div>
                    </div>
                    <div class="progress-text">{progresso_meta3_br}% concluído</div>
                    <div class="benefit">
                        <span class="benefit-icon">🏝️</span> <strong>Benefício:</strong> 100% de uma viagem para a Europa, América do Sul ou Fernando de Noronha custeada pela empresa
                    </div>
                    {f'<div class="corner-ribbon">META ATINGIDA!</div>' if progresso_meta3 >= 100 else ''}
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    # Seção 1: Relacionamento
    st.header("Relacionamento")

    df_metricas = data["metricas_parceiros"]
    if df_metricas.empty:
        st.warning("Não há dados disponíveis para Relacionamento.")
    else:
        fundacoes_row = df_metricas[df_metricas['Métricas de Parceiros'] == 'FUNDAÇÕES']
        ifes_row = df_metricas[df_metricas['Métricas de Parceiros'] == 'IFES']
        
        if not fundacoes_row.empty and not ifes_row.empty:
            fundacoes = {
                "qtd_2024": int(fundacoes_row['Qtd. 2024'].values[0]),
                "qtd_2025": int(fundacoes_row['Qtd. 2025'].values[0]),
                "meta_2025": int(fundacoes_row['META 2025'].values[0]),
                "progresso": round(
                    (int(fundacoes_row['Qtd. 2025'].values[0]) - int(fundacoes_row['Qtd. 2024'].values[0])) /
                    (int(fundacoes_row['META 2025'].values[0]) - int(fundacoes_row['Qtd. 2024'].values[0])) * 100, 1
                )
            }

            ifes = {
                "qtd_2024": int(ifes_row['Qtd. 2024'].values[0]),
                "qtd_2025": int(ifes_row['Qtd. 2025'].values[0]),
                "meta_2025": int(ifes_row['META 2025'].values[0]),
                "progresso": round(
                    (int(ifes_row['Qtd. 2025'].values[0]) - int(ifes_row['Qtd. 2024'].values[0])) /
                    (int(ifes_row['META 2025'].values[0]) - int(ifes_row['Qtd. 2024'].values[0])) * 100, 1
                )
            }

            col1_, col2_, col3_, col4_ = st.columns([0.5, 1.7, 0.5, 1.7])

            with col1_:
                st.markdown("<h3 style='margin-bottom: 20px; margin-top: 0px;'>Fundações</h3>", unsafe_allow_html=True)
                st.markdown("<div class='metrics-container'>", unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div class="metric-card" style="margin-bottom: 10px;">
                        <div class="metric-title">2024</div>
                        <div>
                            <span class="metric-value">{fundacoes["qtd_2024"]}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                variacao = ((fundacoes["qtd_2025"] - fundacoes["qtd_2024"]) / fundacoes["qtd_2024"]) * 100
                variation_class = "variation-positive" if variacao >= 0 else "variation-negative"
                variation_symbol = "↑" if variacao >= 0 else "↓"
                
                st.markdown(f"""
                    <div class="metric-card" style="margin-bottom: 10px;">
                        <div class="metric-title">2025</div>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span class="metric-value">{fundacoes["qtd_2025"]}</span>
                            <span class="metric-variation {variation_class}">
                                {variation_symbol} {abs(variacao):.1f}%
                            </span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div class="metric-card" style="margin-bottom: 10px;">
                        <div class="metric-title">Meta 2025</div>
                        <div>
                            <span class="metric-value">{fundacoes["meta_2025"]}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col2_:
                st.markdown("<div style='margin-top: 95px; margin-bottom: -48px;'><h4 style='text-align: center; font-size: 0.9em; opacity: 0.8;'>Progresso em relação à meta de 2025 para Fundações</h4></div>", unsafe_allow_html=True)
                st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
                create_gauge_chart(
                    "",
                    fundacoes["progresso"],
                    0,
                    100,
                    True,
                    COLORS["fundacoes"]
                )
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col3_:
                st.markdown("<h3 style='margin-bottom: 20px; margin-top: 0px;'>IFES</h3>", unsafe_allow_html=True)
                st.markdown("<div class='metrics-container'>", unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div class="metric-card" style="margin-bottom: 10px;">
                        <div class="metric-title">2024</div>
                        <div>
                            <span class="metric-value">{ifes["qtd_2024"]}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                variacao = ((ifes["qtd_2025"] - ifes["qtd_2024"]) / ifes["qtd_2024"]) * 100
                variation_class = "variation-positive" if variacao >= 0 else "variation-negative"
                variation_symbol = "↑" if variacao >= 0 else "↓"
                
                st.markdown(f"""
                    <div class="metric-card" style="margin-bottom: 10px;">
                        <div class="metric-title">2025</div>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span class="metric-value">{ifes["qtd_2025"]}</span>
                            <span class="metric-variation {variation_class}">
                                {variation_symbol} {abs(variacao):.1f}%
                            </span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div class="metric-card" style="margin-bottom: 10px;">
                        <div class="metric-title">Meta 2025</div>
                        <div>
                            <span class="metric-value">{ifes["meta_2025"]}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col4_:
                st.markdown("<div style='margin-top: 95px; margin-bottom: -48px;'><h4 style='text-align: center; font-size: 0.9em; opacity: 0.8;'>Progresso em relação à meta de 2025 para IFES</h4></div>", unsafe_allow_html=True)
                st.markdown("<div style='display: flex; justify-content: center;'>", unsafe_allow_html=True)
                create_gauge_chart(
                    "",
                    ifes["progresso"],
                    0,
                    100,
                    True,
                    COLORS["ifes"]
                )
                st.markdown("</div>", unsafe_allow_html=True)
            
        else:
            st.warning("Dados incompletos para Relacionamento.")

    st.markdown("---")

    # Seção 2: Desenvolvimento de Plataformas
    st.header("Desenvolvimento de Plataformas")

    df_plataformas = data["desenvolvimento_plataformas"]

    if df_plataformas.empty:
        st.warning("Não há dados disponíveis para Desenvolvimento de Plataformas.")
    else:
        plataformas = ['OPORTUNIDADES', 'GESTÃO DE PROJETOS', 'GAMIFICAÇÃO', 'PRODUTOS', 'ESCRITAS']
        plataformas_data = {}

        for plataforma in plataformas:
            row = df_plataformas[df_plataformas['Desenvolvimento de plataformas'] == plataforma]
            if not row.empty:
                plataformas_data[plataforma] = {
                    "andamento": float(row['Andamento (%)'].values[0]),
                    "feedback": row['Feedback'].values[0]
                }
            else:
                st.warning(f"Dados incompletos para {plataforma}.")

        col_o, col_g, col_ga, col_p, col_e = st.columns(5)

        if 'OPORTUNIDADES' in plataformas_data:
            with col_o:
                st.markdown("<h3 style='text-align: center; font-size: 1.2em;'>Plataforma de Oportunidades</h3>", unsafe_allow_html=True)
                create_circular_progress_chart(plataformas_data['OPORTUNIDADES']["andamento"], key="oportunidades_chart")
                st.markdown(f"<div style='position: relative; bottom: 10px; right: 10px; background-color: rgba(255, 255, 255, 0.6); padding: 10px; border-radius: 5px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);'><strong>Última atualização:</strong> {plataformas_data['OPORTUNIDADES']['feedback']}</div>", unsafe_allow_html=True)

        if 'GESTÃO DE PROJETOS' in plataformas_data:
            with col_g:
                st.markdown("<h3 style='text-align: center; font-size: 1.2em;'>Gestão de Projetos</h3>", unsafe_allow_html=True)
                create_circular_progress_chart(plataformas_data['GESTÃO DE PROJETOS']["andamento"], key="gestao_chart")
                st.markdown(f"<div style='position: relative; bottom: 10px; right: 10px; background-color: rgba(255, 255, 255, 0.6); padding: 10px; border-radius: 5px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);'><strong>Última atualização:</strong> {plataformas_data['GESTÃO DE PROJETOS']['feedback']}</div>", unsafe_allow_html=True)

        if 'GAMIFICAÇÃO' in plataformas_data:
            with col_ga:
                st.markdown("""
                    <h3 style='text-align: center; font-size: 1.2em; line-height: 1.2; 
                    height: 2.4em; display: flex; align-items: center; justify-content: center;'>
                        Gamificação do<br>Relacionamento
                    </h3>
                """, unsafe_allow_html=True)
                create_circular_progress_chart(plataformas_data['GAMIFICAÇÃO']["andamento"], key="gamificacao_chart")
                st.markdown(f"<div style='position: relative; bottom: 10px; right: 10px; background-color: rgba(255, 255, 255, 0.6); padding: 10px; border-radius: 5px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);'><strong>Última atualização:</strong> {plataformas_data['GAMIFICAÇÃO']['feedback']}</div>", unsafe_allow_html=True)

        if 'PRODUTOS' in plataformas_data:
            with col_p:
                st.markdown("<h3 style='text-align: center; font-size: 1.2em;'>Plataforma de Produtos</h3>", unsafe_allow_html=True)
                create_circular_progress_chart(plataformas_data['PRODUTOS']["andamento"], key="produtos_chart")
                st.markdown(f"<div style='position: relative; bottom: 10px; right: 10px; background-color: rgba(255, 255, 255, 0.6); padding: 10px; border-radius: 5px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);'><strong>Última atualização:</strong> {plataformas_data['PRODUTOS']['feedback']}</div>", unsafe_allow_html=True)

        if 'ESCRITAS' in plataformas_data:
            with col_e:
                st.markdown("<h3 style='text-align: center; font-size: 1.2em;'>Escrita de Projetos/Produtos</h3>", unsafe_allow_html=True)
                create_circular_progress_chart(plataformas_data['ESCRITAS']["andamento"], key="escritas_chart")
                st.markdown(f"<div style='position: relative; bottom: 10px; right: 10px; background-color: rgba(255, 255, 255, 0.6); padding: 10px; border-radius: 5px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);'><strong>Última atualização:</strong> {plataformas_data['ESCRITAS']['feedback']}</div>", unsafe_allow_html=True)

    st.markdown("---")

    # Nova Seção: Funil de Vendas
    st.header("Funil de Vendas")

    df_funil = data["funil"]

    if df_funil.empty:
        st.warning("Não há dados disponíveis para o Funil de Vendas.")
    else:
        # Extrair dados do DataFrame
        stages = df_funil['Etapa'].tolist()
        values = df_funil['Quantidade'].tolist()
        
        # Formatar taxas de conversão para exibição
        conversion_rates = []
        for rate in df_funil['Taxa de Conversão'].tolist():
            if isinstance(rate, (int, float)):
                conversion_rates.append(f"{rate:.0%}")
            else:
                conversion_rates.append(rate)
        
        avg_times = df_funil['Tempo médio'].tolist()
        
        # Criar layout com duas colunas principais
        col_funil, col_metricas = st.columns([1, 1])
        
        with col_funil:
            # Criar gráfico de funil
            fig = create_funnel_chart(
                title="",
                stages=stages,
                values=values,
                conversion_rates=conversion_rates,
                avg_times=avg_times
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col_metricas:
            # Calcular métricas importantes
            total_oportunidades = values[0] if len(values) > 0 else 0
            total_contratos = values[4] if len(values) > 4 else 0
            taxa_conversao_total = total_contratos / total_oportunidades if total_oportunidades > 0 else 0
            
            # Calcular tempo médio total excluindo a etapa de EXECUÇÃO
            # Identificar o índice da etapa de EXECUÇÃO
            execucao_idx = -1
            for i, stage in enumerate(stages):
                if "EXECUÇÃO" in stage.upper():
                    execucao_idx = i
                    break
            
            # Calcular tempo médio total sem a etapa de EXECUÇÃO
            tempo_medio_total = sum([time for i, time in enumerate(avg_times) if i != execucao_idx])
            
            # Subseção de métricas
            st.subheader("Resumo do Funil")
            
            # Exibir métricas em cards modernos - 2x2 grid
            col_m1, col_m2 = st.columns(2)
            
            with col_m1:
                st.markdown(f"""
                <div style="background-color: white; border-radius: 12px; padding: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 15px; border-left: 5px solid #FFD966;">
                    <h4 style="margin: 0; font-size: 15px; color: #555; font-weight: 500;">Total de Oportunidades</h4>
                    <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: 600; color: #333;">{total_oportunidades}</p>
                </div>
                """, unsafe_allow_html=True)
                    
                st.markdown(f"""
                <div style="background-color: white; border-radius: 12px; padding: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-left: 5px solid #70AD47;">
                    <h4 style="margin: 0; font-size: 15px; color: #555; font-weight: 500;">Taxa de Conversão Total</h4>
                    <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: 600; color: #333;">{taxa_conversao_total:.1%}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_m2:
                st.markdown(f"""
                <div style="background-color: white; border-radius: 12px; padding: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 15px; border-left: 5px solid #9BC2E6;">
                    <h4 style="margin: 0; font-size: 15px; color: #555; font-weight: 500;">Total de Contratos</h4>
                    <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: 600; color: #333;">{total_contratos}</p>
                </div>
                """, unsafe_allow_html=True)
                    
                st.markdown(f"""
                <div style="background-color: white; border-radius: 12px; padding: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-left: 5px solid #C00000;">
                    <h4 style="margin: 0; font-size: 15px; color: #555; font-weight: 500;">Tempo Médio Total (Exceto Execução) </h4>
                    <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: 600; color: #333;">{tempo_medio_total} dias</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Encontrar gargalos no funil (menor taxa de conversão)
            conversion_values = []
            for i, rate in enumerate(conversion_rates):
                if rate != '-' and isinstance(rate, str):
                    try:
                        # Converter string de porcentagem para float
                        rate_value = float(rate.strip('%')) / 100
                        conversion_values.append((i, rate_value))
                    except:
                        pass
            
            if conversion_values:
                min_conversion_idx = min(conversion_values, key=lambda x: x[1])[0]
                min_conversion_stage = stages[min_conversion_idx]
                min_conversion_rate = conversion_rates[min_conversion_idx]
            else:
                min_conversion_stage = "N/A"
                min_conversion_rate = "N/A"
            
            # Encontrar etapa mais demorada (excluindo EXECUÇÃO)
            if avg_times:
                # Filtrar etapas excluindo EXECUÇÃO
                filtered_times = [(i, time) for i, time in enumerate(avg_times) if i != execucao_idx]
                if filtered_times:
                    max_time_idx = max(filtered_times, key=lambda x: x[1])[0]
                    max_time_stage = stages[max_time_idx]
                    max_time_value = avg_times[max_time_idx]
                else:
                    max_time_stage = "N/A"
                    max_time_value = "N/A"
            else:
                max_time_stage = "N/A"
                max_time_value = "N/A"
            
            # Card de gargalos (sem título "Insights")
            st.markdown(f"""
            <div style="background-color: white; border-radius: 12px; padding: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
                <h4 style="margin: 0 0 10px 0; color: #333; font-size: 16px; border-bottom: 2px solid #f0f0f0; padding-bottom: 8px;">Principais Gargalos</h4>
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <div style="background-color: #FFEBEE; color: #C00000; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 10px;">
                        <span style="font-size: 16px;">⚠️</span>
                    </div>
                    <div>
                        <p style="margin: 0; font-size: 14px; font-weight: 500;">Menor taxa de conversão</p>
                        <p style="margin: 3px 0 0 0; font-size: 14px; color: #666;">
                            <span style="color: #C00000; font-weight: 600;">{min_conversion_stage}</span> ({min_conversion_rate})
                        </p>
                    </div>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="background-color: #FFEBEE; color: #C00000; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 10px;">
                        <span style="font-size: 16px;">⏱️</span>
                    </div>
                    <div>
                        <p style="margin: 0; font-size: 14px; font-weight: 500;">Etapa mais demorada</p>
                        <p style="margin: 3px 0 0 0; font-size: 14px; color: #666;">
                            <span style="color: #C00000; font-weight: 600;">{max_time_stage}</span> ({max_time_value} dias)
                        </p>
                        <p style="margin: 3px 0 0 0; font-size: 12px; color: #666; font-style: italic;">Excluindo a etapa de Execução (que naturalmente é mais longa)</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Seção 3: Captação Digital
    st.markdown("""
    <div style="background: linear-gradient(90deg, #833AB4, #FD1D1D, #FCAF45); border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <h2 style="color: white; margin: 0; text-shadow: 0 2px 4px rgba(0,0,0,0.2);">Captação Digital</h2>
                <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 15px;">Métricas e desempenho da presença digital</p>
            </div>
            <div style="font-size: 32px; color: white; text-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                📱 📊
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    df_captacao = data["captacao_digital"]

    if not df_captacao.empty:
        instagram_row = df_captacao[df_captacao['Captação Digital'] == 'INSTAGRAM']
        instagram_past_row = df_captacao[df_captacao['Captação Digital'] == 'INSTAGRAM (Past)']
        
        if not instagram_row.empty and not instagram_past_row.empty:
            # Adicionar estilo CSS para cards de métricas e links
            st.markdown("""
            <style>
                .social-metrics-container {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 15px;
                    margin-bottom: 20px;
                }
                
                .social-metric-card {
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                    padding: 15px;
                    flex: 1;
                    min-width: 160px;
                    position: relative;
                    transition: transform 0.3s;
                }
                
                .social-metric-card:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 8px 16px rgba(0,0,0,0.1);
                }
                
                .metric-icon {
                    position: absolute;
                    top: 15px;
                    right: 15px;
                    font-size: 22px;
                    opacity: 0.2;
                }
                
                .metric-title {
                    color: #666;
                    font-size: 14px;
                    margin-bottom: 15px;
                    font-weight: 500;
                }
                
                .metric-value {
                    font-size: 28px;
                    font-weight: 600;
                    color: #333;
                    margin-bottom: 5px;
                }
                
                .metric-comparison {
                    font-size: 14px;
                    color: #666;
                    display: flex;
                    align-items: center;
                    margin-top: 8px;
                }
                
                .metric-past {
                    padding: 3px 8px;
                    border-radius: 4px;
                    background: #f0f0f0;
                    margin-left: 5px;
                }
                
                .content-card {
                    background: linear-gradient(135deg, #fdfbfb 0%, #f2f6f7 100%);
                    border-radius: 10px;
                    padding: 15px;
                    margin-bottom: 15px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                    display: flex;
                    align-items: center;
                    transition: transform 0.3s;
                }
                
                .content-card:hover {
                    transform: translateY(-3px);
                    box-shadow: 0 6px 15px rgba(0,0,0,0.1);
                }
                
                .content-icon {
                    font-size: 24px;
                    margin-right: 15px;
                }
                
                .content-link {
                    flex-grow: 1;
                    text-decoration: none;
                    color: #1a73e8;
                    font-weight: 500;
                    word-break: break-all;
                }
                
                .engagement-indicator {
                    height: 8px;
                    border-radius: 4px;
                    background: linear-gradient(90deg, #4CAF50 0%, #8BC34A 100%);
                    margin-top: 5px;
                }
                
                .metric-badge {
                    position: absolute;
                    top: 0;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    background: #FF9500;
                    color: white;
                    font-size: 12px;
                    padding: 3px 10px;
                    border-radius: 12px;
                    font-weight: 500;
                    white-space: nowrap;
                }
            </style>
            """, unsafe_allow_html=True)
                
            # Criar linha de métricas principais
            st.subheader("Métricas do Instagram")
            
            # Criar container de métricas
            st.markdown('<div class="social-metrics-container">', unsafe_allow_html=True)
            
            # Definir métricas e ícones
            metrics = [
                {"col": "Impressões", "icon": "👁️", "title": "Impressões"},
                {"col": "Alcance", "icon": "🔍", "title": "Alcance"},
                {"col": "Visitas no Perfil", "icon": "👤", "title": "Visitas no Perfil"},
                {"col": "Cliques no link da bio", "icon": "🔗", "title": "Cliques no Link"},
                {"col": "Taxa de engajamento", "icon": "❤️", "title": "Engajamento", "is_percentage": True}
            ]
            
            # Renderizar cards de métricas
            for metric in metrics:
                col_name = metric["col"]
                current_value = instagram_row[col_name].values[0]
                past_value = instagram_past_row[col_name].values[0]
                is_percentage = metric.get("is_percentage", False)
                
                # Calcular variação
                if past_value > 0:
                    variation = ((current_value - past_value) / past_value) * 100
                    variation_class = "positive" if variation >= 0 else "negative"
                    variation_symbol = "↑" if variation >= 0 else "↓"
                    variation_color = "#4CAF50" if variation >= 0 else "#F44336"
                else:
                    variation = 0
                    variation_class = "neutral"
                    variation_symbol = "•"
                    variation_color = "#9E9E9E"
                
                # Formatar valores
                if is_percentage:
                    formatted_current = f"{current_value:.1%}"
                    formatted_past = f"{past_value:.1%}"
                else:
                    formatted_current = f"{int(current_value):,}".replace(",", ".")
                    formatted_past = f"{int(past_value):,}".replace(",", ".")
                
                # Renderizar card
                st.markdown(f"""
                <div class="social-metric-card">
                    <div class="metric-icon">{metric["icon"]}</div>
                    <h4 class="metric-title">{metric["title"]}</h4>
                    <div class="metric-value">{formatted_current}</div>
                    <div class="metric-comparison">
                        <span style="color: {variation_color}; margin-right: 8px;">{variation_symbol} {abs(variation):.1f}%</span>
                        vs <span class="metric-past">{formatted_past}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Criar seção para os top conteúdos
            st.markdown("""
            <div style="background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%); border-radius: 10px; padding: 20px; margin: 30px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
                <h3 style="margin-top: 0; color: #333; font-size: 22px; border-bottom: 2px solid #EEE; padding-bottom: 10px;">Conteúdos de Maior Desempenho</h3>
                <p style="color: #666; font-size: 15px; margin-bottom: 20px;">As postagens abaixo apresentaram o maior engajamento e alcance no período analisado.</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                top_content_1 = instagram_row['Top conteudo 1'].values[0]
                st.markdown(f"""
                <div style="background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); overflow: hidden; height: 100%; position: relative;">
                    <div style="background: linear-gradient(90deg, #833AB4, #FD1D1D); height: 8px;"></div>
                    <div style="position: absolute; top: 20px; left: 20px; background: #FF9500; color: white; padding: 5px 12px; border-radius: 30px; font-size: 12px; font-weight: 600; box-shadow: 0 4px 8px rgba(255, 149, 0, 0.3);">TOP #1</div>
                    <div style="padding: 25px 20px 20px 20px;">
                        <div style="display: flex; align-items: center; margin-bottom: 15px;">
                            <div style="width: 50px; height: 50px; border-radius: 50%; background: linear-gradient(45deg, #833AB4, #FD1D1D, #FCAF45); display: flex; align-items: center; justify-content: center; margin-right: 15px; flex-shrink: 0;">
                                <span style="font-size: 24px; color: white;">🥇</span>
                            </div>
                            <div>
                                <h4 style="margin: 0 0 5px 0; color: #333; font-size: 18px;">Melhor Conteúdo</h4>
                                <p style="margin: 0; color: #666; font-size: 13px;">Maior engajamento na plataforma</p>
                            </div>
                        </div>
                        
                        <div style="background: #f8f9fa; border-radius: 8px; padding: 12px; margin-bottom: 15px;">
                            <a href="{top_content_1}" target="_blank" style="color: #1a73e8; text-decoration: none; font-weight: 500; word-break: break-all; display: block;">
                                <div style="display: flex; align-items: center;">
                                    <span style="margin-right: 8px; font-size: 18px;">🔗</span>
                                    <span>{top_content_1}</span>
                                </div>
                            </a>
                        </div>
                        
                        <a href="{top_content_1}" target="_blank" style="background: #1a73e8; color: white; text-decoration: none; padding: 10px 15px; border-radius: 5px; font-weight: 500; display: inline-block; transition: all 0.3s;">
                            Ver no Instagram <span style="margin-left: 5px;">➔</span>
                        </a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                top_content_2 = instagram_row['Top conteudo 2'].values[0]
                st.markdown(f"""
                <div style="background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); overflow: hidden; height: 100%; position: relative;">
                    <div style="background: linear-gradient(90deg, #833AB4, #5851DB); height: 8px;"></div>
                    <div style="position: absolute; top: 20px; left: 20px; background: #5851DB; color: white; padding: 5px 12px; border-radius: 30px; font-size: 12px; font-weight: 600; box-shadow: 0 4px 8px rgba(88, 81, 219, 0.3);">TOP #2</div>
                    <div style="padding: 25px 20px 20px 20px;">
                        <div style="display: flex; align-items: center; margin-bottom: 15px;">
                            <div style="width: 50px; height: 50px; border-radius: 50%; background: linear-gradient(45deg, #833AB4, #5851DB); display: flex; align-items: center; justify-content: center; margin-right: 15px; flex-shrink: 0;">
                                <span style="font-size: 24px; color: white;">🥈</span>
                            </div>
                            <div>
                                <h4 style="margin: 0 0 5px 0; color: #333; font-size: 18px;">Segundo Melhor Conteúdo</h4>
                                <p style="margin: 0; color: #666; font-size: 13px;">Alto desempenho na plataforma</p>
                            </div>
                        </div>
                        
                        <div style="background: #f8f9fa; border-radius: 8px; padding: 12px; margin-bottom: 15px;">
                            <a href="{top_content_2}" target="_blank" style="color: #5851DB; text-decoration: none; font-weight: 500; word-break: break-all; display: block;">
                                <div style="display: flex; align-items: center;">
                                    <span style="margin-right: 8px; font-size: 18px;">🔗</span>
                                    <span>{top_content_2}</span>
                                </div>
                            </a>
                        </div>
                        
                        <a href="{top_content_2}" target="_blank" style="background: #5851DB; color: white; text-decoration: none; padding: 10px 15px; border-radius: 5px; font-weight: 500; display: inline-block; transition: all 0.3s;">
                            Ver no Instagram <span style="margin-left: 5px;">➔</span>
                        </a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Taxa de engajamento com barra de progresso estilizada
            engagement_rate = instagram_row['Taxa de engajamento'].values[0]
            
            st.markdown("<div style='margin-top: 40px; margin-bottom: 15px;'></div>", unsafe_allow_html=True)
            
            # Determine engagement quality and color based on rate
            engagement_quality = "Excelente" if engagement_rate >= 0.03 else "Bom" if engagement_rate >= 0.01 else "Médio" if engagement_rate >= 0.005 else "Baixo"
            engagement_color = "#4CAF50" if engagement_rate >= 0.03 else "#2196F3" if engagement_rate >= 0.01 else "#FF9800" if engagement_rate >= 0.005 else "#F44336"
            
            # Criar gauge card para a taxa de engajamento
            st.markdown(f"""
            <div style="background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); overflow: hidden; margin-bottom: 40px;">
                <div style="background: linear-gradient(90deg, #833AB4, #FD1D1D, #FCAF45); padding: 20px;">
                    <h3 style="margin: 0; color: white; text-shadow: 0 2px 4px rgba(0,0,0,0.2); display: flex; align-items: center;">
                        <span style="margin-right: 12px; font-size: 24px;">❤️</span> Taxa de Engajamento
                    </h3>
                </div>
                
                <div style="padding: 25px;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                        <div style="flex: 1;">
                            <div style="font-weight: 500; color: #666; margin-bottom: 5px; font-size: 15px;">Engajamento atual</div>
                            <div style="display: flex; align-items: baseline;">
                                <span style="font-size: 42px; font-weight: 700; color: {engagement_color};">{engagement_rate:.1%}</span>
                                <span style="margin-left: 8px; font-size: 15px; color: #666; font-weight: 500;">({engagement_quality})</span>
                            </div>
                            
                            <div style="margin-top: 20px;">
                                <div style="height: 8px; background-color: #f0f0f0; border-radius: 4px; margin-bottom: 10px; position: relative;">
                                    <div style="position: absolute; top: 0; left: 0; height: 100%; width: {min(engagement_rate * 100 * 10, 100)}%; border-radius: 4px; background: linear-gradient(90deg, {engagement_color} 0%, {engagement_color}AA 100%);"></div>
                                </div>
                                
                                <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
                                    <span style="color: #777; font-size: 13px;">0%</span>
                                    <span style="color: #777; font-size: 13px;">5%</span>
                                    <span style="color: #777; font-size: 13px;">10%</span>
                                </div>
                            </div>
                        </div>
                        
                        <div style="border-left: 1px solid #eee; padding-left: 25px; margin-left: 25px; flex: 1;">
                            <h4 style="margin-top: 0; color: #333; font-size: 16px; margin-bottom: 15px;">Referências de Mercado</h4>
                            
                            <div style="margin-bottom: 10px;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                    <span style="font-size: 14px; color: #666;">Baixo</span>
                                    <span style="font-size: 14px; font-weight: 500; color: #F44336;">< 0.5%</span>
                                </div>
                                <div style="height: 6px; background-color: #f0f0f0; border-radius: 3px;">
                                    <div style="height: 100%; width: 25%; border-radius: 3px; background-color: #F44336;"></div>
                                </div>
                            </div>
                            
                            <div style="margin-bottom: 10px;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                    <span style="font-size: 14px; color: #666;">Médio</span>
                                    <span style="font-size: 14px; font-weight: 500; color: #FF9800;">0.5% - 1%</span>
                                </div>
                                <div style="height: 6px; background-color: #f0f0f0; border-radius: 3px;">
                                    <div style="height: 100%; width: 50%; border-radius: 3px; background-color: #FF9800;"></div>
                                </div>
                            </div>
                            
                            <div style="margin-bottom: 10px;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                    <span style="font-size: 14px; color: #666;">Bom</span>
                                    <span style="font-size: 14px; font-weight: 500; color: #2196F3;">1% - 3%</span>
                                </div>
                                <div style="height: 6px; background-color: #f0f0f0; border-radius: 3px;">
                                    <div style="height: 100%; width: 75%; border-radius: 3px; background-color: #2196F3;"></div>
                                </div>
                            </div>
                            
                            <div>
                                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                    <span style="font-size: 14px; color: #666;">Excelente</span>
                                    <span style="font-size: 14px; font-weight: 500; color: #4CAF50;">> 3%</span>
                                </div>
                                <div style="height: 6px; background-color: #f0f0f0; border-radius: 3px;">
                                    <div style="height: 100%; width: 100%; border-radius: 3px; background-color: #4CAF50;"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div style="margin-top: 25px; background-color: #f9f9f9; border-radius: 8px; padding: 15px; border-left: 4px solid #833AB4;">
                        <p style="margin: 0; color: #555; font-size: 14px;">
                            <span style="font-weight: 600; color: #833AB4;">💡 Dica:</span> 
                            Para aumentar a taxa de engajamento, publique conteúdos que incentivem a interação dos seguidores, como enquetes, perguntas e conteúdos que gerem discussão. Responder aos comentários também pode aumentar significativamente o envolvimento.
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Dados incompletos para Captação Digital.")
    else:
        st.warning("Não há dados disponíveis para Captação Digital.")

    st.markdown("---")
    st.markdown("<div class='footer-custom'>Dashboard - Indicadores de Crescimento - Metas - Versão 1.0 © Innovatis 2025</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)



