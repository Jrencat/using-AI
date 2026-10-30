# V-LIMS 真实使用记录

整理日期：2026-10-30。用户提供的背景是这些案例属于真实 `$develop` 使用；下列 Git 和报告证据能证明业务开发及测试结果，但不能独立证明每次提交调用了该 Skill。逐案例调用记录、模型与 Agent 版本均未知，不能把提交作者等同于 Agent。

## 证据与计数口径

原始导出目录：`C:\Users\15639\AppData\Local\Temp\vlims-git-evidence-aro8OV`。其中三个仓库各有 `root`、`branch`、`status`、`name-status`、`numstat` 文件；`vilims` 和 `vilims-admin` 为 `it20261026`，`vilims-data-admin` 为 `main`，后者指定时间范围内无可达提交。导出仅涵盖当时当前分支可达记录；工作区并非干净，详细状态见原文件。临时目录可能被清理，应保存原始文件以便长期复核。

文件次数仅统计各案例下所列非合并提交中文件出现次数，不是返工次数。时间均为 UTC+08:00 的作者日期，测试时间按报告所载。Iteration Classification 的可用值：NORMAL_ITERATION（有证据支持正常增量开发）、SUSPECTED_REWORK（有依据但未确认）、CONFIRMED_REWORK（有证据确认）、UNKNOWN（无法判断）。缺少问题原因、验收标准和过程记录时使用 UNKNOWN。

## 2026-10-20：物料处置

- 背景与需求：27107，提交描述为隐藏试剂、设备、色谱柱、耗材处置状态，增加字典处置方式，完成后更新为已处理。
- 模型和 Agent：未知；`$develop` 使用为用户提供背景，缺逐案例调用记录。
- 提交：后端 `aedb0c22ff91dbb0c3c4684816439c5585e68e94`（10:55:56）；前端 `f6183383a8770f6edfad615e6cc6f34351d92d57`（10:55:14）。
- 开发过程：可确认前后端分别提交对应需求；更细的实施顺序和人工干预无法从 Git 确定。
- 测试及时间：未找到可确认关联的测试结果，时间未知；实际业务验收未知。
- Iteration Classification：UNKNOWN；没有足够过程证据判断返工。
- 人工介入次数 / 主动时间、Token、费用：未知或未记录。
- 证据缺口：任务会话、Skill 调用、测试及验收记录。

修改文件及出现次数：

- `vilims/vilims-base-service/src/main/java/cn/vilims/base/service/operation/impl/DisposalServiceImpl.java`：1 次
- `vilims-admin/src/utils/disposal.ts`：1 次
- `vilims-admin/src/views/commonQuery/materialOperationQuery/operationColumnsConfig.ts`：1 次
- `vilims-admin/src/views/commonQuery/materialOperationQuery/operationQuery.vue`：1 次
- `vilims-admin/src/views/operation/disposal/disposal.vue`：1 次
- `vilims-admin/src/views/operation/disposal/review.vue`：1 次

## 2026-10-21：储备液剩余量

- 背景与需求：27113，填写体积时判断试剂剩余量并提示不足。该提交可明确识别为储备液开发，但不能证明覆盖“业务字段及库存数量”原始任务的全部范围。
- 模型和 Agent：未知；`$develop` 使用为用户提供背景，缺逐案例调用记录。
- 提交：后端 `fa96e6a905ac2a63ee295ba6280adbd86e5ba92c`（09:20:16）；前端 `3cad94cc0384f576d1a806665d50580697fb9285`（09:25:43）。
- 开发过程：提交记录显示前后端均涉及剩余量提示；具体业务验收过程未知。
- 测试及时间：未找到可确认关联的测试结果，时间未知。
- Iteration Classification：UNKNOWN；不能据文件修改判断返工。
- 人工介入次数 / 主动时间、Token、费用：未知或未记录。
- 证据缺口：完整需求和字段范围、调用记录、测试及验收记录。

修改文件及出现次数：

