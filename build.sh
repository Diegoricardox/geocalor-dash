#!/bin/bash
# ============================================================
# GeoCalor Dash — Build script para deploy no Render
# Baixa os dados climáticos da Release do GitHub
# ============================================================

set -e

echo "📦 Instalando dependências Python..."
pip install -r requirements.txt

echo "📊 Baixando dados climáticos da Release v1.0..."
mkdir -p data

# Baixar temp.csv.gz da Release pública do GitHub
curl -L \
  "https://github.com/Diegoricardox/geocalor-dash/releases/download/v1.0/temp.csv.gz" \
  -o data/temp.csv.gz \
  --progress-bar

# Validar o arquivo
if python3 -c "import gzip; gzip.open('data/temp.csv.gz').read(10)" 2>/dev/null; then
    echo "✅ Dados validados: data/temp.csv.gz"
else
    echo "❌ Falha ao baixar dados. Verifique a Release v1.0."
    exit 1
fi

echo "✅ Build concluído!"
