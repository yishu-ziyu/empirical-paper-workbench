# Parent Education Wage Delivery Package BDD

本阶段目标是把已经完成的非 UI 产品功能收束成可交付包。它不调用 AI，不重新估计模型，不改变论文结论，只把完整初稿、修复数据、模型证据和验收材料打成可追踪交付物。

## 行为 1：完整初稿未就绪时不能生成交付包

Given P16 没有 `can_claim_complete_paper=true`
When 用户请求生成交付包
Then 系统返回 blocked 状态
And 不写交付 zip
And 明确缺少完整初稿验收包

业务规则：交付包不能把半成品伪装成交付完成。

## 行为 2：完整初稿就绪后生成 manifest、README 和 zip

Given P16 已确认完整初稿可审阅
And DOCX、Markdown、P18 修复数据、P14 执行证据都存在
When 用户请求生成交付包
Then 系统写出 `Submissions/parent_education_wage_delivery_manifest.json`
And 写出 `Submissions/parent_education_wage_delivery_README.md`
And 写出 `Submissions/parent_education_wage_delivery_package.zip`
And manifest 中每个文件都有 size 和 sha256

业务规则：交付物必须可复核，不只是一个文件列表。

## 行为 3：交付包状态可被 UI 无关接口读取

Given 交付包已经生成
When UI 或自动化读取 Product Control headless state
Then 返回 `delivery_package` 组件
And 组件状态为 `completed`
And 组件只包含状态、动作、证据、产物和阻断原因，不包含布局信息

业务规则：UI 设计可以后置，但功能交付状态必须稳定可读。

