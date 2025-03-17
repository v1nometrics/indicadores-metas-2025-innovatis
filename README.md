# Dashboard de Indicadores de Crescimento - Metas 2025

Este é um dashboard Streamlit para visualização mensal dos indicadores de crescimento da empresa. O dashboard se conecta automaticamente ao Google Sheets para obter os dados atualizados, utilizando credenciais armazenadas no AWS S3.

## Requisitos

- Python 3.8+
- Bibliotecas Python listadas em `requirements.txt`
- Acesso ao AWS S3
- Conta de serviço do Google Cloud

## Configuração Rápida

1. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

2. Configure as credenciais do Google Sheets e AWS S3 conforme descrito no arquivo `INSTRUCOES_CONFIGURACAO.md`

3. Configure a planilha do Google Sheets conforme descrito no arquivo `google_sheets_structure.md`

4. Atualize as configurações no arquivo `config.py`

## Instruções Detalhadas

Para instruções detalhadas sobre como configurar o dashboard e solucionar problemas comuns, consulte o arquivo `INSTRUCOES_CONFIGURACAO.md`.

## Execução

Para iniciar o dashboard, execute:

```
streamlit run app.py
```

## Estrutura do Projeto

- `app.py`: Aplicação principal do Streamlit
- `utils/`: Módulos utilitários
  - `sheets_connector.py`: Módulo para conexão com o Google Sheets via S3
  - `data_processor.py`: Módulo para processamento dos dados
  - `visualizations.py`: Módulo para criação de visualizações
- `config.py`: Configurações do projeto (AWS S3, Google Sheets, etc.)
- `google_sheets_structure.md`: Descrição da estrutura necessária para a planilha do Google Sheets
- `INSTRUCOES_CONFIGURACAO.md`: Instruções detalhadas de configuração e solução de problemas
- `exemplo_planilha.csv`: Exemplo da estrutura da planilha em formato CSV

## Funcionalidades

### Meta de Faturamento Anual
- Visualização do faturamento atual em relação às metas estabelecidas
- Barra de progresso animada com marcos de metas
- Programa de reconhecimento INNOVASTAR com benefícios por meta atingida

### Relacionamento
- Métricas de parceiros (Fundações e IFES)
- Visualização de progresso em relação às metas de 2025
- Gráficos de gauge para acompanhamento percentual

### Desenvolvimento de Plataformas
- Acompanhamento do desenvolvimento de 5 plataformas principais:
  - Plataforma de Oportunidades
  - Gestão de Projetos
  - Gamificação do Relacionamento
  - Plataforma de Produtos
  - Escrita de Projetos/Produtos
- Gráficos circulares de progresso com feedback da última atualização

### Funil de Vendas
- Visualização completa do funil de vendas com 6 estágios
- Métricas de conversão entre etapas
- Tempo médio de cada etapa do funil
- Resumo com métricas-chave:
  - Total de oportunidades e contratos
  - Taxa de conversão total
  - Tempo médio total (exceto execução)
- Identificação de gargalos no processo de vendas

### Captação Digital
- Métricas de Instagram e Website
- Visualização de alcance, impressões e cliques
- Variações percentuais em relação ao período anterior

## Design e Usabilidade
- Interface moderna com fonte Poppins
- Layout responsivo e adaptável
- Cards de métricas com design elegante
- Visualizações interativas com Plotly
- Cores consistentes e agradáveis à visão 
