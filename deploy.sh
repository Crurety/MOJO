#!/bin/bash

# 部署脚本

echo "=== AI创作平台部署脚本 ==="

# 检查 Docker 是否已安装
if ! command -v docker &> /dev/null; then
    echo "错误: Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "错误: docker-compose 未安装，请先安装 docker-compose"
    exit 1
fi

# 构建和启动服务
echo "正在构建和启动服务..."
docker-compose up -d --build

# 检查服务状态
echo "正在检查服务状态..."
sleep 5
docker-compose ps

echo "=== 部署完成 ==="
echo "前端访问地址: http://localhost:3000"
echo "后台管理访问地址: http://localhost:3001"
echo "API 接口地址: http://localhost:8000/api/v1"
echo ""
echo "请确保已配置以下环境变量:"
echo "- OPENAI_API_KEY"
echo "- STABILITY_API_KEY"
echo "- RUNWAY_API_KEY"
echo "- WECHAT_APP_ID, WECHAT_MCH_ID, WECHAT_API_KEY"
echo "- ALIPAY_APP_ID, ALIPAY_PRIVATE_KEY"
echo "- UNIONPAY_MERCHANT_ID, UNIONPAY_API_KEY"
