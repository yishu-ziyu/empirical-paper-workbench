import { DEFAULT_LOCAL_API_BASE, apiBase, setBrowserApiBase } from "../lib/apiBase";

interface ServiceConnectionRecoveryProps {
  message?: string | null;
  currentApiBase?: string;
  onRetry?: () => void | Promise<void>;
  onUseLocalBackend?: () => void | Promise<void>;
  retryLabel?: string;
  localActionTestId?: string;
}

const LOCAL_START_COMMAND =
  "python3 -m uvicorn Product.app:app --host 127.0.0.1 --port 8765";

export function ServiceConnectionRecovery({
  message,
  currentApiBase,
  onRetry,
  onUseLocalBackend,
  retryLabel = "重新连接",
  localActionTestId,
}: ServiceConnectionRecoveryProps) {
  const resolvedApiBase = currentApiBase?.trim() || apiBase() || "同源服务";
  const healthEndpoint =
    resolvedApiBase === "同源服务" ? "/api/v1/health" : `${resolvedApiBase}/api/v1/health`;

  const useLocalBackend = () => {
    setBrowserApiBase(DEFAULT_LOCAL_API_BASE);
    if (onUseLocalBackend) {
      void onUseLocalBackend();
      return;
    }
    if (onRetry) {
      void onRetry();
    }
  };

  return (
    <div
      className="service-connection-recovery"
      role="alert"
      data-testid="service-connection-recovery"
    >
      <div className="service-connection-recovery__head">
        <span className="eyebrow">连接本地研究服务</span>
        <h3>研究服务还没有响应</h3>
        <p>{message || "当前页面没有连到本地 FastAPI 服务，先恢复连接再继续下一步。"}</p>
      </div>

      <dl className="service-connection-recovery__facts">
        <div>
          <dt>当前后端地址</dt>
          <dd>
            <code>{resolvedApiBase}</code>
          </dd>
        </div>
        <div>
          <dt>健康检查</dt>
          <dd>
            <code>{healthEndpoint}</code>
          </dd>
        </div>
      </dl>

      <div className="service-connection-recovery__command">
        <span>在项目根目录启动本地服务</span>
        <code>{LOCAL_START_COMMAND}</code>
      </div>

      <p className="service-connection-recovery__note">
        不会丢失已保存的研究材料；恢复服务后，回到当前题目继续。
      </p>

      <div className="service-connection-recovery__actions">
        <button
          className="btn btn--secondary"
          type="button"
          onClick={useLocalBackend}
          data-testid={localActionTestId}
        >
          使用本地后端
        </button>
        {onRetry ? (
          <button className="btn btn--primary" type="button" onClick={() => void onRetry()}>
            {retryLabel}
          </button>
        ) : null}
      </div>
    </div>
  );
}

export default ServiceConnectionRecovery;
