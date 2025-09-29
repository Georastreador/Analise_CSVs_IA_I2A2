import os
import json
import hashlib
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import streamlit as st

class CacheSystem:
    """Sistema de cache inteligente para análises e dados"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.memory_cache: Dict[str, Any] = {}
        self.cache_metadata: Dict[str, Dict[str, Any]] = {}
        self.max_memory_items = 50
        self.cache_expiry_hours = 24
        self._ensure_cache_dir()
        self._load_metadata()
    
    def _ensure_cache_dir(self):
        """Garante que o diretório de cache existe"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _load_metadata(self):
        """Carrega metadados do cache"""
        metadata_file = os.path.join(self.cache_dir, "cache_metadata.json")
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    self.cache_metadata = json.load(f)
            except:
                self.cache_metadata = {}
    
    def _save_metadata(self):
        """Salva metadados do cache"""
        metadata_file = os.path.join(self.cache_dir, "cache_metadata.json")
        try:
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_metadata, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def _generate_cache_key(self, filename: str, analysis_type: str) -> str:
        """Gera chave única para o cache"""
        content = f"{filename}_{analysis_type}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Verifica se o cache ainda é válido"""
        if cache_key not in self.cache_metadata:
            return False
        
        metadata = self.cache_metadata[cache_key]
        created_time = datetime.fromisoformat(metadata.get('created_at', ''))
        expiry_time = created_time + timedelta(hours=self.cache_expiry_hours)
        
        return datetime.now() < expiry_time
    
    def _cleanup_expired_cache(self):
        """Remove cache expirado"""
        expired_keys = []
        for cache_key, metadata in self.cache_metadata.items():
            if not self._is_cache_valid(cache_key):
                expired_keys.append(cache_key)
        
        for cache_key in expired_keys:
            self._remove_cache_item(cache_key)
    
    def _remove_cache_item(self, cache_key: str):
        """Remove item específico do cache"""
        # Remover do cache em memória
        if cache_key in self.memory_cache:
            del self.memory_cache[cache_key]
        
        # Remover arquivo do disco
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        if os.path.exists(cache_file):
            try:
                os.remove(cache_file)
            except:
                pass
        
        # Remover metadados
        if cache_key in self.cache_metadata:
            del self.cache_metadata[cache_key]
        
        self._save_metadata()
    
    def _manage_memory_cache(self):
        """Gerencia o cache em memória para evitar uso excessivo"""
        if len(self.memory_cache) > self.max_memory_items:
            # Remover itens mais antigos
            sorted_items = sorted(
                self.memory_cache.items(),
                key=lambda x: self.cache_metadata.get(x[0], {}).get('last_accessed', ''),
                reverse=True
            )
            
            # Manter apenas os itens mais recentes
            self.memory_cache = dict(sorted_items[:self.max_memory_items])
    
    def get(self, filename: str, analysis_type: str) -> Optional[Any]:
        """Recupera item do cache"""
        cache_key = self._generate_cache_key(filename, analysis_type)
        
        # Verificar se cache é válido
        if not self._is_cache_valid(cache_key):
            self._remove_cache_item(cache_key)
            return None
        
        # Tentar cache em memória primeiro
        if cache_key in self.memory_cache:
            # Atualizar último acesso
            if cache_key in self.cache_metadata:
                self.cache_metadata[cache_key]['last_accessed'] = datetime.now().isoformat()
                self._save_metadata()
            return self.memory_cache[cache_key]
        
        # Tentar carregar do disco
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Adicionar ao cache em memória
                self.memory_cache[cache_key] = data
                self._manage_memory_cache()
                
                # Atualizar último acesso
                if cache_key in self.cache_metadata:
                    self.cache_metadata[cache_key]['last_accessed'] = datetime.now().isoformat()
                    self._save_metadata()
                
                return data
            except:
                return None
        
        return None
    
    def set(self, filename: str, analysis_type: str, data: Any) -> bool:
        """Salva item no cache"""
        try:
            cache_key = self._generate_cache_key(filename, analysis_type)
            
            # Salvar no cache em memória
            self.memory_cache[cache_key] = data
            self._manage_memory_cache()
            
            # Salvar no disco
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Atualizar metadados
            self.cache_metadata[cache_key] = {
                'filename': filename,
                'analysis_type': analysis_type,
                'created_at': datetime.now().isoformat(),
                'last_accessed': datetime.now().isoformat(),
                'size': len(str(data))
            }
            self._save_metadata()
            
            return True
            
        except Exception as e:
            st.error(f"❌ Erro ao salvar no cache: {str(e)}")
            return False
    
    def invalidate(self, filename: str, analysis_type: str = None):
        """Invalida cache para um arquivo específico"""
        if analysis_type:
            # Invalidar análise específica
            cache_key = self._generate_cache_key(filename, analysis_type)
            self._remove_cache_item(cache_key)
        else:
            # Invalidar todas as análises do arquivo
            keys_to_remove = []
            for cache_key, metadata in self.cache_metadata.items():
                if metadata.get('filename') == filename:
                    keys_to_remove.append(cache_key)
            
            for cache_key in keys_to_remove:
                self._remove_cache_item(cache_key)
    
    def clear_all(self):
        """Limpa todo o cache"""
        # Limpar cache em memória
        self.memory_cache.clear()
        
        # Limpar arquivos do disco
        try:
            for file in os.listdir(self.cache_dir):
                if file.endswith('.json') and file != 'cache_metadata.json':
                    os.remove(os.path.join(self.cache_dir, file))
        except:
            pass
        
        # Limpar metadados
        self.cache_metadata.clear()
        self._save_metadata()
        
        st.success("✅ Cache limpo com sucesso!")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        self._cleanup_expired_cache()
        
        total_items = len(self.cache_metadata)
        memory_items = len(self.memory_cache)
        total_size = sum(metadata.get('size', 0) for metadata in self.cache_metadata.values())
        
        # Agrupar por tipo de análise
        analysis_types = {}
        for metadata in self.cache_metadata.values():
            analysis_type = metadata.get('analysis_type', 'unknown')
            if analysis_type not in analysis_types:
                analysis_types[analysis_type] = 0
            analysis_types[analysis_type] += 1
        
        return {
            'total_items': total_items,
            'memory_items': memory_items,
            'total_size': total_size,
            'analysis_types': analysis_types,
            'cache_dir': self.cache_dir
        }
    
    def show_cache_info(self):
        """Mostra informações do cache na interface"""
        stats = self.get_cache_stats()
        
        st.markdown("### 📊 Informações do Cache")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Itens", stats['total_items'])
        
        with col2:
            st.metric("Em Memória", stats['memory_items'])
        
        with col3:
            st.metric("Tamanho Total", f"{stats['total_size']:,} bytes")
        
        if stats['analysis_types']:
            st.markdown("#### Tipos de Análise em Cache:")
            for analysis_type, count in stats['analysis_types'].items():
                st.write(f"• **{analysis_type}**: {count} itens")
        
        # Botões de gerenciamento
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🧹 Limpar Cache", use_container_width=True):
                self.clear_all()
        
        with col2:
            if st.button("🔄 Atualizar Estatísticas", use_container_width=True):
                st.rerun()

# Instância global do CacheSystem
cache_system = CacheSystem()
