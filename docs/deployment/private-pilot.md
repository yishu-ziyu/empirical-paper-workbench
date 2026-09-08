# 受保护个人试用部署

状态：部署包实现中，尚未部署。验收以 [契约](../acceptance/private-pilot-deployment.md) 为准。

沿用根目录 Compose；使用独立 `econpaper-private-pilot` 项目、loopback 端口和新卷。
严禁 `down -v`、覆盖现有部署、挂载开发源码补依赖或上传凭据。
本地验证需 Docker 可用、专用本地安全配置、TLS 入口和真实生成/评审服务；远端另需目标主机、入口与访问范围明确授权。

后续在本文件记录已执行构建/验证/停止/备份/恢复命令与结果，未运行项目不会标记通过。
