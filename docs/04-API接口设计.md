# API接口设计文档

**文档版本**: V1.0  
**创建日期**: 2026-03-04  
**关联文档**: AI创作平台需求规格说明书.md、02-功能详细设计.md、03-数据模型设计.md

---

## 目录

1. [接口设计规范](#1-接口设计规范)
2. [公共定义](#2-公共定义)
3. [用户模块API](#3-用户模块api)
4. [创作模块API](#4-创作模块api)
5. [支付模块API](#5-支付模块api)
6. [作品模块API](#6-作品模块api)
7. [消息模块API](#7-消息模块api)
8. [用户服务API](#8-用户服务api)
9. [运营活动API](#9-运营活动api)
10. [后台管理API](#10-后台管理api)

---

## 1. 接口设计规范

### 1.1 基础URL

| 环境 | URL |
|------|-----|
| 开发环境 | http://localhost:8080/api/v1 |
| 测试环境 | https://test-api.example.com/api/v1 |
| 生产环境 | https://api.example.com/api/v1 |

### 1.2 请求规范

#### 1.2.1 HTTP方法

| 方法 | 说明 | 使用场景 |
|------|------|---------|
| GET | 获取资源 | 查询操作 |
| POST | 创建资源 | 新增操作 |
| PUT | 更新资源 | 完整更新 |
| PATCH | 更新资源 | 部分更新 |
| DELETE | 删除资源 | 删除操作 |

#### 1.2.2 请求头

| 请求头 | 必填 | 说明 |
|--------|------|------|
| Content-Type | 是 | application/json |
| Authorization | 是 | Bearer {token} |
| Accept-Language | 否 | 语言: zh-CN/en-US |
| X-Request-ID | 否 | 请求追踪ID |

#### 1.2.3 分页参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| page | int | 1 | 页码 |
| page_size | int | 20 | 每页数量(最大100) |

### 1.3 响应规范

#### 1.3.1 成功响应

```json
{
  "code": 0,
  "message": "success",
  "data": {},
  "timestamp": 1709548800000
}
```

#### 1.3.2 分页响应

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 100,
      "total_pages": 5
    }
  },
  "timestamp": 1709548800000
}
```

#### 1.3.3 错误响应

```json
{
  "code": 10001,
  "message": "参数错误",
  "errors": [
    {
      "field": "email",
      "message": "邮箱格式不正确"
    }
  ],
  "timestamp": 1709548800000
}
```

### 1.4 错误码定义

| 错误码范围 | 说明 |
|-----------|------|
| 0 | 成功 |
| 10000-19999 | 客户端错误 |
| 20000-29999 | 服务端错误 |
| 30000-39999 | 业务错误 |

#### 常用错误码

| 错误码 | 说明 |
|--------|------|
| 10001 | 参数错误 |
| 10002 | 请求格式错误 |
| 10003 | 认证失败 |
| 10004 | Token过期 |
| 10005 | 权限不足 |
| 10006 | 资源不存在 |
| 10007 | 资源已存在 |
| 20001 | 服务器内部错误 |
| 20002 | 服务不可用 |
| 30001 | 用户不存在 |
| 30002 | 密码错误 |
| 30003 | 账户已禁用 |
| 30004 | 账户已锁定 |
| 30005 | 权限未开通 |
| 30006 | 权限已过期 |
| 30007 | 余额不足 |
| 30008 | 订单已过期 |

---

## 2. 公共定义

### 2.1 用户信息结构

```json
{
  "user_id": "U20260304001",
  "email": "user@example.com",
  "phone": "138****8888",
  "nickname": "用户昵称",
  "avatar": "https://cdn.example.com/avatar.jpg",
  "status": 1,
  "id_verified": 2,
  "balance": 100.00,
  "created_at": "2026-03-04T10:00:00Z"
}
```

### 2.2 权限信息结构

```json
{
  "perm_id": "PERM_IMAGE",
  "perm_name": "图片生成权限",
  "price_model": "monthly",
  "total_count": null,
  "used_count": 15,
  "status": "active",
  "started_at": "2026-03-04T10:00:00Z",
  "expired_at": "2026-04-04T23:59:59Z"
}
```

### 2.3 脚本信息结构

```json
{
  "script_id": "S20260304001",
  "script_no": "S20260304001",
  "title": "职场女性的一天",
  "output_type": "image_set",
  "content": {
    "characters": [],
    "storyline": "",
    "clarity": "1080P",
    "size": "16:9"
  },
  "mode": "simple",
  "status": 1,
  "usage_cost": 5.0,
  "created_at": "2026-03-04T10:00:00Z"
}
```

### 2.4 作品信息结构

```json
{
  "work_id": "W20260304001",
  "work_no": "W20260304001",
  "work_type": "image",
  "title": "作品标题",
  "file_url": "https://cdn.example.com/works/xxx.jpg",
  "thumbnail_url": "https://cdn.example.com/works/xxx_thumb.jpg",
  "file_size": 1024000,
  "file_format": "jpg",
  "width": 1920,
  "height": 1080,
  "clarity": "1080P",
  "status": 1,
  "expired_at": "2026-03-19T10:00:00Z",
  "created_at": "2026-03-04T10:00:00Z"
}
```

### 2.5 任务信息结构

```json
{
  "task_id": "T20260304001",
  "task_no": "T20260304001",
  "task_type": "image",
  "status": "completed",
  "progress": 100,
  "work_id": "W20260304001",
  "created_at": "2026-03-04T10:00:00Z",
  "completed_at": "2026-03-04T10:05:00Z"
}
```

### 2.6 订单信息结构

```json
{
  "order_id": "O20260304001",
  "order_no": "O20260304001",
  "order_type": "permission",
  "items": [
    {
      "item_id": "PERM_IMAGE",
      "item_name": "图片生成权限",
      "price_model": "monthly",
      "quantity": 1,
      "unit_price": 99.00,
      "subtotal": 99.00
    }
  ],
  "total_amount": 99.00,
  "discount_amount": 0,
  "pay_amount": 99.00,
  "status": "pending",
  "payment_method": null,
  "created_at": "2026-03-04T10:00:00Z",
  "expired_at": "2026-03-04T10:30:00Z"
}
```

---

## 3. 用户模块API

### 3.1 用户注册

**POST** `/auth/register`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| register_type | string | 是 | 注册类型: email/phone |
| account | string | 是 | 邮箱/手机号 |
| password | string | 是 | 密码 |
| verify_code | string | 是 | 验证码 |
| nickname | string | 否 | 昵称 |

**请求示例:**

```json
{
  "register_type": "email",
  "account": "user@example.com",
  "password": "Password123",
  "verify_code": "123456",
  "nickname": "新用户"
}
```

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "user_id": "U20260304001",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 86400
  }
}
```

### 3.2 用户登录

**POST** `/auth/login`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| login_type | string | 是 | 登录类型: email_password/phone_password/phone_code |
| account | string | 是 | 邮箱/手机号 |
| password | string | 否 | 密码(密码登录必填) |
| verify_code | string | 否 | 验证码(验证码登录必填) |
| remember_me | boolean | 否 | 记住我，默认false |

**请求示例:**

```json
{
  "login_type": "email_password",
  "account": "user@example.com",
  "password": "Password123",
  "remember_me": false
}
```

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "user_id": "U20260304001",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 86400
  }
}
```

### 3.3 发送验证码

**POST** `/auth/verify-code`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | 是 | 类型: register/login/reset_password |
| target | string | 是 | 邮箱/手机号 |
| target_type | string | 是 | 目标类型: email/phone |

**请求示例:**

```json
{
  "type": "register",
  "target": "user@example.com",
  "target_type": "email"
}
```

**响应示例:**

```json
{
  "code": 0,
  "message": "验证码已发送"
}
```

### 3.4 找回密码

**POST** `/auth/reset-password`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| account | string | 是 | 邮箱/手机号 |
| account_type | string | 是 | 账户类型: email/phone |
| verify_code | string | 是 | 验证码 |
| new_password | string | 是 | 新密码 |

**请求示例:**

```json
{
  "account": "user@example.com",
  "account_type": "email",
  "verify_code": "123456",
  "new_password": "NewPassword123"
}
```

**响应示例:**

```json
{
  "code": 0,
  "message": "密码重置成功"
}
```

### 3.5 获取当前用户信息

**GET** `/users/me`

**请求头:**

```
Authorization: Bearer {token}
```

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "user_id": "U20260304001",
    "email": "user@example.com",
    "phone": "138****8888",
    "nickname": "用户昵称",
    "avatar": "https://cdn.example.com/avatar.jpg",
    "gender": 1,
    "bio": "个人简介",
    "status": 1,
    "id_verified": 2,
    "balance": 100.00,
    "created_at": "2026-03-04T10:00:00Z"
  }
}
```

### 3.6 更新用户信息

**PUT** `/users/me`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| nickname | string | 否 | 昵称 |
| avatar | string | 否 | 头像URL |
| gender | int | 否 | 性别 |
| bio | string | 否 | 个人简介 |

**请求示例:**

```json
{
  "nickname": "新昵称",
  "bio": "新的个人简介"
}
```

**响应示例:**

```json
{
  "code": 0,
  "message": "更新成功"
}
```

### 3.7 修改密码

**PUT** `/users/me/password`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| old_password | string | 是 | 原密码 |
| new_password | string | 是 | 新密码 |

**请求示例:**

```json
{
  "old_password": "OldPassword123",
  "new_password": "NewPassword123"
}
```

**响应示例:**

```json
{
  "code": 0,
  "message": "密码修改成功"
}
```

### 3.8 实名认证

**POST** `/users/me/verify`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| real_name | string | 是 | 真实姓名 |
| id_card | string | 是 | 身份证号 |

**请求示例:**

```json
{
  "real_name": "张三",
  "id_card": "110101199001011234"
}
```

**响应示例:**

```json
{
  "code": 0,
  "message": "认证成功",
  "data": {
    "id_verified": 2
  }
}
```

### 3.9 获取用户权限列表

**GET** `/users/me/permissions`

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "permissions": [
      {
        "perm_id": "PERM_SCRIPT",
        "perm_name": "文字生成脚本权限",
        "price_model": "count",
        "total_count": 100,
        "used_count": 20,
        "status": "active",
        "expired_at": null
      },
      {
        "perm_id": "PERM_IMAGE",
        "perm_name": "图片生成权限",
        "price_model": "monthly",
        "total_count": null,
        "used_count": 15,
        "status": "active",
        "expired_at": "2026-04-04T23:59:59Z"
      }
    ]
  }
}
```

### 3.10 获取登录历史

**GET** `/users/me/login-logs`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "login_type": "email_password",
        "login_ip": "192.168.1.1",
        "login_device": "Chrome/Windows",
        "login_location": "北京市",
        "login_status": 1,
        "created_at": "2026-03-04T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 10,
      "total_pages": 1
    }
  }
}
```

---

## 4. 创作模块API

### 4.1 简化模式生成脚本

**POST** `/scripts/generate/simple`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| keywords | array | 是 | 关键字列表(1-5个) |
| output_type | string | 是 | 输出类型: image_set/single_image/video |

**请求示例:**

```json
{
  "keywords": ["职场", "女性", "励志"],
  "output_type": "image_set"
}
```

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "questions": [
      {
        "question_id": "Q001",
        "question": "请描述主要人物角色的形象特征",
        "required": true,
        "type": "text"
      },
      {
        "question_id": "Q002",
        "question": "请描述故事的主要情节线",
        "required": true,
        "type": "text"
      },
      {
        "question_id": "Q003",
        "question": "请选择期望的图片清晰度",
        "required": true,
        "type": "select",
        "options": ["720P", "1080P", "4K"]
      }
    ],
    "session_id": "SESSION20260304001"
  }
}
```

### 4.2 提交简化模式答案

**POST** `/scripts/generate/simple/submit`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| session_id | string | 是 | 会话ID |
| answers | array | 是 | 答案列表 |

**请求示例:**

```json
{
  "session_id": "SESSION20260304001",
  "answers": [
    {
      "question_id": "Q001",
      "answer": "25岁女性，职业装，干练形象"
    },
    {
      "question_id": "Q002",
      "answer": "职场女性的一天工作生活"
    },
    {
      "question_id": "Q003",
      "answer": "1080P"
    }
  ]
}
```

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "script_id": "S20260304001",
    "script_no": "S20260304001",
    "title": "职场女性的一天",
    "output_type": "image_set",
    "content": {
      "characters": [
        {
          "name": "主角",
          "description": "25岁女性，职业装，干练形象"
        }
      ],
      "storyline": "职场女性的一天工作生活",
      "clarity": "1080P",
      "size": "16:9"
    },
    "usage_cost": 5.0
  }
}
```

### 4.3 完整模式生成脚本

**POST** `/scripts/generate/full`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| output_type | string | 是 | 输出类型: image_set/single_image/video |
| content | object | 是 | 脚本内容 |

**请求示例:**

```json
{
  "output_type": "image_set",
  "content": {
    "characters": [
      {
        "name": "主角",
        "description": "25岁女性，职业装，干练形象",
        "appearance": "长发，戴眼镜"
      }
    ],
    "storyline": "职场女性的一天工作生活",
    "clarity": "1080P",
    "size": "16:9",
    "scenes": [
      {
        "description": "早晨进入办公室",
        "mood": "积极向上"
      }
    ]
  }
}
```

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "script_id": "S20260304001",
    "script_no": "S20260304001",
    "title": "职场女性的一天",
    "output_type": "image_set",
    "content": {},
    "usage_cost": 5.0
  }
}
```

### 4.4 获取脚本列表

**GET** `/scripts`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| output_type | string | 否 | 输出类型筛选 |
| status | int | 否 | 状态筛选 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "script_id": "S20260304001",
        "script_no": "S20260304001",
        "title": "职场女性的一天",
        "output_type": "image_set",
        "status": 1,
        "created_at": "2026-03-04T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 10,
      "total_pages": 1
    }
  }
}
```

