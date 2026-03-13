
import { Hono } from "hono";
import { cors } from "hono/cors";
import { SignJWT, jwtVerify } from "jose";

type Bindings = {
  DB: D1Database;
  ASSETS: R2Bucket;
  TASK_QUEUE: Queue;
  API_PREFIX?: string;
  SECRET_KEY?: string;
  JWT_SECRET?: string;
  OPENAI_API_KEY?: string;
  OPENAI_API_BASE?: string;
  OPENAI_MODEL?: string;
  OPENAI_API_WIRE?: string;
  OPENAI_REASONING_EFFORT?: string;
  OPENAI_DISABLE_RESPONSE_STORAGE?: string;
  DEEPSEEK_API_KEY?: string;
  DEEPSEEK_API_BASE?: string;
  DEEPSEEK_MODEL?: string;
  STABILITY_API_KEY?: string;
  STABILITY_API_BASE?: string;
  STABILITY_ENGINE?: string;
  RUNWAY_API_KEY?: string;
  RUNWAY_API_BASE?: string;
  ASSET_PUBLIC_BASE?: string;
  ADMIN_INIT_USERNAME?: string;
  ADMIN_INIT_PASSWORD?: string;
  ADMIN_INIT_EMAIL?: string;
  ADMIN_INIT_NICKNAME?: string;
};

type Env = Bindings;

type User = {
  id: number;
  email?: string | null;
  phone?: string | null;
  nickname: string;
  avatar?: string | null;
  balance: number;
  status: number;
  created_at: string;
};

type PermissionRow = {
  id: number;
  user_id: number;
  permission_type: string;
  payment_mode: string;
  total_count: number;
  used_count: number;
  expire_at?: string | null;
  status: number;
  created_at?: string | null;
};

type PermissionAllocation = {
  permission_id: number;
  count: number;
};

type PermissionReservation = {
  ok: boolean;
  message: string;
  paymentMode: "subscription" | "per_use" | "none";
  allocations: PermissionAllocation[];
  chargedCount: number;
  errorCode?: string;
  errorParams?: Record<string, string | number>;
};

type AppLanguage = "zh" | "en";

type AdminUser = {
  id: number;
  username: string;
  email?: string | null;
  nickname?: string | null;
  role: string;
  status: number;
  created_at: string;
};

const defaultPermissionPrices = {
  script: { per_use: 1, monthly: 29, yearly: 199 },
  image: { per_use: 3, monthly: 99, yearly: 699 },
  video: { per_use: 5, monthly: 199, yearly: 1399 },
  ad: { per_use: 8, monthly: 299, yearly: 1999 },
};

const encoder = new TextEncoder();

const toISO = () => new Date().toISOString();

const json = (value: unknown) => JSON.stringify(value ?? null);

const detectPrimaryLanguage = (text: string) => {
  const normalized = (text || "").trim();
  if (!normalized) return "mixed";
  const chineseCount = (normalized.match(/[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]/g) || []).length;
  const englishCount = (normalized.match(/[A-Za-z]/g) || []).length;
  if (chineseCount && !englishCount) return "zh";
  if (englishCount && !chineseCount) return "en";
  if (chineseCount && englishCount) return chineseCount >= englishCount ? "zh" : "en";
  return "mixed";
};

const buildLanguageInstruction = (text: string) => {
  const language = detectPrimaryLanguage(text);
  if (language === "zh") {
    return "The user's input is primarily Simplified Chinese. You must answer entirely in Simplified Chinese. Do not switch to English unless the user explicitly asks for it or a fixed brand name must be preserved.";
  }
  if (language === "en") {
    return "The user's input is primarily English. You must answer entirely in English. Do not switch to Chinese unless the user explicitly asks for it or a fixed brand name must be preserved.";
  }
  return "You must follow the primary language used in the user's input. Do not translate or switch languages unless the user explicitly asks for it.";
};

const detectRequestLanguage = (acceptLanguage?: string | null): AppLanguage => {
  const normalized = (acceptLanguage || "").toLowerCase();
  return normalized.startsWith("zh") ? "zh" : "en";
};

const interpolateMessage = (template: string, params?: Record<string, string | number>) => {
  if (!params) return template;
  let content = template;
  for (const [key, value] of Object.entries(params)) {
    content = content.split(`{${key}}`).join(String(value));
  }
  return content;
};

const errorCatalog: Record<string, { zh: string; en: string }> = {
  unauthorized: {
    zh: "登录状态已失效，请重新登录。",
    en: "Your session has expired. Please sign in again.",
  },
  not_found: {
    zh: "请求的资源不存在。",
    en: "The requested resource was not found.",
  },
  email_or_phone_required: {
    zh: "请填写邮箱或手机号。",
    en: "Email or phone number is required.",
  },
  password_too_short: {
    zh: "密码长度不能少于 6 位。",
    en: "Password must be at least 6 characters long.",
  },
  email_already_registered: {
    zh: "该邮箱已被注册。",
    en: "This email address is already registered.",
  },
  phone_already_registered: {
    zh: "该手机号已被注册。",
    en: "This phone number is already registered.",
  },
  account_and_password_required: {
    zh: "请输入账号和密码。",
    en: "Account and password are required.",
  },
  invalid_credentials: {
    zh: "账号或密码错误。",
    en: "Invalid account or password.",
  },
  user_not_found: {
    zh: "用户不存在。",
    en: "User not found.",
  },
  admin_not_found: {
    zh: "管理员不存在。",
    en: "Admin account not found.",
  },
  script_not_found: {
    zh: "脚本不存在。",
    en: "Script not found.",
  },
  task_not_found: {
    zh: "任务不存在。",
    en: "Task not found.",
  },
  work_not_found: {
    zh: "作品不存在。",
    en: "Work not found.",
  },
  invalid_permission_type: {
    zh: "无效的权限类型。",
    en: "Invalid permission type.",
  },
  invalid_payment_mode: {
    zh: "无效的计费模式。",
    en: "Invalid payment mode.",
  },
  invalid_amount: {
    zh: "金额必须大于 0。",
    en: "Amount must be greater than 0.",
  },
  order_not_found: {
    zh: "订单不存在。",
    en: "Order not found.",
  },
  permission_not_enabled: {
    zh: "当前功能未开通或已过期，请先购买套餐。",
    en: "This capability is not enabled or has expired. Please purchase a plan first.",
  },
  permission_quota_insufficient: {
    zh: "可用额度不足，当前需要 {requiredCount} 次，剩余 {remainingCount} 次。",
    en: "Usage quota is insufficient. Required {requiredCount}, remaining {remainingCount}.",
  },
};

const getLocalizedErrorMessage = (
  key: string,
  language: AppLanguage,
  params?: Record<string, string | number>
) => {
  const template = errorCatalog[key]?.[language] || errorCatalog.not_found[language];
  return interpolateMessage(template, params);
};

const errorJson = (
  c: { req: { header: (name: string) => string | null | undefined }; json: (body: unknown, status?: number) => Response },
  errorCode: string,
  status: number,
  params?: Record<string, string | number>
) => {
  const language = detectRequestLanguage(c.req.header("Accept-Language"));
  return c.json(
    {
      detail: getLocalizedErrorMessage(errorCode, language, params),
      error_code: errorCode,
      error_params: params ?? {},
    },
    status
  );
};

const parseJson = <T>(value?: string | null, fallback?: T): T => {
  if (!value) return (fallback ?? ({} as T));
  try {
    return JSON.parse(value) as T;
  } catch {
    return (fallback ?? ({} as T));
  }
};

const sanitizeTaskParameters = <T extends Record<string, unknown>>(value: T): T => {
  if (!value || typeof value !== "object") return value;
  const cloned = { ...value };
  delete (cloned as Record<string, unknown>).__billing;
  return cloned;
};

const randId = (prefix: string) => {
  const now = Date.now().toString(36);
  const rand = crypto.getRandomValues(new Uint8Array(6));
  const randStr = Array.from(rand)
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
  return `${prefix}${now}${randStr}`.toUpperCase();
};

const bytesToBase64 = (bytes: Uint8Array) => btoa(String.fromCharCode(...bytes));

const base64ToBytes = (value: string) => Uint8Array.from(atob(value), (c) => c.charCodeAt(0));

