
## 10. Interaction & Motion（2026-08-29 追加，来源：hallmark redesign 全流程审计）

等待 = 阶段化反馈：凡预计 >2s 的操作必须显示所处阶段（步骤卡轮询 /sessions/{id}/trace；
禁止无阶段转圈）。动效纪律：≤200ms、ease-out、只动 transform/opacity；条件字段出现用
animate-slide-up；:focus-visible 环永不动画。表单 = 列选择优先：凡数据列可枚举，字段用
datalist 从 columns 选择，禁止让用户裸手打列名；可选字段缺失时行内显示"不填由系统自行推断"。
门禁 = 显式解锁条件：禁用按钮必须用 title/文案说明解锁条件（导出、写章）。焦点环：
:focus-visible 2px 货架绿 55%。轨迹可见：Agent 每步的轮次摘要与最终代码在步骤卡可展开
（history_compact / final_code）。reduced-motion 全局坍缩（index.css 末尾）。
