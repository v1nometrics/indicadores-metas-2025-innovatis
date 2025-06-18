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
import streamlit.components.v1 as components

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
            font-size: 16px;
            margin-bottom: 6px;
            font-weight: 500;
        }
        
        /* Ajuste para o valor principal */
        .metric-value {
            font-size: 2.1em;  /* Tamanho da fonte aumentado */
            color: #333;
            font-weight: 600;
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
            
        .social-metrics-container {
            display: flex;
            flex-flow: row wrap;
            justify-content: center;
            gap: 10px;
            margin-bottom: 20px;
            padding: 5px 0;
        }
        
        @media (max-width: 768px) {
            .social-metrics-container {
                justify-content: flex-start;
                overflow-x: auto;
                flex-wrap: nowrap;
            }
        }
        
        .social-metric-card {
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            padding: 15px;
            flex: 0 0 auto;
            width: 140px;
            height: 140px;
            position: relative;
            transition: transform 0.3s;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            align-items: flex-start;
            margin: 5px;
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
            margin-bottom: 10px;
            font-weight: 500;
        }
        
        .metric-value {
            font-size: 24px;
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }
        
        .metric-comparison {
            font-size: 12px;
            color: #666;
            display: flex;
            align-items: center;
            margin-top: auto;
        }
        
        .metric-past {
            padding: 2px 6px;
            border-radius: 4px;
            background: #f0f0f0;
            margin-left: 5px;
            font-size: 11px;
        }

        /* Estilo para os cards de métricas do Instagram */
        .instagram-metric-card-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            width: 100%;
            height: 100%;
        }

        .instagram-metric-card-content {
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 12px;
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            align-items: flex-start;
            position: relative;
        }

        /* Estilos específicos para os embeds do Instagram */
        .instagram-media {
            background: #FFF;
            border: 0;
            border-radius: 3px;
            box-shadow: 0 0 1px 0 rgba(0,0,0,0.5), 0 1px 10px 0 rgba(0,0,0,0.15);
            margin: 1px;
            max-width: 540px;
            min-width: 326px;
            padding: 0;
            width: calc(100% - 2px);
        }

        .instagram-media-rendered {
            margin: auto !important;
        }

        /* Container para os embeds do Instagram */
        .instagram-embed-container {
            position: relative;
            width: 100%;
            padding-bottom: 120%;
            overflow: hidden;
        }

        .instagram-embed-container iframe {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: 0;
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

    # =========================================================================
    # Carregamento e Processamento de Dados
    # =========================================================================
    def prepare_instagram_link(url):
        """
        Prepara uma URL do Instagram para uso em botões de redirecionamento.
        Remove /embed/ e garante uma URL válida.
        """
        try:
            # Se a URL não é válida, retornar URL padrão
            if not url or not isinstance(url, str):
                print("URL inválida: não é uma string ou está vazia")
                return "https://instagram.com"
            
            # Log para debug
            print(f"URL original para botão: {url}")
            
            # Verificação específica para o formato que sabemos que está vindo
            # URLs tipo: https://www.instagram.com/epitaciobrito/p/DG3tEQ4vmKZ/embed/
            if 'epitaciobrito' in url and '/p/' in url:
                # Extrair as partes importantes
                parts = url.split('/p/')
                if len(parts) > 1:
                    post_id = parts[1].replace('embed/', '').replace('/embed', '').strip('/')
                    # Reconstruir a URL no formato correto
                    return f"https://www.instagram.com/p/{post_id}/"
            
            # Remover espaços em branco
            clean_url = url.strip()
            
            # Verificar se a URL está no formato esperado
            if not ('instagram.com' in clean_url or clean_url.startswith('www.') or clean_url.startswith('http')):
                # Pode ser apenas o caminho, adicionar prefixo
                if clean_url.startswith('p/') or clean_url.startswith('/p/'):
                    clean_url = 'https://instagram.com/' + clean_url.lstrip('/')
                elif 'epitaciobrito' in clean_url:
                    # Parece ser um perfil/post específico, adaptar
                    clean_url = 'https://instagram.com/' + clean_url
            
            # Remover /embed/ se presente para o link direto
            clean_url = clean_url.replace('/embed/', '/').replace('/embed', '/')
            
            # Remover parâmetros de consulta (tudo após ?)
            clean_url = clean_url.split('?')[0]
            
            # Garantir que termina com barra
            if not clean_url.endswith('/'):
                clean_url += '/'
                
            # Garantir que tem o protocolo
            if not (clean_url.startswith('http://') or clean_url.startswith('https://')):
                if clean_url.startswith('www.'):
                    clean_url = 'https://' + clean_url
                else:
                    clean_url = 'https://' + clean_url.lstrip('/')
                
            # Garantir que contém instagram.com
            if 'instagram.com' not in clean_url:
                parts = clean_url.replace('https://', '').replace('http://', '').lstrip('/').split('/')
                clean_url = f"https://instagram.com/{'/'.join(parts)}"
                
            print(f"URL limpa para botão: {clean_url}")
            return clean_url
        except Exception as e:
            print(f"Erro ao preparar URL do Instagram para botão: {str(e)}")
            return "https://instagram.com"
            
    def convert_instagram_url_to_embed(url):
        """
        Prepara uma URL do Instagram para incorporação.
        Simplificado para garantir que a URL esteja limpa e válida.
        """
        try:
            # Se a URL não é válida, retornar vazio
            if not url or not isinstance(url, str):
                print(f"URL Instagram inválida: {url}")
                return ""
            
            # Debugar a URL original
            print(f"URL original: {url}")
            
            # Verificar se a URL já tem formato de embed
            is_embed_url = url.endswith('/embed/')
            
            # Limpar a URL
            # Remover parâmetros de consulta (tudo após ?)
            url = url.split('?')[0]
            
            # Garantir que a URL termina com barra (se não for uma URL de embed)
            if not url.endswith('/') and not is_embed_url:
                url += '/'
                
            # Verificar se a URL contém os elementos necessários
            if 'instagram.com' not in url:
                if url.startswith('www.'):
                    url = 'https://' + url
                elif url.startswith('/'):
                    url = 'https://instagram.com' + url
                else:
                    url = 'https://instagram.com/' + url
            
            # Garantir que a URL tem protocolo
            if not (url.startswith('http://') or url.startswith('https://')):
                url = 'https://' + url
            
            # Restaurar o /embed/ se estava presente originalmente
            if is_embed_url and not url.endswith('/embed/'):
                if url.endswith('/'):
                    url += 'embed/'
                else:
                    url += '/embed/'
                
            print(f"URL processada: {url}")
            return url
        except Exception as e:
            print(f"Erro ao processar URL do Instagram: {str(e)}")
            return url if isinstance(url, str) else ""

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

    # Função para verificar credenciais
    def verificar_credenciais():
        try:
            # Baixar o arquivo JSON diretamente do S3
            obj = s3.Bucket('jsoninnovatis').Object('chave2.json').get()
            creds_json = json.loads(obj['Body'].read().decode('utf-8'))
            
            # Verificar se as credenciais têm os campos necessários
            required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email', 'client_id', 'auth_uri', 'token_uri']
            missing_fields = [field for field in required_fields if field not in creds_json]
            
            if missing_fields:
                st.error(f"Campos ausentes nas credenciais: {missing_fields}")
                return False
                
            st.success("Credenciais carregadas com sucesso do S3")
            return True
            
        except Exception as e:
            st.error(f"Erro ao verificar credenciais: {str(e)}")
            return False

    # Função para carregar dados da planilha
    @st.cache_data(ttl=3600)  # Cache por 1 hora
    def carregar_planilha():
        import time
        max_retries = 3
        retry_delay = 2  # segundos
        
        # Criar placeholders para mensagens que podem ser limpas
        status_placeholder = st.empty()
        error_placeholder = st.empty()
        
        for attempt in range(max_retries):
            try:
                with status_placeholder:
                    st.info(f"Tentativa {attempt + 1} de {max_retries} - Carregando dados da planilha...")
                
                # Baixar o arquivo JSON diretamente do S3
                obj = s3.Bucket('jsoninnovatis').Object('chave2.json').get()
                # Ler o conteúdo do objeto e decodificar para string, em seguida converter para dict
                creds_json = json.loads(obj['Body'].read().decode('utf-8'))
                # Definir o escopo de acesso para Google Sheets e Google Drive
                scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
                # Criar as credenciais a partir do JSON baixado
                creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
                client = gspread.authorize(creds)
                
                # Tentar diferentes abordagens para acessar a planilha
                planilha = None
                try:
                    # Primeira tentativa: pelo nome exato
                    planilha = client.open("INDICADORES DE CRESCIMENTO").worksheet("INDICADORES")
                except Exception as e1:
                    with error_placeholder:
                        st.warning(f"Erro ao acessar pelo nome exato, tentando alternativas...")
                    try:
                        # Segunda tentativa: listar todas as planilhas para debug
                        with status_placeholder:
                            st.info("Listando planilhas disponíveis...")
                        all_sheets = client.openall()
                        sheet_names = [sheet.title for sheet in all_sheets]
                        
                        # Tentar encontrar uma planilha com nome similar
                        for sheet in all_sheets:
                            if "INDICADORES" in sheet.title.upper() or "CRESCIMENTO" in sheet.title.upper():
                                with status_placeholder:
                                    st.info(f"Tentando acessar planilha: {sheet.title}")
                                planilha = sheet.worksheet("INDICADORES")
                                break
                    except Exception as e2:
                        with error_placeholder:
                            st.error(f"Erro ao listar planilhas: {str(e2)}")
                        raise e1  # Re-raise o erro original
                
                if planilha is None:
                    raise Exception("Não foi possível acessar nenhuma planilha")
                
                # Limpar todas as mensagens de status quando bem-sucedido
                status_placeholder.empty()
                error_placeholder.empty()
                break  # Sair do loop se teve sucesso
                
            except Exception as e:
                with error_placeholder:
                    st.error(f"Tentativa {attempt + 1} falhou: {str(e)}")
                
                if attempt < max_retries - 1:
                    with status_placeholder:
                        st.info(f"Aguardando {retry_delay} segundos antes da próxima tentativa...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Backoff exponencial
                else:
                    with error_placeholder:
                        st.error("Todas as tentativas falharam. Retornando dados vazios.")
                    status_placeholder.empty()  # Limpar mensagem de status
                    return {
                        'faturamento': pd.DataFrame(),
                        'funil': pd.DataFrame(),
                        'funil_past': pd.DataFrame(),
                        'metricas_parceiros': pd.DataFrame(),
                        'desenvolvimento_plataformas': pd.DataFrame(),
                        'captacao_digital': pd.DataFrame(),
                        'captacao_digital_innovatis': pd.DataFrame(),
                        'total_contratos_2025': 0,
                        'total_oportunidades_2025': 0
                    }
        
        try:
            
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
            
            # Nova seção: Funil de Vendas (Linhas 26-34)
            if len(valores) >= 34:
                # Linha 26 (índice 25) contém os cabeçalhos: FUNIL, Qtd., Taxa de Conversão, Tempo médio
                funil_headers = valores[25][1:5]  # Colunas B-E
                
                # Linhas 27-34 (índices 26-33) contêm os dados das etapas do funil
                funil_data = []
                for i in range(26, 34):
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

            # Nova seção: Funil de Vendas - Dados do Período Anterior (Linhas 42-43)
            if len(valores) >= 43:
                # Linha 42 (índice 41) contém os cabeçalhos: Funil Past, Total de Oportunidades, Taxa de Conversão, Total de Contratos, Tempo Médio
                funil_past_headers = valores[41][1:6]  # Colunas B-F
                
                # Linha 43 (índice 42) contém os dados do período anterior
                # Conforme anexo: C=Total de Oportunidades, D=Taxa de Conversão, E=Total de Contratos, F=Tempo Médio
                funil_past_data = []
                funil_past_row = valores[42]  # Linha 43 (índice 42)
                funil_past_data.append([
                    'Past',  # Nome do período
                    funil_past_row[2],  # Coluna C - Total de Oportunidades (107)
                    funil_past_row[3],  # Coluna D - Taxa de Conversão (20,7%)
                    funil_past_row[4],  # Coluna E - Total de Contratos (12)
                    funil_past_row[5]   # Coluna F - Tempo Médio (198)
                ])
                
                # Criar DataFrame para dados do período anterior
                df_funil_past = pd.DataFrame(funil_past_data, 
                                           columns=['Período', 'Total de Oportunidades', 'Taxa de Conversão', 'Total de Contratos', 'Tempo Médio'])
                
                # Converter colunas numéricas
                df_funil_past['Total de Oportunidades'] = pd.to_numeric(df_funil_past['Total de Oportunidades'], errors='coerce').fillna(0).astype(int)
                df_funil_past['Total de Contratos'] = pd.to_numeric(df_funil_past['Total de Contratos'], errors='coerce').fillna(0).astype(int)
                
                df_funil_past['Tempo Médio'] = pd.to_numeric(df_funil_past['Tempo Médio'], errors='coerce').fillna(0).astype(int)
                
                # Converter taxa de conversão para formato decimal
                df_funil_past['Taxa de Conversão'] = df_funil_past['Taxa de Conversão'].apply(
                    lambda x: float(str(x).replace('%', '').replace(',', '.').strip()) / 100 if isinstance(x, str) and x and x != '-' else 0
                )
            else:
                df_funil_past = pd.DataFrame()
            
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
            
            # Seção 2: Desenvolvimento de Plataformas (Linhas 7-12)
            if len(valores) >= 13:
                plataformas_headers = ['Desenvolvimento de plataformas', 'Andamento (%)', 'Feedback']
                plataformas_data = []
                for i in range(7, 13):  # Incluindo linha 13 para a sexta plataforma
                    plataformas_data.append([valores[i][1], valores[i][2], valores[i][3]])  # Add feedback column
                
                df_plataformas = pd.DataFrame(plataformas_data, columns=plataformas_headers)
                
                if 'Andamento (%)' in df_plataformas.columns:
                    df_plataformas['Andamento (%)'] = df_plataformas['Andamento (%)'].apply(
                        lambda x: float(str(x).replace('%', '').strip()) / 100 if isinstance(x, str) and x else 0
                    )
            else:
                df_plataformas = pd.DataFrame()
            
            # Seção 3: Captação Digital - @epitaciobrito (Linhas 14-16)
            if len(valores) >= 16:
                # Linha 13 (índice 13) contém os cabeçalhos para a nova estrutura
                captacao_headers = valores[13][1:10]  # Colunas B-J (9 colunas)
                
                # Linhas 14-16 (índices 14-15) contêm os dados: INSTAGRAM (atual e passado)
                captacao_data = []
                for i in range(14, 16):
                    # Coluna B contém o nome, colunas C-J contêm os valores
                    captacao_data.append(valores[i][1:10])
                
                # Criar DataFrame com os nomes das colunas corretos - nova estrutura
                df_captacao = pd.DataFrame(captacao_data, 
                                        columns=['Captação Digital', 'Impressões', 'Alcance', 
                                               'Visitas no Perfil', 'Cliques no link da bio', 
                                               'Interações totais', 'Top conteudo 1', 'Top conteudo 2', 'Seguidores'])
                
                # Converter colunas numéricas e porcentagens
                for col in df_captacao.columns:
                    if col not in ['Captação Digital', 'Top conteudo 1', 'Top conteudo 2']:  # Não converter colunas de texto
                        df_captacao[col] = pd.to_numeric(df_captacao[col], errors='coerce')
                        # Substituir NaN por 0
                        df_captacao[col] = df_captacao[col].fillna(0)
            else:
                df_captacao = pd.DataFrame()

            # Nova Seção: Captação Digital - @innovatismc (Linhas 37-39)
            if len(valores) >= 39:
                # Linha 37 (índice 36) contém os cabeçalhos
                captacao_innovatis_headers = valores[36][1:8]  # Colunas B-H (7 colunas)
                
                # Linhas 38-39 (índices 37-38) contêm os dados: INSTAGRAM (atual e passado)
                captacao_innovatis_data = []
                for i in range(37, 39):
                    # Coluna B contém o nome, colunas C-H contêm os valores
                    captacao_innovatis_data.append(valores[i][1:8])
                
                # Criar DataFrame para @innovatismc
                df_captacao_innovatis = pd.DataFrame(captacao_innovatis_data, 
                                               columns=['Captação Digital', 'Impressões', 'Alcance', 
                                                      'Visitas no Perfil', 'Cliques no link da bio', 
                                                      'Interações totais', 'Seguidores'])
                
                # Converter colunas numéricas
                for col in df_captacao_innovatis.columns:
                    if col != 'Captação Digital':  # Não converter a coluna de nomes
                        df_captacao_innovatis[col] = pd.to_numeric(df_captacao_innovatis[col], errors='coerce')
                        # Substituir NaN por 0
                        df_captacao_innovatis[col] = df_captacao_innovatis[col].fillna(0)
            else:
                df_captacao_innovatis = pd.DataFrame()

            # Capturar Total de Contratos Fechados em 2025 da célula 44E
            total_contratos_2025 = 0
            if len(valores) >= 44:
                try:
                    total_contratos_2025 = int(pd.to_numeric(valores[43][4], errors='coerce')) if valores[43][4] else 0
                except:
                    total_contratos_2025 = 0

            # Capturar Total de Oportunidades 2025 da célula 44C
            total_oportunidades_2025 = 0
            if len(valores) >= 44:
                try:
                    total_oportunidades_2025 = int(pd.to_numeric(valores[43][2], errors='coerce')) if valores[43][2] else 0
                except:
                    total_oportunidades_2025 = 0
            
            st.success("Dados carregados com sucesso!")
            
            # Retornar um dicionário com os DataFrames
            return {
                'faturamento': df_faturamento,
                'funil': df_funil,
                'funil_past': df_funil_past,
                'metricas_parceiros': df_metricas,
                'desenvolvimento_plataformas': df_plataformas,
                'captacao_digital': df_captacao,
                'captacao_digital_innovatis': df_captacao_innovatis,
                'total_contratos_2025': total_contratos_2025,
                'total_oportunidades_2025': total_oportunidades_2025
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
                '#8ECAE6',  # Azul claro suave (Oportunidades)
                '#FFD966',  # Amarelo institucional (Orçamento)
                '#219EBC',  # Azul médio (Modelagem)
                '#F4A261',  # Laranja pastel (Propostas)
                '#A8DADC',  # Azul pastel (Cotação)
                '#FFB347',  # Laranja médio (Contratos)
                '#457B9D',  # Azul petróleo (Planejamento)
                '#E9C46A'   # Amarelo pastel (Execução)
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
                "line": {"width": [1, 1, 1, 1, 1, 1, 1, 1], "color": ["white", "white", "white", "white", "white", "white", "white", "white"]}
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
            height=655,  # Altura aumentada em ~19% para melhor proporção com os cards
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
    data = carregar_planilha()

    # Verificar se há dados válidos
    if not data or not all(key in data for key in ['faturamento', 'funil', 'funil_past', 'metricas_parceiros', 'desenvolvimento_plataformas', 'captacao_digital', 'captacao_digital_innovatis', 'total_contratos_2025', 'total_oportunidades_2025']):
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
            
            # Versão sem centavos para o marco da barra de progresso
            meta1_br_sem_centavos = meta1_br.rstrip("0").rstrip(",") if meta1_br.endswith(",00") else meta1_br
            
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
            # Calcular o percentual de progresso em relação à primeira meta (R$ 30.000.000)
            percentual_progresso_meta1 = min((faturamento['atual'] / faturamento['meta1_2025']) * 100, 100)
            
            # Mantemos o percentual original para os marcos
            percentual_progresso = min((faturamento['atual'] / faturamento['meta3_2025']) * 100, 100)

            # Card de faturamento atual com design melhorado
            formatted_value = f"{faturamento['atual']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            formatted_percent_meta1 = f"{percentual_progresso_meta1:.1f}".replace(".", ",")
            st.markdown(f"""
                <div class="faturamento-atual-card" style='text-align: center; padding: 16px; background: linear-gradient(135deg, #2196F3, #0D47A1); color: white; border-radius: 20px; box-shadow: 0 10px 20px rgba(33, 150, 243, 0.3); margin: 20px auto 26px auto; max-width: 650px;'>
                    <p style='color: white; font-size: 21px; margin-bottom: 7px; opacity: 0.9;'>Faturamento Atual:</p>
                    <p style='color: white; font-size: 42px; font-weight: 700; margin: 0; text-shadow: 0 3px 5px rgba(0,0,0,0.2);'>
                        R$ {formatted_value}
                    </p>
                    <p style='color: white; margin-top: 7px; font-size: 22px; opacity: 0.9;'>
                        {formatted_percent_meta1}% da Meta 1
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
                    height: 52px; /* Aumentando a espessura da barra em 15% (de 45px para 52px) */
                    background-color: #f0f0f0;
                    border-radius: 10px 10px 0 0;
                    margin: 10px 0 0 0;
                    position: relative;
                    box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
                    width: 75%; /* Reduzindo a largura total para 75% */
                    margin-left: auto;
                    margin-right: auto;
                    overflow: hidden;
                }}
                .custom-progress-bar {{
                    height: 100%;
                    background: linear-gradient(90deg, #1E88E5 0%, #42A5F5 100%);
                    border-radius: 10px 10px 0 0;
                    width: {percentual_progresso_meta1}%;
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
                    left: {max(percentual_progresso_meta1/2, 3)}%;
                    transform: translate(-50%, -50%);
                    color: white;
                    font-weight: bold;
                    font-size: 18px; /* Aumentando o tamanho da fonte */
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
                    z-index: 10;
                }}
                .marker-line {{
                    height: 2px;
                    background-color: #ccc;
                    margin: 0;
                    position: relative;
                    top: -1px;
                    width: 75%; /* Reduzindo a largura para corresponder à barra de progresso */
                    margin-left: auto;
                    margin-right: auto;
                }}
            </style>
            """, unsafe_allow_html=True)
            
            # Barra de progresso
            progress_html = f"""
            <div class="custom-progress">
                <div class="custom-progress-bar"></div>
                <div class="custom-progress-text">{formatted_percent_meta1}%</div>
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
                    width: 75%; /* Ajustando a largura para corresponder à barra de progresso */
                    margin-top: 5px;
                    padding-top: 10px;
                    margin-left: auto;
                    margin-right: auto;
                    height: 110px; /* Altura suficiente para evitar conflito com outros elementos */
                }}
                .milestone-line {{
                    position: absolute;
                    top: 72px;
                    left: 12px; /* Começa exatamente no início do container */
                    width: calc(100% - 24px); /* Exatamente a largura do container */
                    height: 2px;
                    background-color: #ddd;
                    z-index: 1;
                }}
                .milestone {{
                    position: absolute;
                    display: inline-block;
                    text-align: center;
                    z-index: 2;
                    padding: 0;
                    width: 110px;
                }}
                .milestone-left {{
                    left: 0; /* Alinha com o extremo esquerdo */
                    transform: translateX(-40%);
                    margin-left: 0;
                }}
                .milestone-right {{
                    right: 0; /* Alinha com o extremo direito */
                    transform: translateX(40%);
                    margin-right: 0;
                }}
                .milestone-icon {{
                    font-size: 24px;
                    margin-bottom: 5px;
                    text-align: center;
                    display: block;
                }}
                .milestone-status {{
                    font-size: 20px;
                    margin-bottom: 8px;
                    position: relative;
                    z-index: 3;
                    text-align: center;
                    display: block;
                }}
                .milestone-value {{
                    font-weight: 600;
                    font-size: 14px;
                    text-align: center;
                    display: block;
                    white-space: nowrap; /* Evita quebra de linha */
                }}
                .milestone-label {{
                    font-size: 13px;
                    text-align: center;
                    display: block;
                }}
            </style>
            <div class="milestone-container">
                <div class="milestone-line"></div>
                <div class="milestone milestone-left">
                    <div class="milestone-icon">🏁</div>
                    <div class="milestone-status">{"🔵" if percentual_progresso_meta1 >= 0 else "⚪"}</div>
                    <div class="milestone-value" style="color: #2196F3;">R$&nbsp;0,00</div>
                    <div class="milestone-label" style="color: #2196F3;">Início</div>
                </div>
                <div class="milestone milestone-right">
                    <div class="milestone-icon">🏆</div>
                    <div class="milestone-status">{"🔵" if percentual_progresso_meta1 >= 100 else "⚪"}</div>
                    <div class="milestone-value" style="color: #FF6B6B;">R$&nbsp;{meta1_br_sem_centavos}</div>
                    <div class="milestone-label" style="color: #FF6B6B;">Meta Atingida</div>
                </div>
            </div>
            """
                
            # Dividindo a tabela em partes menores para evitar problemas de renderização
            st.markdown(markers_table, unsafe_allow_html=True)
                
            # Espaçamento após os marcadores (aumentado para evitar sobreposição)
            st.markdown("<div style='margin-bottom: 80px;'></div>", unsafe_allow_html=True)

            # ========== NOVA SEÇÃO: ANÁLISE COMPARATIVA E PROJEÇÕES ==========
            st.markdown("---")
            st.subheader("Análise Comparativa com 2024 e Projeções de Faturamento")

            # Dados históricos e atuais
            faturamento_2024_s1 = 10_618_617.76
            faturamento_2024_s2 = 7_299_772.79
            faturamento_2025_s1 = 14_305_053.60
            contratos_execucao = 22_000_000.00

            # Cálculos
            crescimento_s1 = (faturamento_2025_s1 / faturamento_2024_s1) - 1
            proporcao_s2_2024 = faturamento_2024_s2 / faturamento_2024_s1
            projecao_2025_s2 = faturamento_2025_s1 * proporcao_s2_2024
            progresso_contratos = (contratos_execucao / projecao_2025_s2) * 100 if projecao_2025_s2 > 0 else 0

            # Função de formatação BRL
            def brl_format(val):
                return f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

                        # Cálculo adicional para análise
            diferenca_valor = contratos_execucao - projecao_2025_s2
            
            # SVG Icons
            icon_growth = '<svg viewBox="0 0 24 24" width="32" height="32" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>'
            icon_target = '<svg viewBox="0 0 24 24" width="32" height="32" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>'
            icon_contract = '<svg viewBox="0 0 24 24" width="32" height="32" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>'
            
            # CARDS PRINCIPAIS - Layout Horizontal (altura fixa para alinhamento perfeito)
            col1, col2, col3 = st.columns(3, gap="large")
            
            # Cálculos para o Card 3 - Meta de 30 milhões
            meta_30_milhoes = 30_000_000.00
            pendencia_meta = meta_30_milhoes - faturamento['atual']
            
            # Se contratos em execução cobrem a pendência ou não
            if contratos_execucao >= pendencia_meta:
                status_meta = "Meta coberta pelos contratos"
                percentual_cobertura = 100
                excedente = contratos_execucao - pendencia_meta
            else:
                status_meta = "Cobertura parcial"
                percentual_cobertura = (contratos_execucao / pendencia_meta) * 100 if pendencia_meta > 0 else 100
                excedente = 0
            
            # CARD 1: Performance 1º Semestre
            with col1:
                st.markdown(f"""
                <div class="analise-card-hover" style="background: linear-gradient(135deg, #2196F3, #0D47A1); border-radius: 16px; padding: 24px; color: white; box-shadow: 0 8px 24px rgba(33, 150, 243, 0.3); margin-bottom: 20px; height: 320px; display: flex; flex-direction: column; transition: all 0.3s ease;">
                    <div style="display: flex; align-items: center; margin-bottom: 20px;">
                        <div style="background: rgba(255,255,255,0.2); border-radius: 12px; padding: 12px; margin-right: 16px; flex-shrink: 0;">
                            {icon_growth}
                        </div>
                        <div style="flex: 1; min-width: 0;">
                            <h4 style="margin: 0; color: white; font-size: 16px; opacity: 0.9;">Performance 1º Semestre</h4>
                            <p style="margin: 0; color: rgba(255,255,255,0.8); font-size: 14px;">Crescimento vs. 2024</p>
                        </div>
                    </div>
                    <div style="text-align: center; margin-bottom: 20px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                        <div style="font-size: 36px; font-weight: 700; margin-bottom: 8px;">+{crescimento_s1:.1%}</div>
                        <div style="background: rgba(255,255,255,0.2); border-radius: 8px; padding: 8px; font-size: 14px;">Forte crescimento identificado</div>
                    </div>
                    <div style="border-top: 1px solid rgba(255,255,255,0.2); padding-top: 16px; margin-top: auto;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <span style="opacity: 0.8;">2024:</span>
                            <span style="font-weight: 600; font-size: 13px;">{brl_format(faturamento_2024_s1)}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span style="opacity: 0.8;">2025:</span>
                            <span style="font-weight: 600; font-size: 13px;">{brl_format(faturamento_2025_s1)}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # CARD 2: Projeção 2º Semestre
            with col2:
                st.markdown(f"""
                <div class="analise-card-hover" style="background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%); border-radius: 16px; padding: 24px; color: white; box-shadow: 0 8px 24px rgba(107, 114, 128, 0.3); margin-bottom: 20px; height: 320px; display: flex; flex-direction: column; transition: all 0.3s ease;">
                    <div style="display: flex; align-items: center; margin-bottom: 20px;">
                        <div style="background: rgba(255,255,255,0.2); border-radius: 12px; padding: 12px; margin-right: 16px; flex-shrink: 0;">
                            {icon_target}
                        </div>
                        <div style="flex: 1; min-width: 0;">
                            <h4 style="margin: 0; color: white; font-size: 16px; opacity: 0.9;">Projeção 2º Semestre</h4>
                            <p style="margin: 0; color: rgba(255,255,255,0.8); font-size: 14px;">Para 2025.02</p>
                        </div>
                    </div>
                    <div style="text-align: center; margin-bottom: 20px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                        <div style="font-size: 28px; font-weight: 700; margin-bottom: 8px;">{brl_format(projecao_2025_s2)}</div>
                        <div style="background: rgba(255,255,255,0.2); border-radius: 8px; padding: 8px; font-size: 14px;">Calculado via regra de três</div>
                    </div>
                    <div style="border-top: 1px solid rgba(255,255,255,0.2); padding-top: 16px; margin-top: auto;">
                        <div style="font-size: 13px; opacity: 0.9; line-height: 1.4; text-align: center;">
                            <div style="margin-bottom: 6px;">2º sem 2024 = <strong>{proporcao_s2_2024:.1%}</strong> do 1º sem 2024</div>
                            <div style="font-size: 12px; opacity: 0.8;">Proporção aplicada para 2025.02</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # CARD 3: Contratos em Execução
            with col3:
                st.markdown(f"""
                <div class="analise-card-hover" style="background: linear-gradient(135deg, #2196F3, #0D47A1); border-radius: 16px; padding: 24px; color: white; box-shadow: 0 8px 24px rgba(33, 150, 243, 0.3); margin-bottom: 20px; height: 320px; display: flex; flex-direction: column; transition: all 0.3s ease;">
                    <div style="display: flex; align-items: center; margin-bottom: 20px;">
                        <div style="background: rgba(255,255,255,0.2); border-radius: 12px; padding: 12px; margin-right: 16px; flex-shrink: 0;">
                            {icon_contract}
                        </div>
                        <div style="flex: 1; min-width: 0;">
                            <h4 style="margin: 0; color: white; font-size: 16px; opacity: 0.9;">Contratos em Execução</h4>
                            <p style="margin: 0; color: rgba(255,255,255,0.8); font-size: 14px;">Desembolso até Dez/2025</p>
                        </div>
                    </div>
                    <div style="text-align: center; margin-bottom: 20px; flex: 1; display: flex; flex-direction: column; justify-content: center;">
                        <div style="font-size: 22px; font-weight: 700; margin-bottom: 8px;">{brl_format(contratos_execucao)}</div>
                        <div style="background: rgba(255,255,255,0.2); border-radius: 8px; padding: 8px; font-size: 14px;">{progresso_contratos:.1f}% da projeção</div>
                    </div>
                    <div style="border-top: 1px solid rgba(255,255,255,0.2); padding-top: 12px; margin-top: auto;">
                        <div style="margin-bottom: 6px; font-size: 11px; opacity: 0.8;">Projeção para a Meta de R$ 30mi:</div>
                        <div style="background: rgba(255,255,255,0.2); border-radius: 4px; height: 16px; margin-bottom: 6px; position: relative; display: flex; align-items: center;">
                            <div style="background: white; height: 100%; border-radius: 4px; width: {min(percentual_cobertura, 100)}%; position: absolute; top: 0; left: 0;"></div>
                            <div style="position: relative; z-index: 10; width: 100%; text-align: center; font-size: 11px; font-weight: 600; color: #333;">
                                {percentual_cobertura:.1f}%
                            </div>
                        </div>
                        <div style="text-align: center; font-size: 12px; line-height: 1.2;">
                            <div style="margin-bottom: 2px;">Pendência atual para bater a meta: <strong>{brl_format(pendencia_meta)}</strong></div>
                            <div style="opacity: 0.9;">
                                {f"{status_meta} - Excedente: <strong>{brl_format(excedente)}</strong>" if contratos_execucao >= pendencia_meta else f"{percentual_cobertura:.1f}% da pendência coberta"}
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            

            
            st.markdown("---")
            
            # Programa de Reconhecimento
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
                st.markdown("<h3 style='margin-bottom: 20px; margin-top: 0px; font-size: 22px; font-weight: 600;'>Fundações</h3>", unsafe_allow_html=True)
                st.markdown("<div class='metrics-container'>", unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div class="metric-card" style="margin-bottom: 10px;">
                        <div class="metric-title" style="font-size: 18px; font-weight: 600; color: #444;">2024</div>
                        <div>
                            <span class="metric-value" style="font-size: 2.1em; font-weight: 700;">{fundacoes["qtd_2024"]}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                variacao = ((fundacoes["qtd_2025"] - fundacoes["qtd_2024"]) / fundacoes["qtd_2024"]) * 100
                variation_class = "variation-positive" if variacao >= 0 else "variation-negative"
                variation_symbol = "↑" if variacao >= 0 else "↓"
                
                st.markdown(f"""
                    <div class="metric-card" style="margin-bottom: 10px;">
                        <div class="metric-title" style="font-size: 18px; font-weight: 600; color: #444;">2025</div>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span class="metric-value" style="font-size: 2.1em; font-weight: 700;">{fundacoes["qtd_2025"]}</span>
                            <span class="metric-variation {variation_class}">
                                {variation_symbol} {abs(variacao):.1f}%
                            </span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div class="metric-card" style="margin-bottom: 10px;">
                        <div class="metric-title" style="font-size: 18px; font-weight: 600; color: #444;">Meta 2025</div>
                        <div>
                            <span class="metric-value" style="font-size: 2.1em; font-weight: 700;">{fundacoes["meta_2025"]}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col2_:
                st.markdown("<div style='margin-top: 95px; margin-bottom: -48px;'><h4 style='text-align: center; font-size: 1em; opacity: 0.8;'>Progresso em relação à meta de 2025 para Fundações</h4></div>", unsafe_allow_html=True)
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
                st.markdown("<h3 style='margin-bottom: 20px; margin-top: 0px; font-size: 22px; font-weight: 600;'>IFES</h3>", unsafe_allow_html=True)
                st.markdown("<div class='metrics-container'>", unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div class="metric-card" style="margin-bottom: 10px;">
                        <div class="metric-title" style="font-size: 18px; font-weight: 600; color: #444;">2024</div>
                        <div>
                            <span class="metric-value" style="font-size: 2.1em; font-weight: 700;">{ifes["qtd_2024"]}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                variacao = ((ifes["qtd_2025"] - ifes["qtd_2024"]) / ifes["qtd_2024"]) * 100
                variation_class = "variation-positive" if variacao >= 0 else "variation-negative"
                variation_symbol = "↑" if variacao >= 0 else "↓"
                
                st.markdown(f"""
                    <div class="metric-card" style="margin-bottom: 10px;">
                        <div class="metric-title" style="font-size: 18px; font-weight: 600; color: #444;">2025</div>
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span class="metric-value" style="font-size: 2.1em; font-weight: 700;">{ifes["qtd_2025"]}</span>
                            <span class="metric-variation {variation_class}">
                                {variation_symbol} {abs(variacao):.1f}%
                            </span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div class="metric-card" style="margin-bottom: 10px;">
                        <div class="metric-title" style="font-size: 18px; font-weight: 600; color: #444;">Meta 2025</div>
                        <div>
                            <span class="metric-value" style="font-size: 2.1em; font-weight: 700;">{ifes["meta_2025"]}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col4_:
                st.markdown("<div style='margin-top: 95px; margin-bottom: -48px;'><h4 style='text-align: center; font-size: 1em; opacity: 0.8;'>Progresso em relação à meta de 2025 para IFES</h4></div>", unsafe_allow_html=True)
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
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    df_plataformas = data["desenvolvimento_plataformas"]

    if df_plataformas.empty:
        st.warning("Não há dados disponíveis para Desenvolvimento de Plataformas.")
    else:
        plataformas = ['OPORTUNIDADES', 'MONITORAMENTO FINANCEIRO', 'GESTÃO DE PROJETOS', 'PRODUTOS', 'GAMIFICAÇÃO', 'ESCRITAS']
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

        col_o, col_mf, col_g, col_ga, col_p, col_e = st.columns(6)

        if 'OPORTUNIDADES' in plataformas_data:
            with col_o:
                st.markdown("""
                    <h3 style='text-align: center; font-size: 1.2em; line-height: 1.2; 
                    height: 2.4em; display: flex; align-items: center; justify-content: center; margin-bottom: 0;'>
                        Plataforma de Oportunidades
                    </h3>
                """, unsafe_allow_html=True)
                create_circular_progress_chart(plataformas_data['OPORTUNIDADES']["andamento"], key="oportunidades_chart")
                # Card fino e elegante para o embaixador
                st.markdown("""
                    <div style='background-color: #f8f8f8; text-align: center; margin: 5px 0; padding: 3px 0; border-radius: 3px; font-size: 13px;'>
                        <span style='font-weight: 500;'>Embaixador: </span>Vinícius Torres
                    </div>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                    <div style='background-color: rgba(255, 255, 255, 0.6); padding: 10px; border-radius: 5px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);'>
                        <strong>Última atualização:</strong> {plataformas_data['OPORTUNIDADES']['feedback']}
                    </div>
                """, unsafe_allow_html=True)

        if 'MONITORAMENTO FINANCEIRO' in plataformas_data:
            with col_mf:
                st.markdown("""
                    <h3 style='text-align: center; font-size: 1.2em; line-height: 1.2; 
                    height: 2.4em; display: flex; align-items: center; justify-content: center; margin-bottom: 0;'>
                        Plataforma de Monitoramento
                    </h3>
                """, unsafe_allow_html=True)
                create_circular_progress_chart(plataformas_data['MONITORAMENTO FINANCEIRO']["andamento"], key="monitoramento_chart")
                # Card fino e elegante para o embaixador
                st.markdown("""
                    <div style='background-color: #f8f8f8; text-align: center; margin: 5px 0; padding: 3px 0; border-radius: 3px; font-size: 13px;'>
                        <span style='font-weight: 500;'>Embaixador: </span>Vinícius Torres
                    </div>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                    <div style='background-color: rgba(255, 255, 255, 0.6); padding: 10px; border-radius: 5px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);'>
                        <strong>Última atualização:</strong> {plataformas_data['MONITORAMENTO FINANCEIRO']['feedback']}
                    </div>
                """, unsafe_allow_html=True)

        if 'PRODUTOS' in plataformas_data:
            with col_g:
                st.markdown("""
                    <h3 style='text-align: center; font-size: 1.2em; line-height: 1.2; 
                    height: 2.4em; display: flex; align-items: center; justify-content: center; margin-bottom: 0;'>
                        Plataforma de Produtos
                    </h3>
                """, unsafe_allow_html=True)
                create_circular_progress_chart(plataformas_data['PRODUTOS']["andamento"], key="produtos_chart")
                # Card fino e elegante para o embaixador
                st.markdown("""
                    <div style='background-color: #f8f8f8; text-align: center; margin: 5px 0; padding: 3px 0; border-radius: 3px; font-size: 13px;'>
                        <span style='font-weight: 500;'>Embaixador: </span>Victor Eduardo
                    </div>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                    <div style='background-color: rgba(255, 255, 255, 0.6); padding: 10px; border-radius: 5px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);'>
                        <strong>Última atualização:</strong> {plataformas_data['PRODUTOS']['feedback']}
                    </div>
                """, unsafe_allow_html=True)

        if 'GESTÃO DE PROJETOS' in plataformas_data:
            with col_ga:
                st.markdown("""
                    <h3 style='text-align: center; font-size: 1.2em; line-height: 1.2; 
                    height: 2.4em; display: flex; align-items: center; justify-content: center; margin-bottom: 0;'>
                        Gestão de Projetos
                    </h3>
                """, unsafe_allow_html=True)
                create_circular_progress_chart(plataformas_data['GESTÃO DE PROJETOS']["andamento"], key="gestao_chart")
                # Card fino e elegante para o embaixador
                st.markdown("""
                    <div style='background-color: #f8f8f8; text-align: center; margin: 5px 0; padding: 3px 0; border-radius: 3px; font-size: 13px;'>
                        <span style='font-weight: 500;'>Embaixador: </span>Raissa Cartaxo
                    </div>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                    <div style='background-color: rgba(255, 255, 255, 0.6); padding: 10px; border-radius: 5px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);'>
                        <strong>Última atualização:</strong> {plataformas_data['GESTÃO DE PROJETOS']['feedback']}
                    </div>
                """, unsafe_allow_html=True)

        if 'GAMIFICAÇÃO' in plataformas_data:
            with col_p:
                st.markdown("""
                    <h3 style='text-align: center; font-size: 1.2em; line-height: 1.2; 
                    height: 2.4em; display: flex; align-items: center; justify-content: center; margin-bottom: 0;'>
                        Gamificação do<br>Relacionamento
                    </h3>
                """, unsafe_allow_html=True)
                create_circular_progress_chart(plataformas_data['GAMIFICAÇÃO']["andamento"], key="gamificacao_chart")
                # Card fino e elegante para o embaixador
                st.markdown("""
                    <div style='background-color: #f8f8f8; text-align: center; margin: 5px 0; padding: 3px 0; border-radius: 3px; font-size: 13px;'>
                        <span style='font-weight: 500;'>Embaixador: </span>Marcus Varandas
                    </div>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                    <div style='background-color: rgba(255, 255, 255, 0.6); padding: 10px; border-radius: 5px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);'>
                        <strong>Última atualização:</strong> {plataformas_data['GAMIFICAÇÃO']['feedback']}
                    </div>
                """, unsafe_allow_html=True)

        if 'ESCRITAS' in plataformas_data:
            with col_e:
                st.markdown("""
                    <h3 style='text-align: center; font-size: 1.2em; line-height: 1.2; 
                    height: 2.4em; display: flex; align-items: center; justify-content: center; margin-bottom: 0;'>
                        Escrita de Projetos/Produtos
                    </h3>
                """, unsafe_allow_html=True)
                create_circular_progress_chart(plataformas_data['ESCRITAS']["andamento"], key="escritas_chart")
                # Card fino e elegante para o embaixador
                st.markdown("""
                    <div style='background-color: #f8f8f8; text-align: center; margin: 5px 0; padding: 3px 0; border-radius: 3px; font-size: 13px;'>
                        <span style='font-weight: 500;'>Embaixador: </span>Marcus Varandas
                    </div>
                """, unsafe_allow_html=True)
                st.markdown(f"""
                    <div style='background-color: rgba(255, 255, 255, 0.6); padding: 10px; border-radius: 5px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);'>
                        <strong>Última atualização:</strong> {plataformas_data['ESCRITAS']['feedback']}
                    </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    # Nova Seção: Funil de Vendas
    st.header("Funil de Vendas")
    
    # Adicionar informação do período
    st.markdown("""
        <div style="margin-top: -10px; margin-bottom: 25px;">
            <p style="color: #666; font-size: 15px; font-style: italic;">Dados considerados: 01/01/2025 até hoje</p>
            <p style="color: #ff8c00; font-size: 14px; font-style: italic; margin-top: 8px; padding: 8px 12px; background-color: #fff8f0; border-left: 4px solid #ff8c00; border-radius: 4px;">
                <strong>Observação:</strong> Apenas o funil de "Produtos" está sendo analisado, pois "Projetos" foi recentemente reestruturado e será avaliado a partir das reuniões de meta dos próximos meses.
            </p>
        </div>
    """, unsafe_allow_html=True)

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
            # Total de oportunidades vem da célula 44C (capturadas e tratadas em 2025)
            total_oportunidades = data.get("total_oportunidades_2025", 0)
            
            # Encontrar índices importantes
            modelagem_idx = -1
            planejamento_idx = -1
            contratos_idx = -1
            for i, stage in enumerate(stages):
                if "MODELAGEM" in stage.upper():
                    modelagem_idx = i
                elif "PLANEJAMENTO" in stage.upper():
                    planejamento_idx = i
                elif "CONTRATOS" in stage.upper():
                    contratos_idx = i
            
            # Total de contratos será carregado dos dados da planilha
            total_contratos = data.get("total_contratos_2025", 0)
            
            # Calcular taxa de conversão dos cards que saíram de Modelagem e chegaram até Planejamento
            if modelagem_idx >= 0 and planejamento_idx >= 0 and modelagem_idx < planejamento_idx:
                valor_entrada = values[modelagem_idx]
                valor_saida = values[planejamento_idx]
                taxa_conversao_total = valor_saida / valor_entrada if valor_entrada > 0 else 0
            else:
                taxa_conversao_total = 0
            
            # Calcular tempo médio total da Modelagem até o contrato ser assinado (antes de entrar em Planejamento)
            # Isso inclui: Modelagem + Propostas + Cotação + Contratos (mas exclui Planejamento e Execução)
            if modelagem_idx >= 0 and contratos_idx >= 0:
                tempo_medio_total = sum([time for i, time in enumerate(avg_times) if modelagem_idx <= i <= contratos_idx])
            else:
                tempo_medio_total = 0

            # Carregar dados do período anterior para comparação
            df_funil_past = data["funil_past"]
            
            # Inicializar variáveis do período anterior
            past_oportunidades = 0
            past_contratos = 0
            past_taxa_conversao = 0
            past_tempo_medio = 0
            
            if not df_funil_past.empty:
                past_row = df_funil_past[df_funil_past['Período'] == 'Past']
                if not past_row.empty:
                    past_oportunidades = int(past_row['Total de Oportunidades'].values[0])
                    past_contratos = int(past_row['Total de Contratos'].values[0])
                    past_taxa_conversao = float(past_row['Taxa de Conversão'].values[0])
                    past_tempo_medio = int(past_row['Tempo Médio'].values[0])
            
            # Subseção de métricas
            st.subheader("Resumo do Funil")
            
            # Exibir métricas em cards modernos - 2x2 grid
            col_m1, col_m2 = st.columns(2)
            
            with col_m1:
                # Calcular variação para Total de Oportunidades
                oportunidades_variation = ((total_oportunidades - past_oportunidades) / past_oportunidades * 100) if past_oportunidades > 0 else 0
                oportunidades_var_color = "#4CAF50" if oportunidades_variation >= 0 else "#F44336"
                oportunidades_var_symbol = "↑" if oportunidades_variation >= 0 else "↓"
                
                st.markdown(f"""
                <div class="funil-metric-card" style="background-color: white; border-radius: 12px; padding: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 15px; border-left: 5px solid #FFD966;">
                    <h4 style="margin: 0; font-size: 15px; color: #555; font-weight: 500;">Total de Oportunidades</h4>
                    <p style="margin: 0; font-size: 12px; color: #777;">(Captadas e tratadas em 2025)</p>
                    <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: 600; color: #333;">{total_oportunidades}</p>
                    <div style="margin-top: 8px; display: flex; align-items: center;">
                        <span style="color: {oportunidades_var_color}; font-size: 12px; font-weight: 600; padding: 2px 6px; background-color: {oportunidades_var_color}20; border-radius: 4px; margin-right: 8px;">
                            {oportunidades_var_symbol} {abs(oportunidades_variation):.1f}%
                        </span>
                        <span style="color: #777; font-size: 12px;">vs {past_oportunidades} (até mês passado)</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                    
                # Calcular variação para Taxa de Conversão (em pontos percentuais)
                conversao_variation = (taxa_conversao_total - past_taxa_conversao) * 100 if past_taxa_conversao > 0 else 0
                conversao_var_color = "#4CAF50" if conversao_variation >= 0 else "#F44336"
                conversao_var_symbol = "↑" if conversao_variation >= 0 else "↓"
                
                st.markdown(f"""
                <div class="funil-metric-card" style="background-color: white; border-radius: 12px; padding: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-left: 5px solid #70AD47;">
                    <h4 style="margin: 0; font-size: 15px; color: #555; font-weight: 500;">Taxa de Conversão</h4>
                    <p style="margin: 0; font-size: 12px; color: #777;">(Modelagem até Planejamento)</p>
                    <div style="display: flex; align-items: baseline;">
                        <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: 600; color: #333;">{taxa_conversao_total:.1%}</p>
                        <p style="margin: 5px 0 0 8px; font-size: 14px; color: #777;">Meta: 75%</p>
                    </div>
                    <div style="width: 100%; height: 6px; background-color: #f0f0f0; border-radius: 3px; margin-top: 8px;">
                        <div style="width: {min(taxa_conversao_total*100/75*100, 100)}%; height: 100%; border-radius: 3px; background-color: {('#4CAF50' if taxa_conversao_total >= 0.75 else '#FFC107' if taxa_conversao_total >= 0.5 else '#F44336')}"></div>
                    </div>
                    <div style="margin-top: 8px; display: flex; align-items: center;">
                        <span style="color: {conversao_var_color}; font-size: 12px; font-weight: 600; padding: 2px 6px; background-color: {conversao_var_color}20; border-radius: 4px; margin-right: 8px;">
                            {conversao_var_symbol} {abs(conversao_variation):.1f}%
                        </span>
                        <span style="color: #777; font-size: 12px;">vs {past_taxa_conversao:.1%} (período anterior)</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_m2:
                # Calcular variação para Total de Contratos
                contratos_variation = ((total_contratos - past_contratos) / past_contratos * 100) if past_contratos > 0 else 0
                contratos_var_color = "#4CAF50" if contratos_variation >= 0 else "#F44336"
                contratos_var_symbol = "↑" if contratos_variation >= 0 else "↓"
                
                st.markdown(f"""
                <div class="funil-metric-card" style="background-color: white; border-radius: 12px; padding: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 15px; border-left: 5px solid #9BC2E6;">
                    <h4 style="margin: 0; font-size: 15px; color: #555; font-weight: 500;">Total de Contratos</h4>
                    <p style="margin: 0; font-size: 12px; color: #777;">(Fechados em 2025)</p>
                    <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: 600; color: #333;">{total_contratos}</p>
                    <div style="margin-top: 8px; display: flex; align-items: center;">
                        <span style="color: {contratos_var_color}; font-size: 12px; font-weight: 600; padding: 2px 6px; background-color: {contratos_var_color}20; border-radius: 4px; margin-right: 8px;">
                            {contratos_var_symbol} {abs(contratos_variation):.1f}%
                        </span>
                        <span style="color: #777; font-size: 12px;">vs {past_contratos} (período anterior)</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                    
                # Calcular variação para Tempo Médio (para tempo médio, menor é melhor, então invertemos a lógica)
                tempo_variation = ((tempo_medio_total - past_tempo_medio) / past_tempo_medio * 100) if past_tempo_medio > 0 else 0
                # Para tempo médio: diminuição é boa (verde), aumento é ruim (vermelho)
                tempo_var_color = "#4CAF50" if tempo_variation < 0 else "#F44336"  # Verde se diminuiu, vermelho se aumentou
                tempo_var_symbol = "↓" if tempo_variation < 0 else "↑"  # Seta para baixo se diminuiu, para cima se aumentou
                
                st.markdown(f"""
                <div class="funil-metric-card" style="background-color: white; border-radius: 12px; padding: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); border-left: 5px solid #C00000;">
                    <h4 style="margin: 0; font-size: 15px; color: #555; font-weight: 500;">Tempo Médio</h4>
                    <p style="margin: 0; font-size: 12px; color: #777;">(Modelagem até contrato assinado)</p>
                    <div style="display: flex; align-items: baseline;">
                        <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: 600; color: #333;">{tempo_medio_total} dias</p>
                        <p style="margin: 5px 0 0 8px; font-size: 14px; color: #777;">Meta: 120 dias</p>
                    </div>
                    <div style="width: 100%; height: 6px; background-color: #f0f0f0; border-radius: 3px; margin-top: 8px;">
                        <div style="width: {min(100 - max(tempo_medio_total - 120, 0)/120*100, 100)}%; height: 100%; border-radius: 3px; background-color: {('#4CAF50' if tempo_medio_total <= 120 else '#FFC107' if tempo_medio_total <= 150 else '#F44336')}"></div>
                    </div>
                    <div style="margin-top: 8px; display: flex; align-items: center;">
                        <span style="color: {tempo_var_color}; font-size: 12px; font-weight: 600; padding: 2px 6px; background-color: {tempo_var_color}20; border-radius: 4px; margin-right: 8px;">
                            {tempo_var_symbol} {abs(tempo_variation):.1f}%
                        </span>
                        <span style="color: #777; font-size: 12px;">vs {past_tempo_medio} dias (período anterior)</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Encontrar gargalos no funil (menor taxa de conversão)
            conversion_values = []
            for i, rate in enumerate(conversion_rates):
                # Só considerar taxas entre Modelagem e Planejamento
                if modelagem_idx <= i <= planejamento_idx and rate != '-' and isinstance(rate, str):
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
            
            # Encontrar etapa mais demorada (entre Modelagem e Contratos)
            if avg_times and modelagem_idx >= 0 and contratos_idx >= 0:
                # Filtrar etapas entre Modelagem e Contratos (excluindo Planejamento e Execução)
                filtered_times = [(i, time) for i, time in enumerate(avg_times) if modelagem_idx <= i <= contratos_idx]
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
            <div class="gargalos-card" style="background-color: white; border-radius: 12px; padding: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-top: 15px;">
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
                        <p style="margin: 3px 0 0 0; font-size: 12px; color: #666; font-style: italic;">Até o contrato ser assinado (exclui Planejamento e Execução)</p>
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
                <h2 style="color: white; margin: 0; text-shadow: 0 2px 4px rgba(0,0,0,0.2);">Metas de Comunicação & Marketing</h2>
                <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 15px;">Métricas e desempenho da presença digital</p>
            </div>
            <div style="font-size: 32px; color: white; text-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                📱 📊
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Dados das metas de comunicação e marketing
    marketing_goals = [
        # ——— COMUNICAÇÃO INTERNA ———
        {"objetivo": "Comunicação Interna", "acao": "Comunicados",             "meta": "1 por semana",       "pct": 0.90, "pct_anterior": 0.30, "status": "🟡 Em progresso"},
        {"objetivo": "Comunicação Interna", "acao": "Templates",               "meta": "Finalizados",    "pct": 1.00, "pct_anterior": None, "status": "✅ Concluído"},
        {"objetivo": "Comunicação Interna", "acao": "Material Institucional",  "meta": "Finalizado",     "pct": 0.85, "pct_anterior": 0.80, "status": "🟡 Em progresso"},

        # ——— SINALIZAÇÃO DO ESCRITÓRIO ———
        {"objetivo": "Sinalização Escritório", "acao": "Layout",                   "meta": "Validado",          "pct": 1.00, "pct_anterior": None, "status": "✅ Concluído"},
        {"objetivo": "Sinalização Escritório", "acao": "Preparação para impressão",  "meta": "Arquivos prontos",  "pct": 0.70, "pct_anterior": 0.30, "status": "🟡 Em progresso"},
        {"objetivo": "Sinalização Escritório", "acao": "Produção com fornecedor",   "meta": "—",                 "pct": 0.00, "pct_anterior": None, "status": "🔴 Não iniciado"},
        {"objetivo": "Sinalização Escritório", "acao": "Aplicação adesivos/placas",  "meta": "—",                 "pct": 0.00, "pct_anterior": None, "status": "🔴 Não iniciado"},

        # ——— ALCANCE NO INSTAGRAM ———
        {"objetivo": "Alcance Instagram", "acao": "Captação novos projetos", "meta": "4 projetos por ano", "pct": 0.00, "pct_anterior": None, "status": "🔴 Não iniciado"},
        {"objetivo": "Alcance Instagram", "acao": "Divulgação projetos",     "meta": "1 post por semana", "pct": 0.80, "pct_anterior": 0.40, "status": "🟡 Em progresso"},
        {"objetivo": "Alcance Instagram", "acao": "Vídeos semanais",         "meta": "2 vídeos por semana","pct": 0.80, "pct_anterior": 0.50, "status": "🟡 Em progresso"},
    ]

    # Criar três colunas para os objetivos
    col1, col2, col3 = st.columns(3, gap="large")

    # Mapear objetivos para colunas
    cols = {
        "Comunicação Interna": col1,
        "Sinalização Escritório": col2,
        "Alcance Instagram": col3
    }

    # Reordenar plataformas (trocando Gamificação com Produtos)
    plataformas = ['OPORTUNIDADES', 'MONITORAMENTO FINANCEIRO', 'GESTÃO DE PROJETOS', 'PRODUTOS', 'GAMIFICAÇÃO', 'ESCRITAS']

    # Estilo CSS para os cards de metas
    card_style = """
        padding: 16px;
        background: white;
        border-radius: 12px;
        margin-bottom: 16px;
        box-shadow: rgba(0, 0, 0, 0.1) 0px 4px 12px;
        border: 1px solid rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        cursor: default;
    """

    # Adicionar estilos CSS globais
    st.markdown("""
    <style>
        /* Estilo para os títulos das colunas */
        h3 {
            color: #2C3E50;
            font-weight: 500;
            font-size: 19px !important;
            padding-bottom: 10px;
            border-bottom: 1px solid #f0f0f0;
            margin-bottom: 20px !important;
            text-align: center;
            opacity: 0.9;
        }
        
        /* Estilo base para os cards */
        div[style*="border-radius: 12px"] {
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        /* Efeito hover apenas para os cards das metas */
        div[style*="border-radius: 12px"]:hover {
            transform: translateY(-4px);
            box-shadow: rgba(0, 0, 0, 0.15) 0px 8px 24px !important;
        }
        
        /* Melhorar contraste do texto */
        .meta-title {
            color: #1a1a1a;
            font-weight: 600;
            font-size: 1.05em;
            margin-bottom: 6px;
        }
        
        .meta-value {
            color: #444;
            font-size: 0.95em;
            margin-bottom: 8px;
        }
        
        .meta-status {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            font-weight: 500;
        }
        
        /* Melhorar aparência da barra de progresso */
        .progress-bar-bg {
            background: #f5f5f5;
            border-radius: 6px;
            height: 8px;
            overflow: hidden;
            border: 1px solid rgba(0, 0, 0, 0.05);
        }
        
        .progress-bar-fill {
            height: 100%;
            border-radius: 6px;
            transition: width 0.3s ease;
        }

        /* Ajuste para centralizar o conteúdo das colunas */
        [data-testid="column"] {
            display: flex;
            flex-direction: column;
            align-items: stretch;
        }
    </style>
    """, unsafe_allow_html=True)

    # Renderizar metas em cada coluna
    for objetivo in ["Comunicação Interna", "Sinalização Escritório", "Alcance Instagram"]:
        col = cols[objetivo]
        col.markdown(f"<h3>{objetivo}</h3>", unsafe_allow_html=True)
        
        # Filtrar metas do objetivo atual
        metas_objetivo = [m for m in marketing_goals if m["objetivo"] == objetivo]
        
        for meta in metas_objetivo:
            # Definir cor da barra de progresso
            if meta["pct"] == 1:
                bar_color = "#4CAF50"  # Verde para concluído
            elif meta["pct"] > 0:
                bar_color = "#FFC107"  # Amarelo para em progresso
            else:
                bar_color = "#F44336"  # Vermelho para não iniciado
            
            # Calcular variação se existe valor anterior
            if meta["pct_anterior"] is not None:
                variation = (meta["pct"] - meta["pct_anterior"]) * 100
                variation_percent = f"{abs(variation):.0f}%"
                previous_percent = f"{int(meta['pct_anterior']*100)}%"
            else:
                variation_percent = None
                previous_percent = None
                
            # Criar card usando a mesma estrutura dos outros cards
            col.markdown(f"""
            <div class="funil-metric-card" style="background-color: white; border-radius: 12px; padding: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); margin-bottom: 15px; border-left: 5px solid {bar_color};">
                <h4 style="margin: 0; font-size: 15px; color: #555; font-weight: 500;">{meta['acao']}</h4>
                <p style="margin: 0; font-size: 12px; color: #777;">Meta: {meta['meta']}</p>
                <div style="display: flex; align-items: baseline;">
                    <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: 600; color: #333;">{int(meta['pct']*100)}%</p>
                    <p style="margin: 5px 0 0 8px; font-size: 14px; color: #777;">{meta['status']}</p>
                </div>
                <div style="width: 100%; height: 6px; background-color: #f0f0f0; border-radius: 3px; margin-top: 8px;">
                    <div style="width: {meta['pct']*100}%; height: 100%; border-radius: 3px; background-color: {bar_color}"></div>
                </div>
                {f'''<div style="margin-top: 8px; display: flex; align-items: center;">
                    <span style="color: #4CAF50; font-size: 12px; font-weight: 600; padding: 2px 6px; background-color: #4CAF5020; border-radius: 4px; margin-right: 8px;">
                        ↑ {variation_percent}
                    </span>
                    <span style="color: #777; font-size: 12px;">vs {previous_percent} (período anterior)</span>
                </div>''' if variation_percent else ''}
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
                    flex-flow: row wrap;
                    justify-content: center;
                    gap: 10px;
                    margin-bottom: 20px;
                    padding: 5px 0;
                }
                
                @media (max-width: 768px) {
                    .social-metrics-container {
                        justify-content: flex-start;
                        overflow-x: auto;
                        flex-wrap: nowrap;
                    }
                }
                
                .social-metric-card {
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                    padding: 15px;
                    flex: 0 0 auto;
                    width: 140px;
                    height: 140px;
                    position: relative;
                    transition: transform 0.3s;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    align-items: flex-start;
                    margin: 5px;
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
                    margin-bottom: 10px;
                    font-weight: 500;
                }
                
                .metric-value {
                    font-size: 24px;
                    font-weight: 600;
                    color: #333;
                    margin-bottom: 5px;
                }
                
                .metric-comparison {
                    font-size: 12px;
                    color: #666;
                    display: flex;
                    align-items: center;
                    margin-top: auto;
                }
                
                .metric-past {
                    padding: 2px 6px;
                    border-radius: 4px;
                    background: #f0f0f0;
                    margin-left: 5px;
                    font-size: 11px;
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
            st.markdown("<h2 style='font-size: 24px;'>Métricas do Instagram</h2>", unsafe_allow_html=True)

            # Adicionar informação do período
            st.markdown("""
                <div style="margin-top: -10px; margin-bottom: 25px;">
                    <p style="color: #666; font-size: 15px; font-style: italic;">Dados considerados: últimos 30 dias vs os 30 anteriores a estes</p>
                </div>
            """, unsafe_allow_html=True)

            # Definir métricas e ícones
            metrics = [
                {"col": "Impressões", "icon": "👁️", "title": "Impressões"},
                {"col": "Alcance", "icon": "🔍", "title": "Alcance"},
                {"col": "Visitas no Perfil", "icon": "👤", "title": "Visitas no Perfil"},
                {"col": "Cliques no link da bio", "icon": "🔗", "title": "Cliques no Link"},
                {"col": "Interações totais", "icon": "❤️", "title": "Interações"},
                {"col": "Seguidores", "icon": "👥", "title": "Seguidores"}
            ]

            # ========== MÉTRICAS @EPITACIOBRITO ==========
            st.markdown("""
                <div style="margin: 10px 0 20px 0;">
                    <h3 style="color: #333; font-size: 20px; font-weight: 600; margin-bottom: 15px; 
                               display: flex; align-items: center; border-bottom: 2px solid #f0f0f0; padding-bottom: 8px;">
                        @epitaciobrito
                    </h3>
                </div>
            """, unsafe_allow_html=True)
            
            # Adicionar CSS para melhorar a responsividade
            st.markdown("""
            <style>
                /* Efeito de hover para todos os cards */
                .metric-card, .instagram-metric-card-content, .meta-card, .platform-card, .social-metric-card, 
                div[style*="background: white; border-radius: 12px; box-shadow:"],
                div[style*="background-color: white; border-radius: 10px;"],
                div[style*="background-color: #f5f5f5; border-radius:"],
                div[style*="background-color: rgba(255, 255, 255, 0.6); padding: 10px; border-radius: 5px;"],
                .funil-metric-card {
                    transition: all 0.3s ease;
                }
                
                .metric-card:hover, .instagram-metric-card-content:hover, .meta-card:hover, .platform-card:hover, 
                .social-metric-card:hover, div[style*="background: white; border-radius: 12px; box-shadow:"]:hover,
                div[style*="background-color: white; border-radius: 10px;"]:hover,
                div[style*="background-color: #f5f5f5; border-radius:"]:hover,
                div[style*="background-color: rgba(255, 255, 255, 0.6); padding: 10px; border-radius: 5px;"]:hover,
                .funil-metric-card:hover {
                    transform: scale(1.03);
                    box-shadow: 0 6px 16px rgba(0,0,0,0.15);
                    z-index: 10;
                }
                
                /* Efeito específico para o card de Faturamento Atual */
                div[style*="background: linear-gradient(120deg, #1a237e, #283593);"],
                div[style*="background: linear-gradient(135deg, #1a237e, #283593);"],
                div[style*="background: linear-gradient(135deg, #2196F3, #0D47A1);"],
                .faturamento-atual-card {
                    transition: all 0.3s ease;
                }
                
                div[style*="background: linear-gradient(120deg, #1a237e, #283593);"]:hover,
                div[style*="background: linear-gradient(135deg, #1a237e, #283593);"]:hover,
                div[style*="background: linear-gradient(135deg, #2196F3, #0D47A1);"]:hover,
                .faturamento-atual-card:hover {
                    transform: scale(1.03);
                    box-shadow: 0 12px 24px rgba(33, 150, 243, 0.4);
                    z-index: 10;
                }
                
                /* Efeito hover para os cards de Top Conteúdo */
                .top-content-card {
                    transition: all 0.3s ease;
                }
                
                .top-content-card:hover {
                    transform: scale(1.02);
                    box-shadow: 0 8px 24px rgba(131, 58, 180, 0.25);
                    z-index: 10;
                }
                
                /* Efeito hover para os cards de Análise Comparativa */
                .analise-card-hover:hover {
                    transform: translateY(-8px) scale(1.02);
                    box-shadow: 0 16px 32px rgba(0, 0, 0, 0.2) !important;
                    z-index: 10;
                }
                
                /* Efeito hover para os botões dentro dos cards de Top Conteúdo */
                .top-content-card a[style*="background:"] {
                    transition: all 0.3s ease;
                }
                
                .top-content-card a[style*="background:"]:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
                }
                
                /* Estilo para os cards de texto em Desenvolvimento de Plataformas */
                div[style*="background-color: white; padding: 10px; border-radius: 8px;"],
                div[style*="background-color: white; padding: 12px; border-radius: 10px;"] {
                    transition: all 0.3s ease;
                }
                
                div[style*="background-color: white; padding: 10px; border-radius: 8px;"]:hover,
                div[style*="background-color: white; padding: 12px; border-radius: 10px;"]:hover {
                    transform: scale(1.03);
                    box-shadow: 0 6px 16px rgba(0,0,0,0.15);
                }
                
                /* Cards de Resumo do Funil */
                div[style*="background-color: #ffffff; border-radius: 10px; padding: 15px;"] {
                    transition: all 0.3s ease;
                }
                
                div[style*="background-color: #ffffff; border-radius: 10px; padding: 15px;"]:hover {
                    transform: scale(1.03);
                    box-shadow: 0 6px 16px rgba(0,0,0,0.15);
                }
                
                /* Exceção para o card de Principais Gargalos */
                .gargalos-card {
                    transition: none !important;
                }
                
                .gargalos-card:hover {
                    transform: none !important;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
                }
                
                /* Estilo para os cards de métricas do Instagram */
                .instagram-metric-card-container {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    width: 100%;
                    height: 100%;
                }

                .instagram-metric-card-content {
                    background-color: white;
                    border-radius: 10px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    padding: 12px;
                    width: 100%;
                    height: 100%;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    align-items: flex-start;
                    position: relative;
                }

                /* Estilos específicos para os embeds do Instagram */
                .instagram-media {
                    background: #FFF;
                    border: 0;
                    border-radius: 3px;
                    box-shadow: 0 0 1px 0 rgba(0,0,0,0.5), 0 1px 10px 0 rgba(0,0,0,0.15);
                    margin: 1px;
                    max-width: 540px;
                    min-width: 326px;
                    padding: 0;
                    width: calc(100% - 2px);
                }

                .instagram-media-rendered {
                    margin: auto !important;
                }

                /* Container para os embeds do Instagram */
                .instagram-embed-container {
                    position: relative;
                    width: 100%;
                    padding-bottom: 120%;
                    overflow: hidden;
                }

                .instagram-embed-container iframe {
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    border: 0;
                }
            </style>
            """, unsafe_allow_html=True)
            
            # Criar as colunas para os cards (com gap maior para espaçamento melhor)
            metric_cols = st.columns(6, gap="medium")
            
            # Renderizar cards de métricas usando colunas
            for i, metric in enumerate(metrics):
                col_name = metric["col"]
                current_value = instagram_row[col_name].values[0]
                past_value = instagram_past_row[col_name].values[0]
                is_percentage = metric.get("is_percentage", False)
                
                # Ajustar valores de comparação para 'Alcance' e 'Visitas no Perfil'
                if col_name == "Alcance":
                    past_value = 24680
                elif col_name == "Visitas no Perfil":
                    current_value = 2053
                    past_value = 2024
                
                # Certifique-se de que os valores são convertidos corretamente de strings para floats
                try:
                    # Remove dots from numbers (used as thousand separators) and convert comma to decimal point
                    current_value = float(str(current_value).replace('.', '').replace(',', '.'))
                    past_value = float(str(past_value).replace('.', '').replace(',', '.'))
                    
                    # Convert to integer if not a percentage
                    if not is_percentage:
                        current_value = int(current_value)
                        past_value = int(past_value)
                except ValueError:
                    current_value = 0
                    past_value = 0
                
                # Format the values for display, showing full numbers
                if is_percentage:
                    formatted_current = f"{current_value:.1%}".replace('.', ',')
                    formatted_past = f"{past_value:.1%}".replace('.', ',')
                else:
                    formatted_current = f"{current_value:,}".replace(",", ".")
                    formatted_past = f"{past_value:,}".replace(",", ".")
                
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
                
                # Renderizar card em cada coluna
                with metric_cols[i]:
                    st.markdown(f"""
                    <div class="instagram-metric-card-container">
                        <div class="instagram-metric-card-content" style="border-top: 4px solid {variation_color};">
                            <div style="position: absolute; top: 12px; right: 12px; font-size: 22px; opacity: 0.3;">{metric["icon"]}</div>
                            <div>
                                <h4 style="color: #555; font-size: 16px; margin-bottom: 8px; font-weight: 600;">{metric["title"]}</h4>
                                <div style="font-size: 28px; font-weight: 700; color: #333; margin-top: 4px;">{formatted_current}</div>
                            </div>
                            <div style="font-size: 14px; color: #555; display: flex; align-items: center; margin-top: auto;">
                                <span style="color: {variation_color}; margin-right: 6px; font-weight: 600; font-size: 16px; padding: 2px 6px; background-color: {variation_color}20; border-radius: 4px;">{variation_symbol} {abs(variation):.1f}%</span>
                                vs <span style="padding: 3px 8px; border-radius: 4px; background: #f0f0f0; margin-left: 5px; font-size: 13px; font-weight: 500;">{formatted_past}</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
            # Não é mais necessário fechar o container com st.markdown
            
            # ========== MÉTRICAS @INNOVATISMC ==========
            st.markdown("""
                <div style="margin: 50px 0 20px 0;">
                    <h3 style="color: #333; font-size: 20px; font-weight: 600; margin-bottom: 15px; 
                               display: flex; align-items: center; border-bottom: 2px solid #f0f0f0; padding-bottom: 8px;">
                        @innovatismc
                    </h3>
                </div>
            """, unsafe_allow_html=True)
            
            # Dados do @innovatismc da planilha (linhas 37-39)
            df_captacao_innovatis = data["captacao_digital_innovatis"]
            
            if not df_captacao_innovatis.empty:
                instagram_innovatis_row = df_captacao_innovatis[df_captacao_innovatis['Captação Digital'] == 'INSTAGRAM']
                instagram_innovatis_past_row = df_captacao_innovatis[df_captacao_innovatis['Captação Digital'] == 'INSTAGRAM (Past)']
                
                if not instagram_innovatis_row.empty and not instagram_innovatis_past_row.empty:
                    # Dados atuais do @innovatismc
                    innovatis_current = {}
                    innovatis_past = {}
                    
                    for col_name in ["Impressões", "Alcance", "Visitas no Perfil", "Cliques no link da bio", "Interações totais", "Seguidores"]:
                        innovatis_current[col_name] = int(instagram_innovatis_row[col_name].values[0])
                        innovatis_past[col_name] = int(instagram_innovatis_past_row[col_name].values[0])
                else:
                    st.warning("Dados incompletos para @innovatismc.")
                    innovatis_current = {}
                    innovatis_past = {}
            else:
                st.warning("Não há dados disponíveis para @innovatismc.")
                innovatis_current = {}
                innovatis_past = {}
            
            # Renderizar cards apenas se houver dados válidos
            if innovatis_current and innovatis_past:
                # Criar as colunas para os cards do @innovatismc
                innovatis_metric_cols = st.columns(6, gap="medium")
                
                # Renderizar cards de métricas para @innovatismc
                for i, metric in enumerate(metrics):
                    col_name = metric["col"]
                    current_value = innovatis_current.get(col_name, 0)
                    past_value = innovatis_past.get(col_name, 0)
                    is_percentage = metric.get("is_percentage", False)
                    
                    # Format the values for display
                    if is_percentage:
                        formatted_current = f"{current_value:.1%}".replace('.', ',')
                        formatted_past = f"{past_value:.1%}".replace('.', ',')
                    else:
                        formatted_current = f"{current_value:,}".replace(",", ".")
                        formatted_past = f"{past_value:,}".replace(",", ".")
                    
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
                    
                    # Renderizar card em cada coluna
                    with innovatis_metric_cols[i]:
                        st.markdown(f"""
                        <div class="instagram-metric-card-container">
                            <div class="instagram-metric-card-content" style="border-top: 4px solid {variation_color};">
                                <div style="position: absolute; top: 12px; right: 12px; font-size: 22px; opacity: 0.3;">{metric["icon"]}</div>
                                <div>
                                    <h4 style="color: #555; font-size: 16px; margin-bottom: 8px; font-weight: 600;">{metric["title"]}</h4>
                                    <div style="font-size: 28px; font-weight: 700; color: #333; margin-top: 4px;">{formatted_current}</div>
                                </div>
                                <div style="font-size: 14px; color: #555; display: flex; align-items: center; margin-top: auto;">
                                    <span style="color: {variation_color}; margin-right: 6px; font-weight: 600; font-size: 16px; padding: 2px 6px; background-color: {variation_color}20; border-radius: 4px;">{variation_symbol} {abs(variation):.1f}%</span>
                                    vs <span style="padding: 3px 8px; border-radius: 4px; background: #f0f0f0; margin-left: 5px; font-size: 13px; font-weight: 500;">{formatted_past}</span>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

            # Criar seção para os top conteúdos
            st.markdown("""
            <div style="margin: 30px 0 20px 0;">
                <h2 style="color: #333; font-size: 24px; font-weight: 600; margin-bottom: 10px;">Conteúdos de Maior Desempenho</h2>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                try:
                    top_content_1 = instagram_row['Top conteudo 1'].values[0]
                    
                    # Solução direta: sempre usar a URL fixa para o botão 1, ignorando processamento
                    # Esta abordagem é mais robusta para diferentes ambientes
                    url_for_button_1 = "https://www.instagram.com/reel/DK2hIGvvtRq/embed/"
                    print("Usando URL fixa para o botão 1 (ignorando processamento)")
                    
                    # Log para debug
                    print(f"URL original 1: {top_content_1}")
                    print(f"URL para botão 1: {url_for_button_1}")

                    st.markdown(f"""
                    <div class="top-content-card" style="background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); overflow: hidden; height: 100%; position: relative; margin-bottom: 0px;">
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
                            <div style="text-align: center; margin-top: 10px; margin-bottom: 15px;">
                                <a href="{url_for_button_1}" target="_blank" style="background: #1a73e8; color: white; text-decoration: none; padding: 10px 15px; border-radius: 5px; font-weight: 500; display: inline-block; transition: all 0.3s;">
                                    Ver no Instagram <span style="margin-left: 5px;">➔</span>
                                </a>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                        
                except Exception as e:
                    st.error(f"Erro ao carregar o primeiro conteúdo: {str(e)}")

            with col2:
                try:
                    top_content_2 = instagram_row['Top conteudo 2'].values[0]
                    
                    # Solução direta: sempre usar a URL fixa para o botão 2, ignorando processamento
                    # Esta abordagem é mais robusta para diferentes ambientes
                    url_for_button_2 = "https://www.instagram.com/p/DKNfxxbyq2E/embed/"
                    print("Usando URL fixa para o botão 2 (ignorando processamento)")
                    
                    # Log para debug
                    print(f"URL original 2: {top_content_2}")
                    print(f"URL para botão 2: {url_for_button_2}")

                    st.markdown(f"""
                    <div class="top-content-card" style="background: white; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.06); overflow: hidden; height: 100%; position: relative; margin-bottom: 0px;">
                        <div style="background: linear-gradient(90deg, #5851DB, #405DE6); height: 8px;"></div>
                        <div style="position: absolute; top: 20px; left: 20px; background: #6E45E2; color: white; padding: 5px 12px; border-radius: 30px; font-size: 12px; font-weight: 600; box-shadow: 0 4px 8px rgba(110, 69, 226, 0.3);">TOP #2</div>
                        <div style="padding: 25px 20px 20px 20px;">
                            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                                <div style="width: 50px; height: 50px; border-radius: 50%; background: linear-gradient(45deg, #5851DB, #833AB4, #C13584); display: flex; align-items: center; justify-content: center; margin-right: 15px; flex-shrink: 0;">
                                    <span style="font-size: 24px; color: white;">🥈</span>
                                </div>
                                <div>
                                    <h4 style="margin: 0 0 5px 0; color: #333; font-size: 18px;">Segundo Melhor Conteúdo</h4>
                                    <p style="margin: 0; color: #666; font-size: 13px;">Alto desempenho na plataforma</p>
                                </div>
                            </div>
                            <div style="text-align: center; margin-top: 10px; margin-bottom: 15px;">
                                <a href="{url_for_button_2}" target="_blank" style="background: #1a73e8; color: white; text-decoration: none; padding: 10px 15px; border-radius: 5px; font-weight: 500; display: inline-block; transition: all 0.3s;">
                                    Ver no Instagram <span style="margin-left: 5px;">➔</span>
                                </a>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                        
                except Exception as e:
                    st.error(f"Erro ao carregar o segundo conteúdo: {str(e)}")
            
            # Removido o espaçamento adicional após os cards
            
        else:
            st.warning("Dados incompletos para Captação Digital.")


    st.markdown("---")
    st.markdown("<div class='footer-custom'>Dashboard - Indicadores de Crescimento - Metas - Versão 1.3 © Innovatis 2025</div>", unsafe_allow_html=True)
