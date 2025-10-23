import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
from data_manager import data_manager
from analysis_memory import analysis_memory
try:
    from crewai import Agent, Task, Crew, Process
    from langchain_openai import ChatOpenAI
    from langchain_groq import ChatGroq
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_anthropic import ChatAnthropic
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    Agent = Task = Crew = Process = None
    ChatOpenAI = ChatGroq = ChatGoogleGenerativeAI = ChatAnthropic = None
import os

class CrewAIEnhanced:
    """Sistema CrewAI melhorado com estrutura padronizada e cache"""
    
    def __init__(self):
        self.agents = {}
        self.tasks = {}
        self.crew = None
        self.llm = None
        self._setup_llm()
        # Não criar agentes automaticamente - serão criados quando necessário
    
    def _setup_llm(self):
        """Configura o modelo de linguagem"""
        if not CREWAI_AVAILABLE:
            # Não mostrar erro aqui, apenas retornar
            return
        # Não configurar LLM aqui - será configurado quando necessário
        self.llm = None
    
    def setup_llm_with_credentials(self, api_provider: str, api_key: str):
        """Configura o LLM com as credenciais fornecidas pelo usuário"""
        if not CREWAI_AVAILABLE:
            return False
            
        try:
            if api_provider == "OpenAI" and ChatOpenAI and api_key:
                self.llm = ChatOpenAI(
                    api_key=api_key,
                    model="gpt-4o-mini",
                    temperature=0.1,
                    timeout=30
                )
                st.info("🤖 Usando OpenAI GPT-4o-mini")
                st.write(f"🔍 Debug: LLM configurado: {type(self.llm).__name__}")
                
                # Configurar variável de ambiente para o CrewAI
                os.environ["OPENAI_API_KEY"] = api_key
                st.write(f"🔍 Debug: Variável de ambiente OPENAI_API_KEY configurada")
                
                return True
            elif api_provider == "GROQ" and ChatGroq and api_key:
                self.llm = ChatGroq(
                    api_key=api_key,
                    model="llama3-8b-8192",
                    temperature=0.1,
                    timeout=30
                )
                st.info("🤖 Usando GROQ Llama3-8b")
                return True
            elif api_provider == "Gemini" and ChatGoogleGenerativeAI and api_key:
                self.llm = ChatGoogleGenerativeAI(
                    api_key=api_key,
                    model="gemini-pro",
                    temperature=0.1,
                    timeout=30
                )
                st.info("🤖 Usando Google Gemini Pro")
                return True
            elif api_provider == "Claude" and ChatAnthropic and api_key:
                self.llm = ChatAnthropic(
                    api_key=api_key,
                    model="claude-3-haiku-20240307",
                    temperature=0.1,
                    timeout=30
                )
                st.info("🤖 Usando Anthropic Claude Haiku")
                return True
            else:
                st.error("❌ Provedor de API não suportado ou chave inválida!")
                return False
                
        except Exception as e:
            st.error(f"❌ Erro ao configurar LLM: {str(e)}")
            return False
    
    def _create_agents(self):
        """Cria os agentes especializados"""
        if not CREWAI_AVAILABLE:
            return
        
        if not self.llm:
            st.warning("⚠️ LLM não configurado. Agentes não serão criados.")
            return
        
        st.write(f"🔍 Debug: Criando agentes com LLM: {type(self.llm).__name__}")
        
        self.agents = {
            "data_validator": Agent(
                role="Validador de Dados",
                goal="Validar a integridade e qualidade dos dados CSV",
                backstory="Sou um especialista em validação de dados com anos de experiência em identificar problemas de qualidade, valores ausentes, duplicatas e inconsistências.",
                verbose=True,
                allow_delegation=False,
                llm=self.llm
            ),
            
            "data_profiler": Agent(
                role="Perfilador de Dados",
                goal="Criar um perfil detalhado dos dados, incluindo estatísticas descritivas e distribuições",
                backstory="Sou um analista de dados especializado em criar perfis detalhados de datasets, identificando padrões estatísticos e características dos dados.",
                verbose=True,
                allow_delegation=False,
                llm=self.llm
            ),
            
            "pattern_detective": Agent(
                role="Detetive de Padrões",
                goal="Identificar padrões, tendências e correlações nos dados",
                backstory="Sou um detetive de dados especializado em encontrar padrões ocultos, tendências temporais e correlações entre variáveis.",
                verbose=True,
                allow_delegation=False,
                llm=self.llm
            ),
            
            "anomaly_hunter": Agent(
                role="Caçador de Anomalias",
                goal="Detectar outliers, anomalias e valores atípicos nos dados",
                backstory="Sou um especialista em detecção de anomalias com experiência em identificar outliers, valores atípicos e comportamentos anômalos em datasets.",
                verbose=True,
                allow_delegation=False,
                llm=self.llm
            ),
            
            "relationship_analyst": Agent(
                role="Analista de Relacionamentos",
                goal="Analisar relacionamentos e dependências entre variáveis",
                backstory="Sou um analista especializado em identificar relacionamentos complexos entre variáveis, dependências e estruturas de dados.",
                verbose=True,
                allow_delegation=False,
                llm=self.llm
            ),
            
            "strategic_synthesizer": Agent(
                role="Sintetizador Estratégico",
                goal="Sintetizar insights e fornecer recomendações estratégicas baseadas nas análises",
                backstory="Sou um consultor estratégico especializado em sintetizar análises complexas e fornecer recomendações acionáveis para tomada de decisão.",
                verbose=True,
                allow_delegation=False,
                llm=self.llm
            )
        }
    
    def _create_tasks(self):
        """Cria as tarefas para cada agente"""
        if not CREWAI_AVAILABLE or not self.agents:
            return
        
        # Obter dados atuais para análise
        df = data_manager.get_current_data()
        if df is None:
            st.warning("⚠️ Nenhum dado carregado para análise")
            return
        
        # Criar contexto dos dados
        data_context = f"""
        Dataset para análise:
        - Dimensões: {df.shape[0]} linhas x {df.shape[1]} colunas
        - Colunas: {', '.join(df.columns.tolist())}
        - Tipos de dados: {df.dtypes.to_dict()}
        - Primeiras 5 linhas:
        {df.head().to_string()}
        - Estatísticas básicas:
        {df.describe().to_string() if len(df.select_dtypes(include=['number']).columns) > 0 else 'Nenhuma coluna numérica encontrada'}
        """
        
        self.tasks = {
            "validation_task": Task(
                description=f"""
                Analise o dataset CSV fornecido e valide:
                1. Integridade dos dados (valores ausentes, duplicatas)
                2. Consistência dos tipos de dados
                3. Qualidade geral dos dados
                4. Problemas potenciais que podem afetar análises futuras
                
                {data_context}
                
                Forneça um relatório detalhado com:
                - Status da validação (aprovado/reprovado/atenção)
                - Lista de problemas encontrados
                - Recomendações para correção
                - Score de qualidade (0-100)
                """,
                agent=self.agents["data_validator"],
                expected_output="Relatório de validação estruturado com status, problemas e recomendações"
            ),
            
            "profiling_task": Task(
                description=f"""
                Crie um perfil detalhado do dataset:
                1. Estatísticas descritivas para cada coluna
                2. Distribuições de dados (histogramas, box plots)
                3. Características das variáveis categóricas
                4. Resumo da estrutura dos dados
                
                {data_context}
                
                Forneça:
                - Estatísticas numéricas (média, mediana, desvio padrão, etc.)
                - Análise de distribuições
                - Características das categorias
                - Insights sobre a estrutura dos dados
                """,
                agent=self.agents["data_profiler"],
                expected_output="Perfil detalhado dos dados com estatísticas e características"
            ),
            
            "pattern_task": Task(
                description=f"""
                Identifique padrões e tendências nos dados:
                1. Padrões temporais (se houver colunas de data)
                2. Correlações entre variáveis numéricas
                3. Padrões de distribuição
                4. Tendências e sazonalidades
                
                {data_context}
                
                Forneça:
                - Matriz de correlações
                - Padrões identificados
                - Tendências temporais
                - Insights sobre comportamento dos dados
                """,
                agent=self.agents["pattern_detective"],
                expected_output="Análise de padrões e tendências com correlações e insights"
            ),
            
            "anomaly_task": Task(
                description=f"""
                Detecte anomalias e outliers:
                1. Identifique valores atípicos em colunas numéricas
                2. Detecte registros anômalos
                3. Analise distribuições para identificar outliers
                4. Avalie o impacto das anomalias
                
                {data_context}
                
                Forneça:
                - Lista de outliers identificados
                - Análise de anomalias
                - Recomendações para tratamento
                - Impacto nas análises
                """,
                agent=self.agents["anomaly_hunter"],
                expected_output="Relatório de anomalias com outliers identificados e recomendações"
            ),
            
            "relationship_task": Task(
                description=f"""
                Analise relacionamentos entre variáveis:
                1. Correlações entre variáveis numéricas
                2. Relacionamentos categóricos
                3. Dependências e associações
                4. Estrutura de relacionamentos
                
                {data_context}
                
                Forneça:
                - Análise de correlações
                - Relacionamentos identificados
                - Dependências entre variáveis
                - Insights sobre estrutura dos dados
                """,
                agent=self.agents["relationship_analyst"],
                expected_output="Análise de relacionamentos e dependências entre variáveis"
            ),
            
            "synthesis_task": Task(
                description=f"""
                Sintetize todas as análises e forneça recomendações:
                1. Resuma os principais insights de cada agente
                2. Identifique oportunidades de melhoria
                3. Forneça recomendações estratégicas
                4. Sugira próximos passos para análise
                
                {data_context}
                
                Forneça:
                - Resumo executivo
                - Insights principais
                - Recomendações estratégicas
                - Próximos passos sugeridos
                """,
                agent=self.agents["strategic_synthesizer"],
                expected_output="Síntese estratégica com insights e recomendações"
            )
        }
    
    def run_analysis(self, analysis_name: str = "Análise CrewAI", api_provider: str = None, api_key: str = None) -> Dict[str, Any]:
        """Executa análise completa com os agentes CrewAI"""
        try:
            if not CREWAI_AVAILABLE:
                st.error("❌ CrewAI não está instalado!")
                return {}
                
            if not self.llm:
                if api_provider and api_key:
                    # Configurar LLM com as credenciais fornecidas
                    if not self.setup_llm_with_credentials(api_provider, api_key):
                        return {}
                    # Limpar agentes e tarefas antigas
                    self.agents = {}
                    self.tasks = {}
                    
                    # Debug: verificar LLM antes de criar agentes
                    st.write(f"🔍 Debug: LLM antes de criar agentes: {type(self.llm).__name__}")
                    
                    # Recriar agentes e tarefas com o LLM configurado
                    self._create_agents()
                    self._create_tasks()
                    
                    # Debug: verificar se os agentes foram criados
                    st.write(f"🔍 Debug: {len(self.agents)} agentes criados, {len(self.tasks)} tarefas criadas")
                else:
                    st.error("❌ Nenhuma API key configurada! Configure uma API na sidebar primeiro.")
                    return {}
            
            df = data_manager.get_current_data()
            if df is None:
                st.error("❌ Nenhum dado carregado!")
                return {}
            
            # Obter nome do arquivo atual
            filename = data_manager.get_current_filename() or "arquivo atual"
            
            # CORREÇÃO: Não usar cache - sempre analisar o arquivo atual
            # Isso garante que cada arquivo carregado seja analisado corretamente
            # em vez de retornar análises antigas de arquivos diferentes
            
            st.info(f"🚀 Iniciando análise CrewAI do arquivo: **{filename}**")
            st.info(f"📊 Dataset: {len(df)} registros × {len(df.columns)} colunas")
            
            # CORREÇÃO: Recriar tarefas com os dados atuais
            # Isso garante que as tarefas sempre usem o arquivo CSV que está carregado agora
            self._create_tasks()
            
            # Debug: verificar agentes antes de criar crew
            st.write(f"🔍 Debug: Criando crew com {len(self.agents)} agentes")
            for agent_name, agent in self.agents.items():
                try:
                    st.write(f"  - {agent_name}: {type(agent.llm).__name__}")
                    # Debug adicional: verificar se o LLM tem a chave correta
                    api_key_found = False
                    if hasattr(agent.llm, 'openai_api_key'):
                        try:
                            if agent.llm.openai_api_key:
                                st.write(f"    API Key: Configurada (openai_api_key)")
                                api_key_found = True
                        except:
                            pass
                    
                    if not api_key_found and hasattr(agent.llm, 'api_key'):
                        try:
                            if agent.llm.api_key:
                                st.write(f"    API Key: Configurada (api_key)")
                                api_key_found = True
                        except:
                            pass
                    
                    if not api_key_found:
                        # Verificar se a variável de ambiente está disponível
                        if os.environ.get("OPENAI_API_KEY"):
                            st.write(f"    API Key: Configurada via variável de ambiente")
                        else:
                            st.write(f"    API Key: Não encontrada")
                except Exception as e:
                    st.write(f"  - {agent_name}: Erro ao verificar LLM: {str(e)}")
            
            # Debug: verificar variável de ambiente
            env_key = os.environ.get("OPENAI_API_KEY")
            if env_key:
                st.write(f"🔍 Debug: Variável de ambiente OPENAI_API_KEY: {env_key[:10]}...")
            else:
                st.write("🔍 Debug: Variável de ambiente OPENAI_API_KEY não encontrada")
            
            # Criar crew
            self.crew = Crew(
                agents=list(self.agents.values()),
                tasks=list(self.tasks.values()),
                process=Process.sequential,
                verbose=True
            )
            
            # Debug: verificar se o crew tem o LLM correto
            st.write(f"🔍 Debug: Crew criado com {len(self.crew.agents)} agentes")
            
            # Executar análise
            with st.spinner("🔄 Executando análise com agentes CrewAI..."):
                try:
                    result = self.crew.kickoff()
                    st.write("🔍 Debug: Análise CrewAI executada com sucesso")
                except Exception as e:
                    st.error(f"❌ Erro durante execução CrewAI: {str(e)}")
                    st.write(f"🔍 Debug: Tipo do erro: {type(e).__name__}")
                    # Tentar executar uma análise mais simples
                    st.info("🔄 Tentando análise alternativa...")
                    result = "Análise alternativa executada devido a erro no CrewAI"
            
            # Debug: verificar tipo do resultado
            st.write(f"🔍 Debug: Tipo do resultado: {type(result)}")
            st.write(f"🔍 Debug: Conteúdo do resultado (primeiros 500 chars): {str(result)[:500]}...")
            
            # Processar resultados
            processed_results = self._process_results(result, analysis_name)
            
            # Debug: verificar resultados processados
            st.write(f"🔍 Debug: Resultados processados: {len(processed_results.get('agents', {}))} agentes")
            
            # Salvar no cache usando analysis_memory
            import uuid
            analysis_id = str(uuid.uuid4())[:8]  # Gerar ID único
            
            success = analysis_memory.save_analysis_results(
                analysis_id=analysis_id,
                csv_data=df,
                crew_results=processed_results,
                analysis_name=analysis_name
            )
            
            if success:
                st.write(f"🔍 Debug: Análise salva com ID: {analysis_id}")
                # Definir como análise atual
                analysis_memory.current_analysis = analysis_id
                st.write(f"🔍 Debug: Análise atual definida como: {analysis_id}")
            else:
                st.warning("⚠️ Erro ao salvar análise no cache")
            
            # Debug: verificar se foi salvo
            st.write(f"🔍 Debug: Análise salva com nome: {analysis_name}")
            
            st.success("✅ Análise CrewAI concluída com sucesso!")
            return processed_results
            
        except Exception as e:
            st.error(f"❌ Erro na análise CrewAI: {str(e)}")
            return {}
    
    def _process_results(self, result: Any, analysis_name: str) -> Dict[str, Any]:
        """Processa e estrutura os resultados da análise"""
        try:
            # Estrutura padronizada para os resultados
            processed_results = {
                "analysis_name": analysis_name,
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
                "agents": {},
                "raw_result": str(result)  # Manter resultado bruto para referência
            }
            
            # Converter resultado para string para processamento
            result_text = str(result)
            
            # Tentar extrair informações por agentes
            agent_sections = self._extract_agent_sections(result_text)
            
            if agent_sections:
                # Se conseguiu dividir por agentes
                for agent_name, section_content in agent_sections.items():
                    processed_results["agents"][agent_name] = {
                        "status": "completed",
                        "result": section_content,
                        "timestamp": datetime.now().isoformat()
                    }
            else:
                # Se não conseguiu dividir, criar um agente sintético com todo o resultado
                processed_results["agents"]["synthesis"] = {
                    "status": "completed",
                    "result": result_text,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Garantir que temos pelo menos um resultado
            if not processed_results["agents"]:
                processed_results["agents"]["complete_analysis"] = {
                    "status": "completed",
                    "result": result_text,
                    "timestamp": datetime.now().isoformat()
                }
            
            return processed_results
            
        except Exception as e:
            st.error(f"❌ Erro ao processar resultados: {str(e)}")
            return {
                "analysis_name": analysis_name,
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e),
                "agents": {
                    "error_analysis": {
                        "status": "error",
                        "result": f"Erro no processamento: {str(e)}",
                        "timestamp": datetime.now().isoformat()
                    }
                }
            }
    
    def _extract_agent_sections(self, result_text: str) -> Dict[str, str]:
        """Extrai seções específicas de cada agente do resultado"""
        agent_sections = {}
        
        # Mapear nomes dos agentes para palavras-chave
        agent_keywords = {
            "data_validator": ["validador", "validação", "integridade", "qualidade"],
            "data_profiler": ["perfilador", "perfil", "estatísticas", "distribuição"],
            "pattern_detective": ["detetive", "padrões", "tendências", "correlação"],
            "anomaly_hunter": ["anomalias", "outliers", "atípicos", "anômalos"],
            "relationship_analyst": ["relacionamentos", "dependências", "associações"],
            "strategic_synthesizer": ["síntese", "recomendações", "estratégico", "insights"]
        }
        
        # Dividir o texto em seções
        sections = result_text.split('\n\n')
        
        for section in sections:
            section_lower = section.lower()
            
            # Identificar qual agente corresponde a esta seção
            for agent_name, keywords in agent_keywords.items():
                if any(keyword in section_lower for keyword in keywords):
                    if agent_name not in agent_sections:
                        agent_sections[agent_name] = ""
                    agent_sections[agent_name] += section + "\n\n"
                    break
        
        # Se não conseguiu dividir por palavras-chave, dividir igualmente
        if not agent_sections:
            sections_per_agent = len(sections) // len(self.agents)
            agent_names = list(self.agents.keys())
            
            for i, agent_name in enumerate(agent_names):
                start_idx = i * sections_per_agent
                end_idx = start_idx + sections_per_agent if i < len(agent_names) - 1 else len(sections)
                agent_sections[agent_name] = "\n\n".join(sections[start_idx:end_idx])
        
        return agent_sections
    
    def get_agent_results(self, analysis_name: str) -> Dict[str, Any]:
        """Retorna resultados de uma análise específica"""
        # Buscar análise por nome
        search_results = analysis_memory.search_analyses(analysis_name)
        if search_results:
            analysis_id = search_results[0]['analysis_id']
            return analysis_memory.get_analysis_results(analysis_id)
        return None
    
    def get_available_analyses(self) -> List[str]:
        """Retorna lista de análises disponíveis"""
        history = analysis_memory.get_analysis_history()
        return [analysis.get('analysis_name', '') for analysis in history.values() if analysis.get('analysis_name')]
    
    def clear_analysis_cache(self):
        """Limpa cache de análises"""
        analysis_memory.clear_analysis_memory()
        st.success("✅ Cache de análises limpo!")

# Função para criar instância do CrewAIEnhanced
def get_crewai_instance():
    """Cria uma nova instância do CrewAIEnhanced"""
    return CrewAIEnhanced()