### 4.5 获取脚本详情

**GET** `/scripts/{script_id}`

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "script_id": "S20260304001",
    "script_no": "S20260304001",
    "title": "职场女性的一天",
    "output_type": "image_set",
    "content": {
      "characters": [],
      "storyline": "",
      "clarity": "1080P",
      "size": "16:9"
    },
    "mode": "simple",
    "status": 1,
    "usage_cost": 5.0,
    "created_at": "2026-03-04T10:00:00Z"
  }
}
```

### 4.6 更新脚本

**PUT** `/scripts/{script_id}`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| title | string | 否 | 标题 |
| content | object | 否 | 内容 |

**请求示例:**

```json
{
  "title": "职场女性的一天(修改版)",
  "content": {
    "storyline": "修改后的故事线"
  }
}
```

**响应示例:**

```json
{
  "code": 0,
  "message": "更新成功"
}
```

### 4.7 删除脚本

**DELETE** `/scripts/{script_id}`

**响应示例:**

```json
{
  "code": 0,
  "message": "删除成功"
}
```

### 4.8 生成图片(脚本驱动)

**POST** `/images/generate`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| script_id | string | 是 | 脚本ID |
| generate_count | int | 否 | 生成数量，默认1 |

**请求示例:**

```json
{
  "script_id": "S20260304001",
  "generate_count": 1
}
```

**响应示例:**

```json
{
  "code": 0,
  "message": "任务已提交",
  "data": {
    "task_id": "T20260304001",
    "task_no": "T20260304001",
    "status": "pending"
  }
}
```

### 4.9 生成图片(参考图驱动)

**POST** `/images/generate/reference`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| reference_image | file | 是 | 参考图片文件 |
| description | string | 是 | 生成要求描述 |
| clarity | string | 是 | 清晰度 |
| size | string | 是 | 尺寸 |
| similarity | float | 否 | 相似度(0-1) |

**请求示例:**

```
Content-Type: multipart/form-data

