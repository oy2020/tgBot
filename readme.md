# AI 算命大师聊天机器人

这是一个基于 FastAPI 和 LangChain 开发的智能算命大师聊天机器人系统。该系统模拟了一个有趣的算命先生角色，能够与用户进行自然对话，并提供算命、解梦等服务。

## 技术架构 
![技术架构](https://github.com/oy2020/tgBot/blob/main/%E6%8A%80%E6%9C%AF%E6%9E%B6%E6%9E%84%E5%9B%BE/%E9%A1%B9%E7%9B%AE%E6%9E%B6%E6%9E%84.jpg)

## 实时效果
![实时效果](https://github.com/oy2020/tgBot/blob/main/%E6%8A%80%E6%9C%AF%E6%9E%B6%E6%9E%84%E5%9B%BE/%E5%AE%9E%E6%97%B6%E6%95%88%E6%9E%9C.png)

## 主要功能

1. **情感智能对话**
   - 能够识别用户情绪（开心、愤怒、沮丧等）
   - 根据用户情绪动态调整回复语气
   - 保持角色设定的一致性（60岁算命先生形象）

2. **专业服务**
   - 八字测算
   - 周公解梦
   - 运势分析
   - 知识库查询

3. **多渠道接入**
   - REST API 接口
   - WebSocket 实时通信
   - Telegram 机器人集成

4. **知识库管理**
   - 支持添加网页内容到知识库
   - 支持向量数据库存储和检索
   - 文档自动分段处理

5. **对话记忆功能**
   - Redis 持久化存储对话历史
   - 智能对话摘要生成
   - 长期记忆用户信息

## 技术架构

- **后端框架**: FastAPI
- **AI 模型**: OpenAI GPT-3.5
- **向量数据库**: Qdrant
- **缓存数据库**: Redis
- **对话引擎**: LangChain
- **消息推送**: Telegram Bot API

## 系统要求

- Python 3.8+
- Redis 服务器
- OpenAI API 密钥
- SerpAPI 密钥（用于搜索功能）
- Telegram Bot Token（如需使用 Telegram 功能）

## 安装依赖
    pip install -r requirements.txt

## 启动服务
    redis-server
    python server.py
    python tele.py


## 注意事项

1. 请确保 Redis 服务器正在运行
2. 需要正确配置所有 API 密钥
3. 向量数据库路径需要根据实际情况调整
4. 建议在生产环境中保护好 API 密钥等敏感信息

## 未来计划

- [ ] 添加更多算命相关功能
- [ ] 优化情绪识别准确度
- [ ] 增加用户管理系统
- [ ] 支持更多聊天平台集成
- [ ] 添加管理后台界面

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。

## 许可证

[待补充]
