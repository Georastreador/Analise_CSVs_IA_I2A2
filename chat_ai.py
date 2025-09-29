# Módulo de Chat com IA - Integração com APIs
# Estilo ChatGPT com análise de dados

import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os
import base64

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
    # Perplexity não tem biblioteca oficial, usaremos requests
    Perplexity = "requests_available"
except ImportError:
    Perplexity = None

class ChatAI:
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
            if self.api_provider == "OpenAI" and OpenAI:
                self.client = OpenAI(api_key=self.api_key)
            elif self.api_provider == "GROQ" and Groq:
                self.client = Groq(api_key=self.api_key)
            elif self.api_provider == "Gemini" and genai:
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel('gemini-2.5-flash-lite-preview-09-2025')
            elif self.api_provider == "Claude" and Anthropic:
                self.client = Anthropic(api_key=self.api_key)
            elif self.api_provider == "Perplexity" and Perplexity:
                self.client = {"api_key": self.api_key}
        except Exception as e:
            st.error(f"Erro ao configurar cliente {self.api_provider}: {str(e)}")
    
    def analyze_data_context(self, df, analysis_name="Análise CSV"):
        """Gera contexto sobre os dados para a IA"""
        if df is None:
            return "Nenhum dado carregado."
        
        # Análise de correlação
        correlation_analysis = self.get_correlation_analysis(df)
        
        context = f"""
        CONTEXTO DA ANÁLISE:
        - Nome da análise: {analysis_name}
        - Data/hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
        
        CONTEXTO DOS DADOS:
        - Total de registros: {len(df):,}
        - Total de colunas: {len(df.columns)}
        - Colunas: {', '.join(df.columns.tolist())}
        - Tipos de dados: {dict(df.dtypes)}
        - Valores faltantes: {df.isnull().sum().sum()}
        - Duplicatas: {df.duplicated().sum()}
        
        ESTATÍSTICAS BÁSICAS:
        {df.describe().to_string()}
        
        ANÁLISE DE CORRELAÇÃO:
        {correlation_analysis}
        
        PRIMEIRAS 5 LINHAS:
        {df.head().to_string()}
        """
        return context
    
    def get_correlation_analysis(self, df):
        """Analisa correlações entre variáveis numéricas"""
        try:
            # Selecionar apenas colunas numéricas
            numeric_cols = df.select_dtypes(include=['number']).columns
            
            if len(numeric_cols) < 2:
                return "Não há variáveis numéricas suficientes para análise de correlação (mínimo 2)."
            
            # Calcular matriz de correlação
            corr_matrix = df[numeric_cols].corr()
            
            # Encontrar correlações significativas (|r| > 0.5)
            significant_correlations = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_value = corr_matrix.iloc[i, j]
                    if abs(corr_value) > 0.5:
                        col1 = corr_matrix.columns[i]
                        col2 = corr_matrix.columns[j]
                        strength = "forte" if abs(corr_value) > 0.7 else "moderada"
                        direction = "positiva" if corr_value > 0 else "negativa"
                        significant_correlations.append(
                            f"- {col1} ↔ {col2}: {corr_value:.3f} (correlação {strength} {direction})"
                        )
            
            # Resumo da análise
            analysis = f"""
        Variáveis numéricas analisadas: {len(numeric_cols)}
        Colunas: {', '.join(numeric_cols.tolist())}
        
        CORRELAÇÕES SIGNIFICATIVAS (|r| > 0.5):
        """
            
            if significant_correlations:
                analysis += "\n".join(significant_correlations)
            else:
                analysis += "Nenhuma correlação significativa encontrada (|r| > 0.5)."
            
            # Adicionar interpretação
            analysis += f"""
        
        INTERPRETAÇÃO:
        - Correlação forte: |r| > 0.7
        - Correlação moderada: 0.5 < |r| ≤ 0.7
        - Correlação fraca: |r| ≤ 0.5
        - Valores próximos de 1 indicam correlação positiva forte
        - Valores próximos de -1 indicam correlação negativa forte
        - Valores próximos de 0 indicam pouca ou nenhuma correlação linear
            """
            
            return analysis
            
        except Exception as e:
            return f"Erro ao calcular correlações: {str(e)}"
    
    def generate_response(self, user_message, df=None, analysis_name="Análise CSV"):
        """Gera resposta da IA baseada na mensagem do usuário"""
        if not self.client:
            return "❌ Cliente de IA não configurado. Verifique sua chave de API."
        
        try:
            # Contexto dos dados
            data_context = self.analyze_data_context(df, analysis_name)
            
            # Prompt do sistema
            system_prompt = f"""
            Você é um assistente especializado em análise de dados. 
            Responda de forma clara, objetiva e útil sobre os dados fornecidos.
            
            {data_context}
            
            Instruções:
            - Seja conciso mas informativo
            - Use emojis quando apropriado
            - Sugira visualizações quando relevante
            - Identifique padrões e insights
            - Responda em português brasileiro
            
            ANÁLISE DE CORRELAÇÃO:
            - Quando perguntado sobre correlações, use os dados de correlação fornecidos no contexto
            - Explique o significado das correlações encontradas
            - Mencione que correlação não implica causalidade
            - Sugira interpretações práticas das correlações
            - Se não houver correlações significativas, explique o que isso significa
            """
            
            # Preparar mensagens
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            # Fazer chamada para a API
            if self.api_provider == "OpenAI":
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7
                )
                return response.choices[0].message.content
            
            elif self.api_provider == "GROQ":
                response = self.client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7
                )
                return response.choices[0].message.content
            
            elif self.api_provider == "Gemini":
                # Converter mensagens para formato Gemini
                prompt = f"{system_prompt}\n\n{user_message}"
                response = self.client.generate_content(prompt)
                return response.text
            
            elif self.api_provider == "Claude":
                response = self.client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=1000,
                    temperature=0.7,
                    messages=[
                        {"role": "user", "content": f"{system_prompt}\n\n{user_message}"}
                    ]
                )
                return response.content[0].text
            
            elif self.api_provider == "Perplexity":
                # Perplexity API via requests
                import requests
                headers = {
                    "Authorization": f"Bearer {self.client['api_key']}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": "llama-3.1-sonar-small-128k-online",
                    "messages": messages,
                    "max_tokens": 1000,
                    "temperature": 0.7
                }
                response = requests.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers=headers,
                    json=data
                )
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]
                else:
                    return f"❌ Erro Perplexity: {response.status_code} - {response.text}"
            
        except Exception as e:
            return f"❌ Erro ao gerar resposta: {str(e)}"
    
    def suggest_questions(self, df):
        """Sugere perguntas baseadas nos dados"""
        if df is None:
            return [
                "Carregue um arquivo CSV para começar a análise",
                "Que tipo de insights você gostaria de obter?",
                "Precisa de ajuda com alguma análise específica?"
            ]
        
        suggestions = [
            "📊 Quais são os principais insights destes dados?",
            "🔍 Existem padrões ou tendências interessantes?",
            "📈 Existe correlação entre as variáveis?",
            "⚠️ Há problemas de qualidade nos dados?",
            "📈 Como posso visualizar melhor estes dados?",
            "🎯 Que recomendações você tem para análise?",
            "📋 Resuma as principais características dos dados"
        ]
        
        # Adicionar sugestões específicas baseadas nos dados
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            suggestions.append(f"📊 Analise a correlação entre {', '.join(numeric_cols[:3])}")
        
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            suggestions.append(f"📋 Quais são as categorias mais comuns em {categorical_cols[0]}?")
        
        return suggestions

