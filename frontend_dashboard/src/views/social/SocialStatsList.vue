<template>
  <div class="h-screen flex flex-col bg-slate-50 overflow-hidden">
    <header class="bg-white shadow-sm px-6 py-4 flex justify-between items-center shrink-0 z-10">
      <div class="flex items-center gap-4">
        <h1 class="text-xl font-bold text-slate-800">社媒粉丝维护</h1>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">大屏首页</el-breadcrumb-item>
          <el-breadcrumb-item :to="{ path: '/crm' }">CRM首页</el-breadcrumb-item>
          <el-breadcrumb-item>社媒粉丝</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="flex items-center gap-4">
        <el-button type="primary" @click="handleCreate">新建记录</el-button>
      </div>
    </header>

    <main class="flex-1 p-6 overflow-auto">
      <div class="bg-white rounded-lg shadow p-4 min-h-full">
        <div class="mb-4 flex gap-4">
          <el-input v-model="search" placeholder="搜索平台名称" style="width: 300px" clearable @clear="fetchData" @keyup.enter="fetchData" />
          <el-button type="primary" @click="fetchData">搜索</el-button>
        </div>

        <el-table :data="items" style="width: 100%" v-loading="loading" stripe>
          <el-table-column prop="platform" label="平台" min-width="180" />
          <el-table-column prop="fans_count" label="粉丝数" width="120" />
          <el-table-column prop="status" label="状态" width="120" />
          <el-table-column prop="record_date" label="记录日期" width="140" />
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="scope">{{ new Date(scope.row.created_at).toLocaleString() }}</template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="scope">
              <el-button link type="primary" size="small" @click="handleEdit(scope.row)">编辑</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="mt-4 flex justify-end">
          <el-pagination layout="prev, pager, next" :total="total" :page-size="pageSize" @current-change="handlePageChange" />
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../../api';
import { ElMessage } from 'element-plus';

const router = useRouter();
const items = ref([]);
const loading = ref(false);
const search = ref('');
const total = ref(0);
const pageSize = ref(20);
const currentPage = ref(1);

const fetchData = async () => {
  loading.value = true;
  try {
    const params = { page: currentPage.value, search: search.value };
    const res = await api.get('social-stats/', { params });
    if (res.data.results) {
      items.value = res.data.results;
      total.value = res.data.count;
    } else {
      items.value = res.data;
      total.value = res.data.length;
    }
  } catch (e) {
    console.error(e);
    ElMessage.error('获取列表失败');
  } finally {
    loading.value = false;
  }
};

const handlePageChange = (page: number) => {
  currentPage.value = page;
  fetchData();
};

const handleCreate = () => {
  router.push('/social/stats/create');
};

const handleEdit = (row: any) => {
  router.push(`/social/stats/${row.id}/edit`);
};

onMounted(fetchData);
</script>

