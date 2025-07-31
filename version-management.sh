#!/bin/bash

# 浩流简历编辑器 - 版本管理脚本
# Resume Editor Version Management Script

set -e

# 颜色输出函数
print_info() {
    echo -e "\033[1;34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[1;32m[SUCCESS]\033[0m $1"
}

print_warning() {
    echo -e "\033[1;33m[WARNING]\033[0m $1"
}

print_error() {
    echo -e "\033[1;31m[ERROR]\033[0m $1"
}

# 获取当前版本
get_current_version() {
    if [ -f "VERSION" ]; then
        cat VERSION
    else
        echo "0.0.0"
    fi
}

# 验证版本格式
validate_version() {
    local version=$1
    if [[ $version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        return 0
    else
        print_error "版本格式无效: $version (期望格式: x.y.z)"
        return 1
    fi
}

# 比较版本号
version_gt() {
    test "$(printf '%s\n' "$@" | sort -V | head -n 1)" != "$1"
}

# 更新所有版本文件
update_version_files() {
    local new_version=$1
    
    print_info "更新版本文件..."
    
    # 更新 VERSION 文件
    echo "$new_version" > VERSION
    print_success "已更新 VERSION"
    
    # 更新 frontend/package.json
    if [ -f "frontend/package.json" ]; then
        sed -i.bak "s/\"version\": \"[^\"]*\"/\"version\": \"$new_version\"/" frontend/package.json
        rm -f frontend/package.json.bak
        print_success "已更新 frontend/package.json"
    fi
    
    # 更新 CLAUDE.md 中的版本信息
    if [ -f "CLAUDE.md" ]; then
        sed -i.bak "s/### 当前版本: v[0-9]\+\.[0-9]\+\.[0-9]\+/### 当前版本: v$new_version/" CLAUDE.md
        rm -f CLAUDE.md.bak
        print_success "已更新 CLAUDE.md"
    fi
}

# 创建版本标签
create_version_tag() {
    local version=$1
    local message=$2
    
    print_info "创建 Git 标签..."
    
    # 检查是否有未提交的更改
    if ! git diff --quiet HEAD; then
        print_warning "存在未提交的更改，建议先提交"
        read -p "是否继续创建标签？[y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return 1
        fi
    fi
    
    # 创建标签
    if [ -n "$message" ]; then
        git tag -a "v$version" -m "$message"
    else
        git tag -a "v$version" -m "Release version $version"
    fi
    
    print_success "已创建标签 v$version"
}

# 显示版本信息
show_version_info() {
    local current_version=$(get_current_version)
    
    echo "=================================================="
    echo "📋 浩流简历编辑器 - 版本信息"
    echo "=================================================="
    echo
    echo "当前版本: v$current_version"
    echo
    
    # 显示各文件中的版本
    echo "📁 版本文件状态:"
    
    if [ -f "VERSION" ]; then
        echo "  VERSION: $(cat VERSION)"
    else
        echo "  VERSION: [不存在]"
    fi
    
    if [ -f "frontend/package.json" ]; then
        local package_version=$(grep '"version"' frontend/package.json | cut -d'"' -f4)
        echo "  frontend/package.json: $package_version"
    fi
    
    # 显示 Git 标签
    echo
    echo "🏷️  最近的 Git 标签:"
    git tag -l --sort=-version:refname | head -5 || echo "  无标签"
    
    echo
    echo "📝 提交历史:"
    git log --oneline -5 || echo "  无提交历史"
    echo
}

# 版本升级
bump_version() {
    local bump_type=$1
    local current_version=$(get_current_version)
    
    # 解析当前版本
    IFS='.' read -r major minor patch <<< "$current_version"
    
    case $bump_type in
        major)
            major=$((major + 1))
            minor=0
            patch=0
            ;;
        minor)
            minor=$((minor + 1))
            patch=0
            ;;
        patch)
            patch=$((patch + 1))
            ;;
        *)
            print_error "无效的升级类型: $bump_type (支持: major, minor, patch)"
            return 1
            ;;
    esac
    
    local new_version="$major.$minor.$patch"
    
    print_info "版本升级: $current_version -> $new_version"
    
    # 确认升级
    read -p "确认升级到 v$new_version？[y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        update_version_files "$new_version"
        print_success "版本已升级到 v$new_version"
        
        # 询问是否创建标签
        read -p "是否创建 Git 标签？[y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            read -p "请输入发布说明 (可选): " release_message
            create_version_tag "$new_version" "$release_message"
        fi
    else
        print_info "版本升级已取消"
    fi
}

