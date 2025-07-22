# GridBNB 多币种自动化网格交易机器人

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Binance](https://img.shields.io/badge/Exchange-Binance-yellow.svg)](https://www.binance.com/)

一个基于 Python 的企业级自动化交易程序，支持币安 (Binance) 交易所的**任意多种交易对**。采用先进的网格交易策略，结合动态波动率分析和多层风险管理，旨在稳定捕捉市场波动收益。

## ✨ 核心特性

### 🚀 多币种并发交易
- ✅ **任意交易对支持**: BNB/USDT, ETH/USDT, BTC/USDT 等所有币安现货交易对
- ✅ **并发执行**: 多个交易对同时独立运行，互不干扰
- ✅ **动态配置**: 每个交易对可设置独立的初始价格和网格参数
- ✅ **资源共享**: 单一 ExchangeClient 实例，避免 API 限流

### 📊 智能网格策略
- ✅ **52日年化波动率**: 基于日K线数据的稳定波动率计算
- ✅ **EWMA混合算法**: 70% EWMA + 30% 传统波动率，平衡稳定性与敏感性
- ✅ **动态网格调整**: 根据实时波动率自动调整网格大小 (1.0% - 4.0%)
- ✅ **价格分位分析**: 基于历史价格分位的智能仓位调整

### 🛡️ 多层风险管理
- ✅ **仓位限制**: 可配置的最大/最小仓位比例控制
- ✅ **连续失败保护**: 最大重试次数限制，防止僵尸进程
- ✅ **实时监控**: 风险状态实时评估和告警
- ✅ **紧急停止**: 异常情况下的自动停止机制
- ✅ **理财功能开关**: 可选禁用理财功能，适合子账户用户

### 🌐 企业级部署
- ✅ **Docker 容器化**: 完整的 Docker Compose 部署方案
- ✅ **Nginx 反向代理**: 高性能 Web 服务和负载均衡
- ✅ **健康检查**: 自动监控和故障恢复
- ✅ **数据持久化**: 完整的状态保存和恢复机制

### 📱 现代化 Web 界面
- ✅ **实时监控**: 交易状态、收益统计、风险指标
- ✅ **多币种视图**: 支持多交易对的统一监控界面
- ✅ **基础认证**: 可选的用户名密码保护
- ✅ **响应式设计**: 支持桌面和移动设备访问

## 📋 系统要求

### 基础环境
- **Python**: 3.8+ (推荐 3.10+)
- **Docker**: 20.10+ (可选，推荐用于生产部署)
- **内存**: 最低 512MB，推荐 1GB+
- **存储**: 500MB 可用空间
- **网络**: 稳定的互联网连接，建议低延迟到币安服务器

### 推荐配置
- **CPU**: 1核心及以上
- **内存**: 512MB+ RAM
- **网络**: 亚洲地区服务器 (日本、新加坡等)
- **操作系统**: Ubuntu 20.04+, Windows 10+, macOS 10.15+

## 🚀 快速开始

### 方法一：Docker 部署 (推荐)

1. **克隆项目**
   ```bash
   git clone https://github.com/EBOLABOY/GridBNB-USDT.git
   cd GridBNB-USDT
   ```

2. **配置环境变量**
   ```bash
   # 复制并编辑配置文件
   cp .env.example .env
   # 编辑 .env 文件，填入您的 API 密钥
   ```

3. **启动服务**
   ```bash
   # Windows 用户
   start-with-nginx.bat

   # Linux/Mac 用户
   chmod +x start-with-nginx.sh
   ./start-with-nginx.sh
   ```

4. **访问 Web 界面**
   - 打开浏览器访问: http://localhost

### 方法二：Python 直接运行

1. **克隆并安装**
   ```bash
   git clone https://github.com/EBOLABOY/GridBNB-USDT.git
   cd GridBNB-USDT

   # 创建虚拟环境
   python -m venv .venv

   # 激活虚拟环境
   # Windows:
   .\.venv\Scripts\activate
   # Linux/Mac:
   source .venv/bin/activate

   # 安装依赖
   pip install -r requirements.txt
   ```

2. **配置和运行**
   ```bash
   # 配置 .env 文件
   cp .env.example .env
   # 编辑 .env 文件

   # 运行程序
   python main.py
   ```

## ⚙️ 配置说明

### 环境变量配置 (.env 文件)

创建 `.env` 文件并配置以下参数：

```bash
# ========== 必填项 (Required) ==========
# 币安 API (必须)
BINANCE_API_KEY="your_binance_api_key"
BINANCE_API_SECRET="your_binance_api_secret"

# ========== 策略核心配置 (Strategy Core) ==========
# 要运行的交易对列表，用英文逗号分隔
SYMBOLS="BNB/USDT,ETH/USDT,BTC/USDT"

# 按交易对设置初始参数 (JSON格式)
INITIAL_PARAMS_JSON='{"BNB/USDT": {"initial_base_price": 683.0, "initial_grid": 2.0}, "ETH/USDT": {"initial_base_price": 3000.0, "initial_grid": 2.5}}'

# 全局默认网格大小 (%)
INITIAL_GRID=2.0

# 最小交易金额 (USDT)
MIN_TRADE_AMOUNT=20.0

# ========== 可选配置 (Optional) ==========
# 初始本金 (用于收益计算)
INITIAL_PRINCIPAL=800

# ========== 推送通知配置 ==========
# 启用的推送提供者，用逗号分隔，按优先级排序
NOTIFICATION_PROVIDERS="pushplus,bark"

# PushPlus 通知 Token
PUSHPLUS_TOKEN="your_pushplus_token"

# Bark 推送配置 (iOS推送)
BARK_DEVICE_TOKEN="your_bark_device_token"
BARK_SERVER_URL="https://api.day.app"

# 钉钉机器人推送配置
DINGTALK_WEBHOOK_URL="https://oapi.dingtalk.com/robot/send?access_token=your_token"

# 企业微信机器人推送配置
WECHAT_WORK_WEBHOOK_URL="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your_key"

# 理财功能开关 (true/false)
# 对于子账户用户或不希望使用理财功能的用户，请设置为 false
ENABLE_SAVINGS_FUNCTION=true

# Web UI 认证 (可选)
WEB_USER=admin
WEB_PASSWORD=your_password

# 代理设置 (如需要)
HTTP_PROXY="http://127.0.0.1:7890"
```
### https配置（可选）
[https配置教程(可选)](README-https.md)

### 推送通知配置

系统支持多种推送方式，可以同时配置多个推送渠道作为备用方案：

#### 支持的推送方式

| 推送方式 | 平台 | 特点 | 配置难度 |
|---------|------|------|---------|
| **PushPlus** | 微信 | 免费、稳定、支持微信推送 | ⭐ |
| **Bark** | iOS | 原生iOS通知、支持自定义 | ⭐⭐ |
| **钉钉机器人** | 钉钉 | 企业级、群组通知 | ⭐⭐ |
| **企业微信机器人** | 企业微信 | 企业级、群组通知 | ⭐⭐ |
| **飞书机器人** | 飞书 | 企业级、支持富文本 | ⭐⭐ |
| **Telegram机器人** | Telegram | 国际化、支持Markdown | ⭐⭐⭐ |

#### 配置示例

```bash
# 启用多个推送方式（按优先级排序，支持备用方案）
NOTIFICATION_PROVIDERS="bark,pushplus,dingtalk,feishu"

# PushPlus配置（微信推送）
PUSHPLUS_TOKEN="your_pushplus_token"

# Bark配置（iOS推送）
BARK_DEVICE_TOKEN="your_bark_device_token"
BARK_SERVER_URL="https://api.day.app"

# 钉钉机器人配置
DINGTALK_WEBHOOK_URL="https://oapi.dingtalk.com/robot/send?access_token=your_token"

# 企业微信机器人配置
WECHAT_WORK_WEBHOOK_URL="https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your_key"

# 飞书机器人配置
FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/your_hook_id"

# Telegram机器人配置
TELEGRAM_BOT_TOKEN="your_bot_token"
TELEGRAM_CHAT_ID="your_chat_id"
```

#### 获取推送Token的方法

**PushPlus (推荐)**:
1. 访问 [PushPlus官网](https://www.pushplus.plus/)
2. 微信扫码登录
3. 复制Token到配置文件

**Bark (iOS用户)**:
1. App Store下载Bark应用
2. 打开应用获取设备Token
3. 复制Token到配置文件

**钉钉机器人**:
1. 钉钉群 → 群设置 → 机器人 → 添加机器人
2. 选择"自定义"机器人
3. 复制Webhook地址到配置文件

**企业微信机器人**:
1. 企业微信群 → 群设置 → 群机器人 → 添加机器人
2. 复制Webhook地址

**飞书机器人**:
1. 飞书群 → 群设置 → 群机器人 → 添加机器人
2. 选择"自定义机器人"
3. 复制 Webhook 地址

**Telegram机器人**:
1. 与 @BotFather 对话创建机器人
2. 获取 Bot Token
3. 获取聊天ID（发送消息给机器人后查看）到配置文件

#### 推送策略

- **备用方案**: 按配置顺序尝试推送，任一成功即停止
- **多渠道**: 可配置同时向所有渠道推送
- **容错机制**: 单个推送失败不影响交易执行

### 重要安全提示

⚠️ **API 密钥安全**:
- 确保 API Key 只有**现货交易**权限
- **禁用提现权限**
- 不要在公共场所或代码中暴露密钥
- 定期更换 API 密钥

### 理财功能配置

系统支持币安活期理财的自动申购/赎回功能，通过 `ENABLE_SAVINGS_FUNCTION` 开关控制：

**启用理财功能 (默认)**:
```bash
ENABLE_SAVINGS_FUNCTION=true
```
- ✅ 自动将多余资金申购到活期理财
- ✅ 资金不足时自动从理财赎回
- ✅ 最大化资金利用效率

**禁用理财功能**:
```bash
ENABLE_SAVINGS_FUNCTION=false
```
- ✅ 所有资金保留在现货账户
- ✅ 不调用任何理财相关API
- ✅ 适合子账户用户或保守用户

**适用场景**:
- 🏦 **子账户用户**: 子账户通常没有理财权限
- 🔒 **保守策略**: 不希望资金离开现货账户
- 🧪 **测试环境**: 避免意外的资金操作
- ⚙️ **完全控制**: 手动管理所有资金流向

### 高级配置

系统支持丰富的策略参数调整，主要配置在 `config.py` 中：

- **波动率阈值**: 52日年化波动率计算，支持 EWMA 混合算法
- **网格参数**: 动态网格范围 1.0% - 4.0%
- **风险管理**: 仓位比例限制、连续失败保护
- **理财精度**: 多币种精度配置

## 🌐 Web 监控界面

### 访问地址
- **Docker 部署**: http://localhost (推荐)
- **直接运行**: http://localhost:58181
- **调试端口**: http://localhost:8080

### 功能特性
- 📊 **实时监控**: 交易状态、收益统计、持仓分析
- 📈 **多币种视图**: 支持多交易对统一监控
- 📱 **响应式设计**: 支持手机和平板访问
- 🔐 **安全认证**: 可选的用户名密码保护

## � 更新和维护

### 一键更新脚本 (Ubuntu/Linux)

为已部署的Ubuntu服务器提供简单的一键更新解决方案：

```bash
# 进入项目目录
cd GridBNB-USDT

# 给脚本执行权限 (首次使用)
chmod +x update.sh

# 执行一键更新
./update.sh
```

**更新脚本功能**:
- ✅ 检测代码是否有更新
- ✅ 拉取 GitHub 最新代码
- ✅ 自动处理本地修改冲突
- ✅ 重新构建并重启 Docker 容器
- ✅ 验证服务运行状态
- ✅ 显示更新结果和访问信息

**适用场景**:
- Ubuntu/Linux 服务器环境
- 已通过 Docker 部署的系统
- 需要保持配置文件不变的更新

### 手动更新方式

如果需要手动控制更新过程：

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 重启服务
docker-compose up -d --build

# 3. 检查状态
docker-compose ps
```

**注意**: `.env` 配置文件不会被 Git 更新影响，因为它在 `.gitignore` 中被忽略。

## �📊 监控和日志

### 日志文件
- **应用日志**: `trading_system.log`
- **Nginx 日志**: `nginx/logs/access.log`, `nginx/logs/error.log`
- **Docker 日志**: `docker-compose logs -f`

### 监控命令
```bash
# 查看服务状态
docker-compose ps

# 查看实时日志
docker-compose logs -f gridbnb-bot

# 查看系统资源
docker stats
```

## 🔧 故障排除

### 常见问题

1. **Docker 相关**
   ```bash
   # 检查 Docker 状态
   docker --version
   docker-compose --version

   # 重启服务
   docker-compose restart

   # 查看错误日志
   docker-compose logs gridbnb-bot
   ```

2. **API 连接问题**
   - 检查 API 密钥是否正确
   - 确认网络连接稳定
   - 验证 API 权限设置

3. **Web 界面无法访问**
   - 检查端口是否被占用
   - 确认防火墙设置
   - 验证容器状态

### 获取帮助

- 📖 **详细文档**: 查看 `NGINX_DEPLOYMENT.md` 和 `DOCKER_INSTALLATION_GUIDE.md`
- 🐛 **问题反馈**: 提交 GitHub Issues
- 💬 **社区讨论**: GitHub Discussions

## ⚠️ 风险提示

- **投资风险**: 数字货币交易存在高风险，可能导致本金损失
- **策略风险**: 网格策略在单边行情中可能表现不佳
- **技术风险**: 程序可能存在 bug，建议小额测试
- **市场风险**: 极端市场条件下可能出现意外损失

**请在充分理解风险的前提下使用本程序，投资有风险，入市需谨慎！**

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 🙏 致谢

- [Binance API](https://binance-docs.github.io/apidocs/) - 交易所 API 支持
- [CCXT](https://github.com/ccxt/ccxt) - 统一交易所 API 库
- [Docker](https://www.docker.com/) - 容器化部署支持
- [Nginx](https://nginx.org/) - 高性能 Web 服务器

---

<div align="center">

### 🤝 联系与交流

遇到问题或有任何想法？通过以下方式加入我们的社区，我们期待你的声音！

<p>
  <a href="https://t.me/+b9fKO9kEOkg2ZjI1"><img alt="Telegram" src="https://img.shields.io/badge/Telegram-群组交流-28A8EA?style=flat-square&logo=telegram"></a>
  <a href="https://github.com/EBOLABOY/GridBNB-USDT/issues"><img alt="Issues" src="https://img.shields.io/github/issues/EBOLABOY/GridBNB-USDT?style=flat-square&logo=github&label=Issues"></a>
  </p>

</div>

<div align="center">

**⭐ 如果这个项目对您有帮助，请给个 Star！⭐**

[![Powered by DartNode](https://dartnode.com/branding/DN-Open-Source-sm.png)](https://dartnode.com "Powered by DartNode - Free VPS for Open Source")

</div>
