<template>
  <div class="h-screen flex flex-col bg-slate-50 overflow-hidden">
    <main class="flex-1 p-6 overflow-auto">
      <div class="bg-white rounded-lg shadow p-4">
        <div class="mb-3 flex justify-between items-center">
          <div class="flex gap-3">
            <el-input v-model="search" placeholder="搜索姓名/电话/邮箱" clearable @keyup.enter="fetchData" style="width: 280px" />
            <el-button type="primary" @click="fetchData">搜索</el-button>
          </div>
          <router-link to="/crm/contacts/create"><el-button type="primary">新建联系人</el-button></router-link>
        </div>
        <el-table :data="items" v-loading="loading" style="width:100%" stripe>
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="name" label="姓名" width="140" />
          <el-table-column prop="title" label="职位" width="160" />
          <el-table-column prop="phone" label="电话" width="160" />
          <el-table-column prop="email" label="邮箱" width="200" />
          <el-table-column prop="customer" label="客户ID" width="100" />
          <el-table-column prop="customer_name" label="客户名称" width="200" />
          <el-table-column prop="department" label="部门" width="160" />
          <el-table-column prop="is_decision_maker" label="决策人" width="100">
            <template #default="scope">{{ scope.row.is_decision_maker ? '是' : '否' }}</template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="scope">
              <el-button link type="primary" size="small" @click="handleEdit(scope.row)">编辑</el-button>
              <el-popconfirm title="确定删除该联系人?" @confirm="handleDelete(scope.row)">
                <template #reference>
                  <el-button link type="danger" size="small">删除</el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </main>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../../api';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
const router = useRouter();
const items = ref<any[]>([]);
const loading = ref(false);
const search = ref('');
async function fetchData(){
  loading.value = true;
  try{
    const params:any = {};
    if (search.value) params.search = search.value;
    const res = await api.get('contacts/', { params });
    items.value = res.data.results || res.data || [];
  }catch(e){ console.error(e); ElMessage.error('获取联系人失败'); }
  finally{ loading.value = false; }
}
function handleEdit(row:any){ router.push(`/crm/contacts/${row.id}/edit`); }

async function handleDelete(row:any){
  try{
    await api.delete(`contacts/${row.id}/`);
    ElMessage.success('删除成功');
    fetchData();
  }catch(e){
    console.error(e);
    ElMessage.error('删除失败');
  }
}

onMounted(fetchData);
</script>
