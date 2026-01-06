<template>
  <div class="h-screen flex flex-col bg-slate-50 overflow-hidden">
    <!-- Navbar -->
    <header class="bg-white shadow-sm px-6 py-4 flex justify-between items-center shrink-0 z-10">
      <div class="flex items-center gap-4">
        <h1 class="text-xl font-bold text-slate-800">{{ isEdit ? '编辑商机' : '新建商机' }}</h1>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">大屏首页</el-breadcrumb-item>
          <el-breadcrumb-item :to="{ path: '/crm/opportunities' }">商机列表</el-breadcrumb-item>
          <el-breadcrumb-item>{{ isEdit ? '编辑' : '新建' }}</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="flex items-center gap-4">
        <el-button @click="router.back()">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">保存</el-button>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1 p-6 overflow-auto">
      <div class="bg-white rounded-lg shadow p-8 max-w-4xl mx-auto">
        <el-form :model="form" label-width="120px" ref="formRef" :rules="rules">
            
          <!-- Basic Info -->
          <h3 class="text-lg font-bold text-slate-800 mb-6 pb-2 border-b">基本信息</h3>
          
          <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="商机名称" prop="name">
                    <el-input v-model="form.name" placeholder="请输入商机名称" />
                </el-form-item>
              </el-col>
              <el-col :span="10">
                <el-form-item label="客户公司" prop="customer_company">
                    <el-input v-model="form.customer_company" placeholder="请输入客户公司名称" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="客户代号" prop="customer_code">
                    <el-input v-model="form.customer_code" placeholder="代号" />
                </el-form-item>
              </el-col>
          </el-row>

          <!-- Existing Customer selector -->
          <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="选择客户" prop="customer">
                    <el-select
                        v-model="form.customer"
                        filterable
                        remote
                        reserve-keyword
                        :remote-method="searchCustomers"
                        :loading="custLoading"
                        placeholder="搜索并选择已有客户"
                        style="width: 320px"
                        @change="onCustomerSelected"
                    >
                        <el-option
                            v-for="item in customerOptions"
                            :key="item.value"
                            :label="item.label"
                            :value="item.value"
                        />
                    </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="联系人" prop="customer_contact_name">
                    <el-select v-model="form.customer_contact_name" placeholder="选择联系人" style="width: 100%" @change="onContactSelected">
                        <el-option v-for="p in contactOptions" :key="p.id" :label="p.label" :value="p.label" />
                    </el-select>
                </el-form-item>
              </el-col>
          </el-row>

          <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="预计金额" prop="amount">
                    <el-input-number v-model="form.amount" :min="0" :step="10000" style="width: 100%" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="当前阶段" prop="stage">
                    <el-select v-model="form.stage" placeholder="请选择阶段" style="width: 100%">
                        <el-option label="接触阶段" value="CONTACT" />
                        <el-option label="需求分析" value="REQ_ANALYSIS" />
                        <el-option label="客户立项" value="INITIATION" />
                        <el-option label="招采阶段" value="BIDDING" />
                        <el-option label="交付实施" value="DELIVERY" />
                        <el-option label="售后阶段" value="AFTER_SALES" />
                        <el-option label="项目完成" value="COMPLETED" />
                        <el-option label="商机暂停" value="SUSPENDED" />
                        <el-option label="商机终止" value="TERMINATED" />
                    </el-select>
                </el-form-item>
              </el-col>
          </el-row>

          <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="预计签约时间" prop="expected_sign_date">
                    <el-date-picker
                        v-model="form.expected_sign_date"
                        type="date"
                        placeholder="选择日期"
                        value-format="YYYY-MM-DD"
                        style="width: 100%"
                    />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="赢单概率(%)" prop="win_rate">
                    <el-slider v-model="form.win_rate" show-input />
                </el-form-item>
              </el-col>
          </el-row>

          <el-row :gutter="20">
              <el-col :span="12">
                  <el-form-item label="商机来源" prop="source">
                      <el-input v-model="form.source" placeholder="例如：老客户推荐" />
                  </el-form-item>
              </el-col>
              <el-col :span="12">
                  <el-form-item label="所属产线" prop="product_line">
                      <el-input v-model="form.product_line" placeholder="例如：网络靶场" />
                  </el-form-item>
              </el-col>
          </el-row>
          
          <el-row :gutter="20">
              <el-col :span="8">
                  <el-form-item label="客户行业" prop="customer_industry">
                      <el-input v-model="form.customer_industry" placeholder="例如：教育" />
                  </el-form-item>
              </el-col>
              <el-col :span="8">
                  <el-form-item label="客户区域" prop="customer_region">
                      <el-input v-model="form.customer_region" placeholder="例如：华北区" />
                  </el-form-item>
              </el-col>
              <el-col :span="8">
                  <el-form-item label="客户联系人" prop="customer_contact_name">
                      <el-input v-model="form.customer_contact_name" placeholder="姓名" />
                  </el-form-item>
              </el-col>
          </el-row>
          
          <el-row :gutter="20">
              <el-col :span="12">
                  <el-form-item label="联系电话" prop="customer_phone">
                      <el-input v-model="form.customer_phone" placeholder="电话/手机" />
                  </el-form-item>
              </el-col>
              <el-col :span="12">
                  <el-form-item label="邮箱" prop="customer_email">
                      <el-input v-model="form.customer_email" placeholder="Email" />
                  </el-form-item>
              </el-col>
          </el-row>

          <el-row :gutter="20">
              <el-col :span="12">
                  <el-form-item label="负责销售" v-if="isEdit">
                      <el-input v-model="form.sales_manager_name" disabled />
                  </el-form-item>
              </el-col>
              <el-col :span="12">
                  <el-form-item label="项目经理" prop="project_manager_name">
                      <el-input v-model="form.project_manager_name" placeholder="未指派或AI识别" />
                  </el-form-item>
              </el-col>
          </el-row>

          <!-- AI & Description Combined -->
          <h3 class="text-lg font-bold text-slate-800 mb-6 pb-2 border-b mt-6">商机详情 & AI 智能填充</h3>
          
          <div class="bg-blue-50 p-6 rounded-lg border border-blue-100 mb-6">
              <div class="flex justify-between items-center mb-2">
                  <label class="text-sm font-bold text-blue-800 flex items-center gap-2">
                      ✨ 商机描述 / AI 指令
                      <el-tooltip content="在此输入商机详情，点击右下角按钮，AI将自动提取关键信息填充到上方表单" placement="top">
                          <el-icon><InfoFilled /></el-icon>
                      </el-tooltip>
                  </label>
                  <el-button type="primary" size="small" @click="handleAIParse" :loading="aiLoading" icon="MagicStick">
                      AI 智能识别
                  </el-button>
              </div>
              <el-input 
                v-model="form.ai_raw_text" 
                type="textarea" 
                :rows="6" 
                placeholder="在此描述商机详情，例如：