# 设置特定版本
set_version() {
    local new_version=$1
    local current_version=$(get_current_version)
    
    if ! validate_version "$new_version"; then
        return 1
    fi
    
    if [ "$new_version" = "$current_version" ]; then
        print_warning "新版本与当前版本相同: $new_version"
        return 1
    fi
    
    print_info "设置版本: $current_version -> $new_version"
    
    # 确认设置
    read -p "确认设置版本为 v$new_version？[y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        update_version_files "$new_version"
        print_success "版本已设置为 v$new_version"
        
        # 询问是否创建标签
        read -p "是否创建 Git 标签？[y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            read -p "请输入发布说明 (可选): " release_message
            create_version_tag "$new_version" "$release_message"
        fi
    else
        print_info "版本设置已取消"
    fi
}

# 准备发布
prepare_release() {
    local version=$1
    
    if [ -z "$version" ]; then
        version=$(get_current_version)
    fi
    
    print_info "准备发布 v$version..."
    
    # 检查工作目录状态
    if ! git diff --quiet HEAD; then
        print_error "存在未提交的更改，请先提交所有更改"
        return 1
    fi
    
    # 检查是否在正确的分支
    current_branch=$(git branch --show-current)
    if [ "$current_branch" != "main" ] && [ "$current_branch" != "master" ]; then
        print_warning "当前不在主分支 ($current_branch)，建议切换到 main/master 分支"
        read -p "是否继续？[y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return 1
        fi
    fi
    
    echo "🚀 发布检查清单:"
    echo "  ✅ 工作目录干净"
    echo "  ✅ 版本号: v$version"
    echo "  ✅ 分支: $current_branch"
    
    # 运行测试 (如果存在)
    if [ -f "backend/requirements.txt" ]; then
        print_info "检查后端依赖..."
        # 这里可以添加测试命令
    fi
    
    if [ -f "frontend/package.json" ]; then
        print_info "检查前端依赖..."
        # 这里可以添加测试命令
    fi
    
    # 创建发布标签
    read -p "是否创建发布标签 v$version？[y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "请输入发布说明: " release_message
        create_version_tag "$version" "$release_message"
        
        print_success "✨ 发布准备完成！"
        echo "📋 下一步操作:"
        echo "  1. 推送标签: git push origin v$version"
        echo "  2. 推送到远程: git push origin $current_branch"
        echo "  3. 创建 GitHub Release"
        echo "  4. 部署到生产环境"
    fi
}

# 显示帮助信息
show_help() {
    echo "浩流简历编辑器 - 版本管理脚本"
    echo
    echo "用法: $0 <命令> [参数]"
    echo
    echo "命令:"
    echo "  info                    显示当前版本信息"
    echo "  bump <type>            升级版本 (major|minor|patch)"
    echo "  set <version>          设置特定版本"
    echo "  tag [version]          为指定版本创建标签"
    echo "  release [version]      准备发布"
    echo "  help                   显示帮助信息"
    echo
    echo "示例:"
    echo "  $0 info                显示版本信息"
    echo "  $0 bump patch          升级补丁版本"
    echo "  $0 set 2.2.0          设置版本为 2.2.0"
    echo "  $0 release             准备当前版本发布"
}

# 主函数
main() {
    local command=$1
    
    case $command in
        info)
            show_version_info
            ;;
        bump)
            local bump_type=$2
            if [ -z "$bump_type" ]; then
                print_error "请指定升级类型: major, minor, patch"
                exit 1
            fi
            bump_version "$bump_type"
            ;;
        set)
            local new_version=$2
            if [ -z "$new_version" ]; then
                print_error "请指定版本号"
                exit 1
            fi
            set_version "$new_version"
            ;;
        tag)
            local version=$2
            if [ -z "$version" ]; then
                version=$(get_current_version)
            fi
            read -p "请输入标签说明: " tag_message
            create_version_tag "$version" "$tag_message"
            ;;
        release)
            local version=$2
            prepare_release "$version"
            ;;
        help|--help|-h)
            show_help
            ;;
        "")
            show_version_info
            ;;
        *)
            print_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"