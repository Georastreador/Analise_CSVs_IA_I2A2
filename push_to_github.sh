#!/bin/bash

# Script para fazer push do projeto CSV Analysis AI para o GitHub
# Execute este script quando tiver conectividade com a internet

echo "🚀 Fazendo push do CSV Analysis AI para o GitHub..."
echo "📁 Repositório: https://github.com/Georastreador/Analise_CSVs_IA_I2A2.git"
echo ""

# Verificar se estamos no diretório correto
if [ ! -f "csv_analysis_app_v2.py" ]; then
    echo "❌ Erro: Execute este script no diretório do projeto"
    exit 1
fi

# Verificar status do git
echo "📊 Verificando status do Git..."
git status

echo ""
echo "🔄 Fazendo push para o GitHub..."

# Tentar fazer push
if git push -u origin main; then
    echo ""
    echo "✅ Push realizado com sucesso!"
    echo "🌐 Seu repositório está disponível em:"
    echo "   https://github.com/Georastreador/Analise_CSVs_IA_I2A2"
    echo ""
    echo "📋 Próximos passos:"
    echo "1. Acesse o repositório no GitHub"
    echo "2. Configure as GitHub Actions (se necessário)"
    echo "3. Adicione uma descrição ao repositório"
    echo "4. Configure os secrets para APIs (se necessário)"
    echo "5. Faça deploy no Streamlit Cloud ou outra plataforma"
else
    echo ""
    echo "❌ Erro ao fazer push. Possíveis causas:"
    echo "   - Problema de conectividade"
    echo "   - Credenciais não configuradas"
    echo "   - Repositório não existe ou não tem permissão"
    echo ""
    echo "🔧 Soluções:"
    echo "1. Verifique sua conexão com a internet"
    echo "2. Configure suas credenciais Git:"
    echo "   git config --global user.name 'Seu Nome'"
    echo "   git config --global user.email 'seu@email.com'"
    echo "3. Verifique se o repositório existe no GitHub"
    echo "4. Tente novamente: git push -u origin main"
fi

echo ""
echo "📚 Para mais informações, consulte:"
echo "   - README.md - Documentação do projeto"
echo "   - DEPLOY.md - Guia de deploy"
echo "   - CONTRIBUTING.md - Guia de contribuição"