const passwordHash = async (password: string) => {
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const payload = encoder.encode(`${bytesToBase64(salt)}:${password}`);
  const digest = new Uint8Array(await crypto.subtle.digest("SHA-256", payload));
  return `sha256$${bytesToBase64(salt)}$${bytesToBase64(digest)}`;
};

const verifyPassword = async (password: string, stored: string) => {
  const parts = stored.split("$");
  if (parts.length !== 3 || parts[0] !== "sha256") return false;
  const saltB64 = parts[1];
  const expected = parts[2];
  const payload = encoder.encode(`${saltB64}:${password}`);
  const digest = new Uint8Array(await crypto.subtle.digest("SHA-256", payload));
  return bytesToBase64(digest) === expected;
};

const signToken = async (env: Env, payload: Record<string, unknown>) => {
  const secret = encoder.encode(env.JWT_SECRET || env.SECRET_KEY || "change_this_to_a_random_long_secret");
  const normalizedPayload = { ...payload };
  if (normalizedPayload.sub !== undefined && normalizedPayload.sub !== null) {
    normalizedPayload.sub = String(normalizedPayload.sub);
  }
  return await new SignJWT(normalizedPayload)
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime("7d")
    .sign(secret);
};

const verifyToken = async (env: Env, token: string) => {
  const secret = encoder.encode(env.JWT_SECRET || env.SECRET_KEY || "change_this_to_a_random_long_secret");
  const { payload } = await jwtVerify(token, secret);
  return payload;
};

const extractBearer = (authHeader?: string | null) => {
  if (!authHeader) return null;
  const parts = authHeader.split(" ");
  if (parts.length !== 2) return null;
  if (parts[0] !== "Bearer") return null;
  return parts[1];
};

const ensureAdminSeed = async (env: Env) => {
  const exists = await env.DB.prepare("SELECT id FROM admin_users LIMIT 1").first();
  if (exists) return;
  const username = env.ADMIN_INIT_USERNAME || "admin";
  const password = env.ADMIN_INIT_PASSWORD || "admin123";
  const email = env.ADMIN_INIT_EMAIL || "";
  const nickname = env.ADMIN_INIT_NICKNAME || "Administrator";
  const hash = await passwordHash(password);
  await env.DB.prepare(
    "INSERT INTO admin_users (username, email, nickname, role, password_hash, status, created_at) VALUES (?, ?, ?, 'admin', ?, 1, ?)"
  )
    .bind(username, email, nickname, hash, toISO())
    .run();
};

const getPermissionPrices = async (env: Env) => {
  const row = await env.DB.prepare("SELECT value FROM system_config WHERE key = 'permission_prices'").first<{
    value: string;
  }>();
  if (!row?.value) return defaultPermissionPrices;
  return parseJson<typeof defaultPermissionPrices>(row.value, defaultPermissionPrices);
};

const setPermissionPrices = async (env: Env, prices: typeof defaultPermissionPrices) => {
  await env.DB.prepare(
    "INSERT INTO system_config (key, value, description, updated_at) VALUES ('permission_prices', ?, ?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at"
  )
    .bind(json(prices), "Permission prices", toISO())
    .run();
};

const getProviderSettings = async (env: Env) => {
  const rows = await env.DB.prepare(
    "SELECT key, value FROM system_config WHERE key LIKE 'openai_%' OR key LIKE 'deepseek_%' OR key LIKE 'stability_%' OR key LIKE 'runway_%'"
  ).all<{ key: string; value: string }>();
  const map = new Map(rows.results.map((row) => [row.key, row.value]));

  return {
    openai: {
      apiKey: map.get("openai_api_key") || env.OPENAI_API_KEY || "",
      apiBase: map.get("openai_api_base") || env.OPENAI_API_BASE || "",
      model: map.get("openai_model") || env.OPENAI_MODEL || "gpt-5.2",
      wireApi: map.get("openai_wire_api") || env.OPENAI_API_WIRE || "responses",
      reasoningEffort: map.get("openai_reasoning_effort") || env.OPENAI_REASONING_EFFORT || "",
      disableResponseStorage:
        map.get("openai_disable_response_storage") || env.OPENAI_DISABLE_RESPONSE_STORAGE || "",
      contextWindow: map.get("openai_context_window") || "",
    },
    deepseek: {
      apiKey: map.get("deepseek_api_key") || env.DEEPSEEK_API_KEY || "",
      apiBase: map.get("deepseek_api_base") || env.DEEPSEEK_API_BASE || "https://api.deepseek.com",
      model: map.get("deepseek_model") || env.DEEPSEEK_MODEL || "deepseek-chat",
    },
    stability: {
      apiKey: map.get("stability_api_key") || env.STABILITY_API_KEY || "",
      apiBase: map.get("stability_api_base") || env.STABILITY_API_BASE || "",
      engine: map.get("stability_engine") || env.STABILITY_ENGINE || "",
    },
    runway: {
      apiKey: map.get("runway_api_key") || env.RUNWAY_API_KEY || "",
      apiBase: map.get("runway_api_base") || env.RUNWAY_API_BASE || "",
    },
  };
};

const getProviderConfig = async (env: Env) => {
  const settings = await getProviderSettings(env);
  const openaiKey = settings.openai.apiKey;
  const openaiBase = settings.openai.apiBase;
  const openaiModel = settings.openai.model;
  const openaiWire = settings.openai.wireApi;
  const openaiReasoning = settings.openai.reasoningEffort;
  const openaiStore = settings.openai.disableResponseStorage;
  const openaiContext = settings.openai.contextWindow;

  const deepseekKey = settings.deepseek.apiKey;
  const deepseekBase = settings.deepseek.apiBase;
  const deepseekModel = settings.deepseek.model;

  const stabilityKey = settings.stability.apiKey;
  const stabilityBase = settings.stability.apiBase;
  const stabilityEngine = settings.stability.engine;

  const runwayKey = settings.runway.apiKey;
  const runwayBase = settings.runway.apiBase;

  const mask = (value: string) => {
    if (!value) return "";
    if (value.length <= 8) return "*".repeat(value.length);
    return `${value.slice(0, 4)}***${value.slice(-4)}`;
  };

  return {
    openai: {
      enabled: Boolean(openaiKey),
      api_key: mask(openaiKey),
      api_base: openaiBase,
      model: openaiModel,
      wire_api: openaiWire,
      reasoning_effort: openaiReasoning,
      disable_response_storage: openaiStore,
      context_window: openaiContext,
    },
    deepseek: {
      enabled: Boolean(deepseekKey),
      api_key: mask(deepseekKey),
      api_base: deepseekBase,
      model: deepseekModel,
    },
    stability: {
      enabled: Boolean(stabilityKey),
      api_key: mask(stabilityKey),
      api_base: stabilityBase,
      engine: stabilityEngine,
    },
    runway: {
      enabled: Boolean(runwayKey),
      api_key: mask(runwayKey),
      api_base: runwayBase,
    },
  };
};

const updateProviderConfig = async (env: Env, provider: string, payload: Record<string, string>) => {
  const allowed: Record<string, string[]> = {
    openai: [
      "api_key",
      "api_base",
      "model",
      "wire_api",
      "reasoning_effort",
      "disable_response_storage",
      "context_window",
    ],
    deepseek: ["api_key", "api_base", "model"],
    stability: ["api_key", "api_base", "engine"],
    runway: ["api_key", "api_base"],
  };
  if (!allowed[provider]) throw new Error("Unsupported provider");

  const mapKey = (key: string) => `${provider}_${key}`;
  const now = toISO();
  for (const [key, value] of Object.entries(payload)) {
    if (!allowed[provider].includes(key)) continue;
    await env.DB.prepare(
      "INSERT INTO system_config (key, value, description, updated_at) VALUES (?, ?, ?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at"
    )
      .bind(mapKey(key), value, `${provider} config`, now)
      .run();
  }
};

