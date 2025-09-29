# Módulo de Chat com IA - Versão Melhorada com Integração CrewAI
# Estilo ChatGPT com análise de dados e acesso às conclusões dos agentes

import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os
import base64
import uuid

# Importar sistema de memória
from analysis_memory import analysis_memory

# Importar sistema CrewAI
from crewai_agents import CSVAnalysisCrew, analyze_csv_with_crewai

# Importar sistema de geração de gráficos
from chart_generator import generate_chart_for_question, create_pygwalker_interface
import plotly.graph_objects as go

# Importar visualizações avançadas
from visualization_enhanced import generate_visualization_insights

# Importações para APIs de IA
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
    Perplexity = "requests_available"
except ImportError:
    Perplexity = None

class EnhancedChatAI:
    def __init__(self, api_provider="OpenAI", api_key=None):
        self.api_provider = api_provider
        self.api_key = api_key
        self.client = None
        self.setup_client()
    
    def setup_client(self):
        """Configura o cliente da API selecionada"""
        if not self.api_key:
            return
        
        try:
            if self.api_provider == "OpenAI":
                self.client = OpenAI(api_key=self.api_key)
            elif self.api_provider == "GROQ":
                self.client = Groq(api_key=self.api_key)
            elif self.api_provider == "Gemini":
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel('gemini-pro')
            elif self.api_provider == "Claude":
                self.client = Anthropic(api_key=self.api_key)
            elif self.api_provider == "Perplexity":
                self.client = {"api_key": self.api_key}
        except Exception as e:
            st.error(f"❌ Erro ao configurar cliente {self.api_provider}: {str(e)}")
    
    def run_crewai_analysis(self, df: pd.DataFrame, analysis_name: str = "Análise CSV") -> str:
        """
        Executa análise completa com agentes CrewAI
        
        Args:
            df: DataFrame com os dados
            analysis_name: Nome da análise
        
        Returns:
            String com ID da análise executada
        """
        try:
            # Gerar ID único para a análise
            analysis_id = str(uuid.uuid4())[:8]
            
            # Executar análise com CrewAI
            st.info("🤖 Executando análise com agentes CrewAI...")
            crew_results = analyze_csv_with_crewai(df, analysis_name)
            
            # Salvar resultados na memória
            success = analysis_memory.save_analysis_results(
                analysis_id=analysis_id,
                csv_data=df,
                crew_results=crew_results,
                analysis_name=analysis_name
            )
            
            if success:
                st.success(f"✅ Análise concluída! ID: {analysis_id}")
                return analysis_id
            else:
                st.error("❌ Erro ao salvar resultados da análise")
                return None
                
        except Exception as e:
            st.error(f"❌ Erro na análise CrewAI: {str(e)}")
            return None
    
    def get_analysis_context(self, analysis_id: str = None) -> str:
        """
        Gera contexto sobre as análises disponíveis
        
        Args:
            analysis_id: ID da análise específica (None para análise atual)
        
        Returns:
            String com contexto das análises
        """
        if analysis_id is None:
            analysis_id = analysis_memory.current_analysis
        
        if not analysis_id:
            return "Nenhuma análise CrewAI disponível. Execute uma análise primeiro."
        
        # Obter dados da análise
        analysis_data = analysis_memory.get_analysis_results(analysis_id)
        if not analysis_data:
            return "Análise não encontrada."
        
        # Obter conclusões dos agentes
        conclusions = analysis_memory.get_agent_conclusions(analysis_id)
        
        context = f"""
ANÁLISE CREWAI DISPONÍVEL:
- ID: {analysis_id}
- Nome: {analysis_data.get('analysis_name', 'N/A')}
- Data: {analysis_data.get('timestamp', 'N/A')}
- Registros: {analysis_data.get('data_summary', {}).get('rows', 0):,}
- Colunas: {analysis_data.get('data_summary', {}).get('columns', 0)}

CONCLUSÕES DOS AGENTES:
"""
        
        # Adicionar conclusões de cada agente
        for agent_name, agent_data in conclusions.items():
            status = agent_data.get('status', 'unknown')
            result = agent_data.get('result', 'Nenhum resultado')
            
            # Incluir resultado completo para insights estratégicos
            if isinstance(result, str):
                # Para insights estratégicos, incluir resultado completo
                context += f"{agent_name}: {status}\n{result}\n\n"
            elif isinstance(result, dict):
                # Se for dict, converter para string formatada
                context += f"{agent_name}: {status}\n{json.dumps(result, indent=2, ensure_ascii=False)}\n\n"
            else:
                context += f"{agent_name}: {status} - {str(result)}\n\n"
        
        return context
    
    def generate_enhanced_response(self, user_message: str, df: pd.DataFrame = None, 
                                 analysis_name: str = "Análise CSV") -> tuple:
        """
        Gera resposta da IA com acesso às conclusões dos agentes CrewAI e gráficos
        
        Args:
            user_message: Mensagem do usuário
            df: DataFrame com os dados
            analysis_name: Nome da análise
        
        Returns:
            Tuple[str, Optional[go.Figure]]: (resposta_texto, grafico)
        """
        if not self.client:
            return ("❌ Cliente de IA não configurado. Verifique sua chave de API.", None)
        
        try:
            # Verificar se é uma solicitação para executar análise CrewAI
            execute_analysis_keywords = [
                "execute", "executar", "análise completa", "análise com agentes", "crewai",
                "agentes", "análise crewai", "execute análise", "executar análise"
            ]
            
            is_execute_request = any(keyword in user_message.lower() for keyword in execute_analysis_keywords)
            
            # Verificar se é uma pergunta sobre análises CrewAI
            crewai_keywords = [
                "conclusão", "conclusões", "resultado", "resultados", "insight", "insights",
                "análise", "agente", "agentes", "crewai", "crew", "descoberta", "descobertas",
                "padrão", "padrões", "anomalia", "anomalias", "correlação", "correlações",
                "recomendação", "recomendações", "estratégia", "estratégico"
            ]
            
            is_crewai_question = any(keyword in user_message.lower() for keyword in crewai_keywords)
            
            # Se for uma solicitação para executar análise, executar primeiro
            if is_execute_request and df is not None:
                return self._handle_execute_analysis_request(df, analysis_name)
            
            # Obter contexto das análises se disponível
            analysis_context = ""
            if analysis_memory.current_analysis or is_crewai_question:
                analysis_context = self.get_analysis_context()
            
            # Obter contexto dos dados se disponível
            data_context = ""
            if df is not None:
                data_context = self.analyze_data_context(df, analysis_name)
                
                # Adicionar estatísticas básicas dos dados
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    data_context += f"\n\nESTATÍSTICAS BÁSICAS DOS DADOS:\n"
                    for col in numeric_cols[:10]:  # Limitar a 10 colunas
                        min_val = df[col].min()
                        max_val = df[col].max()
                        mean_val = df[col].mean()
                        data_context += f"- {col}: Min={min_val:.2f}, Max={max_val:.2f}, Média={mean_val:.2f}\n"
            
            # Construir prompt do sistema
            system_prompt = f"""
Você é um assistente especializado em análise de dados com acesso aos resultados de agentes CrewAI.

{analysis_context}

{data_context}

INSTRUÇÕES CRÍTICAS:
- Você TEM ACESSO COMPLETO aos dados CSV carregados e aos resultados de 6 agentes CrewAI especializados
- Use SEMPRE os dados CSV quando disponíveis - NÃO diga que não tem acesso aos dados
- Para perguntas sobre estatísticas, intervalos, valores min/max, use os dados CSV fornecidos acima
- Use SEMPRE as conclusões dos agentes quando disponíveis - NÃO invente informações
- Se perguntado sobre conclusões, insights ou recomendações, consulte EXATAMENTE os resultados dos agentes
- Responda em português brasileiro
- Seja específico e detalhado sobre as descobertas dos agentes e dados
- NUNCA diga que não tem acesso às conclusões ou dados se eles estão disponíveis acima

FUNCIONALIDADES DISPONÍVEIS:
- ✅ 6 Agentes CrewAI: Data Validator, Data Profiler, Pattern Detective, Anomaly Hunter, Relationship Analyst, Strategic Synthesizer
- ✅ Acesso COMPLETO às conclusões específicas de cada agente
- ✅ Análise de correlações e padrões
- ✅ Detecção de anomalias
- ✅ Recomendações estratégicas
- ✅ Histórico de análises

QUANDO USUÁRIO PERGUNTAR SOBRE DADOS (estatísticas, intervalos, min/max, etc.):
- Use SEMPRE os dados CSV fornecidos acima
- Para perguntas sobre intervalos (min/max), use as estatísticas básicas dos dados
- Para perguntas sobre distribuições, use os insights das visualizações
- NUNCA diga que não tem acesso aos dados - eles estão disponíveis acima

QUANDO USUÁRIO PERGUNTAR SOBRE CONCLUSÕES/INSIGHTS/RECOMENDAÇÕES:
- Consulte EXATAMENTE as conclusões dos agentes fornecidas acima
- Para perguntas sobre "resumo executivo", use EXATAMENTE o texto do **Resumo Executivo** do Data Validator
- Para perguntas sobre "insights principais" ou "principais insights", use EXATAMENTE o texto da seção **Insights Principais** do Data Validator
- NÃO interprete, resuma ou modifique o texto do agente - use o texto EXATO
- Cite especificamente o que cada agente descobriu
- Mencione insights, padrões, anomalias e recomendações encontradas
- Use as informações EXATAS dos agentes, não generalize

IMPORTANTE: 
- Os dados CSV estão disponíveis acima com estatísticas básicas
- As conclusões dos agentes estão disponíveis acima
- Use SEMPRE essas informações para responder, não invente ou diga que não tem acesso
"""
            
            # Preparar mensagens
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            # Gerar resposta baseada no provedor
            text_response = ""
            try:
                if self.api_provider == "OpenAI":
                    response = self.client.chat.completions.create(
                        model="gpt-4",
                        messages=messages,
                        max_tokens=1500,
                        temperature=0.7,
                        timeout=30  # Timeout de 30 segundos
                    )
                    text_response = response.choices[0].message.content
            
                elif self.api_provider == "GROQ":
                    response = self.client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=messages,
                        max_tokens=1500,
                        temperature=0.7,
                        timeout=30
                    )
                    text_response = response.choices[0].message.content
                
                elif self.api_provider == "Gemini":
                    prompt = f"{system_prompt}\n\n{user_message}"
                    response = self.client.generate_content(prompt)
                    text_response = response.text
                
                elif self.api_provider == "Claude":
                    response = self.client.messages.create(
                        model="claude-3-sonnet-20240229",
                        max_tokens=1500,
                        temperature=0.7,
                        messages=[
                            {"role": "user", "content": f"{system_prompt}\n\n{user_message}"}
                        ],
                        timeout=30
                    )
                    text_response = response.content[0].text
                
                elif self.api_provider == "Perplexity":
                    headers = {
                        "Authorization": f"Bearer {self.client['api_key']}",
                        "Content-Type": "application/json"
                    }
                    data = {
                        "model": "llama-3.1-sonar-small-128k-online",
                        "messages": messages,
                        "max_tokens": 1500,
                        "temperature": 0.7
                    }
                    response = requests.post(
                        "https://api.perplexity.ai/chat/completions",
                        headers=headers,
                        json=data,
                        timeout=30
                    )
                    if response.status_code == 200:
                        text_response = response.json()["choices"][0]["message"]["content"]
                    else:
                        text_response = f"❌ Erro Perplexity: {response.status_code} - {response.text}"
                
            except Exception as api_error:
                # Se houver erro na API, usar fallback
                raise Exception(f"Erro na API {self.api_provider}: {str(api_error)}")
            
            # Gerar gráfico se necessário
            chart = None
            if df is not None and text_response:
                try:
                    chart = generate_chart_for_question(user_message, df)
                except Exception as e:
                    st.warning(f"⚠️ Não foi possível gerar gráfico: {str(e)}")
            
            return (text_response, chart)
            
        except Exception as e:
            # Fallback: resposta básica com dados disponíveis
            fallback_response = self._generate_fallback_response(user_message, df, analysis_context)
            return (fallback_response, None)
    
    def _generate_fallback_response(self, user_message: str, df: pd.DataFrame = None, analysis_context: str = "") -> str:
        """Gera resposta de fallback quando há erro na API"""
        try:
            # Resposta básica baseada nos dados disponíveis
            if df is not None:
                numeric_cols = df.select_dtypes(include=['number']).columns
                categorical_cols = df.select_dtypes(include=['object']).columns
                
                if "tipos de dados" in user_message.lower():
                    return f"""**Tipos de Dados no Dataset:**
- **Total de colunas:** {len(df.columns)}
- **Colunas numéricas:** {len(numeric_cols)} ({', '.join(numeric_cols[:5])}{'...' if len(numeric_cols) > 5 else ''})
- **Colunas categóricas:** {len(categorical_cols)} ({', '.join(categorical_cols[:5])}{'...' if len(categorical_cols) > 5 else ''})
- **Total de registros:** {len(df):,}"""
                
                elif "intervalo" in user_message.lower() or "mínimo" in user_message.lower() or "máximo" in user_message.lower():
                    response = "**Intervalos das Variáveis Numéricas:**\n"
                    for col in numeric_cols[:10]:
                        min_val = df[col].min()
                        max_val = df[col].max()
                        response += f"- **{col}:** Min = {min_val:.2f}, Max = {max_val:.2f}\n"
                    return response
                
                elif "padrões" in user_message.lower() or "tendências" in user_message.lower():
                    if analysis_context:
                        return f"**Análise de Padrões e Tendências:**\n{analysis_context[:500]}..."
                    else:
                        return "**Análise de Padrões:** Execute uma análise CrewAI primeiro para obter insights sobre padrões e tendências nos dados."
            
            return "Desculpe, houve um problema técnico. Tente novamente ou execute uma análise CrewAI primeiro."
            
        except Exception as e:
            return f"Erro no sistema: {str(e)}"
    
    def analyze_data_context(self, df: pd.DataFrame, analysis_name: str = "Análise CSV") -> str:
        """Gera contexto sobre os dados para a IA"""
        if df is None:
            return "Nenhum dado carregado."
        
        # Análise básica dos dados
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        # Gerar insights das visualizações
        visualization_insights = ""
        try:
            visualization_insights = generate_visualization_insights(df)
        except Exception as e:
            visualization_insights = f"Erro ao gerar insights de visualização: {str(e)}"
        
        context = f"""
CONTEXTO DOS DADOS:
- Nome: {analysis_name}
- Registros: {len(df):,}
- Colunas: {len(df.columns)}
- Numéricas: {len(numeric_cols)} ({', '.join(numeric_cols[:3])}{'...' if len(numeric_cols) > 3 else ''})
- Categóricas: {len(categorical_cols)} ({', '.join(categorical_cols[:3])}{'...' if len(categorical_cols) > 3 else ''})

INSIGHTS DAS VISUALIZAÇÕES (Matplotlib/Seaborn):
{visualization_insights}

BIBLIOTECAS DE VISUALIZAÇÃO DISPONÍVEIS:
- Matplotlib: Para gráficos básicos e personalizados
- Seaborn: Para visualizações estatísticas avançadas
- Plotly: Para gráficos interativos
- Pandas: Para visualizações integradas
"""
        
        return context
    
    def suggest_enhanced_questions(self, df: pd.DataFrame = None) -> list:
        """Sugere perguntas baseadas nos dados e análises disponíveis"""
        suggestions = []
        
        # Sugestões gerais
        suggestions.extend([
            "🤖 Execute uma análise completa com os agentes CrewAI",
            "📊 Quais são as principais conclusões da análise?",
            "🔍 O que os agentes descobriram sobre os dados?",
            "📈 Existem padrões ou tendências interessantes?",
            "⚠️ Há anomalias ou outliers nos dados?",
            "🔗 Quais são as correlações entre as variáveis?",
            "🎯 Que recomendações estratégicas os agentes fizeram?",
            "📋 Resuma os insights mais importantes"
        ])
        
        # Sugestões que GERAM GRÁFICOS
        suggestions.extend([
            "📊 Mostre a distribuição dos dados em um histograma",
            "📈 Visualize as correlações entre as variáveis",
            "📉 Crie um gráfico de box plot para detectar outliers",
            "📊 Mostre os valores mais altos e mais baixos",
            "📈 Como estão distribuídos os dados ao longo do tempo?",
            "📊 Crie um gráfico de barras das categorias mais comuns",
            "📈 Mostre a evolução dos dados em um gráfico de linha",
            "📊 Visualize a matriz de correlação em um heatmap"
        ])
        
        # Sugestões específicas se há análise CrewAI
        if analysis_memory.current_analysis:
            suggestions.extend([
                "🔍 Quais foram as conclusões do Data Validator?",
                "📊 O que o Data Profiler descobriu?",
                "🎯 Que padrões o Pattern Detective identificou?",
                "⚠️ Quais anomalias o Anomaly Hunter encontrou?",
                "🔗 O que o Relationship Analyst descobriu?",
                "🎯 Quais são as recomendações do Strategic Synthesizer?",
                "📈 Mostre um resumo executivo da análise"
            ])
        
        # Sugestões baseadas nos dados
        if df is not None:
            numeric_cols = df.select_dtypes(include=['number']).columns
            categorical_cols = df.select_dtypes(include=['object']).columns
            
            if len(numeric_cols) > 0:
                suggestions.append(f"📊 Analise a correlação entre {', '.join(numeric_cols[:3])}")
                suggestions.append(f"📈 Mostre a distribuição de {numeric_cols[0]} em um histograma")
                suggestions.append(f"📉 Crie um box plot para {numeric_cols[0]}")
            
            if len(categorical_cols) > 0:
                suggestions.append(f"📋 Quais são as categorias mais comuns em {categorical_cols[0]}?")
                suggestions.append(f"📊 Mostre um gráfico de barras de {categorical_cols[0]}")
            
            # Verificar se há coluna de tempo
            time_cols = [col for col in df.columns if 'time' in col.lower() or 'date' in col.lower()]
            if time_cols:
                suggestions.append(f"📅 Mostre a evolução dos dados ao longo do tempo ({time_cols[0]})")
        
        return suggestions[:16]  # Aumentar para 16 sugestões (8 gerais + 8 com gráficos)
    
    def _handle_execute_analysis_request(self, df: pd.DataFrame, analysis_name: str) -> tuple:
        """
        Lida com solicitações para executar análise CrewAI
        
        Args:
            df: DataFrame com os dados
            analysis_name: Nome da análise
        
        Returns:
            Tuple[str, Optional[go.Figure]]: (resposta_texto, grafico)
        """
        try:
            # Executar análise CrewAI
            analysis_id = self.run_crewai_analysis(df, analysis_name)
            
            if analysis_id:
                # Obter contexto da análise executada
                analysis_context = self.get_analysis_context(analysis_id)
                
                return (f"""
🤖 **Análise CrewAI Executada com Sucesso!**

✅ **ID da Análise:** {analysis_id}
📊 **Dados Analisados:** {len(df):,} registros, {len(df.columns)} colunas
📅 **Data/Hora:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

**📋 Resumo da Análise:**
{analysis_memory.get_analysis_summary(analysis_id)}

**🎯 Próximos Passos:**
- Use a aba "🎯 Conclusões" para ver insights detalhados
- Faça perguntas específicas sobre as descobertas
- Explore os resultados de cada agente individualmente

**💡 Sugestões de Perguntas:**
- "Quais foram as principais conclusões da análise?"
- "O que o Data Validator descobriu sobre a qualidade dos dados?"
- "Que padrões o Pattern Detective identificou?"
- "Há anomalias nos dados? O que o Anomaly Hunter encontrou?"
- "Quais são as recomendações estratégicas?"

A análise está completa e pronta para exploração! 🚀
""", None)
            else:
                return ("""
❌ **Erro ao Executar Análise CrewAI**

Não foi possível executar a análise com os agentes CrewAI. Possíveis causas:

1. **Chave de API não configurada:** Verifique se a OPENAI_API_KEY está definida no arquivo .env
2. **Erro na conexão:** Verifique sua conexão com a internet
3. **Dados inválidos:** Verifique se o arquivo CSV está carregado corretamente

**💡 Soluções:**
- Configure sua chave de API OpenAI na barra lateral
- Verifique se o arquivo .env existe e contém a chave correta
- Tente carregar o arquivo CSV novamente

Para mais ajuda, consulte a documentação ou entre em contato com o suporte.
""", None)
                
        except Exception as e:
            return (f"""
❌ **Erro ao Executar Análise CrewAI**

**Erro:** {str(e)}

**💡 Soluções:**
1. Verifique se a chave de API OpenAI está configurada
2. Confirme se o arquivo .env existe e contém OPENAI_API_KEY
3. Verifique sua conexão com a internet
4. Tente novamente em alguns minutos

Se o problema persistir, consulte a documentação ou entre em contato com o suporte.
""", None)

