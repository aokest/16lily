<template>
  <div class="space-y-6">
    <!-- Filter Card -->
    <el-card shadow="never" class="border-none shadow-sm rounded-xl">
      <el-form :inline="true" :model="filters" class="flex flex-wrap gap-4">
        <el-form-item label="行为类型">
          <el-select v-model="filters.type" placeholder="全部类型" clearable class="!w-40">
            <el-option label="商机" value="OPPORTUNITY" />
            <el-option label="客户" value="CUSTOMER" />
            <el-option label="联系人" value="CONTACT" />
            <el-option label="项目" value="PROJECT" />
            <el-option label="日报" value="DAILY_REPORT" />
            <el-option label="用户行为" value="USER" />
            <el-option label="系统" value="SYSTEM" />
          </el-select>
        </el-form-item>
        <el-form-item label="部门">
          <el-select v-model="filters.department" placeholder="全部部门" clearable class="!w-40">
            <el-option v-for="dept in departments" :key="dept.id" :label="dept.name" :value="dept.name" />
          </el-select>
        </el-form-item>
        <el-form-item label="操作人">
          <el-input v-model="filters.actor_name" placeholder="搜索姓名" clearable class="!w-40" />
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="filters.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            class="!w-80"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetFilters">重置</el-button>
          <el-button type="success" @click="handleExport">导出日志</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- List Card -->
    <el-card shadow="never" class="border-none shadow-sm rounded-xl overflow-hidden">
      <el-table :data="logs" v-loading="loading" style="width: 100%" class="modern-table">
        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="type_display" label="类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.type)" size="small">{{ row.type_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="action" label="动作" width="100" />
        <el-table-column prop="operator_name" label="操作人" width="120" />
        <el-table-column prop="operator_dept" label="部门" width="150" />
        <el-table-column prop="content" label="详情" min-width="300" />
      </el-table>

      <div class="mt-6 flex justify-end">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
/**
 * 系统日志管理组件
 * 用于管理员查看、筛选和导出系统行为日志
 */
import { ref, onMounted } from 'vue';
import api from '../../api';
import { ElMessage } from 'element-plus';

const loading = ref(false);
const logs = ref([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(20);
const departments = ref([]);

const filters = ref({
  type: '',
  department: '',
  actor_name: '',
  dateRange: []
});

/** 格式化日期时间显示 */
const formatDateTime = (str: string) => {
  if (!str) return '-';
  const date = new Date(str);
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
};

/** 根据日志类型获取标签样式 */
const getTypeTag = (type: string) => {
  const map: Record<string, string> = {
    'OPPORTUNITY': 'primary',
    'CUSTOMER': 'success',
    'CONTACT': 'info',
    'PROJECT': 'warning',
    'DAILY_REPORT': '',
    'USER': 'danger',
    'SYSTEM': 'info'
  };
  return map[type] || '';
};

/** 获取日志列表数据 */
const fetchLogs = async () => {
  loading.value = true;
  try {
    const params: any = {
      page: currentPage.value,
      page_size: pageSize.value,
      type: filters.value.type,
      department: filters.value.department,
      actor_name: filters.value.actor_name,
    };

    if (filters.value.dateRange && filters.value.dateRange.length === 2) {
      params.start_date = filters.value.dateRange[0];
      params.end_date = filters.value.dateRange[1];
    }

    const res = await api.get('activity-logs/', { params });
    logs.value = res.data.results;
    total.value = res.data.count;
  } catch (error) {
    ElMessage.error('获取日志失败');
  } finally {
    loading.value = false;
  }
};

/** 获取部门列表用于筛选 */
const fetchDepartments = async () => {
  try {
    const res = await api.get('departments/');
    departments.value = res.data;
  } catch (error) {
    console.error('Fetch depts failed', error);
  }
};

/** 执行搜索 */
const handleSearch = () => {
  currentPage.value = 1;
  fetchLogs();
};

/** 重置搜索条件 */
const resetFilters = () => {
  filters.value = {
    type: '',
    department: '',
    actor_name: '',
    dateRange: []
  };
  handleSearch();
};

/** 处理分页大小变化 */
const handleSizeChange = (val: number) => {
  pageSize.value = val;
  fetchLogs();
};

/** 处理当前页变化 */
const handleCurrentChange = (val: number) => {
  currentPage.value = val;
  fetchLogs();
};

/** 导出日志为CSV文件 (调用后端接口导出全量筛选结果) */
const handleExport = async () => {
  try {
    const params: any = {
      type: filters.value.type,
      department: filters.value.department,
      actor_name: filters.value.actor_name,
    };

    if (filters.value.dateRange && filters.value.dateRange.length === 2) {
      params.start_date = filters.value.dateRange[0];
      params.end_date = filters.value.dateRange[1];
    }

    // 转换为查询字符串
    const queryStr = new URLSearchParams(params).toString();
    const exportUrl = `${import.meta.env.VITE_API_URL || '/api/'}activity-logs/export_csv/?${queryStr}`;
    
    // 使用 window.open 或创建一个隐藏链接来触发下载
    window.open(exportUrl, '_blank');
    ElMessage.success('正在准备导出文件...');
  } catch (error) {
    console.error('Export failed', error);
    ElMessage.error('导出失败');
  }
};

onMounted(() => {
  fetchLogs();
  fetchDepartments();
});
</script>

<style scoped>
.modern-table {
  --el-table-header-bg-color: #f8fafc;
  --el-table-row-hover-bg-color: #f1f5f9;
}
</style>
