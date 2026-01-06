<template>
  <div class="h-screen flex flex-col bg-slate-50 overflow-hidden">
    <!-- Main Content -->
    <main class="flex-1 p-6 overflow-auto">
      <div class="bg-white rounded-lg shadow p-4 min-h-full">
        <!-- Filters & Actions -->
        <div class="mb-4 flex flex-wrap gap-4 items-center">
            <el-input v-model="search" placeholder="搜索客户名称/代号" style="width: 200px" clearable @clear="fetchData" @keyup.enter="fetchData" />
            <el-input v-model="industryFilter" placeholder="按行业筛选" style="width: 150px" @keyup.enter="fetchData" />
            <el-select v-model="statusFilter" placeholder="按状态筛选" clearable style="width: 140px" @change="fetchData">
              <el-option label="潜在客户" value="POTENTIAL" />
              <el-option label="合作中" value="ACTIVE" />
              <el-option label="重点客户" value="KEY" />
              <el-option label="流失客户" value="CHURNED" />
            </el-select>
            <el-input v-model="regionFilter" placeholder="按区域筛选" style="width: 140px" @keyup.enter="fetchData" />
            <el-select v-model="tagFilter" placeholder="按标签筛选" clearable filterable style="width: 160px" @change="fetchData">
              <el-option v-for="t in tagOptions" :key="t.id" :label="t.name" :value="t.id" />
            </el-select>
            <el-select v-model="selectedCohort" placeholder="选择分群" clearable filterable style="width: 160px" @change="applyCohort">
              <el-option v-for="c in cohortOptions" :key="c.id" :label="c.name" :value="c.id" />
            </el-select>
            <el-button @click="saveCohort">保存为分群</el-button>
            <el-button type="primary" @click="fetchData">搜索</el-button>
            <div class="flex-1"></div>
            <el-button type="primary" @click="handleCreate">新建客户</el-button>
        </div>

        <!-- Table -->
        <el-table :data="customers" style="width: 100%" v-loading="loading" stripe>
          <el-table-column prop="name" label="客户名称" min-width="180" show-overflow-tooltip />
          <el-table-column prop="customer_code" label="代号" width="120" />
          <el-table-column prop="industry" label="行业" width="120" />
          <el-table-column prop="scale" label="规模" width="120" />
          <el-table-column label="标签" min-width="200">
            <template #default="scope">
              <div class="flex flex-wrap gap-2">
                <el-tag
                  v-for="t in (scope.row.tags_detail || [])"
                  :key="t.id"
                  effect="plain"
                  :style="{ borderColor: t.color || '#dcdfe6', color: (t.color || '#606266'), backgroundColor: 'transparent' }"
                >
                  {{ t.name }}
                </el-tag>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
             <template #default="scope">
                <el-tag :type="scope.row.status === 'ACTIVE' ? 'success' : 'info'">
                    {{ scope.row.status === 'ACTIVE' ? '合作中' : scope.row.status }}
                </el-tag>
             </template>
          </el-table-column>
          <el-table-column prop="owner_name" label="负责人" width="100" />
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
        
        <!-- Pagination -->
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
const customers = ref([]);
const loading = ref(false);
const search = ref('');
const industryFilter = ref('');
const statusFilter = ref('');
const regionFilter = ref('');
const tagFilter = ref<number|null>(null);
const tagOptions = ref<any[]>([]);
const cohortOptions = ref<any[]>([]);
const selectedCohort = ref<number|null>(null);
const total = ref(0);
const pageSize = ref(20);
const currentPage = ref(1);

const fetchData = async () => {
  loading.value = true;
  try {
    const params:any = {
        page: currentPage.value,
        search: search.value
    };
    if (industryFilter.value) params.industry = industryFilter.value;
    if (statusFilter.value) params.status = statusFilter.value;
    if (regionFilter.value) params.region = regionFilter.value;
    if (tagFilter.value) params.tags = tagFilter.value;
    const res = await api.get('customers/', { params });
    if (res.data.results) {
        customers.value = res.data.results;
        total.value = res.data.count;
    } else {
        customers.value = res.data;
        total.value = res.data.length;
    }
  } catch (e) {
    console.error(e);
    ElMessage.error('获取客户列表失败');
  } finally {
    loading.value = false;
  }
};
const fetchTags = async () => {
  try {
    const res = await api.get('customer-tags/');
    tagOptions.value = res.data.results || res.data || [];
  } catch (e) { tagOptions.value = []; }
};
const fetchCohorts = async () => {
  try {
    const res = await api.get('customer-cohorts/');
    cohortOptions.value = res.data.results || res.data || [];
  } catch (e) { cohortOptions.value = []; }
};
const saveCohort = async () => {
  try {
    const name = prompt('输入分群名称');
    if (!name) return;
    const filters:any = {};
    if (search.value) filters.search = search.value;
    if (industryFilter.value) filters.industry = industryFilter.value;
    if (statusFilter.value) filters.status = statusFilter.value;
    if (regionFilter.value) filters.region = regionFilter.value;
    if (tagFilter.value) filters.tags = tagFilter.value;
    const res = await api.post('customer-cohorts/', { name, filters });
    cohortOptions.value = (cohortOptions.value || []).concat([res.data]);
  } catch (e){ console.error(e); }
};
const applyCohort = async (id:number|null) => {
  const found = cohortOptions.value.find((x:any) => x.id === id);
  if (!found) return;
  const f = found.filters || {};
  search.value = f.search || '';
  industryFilter.value = f.industry || '';
  statusFilter.value = f.status || '';
  regionFilter.value = f.region || '';
  tagFilter.value = f.tags || null;
  fetchData();
};

const handlePageChange = (page: number) => {
    currentPage.value = page;
    fetchData();
};

const handleCreate = () => {
    router.push('/crm/customers/create');
};

const handleEdit = (row: any) => {
    router.push(`/crm/customers/${row.id}/edit`);
};

const handleDelete = (row: any) => {
    ElMessageBox.confirm('确定要删除该客户吗？', '提示', {
        type: 'warning'
    }).then(async () => {
        try {
            await api.delete(`customers/${row.id}/`);
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
// @ts-ignore
const _useLogout = logout;

onMounted(() => {
    fetchTags();
    fetchCohorts();
    fetchData();
});
</script>
