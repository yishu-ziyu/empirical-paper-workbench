# P2-I 真实数据字段画像 / 变量字典预览 BDD

## 当前目标

把已经通过 P2-H 显式导入或绑定的真实数据，推进到“安全字段画像 / 变量字典预览”阶段。这个阶段只读取数据结构、样本预览和字段质量，不自动写入 VariableRoleSet、DesignSpec 或 RunPlan。

## 行为 1：CSV 导入后可以生成字段画像

Given 用户已经把候选池 CSV 通过 `copy_to_project_raw` 导入到项目 `Data/Raw`

When 用户点击“生成字段画像”

Then 系统应返回 `evidence_level=local_file` 的 `dataset_import_profile`，包含字段名、字段顺序、推断类型、缺失率、样本值、行列数和源文件哈希

业务规则：真实数据进入变量角色确认前，用户必须先看到可审计的字段字典。

## 行为 2：仅绑定外部引用也可以画像，但必须保留本机路径依赖

Given 用户选择 `bind_external_reference`，没有复制大文件到项目内

When 用户生成字段画像

Then 系统应从已登记的外部只读路径读取字段结构，并在结果中标记 `binding.mode=external_reference`、`read_only=true`

业务规则：纯本地版本允许绑定本机大文件，但必须把“依赖本机路径”的事实显式暴露。

## 行为 3：DTA/XLSX/Parquet 暂不支持解析时不能伪造字段

Given 用户绑定或导入了 `.dta`、`.xlsx`、`.parquet` 等真实文件

When 当前解析器尚未接入对应格式

Then 系统应返回 `status=blocked` / `readiness_status=not_profiled`，保留来源、大小、哈希和阻塞原因，字段列表必须为空

业务规则：产品宁可显示“暂未画像”，也不能用 mock 字段误导后续研究设计。

## 行为 4：来源文件变化后必须阻止画像

Given 用户绑定了一个外部引用，并且 apply 时记录了 SHA256

When 画像前发现源文件 SHA256 与记录不一致

Then API 必须返回 409 `dataset_import_source_changed`

业务规则：同一个导入记录不能在来源已变化时继续产出字段证据，否则 provenance 失真。

## 行为 5：取消的导入记录不能画像

Given 用户取消了某次预检

When 用户尝试对该 `dataset_import_id` 生成字段画像

Then API 必须返回 409 `dataset_import_not_profileable`

业务规则：取消代表用户明确不接入，该记录不能成为后续研究对象。

## 行为 6：前端必须说明字段画像不会改写研究状态

Given 数据与设计页已经显示 P2-H 的接入结果

When 用户查看字段画像入口和结果

Then 页面必须显示“生成字段画像”“字段画像 / 变量字典预览”，并明确“不会改写 VariableRoleSet、DesignSpec 或 RunPlan”

业务规则：用户要理解这是导入后的审查阶段，不是自动建模阶段。

## 边界条件

- 本阶段默认只实现 CSV 内容解析；DTA/XLSX/Parquet 先返回安全阻塞状态。
- 不复制外部绑定文件；只读读取字段结构。
- 不把画像结果自动写入 `state/product/variable_roles.json`、`design_spec.json` 或 `run_plan.json`。
- 线上版本后续必须改为上传或云对象读取，本阶段 API 只服务纯本地版本。