reference_image: [文件]
description: "生成一张风格相似的商业图片"
clarity: "1080P"
size: "16:9"
similarity: 0.7
```

**响应示例:**

```json
{
  "code": 0,
  "message": "任务已提交",
  "data": {
    "task_id": "T20260304001",
    "task_no": "T20260304001",
    "status": "pending"
  }
}
```

### 4.10 图片二次编辑

**POST** `/images/{work_id}/edit`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| edit_type | string | 是 | 编辑类型: modify/enhance/style_transfer/extend |
| edit_instruction | string | 是 | 编辑指令 |

**请求示例:**

```json
{
  "edit_type": "modify",
  "edit_instruction": "将背景改为城市夜景"
}
```

**响应示例:**

```json
{
  "code": 0,
  "message": "任务已提交",
  "data": {
    "task_id": "T20260304002",
    "task_no": "T20260304002",
    "status": "pending"
  }
}
```

### 4.11 生成视频

**POST** `/videos/generate`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| script_id | string | 是 | 脚本ID |
| duration | int | 是 | 时长(秒) |
| clarity | string | 是 | 清晰度 |
| style | string | 否 | 视频风格 |

**请求示例:**

```json
{
  "script_id": "S20260304001",
  "duration": 30,
  "clarity": "1080P",
  "style": "商务风格"
}
```

**响应示例:**

```json
{
  "code": 0,
  "message": "任务已提交",
  "data": {
    "task_id": "T20260304001",
    "task_no": "T20260304001",
    "status": "pending"
  }
}
```

### 4.12 视频二次编辑

**POST** `/videos/{work_id}/edit`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| edit_type | string | 是 | 编辑类型 |
| edit_instruction | string | 是 | 编辑指令 |

**请求示例:**

```json
{
  "edit_type": "modify",
  "edit_instruction": "添加背景音乐"
}
```

**响应示例:**

```json
{
  "code": 0,
  "message": "任务已提交",
  "data": {
    "task_id": "T20260304002",
    "task_no": "T20260304002",
    "status": "pending"
  }
}
```

### 4.13 生成广告(脚本驱动)

**POST** `/ads/generate`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| script_id | string | 是 | 脚本ID |
| ad_type | string | 是 | 广告类型: image/video |
| platform | string | 否 | 投放平台 |
| aspect_ratio | string | 否 | 宽高比 |

**请求示例:**

```json
{
  "script_id": "S20260304001",
  "ad_type": "image",
  "platform": "wechat",
  "aspect_ratio": "16:9"
}
```

**响应示例:**

```json
{
  "code": 0,
  "message": "任务已提交",
  "data": {
    "task_id": "T20260304001",
    "task_no": "T20260304001",
    "status": "pending"
  }
}
```

### 4.14 生成广告(素材组合)

**POST** `/ads/generate/compose`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| materials | array | 是 | 素材文件列表 |
| description | string | 是 | 广告需求描述 |
| ad_type | string | 是 | 广告类型 |
| platform | string | 否 | 投放平台 |

**请求示例:**

```
Content-Type: multipart/form-data