歌者文明公司，42万，销售员卡拉米，做数字清洁服务。
目前处于需求分析阶段，预计下个月签约。
竞争对手有三体科技，赢单率大概80%。" 
              />
          </div>

          <!-- Extended Info (Hidden if empty and not expanded? No, keep visible for manual edit) -->
          <el-row :gutter="20">
              <el-col :span="24">
                  <el-form-item label="竞争对手" prop="competitors">
                      <el-input v-model="form.competitors" placeholder="多个对手请用逗号分隔" />
                  </el-form-item>
              </el-col>
          </el-row>

        </el-form>
        <div v-if="isEdit" class="mt-8">
          <el-tabs>
            <el-tab-pane label="项目组成员">
              <div class="mb-3 flex items-center gap-2">
                <el-select v-model="newMemberUser" filterable placeholder="选择成员" style="width: 260px">
                  <el-option v-for="u in userOptions" :key="u.id" :label="u.name" :value="u.id" />
                </el-select>
                <el-select v-model="newMemberRole" placeholder="角色" style="width: 180px">
                  <el-option label="普通成员" value="MEMBER" />
                  <el-option label="销售经理" value="SALES_REP" />
                  <el-option label="售前工程师" value="PRE_SALES" />
                  <el-option label="产品经理" value="PRODUCT" />
                </el-select>
                <el-button type="primary" size="small" @click="addMember" :loading="memberLoading">添加成员</el-button>
              </div>
              <el-table :data="members" size="small" v-loading="memberLoading">
                <el-table-column prop="user_name" label="成员" />
                <el-table-column prop="role_display" label="角色" />
                <el-table-column prop="workload" label="工时(人天)" width="120" />
                <el-table-column prop="start_date" label="进入时间" width="140" />
              </el-table>
            </el-tab-pane>
            <el-tab-pane label="跟进日志">
              <div class="mb-3 flex items-center gap-2">
                <el-select v-model="newLogStage" placeholder="阶段快照" style="width: 140px" @change="handleStageChange">
                  <el-option label="接触阶段" value="CONTACT" />
                  <el-option label="需求分析" value="REQ_ANALYSIS" />
                  <el-option label="客户立项" value="INITIATION" />
                  <el-option label="招采阶段" value="BIDDING" />
                  <el-option label="交付实施" value="DELIVERY" />
                  <el-option label="售后阶段" value="AFTER_SALES" />
                  <el-option label="项目完成" value="COMPLETED" />
                  <el-option label="商机暂停" value="SUSPENDED" />
                  <el-option label="商机终止" value="TERMINATED" />
                </el-select>
                <el-select v-model="newLogAction" placeholder="动作" style="width: 160px">
                  <el-option v-for="act in availableActions" :key="act" :label="act" :value="act" />
                </el-select>
                <el-input v-model="newLogContent" placeholder="请输入跟进内容" style="width: 320px" />
                <el-button type="primary" size="small" @click="addLog" :loading="logLoading">记录</el-button>
              </div>
              <el-table :data="logs" size="small" v-loading="logLoading">
                <el-table-column prop="action" label="动作" width="140" />
                <el-table-column prop="content" label="内容" />
                <el-table-column prop="created_at" label="时间" width="180">
                  <template #default="scope">{{ new Date(scope.row.created_at).toLocaleString() }}</template>
                </el-table-column>
                <el-table-column prop="operator_name" label="记录人" width="140" />
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../../api';
import { ElMessage } from 'element-plus';

