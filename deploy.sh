#!/bin/bash

################################################################################
# COMPREHENSIVE DEPLOYMENT SCRIPT
# Political Analyst Workbench - Live Political Monitor
#
# This script deploys both frontend and backend while maintaining stable URLs
#
# Usage:
#   ./deploy.sh                  # Deploy both frontend and backend
#   ./deploy.sh backend          # Deploy backend only
#   ./deploy.sh frontend         # Deploy frontend only
#   ./deploy.sh --help           # Show help
#
# Stable URLs (never change):
#   Frontend: https://d2dk8wkh2d0mmy.cloudfront.net
#   Backend:  https://d1h4cjcbl77aah.cloudfront.net
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_DIR="Frontend_v2"
BACKEND_DIR="backend_v2"
S3_BUCKET="tavily-research-frontend-1759377613"
CLOUDFRONT_DISTRIBUTION_ID="E1YO4Y7KXANJNR"
EB_ENVIRONMENT="political-analyst-backend-lb"
FRONTEND_URL="https://d2dk8wkh2d0mmy.cloudfront.net"
BACKEND_URL="https://d1h4cjcbl77aah.cloudfront.net"

# Helper functions
print_header() {
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}  $1"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    local all_good=true
    
    # Check AWS CLI
    if command -v aws &> /dev/null; then
        print_success "AWS CLI installed"
    else
        print_error "AWS CLI not found. Install: https://aws.amazon.com/cli/"
        all_good=false
    fi
    
    # Check EB CLI
    if command -v eb &> /dev/null; then
        print_success "Elastic Beanstalk CLI installed"
    else
        print_error "EB CLI not found. Install: pip install awsebcli"
        all_good=false
    fi
    
    # Check Node.js
    if command -v node &> /dev/null; then
        print_success "Node.js installed ($(node --version))"
    else
        print_error "Node.js not found. Install: https://nodejs.org/"
        all_good=false
    fi
    
    # Check npm
    if command -v npm &> /dev/null; then
        print_success "npm installed ($(npm --version))"
    else
        print_error "npm not found"
        all_good=false
    fi
    
    # Check git
    if command -v git &> /dev/null; then
        print_success "Git installed"
    else
        print_error "Git not found"
        all_good=false
    fi
    
    if [ "$all_good" = false ]; then
        print_error "Please install missing prerequisites"
        exit 1
    fi
    
    echo ""
}

# Check for uncommitted changes
check_git_status() {
    print_header "Checking Git Status"
    
    if [[ -n $(git status -s) ]]; then
        print_warning "You have uncommitted changes:"
        git status -s
        echo ""
        read -p "Do you want to continue? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Deployment cancelled"
            exit 1
        fi
    else
        print_success "Working directory clean"
    fi
    
    echo ""
}

# Deploy backend
deploy_backend() {
    print_header "Deploying Backend to AWS Elastic Beanstalk"
    
    cd "$BACKEND_DIR"
    
    # Check EB environment status
    print_info "Checking backend environment status..."
    eb status "$EB_ENVIRONMENT" > /dev/null 2>&1 || {
        print_error "Backend environment '$EB_ENVIRONMENT' not found"
        print_info "Initialize with: cd $BACKEND_DIR && eb init"
        exit 1
    }
    
    # Deploy
    print_info "Deploying backend..."
    if eb deploy "$EB_ENVIRONMENT"; then
        print_success "Backend deployed successfully"
    else
        print_error "Backend deployment failed"
        cd ..
        exit 1
    fi
    
    # Wait for environment to be ready
    print_info "Waiting for environment to be ready..."
    sleep 5
    
    # Test backend health
    print_info "Testing backend health..."
    if curl -sf "$BACKEND_URL/health" > /dev/null; then
        print_success "Backend health check passed"
        echo -e "${GREEN}   Backend URL: $BACKEND_URL${NC}"
    else
        print_warning "Backend health check failed (may need a moment to start)"
    fi
    
    cd ..
    echo ""
}

# Deploy frontend
deploy_frontend() {
    print_header "Deploying Frontend to S3 + CloudFront"
    
    cd "$FRONTEND_DIR"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_info "Installing dependencies..."
        npm install
    fi
    
    # Verify config.ts has correct backend URL
    print_info "Verifying backend URL in config..."
    if grep -q "d1h4cjcbl77aah.cloudfront.net" src/config.ts; then
        print_success "Backend URL correctly configured"
    else
        print_error "Backend URL not configured correctly in src/config.ts"
        print_info "Expected: https://d1h4cjcbl77aah.cloudfront.net"
        cd ..
        exit 1
    fi
    
    # Build frontend
    print_info "Building frontend..."
    if npx vite build; then
        print_success "Frontend build completed"
    else
        print_error "Frontend build failed"
        cd ..
        exit 1
    fi
    
    # Upload to S3
    print_info "Uploading to S3..."
    if aws s3 sync dist/ "s3://$S3_BUCKET/" --delete; then
        print_success "Frontend uploaded to S3"
    else
        print_error "S3 upload failed"
        cd ..
        exit 1
    fi
    
    # Invalidate CloudFront cache
    print_info "Invalidating CloudFront cache..."
    INVALIDATION_ID=$(aws cloudfront create-invalidation \
        --distribution-id "$CLOUDFRONT_DISTRIBUTION_ID" \
        --paths "/*" \
        --query 'Invalidation.Id' \
        --output text)
    
    if [ -n "$INVALIDATION_ID" ]; then
        print_success "CloudFront cache invalidation created (ID: $INVALIDATION_ID)"
        print_info "Cache will propagate in 2-3 minutes"
    else
        print_error "CloudFront invalidation failed"
        cd ..
        exit 1
    fi
    
    cd ..
    echo ""
}