materials: [文件1, 文件2]
description: "组合生成一个电商促销广告"
ad_type: "image"
platform: "douyin"
```

**响应示例:**

```json
{
  "code": 0,
  "message": "任务已提交",
  "data": {
    "task_id": "T20260304001",
    "task_no": "T20260304001",
    "status": "pending"
  }
}
```

---

## 5. 支付模块API

### 5.1 获取功能价格

**GET** `/prices`

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "features": [
      {
        "feature_id": "PERM_SCRIPT",
        "feature_name": "文字生成脚本",
        "prices": {
          "count": 1,
          "monthly": 29,
          "yearly": 199
        },
        "unit": "次"
      },
      {
        "feature_id": "PERM_IMAGE",
        "feature_name": "图片生成",
        "prices": {
          "count": 3,
          "monthly": 99,
          "yearly": 699
        },
        "unit": "次"
      }
    ]
  }
}
```

### 5.2 创建订单

**POST** `/orders`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| order_type | string | 是 | 订单类型: permission/recharge |
| items | array | 是 | 订单项列表 |
| coupon_id | string | 否 | 优惠券ID |
| discount_code | string | 否 | 折扣码 |

**请求示例:**

```json
{
  "order_type": "permission",
  "items": [
    {
      "item_id": "PERM_IMAGE",
      "price_model": "monthly",
      "quantity": 1
    }
  ],
  "coupon_id": null,
  "discount_code": null
}
```

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "order_id": "O20260304001",
    "order_no": "O20260304001",
    "total_amount": 99.00,
    "discount_amount": 0,
    "pay_amount": 99.00,
    "status": "pending",
    "expired_at": "2026-03-04T10:30:00Z"
  }
}
```

### 5.3 获取订单列表

**GET** `/orders`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| status | string | 否 | 状态筛选 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "order_id": "O20260304001",
        "order_no": "O20260304001",
        "order_type": "permission",
        "total_amount": 99.00,
        "status": "paid",
        "created_at": "2026-03-04T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 10,
      "total_pages": 1
    }
  }
}
```

