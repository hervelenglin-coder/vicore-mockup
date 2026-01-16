#!/bin/bash
# VICORE Web Application - Setup Script (Bash/Linux/Mac)
# ======================================================

echo "=== VICORE Setup Script ==="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check Python version
echo -e "\n${YELLOW}[1/6] Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 || python --version 2>&1)
echo "  Installed: $PYTHON_VERSION"
echo "  Required: Python 3.10-3.12"

# Check/Install Poetry
echo -e "\n${YELLOW}[2/6] Checking Poetry...${NC}"
if ! command -v poetry &> /dev/null; then
    echo -e "  ${RED}Poetry not found. Installing...${NC}"
    pip install poetry
else
    echo -e "  ${GREEN}Poetry is installed: $(poetry --version)${NC}"
fi

# Install dependencies
echo -e "\n${YELLOW}[3/6] Installing Python dependencies...${NC}"
poetry install --no-interaction 2>&1
if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}Dependencies installed successfully${NC}"
else
    echo -e "  ${RED}Warning: Some dependencies may have failed${NC}"
fi

# Check PostgreSQL
echo -e "\n${YELLOW}[4/6] Checking PostgreSQL...${NC}"
if ! command -v psql &> /dev/null; then
    echo -e "  ${RED}PostgreSQL client not found${NC}"
    echo "  Install: sudo apt install postgresql-client (Debian/Ubuntu)"
    echo "  Or: brew install postgresql (macOS)"
else
    echo -e "  ${GREEN}PostgreSQL client found${NC}"
fi

# Check Redis
echo -e "\n${YELLOW}[5/6] Checking Redis...${NC}"
if ! command -v redis-cli &> /dev/null; then
    echo -e "  ${RED}Redis not found${NC}"
    echo "  Install: sudo apt install redis-server (Debian/Ubuntu)"
    echo "  Or: brew install redis (macOS)"
    echo "  Or: docker run -d -p 6379:6379 redis"
else
    echo -e "  ${GREEN}Redis found${NC}"
fi

# Check .env file
echo -e "\n${YELLOW}[6/6] Checking configuration...${NC}"
if [ -f ".env" ]; then
    echo -e "  ${GREEN}.env file exists${NC}"
else
    echo -e "  ${RED}.env file not found. Creating template...${NC}"
    cat > .env.template << 'EOF'
# Database Configuration
export DB_HOST="localhost"
export DB_PORT="5432"
export DB="euro_tunnel_dev"
export DB_USER="your_user"
export DB_PASSWORD="your_password"

# Web Server Configuration
export WEB_HOST="127.0.0.1"
export WEB_PORT="5000"
export WEB_DEBUG="True"

# Image Directory
export WHEEL_IMG_DIR="/path/to/wheel/images"
EOF
    echo -e "  ${YELLOW}Created .env.template - copy to .env and fill in values${NC}"
fi

# Summary
echo -e "\n${CYAN}=== Setup Summary ===${NC}"
echo "To run the application:"
echo "  1. Ensure PostgreSQL is running with the eurotunnel database"
echo "  2. Ensure Redis is running on localhost:6379"
echo "  3. Configure .env with your database credentials"
echo "  4. Run: poetry run python -m eurotunnel_web.app"
echo ""
echo "To run tests:"
echo "  poetry run pytest tests/ -v"