- `vilims/vilims-base-service/src/main/java/cn/vilims/base/pojo/vo/operation/ExperimentRecordUseRecordVO.java`：1 次
- `vilims/vilims-base-service/src/main/java/cn/vilims/base/service/operation/impl/OperationServiceImpl.java`：1 次
- `vilims-admin/src/api/experiment/experimentRecord.ts`：1 次
- `vilims-admin/src/views/experiment/experiment/record/composables/useStepGroups.ts`：1 次
- `vilims-admin/src/views/experiment/experiment/record/index.vue`：1 次
- `vilims-admin/src/views/experiment/experiment/sub-lists/SubListContainer.vue`：1 次
- `vilims-admin/src/views/experiment/experiment/sub-lists/components/EPC004-ResultStockSol.vue`：1 次
- `vilims-admin/src/views/operation/blend/index.vue`：1 次

## 2026-10-22 至 23：物料转移

- 背景与需求：按冰箱、按专题批量转移；需求编号未知。
- 模型和 Agent：未知；`$develop` 使用为用户提供背景，缺逐案例调用记录。
- 提交：10 月 22 日后端 `e98385b40a4a1eded7c0fa1e32882292b5ff3df0`（17:46:28）、前端 `8056ee1015c97b46e18c122d488430febbdc8403`（17:47:32）；10 月 23 日后端 `fbc7828313ced0ac2051bdb856fca0cdb718f8e9`（14:55:54）、前端 `c78a81e77e0b158b10bc53211800a5c18ab82b0b`（14:58:37）。
- 开发过程：提交描述显示先增加两个转移方式，后调整按冰箱转移。V-LIMS 工作区根目录的 `docs/分析/批量转移实施确认.md` 记载 10 月 21 日确认的预览、整盒、混装排除和保存规则；不能由提交顺序推断调整原因。
- 测试及时间：该实施确认文档报告全模块编译、base-service 22 项测试、最终两类定向测试 5 项及前端构建通过；报告未给出这些检查各自的准确执行时间。全量 lint 退出 1（4198 错误、220123 警告），typecheck 退出 2（依赖语法解析阻塞）；报告未声称真实数据库迁移或浏览器后端联调通过。上述为历史文档记载，未在本次复跑，也不能自动归属于某个提交版本。
- Iteration Classification：UNKNOWN；两日的增量和调整可观察，是否返工不能确定。
- 人工介入次数 / 主动时间、Token、费用：未知或未记录；实施确认文档表明规则经用户确认，但无法统计完整人工介入。
- 证据缺口：逐检查时间及对应提交、真实业务验收、完整开发对话和调用记录。

修改文件及出现次数：