### 5.4 获取订单详情

**GET** `/orders/{order_id}`

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "order_id": "O20260304001",
    "order_no": "O20260304001",
    "order_type": "permission",
    "items": [
      {
        "item_id": "PERM_IMAGE",
        "item_name": "图片生成权限",
        "price_model": "monthly",
        "quantity": 1,
        "unit_price": 99.00,
        "subtotal": 99.00
      }
    ],
    "total_amount": 99.00,
    "discount_amount": 0,
    "pay_amount": 99.00,
    "status": "paid",
    "payment_method": "wechat",
    "paid_at": "2026-03-04T10:05:00Z",
    "created_at": "2026-03-04T10:00:00Z"
  }
}
```

### 5.5 发起支付

**POST** `/orders/{order_id}/pay`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| payment_method | string | 是 | 支付方式: wechat/alipay/unionpay/balance |

**请求示例:**

```json
{
  "payment_method": "wechat"
}
```

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "payment_no": "P20260304001",
    "qr_code_url": "weixin://wxpay/bizpayurl?...",
    "deep_link": "weixin://...",
    "expired_at": "2026-03-04T10:30:00Z"
  }
}
```

### 5.6 查询支付状态

**GET** `/orders/{order_id}/payment-status`

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "order_id": "O20260304001",
    "status": "paid",
    "paid_at": "2026-03-04T10:05:00Z"
  }
}
```

### 5.7 取消订单

**POST** `/orders/{order_id}/cancel`

**响应示例:**

```json
{
  "code": 0,
  "message": "订单已取消"
}
```

### 5.8 余额充值

**POST** `/balance/recharge`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| amount | decimal | 是 | 充值金额 |
| payment_method | string | 是 | 支付方式 |

**请求示例:**

```json
{
  "amount": 100.00,
  "payment_method": "wechat"
}
```

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "order_id": "O20260304001",
    "payment_no": "P20260304001",
    "qr_code_url": "weixin://wxpay/bizpayurl?..."
  }
}
```

### 5.9 获取余额流水

**GET** `/balance/transactions`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | 否 | 类型筛选 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "balance": 100.00,
    "list": [
      {
        "transaction_no": "BT20260304001",
        "type": "recharge",
        "amount": 100.00,
        "balance_before": 0,
        "balance_after": 100.00,
        "remark": "余额充值",
        "created_at": "2026-03-04T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 10,
      "total_pages": 1
    }
  }
}
```

### 5.10 申请发票

**POST** `/invoices`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| invoice_type | string | 是 | 发票类型: normal/special |
| invoice_title | string | 是 | 发票抬头 |
| tax_no | string | 是 | 税号 |
| order_ids | array | 是 | 关联订单ID列表 |
| delivery_type | string | 是 | 交付方式: electronic/paper |
| delivery_address | object | 否 | 邮寄地址(纸质发票必填) |

**请求示例:**

```json
{
  "invoice_type": "normal",
  "invoice_title": "个人",
  "tax_no": "",
  "order_ids": ["O20260304001"],
  "delivery_type": "electronic"
}
```

**响应示例:**

```json
{
  "code": 0,
  "message": "申请已提交",
  "data": {
    "invoice_id": "I20260304001",
    "invoice_no": "I20260304001",
    "status": "pending"
  }
}
```

### 5.11 获取发票列表

**GET** `/invoices`

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "invoice_id": "I20260304001",
        "invoice_no": "I20260304001",
        "invoice_type": "normal",
        "invoice_title": "个人",
        "total_amount": 99.00,
        "status": "completed",
        "file_url": "https://cdn.example.com/invoice.pdf",
        "created_at": "2026-03-04T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 5,
      "total_pages": 1
    }
  }
}
```

---

## 6. 作品模块API

### 6.1 获取创作历史

**GET** `/works`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| work_type | string | 否 | 作品类型筛选 |
| status | int | 否 | 状态筛选 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "work_id": "W20260304001",
        "work_no": "W20260304001",
        "work_type": "image",
        "title": "职场女性",
        "thumbnail_url": "https://cdn.example.com/thumb.jpg",
        "status": 1,
        "expired_at": "2026-03-19T10:00:00Z",
        "created_at": "2026-03-04T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 10,
      "total_pages": 1
    }
  }
}
```

### 6.2 获取作品详情

**GET** `/works/{work_id}`

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "work_id": "W20260304001",
    "work_no": "W20260304001",
    "work_type": "image",
    "title": "职场女性",
    "description": "职场女性的一天",
    "file_url": "https://cdn.example.com/work.jpg",
    "thumbnail_url": "https://cdn.example.com/thumb.jpg",
    "file_size": 1024000,
    "file_format": "jpg",
    "width": 1920,
    "height": 1080,
    "clarity": "1080P",
    "status": 1,
    "script_id": "S20260304001",
    "expired_at": "2026-03-19T10:00:00Z",
    "created_at": "2026-03-04T10:00:00Z"
  }
}
```

