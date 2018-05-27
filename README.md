# crypto_auto_trading

自动化交易数字货币。

## 运行

设置火币的 key 到环境变量

```
API_KEY='API Key'
API_SECRET='Secret Key'
```

### 定时任务

* 每天运行 `python manage.py update_symbol_info` 来更新 symbol 信息