#!/bin/bash
# ============================================================
# GeoCalor Dash — Script de setup e execução local
# Desenvolvimento: Diego Ricardo Xavier | OCS/ICICT/Fiocruz
# ============================================================

set -e

REPO="Diegoricardox/geocalor-dash"
DATA_URL="https://github.com/${REPO}/releases/download/v1.0/temp.csv.gz"
DATA_FILE="data/temp.csv.gz"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║       GeoCalor Dash — Setup & Run        ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# 1. Verificar Python 3
if ! command -v python3 &>/dev/null; then
    echo "❌ Python 3 não encontrado. Instale via: brew install python"
    exit 1
fi
echo "✅ Python 3: $(python3 --version)"

# 2. Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
fi

# 3. Ativar ambiente virtual
source venv/bin/activate
echo "✅ Ambiente virtual ativado"

# 4. Instalar dependências
echo "📦 Instalando dependências..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✅ Dependências instaladas"

# 5. Baixar dados se não existirem
mkdir -p data
if [ ! -f "$DATA_FILE" ] || [ $(wc -c < "$DATA_FILE") -lt 1000 ]; then
    echo "⬇️  Baixando dados climáticos (7.5 MB)..."
    curl -L --progress-bar "$DATA_URL" -o "$DATA_FILE"
    echo "✅ Dados baixados: $DATA_FILE"
else
    echo "✅ Dados já disponíveis: $DATA_FILE ($(du -sh $DATA_FILE | cut -f1))"
fi

# 6. Iniciar o app
echo ""
echo "🚀 Iniciando GeoCalor Dash..."
echo "   Acesse: http://localhost:8050"
echo "   Para encerrar: Ctrl+C"
echo ""
python3 app.py
