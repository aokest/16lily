#!/bin/bash

# 文档维护脚本 - 简化版
# 用法: ./maintain_docs.sh [--apply] [--quick] [--help]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 获取脚本所在目录的上一级目录作为项目根目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# 日志函数
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 显示帮助
show_help() {
    echo "文档维护脚本"
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --apply   实际应用链接修复"
    echo "  --quick   快速模式"
    echo "  --help    显示帮助"
    echo ""
    echo "示例:"
    echo "  $0              # 试运行"
    echo "  $0 --apply      # 实际修复"
    echo "  $0 --quick      # 快速检测"
}

# 运行链接修复
run_link_fix() {
    local apply_arg=""
    if [ "$1" = "apply" ]; then
        apply_arg="--apply"
        log_warning "实际应用模式：将修改文件"
    else
        log_info "试运行模式：仅显示需要修复的链接"
    fi
    
    python scripts/docs_link_fix.py $apply_arg
}

# 运行重复检测
run_duplicate_check() {
    local quick_arg=""
    if [ "$1" = "--quick" ]; then
        quick_arg="--quick"
        log_info "快速模式：仅检测完全相同的文档"
    fi
    
    python scripts/docs_duplicate_check.py --docs-root docs $quick_arg
}

# 主函数
main() {
    # 默认参数
    MODE="dryrun"
    QUICK=""
    
    # 解析参数
    for arg in "$@"; do
        case $arg in
            --apply)
                MODE="apply"
                ;;
            --quick)
                QUICK="--quick"
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                # 忽略未知参数或报错
                # log_error "未知选项: $arg"
                # show_help
                # exit 1
                ;;
        esac
    done
    
    log_info "开始文档维护..."
    log_info "项目目录: $PROJECT_ROOT"
    log_info "模式: $MODE"
    
    # 运行链接修复
    run_link_fix $MODE
    
    # 运行重复检测
    run_duplicate_check $QUICK
    
    log_success "文档维护完成！"
}

# 执行
main "$@"
