"""
Sistema de Detecção e Geração Automática de Gráficos
Detecta perguntas que requerem visualizações e gera gráficos apropriados
"""

import re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class ChartDetector:
    """Detecta se uma pergunta requer visualização gráfica"""
    
    def __init__(self):
        # Palavras-chave que indicam necessidade de gráficos (EXPANDIDO)
        self.chart_keywords = {
            'distribuicao': ['distribuição', 'distribuicao', 'histograma', 'frequência', 'frequencia', 'como estão distribuídos', 'distribuição dos dados'],
            'correlacao': ['correlação', 'correlacao', 'relação', 'relacao', 'associação', 'associacao', 'como se relacionam', 'relacionamento entre'],
            'tendencia': ['tendência', 'tendencia', 'evolução', 'evolucao', 'crescimento', 'decrescimento', 'como evolui', 'tendências nos dados'],
            'comparacao': ['comparar', 'comparação', 'comparacao', 'diferença', 'diferenca', 'maior', 'menor', 'quais são os maiores', 'quais são os menores'],
            'agrupamento': ['cluster', 'agrupamento', 'grupos', 'segmentação', 'segmentacao', 'como agrupar', 'padrões de agrupamento'],
            'ranking': ['ranking', 'top', 'melhor', 'pior', 'maior', 'menor', 'ordenar', 'quais são os top', 'ranking dos valores'],
            'geografico': ['mapa', 'geográfico', 'geografico', 'região', 'regiao', 'país', 'pais', 'distribuição geográfica'],
            'temporal': ['tempo', 'data', 'período', 'periodo', 'ano', 'mês', 'mes', 'dia', 'evolução temporal', 'ao longo do tempo'],
            'categoria': ['categoria', 'tipo', 'classe', 'grupo', 'segmento', 'distribuição por categoria'],
            'estatisticas': ['estatísticas', 'estatisticas', 'média', 'mediana', 'desvio', 'quartis', 'resumo estatístico'],
            'outliers': ['outliers', 'valores atípicos', 'anomalias', 'valores extremos', 'detecção de anomalias'],
            'visualizacao': ['visualizar', 'mostrar', 'gráfico', 'grafico', 'plot', 'chart', 'visualização', 'visualizacao']
        }
        
        # Padrões de perguntas que requerem gráficos (EXPANDIDO)
        self.chart_patterns = [
            r'mostre.*gráfico', r'mostre.*grafico', r'mostre.*chart',
            r'visualize.*dados', r'visualizar.*dados',
            r'plote.*informação', r'plot.*dados',
            r'crie.*gráfico', r'crie.*grafico',
            r'gere.*visualização', r'gere.*visualizacao',
            r'como.*distribuído', r'como.*distribuicao',
            r'qual.*relação', r'qual.*relacao',
            r'existe.*correlação', r'existe.*correlacao',
            r'mostre.*tendência', r'mostre.*tendencia',
            r'compare.*valores', r'comparar.*valores',
            r'quais.*maiores', r'quais.*menores',
            r'como.*agrupados', r'como.*agrupamento',
            r'existe.*cluster', r'padrões.*cluster',
            r'mostre.*mapa', r'visualizar.*mapa',
            r'evolução.*tempo', r'evolucao.*tempo',
            r'crescimento.*período', r'crescimento.*periodo',
            r'quais.*tipos', r'quais.*categorias',
            r'como.*variam', r'variação.*dados',
            r'histograma', r'box.*plot', r'boxplot',
            r'scatter.*plot', r'gráfico.*dispersão',
            r'heatmap', r'matriz.*correlação',
            r'gráfico.*linha', r'grafico.*linha',
            r'gráfico.*barras', r'grafico.*barras',
            r'gráfico.*pizza', r'grafico.*pizza',
            r'outliers', r'anomalias', r'valores.*atípicos',
            r'estatísticas.*descritivas', r'resumo.*estatístico',
            r'distribuição.*normal', r'curva.*normal'
        ]
    
    def needs_chart(self, question: str) -> Tuple[bool, str]:
        """
        Detecta se a pergunta requer um gráfico (MELHORADO)
        
        Returns:
            Tuple[bool, str]: (precisa_grafico, tipo_grafico)
        """
        question_lower = question.lower()
        
        # Verifica padrões específicos primeiro
        for pattern in self.chart_patterns:
            if re.search(pattern, question_lower):
                return True, 'auto'
        
        # Verifica palavras-chave por categoria
        for chart_type, keywords in self.chart_keywords.items():
            for keyword in keywords:
                if keyword in question_lower:
                    return True, chart_type
        
        # Verifica perguntas que claramente pedem visualização
        visualization_indicators = [
            'mostre', 'mostrar', 'visualizar', 'visualize', 'gráfico', 'grafico', 
            'chart', 'plot', 'desenhe', 'crie', 'gere', 'como são', 'como estão',
            'quais são', 'onde estão', 'quando ocorrem', 'quanto representam'
        ]
        
        for indicator in visualization_indicators:
            if indicator in question_lower:
                # Verifica se a pergunta é sobre dados/estatísticas
                data_indicators = [
                    'dados', 'valores', 'números', 'estatísticas', 'variáveis', 
                    'colunas', 'registros', 'distribuição', 'correlação', 'tendência'
                ]
                for data_indicator in data_indicators:
                    if data_indicator in question_lower:
                        return True, "visualização_geral"
        
        # Verifica perguntas sobre comparações ou rankings
        comparison_indicators = [
            'maior', 'menor', 'melhor', 'pior', 'top', 'ranking', 'ordenar',
            'comparar', 'diferença', 'mais', 'menos', 'frequente', 'comum'
        ]
        
        for comp_indicator in comparison_indicators:
            if comp_indicator in question_lower:
                return True, "comparação"
        
        return False, None
    
    def extract_chart_requirements(self, question: str, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Extrai requisitos específicos para o gráfico baseado na pergunta e dados
        """
        question_lower = question.lower()
        requirements = {
            'chart_type': 'auto',
            'columns': [],
            'group_by': None,
            'aggregation': 'count',
            'time_column': None,
            'color_column': None,
            'size_column': None
        }
        
        # Identifica colunas mencionadas na pergunta
        for col in df.columns:
            if col.lower() in question_lower:
                requirements['columns'].append(col)
        
        # Detecta tipo de agregação
        if any(word in question_lower for word in ['soma', 'total', 'sum']):
            requirements['aggregation'] = 'sum'
        elif any(word in question_lower for word in ['média', 'media', 'average']):
            requirements['aggregation'] = 'mean'
        elif any(word in question_lower for word in ['máximo', 'maximo', 'max']):
            requirements['aggregation'] = 'max'
        elif any(word in question_lower for word in ['mínimo', 'minimo', 'min']):
            requirements['aggregation'] = 'min'
        
        # Detecta colunas de tempo
        time_keywords = ['data', 'ano', 'mês', 'mes', 'dia', 'tempo', 'período', 'periodo']
        for col in df.columns:
            if any(keyword in col.lower() for keyword in time_keywords):
                requirements['time_column'] = col
                break
        
        return requirements


class ChartGenerator:
    """Gera gráficos automaticamente baseado na pergunta e dados"""
    
    def __init__(self):
        self.detector = ChartDetector()
    
    def generate_chart(self, question: str, df: pd.DataFrame, requirements: Dict[str, Any] = None) -> Optional[go.Figure]:
        """
        Gera um gráfico baseado na pergunta e dados
        
        Args:
            question: Pergunta do usuário
            df: DataFrame com os dados
            requirements: Requisitos específicos do gráfico
            
        Returns:
            go.Figure: Gráfico gerado ou None se não for possível
        """
        if df.empty:
            return None
        
        if requirements is None:
            requirements = self.detector.extract_chart_requirements(question, df)
        
        chart_type = requirements.get('chart_type', 'auto')
        
        try:
            # Determina o tipo de gráfico automaticamente se necessário
            if chart_type == 'auto':
                chart_type = self._determine_chart_type(df, requirements)
            
            # Gera o gráfico baseado no tipo
            if chart_type == 'distribuicao':
                return self._create_distribution_chart(df, requirements)
            elif chart_type == 'correlacao':
                return self._create_correlation_chart(df, requirements)
            elif chart_type == 'tendencia':
                return self._create_trend_chart(df, requirements)
            elif chart_type == 'comparacao':
                return self._create_comparison_chart(df, requirements)
            elif chart_type == 'agrupamento':
                return self._create_clustering_chart(df, requirements)
            elif chart_type == 'ranking':
                return self._create_ranking_chart(df, requirements)
            elif chart_type == 'categoria':
                return self._create_categorical_chart(df, requirements)
            else:
                return self._create_default_chart(df, requirements)
                
        except Exception as e:
            st.error(f"Erro ao gerar gráfico: {str(e)}")
            return None
    
    def _determine_chart_type(self, df: pd.DataFrame, requirements: Dict[str, Any]) -> str:
        """Determina automaticamente o tipo de gráfico mais apropriado"""
        
        # Se há coluna de tempo, prioriza gráfico de tendência
        if requirements.get('time_column'):
            return 'tendencia'
        
        # Se há poucas colunas numéricas, usa distribuição
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) <= 2:
            return 'distribuicao'
        
        # Se há muitas colunas numéricas, usa correlação
        if len(numeric_cols) > 3:
            return 'correlacao'
        
        # Se há colunas categóricas, usa comparação
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(categorical_cols) > 0:
            return 'comparacao'
        
        return 'distribuicao'
    
    def _create_distribution_chart(self, df: pd.DataFrame, requirements: Dict[str, Any]) -> go.Figure:
        """Cria gráfico de distribuição (histograma)"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            return self._create_default_chart(df, requirements)
        
        # Usa a primeira coluna numérica ou a especificada
        col = requirements.get('columns', [numeric_cols[0]])[0] if requirements.get('columns') else numeric_cols[0]
        
        if col not in df.columns:
            col = numeric_cols[0]
        
        fig = px.histogram(df, x=col, title=f'Distribuição de {col}')
        fig.update_layout(
            xaxis_title=col,
            yaxis_title='Frequência',
            showlegend=False
        )
        return fig
    
    def _create_correlation_chart(self, df: pd.DataFrame, requirements: Dict[str, Any]) -> go.Figure:
        """Cria gráfico de correlação (heatmap ou scatter)"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return self._create_distribution_chart(df, requirements)
        
        # Limita a 10 colunas para não sobrecarregar
        numeric_cols = numeric_cols[:10]
        
        # Calcula matriz de correlação
        corr_matrix = df[numeric_cols].corr()
        
        fig = px.imshow(
            corr_matrix,
            title='Matriz de Correlação',
            color_continuous_scale='RdBu',
            aspect='auto'
        )
        
        fig.update_layout(
            xaxis_title='Variáveis',
            yaxis_title='Variáveis'
        )
        
        return fig
    
    def _create_trend_chart(self, df: pd.DataFrame, requirements: Dict[str, Any]) -> go.Figure:
        """Cria gráfico de tendência temporal"""
        time_col = requirements.get('time_column')
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if not time_col or time_col not in df.columns:
            # Se não há coluna de tempo, usa o índice
            time_col = df.index.name or 'index'
            df_plot = df.copy()
            df_plot[time_col] = range(len(df))
        else:
            df_plot = df.copy()
        
        if len(numeric_cols) == 0:
            return self._create_default_chart(df, requirements)
        
        # Usa até 3 colunas numéricas para não sobrecarregar
        plot_cols = numeric_cols[:3]
        
        fig = go.Figure()
        
        for col in plot_cols:
            fig.add_trace(go.Scatter(
                x=df_plot[time_col],
                y=df_plot[col],
                mode='lines+markers',
                name=col,
                line=dict(width=2)
            ))
        
        fig.update_layout(
            title='Evolução Temporal',
            xaxis_title=time_col,
            yaxis_title='Valor',
            hovermode='x unified'
        )
        
        return fig
    
    def _create_comparison_chart(self, df: pd.DataFrame, requirements: Dict[str, Any]) -> go.Figure:
        """Cria gráfico de comparação (bar chart)"""
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(categorical_cols) == 0 or len(numeric_cols) == 0:
            return self._create_default_chart(df, requirements)
        
        # Usa a primeira coluna categórica e numérica
        cat_col = categorical_cols[0]
        num_col = numeric_cols[0]
        
        # Agrupa e agrega
        aggregation = requirements.get('aggregation', 'count')
        if aggregation == 'count':
            grouped = df.groupby(cat_col).size().reset_index(name='count')
            y_col = 'count'
        else:
            grouped = df.groupby(cat_col)[num_col].agg(aggregation).reset_index()
            y_col = num_col
        
        fig = px.bar(
            grouped,
            x=cat_col,
            y=y_col,
            title=f'Comparação por {cat_col}'
        )
        
        fig.update_layout(
            xaxis_title=cat_col,
            yaxis_title=y_col,
            xaxis_tickangle=-45
        )
        
        return fig
    
    def _create_clustering_chart(self, df: pd.DataFrame, requirements: Dict[str, Any]) -> go.Figure:
        """Cria gráfico de agrupamento (clusters)"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return self._create_distribution_chart(df, requirements)
        
        # Usa até 3 colunas numéricas para clustering
        feature_cols = numeric_cols[:3]
        df_cluster = df[feature_cols].dropna()
        
        if len(df_cluster) < 10:
            return self._create_correlation_chart(df, requirements)
        
        # Aplica K-means
        scaler = StandardScaler()
        df_scaled = scaler.fit_transform(df_cluster)
        
        # Determina número de clusters (2-5)
        n_clusters = min(5, max(2, len(df_cluster) // 20))
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(df_scaled)
        
        df_cluster = df_cluster.copy()
        df_cluster['cluster'] = clusters
        
        # Cria gráfico 2D ou 3D
        if len(feature_cols) == 2:
            fig = px.scatter(
                df_cluster,
                x=feature_cols[0],
                y=feature_cols[1],
                color='cluster',
                title='Agrupamento dos Dados (Clusters)'
            )
        else:
            fig = px.scatter_3d(
                df_cluster,
                x=feature_cols[0],
                y=feature_cols[1],
                z=feature_cols[2],
                color='cluster',
                title='Agrupamento dos Dados (Clusters 3D)'
            )
        
        return fig
    
    def _create_ranking_chart(self, df: pd.DataFrame, requirements: Dict[str, Any]) -> go.Figure:
        """Cria gráfico de ranking (top N)"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        
        if len(numeric_cols) == 0:
            return self._create_default_chart(df, requirements)
        
        # Se há coluna categórica, faz ranking por categoria
        if len(categorical_cols) > 0:
            cat_col = categorical_cols[0]
            num_col = numeric_cols[0]
            
            aggregation = requirements.get('aggregation', 'mean')
            ranked = df.groupby(cat_col)[num_col].agg(aggregation).sort_values(ascending=False).head(10)
            
            fig = px.bar(
                x=ranked.values,
                y=ranked.index,
                orientation='h',
                title=f'Top 10 - {cat_col} por {num_col}'
            )
        else:
            # Ranking direto dos valores
            col = numeric_cols[0]
            ranked = df[col].sort_values(ascending=False).head(10)
            
            fig = px.bar(
                x=ranked.values,
                y=ranked.index,
                orientation='h',
                title=f'Top 10 - {col}'
            )
        
        fig.update_layout(
            xaxis_title='Valor',
            yaxis_title='Ranking'
        )
        
        return fig
    
    def _create_categorical_chart(self, df: pd.DataFrame, requirements: Dict[str, Any]) -> go.Figure:
        """Cria gráfico categórico (pie chart)"""
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        
        if len(categorical_cols) == 0:
            return self._create_default_chart(df, requirements)
        
        col = categorical_cols[0]
        value_counts = df[col].value_counts().head(10)
        
        fig = px.pie(
            values=value_counts.values,
            names=value_counts.index,
            title=f'Distribuição de {col}'
        )
        
        return fig
    
    def _create_default_chart(self, df: pd.DataFrame, requirements: Dict[str, Any]) -> go.Figure:
        """Cria gráfico padrão quando não é possível determinar o tipo específico"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) > 0:
            # Usa a primeira coluna numérica
            col = numeric_cols[0]
            fig = px.histogram(df, x=col, title=f'Distribuição de {col}')
        else:
            # Se não há colunas numéricas, mostra contagem de linhas
            fig = go.Figure()
            fig.add_annotation(
                text=f"Dataset com {len(df)} registros e {len(df.columns)} colunas",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(
                title="Resumo dos Dados",
                xaxis=dict(visible=False),
                yaxis=dict(visible=False)
            )
        
        return fig


def create_pygwalker_interface(df: pd.DataFrame) -> None:
    """Cria interface do PyGWalker para exploração visual independente"""
    try:
        import pygwalker as pyg
        
        st.markdown("### 🔍 **Explorador Visual Interativo (PyGWalker)**")
        st.markdown("""
        **Funcionalidades:**
        - 📊 **Drag & Drop**: Arraste colunas para criar visualizações
        - 🔄 **Filtros Dinâmicos**: Filtre dados em tempo real
        - 📈 **Múltiplos Gráficos**: Crie dashboards interativos
        - 💾 **Exportar**: Salve gráficos e dados filtrados
        """)
        
        # Configurações do PyGWalker com tratamento de erros
        try:
            pyg.walk(
                df,
                env='Streamlit',
                spec_io_mode="rw",  # Usar spec_io_mode em vez de debug
                dark="light",  # Tema claro
                show_cloud_tool=False,  # Desabilitar ferramentas de nuvem
                use_kernel_calc=True,  # Usar cálculo do kernel
                kernel_computation=True  # Habilitar computação do kernel
            )
        except Exception as e:
            st.warning(f"⚠️ Erro ao carregar PyGWalker: {str(e)}")
            st.info("💡 Tentando carregar com configurações alternativas...")
            
            # Tentar com configurações mais simples
            try:
                pyg.walk(df, env='Streamlit')
            except Exception as e2:
                st.error(f"❌ Não foi possível carregar o PyGWalker: {str(e2)}")
                st.info("💡 Verifique se o PyGWalker está instalado: `pip install pygwalker`")
        
    except ImportError:
        st.error("PyGWalker não está instalado. Execute: pip install pygwalker")
    except Exception as e:
        st.error(f"Erro ao carregar PyGWalker: {str(e)}")
        st.info("Tentando carregar com configuração simplificada...")
        
        # Fallback: mostra informações básicas do dataset
        st.markdown("### 📊 **Informações do Dataset**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Registros", len(df))
        with col2:
            st.metric("Total de Colunas", len(df.columns))
        with col3:
            numeric_cols = len(df.select_dtypes(include=[np.number]).columns)
            st.metric("Colunas Numéricas", numeric_cols)
        
        # Mostra amostra dos dados
        st.markdown("### 📋 **Amostra dos Dados**")
        st.dataframe(df.head(10), use_container_width=True)


# Função principal para integração com o chat
def generate_chart_for_question(question: str, df: pd.DataFrame) -> Optional[go.Figure]:
    """
    Função principal para gerar gráficos baseados em perguntas
    
    Args:
        question: Pergunta do usuário
        df: DataFrame com os dados
        
    Returns:
        go.Figure: Gráfico gerado ou None
    """
    detector = ChartDetector()
    generator = ChartGenerator()
    
    # Verifica se a pergunta requer gráfico
    needs_chart, chart_type = detector.needs_chart(question)
    
    if not needs_chart:
        return None
    
    # Gera o gráfico
    requirements = detector.extract_chart_requirements(question, df)
    requirements['chart_type'] = chart_type
    
    return generator.generate_chart(question, df, requirements)
