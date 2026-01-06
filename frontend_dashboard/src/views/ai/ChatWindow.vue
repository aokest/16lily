<template>
  <div class="h-screen flex flex-col bg-slate-50 overflow-hidden">
    <header class="bg-white shadow-sm px-6 py-4 flex justify-between items-center shrink-0 z-10">
      <div class="flex items-center gap-4">
        <h1 class="text-xl font-bold text-slate-800">AI对话窗</h1>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">大屏首页</el-breadcrumb-item>
          <el-breadcrumb-item :to="{ path: '/crm' }">CRM首页</el-breadcrumb-item>
          <el-breadcrumb-item>AI对话窗</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
    </header>
    <main class="flex-1 p-6 overflow-auto">
      <el-tabs v-model="tab">
        <el-tab-pane label="智能体" name="agent">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <el-card class="md:col-span-1">
              <template #header>输入需求</template>
              <div class="space-y-3">
                <el-input v-model="agentText" type="textarea" :rows="6" placeholder="例如：通过审批 123，或 新建客户，客户名称：示例公司，行业：教育，区域：北京" />
                <div class="flex flex-col gap-2">
                  <div class="flex gap-2">
                    <el-select v-model="agentConfigId" placeholder="选择AI模型(可选)" class="flex-1">
                      <el-option v-for="c in aiConfigs" :key="c.id" :label="cLabel(c)" :value="String(c.id)" />
                    </el-select>
                    <el-button @click="testAI" type="primary" plain>测试连接</el-button>
                  </div>
                  <div class="flex flex-wrap gap-2">
                    <el-button size="small" @click="fillTemplate('approve')">审批模板</el-button>
                    <el-button size="small" @click="fillTemplate('customer')">客户模板</el-button>
                    <el-button size="small" @click="fillTemplate('opportunity')">商机模板</el-button>
                  </div>
                </div>
                <el-button type="primary" @click="analyzeAgent" :loading="loading" class="w-full">智能分析</el-button>
              </div>
            </el-card>
            <el-card class="md:col-span-2">
              <template #header>建议动作</template>
              <div class="space-y-3">
                <div class="text-sm text-slate-500">智能体推荐（点击下方卡片选择）。解析后已自动填入下方表单，请在下方确认或修改后提交：</div>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <el-card v-for="(alt,i) in agentAlternatives" :key="i" class="cursor-pointer hover:shadow" @click="chooseAlternative(alt)">
                    <div class="font-bold">{{ humanLabel(alt) }}</div>
                    <div class="text-xs text-slate-500 mt-1">{{ humanDesc(alt) }}</div>
                  </el-card>
                </div>
                <div class="text-sm">当前选择：{{ humanLabel(chosen) }}</div>
                <div class="flex items-center gap-3">
                  <el-button type="success" @click="executeChosen" :disabled="needsForm(chosen)" :loading="loading">执行</el-button>
                  <el-button text @click="showRaw = !showRaw">{{ showRaw ? '隐藏请求详情' : '查看请求详情' }}</el-button>
                </div>
                <div v-if="showRaw" class="mt-4">
                  <pre class="text-xs whitespace-pre-wrap">{{ JSON.stringify(agentResult, null, 2) }}</pre>
                </div>
              </div>
            </el-card>
          </div>
        </el-tab-pane>
        <el-tab-pane label="审批助手" name="approvals">
          <div class="flex items-center gap-3 mb-3">
            <el-select v-model="approvalStatus" placeholder="状态" clearable style="width: 160px">
              <el-option label="待确认" value="PENDING" />
              <el-option label="已确认" value="APPROVED" />
              <el-option label="已驳回" value="REJECTED" />
            </el-select>
            <el-button type="primary" @click="loadApprovals" :loading="loading">加载审批</el-button>
            <el-button @click="presetPending">我的待办</el-button>
            <el-button @click="presetHandled">我已处理</el-button>
            <el-input v-model="bulkReason" placeholder="批量备注" style="width: 240px" />
            <el-button type="success" :disabled="!selectedApprovalIds.length" @click="bulkApprove">批量通过</el-button>
            <el-button type="danger" :disabled="!selectedApprovalIds.length" @click="bulkReject">批量驳回</el-button>
          </div>
          <el-table :data="approvals" v-loading="loading" @selection-change="onApprovalSelection" style="width:100%">
            <el-table-column type="selection" width="48" />
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="model_name" label="业务类型" width="120">
              <template #default="{row}">
                <el-tag effect="plain" size="small">{{ row.model_name || row.model_key }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="object_summary" label="审批内容" min-width="200">
              <template #default="{row}">
                <div class="font-medium text-slate-800">{{ row.object_summary }}</div>
                <div class="text-xs text-slate-400">ID: {{ row.object_id }}</div>
              </template>
            </el-table-column>
            <el-table-column prop="applicant_name" label="申请人" width="120" />
            <el-table-column prop="approver_name" label="审批人" width="120" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{row}">
                <el-tag v-if="row.status==='PENDING'" type="warning">待确认</el-tag>
                <el-tag v-else-if="row.status==='APPROVED'" type="success">已通过</el-tag>
                <el-tag v-else-if="row.status==='REJECTED'" type="danger">已驳回</el-tag>
                <el-tag v-else type="info">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="reason" label="理由" />
            <el-table-column label="操作" width="220" fixed="right">
              <template #default="scope">
                <div class="flex items-center gap-2">
                  <el-input v-model="rowOpinion[scope.row.id]" placeholder="备注" size="small" style="width: 140px" />
                  <el-button size="small" type="success" @click="approve(scope.row)">通过</el-button>
                  <el-button size="small" type="danger" @click="reject(scope.row)">驳回</el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="客户助手" name="customers">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <el-card>
              <template #header>新建客户</template>
              <div class="space-y-3">
                <el-input v-model="custForm.name" placeholder="客户名称" />
                <div class="flex gap-3">
                  <el-input v-model="custForm.industry" placeholder="行业" />
                  <el-input v-model="custForm.region" placeholder="区域" />
                </div>
                <el-select v-model="custForm.status" placeholder="客户状态">
                  <el-option label="潜在客户" value="POTENTIAL" />
                  <el-option label="合作中" value="ACTIVE" />
                  <el-option label="重点客户" value="KEY" />
                  <el-option label="流失客户" value="CHURNED" />
                </el-select>
                <el-button type="primary" @click="createCustomer" :loading="loading">创建客户</el-button>
              </div>
            </el-card>
            <el-card>
              <template #header>客户查询</template>
              <div class="flex items-center gap-3 mb-3">
                <el-input v-model="custSearch" placeholder="搜索名称/行业/区域" />
                <el-button type="primary" @click="listCustomers" :loading="loading">搜索</el-button>
              </div>
              <el-table :data="customerList" size="small" v-loading="loading">
                <el-table-column prop="name" label="客户名称" />
                <el-table-column prop="industry" label="行业" width="140" />
                <el-table-column prop="region" label="区域" width="120" />
                <el-table-column prop="status" label="状态" width="120" />
              </el-table>
            </el-card>
          </div>
        </el-tab-pane>
        <el-tab-pane label="商机助手" name="opportunities">
          <el-card>
            <template #header>智能识别新商机</template>
            <div class="space-y-3">
              <el-input v-model="oppText" type="textarea" :rows="6" placeholder="输入商机描述，系统自动识别关键字段并生成商机" />
              <div class="flex items-center gap-3">
                <el-button type="primary" @click="aiParseOpportunity" :loading="loading">AI识别</el-button>
                <el-button @click="createOpportunity" :disabled="!oppParsed?.name" :loading="loading">创建商机</el-button>
              </div>
              <div v-if="oppParsed" class="bg-slate-50 p-3 rounded border text-sm">
                识别结果：名称 {{ oppParsed.name || '-' }}，金额 {{ oppParsed.amount || '-' }}，客户 {{ oppParsed.customer_name || '-' }}，阶段 {{ oppParsed.stage || '-' }}
              </div>
            </div>
          </el-card>
        </el-tab-pane>
        <el-tab-pane label="活动助手" name="activities">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <el-card>
              <template #header>创建活动</template>
              <div class="space-y-3">
                <el-input v-model="actForm.name" placeholder="活动名称" />
                <div class="flex gap-3">
                  <el-date-picker v-model="actForm.time" type="date" placeholder="活动时间" style="width: 180px" />
                  <el-input v-model="actForm.location" placeholder="活动地点" />
                </div>
                <el-input v-model="actForm.type" placeholder="活动类型" />
                <el-input v-model="actForm.scale" placeholder="规模" />
                <el-button type="primary" @click="createActivity" :loading="loading">创建活动</el-button>
              </div>
            </el-card>
            <el-card>
              <template #header>活动查询</template>
              <div class="flex items-center gap-3 mb-3">
                <el-select v-model="actFilters.status" placeholder="状态" clearable style="width: 160px">
                  <el-option label="草稿" value="DRAFT" />
                  <el-option label="待确认" value="PENDING" />
                  <el-option label="已确认" value="APPROVED" />
                  <el-option label="已驳回" value="REJECTED" />
                </el-select>
                <el-input v-model="actFilters.name" placeholder="名称包含" />
                <el-button type="primary" @click="loadActivities" :loading="loading">搜索</el-button>
              </div>
              <el-table :data="actList" size="small" v-loading="loading">
                <el-table-column prop="name" label="活动名称" />
                <el-table-column prop="status" label="状态" width="120" />
                <el-table-column prop="time" label="时间" width="160" />
                <el-table-column prop="location" label="地点" />
                <el-table-column prop="type" label="类型" width="120" />
              </el-table>
            </el-card>
          </div>
        </el-tab-pane>
        <el-tab-pane label="赛事助手" name="competitions">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <el-card>
              <template #header>创建赛事</template>
              <div class="space-y-3">
                <el-input v-model="compForm.name" placeholder="赛事名称" />
                <div class="flex gap-3">
                  <el-date-picker v-model="compForm.time" type="date" placeholder="开始时间" style="width: 180px" />
                  <el-date-picker v-model="compForm.end_time" type="date" placeholder="结束时间" style="width: 180px" />
                </div>
                <el-input v-model="compForm.location" placeholder="地点" />
                <el-input v-model="compForm.type" placeholder="类型" />
                <el-button type="primary" @click="createCompetition" :loading="loading">创建赛事</el-button>
              </div>
            </el-card>
            <el-card>
              <template #header>赛事查询</template>
              <div class="flex items-center gap-3 mb-3">
                <el-select v-model="compFilters.status" placeholder="状态" clearable style="width: 160px">
                  <el-option label="草稿" value="DRAFT" />
                  <el-option label="待确认" value="PENDING" />
                  <el-option label="已确认" value="APPROVED" />
                  <el-option label="已驳回" value="REJECTED" />
                </el-select>
                <el-input v-model="compFilters.name" placeholder="名称包含" />
                <el-button type="primary" @click="loadCompetitions" :loading="loading">搜索</el-button>
              </div>
              <el-table :data="compList" size="small" v-loading="loading">
                <el-table-column prop="name" label="赛事名称" />
                <el-table-column prop="status" label="状态" width="120" />
                <el-table-column prop="time" label="开始时间" width="160" />
                <el-table-column prop="end_time" label="结束时间" width="160" />
                <el-table-column prop="location" label="地点" />
                <el-table-column prop="type" label="类型" width="120" />
              </el-table>
            </el-card>
          </div>
        </el-tab-pane>
        <el-tab-pane label="日报助手" name="daily_reports">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <el-card>
              <template #header>生成日报</template>
              <div class="space-y-3">
                <div class="text-sm text-slate-500 mb-2">请输入今日工作要点、关键词或草稿，AI将为您生成结构化日报。</div>
                <el-input v-model="dailyReportInput" type="textarea" :rows="8" placeholder="例如：
1. 完成了商机跟进模块的API开发
2. 修复了首页加载慢的问题
3. 明日计划：联调前端页面" />
                <el-button type="primary" @click="generateDailyReport" :loading="loading" class="w-full">生成日报</el-button>
              </div>
            </el-card>
            <el-card>
              <template #header>日报预览与保存</template>
              <div v-if="dailyReportResult" class="space-y-4">
                 <div>
                    <div class="text-xs text-slate-500 mb-1">标题</div>
                    <el-input v-model="dailyReportResult.title" />
                 </div>
                 <div>
                    <div class="text-xs text-slate-500 mb-1">内容 (Markdown)</div>
                    <el-input v-model="dailyReportResult.content" type="textarea" :rows="10" />
                 </div>
                 <div class="flex items-center gap-3">
                    <el-date-picker v-model="dailyReportResult.date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 160px" />
                    <el-button type="success" @click="saveGeneratedReport" :loading="loading">保存日报</el-button>
                 </div>
              </div>
              <div v-else class="h-64 flex items-center justify-center text-slate-400 text-sm border-2 border-dashed border-slate-200 rounded">
                生成结果将显示在这里
              </div>
            </el-card>
          </div>
        </el-tab-pane>
      </el-tabs>
      <div v-if="chosen.intent && chosen.entity" class="mt-6">
        <el-card>
          <template #header>智能执行面板</template>
          <div class="space-y-4">
            <div v-if="warnings.length" class="mb-2">
              <el-alert v-for="(w, i) in warnings" :key="i" :title="w" type="warning" show-icon :closable="false" class="mb-2" />
            </div>
            <div class="text-sm text-slate-600">当前选择：{{ humanLabel(chosen) }}</div>
            <div class="flex items-center gap-3">
              <el-input v-model="refineText" placeholder="补充说明（如：行业改为教育，区域北京）" style="max-width: 360px" />
              <el-button @click="refineFields">解析补充</el-button>
              <el-button type="success" @click="executeChosenWithFields" :loading="loading">确认执行</el-button>
              <el-button v-if="chosen.entity==='customer' && chosen.intent==='create'" @click="openOriginalForm">打开原表单（预填）</el-button>
            </div>
            <!-- 动态表单渲染 -->
            <div v-if="chosen.entity==='customer' && chosen.intent==='create'" class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <el-input v-model="execFields.name" placeholder="客户名称" />
              <el-input v-model="execFields.industry" placeholder="行业" />
              <el-input v-model="execFields.region" placeholder="区域" />
              <el-select v-model="execFields.status" placeholder="客户状态">
                <el-option label="潜在客户" value="POTENTIAL" />
                <el-option label="合作中" value="ACTIVE" />
                <el-option label="重点客户" value="KEY" />
                <el-option label="流失客户" value="CHURNED" />
              </el-select>
            </div>
            <div v-else-if="chosen.entity==='approvals' && (chosen.intent==='approve' || chosen.intent==='reject')" class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <el-input v-model="execFields.id" placeholder="审批ID" />
              <el-input v-model="execFields.reason" placeholder="审批备注" />
            </div>
            <div v-else-if="chosen.entity==='activity' && chosen.intent==='create'" class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <el-input v-model="execFields.name" placeholder="活动名称" />
              <el-date-picker v-model="execFields.time" type="date" placeholder="活动时间" />
              <el-input v-model="execFields.location" placeholder="活动地点" />
              <el-input v-model="execFields.type" placeholder="活动类型" />
              <el-input v-model="execFields.scale" placeholder="规模（可选）" />
            </div>
            <div v-else-if="chosen.entity==='competition' && chosen.intent==='create'" class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div><div class="text-xs text-slate-500 mb-1">赛事名称</div><el-input v-model="execFields.name" /></div>
              <div><div class="text-xs text-slate-500 mb-1">开始时间</div><el-date-picker v-model="execFields.time" type="date" /></div>
              <div><div class="text-xs text-slate-500 mb-1">结束时间</div><el-date-picker v-model="execFields.end_time" type="date" /></div>
              <div><div class="text-xs text-slate-500 mb-1">地点</div><el-input v-model="execFields.location" /></div>
              <div><div class="text-xs text-slate-500 mb-1">类型</div><el-input v-model="execFields.type" /></div>
              <div><div class="text-xs text-slate-500 mb-1">队伍数量</div><el-input v-model="execFields.team_count" /></div>
              <div><div class="text-xs text-slate-500 mb-1">题目数量</div><el-input v-model="execFields.challenge_count" /></div>
              <div><div class="text-xs text-slate-500 mb-1">赛制</div><el-select v-model="execFields.system_format">
                <el-option label="CTF" value="CTF" />
                <el-option label="AWD" value="AWD" />
                <el-option label="攻防演练" value="攻防演练" />
              </el-select></div>
              <div><div class="text-xs text-slate-500 mb-1">主办类型</div><el-select v-model="execFields.host_type">
                <el-option label="集团" value="Group" />
                <el-option label="学校" value="School" />
                <el-option label="政府/协会" value="Gov" />
              </el-select></div>
              <div><div class="text-xs text-slate-500 mb-1">级别</div><el-select v-model="execFields.level">
                <el-option label="国家级" value="National" />
                <el-option label="省级" value="Province" />
                <el-option label="市级" value="City" />
              </el-select></div>
              <div><div class="text-xs text-slate-500 mb-1">影响力</div><el-select v-model="execFields.impact_level">
                <el-option label="国家级" value="国家级" />
                <el-option label="省级" value="省级" />
                <el-option label="市级" value="市级" />
              </el-select></div>
              <div><div class="text-xs text-slate-500 mb-1">面向对象</div><el-select v-model="execFields.target_audience">
                <el-option label="高校" value="高校" />
                <el-option label="企业" value="企业" />
                <el-option label="政府" value="政府" />
              </el-select></div>
              <div><div class="text-xs text-slate-500 mb-1">行业</div><el-select v-model="execFields.industry">
                <el-option label="能源" value="能源" />
                <el-option label="教育" value="教育" />
                <el-option label="政府" value="政府" />
                <el-option label="其他" value="其他" />
              </el-select></div>
            </div>
            <div v-else-if="chosen.entity==='opportunity' && chosen.intent==='create'" class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <div class="text-xs text-slate-500 mb-1">商机名称</div>
                <el-input v-model="execFields.name" />
              </div>
              <div>
                <div class="text-xs text-slate-500 mb-1">客户名称</div>
                <el-input v-model="execFields.customer_name" />
              </div>
              <div v-if="chosen.intent==='create' && chosen.entity==='customer'">
                <div class="text-xs text-slate-500 mb-1">客户代号</div>
                <div class="flex gap-2">
                  <el-input v-model="execFields.customer_code" placeholder="例如：CUST-20251212-ABCD" />
                  <el-button type="primary" link @click="genCustomerCode">生成</el-button>
                </div>
              </div>
              <div v-if="execFields.customer_name && chosen.entity!=='customer'">
                 <div class="text-xs text-slate-500 mb-1">客户ID（自动匹配）</div>
                 <el-input v-model="execFields.customer" disabled />
              </div>
              <div>
                <div class="text-xs text-slate-500 mb-1">销售经理（ID）</div>
                <div class="flex gap-2">
                  <el-input v-model="execFields.sales_manager" placeholder="留空默认当前用户" class="w-24" />
                  <el-input v-model="execFields.sales_manager_name" placeholder="销售姓名" readonly />
                </div>
              </div>
              <div>
                <div class="text-xs text-slate-500 mb-1">金额（数字）</div>
                <el-input v-model="execFields.amount" />
              </div>
              <div>
                <div class="text-xs text-slate-500 mb-1">预计签约日期（可选）</div>
                <el-date-picker v-model="execFields.expected_sign_date" type="date" />
              </div>
              <div>
                <div class="text-xs text-slate-500 mb-1">阶段</div>
                <el-select v-model="execFields.stage">
                  <el-option label="初次接触" value="CONTACT" />
                  <el-option label="演示交流" value="DEMO" />
                  <el-option label="方案提交" value="PROPOSAL" />
                  <el-option label="商务谈判" value="NEGOTIATION" />
                  <el-option label="临门一脚" value="CLOSING" />
                </el-select>
              </div>
              <div>
                <div class="text-xs text-slate-500 mb-1">状态</div>
                <el-select v-model="execFields.status">
                  <el-option label="进行中" value="ACTIVE" />
                  <el-option label="潜在" value="POTENTIAL" />
                  <el-option label="已赢单" value="WON" />
                  <el-option label="已输单" value="LOST" />
                </el-select>
              </div>
              <div class="md:col-span-2">
                <div class="text-xs text-slate-500 mb-1">描述（可选）</div>
                <el-input v-model="execFields.description" type="textarea" :rows="3" />
              </div>
            </div>
            <div v-else class="text-xs text-slate-500">暂不支持该动作的可视化表单，您可直接执行或切换卡片。</div>
          </div>
        </el-card>
      </div>
    </main>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../../api';
import { ElMessage } from 'element-plus';

const tab = ref('approvals');
const loading = ref(false);

// 审批
const approvals = ref<any[]>([]);
const approvalStatus = ref<string>('');
const selectedApprovalIds = ref<number[]>([]);
const rowOpinion = ref<Record<number,string>>({});
const bulkReason = ref('');
function onApprovalSelection(rows:any[]){ selectedApprovalIds.value = rows.map(r => r.id); }
const preset = ref<string>('');
function presetPending(){ preset.value = 'pending'; approvalStatus.value=''; loadApprovals(); }
function presetHandled(){ preset.value = 'handled'; approvalStatus.value=''; loadApprovals(); }
async function loadApprovals(){
  loading.value = true;
  try{
    const params:any = {}; 
    if (approvalStatus.value) params.status = approvalStatus.value;
    if (preset.value === 'handled') params.status = ['APPROVED','REJECTED'];
    if (preset.value === 'pending') params.status = ['PENDING'];
    const res = await api.get('approvals/', { params });
    approvals.value = res.data.results || res.data || [];
  }catch(e){ console.error(e); ElMessage.error('加载失败'); } finally{ loading.value = false; }
}
async function approve(row:any){
  try{ await api.post(`approvals/${row.id}/approve/`, { reason: rowOpinion.value[row.id] || '' }); ElMessage.success('已通过'); loadApprovals(); }catch(e){ ElMessage.error('操作失败'); }
}
async function reject(row:any){
  try{ await api.post(`approvals/${row.id}/reject/`, { reason: rowOpinion.value[row.id] || '' }); ElMessage.success('已驳回'); loadApprovals(); }catch(e){ ElMessage.error('操作失败'); }
}
async function bulkApprove(){
  try{
    await api.post('approvals/bulk_approve/', { ids: selectedApprovalIds.value, reason: bulkReason.value });
    ElMessage.success('批量通过完成'); loadApprovals();
  }catch(e){ ElMessage.error('批量失败'); }
}
async function bulkReject(){
  try{
    await api.post('approvals/bulk_reject/', { ids: selectedApprovalIds.value, reason: bulkReason.value });
    ElMessage.success('批量驳回完成'); loadApprovals();
  }catch(e){ ElMessage.error('批量失败'); }
}

// 客户
const custForm = ref<any>({ name:'', industry:'', region:'', status:'POTENTIAL' });
const custSearch = ref(''); const customerList = ref<any[]>([]);
async function createCustomer(){
  if (!custForm.value.name){ ElMessage.warning('请输入客户名称'); return; }
  loading.value = true;
  try{
    // @ts-ignore
    const res = await api.post('chat/', { intent: 'create', entity: 'customer', fields: { ...custForm.value } });
    if (res) {
        // use res
    }
    ElMessage.success('创建成功');
  }catch(e){ console.error(e); ElMessage.error('创建失败'); }
  finally{ loading.value = false; }
}
async function listCustomers(){
  loading.value = true;
  try{
    const res = await api.post('chat/', { intent: 'list', entity: 'customer', filters: { name: custSearch.value, industry: custSearch.value } });
    customerList.value = res.data.result || [];
  }catch(e){ console.error(e); ElMessage.error('查询失败'); }
  finally{ loading.value = false; }
}

// 商机（AI识别）
const oppText = ref(''); const oppParsed = ref<any>(null);
async function aiParseOpportunity(){
  if (!oppText.value){ ElMessage.warning('请输入商机描述'); return; }
  loading.value = true;
  try{
    const res = await api.post('ai/analyze/', { text: oppText.value, mode: 'OPPORTUNITY' });
    if (res.data.error){ ElMessage.error(res.data.error); } else { oppParsed.value = res.data; ElMessage.success('识别成功'); }
  }catch(e){ console.error(e); ElMessage.error('识别失败'); } finally{ loading.value = false; }
}
async function createOpportunity(){
  if (!oppParsed.value){ ElMessage.warning('请先识别商机'); return; }
  loading.value = true;
  try{
    const payload:any = { ...oppParsed.value };
    if (!payload.description && oppText.value) payload.description = oppText.value;
    // @ts-ignore
    const res = await api.post('opportunities/', payload);
    if (res) {
        // use res
    }
    ElMessage.success('商机创建成功');
  }catch(e){ console.error(e); ElMessage.error('创建失败'); } finally{ loading.value = false; }
}
const actFilters = ref<any>({ status: '', name: '' });
const actList = ref<any[]>([]);
const actForm = ref<any>({ name:'', time:'', location:'', type:'', scale:'' });
async function loadActivities(){
  loading.value = true;
  try{
    const res = await api.post('chat/', { intent: 'list', entity: 'activity', filters: { ...actFilters.value } });
    actList.value = res.data.result || [];
  }catch(e){ console.error(e); ElMessage.error('查询失败'); } finally{ loading.value = false; }
}
async function createActivity(){
  if (!actForm.value.name){ ElMessage.warning('请输入活动名称'); return; }
  loading.value = true;
  try{
    await api.post('chat/', { intent: 'create', entity: 'activity', fields: { ...actForm.value } });
    ElMessage.success('创建成功');
    await loadActivities();
  }catch(e){ console.error(e); ElMessage.error('创建失败'); } finally{ loading.value = false; }
}
const compFilters = ref<any>({ status: '', name: '' });
const compList = ref<any[]>([]);
const compForm = ref<any>({ name:'', time:'', end_time:'', location:'', type:'' });
async function loadCompetitions(){
  loading.value = true;
  try{
    const res = await api.post('chat/', { intent: 'list', entity: 'competition', filters: { ...compFilters.value } });
    compList.value = res.data.result || [];
  }catch(e){ console.error(e); ElMessage.error('查询失败'); } finally{ loading.value = false; }
}
async function createCompetition(){
  if (!compForm.value.name){ ElMessage.warning('请输入赛事名称'); return; }
  loading.value = true;
  try{
    await api.post('chat/', { intent: 'create', entity: 'competition', fields: { ...compForm.value } });
    ElMessage.success('创建成功');
    await loadCompetitions();
  }catch(e){ console.error(e); ElMessage.error('创建失败'); } finally{ loading.value = false; }
}
// 智能体
const agentText = ref('');
const agentAlternatives = ref<any[]>([]);
const agentResult = ref<any>(null);
const warnings = ref<string[]>([]);
const chosen = ref<any>({ intent:'', entity:'', fields:{}, filters:{} });
const agentConfigId = ref<string>('');
const showRaw = ref(false);
const aiConfigs = ref<any[]>([]);
function cLabel(c:any){ return `${c.name} · ${c.model_name}${c.is_active ? '（默认）' : ''}`; }
async function loadAIConfigs(){
  try{
    const res = await api.get('ai/configs/');
    aiConfigs.value = res.data.results || [];
    if (!agentConfigId.value && aiConfigs.value.length){
      const active = aiConfigs.value.find((c:any)=>c.is_active);
      agentConfigId.value = String((active || aiConfigs.value[0]).id);
    }
  }catch(e){ /* 忽略 */ }
}
onMounted(loadAIConfigs);
async function testAI(){
  loading.value = true;
  try{
    const params:any = {};
    if (agentConfigId.value) params.config_id = agentConfigId.value;
    const res = await api.get('ai/test-connection/', { params });
    const r = res.data || {};
    ElMessage.success(`连接成功：${r.provider} · ${r.model}`);
    showRaw.value = true;
    agentResult.value = r;
  }catch(e:any){
    const msg = (e.response && e.response.data && (e.response.data.error || e.response.data.detail)) ? (e.response.data.error || e.response.data.detail) : '连接失败';
    ElMessage.error(typeof msg==='string'?msg:JSON.stringify(msg));
  } finally { loading.value = false; }
}
// @ts-ignore
function needsForm(a:any){
  // 所有动作都需要进入“智能执行面板”确认后提交，避免自动执行
  return true;
}
const execFields = ref<any>({});
const refineText = ref('');
async function analyzeAgent(){
  if (!agentText.value){ ElMessage.warning('请输入需求'); return; }
  loading.value = true;
  try{
    const payload:any = { text: agentText.value };
    if (agentConfigId.value) payload.config_id = agentConfigId.value;
    const res = await api.post('agent/route/', payload);
    const data = res.data || {};
    agentResult.value = data;
    if (data.error){
      // 服务器返回错误但HTTP成功 → 启用兜底
      const t = agentText.value;
      if (/商机|机会/.test(t)){
        chosen.value = { intent:'create', entity:'opportunity', fields:{}, filters:{} };
        await autoRefineOpportunity(t);
        ElMessage.warning('模型错误，已使用本地兜底识别商机并填表');
      } else if (/赛事|比赛/.test(t)){
        chosen.value = { intent:'create', entity:'competition', fields:{}, filters:{} };
        await autoRefineCompetition(t);
        ElMessage.warning('模型错误，已使用本地兜底识别赛事并填表');
      } else if (/客户/.test(t) && (/新建|创建/.test(t) || /名称/.test(t))){
        chosen.value = { intent:'create', entity:'customer', fields:{}, filters:{} };
        await autoRefineCustomer(t);
        ElMessage.warning('模型错误，已使用本地兜底识别客户并填表');
      } else if (/活动/.test(t) && (/新建|创建/.test(t) || /名称/.test(t))){
        chosen.value = { intent:'create', entity:'activity', fields:{}, filters:{} };
        await autoRefineActivity(t);
        ElMessage.warning('模型错误，已使用本地兜底识别活动并填表');
      } else {
        ElMessage.error(typeof data.error==='string'?data.error:JSON.stringify(data.error));
      }
    } else {
      chosen.value = { intent: data.intent, entity: data.entity, fields: data.fields || {}, filters: data.filters || {} };
      agentAlternatives.value = data.alternatives || [];
      warnings.value = data.warnings || [];
      // 自动填充建议字段到表单
      execFields.value = { ...(data.fields || {}) };
      // 商机创建：自动进行一次AI补全（金额/客户等）
      if (chosen.value.entity === 'opportunity' && chosen.value.intent === 'create'){
        await autoRefineOpportunity(agentText.value);
      }
      // 赛事创建：自动进行一次AI补全（时间/地点/赛制等）
      if (chosen.value.entity === 'competition' && chosen.value.intent === 'create'){
        await autoRefineCompetition(agentText.value);
      }
      // 如果没有候选且选择为空，兜底
      if ((!chosen.value.intent || !chosen.value.entity) && (!agentAlternatives.value || !agentAlternatives.value.length)){
        const t = agentText.value;
        if (/商机|机会/.test(t)){
          chosen.value = { intent:'create', entity:'opportunity', fields:{}, filters:{} };
          await autoRefineOpportunity(t);
          ElMessage.warning('未识别到明确动作，已兜底为“新建·商机”');
        } else if (/赛事|比赛/.test(t)){
          chosen.value = { intent:'create', entity:'competition', fields:{}, filters:{} };
          await autoRefineCompetition(t);
          ElMessage.warning('未识别到明确动作，已兜底为“新建·赛事”');
        } else if (/客户/.test(t) && (/新建|创建/.test(t) || /名称/.test(t))){
          chosen.value = { intent:'create', entity:'customer', fields:{}, filters:{} };
          await autoRefineCustomer(t);
          ElMessage.warning('未识别到明确动作，已兜底为“新建·客户”');
        } else if (/活动/.test(t) && (/新建|创建/.test(t) || /名称/.test(t))){
          chosen.value = { intent:'create', entity:'activity', fields:{}, filters:{} };
          await autoRefineActivity(t);
          ElMessage.warning('未识别到明确动作，已兜底为“新建·活动”');
        }
      }
      ElMessage.success('分析完成');
    }
  }catch(e:any){ 
    console.error(e); 
    const msg = (e.response && e.response.data && (e.response.data.error || e.response.data.detail)) ? (e.response.data.error || e.response.data.detail) : '分析失败';
    ElMessage.error(typeof msg==='string'?msg:JSON.stringify(msg));
    // 本地兜底：根据文本关键词给出可执行候选并自动填表
    try{
      const t = agentText.value;
      if (/商机|机会/.test(t)){
        chosen.value = { intent:'create', entity:'opportunity', fields:{}, filters:{} };
        await autoRefineOpportunity(t);
        agentResult.value = { fallback: true, intent: 'create', entity: 'opportunity' };
        ElMessage.warning('已使用本地兜底识别商机并填表，请确认后提交');
      } else if (/赛事|比赛/.test(t)){
        chosen.value = { intent:'create', entity:'competition', fields:{}, filters:{} };
        await autoRefineCompetition(t);
        agentResult.value = { fallback: true, intent: 'create', entity: 'competition' };
        ElMessage.warning('已使用本地兜底识别赛事并填表，请确认后提交');
      } else if (/客户/.test(t) && (/新建|创建/.test(t) || /名称/.test(t))){
        chosen.value = { intent:'create', entity:'customer', fields:{}, filters:{} };
        await autoRefineCustomer(t);
        agentResult.value = { fallback: true, intent: 'create', entity: 'customer' };
        ElMessage.warning('已使用本地兜底识别客户并填表，请确认后提交');
      } else if (/活动/.test(t) && (/新建|创建/.test(t) || /名称/.test(t))){
        chosen.value = { intent:'create', entity:'activity', fields:{}, filters:{} };
        await autoRefineActivity(t);
        agentResult.value = { fallback: true, intent: 'create', entity: 'activity' };
        ElMessage.warning('已使用本地兜底识别活动并填表，请确认后提交');
      }
    }catch(_){}
  } finally{ loading.value = false; }
}
function chooseAlternative(alt:any){
  chosen.value = { intent: alt.intent, entity: alt.entity, fields: alt.fields || {}, filters: alt.filters || {} };
}
async function autoRefineCustomer(text:string){
   const mName = text.match(/客户名称[:：]\s*([^\s，,]+)/) || text.match(/新建客户[，,]\s*([^\s，,]{2,40})/);
   if (mName) execFields.value.name = mName[1];
   const mInd = text.match(/行业[:：]\s*([^\s，,]+)/);
   if (mInd) execFields.value.industry = mInd[1];
   const mReg = text.match(/区域[:：]\s*([^\s，,]+)/) || text.match(/在([^\s，,]{1,10})/);
   if (mReg) execFields.value.region = mReg[1];
}
async function autoRefineActivity(text:string){
   const mName = text.match(/活动名称[:：]\s*([^\s，,]+)/) || text.match(/新建(?:一个|一项)?([^\s，,]{2,40})/);
   if (mName) execFields.value.name = mName[1];
   const mLoc = text.match(/地点[:：]\s*([^\s，,]+)/) || text.match(/在([^\s，,]{1,10})/);
   if (mLoc) execFields.value.location = mLoc[1];
   const mType = text.match(/类型[:：]\s*([^\s，,]+)/);
   if (mType) execFields.value.type = mType[1];
   const mDate = text.match(/(\d{4})[-年](\d{1,2})[-月](\d{1,2})/);
   if (mDate) execFields.value.time = `${mDate[1]}-${String(mDate[2]).padStart(2,'0')}-${String(mDate[3]).padStart(2,'0')}`;
}
async function autoRefineOpportunity(text:string){
  try{
    const payload:any = { text, mode: 'OPPORTUNITY' };
    if (agentConfigId.value) payload.config_id = agentConfigId.value;
    let data:any = {};
    try{
      const res = await api.post('ai/analyze/', payload);
      data = res.data || {};
    }catch{}
    execFields.value = { ...(execFields.value || {}), ...(data.error ? {} : data) };
    // 本地兜底：客户名/名称
    if (!execFields.value.customer_name){
      const m = text.match(/客户名称[:：]\s*([^\s，,]+)/) || text.match(/新增(?:一个|一条|一项)?([^\s，,]{2,40})的商机/) || text.match(/([^\s，,]{2,40})商机/);
      if (m) execFields.value.customer_name = m[1];
    }
    if (!execFields.value.name){
      const cname = execFields.value.customer_name || '';
      execFields.value.name = cname ? `${cname}-咨询比赛与演武场` : '咨询比赛与演武场';
    }
    // 金额
    if (!execFields.value.amount){
      const m = text.match(/(预算|金额)\s*([0-9]+(?:\.[0-9]+)?)\s*(千|万|百万|亿)?/);
      if (m){
        // @ts-ignore
        const num = parseFloat(m[2]); const unit = m[3] || '';
        const unitMap:any = { '千':1000,'万':10000,'百万':1000000,'亿':100000000 };
        execFields.value.amount = Math.round(num * (unitMap[unit] || 1));
      } else { execFields.value.amount = 0; }
    }
    // 销售经理
    if (!execFields.value.sales_manager_name){
        const m = text.match(/销售([^\s，,]{2,10})/);
        if (m) execFields.value.sales_manager_name = m[1];
    }
    // 季度 → 预计签约日期
    if (!execFields.value.expected_sign_date){
      const mq = text.match(/明年?\s*Q([1-4])/i) || text.match(/Q([1-4])/i);
      if (mq){
      // @ts-ignore
      const q = parseInt(mq[1],10);
      const middleMonth:any = {1:2,2:5,3:8,4:11}[q];
      const now = new Date(); const y = /明年/.test(text) ? now.getFullYear()+1 : now.getFullYear();
        const pad = (n:number)=>String(n).padStart(2,'0');
        execFields.value.expected_sign_date = `${y}-${pad(middleMonth)}-15`;
      }
    }
    // 阶段/状态
    if (!execFields.value.stage){
      if (/演示/.test(text)) execFields.value.stage = 'DEMO';
      else if (/方案/.test(text)) execFields.value.stage = 'PROPOSAL';
      else if (/谈判/.test(text)) execFields.value.stage = 'NEGOTIATION';
      else if (/临门|签约/.test(text)) execFields.value.stage = 'CLOSING';
      else execFields.value.stage = 'CONTACT';
    }
    // 区域
    if (!execFields.value.customer_region){
      const r1 = text.match(/区域[:：]\s*([^\s，,]+)/);
      const r2 = text.match(/在([^\s，,]{1,10})/);
      if (r1) execFields.value.customer_region = r1[1];
      else if (r2) execFields.value.customer_region = r2[1];
    }
  }catch(e){ /* 忽略失败 */ }
}
async function autoRefineCompetition(text:string){
  try{
    const payload:any = { text, mode: 'COMPETITION' };
    if (agentConfigId.value) payload.config_id = agentConfigId.value;
    let data:any = {};
    try{
      const res = await api.post('ai/analyze/', payload);
      data = res.data || {};
    }catch{}
    execFields.value = { ...(execFields.value || {}), ...(data.error ? {} : data) };
    // 名称
    if (!execFields.value.name){
      const m = text.match(/赛事名称[:：]\s*([^\s，,]+)/) || text.match(/新建(?:一个|一项)?([^\s，,]{2,40})/);
      if (m) execFields.value.name = m[1];
    }
    // 兜底解析模糊时间（上旬/中旬/下旬）
    const fuzzy = text.match(/(\d{1,2})月(上旬|中旬|下旬)/);
    if (fuzzy){
      // @ts-ignore
      const m = parseInt(fuzzy[1],10); const mp:any = { '上旬':5,'中旬':15,'下旬':25 };
      // @ts-ignore
      const d = mp[fuzzy[2]];
      const now = new Date(); const y = /明年/.test(text) ? now.getFullYear()+1 : now.getFullYear();
      const pad = (n:number)=>String(n).padStart(2,'0');
      const ds = `${y}-${pad(m)}-${pad(d)}`;
      if (!execFields.value.time) execFields.value.time = ds;
      if (!execFields.value.end_time) execFields.value.end_time = ds;
    }
    // 兜底解析季度（Q1/Q2/Q3/Q4 → 当季中期）
    const mq = text.match(/Q([1-4])/i);
    if (mq){
      // @ts-ignore
      const q = parseInt(mq[1],10);
      const middleMonth:any = {1:2,2:5,3:8,4:11}[q];
      const now = new Date(); const y = /明年/.test(text) ? now.getFullYear()+1 : now.getFullYear();
      const pad = (n:number)=>String(n).padStart(2,'0');
      const ds = `${y}-${pad(middleMonth)}-15`;
      if (!execFields.value.time) execFields.value.time = ds;
      if (!execFields.value.end_time) execFields.value.end_time = ds;
    }
    // 兜底解析“X天”并根据开始时间自动计算结束时间
    if (execFields.value.time && !execFields.value.end_time){
      const dmatch = text.match(/(\d+)\s*天/);
      if (dmatch){
        // @ts-ignore
        const dur = parseInt(dmatch[1],10);
        const d0 = new Date(execFields.value.time);
        const dEnd = new Date(d0.getTime() + (Math.max(dur-1,0))*24*3600*1000);
        const pad = (n:number)=>String(n).padStart(2,'0');
        execFields.value.end_time = `${dEnd.getFullYear()}-${pad(dEnd.getMonth()+1)}-${pad(dEnd.getDate())}`;
      }
    }
    // 面向对象/行业/影响力标签兜底
    if (!execFields.value.target_audience){
      if (/高校|大学/.test(text)) execFields.value.target_audience = '高校';
      else if (/企业/.test(text)) execFields.value.target_audience = '企业';
      else if (/政府/.test(text)) execFields.value.target_audience = '政府';
    }
    if (!execFields.value.industry){
      if (/电力|能源/.test(text)) execFields.value.industry = '能源';
    }
    if (!execFields.value.impact_level){
      if (/全国/.test(text)) execFields.value.impact_level = '国家级';
      else if (/省/.test(text)) execFields.value.impact_level = '省级';
      else if (/市/.test(text)) execFields.value.impact_level = '市级';
    }
    // 兜底解析地点：匹配“在XX”
    const ml = text.match(/在([^\s，,]{1,10})/);
    if (ml && !execFields.value.location) execFields.value.location = ml[1];
  }catch(e){ /* 忽略失败 */ }
}
async function refineFields(){
  if (!refineText.value){ ElMessage.warning('请输入补充说明'); return; }
  loading.value = true;
  try{
    if (chosen.value.entity === 'opportunity'){
      const payload:any = { text: refineText.value, mode: 'OPPORTUNITY' };
      if (agentConfigId.value) payload.config_id = agentConfigId.value;
      const res = await api.post('ai/analyze/', payload);
      const data = res.data || {};
      if (!data.error){
        execFields.value = { ...(execFields.value || {}), ...data };
        ElMessage.success('已合并AI识别结果');
      } else {
        ElMessage.warning('AI识别失败');
      }
    } else {
      const payload:any = { text: refineText.value };
      if (agentConfigId.value) payload.config_id = agentConfigId.value;
      const res = await api.post('agent/route/', payload);
      const data = res.data || {};
      if (data.entity && data.entity === chosen.value.entity && data.fields){
        execFields.value = { ...(execFields.value || {}), ...data.fields };
        ElMessage.success('已合并补充字段');
      } else {
        ElMessage.warning('补充内容与当前动作不一致，未合并');
      }
    }
  }catch(e){ console.error(e); ElMessage.error('解析失败'); } finally { loading.value = false; }
}
async function executeChosenWithFields(){
  if (!chosen.value.intent || !chosen.value.entity){ ElMessage.warning('请选择动作'); return; }
  loading.value = true;
  try{
    const payload = { intent: chosen.value.intent, entity: chosen.value.entity, fields: normalizeFields(chosen.value.entity, execFields.value || {}), filters: chosen.value.filters || {}, text: agentText.value || '' };
    const res = await api.post('chat/', payload);
    agentResult.value = res.data;
    ElMessage.success('执行完成');
  }catch(e){ 
    console.error(e); 
    // @ts-ignore
    const msg = (e.response && e.response.data && (e.response.data.error || e.response.data.detail)) ? JSON.stringify(e.response.data.error || e.response.data.detail) : '执行失败';
    ElMessage.error(typeof msg==='string'?msg:JSON.stringify(msg));
  } finally { loading.value = false; }
}
// @ts-ignore
function openOriginalForm(){
  // 仅支持客户新建表单的预填
  const q:any = {};
  if (execFields.value.name) q.name = execFields.value.name;
  if (execFields.value.industry) q.industry = execFields.value.industry;
  if (execFields.value.region) q.region = execFields.value.region;
  if (execFields.value.status) q.status = execFields.value.status;
  // 跳到客户创建页并附加 query
  window.location.hash = `#/crm/customers/create?` + new URLSearchParams(q).toString();
}
/** 统一日期/数字等字段的规范化，避免后端校验失败 */
// @ts-ignore
function normalizeFields(entity:string, fields:any){
  const f = { ...(fields || {}) };
  const toDate = (v:any) => {
    if (!v) return v;
    try{
      if (typeof v === 'string') return v; // 可能已是'YYYY-MM-DD'
      if (v instanceof Date) {
        const y = v.getFullYear(); const m = String(v.getMonth()+1).padStart(2,'0'); const d = String(v.getDate()).padStart(2,'0');
        return `${y}-${m}-${d}`;
    }
    }catch(_e){ return v; }
    return v;
};
  // competition/activity/opportunity日期字段
  f.time = toDate(f.time);
  f.end_time = toDate(f.end_time);
  f.expected_sign_date = toDate(f.expected_sign_date);
  // 金额确保为数字
  if (f.amount && typeof f.amount === 'string'){
    const n = Number(f.amount.replace(/[^\d.]/g,''));
    if (!isNaN(n)) f.amount = n;
  }
  return f;
}

async function genCustomerCode(){
  try {
    const res = await api.get('customers/generate_code/');
    execFields.value.customer_code = res.data.code;
  } catch(e){
    ElMessage.error('生成代号失败');
  }
}

function humanLabel(a:any){
  if (!a) return '';
  const intentMap: Record<string,string> = { list:'查看', get:'查看详情', create:'新建', update:'更新', approve:'审批通过', reject:'审批驳回' };
  const entityMap: Record<string,string> = { approvals:'审批', customer:'客户', activity:'活动', competition:'赛事', opportunity:'商机' };
  const intentLabel = intentMap[a.intent] || a.intent;
  const entityLabel = entityMap[a.entity] || a.entity;
  // status hint
  const status = a.filters?.status || a.fields?.status;
  const statusLabel = status ? `（${Array.isArray(status)?status.join('/') : status}）` : '';
  return `${intentLabel} · ${entityLabel}${statusLabel}`;
}
function humanDesc(a:any){
  if (!a) return '';
  const parts:string[] = [];
  if (a.filters && Object.keys(a.filters).length) parts.push(`筛选：${JSON.stringify(a.filters)}`);
  if (a.fields && Object.keys(a.fields).length) parts.push(`参数：${JSON.stringify(a.fields)}`);
  return parts.join('；');
}
function fillTemplate(type:string){
  if (type === 'approve'){
    agentText.value = '审批通过 123，原因：资料齐全';
  } else if (type === 'customer'){
    agentText.value = '新建客户，客户名称：示例公司，行业：教育，区域：北京';
  } else if (type === 'opportunity'){
    agentText.value = '新增一个三峡职业技术学院的商机，他们是老师，想了解一下比赛怎么搞，了解一下演武场。销售魏晶晶';
  }
}
async function executeChosen(){
  if (!chosen.value.intent || !chosen.value.entity){ ElMessage.warning('请选择动作'); return; }
  
  // Sync UI fields back to chosen payload
  chosen.value.fields = { ...chosen.value.fields, ...execFields.value };

  loading.value = true;
  try{
    const res = await api.post('chat/', chosen.value);
    agentResult.value = res.data;
    ElMessage.success('执行完成');
  }catch(e){ console.error(e); ElMessage.error('执行失败'); } finally { loading.value = false; }
}

// 日报助手
const dailyReportInput = ref('');
const dailyReportResult = ref<any>(null);

async function generateDailyReport() {
  if (!dailyReportInput.value) {
    ElMessage.warning('请输入工作内容');
    return;
  }
  loading.value = true;
  try {
    const payload: any = { text: dailyReportInput.value, mode: 'DAILY_REPORT' };
    if (agentConfigId.value) payload.config_id = agentConfigId.value;
    const res = await api.post('ai/analyze/', payload);
    const data = res.data;
    if (data.error) {
       ElMessage.error(data.error);
    } else {
       dailyReportResult.value = {
         title: data.title || `${new Date().getFullYear()}-${new Date().getMonth()+1}-${new Date().getDate()} 日报`,
         content: data.content || data.polished_content || dailyReportInput.value,
         date: new Date().toISOString().split('T')[0]
       };
       ElMessage.success('生成成功，请预览并保存');
    }
  } catch (e: any) {
    console.error(e);
    ElMessage.error('生成失败');
  } finally {
    loading.value = false;
  }
}

async function saveGeneratedReport() {
  if (!dailyReportResult.value) return;
  loading.value = true;
  try {
    // 关键修复：将 AI 生成的内容 (dailyReportResult.value.content) 同时保存到 raw_content 
    // 这样在工作日报板块编辑时，看到的就是 AI 生成后的结果，而不是原始输入的简略内容
    const payload = {
      date: dailyReportResult.value.date,
      title: dailyReportResult.value.title,
      raw_content: dailyReportResult.value.content, // 这里改为保存 AI 润色后的内容
      polished_content: '', // 清空润色内容，让系统默认显示 raw_content
      status: 'SUBMITTED'
    };
    // 这里调用 DailyReportViewSet 的 create 接口
    // 注意：后端 create 方法里有 upsert 逻辑，所以如果是同一天会更新
    await api.post('daily-reports/', payload);
    ElMessage.success('保存成功，已同步至工作日报');
    // 清空
    dailyReportInput.value = '';
    dailyReportResult.value = null;
  } catch (e: any) {
    console.error(e);
    ElMessage.error('保存失败');
  } finally {
    loading.value = false;
  }
}
</script>
