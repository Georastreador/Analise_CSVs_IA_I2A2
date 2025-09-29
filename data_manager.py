import pandas as pd
import streamlit as st
import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib

class DataManager:
    """Sistema central de dados para gerenciar CSV e análises CrewAI"""
    
    def __init__(self):
        self.current_df: Optional[pd.DataFrame] = None
        self.current_filename: Optional[str] = None
        self.analysis_cache: Dict[str, Any] = {}
        self.cache_dir = "cache"
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Garante que o diretório de cache existe"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _get_file_hash(self, filename: str) -> str:
        """Gera hash único para o arquivo"""
        return hashlib.md5(filename.encode()).hexdigest()
    
    def load_csv(self, uploaded_files) -> Optional[pd.DataFrame]:
        """Carrega arquivo CSV e atualiza o estado atual"""
        try:
            if uploaded_files:
                file = uploaded_files[0]
                self.current_filename = file.name
                
                # Tentar diferentes encodings
                encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
                df = None
                
                for encoding in encodings:
                    try:
                        file.seek(0)  # Reset file pointer
                        df = pd.read_csv(file, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                
                if df is None:
                    st.error("❌ Não foi possível carregar o arquivo com nenhum encoding suportado.")
                    return None
                
                # Limpar dados
                df = self._clean_dataframe(df)
                self.current_df = df
                
                # Limpar cache antigo se arquivo mudou
                self._clear_old_cache()
                
                st.success(f"✅ Arquivo '{self.current_filename}' carregado com sucesso!")
                st.info(f"📊 Dados: {len(df):,} registros × {len(df.columns)} colunas")
                
                return df
            else:
                st.info("📁 Nenhum arquivo carregado.")
                return None
                
        except Exception as e:
            st.error(f"❌ Erro ao carregar arquivo: {str(e)}")
            return None
    
    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpa e prepara o DataFrame"""
        # Remover colunas completamente vazias
        df = df.dropna(axis=1, how='all')
        
        # Converter colunas numéricas
        for col in df.columns:
            if df[col].dtype == 'object':
                # Tentar converter para numérico
                try:
                    df[col] = pd.to_numeric(df[col], errors='ignore')
                except:
                    pass
        
        return df
    
    def _clear_old_cache(self):
        """Limpa cache de análises antigas"""
        if self.current_filename:
            file_hash = self._get_file_hash(self.current_filename)
            cache_file = os.path.join(self.cache_dir, f"{file_hash}_analysis.json")
            if os.path.exists(cache_file):
                try:
                    os.remove(cache_file)
                except:
                    pass
    
    def get_current_data(self) -> Optional[pd.DataFrame]:
        """Retorna os dados atuais"""
        return self.current_df
    
    def get_current_filename(self) -> Optional[str]:
        """Retorna o nome do arquivo atual"""
        return self.current_filename
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Retorna resumo dos dados atuais"""
        if self.current_df is None:
            return {}
        
        df = self.current_df
        summary = {
            "total_records": len(df),
            "total_columns": len(df.columns),
            "columns": list(df.columns),
            "data_types": df.dtypes.to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "numeric_columns": df.select_dtypes(include=['number']).columns.tolist(),
            "categorical_columns": df.select_dtypes(include=['object']).columns.tolist(),
            "basic_stats": {}
        }
        
        # Estatísticas básicas para colunas numéricas
        numeric_cols = summary["numeric_columns"]
        if numeric_cols:
            summary["basic_stats"] = df[numeric_cols].describe().to_dict()
        
        return summary
    
    def save_analysis(self, analysis_name: str, results: Dict[str, Any]) -> bool:
        """Salva análise no cache"""
        try:
            # Usar filename atual ou criar um nome padrão
            filename = self.current_filename or "default_analysis"
            file_hash = self._get_file_hash(filename)
            cache_file = os.path.join(self.cache_dir, f"{file_hash}_{analysis_name}.json")
            
            cache_data = {
                "filename": filename,
                "analysis_name": analysis_name,
                "timestamp": datetime.now().isoformat(),
                "results": results
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            # Atualizar cache em memória
            self.analysis_cache[analysis_name] = results
            
            return True
            
        except Exception as e:
            st.error(f"❌ Erro ao salvar análise: {str(e)}")
            return False
    
    def load_analysis(self, analysis_name: str) -> Optional[Dict[str, Any]]:
        """Carrega análise do cache"""
        try:
            # Primeiro tentar cache em memória
            if analysis_name in self.analysis_cache:
                return self.analysis_cache[analysis_name]
            
            # Tentar carregar do disco - procurar por arquivos que contenham o nome da análise
            cache_files = []
            if os.path.exists(self.cache_dir):
                for file in os.listdir(self.cache_dir):
                    if file.endswith(f"_{analysis_name}.json"):
                        cache_files.append(os.path.join(self.cache_dir, file))
            
            # Se não encontrou com o novo padrão, tentar o padrão antigo
            if not cache_files and self.current_filename:
                file_hash = self._get_file_hash(self.current_filename)
                old_cache_file = os.path.join(self.cache_dir, f"{file_hash}_analysis.json")
                if os.path.exists(old_cache_file):
                    cache_files.append(old_cache_file)
            
            # Carregar o primeiro arquivo encontrado
            for cache_file in cache_files:
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    if cache_data.get("analysis_name") == analysis_name:
                        results = cache_data.get("results", {})
                        # Atualizar cache em memória
                        self.analysis_cache[analysis_name] = results
                        return results
                except:
                    continue
            
            return None
            
        except Exception as e:
            st.error(f"❌ Erro ao carregar análise: {str(e)}")
            return None
    
    def get_available_analyses(self) -> List[str]:
        """Retorna lista de análises disponíveis"""
        analyses = set(self.analysis_cache.keys())
        
        # Também procurar no disco
        if os.path.exists(self.cache_dir):
            for file in os.listdir(self.cache_dir):
                if file.endswith("_analysis.json") or "_" in file and file.endswith(".json"):
                    try:
                        with open(os.path.join(self.cache_dir, file), 'r', encoding='utf-8') as f:
                            cache_data = json.load(f)
                        analysis_name = cache_data.get("analysis_name")
                        if analysis_name:
                            analyses.add(analysis_name)
                    except:
                        continue
        
        return list(analyses)
    
    def clear_cache(self):
        """Limpa todo o cache"""
        self.analysis_cache.clear()
        try:
            for file in os.listdir(self.cache_dir):
                if file.endswith("_analysis.json"):
                    os.remove(os.path.join(self.cache_dir, file))
        except:
            pass
    
    def validate_data_integrity(self) -> Dict[str, Any]:
        """Valida integridade dos dados atuais"""
        if self.current_df is None:
            return {"valid": False, "message": "Nenhum dado carregado"}
        
        df = self.current_df
        issues = []
        
        # Verificar se DataFrame não está vazio
        if len(df) == 0:
            issues.append("DataFrame está vazio")
        
        # Verificar se há colunas
        if len(df.columns) == 0:
            issues.append("Nenhuma coluna encontrada")
        
        # Verificar valores duplicados
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            issues.append(f"{duplicates} registros duplicados encontrados")
        
        # Verificar valores ausentes
        missing_percent = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        if missing_percent > 50:
            issues.append(f"{missing_percent:.1f}% dos valores estão ausentes")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "duplicates": duplicates,
            "missing_percent": missing_percent,
            "data_quality": "Boa" if len(issues) == 0 else "Atenção necessária"
        }

# Instância global do DataManager
data_manager = DataManager()