### 6.3 下载作品

**GET** `/works/{work_id}/download`

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "download_url": "https://cdn.example.com/download/work.jpg?token=xxx",
    "expires_in": 300
  }
}
```

### 6.4 删除作品

**DELETE** `/works/{work_id}`

**响应示例:**

```json
{
  "code": 0,
  "message": "删除成功"
}
```

### 6.5 获取任务列表

**GET** `/tasks`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| status | string | 否 | 状态筛选 |
| task_type | string | 否 | 任务类型筛选 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "task_id": "T20260304001",
        "task_no": "T20260304001",
        "task_type": "image",
        "status": "completed",
        "progress": 100,
        "work_id": "W20260304001",
        "created_at": "2026-03-04T10:00:00Z",
        "completed_at": "2026-03-04T10:05:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 10,
      "total_pages": 1
    }
  }
}
```

### 6.6 获取任务详情

**GET** `/tasks/{task_id}`

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "task_id": "T20260304001",
    "task_no": "T20260304001",
    "task_type": "image",
    "status": "completed",
    "progress": 100,
    "work_id": "W20260304001",
    "error_message": null,
    "created_at": "2026-03-04T10:00:00Z",
    "started_at": "2026-03-04T10:00:30Z",
    "completed_at": "2026-03-04T10:05:00Z"
  }
}
```

### 6.7 获取公开作品集

**GET** `/gallery`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| work_type | string | 否 | 作品类型筛选 |
| style | string | 否 | 风格筛选 |
| industry | string | 否 | 行业筛选 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "work_id": "W20260304001",
        "work_type": "image",
        "title": "优秀作品",
        "thumbnail_url": "https://cdn.example.com/thumb.jpg",
        "style": "商务",
        "industry": "金融",
        "view_count": 100,
        "created_at": "2026-03-04T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 100,
      "total_pages": 5
    }
  }
}
```

### 6.8 获取作品集分类

**GET** `/gallery/categories`

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "work_types": ["image", "video", "ad"],
    "styles": ["商务", "创意", "简约", "时尚"],
    "industries": ["电商", "教育", "金融", "餐饮"]
  }
}
```

---

## 7. 消息模块API

### 7.1 获取消息列表

**GET** `/messages`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | 否 | 消息类型筛选 |
| is_read | int | 否 | 是否已读筛选 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "unread_count": 5,
    "list": [
      {
        "message_id": "M20260304001",
        "type": "task_complete",
        "title": "图片生成完成",
        "content": "您的图片生成任务已完成",
        "link": "/works/W20260304001",
        "is_read": 0,
        "created_at": "2026-03-04T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 20,
      "total_pages": 1
    }
  }
}
```

### 7.2 标记消息已读

**PUT** `/messages/{message_id}/read`

**响应示例:**

```json
{
  "code": 0,
  "message": "已标记为已读"
}
```

### 7.3 批量标记已读

**PUT** `/messages/read-all`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | 否 | 消息类型(不传则全部) |

**响应示例:**

```json
{
  "code": 0,
  "message": "已全部标记为已读"
}
```

### 7.4 删除消息

**DELETE** `/messages/{message_id}`

**响应示例:**

```json
{
  "code": 0,
  "message": "删除成功"
}
```

### 7.5 获取系统公告列表

**GET** `/announcements`

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "title": "系统升级公告",
        "content": "系统将于...",
        "type": "notice",
        "is_top": 1,
        "published_at": "2026-03-04T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 5,
      "total_pages": 1
    }
  }
}
```

### 7.6 获取公告详情

**GET** `/announcements/{id}`

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "title": "系统升级公告",
    "content": "系统将于...",
    "type": "notice",
    "is_top": 1,
    "published_at": "2026-03-04T10:00:00Z"
  }
}
```

---

## 8. 用户服务API

### 8.1 获取帮助文章列表

**GET** `/help/articles`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| category | string | 否 | 分类筛选 |
| keyword | string | 否 | 关键字搜索 |

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "id": 1,
        "category": "guide",
        "title": "如何使用图片生成功能",
        "view_count": 100
      }
    ]
  }
}
```

### 8.2 获取帮助文章详情

**GET** `/help/articles/{id}`

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "category": "guide",
    "title": "如何使用图片生成功能",
    "content": "文章内容...",
    "view_count": 101
  }
}
```

### 8.3 提交工单

**POST** `/tickets`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | 是 | 工单类型 |
| title | string | 是 | 标题 |
| content | string | 是 | 内容 |
| attachments | array | 否 | 附件列表 |

**请求示例:**

```json
{
  "type": "function",
  "title": "图片生成失败",
  "content": "我在使用图片生成功能时遇到了问题...",
  "attachments": ["https://cdn.example.com/screenshot.jpg"]
}
```

**响应示例:**

```json
{
  "code": 0,
  "message": "提交成功",
  "data": {
    "ticket_id": "TK20260304001",
    "ticket_no": "TK20260304001",
    "status": "pending"
  }
}
```

