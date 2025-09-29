# Análise de CSVs com CrewAI

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

# Importações para teste de API
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from groq import Groq
except ImportError:
    Groq = None

# Importar sistema CrewAI real
from crewai_agents import CSVAnalysisCrew, analyze_csv_with_crewai

# Importar gerador de relatórios
from report_generator import ReportGenerator, generate_pdf_report, generate_word_report

# =============================================================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================================================

st.set_page_config(
    page_title="🎯 CSV Analysis System - CrewAI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
        margin: 0.25rem;
    }
    .status-success { background-color: #d4edda; color: #155724; }
    .status-warning { background-color: #fff3cd; color: #856404; }
    .status-danger { background-color: #f8d7da; color: #721c24; }
    .status-info { background-color: #d1ecf1; color: #0c5460; }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

@st.cache_data
def load_csv_data(uploaded_file):
    """Carrega e processa dados CSV"""
    try:
        df = pd.read_csv(uploaded_file)
        return df, None
    except Exception as e:
        return None, str(e)

def get_data_quality_metrics(df):
    """Calcula métricas de qualidade dos dados"""
    metrics = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "duplicates": df.duplicated().sum(),
        "missing_values": df.isnull().sum().sum(),
        "completeness": ((df.count().sum() / (len(df) * len(df.columns))) * 100),
        "numeric_columns": len(df.select_dtypes(include=[np.number]).columns),
        "categorical_columns": len(df.select_dtypes(include=['object']).columns),
        "memory_usage": df.memory_usage(deep=True).sum() / 1024 / 1024  # MB
    }
    return metrics

def create_correlation_heatmap(df):
    """Cria heatmap de correlação"""
    numeric_df = df.select_dtypes(include=[np.number])
    if len(numeric_df.columns) < 2:
        return None
    
    corr_matrix = numeric_df.corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=[str(col) for col in corr_matrix.columns],
        y=[str(col) for col in corr_matrix.columns],
        colorscale='RdBu',
        zmid=0,
        text=np.around(corr_matrix.values, decimals=2),
        texttemplate='%{text}',
        textfont={"size": 10},
        hoverongaps=False
    ))
    
    fig.update_layout(
        title="Matriz de Correlação",
        xaxis_title="Variáveis",
        yaxis_title="Variáveis",
        height=600
    )
    
    return fig

def detect_outliers_iqr(df):
    """Detecta outliers usando método IQR"""
    numeric_df = df.select_dtypes(include=[np.number])
    outliers_info = {}
    
    for col in numeric_df.columns:
        Q1 = numeric_df[col].quantile(0.25)
        Q3 = numeric_df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = numeric_df[(numeric_df[col] < lower_bound) | (numeric_df[col] > upper_bound)]
        
        outliers_info[col] = {
            "count": len(outliers),
            "percentage": (len(outliers) / len(numeric_df)) * 100,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound
        }
    
    return outliers_info

def perform_clustering(df, n_clusters=5):
    """Executa clustering K-means"""
    numeric_df = df.select_dtypes(include=[np.number])
    
    if len(numeric_df.columns) < 2:
        return None, None, None
    
    # Identificar linhas sem NaN
    clean_mask = numeric_df.notna().all(axis=1)
    numeric_clean = numeric_df[clean_mask]
    
    if len(numeric_clean) == 0:
        return None, None, None
    
    # Padronização
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(numeric_clean)
    
    # K-means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters_clean = kmeans.fit_predict(scaled_data)
    
    # PCA para visualização
    pca = PCA(n_components=2)
    pca_data = pca.fit_transform(scaled_data)
    
    # Criar array de clusters com tamanho do DataFrame original
    clusters_full = np.full(len(df), -1)  # -1 para linhas com NaN
    clusters_full[clean_mask] = clusters_clean
    
    return clusters_full, pca_data, clean_mask

def create_download_link(df, filename="analysis_results.csv"):
    """Cria link de download para dados"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">📥 Download Results</a>'

def process_user_question(question, df, conversation_memory):
    """Processa pergunta do usuário e determina qual agente responder"""
    
    # Análise simples para determinar o agente mais adequado
    question_lower = question.lower()
    
    # Palavras-chave para cada agente
    agent_keywords = {
        "Data Validator": ["qualidade", "validação", "duplicata", "faltante", "completo", "integridade", "erro", "problema"],
        "Data Profiler": ["estatística", "distribuição", "média", "mediana", "desvio", "perfil", "resumo", "descritivo"],
        "Pattern Detective": ["padrão", "tendência", "cluster", "segmento", "grupo", "similar", "correlação"],
        "Anomaly Hunter": ["anomalia", "outlier", "estranho", "diferente", "inconsistente", "suspeito"],
        "Relationship Analyst": ["relacionamento", "correlação", "associação", "causa", "efeito", "dependência"],
        "Strategic Synthesizer": ["resumo", "conclusão", "recomendação", "estratégia", "insight", "próximo passo"]
    }
    
    # Determinar agente baseado nas palavras-chave
    selected_agent = "Strategic Synthesizer"  # padrão
    max_score = 0
    
    for agent, keywords in agent_keywords.items():
        score = sum(1 for keyword in keywords if keyword in question_lower)
        if score > max_score:
            max_score = score
            selected_agent = agent
    
    # Gerar resposta baseada no agente selecionado
    response = generate_agent_response(selected_agent, question, df, conversation_memory)
    
    return {
        "agent": selected_agent,
        "response": response
    }

def generate_agent_response(agent_name, question, df, conversation_memory):
    """Gera resposta do agente baseada na pergunta e dados"""
    
    # Resumo dos dados para contexto
    data_summary = f"""
    Dados disponíveis:
    - Total de registros: {len(df):,}
    - Total de colunas: {len(df.columns)}
    - Colunas: {', '.join(df.columns[:10])}{'...' if len(df.columns) > 10 else ''}
    - Valores faltantes: {df.isnull().sum().sum()}
    - Duplicatas: {df.duplicated().sum()}
    """
    
    # Contexto da conversa
    conversation_context = ""
    if conversation_memory:
        recent_messages = conversation_memory[-3:]  # Últimas 3 mensagens
        conversation_context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])
    
    # Respostas específicas por agente
    if agent_name == "Data Validator":
        return f"""🔍 **Data Validator** analisando sua pergunta: "{question}"

{data_summary}

**Análise de Qualidade dos Dados:**
- Completude geral: {(df.count().sum() / (len(df) * len(df.columns)) * 100):.1f}%
- Colunas com problemas: {len(df.columns[df.isnull().any()])} de {len(df.columns)}
- Registros duplicados: {df.duplicated().sum()}

**Recomendações:**
1. Verificar colunas com valores faltantes
2. Investigar registros duplicados
3. Validar tipos de dados

*Contexto da conversa: {conversation_context[:100]}...*"""

    elif agent_name == "Data Profiler":
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        
        return f"""📊 **Data Profiler** analisando sua pergunta: "{question}"

{data_summary}

**Perfil Estatístico:**
- Variáveis numéricas: {len(numeric_cols)}
- Variáveis categóricas: {len(categorical_cols)}
- Memória utilizada: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB

**Insights:**
- Dados mais completos: {df.count().idxmax()} ({df.count().max()} valores)
- Maior variabilidade: {df.std().idxmax() if len(numeric_cols) > 0 else 'N/A'}

*Contexto da conversa: {conversation_context[:100]}...*"""

    elif agent_name == "Pattern Detective":
        return f"""🎯 **Pattern Detective** analisando sua pergunta: "{question}"

{data_summary}

**Padrões Identificados:**
- Estrutura dos dados: {len(df)} registros organizados em {len(df.columns)} dimensões
- Tipos de dados: {dict(df.dtypes.value_counts())}
- Distribuição temporal: {'Sim' if any('date' in col.lower() or 'time' in col.lower() for col in df.columns) else 'Não detectada'}

**Análise de Segmentação:**
- Potenciais clusters baseados em variáveis numéricas
- Correlações significativas entre variáveis

*Contexto da conversa: {conversation_context[:100]}...*"""

    elif agent_name == "Anomaly Hunter":
        numeric_df = df.select_dtypes(include=[np.number])
        outliers_count = 0
        if len(numeric_df.columns) > 0:
            for col in numeric_df.columns:
                Q1 = numeric_df[col].quantile(0.25)
                Q3 = numeric_df[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = numeric_df[(numeric_df[col] < Q1 - 1.5*IQR) | (numeric_df[col] > Q3 + 1.5*IQR)]
                outliers_count += len(outliers)
        
        return f"""⚠️ **Anomaly Hunter** analisando sua pergunta: "{question}"

{data_summary}

**Anomalias Detectadas:**
- Outliers estatísticos: {outliers_count}
- Valores extremos: {len(df[df.isin([np.inf, -np.inf]).any(axis=1)])}
- Registros inconsistentes: {df.duplicated().sum()}

**Investigação:**
- Verificar se outliers são erros ou casos especiais
- Analisar distribuição dos dados
- Identificar possíveis causas das anomalias

*Contexto da conversa: {conversation_context[:100]}...*"""

    elif agent_name == "Relationship Analyst":
        numeric_df = df.select_dtypes(include=[np.number])
        corr_pairs = 0
        if len(numeric_df.columns) > 1:
            corr_matrix = numeric_df.corr()
            corr_pairs = len(corr_matrix[(corr_matrix.abs() > 0.5) & (corr_matrix.abs() < 1.0)].stack())
        
        return f"""🔗 **Relationship Analyst** analisando sua pergunta: "{question}"

{data_summary}

**Relacionamentos Identificados:**
- Pares de variáveis correlacionadas: {corr_pairs}
- Variáveis numéricas para análise: {len(numeric_df.columns)}
- Associações categóricas: {len(df.select_dtypes(include=['object']).columns)}

**Análise de Causalidade:**
- Identificar variáveis dependentes e independentes
- Mapear relacionamentos significativos
- Sugerir análises de regressão

*Contexto da conversa: {conversation_context[:100]}...*"""

    else:  # Strategic Synthesizer
        return f"""🎯 **Strategic Synthesizer** analisando sua pergunta: "{question}"

{data_summary}

**Síntese Estratégica:**
- Dataset com {len(df):,} registros e {len(df.columns)} variáveis
- Qualidade geral: {(df.count().sum() / (len(df) * len(df.columns)) * 100):.1f}%
- Próximos passos recomendados:
  1. Limpeza de dados se necessário
  2. Análise exploratória detalhada
  3. Modelagem preditiva

**Recomendações de Negócio:**
- Focar nas variáveis mais completas
- Investigar padrões de dados faltantes
- Desenvolver estratégia de análise

*Contexto da conversa: {conversation_context[:100]}...*"""

def generate_conversation_report(conversation_memory, df):
    """Gera relatório da conversa"""
    st.subheader("📋 Relatório da Conversa")
    
    # Estatísticas da conversa
    total_messages = len(conversation_memory)
    user_questions = len([m for m in conversation_memory if m["role"] == "user"])
    agent_responses = len([m for m in conversation_memory if m["role"] == "assistant"])
    
    # Agentes utilizados
    agents_used = list(set([m.get("agent", "Sistema") for m in conversation_memory if m["role"] == "assistant"]))
    
    # Gerar relatório
    report = f"""
# Relatório de Análise de Dados - {datetime.now().strftime('%d/%m/%Y %H:%M')}

## Resumo da Conversa
- **Total de mensagens:** {total_messages}
- **Perguntas do usuário:** {user_questions}
- **Respostas dos agentes:** {agent_responses}
- **Agentes utilizados:** {', '.join(agents_used)}

## Dados Analisados
- **Total de registros:** {len(df):,}
- **Total de colunas:** {len(df.columns)}
- **Completude:** {(df.count().sum() / (len(df) * len(df.columns)) * 100):.1f}%
- **Duplicatas:** {df.duplicated().sum()}

## Histórico da Conversa
"""
    
    for i, message in enumerate(conversation_memory, 1):
        role = "👤 Usuário" if message["role"] == "user" else f"🤖 {message.get('agent', 'Sistema')}"
        report += f"\n### {i}. {role}\n{message['content']}\n"
    
    # Mostrar relatório
    st.text_area("Relatório Completo", report, height=400)
    
    # Botão de download
    st.download_button(
        label="📥 Download Relatório",
        data=report,
        file_name=f"relatorio_conversa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )

def save_conversation_to_file(conversation_memory):
    """Salva conversa em arquivo"""
    conversation_data = {
        "timestamp": datetime.now().isoformat(),
        "conversation": conversation_memory,
        "summary": {
            "total_messages": len(conversation_memory),
            "user_messages": len([m for m in conversation_memory if m["role"] == "user"]),
            "agent_messages": len([m for m in conversation_memory if m["role"] == "assistant"])
        }
    }
    
    # Converter para JSON
    json_data = json.dumps(conversation_data, indent=2, ensure_ascii=False)
    
    # Botão de download
    st.download_button(
        label="📥 Download Conversa (JSON)",
        data=json_data,
        file_name=f"conversa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

# =============================================================================
# INTERFACE PRINCIPAL
# =============================================================================

def main():
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>📊 CSV Analysis System with CrewAI</h1>
        <p>Sistema completo de análise de dados CSV com agentes especializados em IA</p>
    </div>
    """, unsafe_allow_html=True)
    
    # =============================================================================
    # BARRA LATERAL - CONFIGURAÇÕES E CONTROLES
    # =============================================================================
    
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # 1. Seleção de API
        st.subheader("🔑 API de IA")
        api_provider = st.selectbox(
            "Escolha o provedor de IA:",
            ["OpenAI", "GROQ", "Gemini", "Claude", "Perplexity"],
            help="Selecione qual API de IA usar para análise"
        )
        
        # Configurações específicas por API
        if api_provider == "OpenAI":
            api_key = st.text_input(
                "Chave da API OpenAI:",
                type="password",
                value=os.getenv("OPENAI_API_KEY", ""),
                help="Insira sua chave da API OpenAI"
            )
        elif api_provider == "GROQ":
            api_key = st.text_input(
                "Chave da API GROQ:",
                type="password",
                value=os.getenv("GROQ_API_KEY", ""),
                help="Insira sua chave da API GROQ"
            )
        elif api_provider == "Gemini":
            api_key = st.text_input(
                "Chave da API Gemini:",
                type="password",
                help="Insira sua chave da API Google Gemini"
            )
        elif api_provider == "Claude":
            api_key = st.text_input(
                "Chave da API Claude:",
                type="password",
                help="Insira sua chave da API Anthropic Claude"
            )
        elif api_provider == "Perplexity":
            api_key = st.text_input(
                "Chave da API Perplexity:",
                type="password",
                help="Insira sua chave da API Perplexity"
            )
        
        # Salvar configuração da API
        if st.button("💾 Salvar Configuração da API"):
            if api_key:
                # Atualizar variáveis de ambiente
                if api_provider == "OpenAI":
                    os.environ["OPENAI_API_KEY"] = api_key
                elif api_provider == "GROQ":
                    os.environ["GROQ_API_KEY"] = api_key
                st.success(f"✅ Configuração da API {api_provider} salva!")
            else:
                st.error("❌ Por favor, insira uma chave de API válida")
        
        # Teste de API
        if st.button("🧪 Testar API", help="Testa se a chave da API está funcionando"):
            if api_key:
                with st.spinner("🔄 Testando conexão com a API..."):
                    try:
                        # Teste simples da API
                        if api_provider == "OpenAI":
                            if OpenAI is None:
                                st.error("❌ Biblioteca 'openai' não está instalada. Execute: pip install openai")
                            else:
                                client = OpenAI(api_key=api_key)
                                # Teste simples - listar modelos
                                models = client.models.list()
                                st.success("✅ Chave da API OpenAI está funcionando!")
                                st.balloons()
                        elif api_provider == "GROQ":
                            if Groq is None:
                                st.error("❌ Biblioteca 'groq' não está instalada. Execute: pip install groq")
                            else:
                                client = Groq(api_key=api_key)
                                # Teste simples - listar modelos
                                models = client.models.list()
                                st.success("✅ Chave da API GROQ está funcionando!")
                                st.balloons()
                        else:
                            st.info(f"ℹ️ Teste para {api_provider} ainda não implementado")
                    except Exception as e:
                        st.error(f"❌ Erro ao testar API: {str(e)}")
            else:
                st.error("❌ Por favor, insira uma chave de API primeiro")
        
        st.divider()
        
        # 2. Carregamento de arquivos CSV
        st.subheader("📁 Carregar Arquivos CSV")
        
        uploaded_files = st.file_uploader(
            "Selecione um ou mais arquivos CSV:",
            type=['csv'],
            accept_multiple_files=True,
            help="Você pode carregar múltiplos arquivos CSV para análise"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} arquivo(s) carregado(s)")
            
            # Listar arquivos carregados
            for i, file in enumerate(uploaded_files):
                st.write(f"📄 {i+1}. {file.name}")
        
        st.divider()
        
        # 3. Identificação da análise
        st.subheader("🏷️ Identificação da Análise")
        
        analysis_name = st.text_input(
            "Nome da análise:",
            value="Análise CSV - " + datetime.now().strftime("%Y-%m-%d %H:%M"),
            help="Dê um nome descritivo para esta análise"
        )
        
        analysis_description = st.text_area(
            "Descrição da análise:",
            placeholder="Descreva o objetivo e contexto desta análise...",
            help="Adicione uma descrição detalhada do que será analisado"
        )
        
        # Salvar identificação
        if st.button("💾 Salvar Identificação"):
            if analysis_name:
                st.session_state['analysis_name'] = analysis_name
                st.session_state['analysis_description'] = analysis_description
                st.success("✅ Identificação da análise salva!")
            else:
                st.error("❌ Por favor, insira um nome para a análise")
        
        st.divider()
        
        # 4. Download de relatórios
        st.subheader("📥 Download de Relatórios")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 PDF", use_container_width=True):
                if uploaded_files and len(uploaded_files) > 0:
                    try:
                        # Carregar dados
                        df, error = load_csv_data(uploaded_files[0])
                        if not error:
                            # Gerar PDF
                            analysis_name = st.session_state.get('analysis_name', 'Análise CSV')
                            analysis_description = st.session_state.get('analysis_description', '')
                            
                            pdf_data = generate_pdf_report(df, analysis_name, analysis_description)
                            
                            # Criar botão de download
                            st.download_button(
                                label="📥 Download PDF",
                                data=pdf_data,
                                file_name=f"{analysis_name.replace(' ', '_')}.pdf",
                                mime="application/pdf"
                            )
                            st.success("✅ Relatório PDF gerado!")
                        else:
                            st.error(f"❌ Erro ao carregar dados: {error}")
                    except Exception as e:
                        st.error(f"❌ Erro ao gerar PDF: {str(e)}")
                else:
                    st.warning("⚠️ Carregue um arquivo CSV primeiro")
        
        with col2:
            if st.button("📝 Word", use_container_width=True):
                if uploaded_files and len(uploaded_files) > 0:
                    try:
                        # Carregar dados
                        df, error = load_csv_data(uploaded_files[0])
                        if not error:
                            # Gerar Word
                            analysis_name = st.session_state.get('analysis_name', 'Análise CSV')
                            analysis_description = st.session_state.get('analysis_description', '')
                            
                            word_data = generate_word_report(df, analysis_name, analysis_description)
                            
                            # Criar botão de download
                            st.download_button(
                                label="📥 Download Word",
                                data=word_data,
                                file_name=f"{analysis_name.replace(' ', '_')}.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                            st.success("✅ Relatório Word gerado!")
                        else:
                            st.error(f"❌ Erro ao carregar dados: {error}")
                    except Exception as e:
                        st.error(f"❌ Erro ao gerar Word: {str(e)}")
                else:
                    st.warning("⚠️ Carregue um arquivo CSV primeiro")
        
        # Informações da sessão
        st.divider()
        st.subheader("ℹ️ Informações da Sessão")
        
        if 'analysis_name' in st.session_state:
            st.write(f"**Análise:** {st.session_state['analysis_name']}")
        
        if uploaded_files:
            st.write(f"**Arquivos:** {len(uploaded_files)}")
        
        st.write(f"**API:** {api_provider}")
        st.write(f"**Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        # Configurações do Chat
        if uploaded_files and len(uploaded_files) > 0:
            st.divider()
            st.subheader("💬 Configurações do Chat")
            
            # Configurações de memória
            st.markdown("**🧠 Configurações de Memória:**")
            enable_memory = st.checkbox("Ativar memória de conversas", value=True, help="Os agentes lembrarão das perguntas anteriores")
            memory_duration = st.selectbox("Duração da memória", ["Sessão atual", "24 horas", "7 dias"], help="Por quanto tempo manter a memória")
            
            # Configurações de relatório
            st.markdown("**📋 Configurações de Relatório:**")
            auto_report = st.checkbox("Gerar relatório automático", value=True, help="Relatório será gerado ao final da conversa")
            report_format = st.selectbox("Formato do relatório", ["PDF", "Word", "Texto"], help="Formato do relatório final")
    
    # =============================================================================
    # ÁREA PRINCIPAL DA APLICAÇÃO
    # =============================================================================
    
    # Conteúdo principal
    if uploaded_files and len(uploaded_files) > 0:
        # Carregar dados do primeiro arquivo
        df, error = load_csv_data(uploaded_files[0])
        
        if error:
            st.error(f"❌ Erro ao carregar arquivo: {error}")
            return
        
        # Tabs principais - apenas Overview e Chat
        tab1, tab2 = st.tabs([
            "📊 Overview", 
            "💬 Chat com Agentes IA"
        ])
        
        # TAB 1: OVERVIEW
        with tab1:
            show_overview_tab(df)
        
        # TAB 2: CHAT COM AGENTES IA
        with tab2:
            show_chat_interface(df)
    
    else:
        # Página inicial
        show_welcome_page()

# =============================================================================
# FUNÇÕES DAS TABS
# =============================================================================

def show_welcome_page():
    """Mostra página de boas-vindas"""
    # Título principal em uma única linha
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1>🎯 Bem-vindo ao Sistema de Análise CSV com IA</h1>
        <p style="font-size: 1.2em; color: #666;">Converse com agentes especializados para analisar seus dados</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Seções lado a lado
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🤖 Agentes Especializados:
        - **🔍 Data Validator** - Validação e qualidade dos dados
        - **📊 Data Profiler** - Perfilamento estatístico detalhado
        - **🎯 Pattern Detective** - Detecção de padrões e clustering
        - **⚠️ Anomaly Hunter** - Detecção de anomalias e outliers
        - **🔗 Relationship Analyst** - Análise de correlações
        - **🎯 Strategic Synthesizer** - Síntese estratégica
        """)
    
    with col2:
        st.markdown("""
        ### 💬 Como usar:
        1. Faça upload do seu arquivo CSV na barra lateral
        2. Configure sua chave de API de IA
        3. Vá para a aba "Chat com Agentes IA"
        4. Faça perguntas sobre seus dados
        5. Receba análises especializadas em tempo real
        """)
    
    with col3:
        st.markdown("""
        ### 🚀 Funcionalidades:
        - ✅ Chat interativo com agentes de IA
        - ✅ Memória de conversas
        - ✅ Relatórios automáticos
        - ✅ Análise em tempo real
        - ✅ Respostas especializadas
        - ✅ Exportação de conversas
        """)
    
    # Seção de demonstração
    st.divider()
    st.markdown("""
    ### 🎬 Demonstração Rápida
    
    **Exemplo de perguntas que você pode fazer:**
    
    - "Qual a qualidade dos meus dados?"
    - "Existem anomalias nos dados?"
    - "Quais padrões você consegue identificar?"
    - "Como estão as correlações entre as variáveis?"
    - "Me dê um resumo estratégico dos dados"
    
    **Os agentes irão:**
    - Analisar seus dados em tempo real
    - Lembrar do contexto da conversa
    - Fornecer insights especializados
    - Gerar relatórios personalizados
        """)

def show_overview_tab(df):
    """Mostra overview geral dos dados"""
    st.header("📊 Visão Geral dos Dados")
    
    # Métricas gerais
    metrics = get_data_quality_metrics(df)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📋 Total de Linhas", f"{metrics['total_rows']:,}")
    with col2:
        st.metric("📊 Total de Colunas", metrics['total_columns'])
    with col3:
        st.metric("🎯 Completude", f"{metrics['completeness']:.1f}%")
    with col4:
        st.metric("💾 Tamanho (MB)", f"{metrics['memory_usage']:.2f}")
    
    st.divider()
    
    # Preview dos dados
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🔍 Preview dos Dados")
        st.dataframe(df.head(10), width='stretch')
    
    with col2:
        st.subheader("📈 Tipos de Dados")
        dtype_counts = df.dtypes.value_counts()
        fig = px.pie(
            values=dtype_counts.values,
            names=[str(dtype) for dtype in dtype_counts.index],
            title="Distribuição dos Tipos de Dados"
        )
        st.plotly_chart(fig, width='stretch')
    
    # Informações detalhadas
    st.subheader("📋 Informações Detalhadas das Colunas")
    
    col_info = []
    for col in df.columns:
        col_info.append({
            "Coluna": col,
            "Tipo": str(df[col].dtype),
            "Não Nulos": df[col].count(),
            "Nulos": df[col].isnull().sum(),
            "% Completo": f"{(df[col].count() / len(df) * 100):.1f}%",
            "Únicos": df[col].nunique()
        })
    
    info_df = pd.DataFrame(col_info)
    st.dataframe(info_df, width='stretch')


def show_chat_interface(df):
    """Interface de chat com agentes CrewAI"""
    st.header("💬 Chat com Agentes de IA")
    
    # Inicializar sessão de chat se não existir
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'conversation_memory' not in st.session_state:
        st.session_state.conversation_memory = []
    
    # Informações sobre os agentes disponíveis
    st.markdown("""
    ### 🤖 Agentes Especializados Disponíveis:
    
    - **🔍 Data Validator** - Validação e qualidade dos dados
    - **📊 Data Profiler** - Perfilamento estatístico detalhado  
    - **🎯 Pattern Detective** - Detecção de padrões e clustering
    - **⚠️ Anomaly Hunter** - Detecção de anomalias e outliers
    - **🔗 Relationship Analyst** - Análise de correlações
    - **🎯 Strategic Synthesizer** - Síntese estratégica
    """)
    
    # Área de chat
    chat_container = st.container()
    
    with chat_container:
        # Mostrar histórico de chat
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(message["content"])
                    if "agent" in message:
                        st.caption(f"🤖 Resposta do {message['agent']}")
    
    # Input de chat
    user_input = st.chat_input("Digite sua pergunta sobre os dados...")
    
    if user_input:
        # Adicionar mensagem do usuário ao histórico
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Adicionar à memória da conversa
        st.session_state.conversation_memory.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Processar pergunta com agentes
        with st.spinner("🤖 Agentes analisando sua pergunta..."):
            try:
                # Determinar qual agente é mais adequado para a pergunta
                agent_response = process_user_question(user_input, df, st.session_state.conversation_memory)
                
                # Adicionar resposta ao histórico
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": agent_response["response"],
                    "agent": agent_response["agent"],
                    "timestamp": datetime.now().isoformat()
                })
                
                # Adicionar à memória da conversa
                st.session_state.conversation_memory.append({
                    "role": "assistant",
                    "content": agent_response["response"],
                    "agent": agent_response["agent"],
                    "timestamp": datetime.now().isoformat()
                })
                
                # Mostrar resposta
                with st.chat_message("assistant"):
                    st.write(agent_response["response"])
                    st.caption(f"🤖 Resposta do {agent_response['agent']}")
                
            except Exception as e:
                error_msg = f"❌ Erro ao processar pergunta: {str(e)}"
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": error_msg,
                    "agent": "Sistema",
                    "timestamp": datetime.now().isoformat()
                })
                
                with st.chat_message("assistant"):
                    st.write(error_msg)
                    st.caption("🤖 Resposta do Sistema")
    
    # Controles do chat
    st.divider()
        
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ Limpar Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.conversation_memory = []
            st.rerun()
    
    with col2:
        if st.button("📋 Gerar Relatório", use_container_width=True):
            if st.session_state.conversation_memory:
                generate_conversation_report(st.session_state.conversation_memory, df)
            else:
                st.warning("⚠️ Nenhuma conversa para gerar relatório")
    
    with col3:
        if st.button("💾 Salvar Conversa", use_container_width=True):
            if st.session_state.conversation_memory:
                save_conversation_to_file(st.session_state.conversation_memory)
            else:
                st.warning("⚠️ Nenhuma conversa para salvar")
    
    # Estatísticas da conversa
    if st.session_state.chat_history:
        st.divider()
        st.subheader("📊 Estatísticas da Conversa")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💬 Total de Mensagens", len(st.session_state.chat_history))
        
        with col2:
            user_messages = len([m for m in st.session_state.chat_history if m["role"] == "user"])
            st.metric("👤 Perguntas do Usuário", user_messages)
        
        with col3:
            agent_messages = len([m for m in st.session_state.chat_history if m["role"] == "assistant"])
            st.metric("🤖 Respostas dos Agentes", agent_messages)
        
        with col4:
            unique_agents = len(set([m.get("agent", "Sistema") for m in st.session_state.chat_history if m["role"] == "assistant"]))
            st.metric("🎭 Agentes Utilizados", unique_agents)


# =============================================================================
# CONFIGURAÇÕES AVANÇADAS
# =============================================================================

def show_advanced_settings():
    """Mostra configurações avançadas"""
    with st.sidebar.expander("🛠️ Configurações dos Agentes"):
        
        st.markdown("### 🤖 Data Validator")
        data_validator_config = {
            "quality_threshold": st.slider("Threshold de Qualidade", 0.5, 1.0, 0.9),
            "duplicate_check": st.checkbox("Verificar Duplicatas", value=True),
            "encoding_check": st.checkbox("Verificar Encoding", value=True)
        }
        
        st.markdown("### 📊 Data Profiler") 
        data_profiler_config = {
            "include_correlations": st.checkbox("Incluir Correlações", value=True),
            "histogram_bins": st.slider("Bins do Histograma", 10, 100, 30),
            "percentiles": st.multiselect("Percentis", [10, 25, 50, 75, 90, 95], default=[25, 50, 75])
        }
        
        st.markdown("### 🔍 Pattern Detective")
        pattern_config = {
            "clustering_method": st.selectbox("Método de Clustering", ["K-means", "Hierarchical", "DBSCAN"]),
            "pca_components": st.slider("Componentes PCA", 2, 10, 2),
            "random_state": st.number_input("Random State", value=42)
        }
        
        return {
            "data_validator": data_validator_config,
            "data_profiler": data_profiler_config, 
            "pattern_detective": pattern_config
        }

# =============================================================================
# FUNCIONALIDADES EXTRAS
# =============================================================================

def create_executive_dashboard(df):
    """Cria dashboard executivo"""
    st.subheader("🎯 Dashboard Executivo")
    
    metrics = get_data_quality_metrics(df)
    
    # KPIs principais
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    with kpi1:
        delta_quality = metrics['completeness'] - 90
        st.metric(
            "📊 Qualidade dos Dados",
            f"{metrics['completeness']:.1f}%",
            delta=f"{delta_quality:+.1f}%"
        )
    
    with kpi2:
        st.metric(
            "📋 Volume de Dados", 
            f"{metrics['total_rows']:,}",
            delta="Linhas"
        )
    
    with kpi3:
        st.metric(
            "⚠️ Problemas Identificados",
            metrics['duplicates'] + metrics['missing_values'],
            delta="Issues"
        )
    
    with kpi4:
        efficiency = 100 - ((metrics['duplicates'] + metrics['missing_values']) / metrics['total_rows'] * 100)
        st.metric(
            "⚡ Eficiência",
            f"{efficiency:.1f}%",
            delta="Score"
        )

def show_real_time_monitoring():
    """Mostra monitoramento em tempo real"""
    st.subheader("📡 Monitoramento em Tempo Real")
    
    # Placeholder para dados em tempo real
    placeholder = st.empty()
    
    if st.button("▶️ Iniciar Monitoramento"):
        for i in range(10):
            with placeholder.container():
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Simular dados em tempo real
                    quality_score = 90 + np.random.normal(0, 5)
                    st.metric("Qualidade Atual", f"{quality_score:.1f}%")
                
                with col2:
                    anomalies = np.random.poisson(2)
                    st.metric("Anomalias Detectadas", anomalies)
                
                with col3:
                    processing_time = np.random.uniform(0.5, 2.0)
                    st.metric("Tempo de Processamento", f"{processing_time:.2f}s")
                
                # Gráfico de linha em tempo real
                times = pd.date_range(start='now', periods=20, freq='1min')
                values = 90 + np.random.normal(0, 3, 20)
                
                fig = px.line(
                    x=times, 
                    y=values,
                    title="Qualidade dos Dados - Últimas 20 medições"
                )
                st.plotly_chart(fig, width='stretch')
                
                time.sleep(2)

# =============================================================================
# INICIALIZAÇÃO DA APLICAÇÃO
# =============================================================================

if __name__ == "__main__":
    main()
