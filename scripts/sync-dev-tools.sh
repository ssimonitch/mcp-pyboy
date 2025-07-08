#!/bin/bash
# Script to sync development tool versions between IDE and pre-commit

set -e

echo "🔧 Syncing development tool versions..."

# Get current local tool versions
echo "📋 Current local versions:"
echo "  Ruff: $(ruff --version)"
echo "  Black: $(black --version)"
echo "  MyPy: $(mypy --version)"

# Update pre-commit hooks to latest versions
echo ""
echo "🚀 Updating pre-commit hooks..."
pre-commit autoupdate

# Reinstall hooks
echo ""
echo "🔨 Reinstalling pre-commit hooks..."
pre-commit install

# Run a test to ensure everything works
echo ""
echo "🧪 Testing pre-commit hooks..."
pre-commit run --all-files || {
    echo "❌ Pre-commit hooks failed. Please review the output above."
    exit 1
}

echo ""
echo "✅ Development tools are now in sync!"
echo ""
echo "💡 Tips:"
echo "  - Your IDE and pre-commit now use the same tool versions"
echo "  - Both use Black for formatting, Ruff for linting/imports"
echo "  - Run this script periodically to stay updated"
