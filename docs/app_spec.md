# Property Agent Assistant — 产品需求规格说明书

## 目标摘要
为新加坡的Property Agent（中介）和房产客户提供一个双模式助手App：
- 中介用户模式：基于团队知识库，回答流程、学习资料、销售策略、销售话术等。
- 房产客户模式：购房引导、政策简介（HDB/EC/公寓/别墅/外国人购房规则）、财务规划与贷款流程。
- Admin：可配置/更新知识库。
- 支持按需访问并抓取官方站点（如 hdb.gov.sg, ura.gov.sg）。

## 功能需求
1. 用户与权限
  - 中介（agent）: 登录后可查询团队知识库、保存会话、请求销售话术模板。
  - 客户（buyer）: 可查询政策、贷款计算器、获取购房流程引导。
  - 管理员（admin）: 管理/导入/编辑知识库条目、查看使用统计。

2. 知识库（团队KB）
  - 存储结构：条目包含标题、类别、内容、标签、作者、更新时间。
  - 支持全文检索、按标签过滤、导入（JSON/CSV）。
  - Admin 能在线更新并触发索引重建。

3. 问答与检索
  - 基于检索增强生成（RAG）模式：先检索KB，再调用大模型生成答案（按需调用）。
  - 支持流式回复（Server-Sent Events），以便客户端边看边读。
  - 对于政策类问题，能自动抓取并引用官方来源（返回来源链接）。

4. 前端体验
  - 简洁、接近苹果风格的界面：清爽配色、大面积留白、明确的交互。
  - 移动优先响应式设计。
  - 模式切换（Agent / Buyer / Admin）和会话历史。

5. 性能与成本
  - 默认使用本地检索生成回答，只有在需要“深度生成”时调用付费大模型。
  - 支持配置OpenAI等模型的API key（通过环境变量或管理端配置）。

6. 安全与合规
  - 管理界面需鉴权（基于简单的Bearer token或OAuth）。
  - 对外抓取官方站点时遵守robots.txt并记录来源。

## 非功能需求
- 响应时间宜短，检索优先，生成按需。
- 界面友好、无障碍考虑（合适的对比、可访问标签）。
- 提供日志与基本使用统计。

## API 设计（高层）
- GET `/api/kb` — 列表KB条目（支持query参数搜索/标签）。
- POST `/api/kb` — Admin: 添加/更新KB。
- POST `/api/query` — 提交问题（body: {mode, query, context}），返回stream或最终答案。
- GET `/api/fetch?url=...` — 抓取目标url并返回摘要（admin或受控访问）。

## 数据模型（简化）
KBItem: {id, title, category, content, tags[], author, updated_at}

## 开发里程碑
1. 完成最小可运行后端 + 基础前端（Agent / Buyer 两个模式）
2. 增加Admin KB管理接口和前端
3. 集成真实LLM（OpenAI）与RAG
4. 测试、优化并准备部署（Vercel/Heroku/其它）

## 体验与部署
- 本地启动：uvicorn 启动FastAPI后访问 `http://<host>:8000`。
- 若部署到Vercel/平台，需创建git仓库并配置环境变量（OPENAI_API_KEY）。