const route = useRoute();
const router = useRouter();
const formRef = ref();
const loading = ref(false);
const aiLoading = ref(false);

const id = route.params.id;
const isEdit = computed(() => !!id);

const form = ref({
    name: '',
    customer_company: '',
    customer_code: '',
    customer: null,
    amount: 0,
    stage: 'CONTACT',
    expected_sign_date: '',
    ai_raw_text: '',
    sales_manager_name: '',
    win_rate: 0,
    source: '',
    description: '',
    competitors: '',
    // New fields
    product_line: '',
    customer_industry: '',
    customer_region: '',
    customer_contact_name: '',
    customer_phone: '',
    customer_email: '',
    project_manager_name: '' // Read-only for now or text input?
});

// Customer selector
const customerOptions = ref<any[]>([]);
const custLoading = ref(false);
const contactOptions = ref<any[]>([]);
const searchCustomers = async (query: string) => {
    custLoading.value = true;
    try {
        const res = await api.get('customers/', { params: { search: query } });
        const list = res.data.results || res.data;
        customerOptions.value = list.map((c: any) => ({
            label: `${c.name}${c.customer_code ? ' (' + c.customer_code + ')' : ''}`,
            value: c.id,
            name: c.name,
            code: c.customer_code
        }));
    } catch (e) {
        console.error(e);
    } finally {
        custLoading.value = false;
    }
};

const onCustomerSelected = async (val: any) => {
    const found = customerOptions.value.find((x: any) => x.value === val);
    if (found) {
        form.value.customer_company = found.name;
        form.value.customer_code = found.code || form.value.customer_code;
        try {
            const res = await api.get(`customers/${val}/`);
            const cust = res.data || {};
            form.value.customer_industry = cust.industry || form.value.customer_industry;
            const contacts = cust.contacts || [];
            contactOptions.value = contacts.map((c: any) => ({ id: c.id, name: c.name, phone: c.phone, email: c.email, label: `${c.name}${c.phone ? ' ' + c.phone : ''}` }));
        } catch (e) { console.error(e); }
    }
};

