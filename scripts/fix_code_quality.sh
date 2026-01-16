#!/bin/bash
# =============================================================================
# VICORE - Script de Correction Automatique de la Qualité du Code
# =============================================================================
# Ce script corrige automatiquement les problèmes de style et de formatage.
# Les corrections de sécurité doivent être faites manuellement.
# =============================================================================

set -e  # Exit on error

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}=== VICORE Code Quality Fix ===${NC}"
echo ""

# Check we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}Error: pyproject.toml not found. Run this script from the project root.${NC}"
    exit 1
fi

# 1. Install tools
echo -e "${YELLOW}[1/6] Installing tools...${NC}"
pip install black isort autoflake flake8 --quiet
echo -e "${GREEN}  ✓ Tools installed${NC}"

# 2. Remove unused imports
echo -e "${YELLOW}[2/6] Removing unused imports...${NC}"
autoflake --in-place --remove-all-unused-imports --recursive eurotunnel_web/
echo -e "${GREEN}  ✓ Unused imports removed${NC}"

# 3. Sort imports
echo -e "${YELLOW}[3/6] Sorting imports...${NC}"
isort eurotunnel_web/ --profile black --line-length 120 --quiet
echo -e "${GREEN}  ✓ Imports sorted${NC}"

# 4. Format with Black
echo -e "${YELLOW}[4/6] Formatting with Black...${NC}"
black eurotunnel_web/ --line-length 120 --quiet
echo -e "${GREEN}  ✓ Code formatted${NC}"

# 5. Fix trailing whitespace and end of file
echo -e "${YELLOW}[5/6] Fixing whitespace issues...${NC}"
find eurotunnel_web -name "*.py" -exec sed -i 's/[[:space:]]*$//' {} \;
find eurotunnel_web -name "*.py" -exec sed -i -e '$a\' {} \;
echo -e "${GREEN}  ✓ Whitespace fixed${NC}"

# 6. Check with Flake8
echo -e "${YELLOW}[6/6] Checking with Flake8...${NC}"
FLAKE8_COUNT=$(flake8 eurotunnel_web/ --max-line-length=120 --ignore=E501,W503,E203 --count --quiet 2>&1 | tail -1 || echo "0")
if [ "$FLAKE8_COUNT" = "0" ] || [ -z "$FLAKE8_COUNT" ]; then
    echo -e "${GREEN}  ✓ No flake8 issues found!${NC}"
else
    echo -e "${YELLOW}  ⚠ $FLAKE8_COUNT remaining flake8 issues${NC}"
    echo ""
    echo "Run 'flake8 eurotunnel_web/ --max-line-length=120' to see details"
fi

echo ""
echo -e "${CYAN}=== Summary ===${NC}"
echo -e "${GREEN}✓ Automatic fixes applied${NC}"
echo ""
echo -e "${YELLOW}Manual fixes still required:${NC}"
echo "  1. Replace '== None' with 'is None' in:"
echo "     - eurotunnel_web/db_iface.py"
echo "     - eurotunnel_web/display_name_iface.py"
echo "  2. Fix bare except in eurotunnel_web/version.py"
echo "  3. Security fixes (see PLAN_CORRECTION.md)"
echo ""
echo -e "${CYAN}=== Done ===${NC}"
