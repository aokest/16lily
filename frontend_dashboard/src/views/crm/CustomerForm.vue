<template>
  <div class="h-screen flex flex-col bg-slate-50 overflow-hidden">
    <!-- Navbar -->
    <header class="bg-white shadow-sm px-6 py-4 flex justify-between items-center shrink-0 z-10">
      <div class="flex items-center gap-4">
        <h1 class="text-xl font-bold text-slate-800">{{ isEdit ? '编辑客户' : '新建客户' }}</h1>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">大屏首页</el-breadcrumb-item>
          <el-breadcrumb-item :to="{ path: '/crm/customers' }">客户列表</el-breadcrumb-item>
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
                <el-form-item label="客户名称" prop="name">
                    <el-input v-model="form.name" placeholder="请输入客户名称" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="客户代号" prop="customer_code">
                    <el-input v-model="form.customer_code" placeholder="例如：CUST-001" />
                </el-form-item>
              </el-col>
          </el-row>

          <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="行业" prop="industry">
                    <el-input v-model="form.industry" placeholder="例如：互联网" />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="规模" prop="scale">
                    <el-select v-model="form.scale" placeholder="请选择规模" style="width: 100%">
                        <el-option label="小型 (0-50人)" value="SMALL" />
                        <el-option label="中型 (50-500人)" value="MEDIUM" />
                        <el-option label="大型 (500+人)" value="LARGE" />
                    </el-select>
                </el-form-item>
              </el-col>
          </el-row>

          <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="客户状态" prop="status">
                    <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%">
                        <el-option label="潜在客户" value="POTENTIAL" />
                        <el-option label="合作中" value="ACTIVE" />
                        <el-option label="流失" value="LOST" />
                    </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="12">
                  <el-form-item label="区域" prop="region">
                      <el-input v-model="form.region" placeholder="例如：北京" />
                  </el-form-item>
              </el-col>
          </el-row>

          <!-- Extended Info -->
          <h3 class="text-lg font-bold text-slate-800 mb-6 pb-2 border-b mt-6">详细信息</h3>
          
          <el-row :gutter="20">
              <el-col :span="12">
                  <el-form-item label="法人代表" prop="legal_representative">
                      <el-input v-model="form.legal_representative" />
                  </el-form-item>
              </el-col>
              <el-col :span="12">
                  <el-form-item label="网址" prop="website">
                      <el-input v-model="form.website" placeholder="https://" />
                  </el-form-item>
              </el-col>
          </el-row>

          <el-form-item label="地址" prop="address">
              <el-input v-model="form.address" placeholder="详细地址" />
          </el-form-item>

          <el-form-item label="备注/描述" prop="description">
              <el-input v-model="form.description" type="textarea" :rows="4" />
          </el-form-item>

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
    customer_code: '',
    industry: '',
    scale: 'SMALL',
    status: 'POTENTIAL',
    region: '',
    address: '',
    website: '',
    legal_representative: '',
    description: ''
});

const rules = {
    name: [{ required: true, message: '请输入客户名称', trigger: 'blur' }],
};

const fetchData = async () => {
    if (!isEdit.value) return;
    try {
        const res = await api.get(`customers/${id}/`);
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
                if (isEdit.value) {
                    await api.patch(`customers/${id}/`, form.value);
                    ElMessage.success('更新成功');
                } else {
                    await api.post('customers/', form.value);
                    ElMessage.success('创建成功');
                }
                router.push('/crm/customers');
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