- `vilims/vilims-base-service/src/main/java/cn/vilims/base/controller/operation/TransferController.java`：1 次
- `vilims/vilims-base-service/src/main/java/cn/vilims/base/dao/TransferBatchDao.java`：2 次
- `vilims/vilims-base-service/src/main/java/cn/vilims/base/pojo/entity/MaterialOperation.java`：1 次
- `vilims/vilims-base-service/src/main/java/cn/vilims/base/pojo/entity/MaterialTransfer.java`：1 次
- `vilims/vilims-base-service/src/main/java/cn/vilims/base/pojo/req/operation/TransferSaveReq.java`：1 次
- `vilims/vilims-base-service/src/main/java/cn/vilims/base/pojo/vo/TransferPreviewVO.java`：1 次
- `vilims/vilims-base-service/src/main/java/cn/vilims/base/pojo/vo/TransferRowVO.java`：2 次
- `vilims/vilims-base-service/src/main/java/cn/vilims/base/pojo/vo/operation/MaterialOperationVO.java`：1 次
- `vilims/vilims-base-service/src/main/java/cn/vilims/base/service/operation/impl/TransferBatchService.java`：2 次
- `vilims/vilims-base-service/src/main/java/cn/vilims/base/service/operation/impl/TransferServiceImpl.java`：2 次
- `vilims/vilims-base-service/src/main/resources/mybatis/MaterialOperationDao.xml`：1 次
- `vilims/vilims-base-service/src/main/resources/mybatis/MaterialTransferDao.xml`：1 次
- `vilims/vilims-base-service/src/main/resources/mybatis/TransferBatchDao.xml`：2 次
- `vilims/vilims-common/src/main/java/cn/vilims/common/enums/CommonEnum.java`：1 次
- `vilims/vilims-common/src/main/resources/common/messages.properties`：1 次
- `vilims/vilims-common/src/main/resources/common/messages_en_US.properties`：1 次
- `vilims/vilims-common/src/main/resources/common/messages_zh_CN.properties`：1 次
- `vilims/vilims-base-service/src/main/java/cn/vilims/base/dao/MatConPosRelationDao.java`：1 次
- `vilims/vilims-base-service/src/main/java/cn/vilims/base/feign/ProjectFeign.java`：1 次
- `vilims/vilims-base-service/src/main/resources/mybatis/MatConPosRelationDao.xml`：1 次
- `vilims/vilims-experiment-service/src/main/java/cn/vilims/experiment/controller/feign/ProjectFeignController.java`：1 次
- `vilims/vilims-experiment-service/src/main/java/cn/vilims/experiment/dao/project/ProjectDao.java`：1 次
- `vilims/vilims-experiment-service/src/main/resources/mybatis/ProjectDao.xml`：1 次
- `vilims-admin/src/api/operation/operation.ts`：2 次
- `vilims-admin/src/components/auto-select-table.vue`：1 次
- `vilims-admin/src/views/commonQuery/materialOperationQuery/operationColumnsConfig.ts`：1 次
- `vilims-admin/src/views/commonQuery/materialOperationQuery/operationQuery.vue`：1 次
- `vilims-admin/src/views/operation/transfer/transfer.vue`：2 次

## 2026-10-26：专题转移盒子遗漏修复

- 背景与需求：用户描述按专题转移时盒子未被包含；提交描述为转移样品时同时转移其所在容器。需求编号未知。
- 模型和 Agent：未知；`$develop` 使用为用户提供背景，缺逐案例调用记录。
- 时间线：`tmp_topic_box_targeted.log` 的构建于 09:55:47 结束，测试共 21 项、失败 1 项（`TransferBatchSourceQueryTest.originalLocationIsSelectedAndLockedForBatchPreview` 断言 expected true but was false），其中保存测试 4 项及服务测试 14 项通过。该测试发生在修复提交前；其失败不能仅凭现有记录认定为盒子遗漏的根因。10:13:10 提交 `811a8ba899ba2b6bd61e0af661c3cb706d323035`。修复后缺少可确认关联的测试结果，不能把 09:55 的结果作为修复后验证。
- 开发过程：该提交的实际 diff 将固定“盒子”类别判断改为读取配置的耗材容器类别，并处理配置缺失和解析；文件 29 行新增、1 行删除。
- Iteration Classification：UNKNOWN；可观察到问题修复，缺少初始验收、缺陷原因和过程记录，无法确认是否构成返工。
- 人工介入次数 / 主动时间、Token、费用：未知或未记录。
- 证据缺口：修复后测试、真实数据业务验收、缺陷发现及 Skill 调用记录。原始日志位于 V-LIMS 工作区根目录 `tmp_topic_box_targeted.log` 和 `tmp_topic_box_full.log`；后者也报告构建失败。

修改文件及出现次数：

- `vilims/vilims-base-service/src/main/java/cn/vilims/base/service/operation/impl/TransferBatchService.java`：1 次

## 当前认识与下一步

- 已经证明：真实业务代码开发已经发生；按照用户提供的历史背景，`$develop` 已用于真实业务开发。Git 本身不能证明各提交的 Skill 调用，仍需原始会话或等价记录逐项核验。
- 已经观察：前后端跨模块实现、业务规则调整、历史测试失败及后续问题修复；测试失败与某个缺陷之间的因果关系尚未证明。
- 尚未证明：返工减少比例、Token 节省比例、人工时间节省比例；没有完整实测数据和同条件基线。
- 下一步最值得改善：在现有开发流程交付时记录实现后定向验证、失败诊断、修复及修复后复验的时间、结果和对应版本，明确未验证项；使用现有工具，不引入新框架。
