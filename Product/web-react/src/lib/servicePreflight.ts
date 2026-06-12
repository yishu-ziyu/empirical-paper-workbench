export type ServicePreflightFailureKind =
  | "backend_unreachable"
  | "wrong_service"
  | "cors_blocked"
  | "llm_not_configured"
  | "backend_error";

export interface ServicePreflightPayload {
  status?: "ready" | "needs_llm" | string;
  service?: {
    kind?: string;
    health_endpoint?: string;
  };
  llm_supervisor?: {
    ready?: boolean;
    reason?: string;
  };
  recommended_action?: {
    id?: string;
    label?: string;
    hint?: string;
  };
}

export interface ServicePreflightFailureInput {
  status?: number;
  contentType?: string | null;
  message?: string;
  serviceRespondedWithoutCors?: boolean;
}

export interface ServicePreflightMessage {
  kind: ServicePreflightFailureKind;
  title: string;
  message: string;
}

export function classifyServicePreflightFailure({
  status,
  contentType,
  serviceRespondedWithoutCors,
}: ServicePreflightFailureInput): ServicePreflightMessage {
  if (serviceRespondedWithoutCors) {
    return {
      kind: "cors_blocked",
      title: "服务有响应，但浏览器预检失败",
      message: "这个地址有服务响应，但页面无法读取它。请确认它是 FastAPI 研究后端，并允许当前页面访问。",
    };
  }

  if (status === 501 || status === 405 || contentType?.includes("text/html")) {
    return {
      kind: "wrong_service",
      title: "当前端口不是研究后端",
      message: "这个地址有服务响应，但不是本地研究 API。请切到真正的 FastAPI 后端地址。",
    };
  }

  if (!status || status === 0) {
    return {
      kind: "backend_unreachable",
      title: "本地研究服务没有响应",
      message: "当前页面还没有连到研究后端。请先启动本地服务，再回到当前任务继续。",
    };
  }

  return {
    kind: "backend_error",
    title: "研究服务返回异常",
    message: "后端已经响应，但状态不正常。请重新连接或查看本地服务日志。",
  };
}

export function servicePreflightMessage(payload: ServicePreflightPayload): ServicePreflightMessage {
  if (payload.status === "needs_llm" || payload.llm_supervisor?.ready === false) {
    return {
      kind: "llm_not_configured",
      title: "后端在线，模型还没准备好",
      message:
        payload.recommended_action?.hint ||
        payload.llm_supervisor?.reason ||
        "本地研究服务已连接，但 LLM Supervisor 还不能接管任务。",
    };
  }

  return {
    kind: "backend_error",
    title: "研究服务状态待确认",
    message: "预检已返回，但还没有进入可执行状态。请重新连接后再继续。",
  };
}

export async function probeLocalServiceReachability(url: string, signal?: AbortSignal): Promise<boolean> {
  try {
    await fetch(url, {
      method: "GET",
      mode: "no-cors",
      signal,
    });
    return true;
  } catch {
    return false;
  }
}

export async function fetchServicePreflight(apiUrlBuilder: (path: string) => string) {
  const response = await fetch(apiUrlBuilder("/api/v1/service-preflight"), {
    method: "GET",
  });
  if (!response.ok) {
    throw classifyServicePreflightFailure({
      status: response.status,
      contentType: response.headers.get("content-type"),
    });
  }
  const payload = (await response.json()) as ServicePreflightPayload;
  if (payload.status !== "ready") {
    throw servicePreflightMessage(payload);
  }
  return payload;
}
