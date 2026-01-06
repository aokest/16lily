<template>
  <div class="h-screen flex flex-col bg-slate-50 overflow-hidden">
    <main class="flex-1 p-6 overflow-auto">
      <div class="bg-white rounded-lg shadow p-4 min-h-full">
        <div class="mb-4 flex justify-between items-center">
          <div class="flex gap-4">
            <el-input v-model="search" placeholder="搜索平台或用户名" style="width: 300px" clearable @clear="fetchData" @keyup.enter="fetchData" />
            <el-button type="primary" @click="fetchData">搜索</el-button>
          </div>
          <router-link to="/social/accounts/create">
            <el-button type="primary">新建账号</el-button>
          </router-link>
        </div>

        <el-table :data="items" style="width: 100%" v-loading="loading" stripe>
          <el-table-column prop="platform" label="平台" min-width="160" />
          <el-table-column prop="display_name" label="显示名称" min-width="160" />
          <el-table-column prop="account_username" label="后台用户名" min-width="160" />
          <el-table-column prop="account_id" label="账号ID" min-width="160" />
          <el-table-column prop="register_phone" label="注册手机号" width="140" />
          <el-table-column prop="register_email" label="注册邮箱" width="180" />
          <el-table-column prop="status" label="状态" width="120" />
          <el-table-column label="最新粉丝数" width="140">
            <template #default="scope">
              {{ getLatestFans(scope.row) }}
            </template>
          </el-table-column>
          <el-table-column label="维护粉丝" min-width="240">
            <template #default="scope">
              <div class="flex items-center gap-2">
                <el-input-number v-model="newFans[scope.row.id]" :min="0" :step="100" />
                <el-button type="primary" size="small" :loading="savingId===scope.row.id" @click="addFans(scope.row)">新增</el-button>
                <el-button size="small" @click="pullFromApi(scope.row)" :disabled="pullingId===scope.row.id">从API拉取</el-button>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="管理员" min-width="220">
            <template #default="scope">
              <div class="flex flex-wrap gap-2">
                <el-tag v-for="a in scope.row.admins_detail" :key="a.user" type="info">{{ a.admin_name || a.username }}</el-tag>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="scope">{{ new Date(scope.row.created_at).toLocaleString() }}</template>
          </el-table-column>
          <el-table-column label="历史" width="120">
            <template #default="scope">
              <el-popover placement="left" width="320" trigger="click">
                <template #reference>
                  <el-button link size="small">查看</el-button>
                </template>
                <div v-if="(scope.row.change_logs||[]).length">
                  <div class="text-xs text-slate-600 mb-2">最近变更</div>
                  <ul class="text-xs space-y-1">
                    <li v-for="l in scope.row.change_logs" :key="l.changed_at">
                      <span class="font-mono">{{ l.field }}</span>: <span class="text-slate-500">{{ l.old }}</span> → <span class="text-slate-300">{{ l.new }}</span>
                      <span class="ml-1 text-slate-500">{{ new Date(l.changed_at).toLocaleString() }}</span>
                    </li>
                  </ul>
                </div>
                <div class="mt-2" v-if="(scope.row.admin_history||[]).length">
                  <div class="text-xs text-slate-600 mb-2">管理员变更</div>
                  <ul class="text-xs space-y-1">
                    <li v-for="h in scope.row.admin_history" :key="h.changed_at">
                      {{ h.from || '-' }} → {{ h.to || '-' }}
                      <span class="ml-1 text-slate-500">{{ new Date(h.changed_at).toLocaleString() }}</span>
                      <span v-if="h.note" class="ml-1 text-slate-400">{{ h.note }}</span>
                    </li>
                  </ul>
                </div>
                <div v-else class="text-xs text-slate-500">暂无记录</div>
              </el-popover>
            </template>
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

// 获取最新粉丝数
function getLatestFans(row: any) {
  const list = row.stats_recent || [];
  if (!list.length) return 0;
  return list[0].fans_count || 0;
}

const router = useRouter();
const items = ref([]);
const loading = ref(false);
const search = ref('');
const total = ref(0);
const pageSize = ref(20);
const currentPage = ref(1);
const newFans = ref<Record<number, number>>({});
const savingId = ref<number | null>(null);
const pullingId = ref<number | null>(null);

// 拉取列表数据
const fetchData = async () => {
  loading.value = true;
  try {
    const params = { page: currentPage.value, search: search.value };
    const res = await api.get('social-accounts/', { params });
    if (res.data.results) {
      items.value = res.data.results;
      total.value = res.data.count;
    } else {
      items.value = res.data;
      total.value = res.data.length;
    }
  } catch (e) {
    console.error(e);
    ElMessage.error('获取账号列表失败');
  } finally {
    loading.value = false;
  }
};

// 分页切换
const handlePageChange = (page: number) => {
  currentPage.value = page;
  fetchData();
};

// 跳转编辑
const handleEdit = (row: any) => {
  router.push(`/social/accounts/${row.id}/edit`);
};

// 新增粉丝记录
async function addFans(row: any) {
  try {
    const count = Number(newFans.value[row.id] || 0);
    if (Number.isNaN(count) || count < 0) {
      ElMessage.error('请输入合法的粉丝数');
      return;
    }
    savingId.value = row.id;
    await api.post('social-stats/', {
      account: row.id,
      fans_count: count,
      platform: row.platform
    });
    ElMessage.success('粉丝记录已新增');
    newFans.value[row.id] = 0;
    await fetchData();
  } catch (e) {
    console.error(e);
    ElMessage.error('新增失败');
  } finally {
    savingId.value = null;
  }
}

// 从社媒API拉取（占位，后续接入具体平台）
async function pullFromApi(row: any) {
  try {
    pullingId.value = row.id;
    // TODO: 接入平台API，当前仅提示
    ElMessage.info('暂未接入平台API，后续将支持自动拉取运营数据');
  } finally {
    pullingId.value = null;
  }
}

onMounted(fetchData);
</script>
