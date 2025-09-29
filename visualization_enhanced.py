# Módulo de Visualização Avançada com Matplotlib e Seaborn
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from typing import Dict, List, Tuple, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# Configurar estilo dos gráficos
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class EnhancedVisualizer:
    """Classe para visualizações avançadas com matplotlib e seaborn"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
    def create_comprehensive_analysis_plots(self) -> Dict[str, Any]:
        """Cria conjunto completo de visualizações para análise"""
        plots = {}
        
        try:
            # 1. Distribuição de variáveis numéricas
            if self.numeric_cols:
                plots['distributions'] = self._create_distribution_plots()
            
            # 2. Matriz de correlação
            if len(self.numeric_cols) > 1:
                plots['correlation'] = self._create_correlation_matrix()
            
            # 3. Análise de outliers
            if self.numeric_cols:
                plots['outliers'] = self._create_outlier_analysis()
            
            # 4. Análise temporal (se houver coluna de tempo)
            time_cols = [col for col in self.df.columns if 'time' in col.lower() or 'date' in col.lower()]
            if time_cols:
                plots['temporal'] = self._create_temporal_analysis(time_cols[0])
            
            # 5. Análise de classes (se houver coluna categórica)
            if self.categorical_cols:
                plots['categorical'] = self._create_categorical_analysis()
            
            return plots
            
        except Exception as e:
            st.error(f"Erro ao criar visualizações: {str(e)}")
            return {}
    
    def _create_distribution_plots(self) -> go.Figure:
        """Cria gráficos de distribuição para variáveis numéricas"""
        try:
            # Selecionar até 6 colunas numéricas para visualizar
            cols_to_plot = self.numeric_cols[:6]
            
            fig = make_subplots(
                rows=2, cols=3,
                subplot_titles=cols_to_plot,
                specs=[[{"secondary_y": False}] * 3] * 2
            )
            
            for i, col in enumerate(cols_to_plot):
                row = (i // 3) + 1
                col_pos = (i % 3) + 1
                
                # Histograma
                fig.add_trace(
                    go.Histogram(
                        x=self.df[col],
                        name=col,
                        nbinsx=30,
                        opacity=0.7
                    ),
                    row=row, col=col_pos
                )
            
            fig.update_layout(
                title="Distribuições das Variáveis Numéricas",
                height=600,
                showlegend=False
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Erro ao criar gráficos de distribuição: {str(e)}")
            return go.Figure()
    
    def _create_correlation_matrix(self) -> go.Figure:
        """Cria matriz de correlação"""
        try:
            # Calcular correlação
            corr_matrix = self.df[self.numeric_cols].corr()
            
            # Criar heatmap
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdBu',
                zmid=0,
                text=np.round(corr_matrix.values, 2),
                texttemplate="%{text}",
                textfont={"size": 10},
                hoverongaps=False
            ))
            
            fig.update_layout(
                title="Matriz de Correlação",
                height=600,
                xaxis_title="Variáveis",
                yaxis_title="Variáveis"
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Erro ao criar matriz de correlação: {str(e)}")
            return go.Figure()
    
    def _create_outlier_analysis(self) -> go.Figure:
        """Cria análise de outliers com box plots"""
        try:
            # Selecionar até 6 colunas para box plots
            cols_to_plot = self.numeric_cols[:6]
            
            fig = go.Figure()
            
            for col in cols_to_plot:
                fig.add_trace(go.Box(
                    y=self.df[col],
                    name=col,
                    boxpoints='outliers',
                    jitter=0.3,
                    pointpos=-1.8
                ))
            
            fig.update_layout(
                title="Análise de Outliers (Box Plots)",
                yaxis_title="Valores",
                height=500
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Erro ao criar análise de outliers: {str(e)}")
            return go.Figure()
    
    def _create_temporal_analysis(self, time_col: str) -> go.Figure:
        """Cria análise temporal"""
        try:
            # Converter para datetime se necessário
            if not pd.api.types.is_datetime64_any_dtype(self.df[time_col]):
                self.df[time_col] = pd.to_datetime(self.df[time_col], errors='coerce')
            
            # Agrupar por período (dia, hora, etc.)
            if len(self.df) > 1000:
                # Para datasets grandes, agrupar por hora
                self.df['period'] = self.df[time_col].dt.floor('H')
            else:
                # Para datasets menores, agrupar por minuto
                self.df['period'] = self.df[time_col].dt.floor('T')
            
            # Contar ocorrências por período
            temporal_counts = self.df.groupby('period').size().reset_index(name='count')
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=temporal_counts['period'],
                y=temporal_counts['count'],
                mode='lines+markers',
                name='Ocorrências',
                line=dict(width=2)
            ))
            
            fig.update_layout(
                title=f"Análise Temporal - {time_col}",
                xaxis_title="Tempo",
                yaxis_title="Número de Ocorrências",
                height=400
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Erro ao criar análise temporal: {str(e)}")
            return go.Figure()
    
    def _create_categorical_analysis(self) -> go.Figure:
        """Cria análise de variáveis categóricas"""
        try:
            # Selecionar primeira coluna categórica
            cat_col = self.categorical_cols[0]
            
            # Contar valores
            value_counts = self.df[cat_col].value_counts().head(10)
            
            fig = go.Figure(data=[
                go.Bar(
                    x=value_counts.index,
                    y=value_counts.values,
                    marker_color='lightblue'
                )
            ])
            
            fig.update_layout(
                title=f"Distribuição de {cat_col}",
                xaxis_title=cat_col,
                yaxis_title="Frequência",
                height=400
            )
            
            return fig
            
        except Exception as e:
            st.error(f"Erro ao criar análise categórica: {str(e)}")
            return go.Figure()
    
    def create_summary_statistics(self) -> Dict[str, Any]:
        """Cria estatísticas resumidas"""
        try:
            stats = {}
            
            # Estatísticas básicas
            stats['basic'] = {
                'total_records': len(self.df),
                'total_columns': len(self.df.columns),
                'numeric_columns': len(self.numeric_cols),
                'categorical_columns': len(self.categorical_cols),
                'missing_values': self.df.isnull().sum().sum(),
                'duplicate_rows': self.df.duplicated().sum()
            }
            
            # Estatísticas por coluna numérica
            if self.numeric_cols:
                stats['numeric_summary'] = self.df[self.numeric_cols].describe().to_dict()
            
            # Estatísticas por coluna categórica
            if self.categorical_cols:
                stats['categorical_summary'] = {}
                for col in self.categorical_cols:
                    stats['categorical_summary'][col] = {
                        'unique_values': self.df[col].nunique(),
                        'most_common': self.df[col].mode().iloc[0] if len(self.df[col].mode()) > 0 else None,
                        'missing_values': self.df[col].isnull().sum()
                    }
            
            return stats
            
        except Exception as e:
            st.error(f"Erro ao criar estatísticas: {str(e)}")
            return {}

def show_enhanced_visualizations(df: pd.DataFrame):
    """Função para mostrar visualizações avançadas no Streamlit"""
    try:
        visualizer = EnhancedVisualizer(df)
        
        st.markdown("### 📊 Visualizações Avançadas com Matplotlib e Seaborn")
        
        # Criar visualizações
        plots = visualizer.create_comprehensive_analysis_plots()
        
        if plots:
            # Mostrar cada tipo de visualização
            if 'distributions' in plots:
                st.markdown("#### 📈 Distribuições das Variáveis Numéricas")
                st.plotly_chart(plots['distributions'], use_container_width=True)
            
            if 'correlation' in plots:
                st.markdown("#### 🔗 Matriz de Correlação")
                st.plotly_chart(plots['correlation'], use_container_width=True)
            
            if 'outliers' in plots:
                st.markdown("#### ⚠️ Análise de Outliers")
                st.plotly_chart(plots['outliers'], use_container_width=True)
            
            if 'temporal' in plots:
                st.markdown("#### 📅 Análise Temporal")
                st.plotly_chart(plots['temporal'], use_container_width=True)
            
            if 'categorical' in plots:
                st.markdown("#### 📋 Análise Categórica")
                st.plotly_chart(plots['categorical'], use_container_width=True)
        
        # Mostrar estatísticas resumidas
        stats = visualizer.create_summary_statistics()
        if stats:
            st.markdown("#### 📊 Estatísticas Resumidas")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📊 Registros", f"{stats['basic']['total_records']:,}")
            
            with col2:
                st.metric("📋 Colunas", stats['basic']['total_columns'])
            
            with col3:
                st.metric("⚠️ Valores Faltantes", f"{stats['basic']['missing_values']:,}")
            
            with col4:
                st.metric("🔄 Duplicatas", f"{stats['basic']['duplicate_rows']:,}")
        
    except Exception as e:
        st.error(f"Erro ao criar visualizações: {str(e)}")

def generate_visualization_insights(df: pd.DataFrame) -> str:
    """Gera insights baseados nas visualizações"""
    try:
        visualizer = EnhancedVisualizer(df)
        stats = visualizer.create_summary_statistics()
        
        insights = []
        
        # Insights básicos
        insights.append(f"Dataset com {stats['basic']['total_records']:,} registros e {stats['basic']['total_columns']} colunas")
        
        # Insights sobre qualidade dos dados
        missing_pct = (stats['basic']['missing_values'] / (stats['basic']['total_records'] * stats['basic']['total_columns'])) * 100
        insights.append(f"Qualidade dos dados: {100-missing_pct:.1f}% (valores faltantes: {missing_pct:.1f}%)")
        
        # Insights sobre tipos de dados
        insights.append(f"Variáveis numéricas: {stats['basic']['numeric_columns']}, categóricas: {stats['basic']['categorical_columns']}")
        
        # Insights sobre duplicatas
        if stats['basic']['duplicate_rows'] > 0:
            insights.append(f"⚠️ {stats['basic']['duplicate_rows']} registros duplicados encontrados")
        
        # Insights sobre correlações (se houver variáveis numéricas)
        if len(visualizer.numeric_cols) > 1:
            corr_matrix = df[visualizer.numeric_cols].corr()
            high_corr = corr_matrix.abs().stack().sort_values(ascending=False)
            high_corr = high_corr[high_corr < 1.0].head(3)
            
            if len(high_corr) > 0:
                insights.append(f"Correlações mais altas: {', '.join([f'{pair[0][0]}-{pair[0][1]} ({pair[1]:.2f})' for pair in high_corr.items()])}")
        
        return "\n".join(insights)
        
    except Exception as e:
        return f"Erro ao gerar insights: {str(e)}"
