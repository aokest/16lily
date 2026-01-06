<template>
  <div class="h-screen flex flex-col bg-slate-50 overflow-hidden">
    <header class="bg-white shadow-sm px-6 py-4 flex justify-between items-center shrink-0 z-10">
      <div class="flex items-center gap-4">
        <h1 class="text-xl font-bold text-slate-800">{{ isEdit ? '编辑社媒账号' : '新建社媒账号' }}</h1>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">大屏首页</el-breadcrumb-item>
          <el-breadcrumb-item :to="{ path: '/crm' }">CRM首页</el-breadcrumb-item>
          <el-breadcrumb-item>社媒管理</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="flex items-center gap-4">
        <el-button @click="router.back()">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">保存</el-button>
      </div>
    </header>

    <main class="flex-1 p-6 overflow-auto">
      <div class="bg-white rounded-lg shadow p-8 max-w-4xl mx-auto">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="基本信息" name="basic">
        <el-form :model="form" label-width="140px" ref="formRef" :rules="rules">
          <el-form-item label="平台" prop="platform">
            <el-input v-model="form.platform" placeholder="如：抖音/公众号/微博" />
          </el-form-item>
          <el-form-item label="显示名称">
            <el-input v-model="form.display_name" placeholder="对外显示名称" />
          </el-form-item>
          <el-form-item label="用户名" prop="account_username">
            <el-input v-model="form.account_username" />
          </el-form-item>
          <el-form-item label="账号ID">
            <el-input v-model="form.account_id" placeholder="平台唯一账号ID" />
          </el-form-item>
          <el-form-item label="密码提示">
            <el-input v-model="form.password_hint" placeholder="不保存明文，填写提示" />
          </el-form-item>
          <el-form-item label="注册手机号">
            <el-input v-model="form.register_phone" />
          </el-form-item>
          <el-form-item label="注册邮箱">
            <el-input v-model="form.register_email" />
          </el-form-item>
          <el-form-item label="凭据引用">
            <el-input v-model="form.credential_ref" placeholder="外部密码库引用ID" />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="form.status" placeholder="选择状态" style="width: 200px">
              <el-option label="待确认" value="PENDING" />
              <el-option label="已确认" value="APPROVED" />
            </el-select>
          </el-form-item>
          <el-form-item label="初始粉丝数">
            <el-input-number v-model="initialFans" :min="0" :step="100" />
          </el-form-item>
          <el-form-item label="管理员">
            <el-select v-model="adminIds" multiple filterable style="width: 100%" placeholder="选择管理员">
              <el-option v-for="u in userOptions" :key="u.id" :label="u.name + ' / ' + (u.phone || '-')" :value="u.id" />
            </el-select>
          </el-form-item>
        </el-form>
          </el-tab-pane>
          <el-tab-pane v-if="isEdit" label="粉丝数据" name="fans">
        <div v-if="isEdit" class="mt-8">
          <h2 class="text-lg font-bold mb-3">粉丝数据</h2>
          <div class="flex items-end gap-3 mb-4">
            <el-input-number v-model="newFans" :min="0" :step="100" label="新增粉丝数" />
            <el-button type="primary" @click="addFansStat" :loading="statLoading">添加记录</el-button>
          </div>
          <el-table :data="statsList" v-loading="statLoading" style="width:100%" size="small">
            <el-table-column prop="record_date" label="日期" width="140" />
            <el-table-column prop="fans_count" label="粉丝数" width="120" />
            <el-table-column prop="status" label="状态" width="120" />
          </el-table>
        </div>
          </el-tab-pane>
          <el-tab-pane v-if="isEdit" label="历史记录" name="history">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 class="text-base font-semibold mb-2">资产字段变更</h3>
                <el-table :data="changeLogs" size="small">
                  <el-table-column prop="field" label="字段" width="140" />
                  <el-table-column label="旧值">
                    <template #default="scope">{{ scope.row.old }}</template>
                  </el-table-column>
                  <el-table-column label="新值">
                    <template #default="scope">{{ scope.row.new }}</template>
                  </el-table-column>
                  <el-table-column prop="changed_at" label="时间" width="180">
                    <template #default="scope">{{ new Date(scope.row.changed_at).toLocaleString() }}</template>
                  </el-table-column>
                </el-table>
              </div>
              <div>
                <h3 class="text-base font-semibold mb-2">管理员变更历史</h3>
                <el-table :data="adminHistory" size="small">
                  <el-table-column label="从" width="120">
                    <template #default="scope">{{ scope.row.from || '-' }}</template>
                  </el-table-column>
                  <el-table-column label="到" width="120">
                    <template #default="scope">{{ scope.row.to || '-' }}</template>
                  </el-table-column>
                  <el-table-column prop="note" label="备注" />
                  <el-table-column prop="changed_at" label="时间" width="180">
                    <template #default="scope">{{ new Date(scope.row.changed_at).toLocaleString() }}</template>
                  </el-table-column>
                </el-table>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>
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
const activeTab = ref('basic');

const form = ref({ platform: '', account_username: '', password_hint: '', register_phone: '', credential_ref: '', status: 'PENDING' } as any);
const adminIds = ref<number[]>([]);
const userOptions = ref<any[]>([]);
const statsList = ref<any[]>([]);
const statLoading = ref(false);
const newFans = ref(0);
const newStatus = ref('APPROVED');
// @ts-ignore
const _useStatus = newStatus;
const initialFans = ref(0);
const changeLogs = ref<any[]>([]);
const adminHistory = ref<any[]>([]);

const rules = {
  platform: [{ required: true, message: '请输入平台', trigger: 'blur' }],
  account_username: [{ required: true, message: '请输入用户名', trigger: 'blur' }]
};

const fetchUsers = async () => {
  try {
    const res = await api.get('users/simple/');
    userOptions.value = res.data.results || [];
  } catch {
    userOptions.value = [];
  }
};

const fetchData = async () => {
  if (!isEdit.value) return;
  try {
    const res = await api.get(`social-accounts/${id}/`);
    form.value = { ...res.data };
    adminIds.value = (res.data.admins_detail || []).map((x: any) => x.user);
    statsList.value = res.data.stats_recent || [];
    changeLogs.value = res.data.change_logs || [];
    adminHistory.value = res.data.admin_history || [];
  } catch { ElMessage.error('获取详情失败'); }
};

const handleSubmit = async () => {
  if (!formRef.value) return;
  await formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      loading.value = true;
      try {
        const payload = { ...form.value, admin_ids: adminIds.value, initial_fans_count: initialFans.value };
        if (isEdit.value) { await api.patch(`social-accounts/${id}/`, payload); ElMessage.success('更新成功'); }
        else { await api.post('social-accounts/', payload); ElMessage.success('创建成功'); }
        router.push('/social/accounts');
      } catch (e: any) {
        console.error(e); ElMessage.error('保存失败');
      } finally { loading.value = false; }
    }
  });
};

onMounted(async () => { await fetchUsers(); await fetchData(); });

const addFansStat = async () => {
  if (!isEdit.value) return;
  statLoading.value = true;
  try {
    await api.post('social-stats/', { account: Number(id), fans_count: newFans.value, platform: form.value.platform });
    ElMessage.success('已添加粉丝记录');
    await fetchData();
  } catch (e:any) {
    console.error(e);
    ElMessage.error('添加失败');
  } finally { statLoading.value = false; }
};
</script>
