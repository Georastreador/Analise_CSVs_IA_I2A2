# Sistema de Memória para Análises CrewAI
import json
import os
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
import pickle

class AnalysisMemory:
    """Sistema de memória para armazenar e recuperar resultados de análises dos agentes CrewAI"""
    
    def __init__(self, memory_dir: str = "analysis_memory"):
        self.memory_dir = memory_dir
        self.ensure_memory_dir()
        self.current_analysis = self.load_current_analysis()
        self.analysis_history = self.load_analysis_history()
    
    def ensure_memory_dir(self):
        """Garante que o diretório de memória existe"""
        if not os.path.exists(self.memory_dir):
            os.makedirs(self.memory_dir)
    
    def _convert_dataframe_to_json_safe(self, df: pd.DataFrame) -> List[Dict]:
        """
        Converte DataFrame para formato JSON-safe
        
        Args:
            df: DataFrame para converter
        
        Returns:
            Lista de dicionários JSON-safe
        """
        try:
            # Converter para dict e depois processar valores não serializáveis
            data = df.to_dict('records')
            
            # Processar cada registro para garantir que todos os valores sejam JSON-safe
            json_safe_data = []
            for record in data:
                json_safe_record = {}
                for key, value in record.items():
                    if pd.isna(value):
                        json_safe_record[key] = None
                    elif isinstance(value, (pd.Timestamp, pd.DatetimeTZDtype)):
                        json_safe_record[key] = str(value)
                    elif hasattr(value, 'item'):  # Para numpy types
                        json_safe_record[key] = value.item()
                    else:
                        json_safe_record[key] = value
                json_safe_data.append(json_safe_record)
            
            return json_safe_data
        except Exception as e:
            # Se houver erro, retornar dados básicos
            return [{"error": f"Erro ao converter dados: {str(e)}"}]
    
    def save_analysis_results(self, analysis_id: str, csv_data: pd.DataFrame, 
                            crew_results: Dict[str, Any], analysis_name: str = "Análise CSV") -> bool:
        """
        Salva os resultados de uma análise dos agentes CrewAI
        
        Args:
            analysis_id: ID único da análise
            csv_data: DataFrame com os dados analisados
            crew_results: Resultados dos agentes CrewAI
            analysis_name: Nome da análise
        
        Returns:
            bool: True se salvou com sucesso
        """
        try:
            # Criar estrutura de dados da análise
            analysis_data = {
                "analysis_id": analysis_id,
                "analysis_name": analysis_name,
                "timestamp": datetime.now().isoformat(),
                "data_summary": {
                    "rows": len(csv_data),
                    "columns": len(csv_data.columns),
                    "column_names": csv_data.columns.tolist(),
                    "data_types": {col: str(dtype) for col, dtype in csv_data.dtypes.items()},
                    "sample_data": self._convert_dataframe_to_json_safe(csv_data.head(3))
                },
                "crew_results": crew_results,
                "status": "completed"
            }
            
            # Salvar dados da análise
            analysis_file = os.path.join(self.memory_dir, f"{analysis_id}.json")
            # Garantir que os dados sejam JSON-safe
            json_safe_data = self._make_json_safe(analysis_data)
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(json_safe_data, f, ensure_ascii=False, indent=2)
            
            # Salvar dados CSV (amostra)
            csv_sample_file = os.path.join(self.memory_dir, f"{analysis_id}_sample.csv")
            csv_data.head(100).to_csv(csv_sample_file, index=False)
            
            # Atualizar histórico
            self.analysis_history[analysis_id] = {
                "analysis_name": analysis_name,
                "timestamp": analysis_data["timestamp"],
                "status": "completed",
                "data_summary": analysis_data["data_summary"]
            }
            
            # Salvar histórico atualizado
            self.save_analysis_history()
            
            # Definir como análise atual
            self.current_analysis = analysis_id
            self.save_current_analysis()
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar análise: {str(e)}")
            return False
    
    def get_analysis_results(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Recupera os resultados de uma análise específica
        
        Args:
            analysis_id: ID da análise
        
        Returns:
            Dict com resultados da análise ou None se não encontrada
        """
        try:
            analysis_file = os.path.join(self.memory_dir, f"{analysis_id}.json")
            if os.path.exists(analysis_file):
                with open(analysis_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"❌ Erro ao recuperar análise: {str(e)}")
            return None
    
    def get_current_analysis_results(self) -> Optional[Dict[str, Any]]:
        """Recupera os resultados da análise atual"""
        if self.current_analysis:
            return self.get_analysis_results(self.current_analysis)
        return None
    
    def get_analysis_history(self) -> Dict[str, Dict[str, Any]]:
        """Retorna o histórico de análises"""
        return self.analysis_history
    
    def load_analysis_history(self) -> Dict[str, Dict[str, Any]]:
        """Carrega o histórico de análises do arquivo"""
        try:
            history_file = os.path.join(self.memory_dir, "analysis_history.json")
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"❌ Erro ao carregar histórico: {str(e)}")
            return {}
    
    def save_analysis_history(self):
        """Salva o histórico de análises"""
        try:
            history_file = os.path.join(self.memory_dir, "analysis_history.json")
            # Garantir que o histórico seja JSON-safe
            json_safe_history = self._make_json_safe(self.analysis_history)
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(json_safe_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Erro ao salvar histórico: {str(e)}")
    
    def _make_json_safe(self, obj):
        """
        Converte objeto para formato JSON-safe recursivamente
        
        Args:
            obj: Objeto para converter
        
        Returns:
            Objeto JSON-safe
        """
        if isinstance(obj, dict):
            return {key: self._make_json_safe(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_safe(item) for item in obj]
        elif pd.isna(obj):
            return None
        elif isinstance(obj, (pd.Timestamp, pd.DatetimeTZDtype)):
            return str(obj)
        elif hasattr(obj, 'item'):  # Para numpy types
            return obj.item()
        elif hasattr(obj, 'dtype'):  # Para pandas dtypes
            return str(obj)
        else:
            return obj
    
    def get_agent_conclusions(self, analysis_id: str = None) -> Dict[str, Any]:
        """
        Extrai as conclusões de cada agente de uma análise
        
        Args:
            analysis_id: ID da análise (usa análise atual se None)
        
        Returns:
            Dict com conclusões de cada agente
        """
        if analysis_id is None:
            analysis_id = self.current_analysis
        
        if not analysis_id:
            return {}
        
        analysis_data = self.get_analysis_results(analysis_id)
        if not analysis_data:
            return {}
        
        crew_results = analysis_data.get("crew_results", {})
        conclusions = {}
        
        # Obter agentes diretamente dos resultados armazenados
        agents = crew_results.get("agents", {})
        
        # Mapear nomes dos agentes para nomes mais legíveis
        agent_name_mapping = {
            "data_validator": "Data Validator",
            "data_profiler": "Data Profiler",
            "pattern_detective": "Pattern Detective", 
            "anomaly_hunter": "Anomaly Hunter",
            "relationship_analyst": "Relationship Analyst",
            "strategic_synthesizer": "Strategic Synthesizer",
            "synthesis": "Strategic Synthesizer",
            "complete_analysis": "Complete Analysis"
        }
        
        for agent_key, agent_data in agents.items():
            # Usar nome mapeado ou o nome original
            agent_name = agent_name_mapping.get(agent_key, agent_key.replace("_", " ").title())
            result = agent_data.get("result", "Nenhum resultado disponível")
            
            # Manter resultado completo para o chat
            formatted_result = result
            
            conclusions[agent_name] = {
                "status": agent_data.get("status", "unknown"),
                "result": formatted_result,
                "timestamp": agent_data.get("timestamp", ""),
                "agent_type": agent_key
            }
        
        return conclusions
    
    def search_analyses(self, query: str) -> List[Dict[str, Any]]:
        """
        Busca análises por nome ou conteúdo
        
        Args:
            query: Termo de busca
        
        Returns:
            Lista de análises que correspondem à busca
        """
        results = []
        query_lower = query.lower()
        
        for analysis_id, analysis_info in self.analysis_history.items():
            # Buscar no nome da análise
            if query_lower in analysis_info.get("analysis_name", "").lower():
                results.append({
                    "analysis_id": analysis_id,
                    "analysis_name": analysis_info["analysis_name"],
                    "timestamp": analysis_info["timestamp"],
                    "match_type": "name"
                })
                continue
            
            # Buscar no resumo dos dados
            data_summary = analysis_info.get("data_summary", {})
            column_names = data_summary.get("column_names", [])
            for col in column_names:
                if query_lower in col.lower():
                    results.append({
                        "analysis_id": analysis_id,
                        "analysis_name": analysis_info["analysis_name"],
                        "timestamp": analysis_info["timestamp"],
                        "match_type": "column",
                        "matched_column": col
                    })
                    break
        
        return results
    
    def get_analysis_summary(self, analysis_id: str = None) -> str:
        """
        Gera um resumo textual da análise
        
        Args:
            analysis_id: ID da análise (usa análise atual se None)
        
        Returns:
            String com resumo da análise
        """
        if analysis_id is None:
            analysis_id = self.current_analysis
        
        if not analysis_id:
            return "Nenhuma análise disponível."
        
        analysis_data = self.get_analysis_results(analysis_id)
        if not analysis_data:
            return "Análise não encontrada."
        
        data_summary = analysis_data.get("data_summary", {})
        crew_results = analysis_data.get("crew_results", {})
        
        summary = f"""
📊 **RESUMO DA ANÁLISE: {analysis_data.get('analysis_name', 'N/A')}**

📅 **Data/Hora:** {analysis_data.get('timestamp', 'N/A')}

📋 **Dados Analisados:**
- Registros: {data_summary.get('rows', 0):,}
- Colunas: {data_summary.get('columns', 0)}
- Colunas: {', '.join(data_summary.get('column_names', [])[:5])}{'...' if len(data_summary.get('column_names', [])) > 5 else ''}

🤖 **Status dos Agentes:**
"""
        
        agent_mapping = {
            "validation": "🔍 Data Validator",
            "profiling": "📊 Data Profiler", 
            "patterns": "🎯 Pattern Detective",
            "anomalies": "⚠️ Anomaly Hunter",
            "relationships": "🔗 Relationship Analyst",
            "synthesis": "🎯 Strategic Synthesizer"
        }
        
        for agent_key, agent_name in agent_mapping.items():
            agent_result = crew_results.get(agent_key, {})
            status = agent_result.get("status", "unknown")
            status_emoji = "✅" if status == "completed" else "❌" if status == "error" else "⏳"
            summary += f"- {agent_name}: {status_emoji} {status}\n"
        
        return summary
    
    def clear_analysis_memory(self):
        """Limpa toda a memória de análises"""
        try:
            import shutil
            if os.path.exists(self.memory_dir):
                shutil.rmtree(self.memory_dir)
            self.ensure_memory_dir()
            self.analysis_history = {}
            self.current_analysis = None
            self.save_current_analysis()
            return True
        except Exception as e:
            print(f"❌ Erro ao limpar memória: {str(e)}")
            return False
    
    def save_current_analysis(self):
        """Salva a análise atual em arquivo"""
        try:
            current_file = os.path.join(self.memory_dir, "current_analysis.txt")
            with open(current_file, 'w', encoding='utf-8') as f:
                f.write(self.current_analysis or "")
            return True
        except Exception as e:
            print(f"❌ Erro ao salvar análise atual: {str(e)}")
            return False
    
    def load_current_analysis(self):
        """Carrega a análise atual do arquivo"""
        try:
            current_file = os.path.join(self.memory_dir, "current_analysis.txt")
            if os.path.exists(current_file):
                with open(current_file, 'r', encoding='utf-8') as f:
                    analysis_id = f.read().strip()
                    # Verificar se a análise ainda existe
                    if analysis_id and self.get_analysis_results(analysis_id):
                        return analysis_id
            return None
        except Exception as e:
            print(f"❌ Erro ao carregar análise atual: {str(e)}")
            return None

# Instância global do sistema de memória
analysis_memory = AnalysisMemory()
