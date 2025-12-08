<template>
  <div class="h-screen flex flex-col bg-slate-50 overflow-hidden">
    <!-- Navbar -->
    <header class="bg-white shadow-sm px-6 py-4 flex justify-between items-center shrink-0 z-10">
      <div class="flex items-center gap-4">
        <h1 class="text-xl font-bold text-slate-800">商机管理</h1>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">大屏首页</el-breadcrumb-item>
          <el-breadcrumb-item>商机列表</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="flex items-center gap-4">
        <el-button type="primary" @click="handleCreate">新建商机</el-button>
        <el-button @click="logout">退出</el-button>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1 p-6 overflow-auto">
      <div class="bg-white rounded-lg shadow p-4 min-h-full">
        <!-- Filters -->
        <div class="mb-4 flex gap-4">
            <el-input v-model="search" placeholder="搜索商机名称/客户" style="width: 300px" clearable @clear="fetchData" @keyup.enter="fetchData" />
            <el-button type="primary" @click="fetchData">搜索</el-button>
        </div>

        <!-- Table -->
        <el-table :data="opportunities" style="width: 100%" v-loading="loading" stripe>
          <el-table-column prop="name" label="商机名称" min-width="180" show-overflow-tooltip />
          <el-table-column prop="customer_company" label="客户名称" min-width="150" />
          <el-table-column prop="amount" label="预计金额" width="120">
            <template #default="scope">
              ¥ {{ scope.row.amount?.toLocaleString() }}
            </template>
          </el-table-column>
          <el-table-column prop="stage" label="阶段" width="120">
             <template #default="scope">
                <el-tag>{{ scope.row.stage }}</el-tag>
             </template>
          </el-table-column>
          <el-table-column prop="sales_manager_name" label="负责人" width="100" />
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="scope">
                {{ new Date(scope.row.created_at).toLocaleString() }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="scope">
              <el-button link type="primary" size="small" @click="handleEdit(scope.row)">编辑</el-button>
              <el-button link type="danger" size="small" @click="handleDelete(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- Pagination (Simple) -->
        <div class="mt-4 flex justify-end">
            <el-pagination 
                layout="prev, pager, next" 
                :total="total" 
                :page-size="pageSize" 
                @current-change="handlePageChange"
            />
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../../api';
import { ElMessage, ElMessageBox } from 'element-plus';

const router = useRouter();
const opportunities = ref([]);
const loading = ref(false);
const search = ref('');
const total = ref(0);
const pageSize = ref(20);
const currentPage = ref(1);

const fetchData = async () => {
  loading.value = true;
  try {
    const params = {
        page: currentPage.value,
        search: search.value
    };
    const res = await api.get('opportunities/', { params });
    // DRF default pagination returns { count: 100, next: '...', previous: '...', results: [] }
    if (res.data.results) {
        opportunities.value = res.data.results;
        total.value = res.data.count;
    } else {
        // If no pagination
        opportunities.value = res.data;
        total.value = res.data.length;
    }
  } catch (e) {
    console.error(e);
    ElMessage.error('获取商机列表失败');
  } finally {
    loading.value = false;
  }
};

const handlePageChange = (page: number) => {
    currentPage.value = page;
    fetchData();
};

const handleCreate = () => {
    router.push('/crm/opportunities/create');
};

const handleEdit = (row: any) => {
    router.push(`/crm/opportunities/${row.id}/edit`);
};

const handleDelete = (row: any) => {
    ElMessageBox.confirm('确定要删除该商机吗？', '提示', {
        type: 'warning'
    }).then(async () => {
        try {
            await api.delete(`opportunities/${row.id}/`);
            ElMessage.success('删除成功');
            fetchData();
        } catch (e) {
            ElMessage.error('删除失败');
        }
    });
};

const logout = () => {
    localStorage.removeItem('auth_token');
    router.push('/login');
};

onMounted(() => {
    fetchData();
});
</script>
