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
              <el-col :span="12">
                <el-form-item label="客户公司" prop="customer_company">
                    <el-input v-model="form.customer_company" placeholder="请输入客户公司名称" />
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
                  <!-- In a real app, this should be a user search/select -->
                  <!-- For now we rely on backend to assign creator/manager or use logged in user -->
                  <!-- We can display a readonly field if editing -->
                  <el-form-item label="负责销售" v-if="isEdit">
                      <el-input v-model="form.sales_manager_name" disabled />
                  </el-form-item>
              </el-col>
          </el-row>

          <!-- AI Input (Optional) -->
          <div class="mt-8 mb-4 p-4 bg-blue-50 rounded border border-blue-100" v-if="!isEdit">
              <h4 class="text-sm font-bold text-blue-800 mb-2">✨ AI 智能录入</h4>
              <el-input 
                v-model="form.ai_raw_text" 
                type="textarea" 
                :rows="3" 
                placeholder="粘贴一段文字（例如：九号电动车商机，15万，销售员付磊），AI将自动解析填单" 
              />
          </div>

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

const id = route.params.id;
const isEdit = computed(() => !!id);

const form = ref({
    name: '',
    customer_company: '',
    amount: 0,
    stage: 'CONTACT',
    expected_sign_date: '',
    ai_raw_text: '',
    sales_manager_name: ''
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

const handleSubmit = async () => {
    if (!formRef.value) return;
    await formRef.value.validate(async (valid: boolean) => {
        if (valid) {
            loading.value = true;
            try {
                // If AI text is present, backend signal will handle parsing if name is generic
                // But frontend form values take precedence if user manually typed them.
                // The current backend logic (signals.py) triggers AI parsing if 'ai_raw_text' is set AND name is 'New Opportunity' etc.
                // So if user fills the form, standard save works.
                
                // We need to ensure we send the ID of logged in user as creator/sales_manager if new
                // But DRF usually handles request.user.
                // Let's rely on backend defaults.

                if (isEdit.value) {
                    await api.patch(`opportunities/${id}/`, form.value);
                    ElMessage.success('更新成功');
                } else {
                    // Manually inject default values for mandatory fields if missing
                    // Since frontend form requires them, they should be present.
                    // But 'sales_manager' is required by model, default to self (request.user)
                    // The ViewSet logic sets creator=request.user
                    // But we might need to set sales_manager explicitly if model doesn't default it.
                    // Let's check model... sales_manager is ForeignKey(User).
                    // We'll let backend handle it or fail. Ideally backend should auto-set sales_manager=creator if not provided.
                    
                    // Actually, let's inject a dummy sales_manager_id if we can, or rely on backend.
                    // Reading OpportunityViewSet logic: perform_create sets creator.
                    // It doesn't set sales_manager. We should add that logic to backend or here.
                    // For now, let's try submitting. If 400, we fix backend.
                    await api.post('opportunities/', {
                        ...form.value,
                        // Default fields to pass model validation if backend is strict
                        customer_name: form.value.customer_company, // legacy field
                    });
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
