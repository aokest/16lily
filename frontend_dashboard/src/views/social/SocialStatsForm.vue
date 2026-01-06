<template>
  <div class="h-screen flex flex-col bg-slate-50 overflow-hidden">
    <header class="bg-white shadow-sm px-6 py-4 flex justify-between items-center shrink-0 z-10">
      <div class="flex items-center gap-4">
        <h1 class="text-xl font-bold text-slate-800">{{ isEdit ? '编辑粉丝记录' : '新建粉丝记录' }}</h1>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">大屏首页</el-breadcrumb-item>
          <el-breadcrumb-item :to="{ path: '/crm' }">CRM首页</el-breadcrumb-item>
          <el-breadcrumb-item>社媒粉丝</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="flex items-center gap-4">
        <el-button @click="router.back()">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">保存</el-button>
      </div>
    </header>

    <main class="flex-1 p-6 overflow-auto">
      <div class="bg-white rounded-lg shadow p-8 max-w-3xl mx-auto">
        <el-form :model="form" label-width="120px" ref="formRef" :rules="rules">
          <el-form-item label="关联账号" prop="account">
            <el-select v-model="form.account" placeholder="选择社媒账号" filterable style="width: 100%" @change="syncPlatform">
              <el-option v-for="acc in accountOptions" :key="acc.id" :label="acc.platform + ' / ' + acc.account_username" :value="acc.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="粉丝数" prop="fans_count">
            <el-input-number v-model="form.fans_count" :min="0" :step="100" />
          </el-form-item>
          <el-form-item label="平台">
            <el-input v-model="form.platform" disabled />
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
const id = route.params.id as any;
const isEdit = computed(() => !!id);

const form = ref({ account: null as any, fans_count: 0, platform: '' });
const rules = { account: [{ required: true, message: '请选择社媒账号', trigger: 'change' }] };
const accountOptions = ref<any[]>([]);

const fetchData = async () => {
  if (!isEdit.value) return;
  try { const res = await api.get(`social-stats/${id}/`); form.value = { ...res.data }; }
  catch { ElMessage.error('获取详情失败'); }
};

const fetchAccounts = async () => {
  try { const res = await api.get('social-accounts/'); accountOptions.value = res.data.results || res.data || []; }
  catch { accountOptions.value = []; }
};

const syncPlatform = () => {
  const acc = accountOptions.value.find((x:any) => x.id === form.value.account);
  if (acc) form.value.platform = acc.platform;
};

const handleSubmit = async () => {
  if (!formRef.value) return;
  await formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      loading.value = true;
      try {
        if (isEdit.value) { await api.patch(`social-stats/${id}/`, form.value); ElMessage.success('更新成功'); }
        else { await api.post('social-stats/', form.value); ElMessage.success('创建成功'); }
        router.push('/social/stats');
      } catch (e: any) {
        console.error(e); ElMessage.error('保存失败');
      } finally { loading.value = false; }
    }
  });
};

onMounted(async () => { await fetchAccounts(); await fetchData(); });
</script>