const loadCustomerContacts = async (id: number) => {
    try {
        const res = await api.get('contacts/', { params: { customer: id } });
        contactOptions.value = res.data.results || res.data;
    } catch (e) { console.error(e); }
};
// @ts-ignore
const _useLoadContacts = loadCustomerContacts;

const onContactSelected = (label: string) => {
    const found = contactOptions.value.find((x: any) => x.label === label);
    if (found) {
        form.value.customer_contact_name = found.name;
        form.value.customer_phone = found.phone || form.value.customer_phone;
        form.value.customer_email = found.email || form.value.customer_email;
    }
};


const rules = {
    name: [{ required: true, message: '请输入商机名称', trigger: 'blur' }],
    customer_company: [{ required: true, message: '请输入客户公司', trigger: 'blur' }],
    amount: [{ required: true, message: '请输入金额', trigger: 'blur' }],
};
// Team members & logs
const members = ref<any[]>([]);
const logs = ref<any[]>([]);
const memberLoading = ref(false);
const logLoading = ref(false);
const newMemberUser = ref<number|null>(null);
const newMemberRole = ref('MEMBER');
const newLogContent = ref('');
const newLogAction = ref('');
const newLogStage = ref('');
const availableActions = ref<string[]>([]);

const stageActionMap: Record<string, string[]> = {
    'CONTACT': ['初步接触', '资料发送', '预约拜访', '电话沟通'],
    'REQ_ANALYSIS': ['需求调研', '方案汇报', '技术交流', '客户痛点确认'],
    'INITIATION': ['客户立项', '预算确认', '立项审批', '招标参数确认'],
    'BIDDING': ['标书购买', '投标', '讲标/述标', '中标通知'],
    'DELIVERY': ['合同签订', '进场实施', '阶段汇报', '初验'],
    'AFTER_SALES': ['终验', '维保服务', '回款', '客户回访'],
    'COMPLETED': ['项目复盘', '资料归档'],
    'SUSPENDED': ['暂停说明', '重启计划'],
    'TERMINATED': ['中止说明', '丢单分析']
};

const handleStageChange = (val: string) => {
    availableActions.value = stageActionMap[val] || ['其他'];
    newLogAction.value = availableActions.value[0] || '';
};

const userOptions = ref<any[]>([]);

const fetchData = async () => {
    if (!isEdit.value) return;
    try {
        const res = await api.get(`opportunities/${id}/`);
        form.value = { ...res.data };
        // Preload customer display
        if (res.data.customer) {
            form.value.customer = res.data.customer;
        }
        // Load members & logs
        await fetchMembers();
        await fetchLogs();
    } catch (e) {
        ElMessage.error('获取详情失败');
    }
};
const fetchMembers = async () => {
  memberLoading.value = true;
  try {
    const res = await api.get('opportunity-team-members/', { params: { opportunity: id } });
    members.value = res.data.results || res.data || [];
  } catch (e){ console.error(e); } finally { memberLoading.value = false; }
};
const fetchLogs = async () => {
  logLoading.value = true;
  try {
    const res = await api.get('opportunity-logs/', { params: { opportunity: id } });
    logs.value = res.data.results || res.data || [];
  } catch (e){ console.error(e); } finally { logLoading.value = false; }
};
const fetchUsers = async () => {
  try { 
    const res = await api.get('users/simple/'); 
    userOptions.value = res.data.results || res.data || []; 
  } catch (e) {
    console.error('Fetch users error:', e);
  }
};
const addMember = async () => {
  if (!newMemberUser.value) { ElMessage.warning('请选择成员'); return; }
  memberLoading.value = true;
  try {
    await api.post('opportunity-team-members/', { opportunity: id, user: newMemberUser.value, role: newMemberRole });
    ElMessage.success('已添加成员');
    newMemberUser.value = null;
    await fetchMembers();
  } catch (e){ console.error(e); ElMessage.error('添加失败'); } finally { memberLoading.value = false; }
};
const addLog = async () => {
  if (!newLogContent.value) { ElMessage.warning('请输入内容'); return; }
  logLoading.value = true;
  try {
    await api.post('opportunity-logs/', { opportunity: id, content: newLogContent.value, action: newLogAction });
    ElMessage.success('已记录');
    newLogContent.value = '';
    await fetchLogs();
  } catch (e){ console.error(e); ElMessage.error('记录失败'); } finally { logLoading.value = false; }
};

