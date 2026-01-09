<template>
  <div class="h-screen flex flex-col bg-slate-50 overflow-hidden">
    <header class="bg-white shadow-sm px-6 py-4 flex justify-between items-center shrink-0 z-10">
      <div class="flex items-center gap-4">
        <h1 class="text-xl font-bold text-slate-800">{{ isEdit ? '编辑联系人' : '新建联系人' }}</h1>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">大屏首页</el-breadcrumb-item>
          <el-breadcrumb-item :to="{ path: '/crm' }">CRM首页</el-breadcrumb-item>
          <el-breadcrumb-item>联系人</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="flex items-center gap-3">
        <el-button @click="router.back()">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">保存</el-button>
      </div>
    </header>
    <main class="flex-1 p-6 overflow-auto">
      <div class="bg-white rounded-lg shadow p-8 max-w-3xl mx-auto">
        <el-form :model="form" label-width="120px" ref="formRef" :rules="rules">
          <el-form-item label="客户" prop="customer">
            <el-select v-model="form.customer" filterable remote reserve-keyword :remote-method="searchCustomers" :loading="custLoading" placeholder="请输入客户名称或代码搜索" style="width: 100%">
              <el-option v-for="c in customerOptions" :key="c.value" :label="c.label" :value="c.value" />
            </el-select>
          </el-form-item>
          <el-form-item label="客户名称">
            <el-input :model-value="currentCustomerName" disabled />
          </el-form-item>
          <el-form-item label="姓名" prop="name"><el-input v-model="form.name" /></el-form-item>
          <el-form-item label="职位"><el-input v-model="form.title" /></el-form-item>
          <el-form-item label="电话"><el-input v-model="form.phone" /></el-form-item>
          <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
          <el-form-item label="微信"><el-input v-model="form.wechat" /></el-form-item>
          <el-form-item label="部门"><el-input v-model="form.department" /></el-form-item>
          <el-form-item label="是否决策人"><el-switch v-model="form.is_decision_maker" /></el-form-item>
          <el-form-item label="备注"><el-input v-model="form.notes" type="textarea" :rows="4" /></el-form-item>
        </el-form>
      </div>
    </main>
  </div>
</template>
<script setup lang="ts">
import { ref, computed } from 'vue';
import api from '../../api';
import { useRoute, useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
const route = useRoute(); const router = useRouter();
const id = route.params.id as any; const isEdit = computed(() => !!id);
const loading = ref(false); const formRef = ref();
const form = ref<any>({ customer: null, name: '', title: '', phone: '', email: '', wechat: '', department: '', is_decision_maker: false, notes: '' });
const rules = { customer: [{ required: true, message: '请选择客户', trigger: 'change' }], name: [{ required: true, message: '请输入姓名', trigger: 'blur' }] };
const customerOptions = ref<any[]>([]); const custLoading = ref(false);
const currentCustomerName = computed(() => {
  const found = customerOptions.value.find((c:any) => c.value === form.value.customer);
  return found ? found.label : '';
});
async function searchCustomers(query:string){ custLoading.value = true; try{ const res = await api.get('customers/', { params: { search: query } }); const list = res.data.results || res.data; customerOptions.value = list.map((c:any) => ({ label: c.name, value: c.id })); } catch{} finally{ custLoading.value = false; } }
async function fetchData(){ if (!isEdit.value) return; try{ const res = await api.get(`contacts/${id}/`); form.value = { ...res.data }; } catch{ ElMessage.error('获取详情失败'); } }
async function handleSubmit(){ if (!formRef.value) return; await formRef.value.validate(async (valid:boolean) => { if(valid){ loading.value = true; try{ if(isEdit.value){ await api.patch(`contacts/${id}/`, form.value); ElMessage.success('更新成功'); } else { await api.post('contacts/', form.value); ElMessage.success('创建成功'); } router.push('/crm/contacts'); } catch(e:any){ console.error(e); ElMessage.error('保存失败'); } finally{ loading.value = false; } } }); }
fetchData();
</script>