def show_enhanced_chat_interface(api_provider: str, api_key: str, df: pd.DataFrame = None, 
                                analysis_name: str = "Análise CSV"):
    """Interface de chat melhorada com integração CrewAI"""
    
    # Inicializar chat AI
    chat_ai = EnhancedChatAI(api_provider, api_key)
    
    # Inicializar sessão
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "analysis_id" not in st.session_state:
        st.session_state.analysis_id = None
    
    # Sidebar com controles
    with st.sidebar:
        st.markdown("### 🤖 Controles de Análise")
        
        # Botão para executar análise CrewAI
        if st.button("🚀 Executar Análise CrewAI", type="primary"):
            if df is not None:
                with st.spinner("Executando análise com agentes CrewAI..."):
                    analysis_id = chat_ai.run_crewai_analysis(df, analysis_name)
                    if analysis_id:
                        st.session_state.analysis_id = analysis_id
                        st.success(f"✅ Análise concluída! ID: {analysis_id}")
            else:
                st.warning("⚠️ Carregue um arquivo CSV primeiro")
        
        # Mostrar análise atual
        if analysis_memory.current_analysis:
            st.markdown("### 📊 Análise Atual")
            st.info(f"ID: {analysis_memory.current_analysis}")
            
            # Botão para ver resumo
            if st.button("📋 Ver Resumo da Análise"):
                summary = analysis_memory.get_analysis_summary()
                st.markdown(summary)
        
        # Histórico de análises
        history = analysis_memory.get_analysis_history()
        if history:
            st.markdown("### 📚 Histórico de Análises")
            for analysis_id, info in list(history.items())[-5:]:  # Últimas 5
                if st.button(f"📄 {info['analysis_name']} ({analysis_id})"):
                    st.session_state.analysis_id = analysis_id
                    analysis_memory.current_analysis = analysis_id
                    st.rerun()
    
    # Área principal do chat
    st.markdown("### 💬 Chat com Agentes de IA")
    
    # Mostrar mensagens
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Sugestões de perguntas
    suggestions = chat_ai.suggest_enhanced_questions(df)
    if suggestions:
        st.markdown("#### 💡 Sugestões de Perguntas:")
        
        # Dividir sugestões em 2 colunas
        col1, col2 = st.columns(2)
        
        # Dividir a lista de sugestões ao meio
        mid_point = len(suggestions) // 2
        suggestions_col1 = suggestions[:mid_point]
        suggestions_col2 = suggestions[mid_point:]
        
        # Coluna 1
        with col1:
            for suggestion in suggestions_col1:
                st.markdown(f"• {suggestion}")
        
        # Coluna 2
        with col2:
            for suggestion in suggestions_col2:
                st.markdown(f"• {suggestion}")
    
    # Input do usuário
    if prompt := st.chat_input("Faça uma pergunta sobre os dados ou análises..."):
        # Adicionar mensagem do usuário
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Mostrar mensagem do usuário
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Gerar resposta
        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                response, chart = chat_ai.generate_enhanced_response(prompt, df, analysis_name)
                st.markdown(response)
                
                # Mostrar gráfico se disponível
                if chart:
                    st.plotly_chart(chart, use_container_width=True)
        
        # Adicionar resposta às mensagens
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Botões de ação
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗑️ Limpar Chat"):
            st.session_state.messages = []
            st.rerun()
    
    with col2:
        if st.button("📥 Exportar Conversa"):
            if st.session_state.messages:
                export_data = {
                    "conversation": st.session_state.messages,
                    "analysis_id": st.session_state.analysis_id,
                    "timestamp": datetime.now().isoformat()
                }
                json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
                st.download_button(
                    label="📄 Download JSON",
                    data=json_str,
                    file_name=f"chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
    
    with col3:
        if st.button("🧠 Limpar Memória"):
            if analysis_memory.clear_analysis_memory():
                st.success("✅ Memória de análises limpa!")
                st.session_state.analysis_id = None
                st.rerun()
            else:
                st.error("❌ Erro ao limpar memória")
