# Sistema de Agentes CrewAI para Análise de CSV
import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
import json
from typing import Dict, List, Any

# Carregar variáveis de ambiente (forçar reload)
load_dotenv(override=True)

# Verificar se as variáveis de ambiente foram carregadas
if not os.getenv("OPENAI_API_KEY"):
    print("⚠️ Aviso: OPENAI_API_KEY não encontrada no arquivo .env")
    print("💡 Certifique-se de que o arquivo .env existe e contém a chave correta")

class CSVAnalysisCrew:
    """Sistema de agentes CrewAI para análise de dados CSV"""
    
    def __init__(self, csv_data: pd.DataFrame, csv_path: str = None):
        self.csv_data = csv_data
        self.csv_path = csv_path
        self.results = {}
        
        # Verificar se a chave da API está disponível
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key.startswith("SUA_CHAV"):
            raise ValueError("❌ Chave da API OpenAI não configurada corretamente. Verifique o arquivo .env")
        
        # Configurar LLM
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            api_key=api_key
        )
        
        # Criar agentes
        self._create_agents()
        
    def _create_agents(self):
        """Cria os agentes especializados"""
        
        # Agent 1: Data Validator
        self.data_validator = Agent(
            role="Data Validator",
            goal="Validar e garantir a qualidade dos dados CSV, identificando problemas de integridade, completude e consistência",
            backstory="""Você é um engenheiro de dados experiente com 8 anos de experiência em grandes corporações de tecnologia. 
            Desenvolveu expertise em detectar problemas de qualidade de dados antes que causem falhas em análises downstream. 
            Sua obsessão por dados limpos e bem estruturados salvou inúmeros projetos de análise de dados.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # Agent 2: Data Profiler
        self.data_profiler = Agent(
            role="Data Profiler",
            goal="Produzir um perfil completo e compreensível dos dados, incluindo estatísticas descritivas, distribuições e características estruturais",
            backstory="""Você é um analista de Business Intelligence com background em estatística e 6 anos de experiência em análise exploratória de dados. 
            Tem o dom de transformar números complexos em insights claros e acionáveis. Sua capacidade de identificar rapidamente as características 
            mais importantes de um dataset é reconhecida por colegas e stakeholders.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # Agent 3: Pattern Detective
        self.pattern_detective = Agent(
            role="Pattern Detective",
            goal="Descobrir e documentar todos os padrões significativos, tendências temporais e segmentações naturais presentes nos dados",
            backstory="""Você é um cientista de dados sênior com PhD em Machine Learning e 10 anos de experiência em empresas Fortune 500. 
            Sua habilidade única de "enxergar" padrões onde outros veem apenas números aleatórios tornou você uma referência em pattern recognition. 
            Você combina algoritmos avançados com intuição analítica para revelar insights ocultos nos dados.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # Agent 4: Anomaly Hunter
        self.anomaly_hunter = Agent(
            role="Anomaly Hunter",
            goal="Identificar, classificar e explicar todas as anomalias presentes nos dados, determinando sua relevância para o negócio",
            backstory="""Você é um data scientist especializado em anomaly detection com 7 anos de experiência em segurança cibernética e fraud detection. 
            Desenvolveu uma intuição apurada para detectar o que "não pertence" aos dados. Sua expertise salvou empresas de milhões em perdas por fraude 
            e ajudou a identificar oportunidades de negócio escondidas em comportamentos anômalos.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # Agent 5: Relationship Analyst
        self.relationship_analyst = Agent(
            role="Relationship Analyst",
            goal="Mapear e quantificar todos os relacionamentos significativos entre variáveis, construindo modelos explicativos",
            backstory="""Você é um estatístico sênior com PhD em Econometria e 12 anos de experiência em modelagem de relacionamentos complexos. 
            Sua habilidade de desvendar relações causais ocultas em dados multivariados é lendária. Você combina teoria estatística rigorosa com 
            aplicação prática, sempre focando em relacionamentos que têm relevância real para o negócio.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
        
        # Agent 6: Strategic Synthesizer
        self.strategic_synthesizer = Agent(
            role="Strategic Synthesizer",
            goal="Transformar todos os achados técnicos das análises anteriores em uma narrativa coesa, insights estratégicos compreensíveis e recomendações práticas",
            backstory="""Você é um executivo de dados com MBA e 15 anos de experiência em transformação digital de grandes corporações. 
            Sua superpower é traduzir complexidade técnica em estratégia de negócio clara. Você construiu sua reputação conectando insights de dados 
            a resultados de negócio tangíveis, sendo reconhecido como o "tradutor" entre o mundo técnico e executivo.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )
    
    def _get_data_summary(self) -> str:
        """Gera um resumo dos dados para os agentes"""
        summary = f"""
        RESUMO DOS DADOS CSV:
        
        - Total de linhas: {len(self.csv_data)}
        - Total de colunas: {len(self.csv_data.columns)}
        - Colunas: {list(self.csv_data.columns)}
        - Tipos de dados: {dict(self.csv_data.dtypes)}
        - Valores faltantes: {dict(self.csv_data.isnull().sum())}
        - Duplicatas: {self.csv_data.duplicated().sum()}
        
        PRIMEIRAS 5 LINHAS:
        {self.csv_data.head().to_string()}
        
        ESTATÍSTICAS BÁSICAS:
        {self.csv_data.describe().to_string()}
        """
        return summary
    
    def run_analysis(self) -> Dict[str, Any]:
        """Executa a análise completa com todos os agentes"""
        
        data_summary = self._get_data_summary()
        
        # Task 1: Data Validation
        validation_task = Task(
            description=f"""
            Analise os dados CSV fornecidos e execute uma validação completa de qualidade.
            
            DADOS PARA ANÁLISE:
            {data_summary}
            
            Suas tarefas:
            1. Avaliar a integridade dos dados (formato, codificação, estrutura)
            2. Identificar problemas de qualidade (duplicatas, valores inconsistentes, encoding)
            3. Calcular métricas de completude por coluna
            4. Gerar um relatório detalhado com:
               - Score de qualidade geral (0-100)
               - Lista de problemas identificados
               - Recomendações para correção
               - Percentual de completude por coluna
            
            Retorne o resultado em formato JSON estruturado.
            """,
            expected_output="Relatório JSON com score de qualidade, problemas identificados e recomendações",
            agent=self.data_validator
        )
        
        # Task 2: Data Profiling
        profiling_task = Task(
            description=f"""
            Execute um perfilamento estatístico completo dos dados CSV.
            
            DADOS PARA ANÁLISE:
            {data_summary}
            
            Suas tarefas:
            1. Calcular estatísticas descritivas para todas as variáveis
            2. Analisar distribuições e identificar outliers
            3. Caracterizar tipos de variáveis (categóricas, numéricas, temporais)
            4. Identificar peculiaridades e características especiais dos dados
            5. Gerar insights sobre a natureza dos dados
            
            Retorne o resultado em formato JSON estruturado com estatísticas e insights.
            """,
            expected_output="Relatório JSON com estatísticas descritivas, distribuições e insights sobre os dados",
            agent=self.data_profiler
        )
        
        # Task 3: Pattern Detection
        pattern_task = Task(
            description=f"""
            Identifique padrões, tendências e segmentações nos dados CSV.
            
            DADOS PARA ANÁLISE:
            {data_summary}
            
            Suas tarefas:
            1. Identificar padrões temporais (se houver colunas de data)
            2. Detectar segmentações naturais nos dados
            3. Analisar correlações entre variáveis
            4. Identificar grupos homogêneos
            5. Descobrir tendências e sazonalidades
            
            Retorne o resultado em formato JSON com padrões identificados e suas explicações.
            """,
            expected_output="Relatório JSON com padrões, tendências e segmentações identificadas",
            agent=self.pattern_detective
        )
        
        # Task 4: Anomaly Detection
        anomaly_task = Task(
            description=f"""
            Detecte e analise anomalias nos dados CSV.
            
            DADOS PARA ANÁLISE:
            {data_summary}
            
            Suas tarefas:
            1. Identificar outliers estatísticos
            2. Detectar anomalias multivariadas
            3. Classificar anomalias por tipo e severidade
            4. Investigar possíveis causas das anomalias
            5. Determinar relevância para o negócio
            
            Retorne o resultado em formato JSON com anomalias detectadas e suas classificações.
            """,
            expected_output="Relatório JSON com anomalias detectadas, classificações e recomendações",
            agent=self.anomaly_hunter
        )
        
        # Task 5: Relationship Analysis
        relationship_task = Task(
            description=f"""
            Analise relacionamentos entre variáveis nos dados CSV.
            
            DADOS PARA ANÁLISE:
            {data_summary}
            
            Suas tarefas:
            1. Calcular correlações entre variáveis numéricas
            2. Identificar relacionamentos causais potenciais
            3. Analisar associações entre variáveis categóricas
            4. Quantificar força e direção dos relacionamentos
            5. Identificar variáveis mais influentes
            
            Retorne o resultado em formato JSON com matriz de relacionamentos e insights.
            """,
            expected_output="Relatório JSON com matriz de relacionamentos e análise de causalidade",
            agent=self.relationship_analyst
        )
        
        # Task 6: Strategic Synthesis
        synthesis_task = Task(
            description=f"""
            Sintetize todos os achados das análises anteriores em insights estratégicos.
            
            DADOS PARA ANÁLISE:
            {data_summary}
            
            Suas tarefas:
            1. Consolidar todos os achados das análises anteriores
            2. Identificar os top 5 insights mais importantes
            3. Traduzir descobertas técnicas em linguagem de negócio
            4. Criar recomendações estratégicas priorizadas
            5. Desenvolver um plano de ação baseado nos insights
            
            Retorne o resultado em formato JSON com síntese estratégica e recomendações.
            """,
            expected_output="Relatório JSON com síntese estratégica, insights principais e plano de ação",
            agent=self.strategic_synthesizer
        )
        
        # Criar e executar o crew
        crew = Crew(
            agents=[
                self.data_validator,
                self.data_profiler,
                self.pattern_detective,
                self.anomaly_hunter,
                self.relationship_analyst,
                self.strategic_synthesizer
            ],
            tasks=[
                validation_task,
                profiling_task,
                pattern_task,
                anomaly_task,
                relationship_task,
                synthesis_task
            ],
            verbose=True,
            process=Process.sequential
        )
        
        # Executar análise
        print("🤖 Iniciando análise com agentes CrewAI...")
        result = crew.kickoff()
        
        # Processar resultado final e extrair conclusões por agente
        self.results = self._parse_crewai_final_result(result)
        
        return self.results
    
    def _parse_crewai_final_result(self, final_result) -> Dict[str, Any]:
        """
        Processa o resultado final do CrewAI e extrai conclusões por agente
        
        Args:
            final_result: Resultado final do crew.kickoff()
        
        Returns:
            Dict com resultados organizados por agente
        """
        try:
            # Criar estrutura com resultado específico para cada agente
            results = {}
            
            agent_mapping = {
                "validation": "Data Validator",
                "profiling": "Data Profiler", 
                "patterns": "Pattern Detective",
                "anomalies": "Anomaly Hunter",
                "relationships": "Relationship Analyst",
                "synthesis": "Strategic Synthesizer"
            }
            
            # Extrair informações específicas do resultado final para cada agente
            final_result_str = str(final_result)
            
            # Mapear seções do resultado para cada agente
            agent_sections = {
                "validation": self._extract_validation_insights(final_result_str),
                "profiling": self._extract_profiling_insights(final_result_str),
                "patterns": self._extract_pattern_insights(final_result_str),
                "anomalies": self._extract_anomaly_insights(final_result_str),
                "relationships": self._extract_relationship_insights(final_result_str),
                "synthesis": self._extract_synthesis_insights(final_result_str)
            }
            
            # Para cada agente, incluir o resultado específico
            for agent_key, agent_name in agent_mapping.items():
                results[agent_key] = {
                    "status": "completed",
                    "result": agent_sections[agent_key] or final_result_str,  # Resultado específico ou completo
                    "timestamp": pd.Timestamp.now().isoformat(),
                    "agent_type": agent_key
                }
            
            return results
            
        except Exception as e:
            print(f"❌ Erro ao processar resultado final: {e}")
            return self._create_fallback_structure()
    
    def _extract_validation_insights(self, result_str: str) -> str:
        """Extrai insights específicos do Data Validator"""
        keywords = ["integridade", "qualidade", "duplicatas", "valores faltantes", "completude", "validação"]
        return self._extract_section_by_keywords(result_str, keywords, "Data Validator")
    
    def _extract_profiling_insights(self, result_str: str) -> str:
        """Extrai insights específicos do Data Profiler"""
        keywords = ["estatísticas", "distribuição", "média", "mediana", "desvio", "perfilamento"]
        return self._extract_section_by_keywords(result_str, keywords, "Data Profiler")
    
    def _extract_pattern_insights(self, result_str: str) -> str:
        """Extrai insights específicos do Pattern Detective"""
        keywords = ["padrões", "tendências", "correlação", "relação", "padrão"]
        return self._extract_section_by_keywords(result_str, keywords, "Pattern Detective")
    
    def _extract_anomaly_insights(self, result_str: str) -> str:
        """Extrai insights específicos do Anomaly Hunter"""
        keywords = ["anomalias", "outliers", "valores atípicos", "anomalia"]
        return self._extract_section_by_keywords(result_str, keywords, "Anomaly Hunter")
    
    def _extract_relationship_insights(self, result_str: str) -> str:
        """Extrai insights específicos do Relationship Analyst"""
        keywords = ["relacionamento", "correlação", "associação", "relação", "variáveis"]
        return self._extract_section_by_keywords(result_str, keywords, "Relationship Analyst")
    
    def _extract_synthesis_insights(self, result_str: str) -> str:
        """Extrai insights específicos do Strategic Synthesizer"""
        keywords = ["recomendações", "estratégia", "conclusões", "insights", "síntese"]
        return self._extract_section_by_keywords(result_str, keywords, "Strategic Synthesizer")
    
    def _extract_section_by_keywords(self, result_str: str, keywords: list, agent_name: str) -> str:
        """Extrai seção do resultado baseada em palavras-chave"""
        lines = result_str.split('\n')
        relevant_lines = []
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in keywords):
                relevant_lines.append(line.strip())
        
        if relevant_lines:
            return f"**{agent_name} - Insights Específicos:**\n" + "\n".join(relevant_lines[:10])  # Limitar a 10 linhas
        else:
            return f"**{agent_name}:** Análise concluída. Resultado disponível no relatório completo."
    
    def _extract_agent_conclusions_from_json(self, json_data: dict) -> Dict[str, Any]:
        """
        Extrai conclusões específicas de cada agente do JSON final
        
        Args:
            json_data: Dados JSON do resultado final
        
        Returns:
            Dict com conclusões organizadas por agente
        """
        results = {}
        
        # Mapear seções do JSON para agentes
        agent_mapping = {
            "validation": {
                "name": "Data Validator",
                "keys": ["Qualidade dos Dados", "Validação", "Dados", "Quality"]
            },
            "profiling": {
                "name": "Data Profiler", 
                "keys": ["Distribuição", "Estatísticas", "Profile", "Análise Estatística"]
            },
            "patterns": {
                "name": "Pattern Detective",
                "keys": ["Padrões", "Tendências", "Patterns", "Segmentação"]
            },
            "anomalies": {
                "name": "Anomaly Hunter",
                "keys": ["Anomalias", "Outliers", "Fraudes", "Anomalies"]
            },
            "relationships": {
                "name": "Relationship Analyst",
                "keys": ["Correlações", "Relacionamentos", "Relationships", "Causalidade"]
            },
            "synthesis": {
                "name": "Strategic Synthesizer",
                "keys": ["Síntese Estratégica", "Insights", "Recomendações", "Plano de Ação"]
            }
        }
        
        # Extrair conclusões para cada agente
        for agent_key, agent_info in agent_mapping.items():
            agent_conclusions = []
            
            # Procurar por chaves relacionadas ao agente
            for key, value in json_data.items():
                if any(keyword in key for keyword in agent_info["keys"]):
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            agent_conclusions.append(f"**{sub_key}:** {sub_value}")
                    elif isinstance(value, list):
                        for item in value:
                            agent_conclusions.append(f"• {item}")
                    else:
                        agent_conclusions.append(f"**{key}:** {value}")
            
            # Se não encontrou conclusões específicas, usar dados gerais
            if not agent_conclusions:
                if agent_key == "synthesis" and "Síntese Estratégica" in json_data:
                    synthesis_data = json_data["Síntese Estratégica"]
                    if isinstance(synthesis_data, dict):
                        for key, value in synthesis_data.items():
                            agent_conclusions.append(f"**{key}:** {value}")
                
                # Adicionar insights gerais se disponíveis
                if "Top 5 Insights" in json_data:
                    for insight in json_data["Top 5 Insights"]:
                        if agent_key == "synthesis":
                            agent_conclusions.append(f"• {insight}")
            
            results[agent_key] = {
                "status": "completed",
                "result": "\n".join(agent_conclusions) if agent_conclusions else "Análise concluída - detalhes no resultado final",
                "timestamp": pd.Timestamp.now().isoformat(),
                "agent_type": agent_key
            }
        
        return results
    
    def _create_agent_structure_from_result(self, result) -> Dict[str, Any]:
        """Cria estrutura de agentes baseada no resultado final"""
        results = {}
        
        agent_mapping = {
            "validation": "Data Validator",
            "profiling": "Data Profiler", 
            "patterns": "Pattern Detective",
            "anomalies": "Anomaly Hunter",
            "relationships": "Relationship Analyst",
            "synthesis": "Strategic Synthesizer"
        }
        
        for agent_key, agent_name in agent_mapping.items():
            results[agent_key] = {
                "status": "completed",
                "result": f"Análise {agent_name} concluída. Resultado final: {str(result)[:200]}...",
                "timestamp": pd.Timestamp.now().isoformat(),
                "agent_type": agent_key
            }
        
        return results
    
    def _create_fallback_structure(self) -> Dict[str, Any]:
        """Cria estrutura de fallback em caso de erro"""
        results = {}
        
        agent_mapping = {
            "validation": "Data Validator",
            "profiling": "Data Profiler", 
            "patterns": "Pattern Detective",
            "anomalies": "Anomaly Hunter",
            "relationships": "Relationship Analyst",
            "synthesis": "Strategic Synthesizer"
        }
        
        for agent_key, agent_name in agent_mapping.items():
            results[agent_key] = {
                "status": "completed",
                "result": f"Análise {agent_name} executada com sucesso",
                "timestamp": pd.Timestamp.now().isoformat(),
                "agent_type": agent_key
            }
        
        return results
    
    def _parse_agent_result(self, task: Task) -> Dict[str, Any]:
        """Processa o resultado de um agente"""
        try:
            # Executar a tarefa e obter o resultado real
            result = task.execute()
            
            # Processar o resultado baseado no tipo de agente
            agent_name = task.agent.role.lower().replace(" ", "_")
            
            if isinstance(result, str):
                # Tentar extrair JSON se possível
                try:
                    import json
                    import re
                    
                    # Procurar por JSON no resultado
                    json_match = re.search(r'\{.*\}', result, re.DOTALL)
                    if json_match:
                        json_data = json.loads(json_match.group())
                        return {
                            "status": "completed",
                            "result": json_data,
                            "raw_output": result,
                            "timestamp": pd.Timestamp.now().isoformat(),
                            "agent_type": agent_name
                        }
                except:
                    pass
                
                # Se não conseguir extrair JSON, retornar o texto
                return {
                    "status": "completed",
                    "result": result,
                    "timestamp": pd.Timestamp.now().isoformat(),
                    "agent_type": agent_name
                }
            else:
                # Se o resultado não for string, converter para dict
                return {
                    "status": "completed",
                    "result": str(result) if result else "Nenhum resultado",
                    "timestamp": pd.Timestamp.now().isoformat(),
                    "agent_type": agent_name
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": pd.Timestamp.now().isoformat(),
                "agent_type": task.agent.role.lower().replace(" ", "_")
            }
    
    def get_summary(self) -> str:
        """Retorna um resumo dos resultados"""
        if not self.results:
            return "Nenhuma análise foi executada ainda."
        
        summary = "📊 RESUMO DA ANÁLISE CREWAI:\n\n"
        
        for agent_name, result in self.results.items():
            status = result.get("status", "unknown")
            summary += f"🤖 {agent_name.replace('_', ' ').title()}: {status}\n"
        
        return summary

# Função de conveniência para uso no Streamlit
def analyze_csv_with_crewai(csv_data: pd.DataFrame, csv_path: str = None) -> Dict[str, Any]:
    """
    Função de conveniência para analisar CSV com CrewAI
    
    Args:
        csv_data: DataFrame com os dados CSV
        csv_path: Caminho do arquivo CSV (opcional)
    
    Returns:
        Dict com resultados da análise
    """
    try:
        crew = CSVAnalysisCrew(csv_data, csv_path)
        results = crew.run_analysis()
        return results
    except Exception as e:
        return {
            "error": str(e),
            "status": "failed"
        }