# Run post-deployment tests
run_tests() {
    print_header "Running Post-Deployment Tests"
    
    # Test backend health
    print_info "Testing backend health endpoint..."
    if curl -sf "$BACKEND_URL/health" > /dev/null; then
        print_success "Backend health check: PASSED"
    else
        print_warning "Backend health check: FAILED (may need time to start)"
    fi
    
    # Test Live Monitor endpoint
    print_info "Testing Live Monitor endpoint..."
    RESPONSE=$(curl -sf -X POST "$BACKEND_URL/api/live-monitor/explosive-topics" \
        -H "Content-Type: application/json" \
        -d '{"keywords": ["test"], "cache_hours": 1, "max_results": 1}' 2>&1)
    
    if echo "$RESPONSE" | grep -q '"success":true'; then
        print_success "Live Monitor endpoint: PASSED"
    else
        print_warning "Live Monitor endpoint: FAILED or needs time"
    fi
    
    # Test frontend
    print_info "Testing frontend URL..."
    if curl -sf "$FRONTEND_URL" > /dev/null; then
        print_success "Frontend accessible: PASSED"
    else
        print_warning "Frontend check: FAILED (CloudFront may be propagating)"
    fi
    
    echo ""
}

# Show deployment summary
show_summary() {
    print_header "Deployment Summary"
    
    echo -e "${GREEN}✅ Deployment Complete!${NC}"
    echo ""
    echo -e "${BLUE}Production URLs (stable, never change):${NC}"
    echo -e "   Frontend:  ${GREEN}$FRONTEND_URL${NC}"
    echo -e "   Backend:   ${GREEN}$BACKEND_URL${NC}"
    echo ""
    echo -e "${BLUE}What was deployed:${NC}"
    echo -e "   • Backend:  Elastic Beanstalk ($EB_ENVIRONMENT)"
    echo -e "   • Frontend: S3 + CloudFront (distribution: $CLOUDFRONT_DISTRIBUTION_ID)"
    echo ""
    echo -e "${YELLOW}⏰ Wait 2-3 minutes for CloudFront cache to propagate${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo -e "   1. Test the frontend: ${GREEN}$FRONTEND_URL${NC}"
    echo -e "   2. Check browser console for errors"
    echo -e "   3. Verify Live Monitor auto-fetches topics"
    echo -e "   4. Share URL with clients: ${GREEN}$FRONTEND_URL${NC}"
    echo ""
}

# Show help
show_help() {
    cat << EOF
╔════════════════════════════════════════════════════════════════╗
║           Deployment Script - Political Analyst Workbench       ║
╚════════════════════════════════════════════════════════════════╝

Usage:
  ./deploy.sh                  Deploy both frontend and backend
  ./deploy.sh backend          Deploy backend only
  ./deploy.sh frontend         Deploy frontend only
  ./deploy.sh --help           Show this help message

Stable URLs (never change):
  Frontend: https://d2dk8wkh2d0mmy.cloudfront.net
  Backend:  https://d1h4cjcbl77aah.cloudfront.net

Prerequisites:
  • AWS CLI configured (aws configure)
  • Elastic Beanstalk CLI (pip install awsebcli)
  • Node.js 18+ and npm
  • Git

Examples:
  # Full deployment
  ./deploy.sh

  # Backend changes only
  ./deploy.sh backend

  # Frontend changes only
  ./deploy.sh frontend

Notes:
  • The script checks for uncommitted changes
  • CloudFront cache takes 2-3 minutes to propagate
  • Backend deployment takes ~2 minutes
  • Frontend build + upload takes ~1 minute

EOF
}

# Main execution
main() {
    echo ""
    print_header "Political Analyst Workbench - Deployment Script"
    echo ""
    
    # Parse arguments
    DEPLOY_TARGET="${1:-all}"
    
    case "$DEPLOY_TARGET" in
        --help|-h|help)
            show_help
            exit 0
            ;;
        backend)
            check_prerequisites
            check_git_status
            deploy_backend
            run_tests
            show_summary
            ;;
        frontend)
            check_prerequisites
            check_git_status
            deploy_frontend
            run_tests
            show_summary
            ;;
        all)
            check_prerequisites
            check_git_status
            deploy_backend
            deploy_frontend
            run_tests
            show_summary
            ;;
        *)
            print_error "Invalid argument: $DEPLOY_TARGET"
            echo ""
            show_help
            exit 1
            ;;
    esac
    
    print_success "Deployment process completed!"
    echo ""
}

# Run main function
main "$@"

