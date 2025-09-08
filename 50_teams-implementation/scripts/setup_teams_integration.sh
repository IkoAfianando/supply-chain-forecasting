#!/bin/bash

# Supply Chain Forecasting with Microsoft Teams Integration
# Automated Environment Setup and Deployment Script
# Version: 2.0.0

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_ROOT/logs/setup_$(date +%Y%m%d_%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

# Create logs directory
mkdir -p "$PROJECT_ROOT/logs"

log "Starting Supply Chain Forecasting with Teams Integration Setup"
log "Project Root: $PROJECT_ROOT"

# Check if running as root (for Docker installation)
check_sudo() {
    if [[ $EUID -eq 0 ]]; then
        warn "Running as root. This is recommended only for initial system setup."
    fi
}

# Detect operating system
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        if command -v apt-get &> /dev/null; then
            PACKAGE_MANAGER="apt"
        elif command -v yum &> /dev/null; then
            PACKAGE_MANAGER="yum"
        else
            error "Unsupported Linux distribution. Please install Docker manually."
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        PACKAGE_MANAGER="brew"
    elif [[ "$OSTYPE" == "msys" ]]; then
        OS="windows"
        warn "Windows detected. Please use Docker Desktop for Windows."
    else
        error "Unsupported operating system: $OSTYPE"
    fi
    
    log "Detected OS: $OS with package manager: $PACKAGE_MANAGER"
}

# Check system requirements
check_requirements() {
    log "Checking system requirements..."
    
    # Check minimum RAM (8GB recommended)
    if [[ "$OS" == "linux" ]]; then
        TOTAL_RAM=$(free -g | awk '/^Mem:/{print $2}')
        if [[ $TOTAL_RAM -lt 8 ]]; then
            warn "Less than 8GB RAM detected. Performance may be impacted."
        fi
    fi
    
    # Check disk space (minimum 20GB)
    AVAILABLE_SPACE=$(df -BG "$PROJECT_ROOT" | awk 'NR==2 {print $4}' | sed 's/G//')
    if [[ $AVAILABLE_SPACE -lt 20 ]]; then
        warn "Less than 20GB disk space available. May cause issues during deployment."
    fi
    
    log "System requirements check completed"
}

# Install Docker and Docker Compose
install_docker() {
    log "Installing Docker and Docker Compose..."
    
    if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
        log "Docker and Docker Compose already installed"
        return
    fi
    
    case "$PACKAGE_MANAGER" in
        "apt")
            sudo apt-get update
            sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
            echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            sudo apt-get update
            sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            ;;
        "yum")
            sudo yum install -y yum-utils
            sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            sudo systemctl start docker
            sudo systemctl enable docker
            ;;
        "brew")
            if ! command -v brew &> /dev/null; then
                error "Homebrew not found. Please install Homebrew first: https://brew.sh"
            fi
            brew install --cask docker
            ;;
        *)
            error "Unsupported package manager for Docker installation"
            ;;
    esac
    
    # Add user to docker group (Linux only)
    if [[ "$OS" == "linux" ]] && [[ $EUID -ne 0 ]]; then
        sudo usermod -aG docker "$USER"
        warn "User added to docker group. Please log out and back in, or run 'newgrp docker'"
    fi
    
    log "Docker installation completed"
}

# Install Python dependencies
install_python_deps() {
    log "Installing Python dependencies..."
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d" " -f2 | cut -d"." -f1-2)
        if [[ $(echo "$PYTHON_VERSION >= 3.8" | bc -l) -eq 0 ]]; then
            error "Python 3.8+ required. Found version: $PYTHON_VERSION"
        fi
    else
        error "Python 3 not found. Please install Python 3.8+"
    fi
    
    # Install pip if not available
    if ! command -v pip3 &> /dev/null; then
        case "$PACKAGE_MANAGER" in
            "apt") sudo apt-get install -y python3-pip ;;
            "yum") sudo yum install -y python3-pip ;;
            "brew") brew install python3 ;;
        esac
    fi
    
    # Create virtual environment
    if [[ ! -d "$PROJECT_ROOT/venv" ]]; then
        python3 -m venv "$PROJECT_ROOT/venv"
    fi
    
    # Activate virtual environment and install requirements
    source "$PROJECT_ROOT/venv/bin/activate"
    
    # Create requirements.txt if it doesn't exist
    cat > "$PROJECT_ROOT/requirements.txt" << EOF
fastapi==0.104.1
uvicorn[standard]==0.24.0
pymongo==4.6.0
redis==5.0.1
kafka-python==2.0.2
aiohttp==3.9.1
pandas==2.1.4
numpy==1.25.2
pymsteams==0.2.2
pydantic==2.5.2
python-jose[cryptography]==3.3.0
python-multipart==0.0.6
prometheus-client==0.19.0
asyncio-mqtt==0.16.1
structlog==23.2.0
python-dotenv==1.0.0
alembic==1.13.1
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
celery==5.3.4
flower==2.0.1
gunicorn==21.2.0
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.12.1
flake8==6.1.0
mypy==1.8.0
EOF
    
    pip install -r "$PROJECT_ROOT/requirements.txt"
    
    log "Python dependencies installed successfully"
}