### 8.4 获取工单列表

**GET** `/tickets`

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "ticket_id": "TK20260304001",
        "ticket_no": "TK20260304001",
        "type": "function",
        "title": "图片生成失败",
        "status": "resolved",
        "created_at": "2026-03-04T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 5,
      "total_pages": 1
    }
  }
}
```

### 8.5 获取工单详情

**GET** `/tickets/{ticket_id}`

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "ticket_id": "TK20260304001",
    "ticket_no": "TK20260304001",
    "type": "function",
    "title": "图片生成失败",
    "content": "问题描述...",
    "status": "resolved",
    "replies": [
      {
        "reply_id": 1,
        "user_type": "admin",
        "content": "您好，问题已解决...",
        "created_at": "2026-03-04T11:00:00Z"
      }
    ],
    "created_at": "2026-03-04T10:00:00Z"
  }
}
```

### 8.6 回复工单

**POST** `/tickets/{ticket_id}/reply`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| content | string | 是 | 回复内容 |
| attachments | array | 否 | 附件列表 |

**响应示例:**

```json
{
  "code": 0,
  "message": "回复成功"
}
```

### 8.7 提交反馈

**POST** `/feedbacks`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | 是 | 反馈类型: bug/suggestion/other |
| content | string | 是 | 反馈内容 |
| screenshots | array | 否 | 截图列表 |

**请求示例:**

```json
{
  "type": "suggestion",
  "content": "建议增加批量下载功能",
  "screenshots": []
}
```

**响应示例:**

```json
{
  "code": 0,
  "message": "感谢您的反馈"
}
```

---

## 9. 运营活动API

### 9.1 获取邀请信息

**GET** `/invitations/info`

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "invite_code": "ABC123",
    "invite_link": "https://example.com/register?code=ABC123",
    "invite_count": 5,
    "reward_amount": 50.00,
    "rules": [
      {
        "count": 1,
        "reward": "10元余额"
      },
      {
        "count": 5,
        "reward": "50元余额 + 10次图片生成"
      }
    ]
  }
}
```

### 9.2 获取邀请记录

**GET** `/invitations/records`

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "invitee_id": "U20260304002",
        "invitee_nickname": "好友1",
        "reward_amount": 10.00,
        "reward_status": 1,
        "created_at": "2026-03-04T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 5,
      "total_pages": 1
    }
  }
}
```

### 9.3 获取我的优惠券

**GET** `/coupons`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| status | string | 否 | 状态筛选: unused/used/expired |

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "user_coupon_id": 1,
        "coupon_id": 1,
        "coupon_name": "新用户专享券",
        "type": "full_reduction",
        "discount_amount": 20.00,
        "min_amount": 99.00,
        "status": "unused",
        "expired_at": "2026-04-04T23:59:59Z"
      }
    ]
  }
}
```

### 9.4 验证折扣码

**POST** `/discount-codes/validate`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | string | 是 | 折扣码 |

**请求示例:**

```json
{
  "code": "DISCOUNT2026"
}
```

**响应示例:**

```json
{
  "code": 0,
  "message": "折扣码有效",
  "data": {
    "code": "DISCOUNT2026",
    "name": "限时折扣",
    "type": "discount",
    "discount_rate": 0.8,
    "discount_amount": null,
    "expired_at": "2026-04-04T23:59:59Z"
  }
}
```

---

## 10. 后台管理API

### 10.1 管理员登录

**POST** `/admin/auth/login`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| email | string | 是 | 邮箱 |
| password | string | 是 | 密码 |
| verify_code | string | 是 | 邮箱验证码 |

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "admin_id": "A001",
    "name": "管理员",
    "role": "super_admin",
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 28800
  }
}
```

### 10.2 获取用户列表

**GET** `/admin/users`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| status | int | 否 | 状态筛选 |
| keyword | string | 否 | 关键字搜索 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "user_id": "U20260304001",
        "email": "user@example.com",
        "phone": "138****8888",
        "nickname": "用户昵称",
        "status": 1,
        "id_verified": 2,
        "balance": 100.00,
        "created_at": "2026-03-04T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 1000,
      "total_pages": 50
    }
  }
}
```

### 10.3 获取用户详情

**GET** `/admin/users/{user_id}`

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "user_id": "U20260304001",
    "email": "user@example.com",
    "phone": "13888888888",
    "nickname": "用户昵称",
    "avatar": "https://cdn.example.com/avatar.jpg",
    "status": 1,
    "id_verified": 2,
    "balance": 100.00,
    "permissions": [
      {
        "perm_id": "PERM_IMAGE",
        "perm_name": "图片生成权限",
        "price_model": "monthly",
        "status": "active",
        "expired_at": "2026-04-04T23:59:59Z"
      }
    ],
    "order_count": 5,
    "work_count": 20,
    "created_at": "2026-03-04T10:00:00Z"
  }
}
```

### 10.4 更新用户状态

**PUT** `/admin/users/{user_id}/status`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| status | int | 是 | 状态: 0禁用 1正常 |
| reason | string | 否 | 原因 |

**请求示例:**

```json
{
  "status": 0,
  "reason": "违规操作"
}
```

**响应示例:**

