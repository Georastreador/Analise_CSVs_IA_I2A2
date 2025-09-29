import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any, List
import json
from data_manager import data_manager
from chart_generator import ChartDetector
import plotly.express as px
import plotly.graph_objects as go

class SimpleChat:
    """Sistema de chat simplificado e eficaz"""
    
    def __init__(self):
        self.chart_detector = ChartDetector()
        self.suggestions = [
            "Quais são os tipos de dados das colunas?",
            "Quantos registros existem no dataset?",
            "Quais colunas têm valores ausentes?",
            "Mostre a distribuição da coluna [nome_da_coluna]",
            "Quais são os valores únicos em [coluna_categórica]?",
            "Calcule estatísticas descritivas das colunas numéricas",
            "Identifique possíveis outliers nos dados",
            "Mostre a correlação entre variáveis numéricas",
            "Qual é a tendência temporal dos dados?",
            "Resuma os principais insights dos dados"
        ]
    
    def get_data_context(self) -> str:
        """Gera contexto dos dados atuais"""
        df = data_manager.get_current_data()
        if df is None:
            return "Nenhum dado carregado."
        
        summary = data_manager.get_data_summary()
        context = f"""
DADOS CARREGADOS:
- Arquivo: {data_manager.get_current_filename()}
- Registros: {summary.get('total_records', 0):,}
- Colunas: {summary.get('total_columns', 0)}
- Colunas numéricas: {', '.join(summary.get('numeric_columns', []))}
- Colunas categóricas: {', '.join(summary.get('categorical_columns', []))}

ESTATÍSTICAS BÁSICAS:
"""
        
        # Adicionar estatísticas básicas
        basic_stats = summary.get('basic_stats', {})
        for col, stats in basic_stats.items():
            if isinstance(stats, dict):
                context += f"\n{col}:\n"
                for stat_name, value in stats.items():
                    if isinstance(value, (int, float)):
                        context += f"  {stat_name}: {value:.2f}\n"
        
        # Adicionar valores únicos para colunas categóricas
        categorical_cols = summary.get('categorical_columns', [])
        if categorical_cols:
            context += "\nVALORES ÚNICOS (colunas categóricas):\n"
            for col in categorical_cols[:5]:  # Limitar a 5 colunas
                unique_count = df[col].nunique()
                context += f"- {col}: {unique_count} valores únicos\n"
        
        return context
    
    def get_analysis_context(self) -> str:
        """Gera contexto das análises CrewAI disponíveis"""
        available_analyses = data_manager.get_available_analyses()
        if not available_analyses:
            return "Nenhuma análise CrewAI disponível."
        
        context = "ANÁLISES CREWAI DISPONÍVEIS:\n"
        for analysis_name in available_analyses:
            results = data_manager.load_analysis(analysis_name)
            if results:
                context += f"\n{analysis_name.upper()}:\n"
                for agent_name, agent_data in results.items():
                    status = agent_data.get('status', 'unknown')
                    result = agent_data.get('result', 'Nenhum resultado')
                    context += f"- {agent_name}: {status}\n"
                    if isinstance(result, str) and len(result) > 0:
                        # Limitar tamanho para não sobrecarregar o prompt
                        context += f"  {result[:500]}{'...' if len(result) > 500 else ''}\n"
        
        return context
    
    def generate_response(self, user_message: str) -> tuple[str, Optional[Any]]:
        """Gera resposta do chat"""
        try:
            # Verificar se precisa de gráfico
            needs_chart, chart_type = self.chart_detector.needs_chart(user_message)
            
            if needs_chart:
                return self._generate_chart_response(user_message, chart_type)
            else:
                return self._generate_text_response(user_message)
                
        except Exception as e:
            return self._generate_fallback_response(user_message, str(e))
    
    def _generate_chart_response(self, user_message: str, chart_type: str) -> tuple[str, Optional[Any]]:
        """Gera resposta com gráfico"""
        df = data_manager.get_current_data()
        if df is None:
            return "❌ Nenhum dado carregado para gerar gráfico.", None
        
        try:
            # Gerar gráfico baseado no tipo
            if chart_type == "histogram":
                return self._create_histogram(df, user_message)
            elif chart_type == "scatter":
                return self._create_scatter(df, user_message)
            elif chart_type == "bar":
                return self._create_bar_chart(df, user_message)
            elif chart_type == "line":
                return self._create_line_chart(df, user_message)
            else:
                return self._create_general_chart(df, user_message)
                
        except Exception as e:
            return f"❌ Erro ao gerar gráfico: {str(e)}", None
    
    def _create_histogram(self, df: pd.DataFrame, user_message: str) -> tuple[str, Optional[Any]]:
        """Cria histograma"""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if not numeric_cols:
            return "❌ Nenhuma coluna numérica encontrada para histograma.", None
        
        # Tentar identificar coluna específica na mensagem
        selected_col = None
        for col in numeric_cols:
            if col.lower() in user_message.lower():
                selected_col = col
                break
        
        if not selected_col:
            selected_col = numeric_cols[0]
        
        fig = px.histogram(df, x=selected_col, title=f"Distribuição de {selected_col}")
        response = f"📊 Histograma da coluna '{selected_col}' gerado com sucesso!"
        return response, fig
    
    def _create_scatter(self, df: pd.DataFrame, user_message: str) -> tuple[str, Optional[Any]]:
        """Cria gráfico de dispersão"""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if len(numeric_cols) < 2:
            return "❌ São necessárias pelo menos 2 colunas numéricas para gráfico de dispersão.", None
        
        x_col = numeric_cols[0]
        y_col = numeric_cols[1]
        
        fig = px.scatter(df, x=x_col, y=y_col, title=f"Correlação: {x_col} vs {y_col}")
        response = f"📊 Gráfico de dispersão: {x_col} vs {y_col}"
        return response, fig
    
    def _create_bar_chart(self, df: pd.DataFrame, user_message: str) -> tuple[str, Optional[Any]]:
        """Cria gráfico de barras"""
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        if not categorical_cols:
            return "❌ Nenhuma coluna categórica encontrada para gráfico de barras.", None
        
        selected_col = categorical_cols[0]
        value_counts = df[selected_col].value_counts().head(10)
        
        fig = px.bar(x=value_counts.index, y=value_counts.values, 
                    title=f"Frequência de {selected_col}")
        response = f"📊 Gráfico de barras da coluna '{selected_col}'"
        return response, fig
    
    def _create_line_chart(self, df: pd.DataFrame, user_message: str) -> tuple[str, Optional[Any]]:
        """Cria gráfico de linha"""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if not numeric_cols:
            return "❌ Nenhuma coluna numérica encontrada para gráfico de linha.", None
        
        selected_col = numeric_cols[0]
        fig = px.line(df, y=selected_col, title=f"Tendência de {selected_col}")
        response = f"📊 Gráfico de linha da coluna '{selected_col}'"
        return response, fig
    
    def _create_general_chart(self, df: pd.DataFrame, user_message: str) -> tuple[str, Optional[Any]]:
        """Cria gráfico geral baseado nos dados"""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        if numeric_cols and categorical_cols:
            # Box plot: numérico vs categórico
            fig = px.box(df, x=categorical_cols[0], y=numeric_cols[0], 
                        title=f"Distribuição de {numeric_cols[0]} por {categorical_cols[0]}")
            response = f"📊 Box plot: {numeric_cols[0]} por {categorical_cols[0]}"
        elif numeric_cols:
            # Histograma da primeira coluna numérica
            fig = px.histogram(df, x=numeric_cols[0], title=f"Distribuição de {numeric_cols[0]}")
            response = f"📊 Histograma da coluna '{numeric_cols[0]}'"
        else:
            # Gráfico de barras da primeira coluna categórica
            value_counts = df[categorical_cols[0]].value_counts().head(10)
            fig = px.bar(x=value_counts.index, y=value_counts.values, 
                        title=f"Frequência de {categorical_cols[0]}")
            response = f"📊 Gráfico de barras da coluna '{categorical_cols[0]}'"
        
        return response, fig
    
    def _generate_text_response(self, user_message: str) -> tuple[str, Optional[Any]]:
        """Gera resposta textual baseada nos dados"""
        df = data_manager.get_current_data()
        if df is None:
            return "❌ Nenhum dado carregado. Carregue um arquivo CSV primeiro.", None
        
        # Respostas baseadas em padrões comuns
        user_lower = user_message.lower()
        
        if "tipos de dados" in user_lower or "tipos" in user_lower:
            return self._answer_data_types(df)
        elif "registros" in user_lower or "linhas" in user_lower:
            return self._answer_records_count(df)
        elif "colunas" in user_lower and "ausentes" in user_lower:
            return self._answer_missing_values(df)
        elif "estatísticas" in user_lower or "descritivas" in user_lower:
            return self._answer_descriptive_stats(df)
        elif "valores únicos" in user_lower:
            return self._answer_unique_values(df)
        elif "outliers" in user_lower:
            return self._answer_outliers(df)
        elif "correlação" in user_lower:
            return self._answer_correlation(df)
        elif "insights" in user_lower or "conclusões" in user_lower:
            return self._answer_insights()
        else:
            return self._answer_general_question(user_message, df)
    
    def _answer_data_types(self, df: pd.DataFrame) -> tuple[str, Optional[Any]]:
        """Responde sobre tipos de dados"""
        response = "📊 **Tipos de Dados das Colunas:**\n\n"
        for col in df.columns:
            dtype = str(df[col].dtype)
            response += f"• **{col}**: {dtype}\n"
        return response, None
    
    def _answer_records_count(self, df: pd.DataFrame) -> tuple[str, Optional[Any]]:
        """Responde sobre número de registros"""
        response = f"📊 **Total de Registros:** {len(df):,}\n"
        response += f"📊 **Total de Colunas:** {len(df.columns)}\n"
        return response, None
    
    def _answer_missing_values(self, df: pd.DataFrame) -> tuple[str, Optional[Any]]:
        """Responde sobre valores ausentes"""
        missing = df.isnull().sum()
        response = "📊 **Valores Ausentes por Coluna:**\n\n"
        for col, count in missing.items():
            if count > 0:
                percentage = (count / len(df)) * 100
                response += f"• **{col}**: {count:,} ({percentage:.1f}%)\n"
        
        if missing.sum() == 0:
            response += "✅ Nenhum valor ausente encontrado!"
        
        return response, None
    
    def _answer_descriptive_stats(self, df: pd.DataFrame) -> tuple[str, Optional[Any]]:
        """Responde sobre estatísticas descritivas"""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if not numeric_cols:
            return "❌ Nenhuma coluna numérica encontrada para estatísticas descritivas.", None
        
        response = "📊 **Estatísticas Descritivas:**\n\n"
        stats = df[numeric_cols].describe()
        
        for col in numeric_cols:
            response += f"**{col}:**\n"
            response += f"• Média: {stats.loc['mean', col]:.2f}\n"
            response += f"• Mediana: {stats.loc['50%', col]:.2f}\n"
            response += f"• Desvio Padrão: {stats.loc['std', col]:.2f}\n"
            response += f"• Mínimo: {stats.loc['min', col]:.2f}\n"
            response += f"• Máximo: {stats.loc['max', col]:.2f}\n\n"
        
        return response, None
    
    def _answer_unique_values(self, df: pd.DataFrame) -> tuple[str, Optional[Any]]:
        """Responde sobre valores únicos"""
        response = "📊 **Valores Únicos por Coluna:**\n\n"
        for col in df.columns:
            unique_count = df[col].nunique()
            response += f"• **{col}**: {unique_count:,} valores únicos\n"
        return response, None
    
    def _answer_outliers(self, df: pd.DataFrame) -> tuple[str, Optional[Any]]:
        """Responde sobre outliers"""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if not numeric_cols:
            return "❌ Nenhuma coluna numérica encontrada para análise de outliers.", None
        
        response = "📊 **Análise de Outliers:**\n\n"
        for col in numeric_cols[:5]:  # Limitar a 5 colunas
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = df[(df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))]
            response += f"• **{col}**: {len(outliers)} outliers\n"
        
        return response, None
    
    def _answer_correlation(self, df: pd.DataFrame) -> tuple[str, Optional[Any]]:
        """Responde sobre correlação"""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if len(numeric_cols) < 2:
            return "❌ São necessárias pelo menos 2 colunas numéricas para análise de correlação.", None
        
        corr_matrix = df[numeric_cols].corr()
        response = "📊 **Correlações Significativas:**\n\n"
        
        # Encontrar correlações fortes
        strong_correlations = []
        for i in range(len(numeric_cols)):
            for j in range(i + 1, len(numeric_cols)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:
                    strong_correlations.append((numeric_cols[i], numeric_cols[j], corr_value))
        
        if strong_correlations:
            for col1, col2, corr in strong_correlations:
                response += f"• **{col1}** ↔ **{col2}**: {corr:.3f}\n"
        else:
            response += "Nenhuma correlação forte (>0.7) encontrada entre as variáveis numéricas.\n"
        
        return response, None
    
    def _answer_insights(self) -> tuple[str, Optional[Any]]:
        """Responde sobre insights das análises CrewAI"""
        analysis_context = self.get_analysis_context()
        if "Nenhuma análise CrewAI disponível" in analysis_context:
            return "❌ Nenhuma análise CrewAI disponível. Execute uma análise primeiro.", None
        
        response = "🎯 **Insights das Análises CrewAI:**\n\n"
        response += analysis_context
        return response, None
    
    def _answer_general_question(self, user_message: str, df: pd.DataFrame) -> tuple[str, Optional[Any]]:
        """Responde perguntas gerais"""
        # Tentar extrair informações específicas da pergunta
        if "maior" in user_message.lower() or "máximo" in user_message.lower():
            return self._answer_max_values(df, user_message)
        elif "menor" in user_message.lower() or "mínimo" in user_message.lower():
            return self._answer_min_values(df, user_message)
        elif "média" in user_message.lower() or "médio" in user_message.lower():
            return self._answer_mean_values(df, user_message)
        else:
            return self._answer_data_overview(df)
    
    def _answer_max_values(self, df: pd.DataFrame, user_message: str) -> tuple[str, Optional[Any]]:
        """Responde sobre valores máximos"""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if not numeric_cols:
            return "❌ Nenhuma coluna numérica encontrada.", None
        
        response = "📊 **Valores Máximos:**\n\n"
        for col in numeric_cols:
            max_val = df[col].max()
            response += f"• **{col}**: {max_val:.2f}\n"
        return response, None
    
    def _answer_min_values(self, df: pd.DataFrame, user_message: str) -> tuple[str, Optional[Any]]:
        """Responde sobre valores mínimos"""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if not numeric_cols:
            return "❌ Nenhuma coluna numérica encontrada.", None
        
        response = "📊 **Valores Mínimos:**\n\n"
        for col in numeric_cols:
            min_val = df[col].min()
            response += f"• **{col}**: {min_val:.2f}\n"
        return response, None
    
    def _answer_mean_values(self, df: pd.DataFrame, user_message: str) -> tuple[str, Optional[Any]]:
        """Responde sobre valores médios"""
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if not numeric_cols:
            return "❌ Nenhuma coluna numérica encontrada.", None
        
        response = "📊 **Valores Médios:**\n\n"
        for col in numeric_cols:
            mean_val = df[col].mean()
            response += f"• **{col}**: {mean_val:.2f}\n"
        return response, None
    
    def _answer_data_overview(self, df: pd.DataFrame) -> tuple[str, Optional[Any]]:
        """Responde com visão geral dos dados"""
        response = "📊 **Visão Geral dos Dados:**\n\n"
        response += f"• **Total de registros**: {len(df):,}\n"
        response += f"• **Total de colunas**: {len(df.columns)}\n"
        response += f"• **Colunas numéricas**: {len(df.select_dtypes(include=['number']).columns)}\n"
        response += f"• **Colunas categóricas**: {len(df.select_dtypes(include=['object']).columns)}\n"
        response += f"• **Valores ausentes**: {df.isnull().sum().sum():,}\n"
        response += f"• **Registros duplicados**: {df.duplicated().sum():,}\n"
        return response, None
    
    def _generate_fallback_response(self, user_message: str, error: str) -> tuple[str, Optional[Any]]:
        """Gera resposta de fallback quando há erro"""
        df = data_manager.get_current_data()
        if df is None:
            return "❌ Nenhum dado carregado. Carregue um arquivo CSV primeiro.", None
        
        return f"⚠️ Erro ao processar pergunta: {error}\n\n📊 Dados disponíveis: {len(df):,} registros × {len(df.columns)} colunas", None
    
    def show_suggestions(self):
        """Mostra sugestões de perguntas em 2 colunas"""
        if self.suggestions:
            st.markdown("#### 💡 Sugestões de Perguntas:")
            col1, col2 = st.columns(2)
            mid_point = len(self.suggestions) // 2
            suggestions_col1 = self.suggestions[:mid_point]
            suggestions_col2 = self.suggestions[mid_point:]
            
            with col1:
                for suggestion in suggestions_col1:
                    st.markdown(f"• {suggestion}")
            
            with col2:
                for suggestion in suggestions_col2:
                    st.markdown(f"• {suggestion}")

# Instância global do SimpleChat
simple_chat = SimpleChat()