const handleAIParse = async () => {
    if (!form.value.ai_raw_text) {
        ElMessage.warning('请先输入需要识别的文字内容');
        return;
    }
    aiLoading.value = true;
    try {
        const res = await api.post('ai/analyze/', {
            text: form.value.ai_raw_text,
            mode: 'OPPORTUNITY'
        });
        
        const data = res.data;
        if (data.error) {
            ElMessage.error('AI识别失败: ' + data.error);
        } else {
            // Auto fill form
            form.value.name = data.name || form.value.name;
            form.value.amount = data.amount || form.value.amount;
            form.value.customer_company = data.customer_name || form.value.customer_company;
            form.value.customer_code = data.customer_code || form.value.customer_code;
            form.value.stage = data.stage || form.value.stage;
            form.value.expected_sign_date = data.expected_sign_date || form.value.expected_sign_date;
            
            // Try to fill extended fields if AI returned them (Needs backend prompt update to support new fields)
            // Use ai_raw_text as description if description is empty
            if (data.description) {
                form.value.description = data.description;
            } else if (!form.value.description) {
                // If AI didn't return specific description, use the raw input as description
                form.value.description = form.value.ai_raw_text; 
            }
            
            if (data.win_rate) form.value.win_rate = data.win_rate;
            if (data.competitors) form.value.competitors = data.competitors;
            if (data.source) form.value.source = data.source;
            if (data.product_line) form.value.product_line = data.product_line;
            if (data.customer_industry) form.value.customer_industry = data.customer_industry;
            if (data.customer_region) form.value.customer_region = data.customer_region;
            if (data.customer_contact_name) form.value.customer_contact_name = data.customer_contact_name;
            if (data.customer_phone) form.value.customer_phone = data.customer_phone;
            if (data.customer_email) form.value.customer_email = data.customer_email;
            if (data.project_manager_name) form.value.project_manager_name = data.project_manager_name;
            
            ElMessage.success('AI 识别成功，请核对信息');
        }
    } catch (e) {
        ElMessage.error('AI 服务请求失败');
        console.error(e);
    } finally {
        aiLoading.value = false;
    }
};

const handleSubmit = async () => {
    if (!formRef.value) return;
    await formRef.value.validate(async (valid: boolean) => {
        if (valid) {
            loading.value = true;
            try {
                // Prepare payload
                const payload = { ...form.value };
                // Ensure customer_name is set for legacy compatibility
                // @ts-ignore
                if (!payload.customer_name) {
                    // @ts-ignore
                    payload.customer_name = payload.customer_company;
                }
                // If selected customer id exists, keep it; otherwise backend will try to match by name

                if (isEdit.value) {
                    await api.patch(`opportunities/${id}/`, payload);
                    ElMessage.success('更新成功');
                } else {
                    // Inject description from AI text if not set
                    if (!payload.description && payload.ai_raw_text) {
                        payload.description = payload.ai_raw_text;
                    }
                    await api.post('opportunities/', payload);
                    ElMessage.success('创建成功');
                }
                router.push('/crm/opportunities');
            } catch (e: any) {
                console.error(e);
                ElMessage.error('保存失败: ' + (e.response?.data?.detail || '未知错误'));
            } finally {
                loading.value = false;
            }
        }
    });
};

onMounted(() => {
    fetchUsers();
    fetchData();
});
</script>
