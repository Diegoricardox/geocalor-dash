#!/bin/bash
# ============================================================
# GeoCalor Dash — Script de setup e execução local
# Desenvolvimento: Diego Ricardo Xavier | OCS/ICICT/Fiocruz
# ============================================================

REPO="Diegoricardox/geocalor-dash"
DATA_FILE="data/temp.csv.gz"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║       GeoCalor Dash — Setup & Run        ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# 0. Atualizar código do repositório (git pull)
if git rev-parse --is-inside-work-tree &>/dev/null; then
    echo "🔄 Atualizando código do repositório..."
    git config pull.rebase false
    git pull origin main --allow-unrelated-histories 2>&1 | tail -3
    echo "✅ Código atualizado"
else
    echo "⚠️  Não é um repositório git — pulando git pull"
fi
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

# 4. Instalar/atualizar dependências
echo "📦 Verificando dependências..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✅ Dependências OK"

# 5. Baixar dados se não existirem ou estiverem corrompidos
mkdir -p data
NEED_DOWNLOAD=false
if [ ! -f "$DATA_FILE" ]; then
    NEED_DOWNLOAD=true
else
    # Verificar se é um gzip válido
    if ! python3 -c "import gzip; gzip.open('$DATA_FILE').read(10)" 2>/dev/null; then
        echo "⚠️  Arquivo de dados corrompido — baixando novamente..."
        rm -f "$DATA_FILE"
        NEED_DOWNLOAD=true
    fi
fi

if [ "$NEED_DOWNLOAD" = true ]; then
    echo "⬇️  Baixando dados climáticos (7.5 MB)..."

    # Tentar com gh CLI (autenticado — funciona com repositório privado)
    if command -v gh &>/dev/null && gh auth status &>/dev/null 2>&1; then
        echo "   Usando gh CLI (autenticado)..."
        gh release download v1.0 \
            --repo "$REPO" \
            --pattern "temp.csv.gz" \
            --dir data \
            --clobber
    else
        echo ""
        echo "⚠️  gh CLI não encontrado ou não autenticado."
        echo "   Para baixar os dados, você tem duas opções:"
        echo ""
        echo "   OPÇÃO A — Autenticar o gh CLI (recomendado):"
        echo "     brew install gh && gh auth login"
        echo "     Depois rode: bash run.sh"
        echo ""
        echo "   OPÇÃO B — Baixar manualmente:"
        echo "     1. Acesse: https://github.com/$REPO/releases/tag/v1.0"
        echo "     2. Baixe o arquivo temp.csv.gz"
        echo "     3. Mova para: $(pwd)/data/temp.csv.gz"
        echo "     4. Rode: bash run.sh"
        echo ""
        exit 1
    fi

    # Validar download
    if python3 -c "import gzip; gzip.open('$DATA_FILE').read(10)" 2>/dev/null; then
        echo "✅ Dados baixados e validados: $DATA_FILE"
    else
        echo "❌ Falha ao baixar os dados. Tente a OPÇÃO B acima."
        exit 1
    fi
else
    echo "✅ Dados disponíveis: $DATA_FILE ($(du -sh $DATA_FILE | cut -f1))"
fi

# 6. Iniciar o app
echo ""
echo "🚀 Iniciando GeoCalor Dash..."
echo "   Acesse: http://localhost:8050"
echo "   Para encerrar: Ctrl+C"
echo ""
python3 app.py