# Setup environment configuration
setup_environment() {
    log "Setting up environment configuration..."
    
    # Create .env file from template
    ENV_FILE="$PROJECT_ROOT/50_teams-implementation/deployment/.env"
    ENV_TEMPLATE="$PROJECT_ROOT/50_teams-implementation/deployment/.env.template"
    
    if [[ ! -f "$ENV_TEMPLATE" ]]; then
        cat > "$ENV_TEMPLATE" << EOF
# Supply Chain Forecasting with Teams Integration
# Environment Configuration

# Database Configuration
MONGO_ROOT_USERNAME=admin
MONGO_ROOT_PASSWORD=supplychain2025
MONGO_DATABASE=supply_chain_forecasting
REDIS_PASSWORD=supplychain2025

# Microsoft Teams Integration
TEAMS_WEBHOOK_URL=https://your-company.webhook.office.com/webhookb2/...
TEAMS_BOT_APP_ID=your-bot-app-id
TEAMS_BOT_APP_PASSWORD=your-bot-app-password

# API Configuration
API_SECRET_KEY=supply-chain-secret-key-2025
JWT_SECRET_KEY=jwt-secret-key-2025
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# External Services
WEATHER_API_KEY=your-weather-api-key
SUPPLIER_API_ENDPOINTS={"steel": "https://api.supplier1.com", "welding": "https://api.supplier2.com"}

# Monitoring Configuration
GRAFANA_PASSWORD=supplychain2025
PROMETHEUS_RETENTION=30d

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json

# Health Check Configuration
HEALTH_CHECK_INTERVAL=300
ALERT_COOLDOWN_MINUTES=15

# Business Configuration
COMPANY_NAME=Your Company Name
BUSINESS_HOURS_START=08:00
BUSINESS_HOURS_END=18:00
TIMEZONE=UTC

# Performance Configuration
MAX_WORKERS=4
KAFKA_BATCH_SIZE=100
REDIS_TTL_SECONDS=3600
EOF
    fi
    
    if [[ ! -f "$ENV_FILE" ]]; then
        cp "$ENV_TEMPLATE" "$ENV_FILE"
        warn "Created .env file from template. Please update with your specific configuration."
    fi
    
    log "Environment configuration completed"
}