def export_conversations_to_json(messages, analysis_name="Análise CSV"):
    """Exporta as conversas para formato JSON"""
    try:
        # Criar estrutura de dados para exportação
        export_data = {
            "metadata": {
                "analysis_name": analysis_name,
                "export_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_messages": len(messages),
                "export_format": "JSON"
            },
            "conversation": []
        }
        
        # Adicionar mensagens à conversa
        for i, message in enumerate(messages):
            export_data["conversation"].append({
                "message_id": i + 1,
                "role": message["role"],
                "content": message["content"],
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        
        # Converter para JSON
        json_data = json.dumps(export_data, ensure_ascii=False, indent=2)
        
        return json_data
        
    except Exception as e:
        return f"Erro ao exportar conversas: {str(e)}"

def show_chat_interface_v2(api_provider, api_key, df, analysis_name="Análise CSV"):
    """Interface de chat melhorada estilo ChatGPT"""
    
    # Inicializar chat AI
    if "chat_ai" not in st.session_state:
        st.session_state.chat_ai = ChatAI(api_provider, api_key)
    
    # Atualizar cliente se necessário
    if st.session_state.chat_ai.api_key != api_key:
        st.session_state.chat_ai = ChatAI(api_provider, api_key)
    
    # Container do chat
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Inicializar histórico
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # ===== CAMPO DE INPUT - SEMPRE NO TOPO =====
    col1, col2 = st.columns([4, 1])
    
    # Inicializar contador de input se não existir
    if "input_counter" not in st.session_state:
        st.session_state.input_counter = 0
    
    with col1:
        user_input = st.text_input(
            "Digite sua pergunta aqui...",
            key=f"user_input_{st.session_state.input_counter}",
            placeholder="Digite sua pergunta aqui...",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("📤 Enviar", use_container_width=True, type="primary")
    
    # Processar envio da mensagem (botão ou Enter)
    if (send_button or user_input.strip()) and user_input.strip():
        # Adicionar mensagem do usuário
        st.session_state.messages.append({"role": "user", "content": user_input.strip()})
        
        # Incrementar contador para limpar o campo
        st.session_state.input_counter += 1
        
        # Gerar resposta automaticamente
        with st.spinner("🤖 Analisando..."):
            response = st.session_state.chat_ai.generate_response(user_message=user_input.strip(), df=df, analysis_name=analysis_name)
            st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Usar st.rerun() para recarregar a página e limpar o campo
        st.rerun()
    
    # ===== SUGESTÕES DE PERGUNTAS - APENAS QUANDO NÃO HÁ HISTÓRICO =====
    if not st.session_state.messages:
        st.markdown("**💡 Sugestões de perguntas:**")
        suggestions = st.session_state.chat_ai.suggest_questions(df)
        
        cols = st.columns(2)
        for i, suggestion in enumerate(suggestions[:6]):
            with cols[i % 2]:
                if st.button(suggestion, key=f"suggestion_{i}", use_container_width=True):
                    # Adicionar sugestão como mensagem do usuário
                    st.session_state.messages.append({"role": "user", "content": suggestion})
                    
                    # Gerar resposta automaticamente
                    with st.spinner("🤖 Analisando..."):
                        response = st.session_state.chat_ai.generate_response(user_message=suggestion, df=df, analysis_name=analysis_name)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    st.rerun()
    
    # ===== LINHA SEPARADORA =====
    st.markdown("---")
    
    # ===== HISTÓRICO DA CONVERSA - EM CASCATA =====
    if st.session_state.messages:
        st.markdown("### 📝 Histórico da Conversa")
        
        # Mostrar histórico de mensagens (mais recentes primeiro)
        for i, message in enumerate(reversed(st.session_state.messages)):
            # Determinar emoji baseado no role
            if message["role"] == "user":
                emoji = "👤"
                role_display = "Usuário"
            else:
                emoji = "🤖"
                role_display = "IA"
            
            # Container para cada mensagem
            with st.container():
                st.markdown(f"**{emoji} {role_display}:**")
                st.markdown(message["content"])
                st.markdown("")  # Espaço entre mensagens
        
        # Botões de ação - no final do histórico
        st.markdown("---")  # Linha separadora
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Limpar Conversa", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        
        with col2:
            if st.button("📄 Exportar JSON", use_container_width=True):
                # Exportar conversas para JSON
                json_data = export_conversations_to_json(st.session_state.messages, analysis_name)
                
                # Criar nome do arquivo
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"conversas_{analysis_name.replace(' ', '_')}_{timestamp}.json"
                
                # Criar botão de download
                st.download_button(
                    label="📥 Download JSON",
                    data=json_data,
                    file_name=filename,
                    mime="application/json",
                    use_container_width=True
                )
    else:
        # Quando não há histórico, mostrar mensagem
        st.info("💬 Faça uma pergunta ou escolha uma sugestão acima para começar a conversa!")
    
    st.markdown('</div>', unsafe_allow_html=True)
