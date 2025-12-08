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
              <el-col :span="12">
                <el-form-item label="商机名称" prop="name">
                    <el-input v-model="form.name" placeholder="请输入商机名称" />
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="客户公司" prop="customer_company">
                    <el-input v-model="form.customer_company" placeholder="请输入客户公司名称" />
                </el-form-item>
              </el-col>
              <el-col :span="4">
                <el-form-item label="客户代号" prop="customer_code">
                    <el-input v-model="form.customer_code" placeholder="代号" />
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

const rules = {
    name: [{ required: true, message: '请输入商机名称', trigger: 'blur' }],
    customer_company: [{ required: true, message: '请输入客户公司', trigger: 'blur' }],
    amount: [{ required: true, message: '请输入金额', trigger: 'blur' }],
};

const fetchData = async () => {
    if (!isEdit.value) return;
    try {
        const res = await api.get(`opportunities/${id}/`);
        form.value = { ...res.data };
    } catch (e) {
        ElMessage.error('获取详情失败');
    }
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
                if (!payload.customer_name) payload.customer_name = payload.customer_company;

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
    fetchData();
});
</script>