# Setup directory structure
setup_directories() {
    log "Setting up directory structure..."
    
    mkdir -p "$PROJECT_ROOT"/{data,logs,backups,temp}
    mkdir -p "$PROJECT_ROOT/data"/{migration,exports,imports}
    mkdir -p "$PROJECT_ROOT/50_teams-implementation"/{nginx,monitoring}
    mkdir -p "$PROJECT_ROOT/50_teams-implementation/monitoring"/{prometheus,grafana}
    mkdir -p "$PROJECT_ROOT/50_teams-implementation/monitoring/grafana"/{dashboards,datasources}
    
    # Create placeholder configuration files
    if [[ ! -f "$PROJECT_ROOT/50_teams-implementation/monitoring/prometheus.yml" ]]; then
        cat > "$PROJECT_ROOT/50_teams-implementation/monitoring/prometheus.yml" << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
  
  - job_name: 'supply-chain-api'
    static_configs:
      - targets: ['supply-chain-api:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s
  
  - job_name: 'teams-pipeline'
    static_configs:
      - targets: ['teams-pipeline:8001']
    metrics_path: '/metrics'
    scrape_interval: 30s
EOF
    fi
    
    log "Directory structure setup completed"
}

# Initialize Git repository if needed
setup_git() {
    log "Setting up Git repository..."
    
    if [[ ! -d "$PROJECT_ROOT/.git" ]]; then
        cd "$PROJECT_ROOT"
        git init
        git add .
        git commit -m "Initial commit: Supply Chain Forecasting with Teams Integration"
    fi
    
    # Create .gitignore if it doesn't exist
    if [[ ! -f "$PROJECT_ROOT/.gitignore" ]]; then
        cat > "$PROJECT_ROOT/.gitignore" << EOF
# Environment files
.env
.env.local
.env.production

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Docker
.docker/
docker-compose.override.yml

# Logs
logs/
*.log

# Data
data/migration/*
data/exports/*
temp/
backups/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Security
*.pem
*.key
secrets/
EOF
    fi
    
    log "Git repository setup completed"
}

# Create Docker health check script
create_health_check() {
    log "Creating health check scripts..."
    
    cat > "$PROJECT_ROOT/50_teams-implementation/scripts/health_check.sh" << 'EOF'
#!/bin/bash

# Health Check Script for Supply Chain Forecasting with Teams Integration

echo "🔍 Supply Chain Forecasting Health Check"
echo "=========================================="

# Check Docker containers
echo "📦 Checking Docker containers..."
docker-compose -f 50_teams-implementation/deployment/docker-compose.yml ps

# Check API health
echo ""
echo "🌐 Checking API health..."
API_HEALTH=$(curl -s http://localhost:8000/health || echo "FAILED")
if [[ "$API_HEALTH" == *"healthy"* ]]; then
    echo "✅ API is healthy"
else
    echo "❌ API health check failed"
fi

# Check database connections
echo ""
echo "🗄️ Checking database connections..."
MONGO_STATUS=$(docker exec supply-chain-mongodb mongosh --eval "db.adminCommand('ping')" 2>/dev/null || echo "FAILED")
if [[ "$MONGO_STATUS" == *"ok"* ]]; then
    echo "✅ MongoDB is connected"
else
    echo "❌ MongoDB connection failed"
fi

REDIS_STATUS=$(docker exec supply-chain-redis redis-cli ping 2>/dev/null || echo "FAILED")
if [[ "$REDIS_STATUS" == "PONG" ]]; then
    echo "✅ Redis is connected"
else
    echo "❌ Redis connection failed"
fi

# Check Kafka
echo ""
echo "📡 Checking Kafka..."
KAFKA_STATUS=$(docker exec supply-chain-kafka kafka-topics.sh --bootstrap-server localhost:9092 --list 2>/dev/null || echo "FAILED")
if [[ "$KAFKA_STATUS" != "FAILED" ]]; then
    echo "✅ Kafka is running"
else
    echo "❌ Kafka check failed"
fi

# Check monitoring services
echo ""
echo "📊 Checking monitoring services..."
PROMETHEUS_STATUS=$(curl -s http://localhost:9090/-/healthy || echo "FAILED")
if [[ "$PROMETHEUS_STATUS" == "Prometheus is Healthy." ]]; then
    echo "✅ Prometheus is healthy"
else
    echo "❌ Prometheus health check failed"
fi

GRAFANA_STATUS=$(curl -s http://localhost:3000/api/health || echo "FAILED")
if [[ "$GRAFANA_STATUS" == *"ok"* ]]; then
    echo "✅ Grafana is healthy"
else
    echo "❌ Grafana health check failed"
fi

echo ""
echo "🎯 Health check completed!"
EOF

    chmod +x "$PROJECT_ROOT/50_teams-implementation/scripts/health_check.sh"
    
    log "Health check scripts created"
}

# Build and start services
deploy_services() {
    log "Building and deploying services..."
    
    cd "$PROJECT_ROOT/50_teams-implementation/deployment"
    
    # Pull required images
    docker-compose pull
    
    # Build custom images
    docker-compose build
    
    # Start services
    docker-compose up -d
    
    # Wait for services to start
    log "Waiting for services to initialize..."
    sleep 30
    
    # Run health check
    "$PROJECT_ROOT/50_teams-implementation/scripts/health_check.sh"
    
    log "Services deployment completed"
}

# Setup monitoring dashboards
setup_monitoring() {
    log "Setting up monitoring dashboards..."
    
    # Create Grafana dashboard configuration
    mkdir -p "$PROJECT_ROOT/50_teams-implementation/monitoring/grafana/dashboards"
    
    cat > "$PROJECT_ROOT/50_teams-implementation/monitoring/grafana/dashboards/supply-chain-dashboard.json" << 'EOF'
{
  "dashboard": {
    "id": null,
    "title": "Supply Chain Forecasting with Teams Integration",
    "tags": ["supply-chain", "teams", "forecasting"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Supply Chain Events Processed",
        "type": "stat",
        "targets": [
          {
            "expr": "increase(supply_chain_events_processed_total[1h])",
            "legendFormat": "Events/Hour"
          }
        ]
      },
      {
        "id": 2,
        "title": "Teams Notifications Sent",
        "type": "stat",
        "targets": [
          {
            "expr": "increase(teams_notifications_sent_total[1h])",
            "legendFormat": "Notifications/Hour"
          }
        ]
      }
    ],
    "time": {
      "from": "now-6h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
EOF
    
    log "Monitoring setup completed"
}

# Main setup function
main() {
    log "Supply Chain Forecasting with Teams Integration Setup Started"
    
    check_sudo
    detect_os
    check_requirements
    install_docker
    install_python_deps
    setup_environment
    setup_directories
    setup_git
    create_health_check
    deploy_services
    setup_monitoring
    
    log "🎉 Setup completed successfully!"
    echo ""
    info "Next steps:"
    info "1. Update .env file with your Teams webhook URL and other configurations"
    info "2. Access Grafana dashboard at http://localhost:3000 (admin/supplychain2025)"
    info "3. Access Prometheus at http://localhost:9090"
    info "4. Run health check: ./50_teams-implementation/scripts/health_check.sh"
    info "5. View logs: docker-compose -f 50_teams-implementation/deployment/docker-compose.yml logs -f"
    echo ""
    warn "Important: Configure your Microsoft Teams webhook URL in the .env file before starting the Teams integration!"
}

# Handle script interruption
trap 'error "Setup interrupted by user"' INT

# Run main function
main "$@"