#!/bin/bash
# ============================================================
# GeoCalor Dash — Script de atualização (código + dados)
# Usa GitHub CLI (gh) para autenticação segura com repos privados
# Desenvolvimento: Diego Ricardo Xavier | OCS/ICICT/Fiocruz
# ============================================================

REPO="Diegoricardox/geocalor-dash"
DATA_FILE="data/temp.csv.gz"
DATA_RELEASE="v1.0"

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║     GeoCalor Dash — Atualização          ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── Verificar gh CLI ──────────────────────────────────────────
if ! command -v gh &>/dev/null; then
    echo "❌ GitHub CLI (gh) não encontrado."
    echo ""
    echo "   Instale com:"
    echo "     macOS:  brew install gh"
    echo "     Linux:  sudo apt install gh  (ou snap install gh)"
    echo ""
    echo "   Após instalar, autentique:"
    echo "     gh auth login"
    echo ""
    exit 1
fi

# ── Verificar autenticação ────────────────────────────────────
if ! gh auth status &>/dev/null 2>&1; then
    echo "❌ GitHub CLI não autenticado."
    echo ""
    echo "   Execute:"
    echo "     gh auth login"
    echo ""
    echo "   Escolha:"
    echo "     - GitHub.com"
    echo "     - HTTPS"
    echo "     - Login with a web browser (ou Personal Access Token)"
    echo ""
    exit 1
fi

echo "✅ GitHub CLI autenticado como: $(gh api user --jq '.login' 2>/dev/null || echo 'usuário autenticado')"
echo ""

# ── Atualizar código via gh ───────────────────────────────────
echo "🔄 Atualizando código do repositório..."

if git rev-parse --is-inside-work-tree &>/dev/null; then
    # Configurar remote para usar gh como helper de credenciais
    REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "")

    if [ -n "$REMOTE_URL" ]; then
        # Usar gh para fazer o pull autenticado
        # gh sync usa a autenticação do gh CLI, evitando problemas com HTTPS privado
        if gh repo sync --source "$REPO" --branch main 2>/dev/null; then
            echo "✅ Código atualizado via gh repo sync"
        else
            # Fallback: configurar credencial via gh e fazer git pull
            echo "   Tentando git pull com credenciais gh..."
            # gh auth setup-git configura o git para usar gh como credential helper
            gh auth setup-git 2>/dev/null || true
            git pull origin main 2>&1 | tail -5
            echo "✅ Código atualizado via git pull"
        fi
    else
        echo "⚠️  Remote 'origin' não configurado — pulando atualização de código"
    fi
else
    echo "⚠️  Não é um repositório git — pulando atualização de código"
    echo "   Para clonar o repositório:"
    echo "     gh repo clone $REPO"
    echo ""
fi

echo ""

# ── Atualizar dados da Release ────────────────────────────────
echo "📊 Verificando dados climáticos..."
mkdir -p data

NEED_DOWNLOAD=false

if [ ! -f "$DATA_FILE" ]; then
    echo "   Arquivo de dados não encontrado — baixando..."
    NEED_DOWNLOAD=true
else
    # Verificar se é um gzip válido
    if ! python3 -c "import gzip; gzip.open('$DATA_FILE').read(10)" 2>/dev/null; then
        echo "⚠️  Arquivo corrompido — baixando novamente..."
        rm -f "$DATA_FILE"
        NEED_DOWNLOAD=true
    else
        TAMANHO=$(du -sh "$DATA_FILE" | cut -f1)
        echo "✅ Dados OK: $DATA_FILE ($TAMANHO)"
    fi
fi

if [ "$NEED_DOWNLOAD" = true ]; then
    echo "⬇️  Baixando dados climáticos da Release $DATA_RELEASE (~7.5 MB)..."
    if gh release download "$DATA_RELEASE" \
        --repo "$REPO" \
        --pattern "temp.csv.gz" \
        --dir data \
        --clobber; then
        if python3 -c "import gzip; gzip.open('$DATA_FILE').read(10)" 2>/dev/null; then
            echo "✅ Dados baixados e validados: $DATA_FILE"
        else
            echo "❌ Arquivo baixado está corrompido. Tente novamente."
            exit 1
        fi
    else
        echo "❌ Falha ao baixar dados via gh CLI."
        echo ""
        echo "   Alternativa manual:"
        echo "     1. Acesse: https://github.com/$REPO/releases/tag/$DATA_RELEASE"
        echo "     2. Baixe: temp.csv.gz"
        echo "     3. Mova para: $(pwd)/data/temp.csv.gz"
        exit 1
    fi
fi

echo ""

# ── Verificar se o app precisa ser reiniciado ─────────────────
echo "ℹ️  Atualização concluída!"
echo ""
echo "   Se o app já estiver rodando, reinicie-o para aplicar as mudanças:"
echo "     Ctrl+C  (para encerrar)"
echo "     bash run.sh  (para reiniciar)"
echo ""
echo "   Ou inicie agora com:"
echo "     bash run.sh"
echo ""