const calculateCost = (taskType: string, clarity: string, duration: number, count: number) => {
  const clarityWeights: Record<string, number> = {
    "720p": 1.0,
    "1080p": 1.5,
    "2k": 2.0,
    "4k": 2.5,
    "8k": 4.0,
  };
  const base: Record<string, number> = { script: 1, image: 3, video: 5, ad: 8 };
  const baseCost = base[taskType] ?? 1;
  const clarityWeight = clarityWeights[clarity] ?? 1.0;
  if (taskType === "video") {
    const durationWeight = Math.max(1.0, duration / 30.0);
    return Math.max(1, Math.round(baseCost * clarityWeight * durationWeight));
  }
  return Math.max(1, Math.round(baseCost * clarityWeight * Math.max(1, count)));
};

const isPermissionRowActive = (row: PermissionRow, now = Date.now()) => {
  if (row.status !== 1) return false;
  if (!row.expire_at) return true;
  const expireAt = Date.parse(row.expire_at);
  return Number.isNaN(expireAt) ? true : expireAt > now;
};

const getPermissionRows = async (env: Env, userId: number, permissionType: string) => {
  const rows = await env.DB.prepare(
    "SELECT * FROM user_permissions WHERE user_id = ? AND permission_type = ? AND status = 1 ORDER BY created_at ASC, id ASC"
  )
    .bind(userId, permissionType)
    .all<PermissionRow>();
  return rows.results;
};

const buildPermissionDeniedMessage = (permissionType: string, requiredCount: number, remainingCount = 0) => {
  if (remainingCount > 0) {
    return `${permissionType} quota is insufficient. Required ${requiredCount}, remaining ${remainingCount}.`;
  }
  return `${permissionType} permission is not enabled or has expired.`;
};

const checkPermissionAccess = async (env: Env, userId: number, permissionType: string, requiredCount = 1) => {
  const rows = await getPermissionRows(env, userId, permissionType);
  const activeRows = rows.filter((row) => isPermissionRowActive(row));
  const subscription = activeRows.find((row) => row.payment_mode !== "per_use");
  if (subscription) {
    return {
      ok: true,
      message: "Permission is valid",
      paymentMode: "subscription" as const,
      remainingCount: Number.POSITIVE_INFINITY,
      rows: activeRows,
    };
  }

  const remainingCount = activeRows
    .filter((row) => row.payment_mode === "per_use")
    .reduce((sum, row) => sum + Math.max(0, Number(row.total_count || 0) - Number(row.used_count || 0)), 0);

  if (remainingCount < requiredCount) {
    return {
      ok: false,
      message: buildPermissionDeniedMessage(permissionType, requiredCount, remainingCount),
      paymentMode: "none" as const,
      remainingCount,
      rows: activeRows,
    };
  }

  return {
    ok: true,
    message: "Permission is valid",
    paymentMode: "per_use" as const,
    remainingCount,
    rows: activeRows,
  };
};

const releasePermissionAllocations = async (env: Env, allocations: PermissionAllocation[]) => {
  for (const allocation of allocations) {
    await env.DB.prepare(
      "UPDATE user_permissions SET used_count = CASE WHEN used_count >= ? THEN used_count - ? ELSE 0 END WHERE id = ?"
    )
      .bind(allocation.count, allocation.count, allocation.permission_id)
      .run();
  }
};

const reservePermissionUsage = async (
  env: Env,
  userId: number,
  permissionType: string,
  requiredCount: number
): Promise<PermissionReservation> => {
  const access = await checkPermissionAccess(env, userId, permissionType, requiredCount);
  if (!access.ok) {
    return {
      ok: false,
      message: access.message,
      paymentMode: "none",
      allocations: [],
      chargedCount: 0,
    };
  }

  if (access.paymentMode === "subscription") {
    return {
      ok: true,
      message: access.message,
      paymentMode: "subscription",
      allocations: [],
      chargedCount: 0,
    };
  }

  let remainingToCharge = requiredCount;
  const allocations: PermissionAllocation[] = [];
  const perUseRows = access.rows.filter((row) => row.payment_mode === "per_use");

  for (const row of perUseRows) {
    const rowRemaining = Math.max(0, Number(row.total_count || 0) - Number(row.used_count || 0));
    if (!rowRemaining) continue;
    const charge = Math.min(remainingToCharge, rowRemaining);
    await env.DB.prepare("UPDATE user_permissions SET used_count = used_count + ? WHERE id = ?")
      .bind(charge, row.id)
      .run();
    allocations.push({ permission_id: row.id, count: charge });
    remainingToCharge -= charge;
    if (remainingToCharge <= 0) break;
  }

  if (remainingToCharge > 0) {
    await releasePermissionAllocations(env, allocations);
    return {
      ok: false,
      message: buildPermissionDeniedMessage(permissionType, requiredCount, access.remainingCount),
      paymentMode: "none",
      allocations: [],
      chargedCount: 0,
    };
  }

  return {
    ok: true,
    message: "Permission consumed",
    paymentMode: "per_use",
    allocations,
    chargedCount: requiredCount,
  };
};

const getUserFromToken = async (env: Env, authHeader?: string | null) => {
  const token = extractBearer(authHeader);
  if (!token) return null;
  try {
    const payload = await verifyToken(env, token);
    if (payload.role !== "user") return null;
    return Number(payload.sub);
  } catch {
    return null;
  }
};

const getAdminFromToken = async (env: Env, authHeader?: string | null) => {
  const token = extractBearer(authHeader);
  if (!token) return null;
  try {
    const payload = await verifyToken(env, token);
    if (payload.role !== "admin") return null;
    return Number(payload.sub);
  } catch {
    return null;
  }
};
const openaiGenerate = async (env: Env, prompt: string, systemPrompt?: string) => {
  const settings = await getProviderSettings(env);
  const apiKey = settings.openai.apiKey;
  const baseUrl = (settings.openai.apiBase || "https://api.openai.com/v1").replace(/\/+$/, "");
  const model = settings.openai.model || "gpt-5.2";
  const wire = (settings.openai.wireApi || "responses").toLowerCase();
  const headers = {
    Authorization: `Bearer ${apiKey}`,
    "Content-Type": "application/json",
  };
  if (!apiKey) throw new Error("OpenAI key missing");

  if (wire === "responses") {
    const payload: Record<string, unknown> = {
      model,
      input: prompt,
      temperature: 0.7,
      max_output_tokens: 2000,
    };
    if (systemPrompt) payload.instructions = systemPrompt;
    if (settings.openai.reasoningEffort) payload.reasoning = { effort: settings.openai.reasoningEffort };
    if (settings.openai.disableResponseStorage === "true") payload.store = false;

    const res = await fetch(`${baseUrl}/responses`, {
      method: "POST",
      headers,
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(await res.text());
    const data = (await res.json()) as any;
    const outputText = data.output_text;
    if (typeof outputText === "string" && outputText.trim()) return outputText;
    const output = data.output ?? [];
    for (const item of output) {
      if (item?.type !== "message") continue;
      for (const content of item?.content ?? []) {
        if (content?.type === "output_text" || content?.type === "text") {
          if (content?.text) return content.text as string;
        }
      }
    }
    throw new Error("Empty response");
  }

  const messages = [] as Array<{ role: string; content: string }>;
  if (systemPrompt) messages.push({ role: "system", content: systemPrompt });
  messages.push({ role: "user", content: prompt });
  const res = await fetch(`${baseUrl}/chat/completions`, {
    method: "POST",
    headers,
    body: JSON.stringify({ model, messages, temperature: 0.7, max_tokens: 2000 }),
  });
  if (!res.ok) throw new Error(await res.text());
  const data = (await res.json()) as any;
  return data?.choices?.[0]?.message?.content ?? "";
};

const deepseekGenerate = async (env: Env, prompt: string, systemPrompt?: string) => {
  const settings = await getProviderSettings(env);
  const apiKey = settings.deepseek.apiKey;
  const baseUrl = (settings.deepseek.apiBase || "https://api.deepseek.com").replace(/\/+$/, "");
  const model = settings.deepseek.model || "deepseek-chat";
  if (!apiKey) throw new Error("DeepSeek key missing");

  const messages = [] as Array<{ role: string; content: string }>;
  if (systemPrompt) messages.push({ role: "system", content: systemPrompt });
  messages.push({ role: "user", content: prompt });

  const res = await fetch(`${baseUrl}/chat/completions`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ model, messages, temperature: 0.7, max_tokens: 2000 }),
  });
  if (!res.ok) throw new Error(await res.text());
  const data = (await res.json()) as any;
  return data?.choices?.[0]?.message?.content ?? "";
};

