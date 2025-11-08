# Sistema de Análise CSV com IA - Versão Minimalista
# Layout estilo Apple com SHADCN

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from scipy import stats
import json
import time
from datetime import datetime
import io
import base64
import os
import uuid

# Importações para chat e UI moderna
from streamlit_chat import message
from streamlit_option_menu import option_menu

# Importações para teste de API
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from groq import Groq
except ImportError:
    Groq = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

try:
    import requests
    # Perplexity não tem biblioteca oficial, usaremos requests
    Perplexity = "requests_available"
except ImportError:
    Perplexity = None

# Importar nova arquitetura
from data_manager import data_manager
from chat_ai_enhanced import EnhancedChatAI
from crewai_enhanced import get_crewai_instance
from cache_system import cache_system

# Importar gerador de relatórios
from Relatorios_appCSV.report_generator import ReportGenerator, generate_pdf_report, generate_markdown_report

# Importar visualizações avançadas
from visualization_enhanced import show_enhanced_visualizations, generate_visualization_insights

# =============================================================================
# CONFIGURAÇÃO DA PÁGINA - ESTILO APPLE
# =============================================================================

st.set_page_config(
    page_title="CSV Analysis AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado estilo Apple
st.markdown("""
<style>
    /* Reset e base */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Header minimalista */
    .header-container {
        text-align: center;
        margin-bottom: 3rem;
        padding: 2rem 0;
        border-bottom: 1px solid #2C5F5D;
        background: linear-gradient(135deg, #2C5F5D 0%, #4A7C7A 100%);
        border-radius: 12px;
        color: white;
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 600;
        color: white;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .header-subtitle {
        font-size: 1.1rem;
        color: #E8F4F3;
        margin-top: 0.5rem;
        font-weight: 400;
    }
    
    /* Chat container estilo ChatGPT */
    .chat-container {
        background: transparent;
        border-radius: 12px;
        border: none;
        padding: 0;
        margin: 0;
        box-shadow: none;
    }
    
    /* Linha elegante abaixo do título do chat */
    .chat-title-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, #e5e5e7 20%, #e5e5e7 80%, transparent 100%);
        margin: 1rem 0 2rem 0;
        border: none;
    }
    
    /* Botões estilo Apple */
    .stButton > button {
        background: #2C5F5D;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background: #1A4A48;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(44, 95, 93, 0.3);
    }
    
    /* Sidebar minimalista */
    .css-1d391kg {
        background: #f5f5f7;
    }
    
    /* Reduzir espaçamentos na sidebar */
    .css-1d391kg .stMarkdown {
        margin-bottom: 0.5rem;
    }
    
    .css-1d391kg .stSelectbox,
    .css-1d391kg .stTextInput,
    .css-1d391kg .stButton {
        margin-bottom: 0.5rem;
    }
    
    .css-1d391kg .stDivider {
        margin: 0.5rem 0;
    }
    
    .css-1d391kg h3 {
        margin-bottom: 0.5rem;
    }
    
    /* Cards de informação */
    .info-card {
        background: linear-gradient(135deg, #2C5F5D 0%, #4A7C7A 100%);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #2C5F5D;
        box-shadow: 0 4px 12px rgba(44, 95, 93, 0.3);
        color: white;
    }
    
    .info-card h3 {
        color: white;
        font-weight: 600;
    }
    
    .info-card p, .info-card li {
        color: #E8F4F3;
    }
    
    .info-card strong {
        color: white;
        font-weight: 600;
    }
    
    /* Status indicators */
    .status-success {
        color: #30d158;
        font-weight: 500;
    }
    
    .status-error {
        color: #ff3b30;
        font-weight: 500;
    }
    
    .status-warning {
        color: #ff9500;
        font-weight: 500;
    }
    
    /* Typography */
    h1, h2, h3 {
        color: #1d1d1f;
        font-weight: 600;
        letter-spacing: -0.01em;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def load_csv_data(uploaded_files):
    """Carrega dados CSV dos arquivos enviados usando o DataManager"""
    return data_manager.load_csv(uploaded_files)


def save_conversation_to_json(conversation_data):
    """Salva a conversação em formato JSON"""
    try:
        # Criar estrutura da conversação
        conversation = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "session_id": str(uuid.uuid4()),
                "total_messages": len(conversation_data.get('messages', [])),
                "analysis_id": conversation_data.get('analysis_id'),
                "csv_file": conversation_data.get('csv_file')
            },
            "conversation": conversation_data.get('messages', []),
            "analysis_results": conversation_data.get('analysis_results', {})
        }
        
        # Converter para JSON
        json_data = json.dumps(conversation, indent=2, ensure_ascii=False)
        return json_data
    except Exception as e:
        st.error(f"Erro ao salvar conversação: {str(e)}")
        return None

def download_json_file(json_data, filename):
    """Cria um botão de download para arquivo JSON"""
    if json_data:
        # Codificar em base64
        b64 = base64.b64encode(json_data.encode('utf-8')).decode()
        
        # Criar link de download
        href = f'<a href="data:application/json;base64,{b64}" download="{filename}">📥 Baixar {filename}</a>'
        st.markdown(href, unsafe_allow_html=True)

def show_suggestions():
    """Mostrar sugestões de perguntas"""
    st.markdown("""
    <div class="suggestions-container">
        <h4>💡 Sugestões de Perguntas:</h4>
        <ul>
            <li>Quais são os tipos de dados das colunas?</li>
            <li>Quantos registros existem no dataset?</li>
            <li>Quais colunas têm valores ausentes?</li>
            <li>Mostre a distribuição da coluna [nome_da_coluna]</li>
            <li>Quais são os valores únicos em [coluna_categórica]?</li>
            <li>Calcule estatísticas descritivas das colunas numéricas</li>
            <li>Identifique possíveis outliers nos dados</li>
            <li>Mostre a correlação entre variáveis numéricas</li>
            <li>Qual é a tendência temporal dos dados?</li>
            <li>Resuma os principais insights dos dados</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def show_simple_chat_interface(df):
    """Interface do chat simplificado"""
    st.markdown("### 💬 Chat com IA")
    st.markdown('<hr class="chat-title-divider">', unsafe_allow_html=True)
    
    # Botão para executar análise CrewAI
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("🚀 Executar Análise CrewAI", use_container_width=True):
            # Obter credenciais da sidebar
            api_provider = st.session_state.get('api_provider', 'OpenAI')
            api_key = st.session_state.get('api_key', '')
            
            if not api_key:
                st.error("❌ Configure uma API key na sidebar primeiro!")
                return
                
            with st.spinner("Executando análise com agentes CrewAI..."):
                # Debug: verificar se a chave está sendo passada
                st.write(f"🔍 Debug: Provedor: {api_provider}, Chave: {api_key[:10]}...")
                
                # Criar nova instância do CrewAI
                crewai_instance = get_crewai_instance()
                results = crewai_instance.run_analysis("Análise CrewAI", api_provider, api_key)
                if results:
                    st.success("✅ Análise CrewAI concluída!")
                    st.info("Agora você pode fazer perguntas sobre os insights dos agentes.")
    
    with col2:
        # Mostrar status da API
        api_provider = st.session_state.get('api_provider', 'OpenAI')
        api_key = st.session_state.get('api_key', '')
        if api_key:
            st.success(f"✅ {api_provider} configurado")
        else:
            st.warning("⚠️ API não configurada")
    
    # Mostrar sugestões
    show_suggestions()
    
    # Inicializar conversação no session_state se não existir
    if 'conversation' not in st.session_state:
        st.session_state.conversation = []
    
    # Input do usuário
    user_message = st.text_input("Digite sua pergunta:", placeholder="Ex: Quais são os tipos de dados das colunas?")
    
    if user_message:
        # Obter credenciais da sidebar
        api_provider = st.session_state.get('api_provider', 'OpenAI')
        api_key = st.session_state.get('api_key', '')
        
        if not api_key:
            st.error("❌ Configure uma API key na sidebar primeiro!")
            return
        
        # Gerar resposta usando EnhancedChatAI
        chat_ai = EnhancedChatAI(api_provider, api_key)
        response = chat_ai.generate_enhanced_response(user_message, df)
        
        # Inicializar variáveis
        response_text = None
        chart = None
        
        # Mostrar resposta (response é uma tupla: (texto, gráfico))
        st.markdown("#### 🤖 Resposta:")
        if isinstance(response, tuple):
            response_text, chart = response
            st.write(response_text)
            
            # Mostrar gráfico se houver
            if chart:
                st.plotly_chart(chart, use_container_width=True)
        else:
            response_text = response
            st.write(response)
        
        # Salvar na conversação
        st.session_state.conversation.append({
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "ai_response": response_text,
            "has_chart": chart is not None
        })
    
    # Botão para download da conversação em JSON
    if st.session_state.conversation:
        st.markdown("---")
        st.markdown("### 📥 Download da Conversação")
        
        # Preparar dados da conversação
        conversation_data = {
            "messages": st.session_state.conversation,
            "analysis_id": st.session_state.get('current_analysis_id'),
            "csv_file": st.session_state.get('current_csv_file', 'unknown'),
            "analysis_results": {}
        }
        
        # Adicionar resultados da análise se disponível
        from analysis_memory import analysis_memory
        if analysis_memory.current_analysis:
            results = analysis_memory.get_analysis_results(analysis_memory.current_analysis)
            if results:
                conversation_data["analysis_results"] = results
        
        # Gerar JSON
        json_data = save_conversation_to_json(conversation_data)
        
        if json_data:
            # Nome do arquivo com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversacao_analise_{timestamp}.json"
            
            # Botão de download
            download_json_file(json_data, filename)
            
            # Mostrar estatísticas da conversação
            st.info(f"💬 Conversação com {len(st.session_state.conversation)} mensagens")
            
            # Botão para limpar conversação
            if st.button("🗑️ Limpar Conversação"):
                st.session_state.conversation = []
                st.rerun()

def show_conclusions_interface():
    """Interface para mostrar conclusões dos agentes CrewAI"""
    from analysis_memory import analysis_memory
    
    # Botão para limpar análises antigas
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🗑️ Limpar Histórico"):
            analysis_memory.clear_analysis_memory()
            st.success("✅ Histórico de análises limpo!")
            st.rerun()
    
    # CORREÇÃO: Mostrar automaticamente a análise ATUAL (mais recente)
    # em vez de forçar o usuário a selecionar de uma lista de análises antigas
    current_analysis_id = analysis_memory.current_analysis
    
    if not current_analysis_id:
        st.info("📋 Nenhuma análise CrewAI disponível. Execute uma análise primeiro.")
        return
    
    # Obter resultados da análise atual
    results = analysis_memory.get_analysis_results(current_analysis_id)
    
    if results:
        # Mostrar informações da análise atual
        data_summary = results.get('data_summary', {})
        st.markdown(f"### 📊 Análise Atual: {results.get('analysis_name', 'Análise CrewAI')}")
        st.markdown(f"**Data:** {results.get('timestamp', 'N/A')}")
        st.markdown(f"**Dataset analisado:** {data_summary.get('rows', 0)} registros × {data_summary.get('columns', 0)} colunas")
        
        # Mostrar colunas analisadas
        if data_summary.get('column_names'):
            with st.expander("📋 Colunas Analisadas", expanded=False):
                st.write(", ".join(data_summary.get('column_names', [])))
        
        st.markdown("---")
        
        # Obter resultados dos agentes
        crew_results = results.get('crew_results', {})
        
        if crew_results:
            # Verificar se há agentes nos resultados
            agents = crew_results.get('agents', {})
            
            if agents:
                st.markdown("### 🤖 Conclusões dos Agentes")
                
                for agent_key, agent_result in agents.items():
                    # Mapear chaves dos agentes para nomes amigáveis
                    agent_names = {
                        'data_validator': '🔍 Data Validator',
                        'data_profiler': '📊 Data Profiler', 
                        'pattern_detective': '🎯 Pattern Detective',
                        'anomaly_hunter': '⚠️ Anomaly Hunter',
                        'relationship_analyst': '🔗 Relationship Analyst',
                        'strategic_synthesizer': '💡 Strategic Synthesizer',
                        'synthesis': '💡 Strategic Synthesizer',
                        'complete_analysis': '📋 Complete Analysis'
                    }
                    
                    agent_name = agent_names.get(agent_key, agent_key.replace('_', ' ').title())
                    
                    with st.expander(f"{agent_name}", expanded=True):
                        if isinstance(agent_result, dict):
                            result_text = agent_result.get('result', agent_result.get('output', 'Nenhum resultado disponível'))
                            st.markdown(result_text)
                        else:
                            st.markdown(str(agent_result))
            else:
                # Resultados antigos sem estrutura de agentes
                st.warning("⚠️ Formato de resultados desatualizado. Execute uma nova análise.")
        else:
            st.warning("⚠️ Nenhum resultado encontrado nesta análise.")
    else:
        st.warning("⚠️ Não foi possível carregar os resultados da análise atual.")
    
    # Seção opcional para ver análises antigas (colapsada por padrão)
    with st.expander("📚 Ver Análises Anteriores", expanded=False):
        analysis_history = analysis_memory.get_analysis_history()
        
        if not analysis_history:
            st.info("Nenhuma análise anterior disponível.")
        else:
            # Converter dicionário para lista de análises
            analyses_list = []
            for analysis_id, analysis_data in analysis_history.items():
                if analysis_id != current_analysis_id:  # Não mostrar a atual
                    analyses_list.append({
                        'id': analysis_id,
                        'name': analysis_data.get('analysis_name', f'Análise {analysis_id[:8]}'),
                        'date': analysis_data.get('timestamp', 'Data não disponível'),
                        'status': analysis_data.get('status', 'unknown')
                    })
            
            if analyses_list:
                # Selecionar análise anterior
                analysis_names = [f"{a['name']} ({a['date']})" for a in analyses_list]
                selected_idx = st.selectbox("Selecione uma análise anterior:", range(len(analysis_names)), format_func=lambda i: analysis_names[i])
                
                if selected_idx is not None:
                    selected_analysis = analyses_list[selected_idx]
                    old_analysis_id = selected_analysis['id']
                    old_results = analysis_memory.get_analysis_results(old_analysis_id)
                    
                    if old_results and 'crew_results' in old_results:
                        st.markdown(f"### 📊 {selected_analysis['name']}")
                        st.markdown(f"**Data:** {selected_analysis['date']}")
                        
                        # Mostrar resultados dos agentes antigos
                        old_crew_results = old_results['crew_results']
                        
                        # Verificar se tem estrutura nova ou antiga
                        if 'agents' in old_crew_results:
                            agents = old_crew_results['agents']
                            for agent_key, agent_result in agents.items():
                                agent_names = {
                                    'data_validator': '🔍 Data Validator',
                                    'data_profiler': '📊 Data Profiler', 
                                    'pattern_detective': '🎯 Pattern Detective',
                                    'anomaly_hunter': '⚠️ Anomaly Hunter',
                                    'relationship_analyst': '🔗 Relationship Analyst',
                                    'strategic_synthesizer': '💡 Strategic Synthesizer'
                                }
                                agent_name = agent_names.get(agent_key, agent_key.replace('_', ' ').title())
                                with st.expander(f"{agent_name}", expanded=False):
                                    if isinstance(agent_result, dict):
                                        st.markdown(agent_result.get('result', 'Nenhum resultado disponível'))
                                    else:
                                        st.markdown(str(agent_result))
                        else:
                            # Formato antigo
                            for agent_key, agent_result in old_crew_results.items():
                                with st.expander(f"🤖 {agent_key}", expanded=False):
                                    st.write(agent_result)
                    else:
                        st.warning("⚠️ Nenhum resultado encontrado para esta análise.")
            else:
                st.info("Nenhuma análise anterior disponível (somente a análise atual existe).")

def show_minimal_overview(df):
    """Overview minimalista dos dados"""
    if df is None:
        st.info("📁 Carregue um arquivo CSV para ver a visão geral")
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Registros", f"{len(df):,}")
    
    with col2:
        st.metric("📋 Colunas", f"{len(df.columns)}")
    
    with col3:
        missing = df.isnull().sum().sum()
        st.metric("⚠️ Valores Faltantes", f"{missing:,}")
    
    with col4:
        duplicates = df.duplicated().sum()
        st.metric("🔄 Duplicatas", f"{duplicates:,}")
    
    # Tipos de dados - Gráfico maior
    st.subheader("📈 Distribuição dos Tipos de Dados")
    dtype_counts = df.dtypes.value_counts()
    fig = px.pie(
        values=dtype_counts.values,
        names=[str(dtype) for dtype in dtype_counts.index],
        title="Distribuição dos Tipos de Dados",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_layout(
        showlegend=True, 
        height=500,
        title_font_size=16,
        font_size=12
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Dados de Perfilamento
    st.subheader("🔍 Perfilamento dos Dados")
    
    # Análise de correlação
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) >= 2:
        st.markdown("**📊 Matriz de Correlação**")
        corr_matrix = df[numeric_cols].corr()
        
        # Criar heatmap de correlação
        fig_corr = px.imshow(
            corr_matrix,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="RdBu_r",
            title="Matriz de Correlação entre Variáveis Numéricas"
        )
        fig_corr.update_layout(height=500)
        st.plotly_chart(fig_corr, use_container_width=True)
    
    # Estatísticas por tipo de coluna
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Colunas Numéricas**")
        if len(numeric_cols) > 0:
            for col in numeric_cols[:5]:  # Mostrar até 5 colunas
                stats = df[col].describe()
                st.write(f"**{col}**:")
                st.write(f"  - Média: {stats['mean']:.2f}")
                st.write(f"  - Mediana: {stats['50%']:.2f}")
                st.write(f"  - Desvio Padrão: {stats['std']:.2f}")
                st.write(f"  - Min: {stats['min']:.2f} | Max: {stats['max']:.2f}")
                st.write("")
        else:
            st.info("Nenhuma coluna numérica encontrada")
    
    with col2:
        st.markdown("**📋 Colunas Categóricas**")
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            for col in categorical_cols[:5]:  # Mostrar até 5 colunas
                unique_count = df[col].nunique()
                most_common = df[col].mode().iloc[0] if len(df[col].mode()) > 0 else "N/A"
                st.write(f"**{col}**:")
                st.write(f"  - Valores únicos: {unique_count}")
                st.write(f"  - Mais comum: {most_common}")
                st.write(f"  - Valores faltantes: {df[col].isnull().sum()}")
                st.write("")
        else:
            st.info("Nenhuma coluna categórica encontrada")
    
    # Qualidade dos dados
    st.subheader("📋 Qualidade dos Dados")
    quality_col1, quality_col2, quality_col3 = st.columns(3)
    
    with quality_col1:
        st.metric("✅ Completude", f"{((len(df) - df.isnull().sum().sum()) / (len(df) * len(df.columns)) * 100):.1f}%")
    
    with quality_col2:
        st.metric("🔄 Unicidade", f"{((len(df) - df.duplicated().sum()) / len(df) * 100):.1f}%")
    
    with quality_col3:
        numeric_ratio = len(numeric_cols) / len(df.columns) * 100
        st.metric("📊 % Numéricas", f"{numeric_ratio:.1f}%")

def show_sidebar():
    """Sidebar minimalista"""
    with st.sidebar:
        st.markdown("### ⚙️ Configurações")
        
        # API Selection
        api_provider = st.selectbox(
            "🔑 Provedor de IA",
            ["OpenAI", "GROQ", "Gemini", "Claude", "Perplexity"],
            help="Selecione qual API de IA usar"
        )
        
        # Salvar no session_state
        st.session_state['api_provider'] = api_provider
        
        # API Key
        api_key = st.text_input(
            f"Chave da API {api_provider}:",
            type="password",
            help="Insira sua chave de API"
        )
        
        # Salvar no session_state
        st.session_state['api_key'] = api_key
        
        # Test API Button
        if st.button("🧪 Testar API", use_container_width=True):
            if api_key:
                with st.spinner("Testando..."):
                    try:
                        if api_provider == "OpenAI" and OpenAI:
                            client = OpenAI(api_key=api_key)
                            models = client.models.list()
                            st.success("✅ API funcionando!")
                        elif api_provider == "GROQ" and Groq:
                            client = Groq(api_key=api_key)
                            models = client.models.list()
                            st.success("✅ API funcionando!")
                        elif api_provider == "Gemini" and genai:
                            genai.configure(api_key=api_key)
                            model = genai.GenerativeModel('gemini-2.5-flash-lite-preview-09-2025')
                            response = model.generate_content("Teste de conexão")
                            st.success("✅ API funcionando!")
                        elif api_provider == "Claude" and Anthropic:
                            client = Anthropic(api_key=api_key)
                            response = client.messages.create(
                                model="claude-3-sonnet-20240229",
                                max_tokens=10,
                                messages=[{"role": "user", "content": "Teste"}]
                            )
                            st.success("✅ API funcionando!")
                        elif api_provider == "Perplexity" and Perplexity:
                            import requests
                            headers = {
                                "Authorization": f"Bearer {api_key}",
                                "Content-Type": "application/json"
                            }
                            data = {
                                "model": "llama-3.1-sonar-small-128k-online",
                                "messages": [{"role": "user", "content": "Teste"}],
                                "max_tokens": 10
                            }
                            response = requests.post(
                                "https://api.perplexity.ai/chat/completions",
                                headers=headers,
                                json=data
                            )
                            if response.status_code == 200:
                                st.success("✅ API funcionando!")
                            else:
                                st.error(f"❌ Erro: {response.status_code}")
                        else:
                            st.info("ℹ️ Biblioteca não instalada ou API não suportada")
                    except Exception as e:
                        st.error(f"❌ Erro: {str(e)}")
            else:
                st.error("❌ Insira uma chave de API")
        
        # File Upload
        st.markdown("### 📁 Arquivos")
        uploaded_files = st.file_uploader(
            "Carregar CSV",
            type=['csv'],
            accept_multiple_files=True,
            help="Selecione arquivos CSV para análise"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} arquivo(s) carregado(s)")
        
        # Analysis Info
        st.markdown("### 🏷️ Análise")
        analysis_name = st.text_input(
            "Nome da análise:",
            value=f"Análise - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )
        
        # Cache Management
        st.markdown("### 🗄️ Cache")
        if st.button("🧹 Limpar Cache", use_container_width=True):
            cache_system.clear_all()
        
        # Mostrar estatísticas do cache
        cache_stats = cache_system.get_cache_stats()
        if cache_stats['total_items'] > 0:
            st.info(f"📊 Cache: {cache_stats['total_items']} itens")
        
        # Reports
        st.markdown("### 📄 Relatórios")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 PDF", use_container_width=True):
                if uploaded_files:
                    df = load_csv_data(uploaded_files)
                    if df is not None:
                        try:
                            with st.spinner("Gerando relatório PDF..."):
                                # Coletar dados de conversação se disponíveis
                                conversation_data = {
                                    'messages': st.session_state.get('conversation', [])
                                }
                                
                                # Coletar dados de overview
                                overview_data = {
                                    'data_quality': (df.count().sum() / (len(df) * len(df.columns)) * 100),
                                    'numeric_columns': len(df.select_dtypes(include=[np.number]).columns),
                                    'categorical_columns': len(df.select_dtypes(include=['object']).columns),
                                    'insights': [
                                        f"Dataset com {len(df):,} registros e {len(df.columns)} colunas",
                                        f"Completude geral: {(df.count().sum() / (len(df) * len(df.columns)) * 100):.1f}%",
                                        f"Valores faltantes: {df.isnull().sum().sum()}",
                                        f"Duplicatas: {df.duplicated().sum()}"
                                    ]
                                }
                                
                                # Obter conclusões dos agentes CrewAI se disponíveis
                                crewai_conclusions = None
                                try:
                                    available_analyses = data_manager.get_available_analyses()
                                    if available_analyses:
                                        # Usar a primeira análise disponível
                                        analysis_name = available_analyses[0]
                                        crewai_conclusions = data_manager.load_analysis(analysis_name)
                                        if not crewai_conclusions:
                                            st.warning("⚠️ Nenhuma conclusão de agente encontrada. Execute uma análise CrewAI primeiro.")
                                    else:
                                        st.warning("⚠️ Nenhuma análise CrewAI ativa. Execute uma análise primeiro.")
                                except Exception as e:
                                    st.warning(f"Não foi possível obter conclusões dos agentes: {e}")
                                
                                # Limpar nome do arquivo para evitar caracteres problemáticos
                                safe_filename = "".join(c for c in analysis_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                                if not safe_filename:
                                    safe_filename = "relatorio_analise"
                                
                                pdf_data = generate_pdf_report(df, safe_filename, "", None, conversation_data, overview_data, crewai_conclusions)
                                st.download_button(
                                    "📥 Download PDF",
                                    pdf_data,
                                    file_name=f"{safe_filename}.pdf",
                                    mime="application/pdf"
                                )
                                st.success("✅ Relatório PDF gerado com sucesso!")
                                
                                # Informações sobre o relatório
                                st.info(f"""
                                **📄 Relatório PDF Gerado:**
                                - **Arquivo:** {safe_filename}.pdf
                                - **Registros analisados:** {len(df):,}
                                - **Colunas:** {len(df.columns)}
                                - **Mensagens de conversa:** {len(conversation_data) if conversation_data else 0}
                                - **Conclusões dos agentes:** {len(crewai_conclusions) if crewai_conclusions else 0}
                                """)
                                
                                # Seção de retorno à análise
                                st.markdown("---")
                                st.markdown("### 🔄 Navegação")
                                col_return1, col_return2 = st.columns([1, 1])
                                
                                with col_return1:
                                    if st.button("🔄 Retornar à Análise", use_container_width=True, key="return_from_pdf"):
                                        st.rerun()
                                
                                with col_return2:
                                    if st.button("📊 Ver Overview", use_container_width=True, key="view_overview_from_pdf"):
                                        st.session_state['show_overview'] = True
                                        st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao gerar PDF: {str(e)}")
                            st.error("Dica: Verifique se o arquivo CSV não contém caracteres especiais problemáticos.")
        
        with col2:
            if st.button("📝 Markdown", use_container_width=True):
                if uploaded_files:
                    df = load_csv_data(uploaded_files)
                    if df is not None:
                        try:
                            with st.spinner("Gerando relatório Markdown..."):
                                # Coletar dados de conversação se disponíveis
                                conversation_data = {
                                    'messages': st.session_state.get('conversation', [])
                                }
                                
                                # Coletar dados de overview
                                overview_data = {
                                    'data_quality': (df.count().sum() / (len(df) * len(df.columns)) * 100),
                                    'numeric_columns': len(df.select_dtypes(include=[np.number]).columns),
                                    'categorical_columns': len(df.select_dtypes(include=['object']).columns),
                                    'insights': [
                                        f"Dataset com {len(df):,} registros e {len(df.columns)} colunas",
                                        f"Completude geral: {(df.count().sum() / (len(df) * len(df.columns)) * 100):.1f}%",
                                        f"Valores faltantes: {df.isnull().sum().sum()}",
                                        f"Duplicatas: {df.duplicated().sum()}"
                                    ]
                                }
                                
                                # Obter conclusões dos agentes CrewAI se disponíveis
                                crewai_conclusions = None
                                try:
                                    available_analyses = data_manager.get_available_analyses()
                                    if available_analyses:
                                        # Usar a primeira análise disponível
                                        analysis_name = available_analyses[0]
                                        crewai_conclusions = data_manager.load_analysis(analysis_name)
                                        if not crewai_conclusions:
                                            st.warning("⚠️ Nenhuma conclusão de agente encontrada. Execute uma análise CrewAI primeiro.")
                                    else:
                                        st.warning("⚠️ Nenhuma análise CrewAI ativa. Execute uma análise primeiro.")
                                except Exception as e:
                                    st.warning(f"Não foi possível obter conclusões dos agentes: {e}")
                                
                                # Limpar nome do arquivo para evitar caracteres problemáticos
                                safe_filename = "".join(c for c in analysis_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                                if not safe_filename:
                                    safe_filename = "relatorio_analise"
                                
                                markdown_data = generate_markdown_report(df, safe_filename, "", None, conversation_data, overview_data, crewai_conclusions)
                                st.download_button(
                                    "📥 Download Markdown",
                                    markdown_data,
                                    file_name=f"{safe_filename}.md",
                                    mime="text/markdown"
                                )
                                st.success("✅ Relatório Markdown gerado com sucesso!")
                                
                                # Informações sobre o relatório
                                st.info(f"""
                                **📝 Relatório Markdown Gerado:**
                                - **Arquivo:** {safe_filename}.md
                                - **Registros analisados:** {len(df):,}
                                - **Colunas:** {len(df.columns)}
                                - **Mensagens de conversa:** {len(conversation_data) if conversation_data else 0}
                                - **Conclusões dos agentes:** {len(crewai_conclusions) if crewai_conclusions else 0}
                                """)
                                
                                # Seção de retorno à análise
                                st.markdown("---")
                                st.markdown("### 🔄 Navegação")
                                col_return1, col_return2 = st.columns([1, 1])
                                
                                with col_return1:
                                    if st.button("🔄 Retornar à Análise", use_container_width=True, key="return_from_markdown"):
                                        st.rerun()
                                
                                with col_return2:
                                    if st.button("📊 Ver Overview", use_container_width=True, key="view_overview_from_markdown"):
                                        st.session_state['show_overview'] = True
                                        st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao gerar Markdown: {str(e)}")
                            st.error("Dica: Verifique se o arquivo CSV não contém caracteres especiais problemáticos.")
        
        return uploaded_files, api_provider, api_key, analysis_name

# =============================================================================
# FUNÇÃO PRINCIPAL
# =============================================================================

def main():
    # Header minimalista
    st.markdown("""
    <div class="header-container">
        <h1 class="header-title">🤖 CSV Analysis AI</h1>
        <p class="header-subtitle">Análise inteligente de dados com agentes de IA</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    uploaded_files, api_provider, api_key, analysis_name = show_sidebar()
    
    # Main content
    if uploaded_files:
        df = load_csv_data(uploaded_files)
        
        if df is not None:
            # Menu de navegação principal
            selected = option_menu(
                menu_title=None,
                options=["💬 Chat IA", "🎯 Conclusões", "📊 Overview", "📈 Visualizações"],
                icons=["chat-dots", "target", "bar-chart", "chart-line"],
                menu_icon="cast",
                default_index=0,
                orientation="horizontal",
                styles={
                    "container": {"padding": "0!important", "background-color": "#f5f5f7"},
                    "icon": {"color": "#2C5F5D", "font-size": "18px"},
                    "nav-link": {
                        "font-size": "16px",
                        "text-align": "center",
                        "margin": "0px",
                        "--hover-color": "#E8F4F3",
                        "color": "#1d1d1f",
                        "font-weight": "500"
                    },
                    "nav-link-selected": {
                        "background-color": "#2C5F5D",
                        "color": "#ffffff",
                        "font-weight": "600"
                    },
                }
            )
            
            if selected == "💬 Chat IA":
                show_simple_chat_interface(df)
                    
            elif selected == "🎯 Conclusões":
                st.markdown("### 🎯 Conclusões dos Agentes CrewAI")
                st.markdown('<hr class="chat-title-divider">', unsafe_allow_html=True)
                show_conclusions_interface()
                
            elif selected == "📊 Overview":
                st.markdown("### 📊 Visão Geral dos Dados")
                show_minimal_overview(df)
                
            elif selected == "📈 Visualizações":
                st.markdown("### 📈 Visualizações Avançadas")
                st.markdown('<hr class="chat-title-divider">', unsafe_allow_html=True)
                show_enhanced_visualizations(df)
                
    
    else:
        # Tela inicial
        st.markdown("""
        <div class="info-card">
            <h3>🎯 Bem-vindo ao CSV Analysis AI</h3>
            <p>Esta é uma ferramenta de análise de dados com inteligência artificial que permite:</p>
            <ul>
                <li>💬 <strong>Chat com Agentes IA:</strong> Faça perguntas sobre seus dados em linguagem natural</li>
                <li>🎯 <strong>Conclusões dos Agentes:</strong> Consulte insights e descobertas dos agentes CrewAI</li>
                <li>📊 <strong>Overview Inteligente:</strong> Visualização clara e objetiva dos seus dados</li>
                <li>📈 <strong>Visualizações Avançadas:</strong> Gráficos e análises visuais dos dados</li>
                <li>📄 <strong>Relatórios Automáticos:</strong> Geração de relatórios em PDF e Markdown</li>
            </ul>
            <p><strong>Para começar:</strong> Carregue um arquivo CSV na barra lateral e comece a conversar com nossos agentes de IA!</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