```json
{
  "code": 0,
  "message": "更新成功"
}
```

### 10.5 获取订单列表

**GET** `/admin/orders`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| status | string | 否 | 状态筛选 |
| order_type | string | 否 | 订单类型筛选 |
| keyword | string | 否 | 关键字搜索 |
| start_date | string | 否 | 开始日期 |
| end_date | string | 否 | 结束日期 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "order_id": "O20260304001",
        "order_no": "O20260304001",
        "user_id": "U20260304001",
        "user_nickname": "用户昵称",
        "order_type": "permission",
        "total_amount": 99.00,
        "status": "paid",
        "payment_method": "wechat",
        "created_at": "2026-03-04T10:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 500,
      "total_pages": 25
    }
  }
}
```

### 10.6 获取数据统计

**GET** `/admin/statistics`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| start_date | string | 是 | 开始日期 |
| end_date | string | 是 | 结束日期 |

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "user": {
      "new_users": 100,
      "active_users": 50,
      "paid_users": 20,
      "retention_rate": {
        "day1": 0.8,
        "day7": 0.5,
        "day30": 0.3
      }
    },
    "revenue": {
      "total": 10000.00,
      "by_feature": {
        "script": 1000.00,
        "image": 5000.00,
        "video": 3000.00,
        "ad": 1000.00
      },
      "by_model": {
        "count": 3000.00,
        "monthly": 5000.00,
        "yearly": 2000.00
      }
    },
    "usage": {
      "script_count": 500,
      "image_count": 300,
      "video_count": 100,
      "ad_count": 50,
      "success_rate": 0.98,
      "avg_duration": 30
    }
  }
}
```

### 10.7 获取功能开关配置

**GET** `/admin/configs/features`

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "features": [
      {
        "key": "feature_script_enabled",
        "name": "文字生成功能",
        "value": true
      },
      {
        "key": "feature_image_enabled",
        "name": "图片生成功能",
        "value": true
      },
      {
        "key": "feature_video_enabled",
        "name": "视频生成功能",
        "value": true
      },
      {
        "key": "feature_ad_enabled",
        "name": "广告设计功能",
        "value": true
      }
    ]
  }
}
```

### 10.8 更新功能开关

**PUT** `/admin/configs/features`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| features | array | 是 | 功能配置列表 |

**请求示例:**

```json
{
  "features": [
    {
      "key": "feature_script_enabled",
      "value": true
    }
  ]
}
```

**响应示例:**

```json
{
  "code": 0,
  "message": "更新成功"
}
```

### 10.9 获取价格配置

**GET** `/admin/configs/prices`

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "prices": [
      {
        "feature_id": "PERM_SCRIPT",
        "feature_name": "文字生成脚本",
        "count_price": 1,
        "monthly_price": 29,
        "yearly_price": 199
      },
      {
        "feature_id": "PERM_IMAGE",
        "feature_name": "图片生成",
        "count_price": 3,
        "monthly_price": 99,
        "yearly_price": 699
      }
    ],
    "weights": {
      "clarity_720p": 1.0,
      "clarity_1080p": 1.5,
      "clarity_4k": 2.5
    }
  }
}
```

### 10.10 更新价格配置

**PUT** `/admin/configs/prices`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| prices | array | 否 | 价格配置 |
| weights | object | 否 | 权重配置 |

**请求示例:**

```json
{
  "prices": [
    {
      "feature_id": "PERM_IMAGE",
      "count_price": 5,
      "monthly_price": 129,
      "yearly_price": 899
    }
  ],
  "weights": {
    "clarity_4k": 3.0
  }
}
```

**响应示例:**

```json
{
  "code": 0,
  "message": "更新成功"
}
```

### 10.11 获取管理员列表

**GET** `/admin/admins`

**响应示例:**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [
      {
        "admin_id": "A001",
        "email": "admin@example.com",
        "name": "超级管理员",
        "role": "super_admin",
        "status": 1,
        "last_login_at": "2026-03-04T10:00:00Z",
        "created_at": "2026-01-01T00:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 5,
      "total_pages": 1
    }
  }
}
```

### 10.12 创建管理员

**POST** `/admin/admins`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| email | string | 是 | 邮箱 |
| password | string | 是 | 密码 |
| name | string | 是 | 姓名 |
| role | string | 是 | 角色: super_admin/admin |

**请求示例:**

```json
{
  "email": "newadmin@example.com",
  "password": "Password123",
  "name": "新管理员",
  "role": "admin"
}
```

**响应示例:**

```json
{
  "code": 0,
  "message": "创建成功",
  "data": {
    "admin_id": "A002"
  }
}
```

### 10.13 更新管理员

**PUT** `/admin/admins/{admin_id}`

**请求参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 否 | 姓名 |
| role | string | 否 | 角色 |
| status | int | 否 | 状态 |

**响应示例:**

```json
{
  "code": 0,
  "message": "更新成功"
}
```

### 10.14 删除管理员

**DELETE** `/admin/admins/{admin_id}`

**响应示例:**

```json
{
  "code": 0,
  "message": "删除成功"
}
```

---

## 文档结束

**备注**: 本文档基于需求规格说明书编写，后续如有变更需更新文档版本。