const stabilityGenerate = async (env: Env, prompt: string, width: number, height: number, style?: string) => {
  if (!env.STABILITY_API_KEY) throw new Error("Stability key missing");
  const baseUrl = (env.STABILITY_API_BASE || "https://api.stability.ai/v1").replace(/\/+$/, "");
  const engine = env.STABILITY_ENGINE || "stable-diffusion-xl-1024-v1-0";
  const payload: Record<string, unknown> = {
    text_prompts: [{ text: prompt, weight: 1.0 }],
    cfg_scale: 7,
    height,
    width,
    steps: 30,
    seed: Math.floor(Date.now() / 1000),
  };
  if (style) payload.style_preset = style;
  const res = await fetch(`${baseUrl}/generation/${engine}/text-to-image`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${env.STABILITY_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(await res.text());
  const data = (await res.json()) as any;
  return (data.artifacts ?? []).map((item: any) => item.base64).filter(Boolean);
};

const runwayGenerate = async (env: Env, prompt: string, duration: number, resolution: string, style?: string) => {
  if (!env.RUNWAY_API_KEY) throw new Error("Runway key missing");
  const baseUrl = (env.RUNWAY_API_BASE || "https://api.runwayml.com/v1").replace(/\/+$/, "");
  const payload = { prompt, duration, resolution, fps: 24, style };
  const res = await fetch(`${baseUrl}/generate`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${env.RUNWAY_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(await res.text());
  return (await res.json()) as any;
};

const runwayStatus = async (env: Env, taskId: string) => {
  if (!env.RUNWAY_API_KEY) throw new Error("Runway key missing");
  const baseUrl = (env.RUNWAY_API_BASE || "https://api.runwayml.com/v1").replace(/\/+$/, "");
  const res = await fetch(`${baseUrl}/tasks/${taskId}`, {
    headers: { Authorization: `Bearer ${env.RUNWAY_API_KEY}` },
  });
  if (!res.ok) throw new Error(await res.text());
  return (await res.json()) as any;
};

const uploadBase64ToR2 = async (env: Env, base64: string, prefix: string) => {
  const binary = Uint8Array.from(atob(base64), (c) => c.charCodeAt(0));
  const key = `${prefix}/${new Date().toISOString().slice(0, 10).replace(/-/g, "/")}/${randId("F")}.png`;
  await env.ASSETS.put(key, binary, { httpMetadata: { contentType: "image/png" } });
  const base = env.ASSET_PUBLIC_BASE || "";
  if (base) return `${base.replace(/\/+$/, "")}/${key}`;
  return `r2://${key}`;
};

const createApp = (env: Env) => {
  const app = new Hono<{ Bindings: Env }>();
  app.use(
    "*",
    cors({
      origin: ["https://www.magicmotro.com", "https://admin.magicmotro.com", "http://localhost:5173"],
      allowHeaders: ["Content-Type", "Authorization"],
      allowMethods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
      credentials: true,
    })
  );

  app.get("/health", (c) => c.json({ status: "ok" }));

  app.get("/assets/*", async (c) => {
    const key = c.req.path.replace(/^\/assets\//, "");
    if (!key) return errorJson(c, "not_found", 404);
    const object = await env.ASSETS.get(key);
    if (!object) return errorJson(c, "not_found", 404);
    const headers = new Headers();
    object.writeHttpMetadata(headers);
    headers.set("etag", object.httpEtag);
    return new Response(object.body, { headers });
  });

  app.post("/auth/register", async (c) => {
    const body = await c.req.json();
    const email = (body.email || "").trim() || null;
    const phone = (body.phone || "").trim() || null;
    const password = (body.password || "").trim();
    const nickname = (body.nickname || "User").trim();
    if (!email && !phone) return errorJson(c, "email_or_phone_required", 400);
    if (!password || password.length < 6) return errorJson(c, "password_too_short", 400);

    if (email) {
      const existing = await env.DB.prepare("SELECT id FROM users WHERE email = ?").bind(email).first();
      if (existing) return errorJson(c, "email_already_registered", 400);
    }
    if (phone) {
      const existing = await env.DB.prepare("SELECT id FROM users WHERE phone = ?").bind(phone).first();
      if (existing) return errorJson(c, "phone_already_registered", 400);
    }
    const hash = await passwordHash(password);
    const createdAt = toISO();
    const result = await env.DB.prepare(
      "INSERT INTO users (email, phone, nickname, password_hash, balance, status, created_at) VALUES (?, ?, ?, ?, 0, 1, ?)"
    )
      .bind(email, phone, nickname, hash, createdAt)
      .run();
    const inserted = email
      ? await env.DB.prepare("SELECT * FROM users WHERE email = ? ORDER BY id DESC LIMIT 1").bind(email).first<any>()
      : await env.DB.prepare("SELECT * FROM users WHERE phone = ? ORDER BY id DESC LIMIT 1").bind(phone).first<any>();
    const user: User = {
      id: Number(inserted?.id || result.meta.last_row_id || 0),
      email: inserted?.email ?? email,
      phone: inserted?.phone ?? phone,
      nickname: inserted?.nickname ?? nickname,
      avatar: inserted?.avatar ?? null,
      balance: Number(inserted?.balance || 0),
      status: Number(inserted?.status || 1),
      created_at: inserted?.created_at ?? createdAt,
    };
    const token = await signToken(env, { sub: user.id, role: "user" });
    return c.json({ user, token: { access_token: token, token_type: "bearer" } });
  });

  app.post("/auth/login", async (c) => {
    const body = await c.req.json();
    const account = (body.account || "").trim();
    const password = (body.password || "").trim();
    if (!account || !password) return errorJson(c, "account_and_password_required", 400);

    const row = await env.DB.prepare("SELECT * FROM users WHERE email = ? OR phone = ?")
      .bind(account, account)
      .first<any>();
    if (!row) return errorJson(c, "invalid_credentials", 401);
    const ok = await verifyPassword(password, row.password_hash);
    if (!ok) return errorJson(c, "invalid_credentials", 401);
    const user: User = {
      id: row.id,
      email: row.email,
      phone: row.phone,
      nickname: row.nickname,
      avatar: row.avatar,
      balance: Number(row.balance || 0),
      status: row.status,
      created_at: row.created_at,
    };
    const token = await signToken(env, { sub: user.id, role: "user" });
    return c.json({ user, token: { access_token: token, token_type: "bearer" } });
  });

  app.get("/auth/me", async (c) => {
    const userId = await getUserFromToken(env, c.req.header("Authorization"));
    if (!userId) return errorJson(c, "unauthorized", 401);
    const row = await env.DB.prepare("SELECT * FROM users WHERE id = ?").bind(userId).first<any>();
    if (!row) return errorJson(c, "user_not_found", 404);
    return c.json({
      id: row.id,
      email: row.email,
      phone: row.phone,
      nickname: row.nickname,
      avatar: row.avatar,
      balance: Number(row.balance || 0),
      status: row.status,
      created_at: row.created_at,
    });
  });

  app.put("/auth/me", async (c) => {
    const userId = await getUserFromToken(env, c.req.header("Authorization"));
    if (!userId) return errorJson(c, "unauthorized", 401);
    const body = await c.req.json();
    const nickname = body.nickname ? String(body.nickname).trim() : null;
    const avatar = body.avatar ? String(body.avatar).trim() : null;
    await env.DB.prepare("UPDATE users SET nickname = COALESCE(?, nickname), avatar = COALESCE(?, avatar) WHERE id = ?")
      .bind(nickname, avatar, userId)
      .run();
    const row = await env.DB.prepare("SELECT * FROM users WHERE id = ?").bind(userId).first<any>();
    return c.json({
      id: row.id,
      email: row.email,
      phone: row.phone,
      nickname: row.nickname,
      avatar: row.avatar,
      balance: Number(row.balance || 0),
      status: row.status,
      created_at: row.created_at,
    });
  });

  app.get("/auth/me/balance", async (c) => {
    const userId = await getUserFromToken(env, c.req.header("Authorization"));
    if (!userId) return errorJson(c, "unauthorized", 401);
    const row = await env.DB.prepare("SELECT balance FROM users WHERE id = ?").bind(userId).first<any>();
    return c.json({ balance: Number(row?.balance || 0) });
  });
  app.get("/user/permissions", async (c) => {
    const userId = await getUserFromToken(env, c.req.header("Authorization"));
    if (!userId) return errorJson(c, "unauthorized", 401);
    const rows = await env.DB.prepare("SELECT * FROM user_permissions WHERE user_id = ?").bind(userId).all<any>();
    return c.json(
      rows.results.map((row) => ({
        id: row.id,
        permission_type: row.permission_type,
        payment_mode: row.payment_mode,
        total_count: row.total_count,
        used_count: row.used_count,
        expire_at: row.expire_at,
        status: row.status,
      }))
    );
  });

  app.get("/user/permissions/check", async (c) => {
    const userId = await getUserFromToken(env, c.req.header("Authorization"));
    if (!userId) return errorJson(c, "unauthorized", 401);
    const permissionType = c.req.query("permission_type");
    const requiredCount = Math.max(1, Number(c.req.query("required_count") || 1));
    if (!permissionType) return c.json({ has_permission: false });
    const access = await checkPermissionAccess(env, userId, permissionType, requiredCount);
    return c.json({ has_permission: access.ok, required_count: requiredCount, remaining_count: access.remainingCount });
  });

  app.post("/content/scripts", async (c) => {
    const userId = await getUserFromToken(env, c.req.header("Authorization"));
    if (!userId) return errorJson(c, "unauthorized", 401);
    const body = await c.req.json();
    const content = (body.content || "").trim();
    const keywords = (body.keywords || "").trim();
    const outputType = body.output_type || "image_set";
    const parameters = body.parameters ?? {};
    let finalContent = content;
    let reservation: PermissionReservation | null = null;
    if (!finalContent) {
      reservation = await reservePermissionUsage(env, userId, "script", 1);
      if (!reservation.ok) {
        return errorJson(c, reservation.errorCode || "permission_not_enabled", 400, reservation.errorParams);
      }
      const languageInstruction = buildLanguageInstruction(`${keywords}\n${parameters?.style || ""}`);
      const systemPrompt =
        `You are a creative script assistant. Produce a structured script with scenes, shots, and style notes. ${languageInstruction}`;
      const prompt = `Create a script for:\nKeywords: ${keywords}\nOutput: ${outputType}\nStyle: ${
        parameters?.style || "natural"
      }\nScenes: ${parameters?.scene_count || 1}\nLanguage requirement: ${languageInstruction}`;
      try {
        finalContent = await deepseekGenerate(env, prompt, systemPrompt);
      } catch (error) {
        if (reservation.allocations.length) {
          await releasePermissionAllocations(env, reservation.allocations);
        }
        throw error;
      }
      if (!finalContent?.trim() && reservation.allocations.length) {
        await releasePermissionAllocations(env, reservation.allocations);
      }
    }
    const createdAt = toISO();
    const result = await env.DB.prepare(
      "INSERT INTO scripts (user_id, title, content, output_type, parameters, status, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)"
    )
      .bind(
        userId,
        body.title || null,
        finalContent,
        outputType,
        json(parameters),
        finalContent ? 1 : 0,
        createdAt
      )
      .run();
    const script = {
      id: Number(result.meta.last_row_id),
      user_id: userId,
      title: body.title || null,
      content: finalContent,
      output_type: outputType,
      parameters,
      created_at: createdAt,
    };
    return c.json({ message: "Script created", data: { script_id: script.id, script } });
  });

  app.get("/content/scripts", async (c) => {
    const userId = await getUserFromToken(env, c.req.header("Authorization"));
    if (!userId) return errorJson(c, "unauthorized", 401);
    const skip = Number(c.req.query("skip") || 0);
    const limit = Number(c.req.query("limit") || 20);
    const rows = await env.DB.prepare(
      "SELECT * FROM scripts WHERE user_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?"
    )
      .bind(userId, limit, skip)
      .all<any>();
    return c.json(
      rows.results.map((row) => ({
        id: row.id,
        user_id: row.user_id,
        title: row.title,
        content: row.content,
        output_type: row.output_type,
        parameters: parseJson(row.parameters, {}),
        created_at: row.created_at,
      }))
    );
  });

  app.get("/content/scripts/:id", async (c) => {
    const userId = await getUserFromToken(env, c.req.header("Authorization"));
    if (!userId) return errorJson(c, "unauthorized", 401);
    const id = Number(c.req.param("id"));
    const row = await env.DB.prepare("SELECT * FROM scripts WHERE id = ? AND user_id = ?")
      .bind(id, userId)
      .first<any>();
    if (!row) return errorJson(c, "script_not_found", 404);
    return c.json({
      id: row.id,
      user_id: row.user_id,
      title: row.title,
      content: row.content,
      output_type: row.output_type,
      parameters: parseJson(row.parameters, {}),
      created_at: row.created_at,
    });
  });

  app.put("/content/scripts/:id", async (c) => {
    const userId = await getUserFromToken(env, c.req.header("Authorization"));
    if (!userId) return errorJson(c, "unauthorized", 401);
    const id = Number(c.req.param("id"));
    const body = await c.req.json();
    await env.DB.prepare(
      "UPDATE scripts SET title = COALESCE(?, title), content = COALESCE(?, content), parameters = COALESCE(?, parameters) WHERE id = ? AND user_id = ?"
    )
      .bind(body.title || null, body.content || null, json(body.parameters || null), id, userId)
      .run();
    return c.json({ message: "Script updated" });
  });

  app.delete("/content/scripts/:id", async (c) => {
    const userId = await getUserFromToken(env, c.req.header("Authorization"));
    if (!userId) return errorJson(c, "unauthorized", 401);
    const id = Number(c.req.param("id"));
    await env.DB.prepare("DELETE FROM scripts WHERE id = ? AND user_id = ?").bind(id, userId).run();
    return c.json({ message: "Script deleted" });
  });
  app.post("/content/tasks", async (c) => {
    const userId = await getUserFromToken(env, c.req.header("Authorization"));
    if (!userId) return errorJson(c, "unauthorized", 401);
    const body = await c.req.json();
    const taskType = body.task_type;
    const parameters = body.parameters ?? {};
    const clarity = parameters.clarity || "1080p";
    const duration = Number(parameters.duration || 0);
    const count = Number(parameters.count || 1);
    const cost = calculateCost(taskType, clarity, duration, count);
    const reservation = await reservePermissionUsage(env, userId, taskType, cost);
    if (!reservation.ok) {
      return errorJson(c, reservation.errorCode || "permission_not_enabled", 400, reservation.errorParams);
    }
    const taskNo = randId("T");
    const createdAt = toISO();
    const storedParameters = {
      ...parameters,
      __billing: {
        permission_type: taskType,
        charged_count: reservation.chargedCount,
        payment_mode: reservation.paymentMode,
        allocations: reservation.allocations,
      },
    };
    const result = await env.DB.prepare(
      "INSERT INTO tasks (task_no, user_id, task_type, parameters, status, progress, cost_amount, created_at) VALUES (?, ?, ?, ?, 0, 0, ?, ?)"
    )
      .bind(taskNo, userId, taskType, json(storedParameters), cost, createdAt)
      .run();
    const task = {
      id: Number(result.meta.last_row_id),
      task_no: taskNo,
      task_type: taskType,
      parameters,
      status: 0,
      progress: 0,
      cost_amount: cost,
      created_at: createdAt,
    };
    await env.TASK_QUEUE.send({ taskId: task.id });
    return c.json({ message: "Task created", data: { task_id: task.id, task_no: taskNo, task } });
  });

  app.get("/content/tasks", async (c) => {
    const userId = await getUserFromToken(env, c.req.header("Authorization"));
    if (!userId) return errorJson(c, "unauthorized", 401);
    const skip = Number(c.req.query("skip") || 0);
    const limit = Number(c.req.query("limit") || 20);
    const status = c.req.query("status");
    const taskType = c.req.query("task_type");
    let query = "SELECT * FROM tasks WHERE user_id = ?";
    const params: unknown[] = [userId];
    if (status !== undefined) {
      query += " AND status = ?";
      params.push(Number(status));
    }
    if (taskType) {
      query += " AND task_type = ?";
      params.push(taskType);
    }
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?";
    params.push(limit, skip);
    const rows = await env.DB.prepare(query).bind(...params).all<any>();
    return c.json(
      rows.results.map((row) => ({
        id: row.id,
        task_no: row.task_no,
        task_type: row.task_type,
        parameters: sanitizeTaskParameters(parseJson(row.parameters, {})),
        status: row.status,
        progress: row.progress,
        result_url: row.result_url,
        error_message: row.error_message,
        cost_amount: row.cost_amount,
        created_at: row.created_at,
        completed_at: row.completed_at,
      }))
    );
  });

  app.get("/content/tasks/:taskNo", async (c) => {
    const userId = await getUserFromToken(env, c.req.header("Authorization"));
    if (!userId) return errorJson(c, "unauthorized", 401);
    const taskNo = c.req.param("taskNo");
    const row = await env.DB.prepare("SELECT * FROM tasks WHERE task_no = ? AND user_id = ?")
      .bind(taskNo, userId)
      .first<any>();
    if (!row) return errorJson(c, "task_not_found", 404);
    return c.json({
      id: row.id,
      task_no: row.task_no,
      task_type: row.task_type,
      parameters: sanitizeTaskParameters(parseJson(row.parameters, {})),
      status: row.status,
      progress: row.progress,
      result_url: row.result_url,
      error_message: row.error_message,
      cost_amount: row.cost_amount,
      created_at: row.created_at,
      completed_at: row.completed_at,
    });
  });

  app.get("/content/works", async (c) => {
    const userId = await getUserFromToken(env, c.req.header("Authorization"));
    if (!userId) return errorJson(c, "unauthorized", 401);
    const skip = Number(c.req.query("skip") || 0);
    const limit = Number(c.req.query("limit") || 20);
    const workType = c.req.query("work_type");
    let query = "SELECT * FROM works WHERE user_id = ?";
    const params: unknown[] = [userId];
    if (workType) {
      query += " AND work_type = ?";
      params.push(workType);
    }
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?";
    params.push(limit, skip);
    const rows = await env.DB.prepare(query).bind(...params).all<any>();
    return c.json(
      rows.results.map((row) => ({
        id: row.id,
        work_type: row.work_type,
        title: row.title,
        description: row.description,
        content_url: row.content_url,
        thumbnail_url: row.thumbnail_url,
        status: row.status,
        created_at: row.created_at,
        updated_at: row.updated_at,
      }))
    );
  });

  app.get("/content/works/:id", async (c) => {
    const userId = await getUserFromToken(env, c.req.header("Authorization"));
    if (!userId) return errorJson(c, "unauthorized", 401);
    const id = Number(c.req.param("id"));
    const row = await env.DB.prepare("SELECT * FROM works WHERE id = ? AND user_id = ?")
      .bind(id, userId)
      .first<any>();
    if (!row) return errorJson(c, "work_not_found", 404);
    return c.json({
      id: row.id,
      work_type: row.work_type,
      title: row.title,
      description: row.description,
      content_url: row.content_url,
      thumbnail_url: row.thumbnail_url,
      status: row.status,
      created_at: row.created_at,
      updated_at: row.updated_at,
    });
  });

  app.delete("/content/works/:id", async (c) => {
    const userId = await getUserFromToken(env, c.req.header("Authorization"));
    if (!userId) return errorJson(c, "unauthorized", 401);
    const id = Number(c.req.param("id"));
    await env.DB.prepare("DELETE FROM works WHERE id = ? AND user_id = ?").bind(id, userId).run();
    return c.json({ message: "Work deleted" });
  });

  app.get("/content/gallery", async (c) => {
    const skip = Number(c.req.query("skip") || 0);
    const limit = Number(c.req.query("limit") || 20);
    const workType = c.req.query("work_type");
    let query = "SELECT * FROM works WHERE status = 1";
    const params: unknown[] = [];
    if (workType) {
      query += " AND work_type = ?";
      params.push(workType);
    }
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?";
    params.push(limit, skip);
    const rows = await env.DB.prepare(query).bind(...params).all<any>();
    return c.json(
      rows.results.map((row) => ({
        id: row.id,
        work_type: row.work_type,
        title: row.title,
        description: row.description,
        content_url: row.content_url,
        thumbnail_url: row.thumbnail_url,
        status: row.status,
        created_at: row.created_at,
        updated_at: row.updated_at,
      }))
    );
  });

  app.get("/payment/permissions/prices", async (c) => {
    const prices = await getPermissionPrices(env);
    return c.json(prices);
  });

  app.post("/payment/orders", async (c) => {
    const userId = await getUserFromToken(env, c.req.header("Authorization"));
    if (!userId) return errorJson(c, "unauthorized", 401);
    const body = await c.req.json();
    const prices = await getPermissionPrices(env);
    const permissionType = body.permission_type;
    const paymentMode = body.payment_mode;
    const count = Number(body.count || 1);
    const paymentMethod = body.payment_method || "balance";
    if (!prices[permissionType]) return errorJson(c, "invalid_permission_type", 400);
    const unit = prices[permissionType][paymentMode] ?? 0;
    if (!unit) return errorJson(c, "invalid_payment_mode", 400);
    const amount = paymentMode === "per_use" ? unit * count : unit;
    const orderNo = randId("O");
    await env.DB.prepare(
      "INSERT INTO orders (order_no, user_id, order_type, product_name, amount, payment_method, status, created_at, remark) VALUES (?, ?, 'permission', ?, ?, ?, 0, ?, ?)"
    )
      .bind(orderNo, userId, `${permissionType}-permission-${paymentMode}`, amount, paymentMethod, toISO(), json({ permission_type: permissionType, payment_mode: paymentMode, count }))
      .run();
    return c.json({ order_no: orderNo, amount, status: 0 });
  });

  app.post("/payment/orders/balance", async (c) => {
    const userId = await getUserFromToken(env, c.req.header("Authorization"));
    if (!userId) return errorJson(c, "unauthorized", 401);
    const amount = Number(c.req.query("amount") || 0);
    const paymentMethod = c.req.query("payment_method") || "wechat";
    if (amount <= 0) return errorJson(c, "invalid_amount", 400);
    const orderNo = randId("O");
    await env.DB.prepare(
      "INSERT INTO orders (order_no, user_id, order_type, product_name, amount, payment_method, status, created_at) VALUES (?, ?, 'balance', ?, ?, ?, 0, ?)"
    )
      .bind(orderNo, userId, `balance-${amount}`, amount, paymentMethod, toISO())
      .run();
    return c.json({ order_no: orderNo, amount, status: 0 });
  });

  app.get("/payment/orders", async (c) => {
    const userId = await getUserFromToken(env, c.req.header("Authorization"));
    if (!userId) return errorJson(c, "unauthorized", 401);
    const skip = Number(c.req.query("skip") || 0);
    const limit = Number(c.req.query("limit") || 20);
    const status = c.req.query("status");
    let query = "SELECT * FROM orders WHERE user_id = ?";
    const params: unknown[] = [userId];
    if (status !== undefined) {
      query += " AND status = ?";
      params.push(Number(status));
    }
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?";
    params.push(limit, skip);
    const rows = await env.DB.prepare(query).bind(...params).all<any>();
    return c.json(
      rows.results.map((row) => ({
        order_no: row.order_no,
        user_id: row.user_id,
        user_nickname: "",
        order_type: row.order_type,
        product_name: row.product_name,
        amount: row.amount,
        payment_method: row.payment_method,
        status: row.status,
        created_at: row.created_at,
        completed_at: row.completed_at,
      }))
    );
  });

  app.get("/payment/orders/:orderNo", async (c) => {
    const userId = await getUserFromToken(env, c.req.header("Authorization"));
    if (!userId) return errorJson(c, "unauthorized", 401);
    const orderNo = c.req.param("orderNo");
    const row = await env.DB.prepare("SELECT * FROM orders WHERE order_no = ? AND user_id = ?")
      .bind(orderNo, userId)
      .first<any>();
    if (!row) return errorJson(c, "order_not_found", 404);
    return c.json({
      order_no: row.order_no,
      user_id: row.user_id,
      user_nickname: "",
      order_type: row.order_type,
      product_name: row.product_name,
      amount: row.amount,
      payment_method: row.payment_method,
      status: row.status,
      created_at: row.created_at,
      completed_at: row.completed_at,
    });
  });

  app.post("/payment/orders/:orderNo/pay", async (c) => {
    const userId = await getUserFromToken(env, c.req.header("Authorization"));
    if (!userId) return errorJson(c, "unauthorized", 401);
    const orderNo = c.req.param("orderNo");
    const row = await env.DB.prepare("SELECT * FROM orders WHERE order_no = ? AND user_id = ?")
      .bind(orderNo, userId)
      .first<any>();
    if (!row) return errorJson(c, "order_not_found", 404);
    if (row.status === 1) return c.json({ message: "Payment succeeded", data: { order_no: orderNo } });
    await env.DB.prepare("UPDATE orders SET status = 1, completed_at = ? WHERE order_no = ?")
      .bind(toISO(), orderNo)
      .run();
    if (row.order_type === "balance") {
      await env.DB.prepare("UPDATE users SET balance = balance + ? WHERE id = ?").bind(row.amount, userId).run();
    } else if (row.order_type === "permission") {
      const remark = parseJson<any>(row.remark, {});
      const permissionType = remark.permission_type || "script";
      const paymentMode = remark.payment_mode || "per_use";
      const count = Number(remark.count || 1);
      const expireAt =
        paymentMode === "monthly"
          ? new Date(Date.now() + 30 * 24 * 3600 * 1000).toISOString()
          : paymentMode === "yearly"
            ? new Date(Date.now() + 365 * 24 * 3600 * 1000).toISOString()
            : null;
      await env.DB.prepare(
        "INSERT INTO user_permissions (user_id, permission_type, payment_mode, total_count, used_count, expire_at, status, created_at) VALUES (?, ?, ?, ?, 0, ?, 1, ?)"
      )
        .bind(userId, permissionType, paymentMode, paymentMode === "per_use" ? count : 0, expireAt, toISO())
        .run();
    }
    return c.json({ message: "Payment succeeded", data: { order_no: orderNo } });
  });
  app.post("/auth/admin/login", async (c) => {
    await ensureAdminSeed(env);
    const body = await c.req.json();
    const account = (body.account || "").trim();
    const password = (body.password || "").trim();
    const row = await env.DB.prepare("SELECT * FROM admin_users WHERE username = ? OR email = ?")
      .bind(account, account)
      .first<any>();
    if (!row) return errorJson(c, "invalid_credentials", 401);
    const ok = await verifyPassword(password, row.password_hash);
    if (!ok) return errorJson(c, "invalid_credentials", 401);
    const admin: AdminUser = {
      id: row.id,
      username: row.username,
      email: row.email,
      nickname: row.nickname,
      role: row.role,
      status: row.status,
      created_at: row.created_at,
    };
    const token = await signToken(env, { sub: admin.id, role: "admin" });
    return c.json({ user: admin, token: { access_token: token, token_type: "bearer" } });
  });

  app.get("/auth/admin/me", async (c) => {
    const adminId = await getAdminFromToken(env, c.req.header("Authorization"));
    if (!adminId) return errorJson(c, "unauthorized", 401);
    const row = await env.DB.prepare("SELECT * FROM admin_users WHERE id = ?").bind(adminId).first<any>();
    if (!row) return errorJson(c, "admin_not_found", 404);
    return c.json({
      id: row.id,
      username: row.username,
      email: row.email,
      nickname: row.nickname,
      role: row.role,
      status: row.status,
      created_at: row.created_at,
    });
  });

  app.get("/admin/dashboard", async (c) => {
    const adminId = await getAdminFromToken(env, c.req.header("Authorization"));
    if (!adminId) return c.json({ detail: "Unauthorized" }, 401);
    const totalUsers = await env.DB.prepare("SELECT COUNT(*) as count FROM users").first<any>();
    const totalOrders = await env.DB.prepare("SELECT COUNT(*) as count FROM orders").first<any>();
    const totalRevenue = await env.DB.prepare("SELECT SUM(amount) as total FROM orders WHERE status = 1").first<any>();
    const recent = await env.DB.prepare("SELECT * FROM orders ORDER BY created_at DESC LIMIT 6").all<any>();
    const trend = await env.DB.prepare(
      "SELECT substr(created_at,1,10) as date, SUM(amount) as amount FROM orders WHERE status = 1 GROUP BY substr(created_at,1,10) ORDER BY date DESC LIMIT 7"
    ).all<any>();
    return c.json({
      total_users: Number(totalUsers?.count || 0),
      total_orders: Number(totalOrders?.count || 0),
      total_revenue: Number(totalRevenue?.total || 0),
      recent_orders: recent.results.map((row) => ({
        order_no: row.order_no,
        user_id: row.user_id,
        user_nickname: "",
        order_type: row.order_type,
        product_name: row.product_name,
        amount: row.amount,
        payment_method: row.payment_method,
        status: row.status,
        created_at: row.created_at,
        completed_at: row.completed_at,
      })),
      revenue_trend: trend.results.map((row) => ({ date: row.date, amount: Number(row.amount || 0) })),
    });
  });

  app.get("/admin/users", async (c) => {
    const adminId = await getAdminFromToken(env, c.req.header("Authorization"));
    if (!adminId) return c.json({ detail: "Unauthorized" }, 401);
    const skip = Number(c.req.query("skip") || 0);
    const limit = Number(c.req.query("limit") || 20);
    const status = c.req.query("status");
    const keyword = c.req.query("keyword");
    let query = "SELECT * FROM users WHERE 1=1";
    const params: unknown[] = [];
    if (status !== undefined) {
      query += " AND status = ?";
      params.push(Number(status));
    }
    if (keyword) {
      query += " AND (email LIKE ? OR phone LIKE ? OR nickname LIKE ?)";
      const like = `%${keyword}%`;
      params.push(like, like, like);
    }
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?";
    params.push(limit, skip);
    const rows = await env.DB.prepare(query).bind(...params).all<any>();
    const countRow = await env.DB.prepare("SELECT COUNT(*) as count FROM users").first<any>();
    return c.json({ items: rows.results, total: Number(countRow?.count || 0), skip, limit });
  });

  app.put("/admin/users/:userId/status", async (c) => {
    const adminId = await getAdminFromToken(env, c.req.header("Authorization"));
    if (!adminId) return c.json({ detail: "Unauthorized" }, 401);
    const userId = Number(c.req.param("userId"));
    const status = Number(c.req.query("status") || 0);
    await env.DB.prepare("UPDATE users SET status = ? WHERE id = ?").bind(status, userId).run();
    return c.json({ message: "User status updated" });
  });

  app.get("/admin/orders", async (c) => {
    const adminId = await getAdminFromToken(env, c.req.header("Authorization"));
    if (!adminId) return c.json({ detail: "Unauthorized" }, 401);
    const skip = Number(c.req.query("skip") || 0);
    const limit = Number(c.req.query("limit") || 20);
    const status = c.req.query("status");
    const orderType = c.req.query("order_type");
    const keyword = c.req.query("keyword");
    let query = "SELECT * FROM orders WHERE 1=1";
    const params: unknown[] = [];
    if (status !== undefined) {
      query += " AND status = ?";
      params.push(Number(status));
    }
    if (orderType) {
      query += " AND order_type = ?";
      params.push(orderType);
    }
    if (keyword) {
      query += " AND (order_no LIKE ? OR product_name LIKE ?)";
      const like = `%${keyword}%`;
      params.push(like, like);
    }
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?";
    params.push(limit, skip);
    const rows = await env.DB.prepare(query).bind(...params).all<any>();
    const countRow = await env.DB.prepare("SELECT COUNT(*) as count FROM orders").first<any>();
    return c.json({ items: rows.results, total: Number(countRow?.count || 0), skip, limit });
  });

  app.get("/admin/revenue/stats", async (c) => {
    const adminId = await getAdminFromToken(env, c.req.header("Authorization"));
    if (!adminId) return c.json({ detail: "Unauthorized" }, 401);
    const totalRow = await env.DB.prepare("SELECT SUM(amount) as total FROM orders WHERE status = 1").first<any>();
    const dailyRows = await env.DB.prepare(
      "SELECT substr(created_at,1,10) as date, SUM(amount) as amount FROM orders WHERE status = 1 GROUP BY substr(created_at,1,10) ORDER BY date DESC LIMIT 30"
    ).all<any>();
    return c.json({
      total_revenue: Number(totalRow?.total || 0),
      daily_stats: dailyRows.results.map((row) => ({ date: row.date, amount: Number(row.amount || 0) })),
      payment_method_stats: [],
      order_type_stats: [],
    });
  });

  app.get("/admin/permissions/prices", async (c) => {
    const adminId = await getAdminFromToken(env, c.req.header("Authorization"));
    if (!adminId) return c.json({ detail: "Unauthorized" }, 401);
    const prices = await getPermissionPrices(env);
    return c.json(prices);
  });

  app.put("/admin/permissions/prices", async (c) => {
    const adminId = await getAdminFromToken(env, c.req.header("Authorization"));
    if (!adminId) return c.json({ detail: "Unauthorized" }, 401);
    const body = await c.req.json();
    await setPermissionPrices(env, body);
    return c.json({ message: "Prices updated" });
  });

  app.get("/admin/ai/providers", async (c) => {
    const adminId = await getAdminFromToken(env, c.req.header("Authorization"));
    if (!adminId) return c.json({ detail: "Unauthorized" }, 401);
    return c.json(await getProviderConfig(env));
  });

  app.put("/admin/ai/providers/:provider", async (c) => {
    const adminId = await getAdminFromToken(env, c.req.header("Authorization"));
    if (!adminId) return c.json({ detail: "Unauthorized" }, 401);
    const provider = c.req.param("provider");
    const body = await c.req.json();
    await updateProviderConfig(env, provider, body);
    return c.json({ message: "AI provider config updated" });
  });

  return app;
};

const handleQueue = async (message: Message, env: Env) => {
  const payload = message.body as { taskId?: number };
  if (!payload?.taskId) return;
  const row = await env.DB.prepare("SELECT * FROM tasks WHERE id = ?").bind(payload.taskId).first<any>();
  if (!row) return;
  if (row.status === 2 || row.status === 3) return;
  const params = parseJson<any>(row.parameters, {});
  const billing = params.__billing ?? { allocations: [] };
  const publicParams = sanitizeTaskParameters(params);
  try {
    await env.DB.prepare("UPDATE tasks SET status = 1, progress = 10 WHERE id = ?").bind(row.id).run();
    if (row.task_type === "image") {
      const prompt = publicParams.prompt || "";
      const clarity = publicParams.clarity || "1080p";
      const style = publicParams.style || undefined;
      const count = Math.max(1, Number(publicParams.count || 1));
      const resolutionMap: Record<string, [number, number]> = {
        "720p": [1280, 768],
        "1080p": [1536, 896],
        "4k": [2048, 1152],
      };
      const [width, height] = resolutionMap[clarity] || [1536, 896];
      const images: string[] = [];
      for (let i = 0; i < count; i += 1) {
        const result = await stabilityGenerate(env, prompt, width, height, style);
        images.push(...result);
      }
      const urls: string[] = [];
      for (const base64 of images) {
        const url = await uploadBase64ToR2(env, base64, "images");
        urls.push(url);
      }
      const resultUrl = urls[0] || "";
      await env.DB.prepare(
        "INSERT INTO works (user_id, work_type, title, description, content_url, thumbnail_url, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)"
      )
        .bind(row.user_id, "image", "Generated image", "", resultUrl, resultUrl, toISO(), toISO())
        .run();
      await env.DB.prepare("UPDATE tasks SET status = 2, progress = 100, result_url = ?, completed_at = ? WHERE id = ?")
        .bind(resultUrl, toISO(), row.id)
        .run();
      return;
    }

    if (row.task_type === "video") {
      const prompt = publicParams.prompt || "";
      const duration = Math.max(1, Number(publicParams.duration || 4));
      const clarity = publicParams.clarity || "1080p";
      const style = publicParams.style || undefined;
      const result = await runwayGenerate(env, prompt, duration, clarity, style);
      const resultUrl = result?.result_url || "";
      const taskId = result?.id || result?.task_id;
      if (resultUrl) {
        await env.DB.prepare(
          "INSERT INTO works (user_id, work_type, title, description, content_url, thumbnail_url, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)"
        )
          .bind(row.user_id, "video", "Generated video", "", resultUrl, resultUrl, toISO(), toISO())
          .run();
        await env.DB.prepare("UPDATE tasks SET status = 2, progress = 100, result_url = ?, completed_at = ? WHERE id = ?")
          .bind(resultUrl, toISO(), row.id)
          .run();
      } else {
        const nextParams = { ...params, external_task_id: taskId };
        await env.DB.prepare("UPDATE tasks SET status = 1, progress = 60, parameters = ? WHERE id = ?")
          .bind(json(nextParams), row.id)
          .run();
      }
      return;
    }

    if (billing.allocations?.length) {
      await releasePermissionAllocations(env, billing.allocations);
    }
    await env.DB.prepare("UPDATE tasks SET status = 3, error_message = ? WHERE id = ?")
      .bind("Unsupported task type", row.id)
      .run();
  } catch (err: any) {
    if (billing.allocations?.length) {
      await releasePermissionAllocations(env, billing.allocations);
    }
    await env.DB.prepare("UPDATE tasks SET status = 3, error_message = ? WHERE id = ?")
      .bind(String(err?.message || err), row.id)
      .run();
  }
};

const handleScheduled = async (env: Env) => {
  const rows = await env.DB.prepare(
    "SELECT * FROM tasks WHERE status = 1 AND task_type = 'video' ORDER BY created_at DESC LIMIT 20"
  ).all<any>();
  for (const row of rows.results) {
    const params = parseJson<any>(row.parameters, {});
    const billing = params.__billing ?? { allocations: [] };
    const externalTaskId = params.external_task_id;
    if (!externalTaskId) continue;
    try {
      const status = await runwayStatus(env, externalTaskId);
      const state = String(status.status || "").toLowerCase();
      if (["completed", "succeeded", "success"].includes(state)) {
        const resultUrl = status.result_url || "";
        if (resultUrl) {
          await env.DB.prepare(
            "INSERT INTO works (user_id, work_type, title, description, content_url, thumbnail_url, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)"
          )
            .bind(row.user_id, "video", "Generated video", "", resultUrl, resultUrl, toISO(), toISO())
            .run();
        }
        await env.DB.prepare("UPDATE tasks SET status = 2, progress = 100, result_url = ?, completed_at = ? WHERE id = ?")
          .bind(resultUrl, toISO(), row.id)
          .run();
      } else if (["failed", "error", "cancelled"].includes(state)) {
        await env.DB.prepare("UPDATE tasks SET status = 3, error_message = ? WHERE id = ?")
          .bind(status.error || "Video generation failed", row.id)
          .run();
        if (billing.allocations?.length) {
          await releasePermissionAllocations(env, billing.allocations);
        }
      }
    } catch (err: any) {
      await env.DB.prepare("UPDATE tasks SET error_message = ? WHERE id = ?")
        .bind(String(err?.message || err), row.id)
        .run();
    }
  }
};

export default {
  fetch(request: Request, env: Env, ctx: ExecutionContext) {
    const app = createApp(env);
    const prefix = env.API_PREFIX || "/api/v1";
    const url = new URL(request.url);
    if (url.pathname.startsWith(prefix)) {
      url.pathname = url.pathname.slice(prefix.length) || "/";
      return app.fetch(new Request(url, request), env, ctx);
    }
    return app.fetch(request, env, ctx);
  },
  async queue(batch: MessageBatch, env: Env) {
    for (const message of batch.messages) {
      await handleQueue(message, env);
    }
  },
  async scheduled(event: ScheduledEvent, env: Env, ctx: ExecutionContext) {
    ctx.waitUntil(handleScheduled(env));
  },
};
