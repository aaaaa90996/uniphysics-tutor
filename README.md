# UniPhysics Tutor：本科物理数字人智能助教

本项目设计并实现一个面向本科生的物理数字人智能助教。系统调用大语言模型，并结合本地物理知识库（RAG），实现大学物理概念讲解、分步解题、误区诊断、练习题生成和交互式引导学习。

系统重点解决本科物理学习中**公式适用条件不清、物理图像薄弱、矢量和微积分建模困难**等问题。数字人形象作为交互入口，后端通过 RAG 检索、提示词约束和物理校验器提升回答的准确性与可控性。

## 系统架构

```
前端界面 (Next.js + React + TypeScript + Tailwind CSS + KaTeX)
  ↓
学生文本/语音输入
  ↓
问题分类器
  ↓
知识库检索 RAG (Chroma + text-embedding)
  ↓
大模型推理与生成 (OpenAI API / 兼容 API)
  ↓
物理答案校验器 (physics_validator)
  ↓
教学风格格式化
  ↓
TTS 语音合成 (Web Speech API / Edge TTS)
  ↓
数字人播报
```

## 项目结构

```
uniphysics-tutor/
├── frontend/                 # Next.js 前端页面
├── backend/                  # FastAPI 后端
├── prompts/                  # 提示词模板
├── knowledge_base/           # 教材、讲义、公式表
├── digital_human/            # 数字人展示模块
├── evaluation/               # 测试题与评估脚本
├── examples/                 # 演示案例
├── docker-compose.yml
└── README.md
```

## 快速开始

### 环境要求

- Node.js 18+
- Python 3.10+
- Docker & Docker Compose（可选）

### 方式一：Docker Compose（推荐）

```bash
git clone <repo-url>
cd uniphysics-tutor
cp .env.example .env
# 编辑 .env 填入 API Key
docker compose up
```

访问 http://localhost:3000

### 方式二：分别启动

#### 后端

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入 API Key
uvicorn main:app --reload --port 8000
```

#### 前端

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

访问 http://localhost:3000

## .env 配置

```env
# LLM API 配置
LLM_API_KEY=your-api-key-here
LLM_API_BASE=https://api.openai.com/v1
LLM_MODEL=gpt-4o

# Embedding 模型（用于 RAG）
EMBEDDING_MODEL=text-embedding-3-small

# TTS 配置（可选）
TTS_ENABLED=true
TTS_PROVIDER=edge-tts

# 知识库路径
KNOWLEDGE_BASE_PATH=../knowledge_base
```

## 功能模块

### 前端功能

- 数字人头像区域（SVG 动画）
- 对话输入与历史记录
- KaTeX 公式渲染
- 板书区（分步推导展示）
- 模式切换：概念讲解 / 引导解题 / 完整解题 / 误区诊断 / 生成练习
- 课程模块选择：力学 / 电磁学 / 振动与波 / 热学 / 光学

### 后端 API

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/chat` | POST | 概念讲解问答 |
| `/api/solve` | POST | 分步解题 |
| `/api/diagnose` | POST | 误区诊断 |
| `/api/exercise` | POST | 生成练习题 |
| `/api/retrieve` | POST | 知识库检索 |
| `/api/health` | GET | 健康检查 |

### 物理校验器

自动检查以下规则：

- 牛顿第二定律 → 需说明惯性系
- 动量守恒 → 需说明合外力为零
- 机械能守恒 → 需说明非保守力做功为零
- 高斯定理求电场 → 需说明对称性
- 电磁感应 → 需说明磁通量变化和方向
- 矢量运算 → 需说明方向和坐标系
- 积分运算 → 需说明积分区域和边界条件

## 如何添加知识库

在 `knowledge_base/` 目录下按课程分类创建 Markdown 文件：

```markdown
# 知识点名称

## 核心结论
...

## 数学表达
...

## 适用条件
...

## 常见误区
...

## 典型例题
...

## 教学提示
...
```

后端启动时会自动索引 `knowledge_base/` 下的所有 `.md` 文件。

## 如何运行测试

```bash
cd evaluation
pip install -r ../backend/requirements.txt
python evaluate.py
```

## 扩展数字人语音和形象

1. **TTS 语音**：修改 `backend/config.py` 中的 `TTS_PROVIDER`，支持 `edge-tts`、`openai-tts`、`azure-tts`
2. **数字人形象**：替换 `frontend/components/AvatarPanel.tsx` 中的 SVG 为 Live2D / Ready Player Me / D-ID 等方案
3. **口型同步**：引入 Rhubarb Lip Sync 或类似方案

## 首期课程范围

- 质点运动学
- 牛顿运动定律
- 功和能
- 动量与角动量
- 简谐振动
- 静电场
- 高斯定理
- 电势
- 稳恒电流
- 磁场与洛伦兹力
- 电磁感应
- 麦克斯韦方程组初步

## License

MIT
