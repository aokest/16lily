<template>
  <div class="h-screen flex flex-col bg-slate-50 overflow-hidden">
    <header class="bg-white shadow-sm px-6 py-4 flex justify-between items-center shrink-0 z-10">
      <div class="flex items-center gap-4">
        <h1 class="text-xl font-bold text-slate-800">业绩统计报表</h1>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">大屏首页</el-breadcrumb-item>
          <el-breadcrumb-item>业绩统计</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="flex items-center gap-4">
        <div class="flex gap-3 text-sm mr-4">
          <router-link to="/crm" class="text-slate-500 hover:text-blue-600">CRM首页</router-link>
          <router-link to="/crm/opportunities" class="text-slate-500 hover:text-blue-600">商机管理</router-link>
        </div>
        
        <!-- Scope Toggle -->
        <el-radio-group v-model="scope" @change="load">
            <el-radio-button label="department">部门业绩</el-radio-button>
            <el-radio-button label="personal">个人业绩</el-radio-button>
        </el-radio-group>

        <!-- Year Selection -->
        <el-select v-model="selectedYear" style="width: 100px" @change="load">
            <el-option :label="new Date().getFullYear()" :value="new Date().getFullYear()" />
            <el-option :label="new Date().getFullYear() - 1" :value="new Date().getFullYear() - 1" />
            <el-option :label="new Date().getFullYear() + 1" :value="new Date().getFullYear() + 1" />
        </el-select>

        <!-- Time Range Selection -->
        <el-select v-model="timeRange" style="width: 100px" @change="load">
            <el-option label="全年" value="year" />
            <el-option label="按季度" value="quarter" />
            <el-option label="按月份" value="month" />
        </el-select>

        <el-select v-if="timeRange === 'quarter'" v-model="selectedQuarter" style="width: 100px" @change="load">
            <el-option label="Q1" :value="1" />
            <el-option label="Q2" :value="2" />
            <el-option label="Q3" :value="3" />
            <el-option label="Q4" :value="4" />
        </el-select>

        <el-select v-if="timeRange === 'month'" v-model="selectedMonth" style="width: 100px" @change="load">
            <el-option v-for="m in 12" :key="m" :label="`${m}月`" :value="m" />
        </el-select>

        <!-- Department Select (Only visible if scope is department) -->
        <el-select v-if="scope === 'department'" v-model="department" placeholder="选择部门" style="width: 150px" @change="load">
          <el-option label="销售部" value="SALES" />
          <el-option label="春秋GAME" value="GAME" />
          <el-option label="集团市场部" value="GROUP_MARKETING" />
          <el-option label="标准实践实验室" value="LAB" />
          <el-option label="研发中心" value="RND" />
          <el-option label="其他" value="OTHER" />
        </el-select>
        
        <el-button type="primary" @click="load">刷新</el-button>
      </div>
    </header>

    <main class="flex-1 p-6 overflow-auto">
      <!-- 5 Indicators Grid -->
      <div class="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
        <!-- 1. Opportunity Pool -->
        <el-card shadow="hover" class="flex flex-col justify-center items-center text-center py-6 border-t-4 border-blue-500">
           <div class="text-slate-500 text-sm mb-2 font-medium">商机池 (预计金额)</div>
           <div class="text-2xl font-bold text-slate-800">¥ {{ format(stats.totals?.pipeline) }}</div>
        </el-card>
        <!-- 2. Signed -->
        <el-card shadow="hover" class="flex flex-col justify-center items-center text-center py-6 border-t-4 border-green-500">
           <div class="text-slate-500 text-sm mb-2 font-medium">新签合同金额</div>
           <div class="text-2xl font-bold text-slate-800">¥ {{ format(stats.totals?.signed) }}</div>
           <div v-if="stats.targets?.t_signed" class="text-xs text-slate-400 mt-1">
             目标: ¥{{ format(stats.targets.t_signed) }}
             <span :class="getPercentColor(stats.totals?.signed, stats.targets.t_signed)">
                ({{ getPercentage(stats.totals?.signed, stats.targets.t_signed) }}%)
             </span>
           </div>
        </el-card>
        <!-- 3. Collections -->
        <el-card shadow="hover" class="flex flex-col justify-center items-center text-center py-6 border-t-4 border-emerald-500">
           <div class="text-slate-500 text-sm mb-2 font-medium">已回款金额</div>
           <div class="text-2xl font-bold text-slate-800">¥ {{ format(stats.totals?.collection) }}</div>
        </el-card>
        <!-- 4. Gross Profit -->
        <el-card shadow="hover" class="flex flex-col justify-center items-center text-center py-6 border-t-4 border-orange-500">
           <div class="text-slate-500 text-sm mb-2 font-medium">回款毛利</div>
           <div class="text-2xl font-bold text-slate-800">¥ {{ format(stats.totals?.gross) }}</div>
           <div v-if="stats.targets?.t_gross" class="text-xs text-slate-400 mt-1">
             目标: ¥{{ format(stats.targets.t_gross) }}
             <span :class="getPercentColor(stats.totals?.gross, stats.targets.t_gross)">
                ({{ getPercentage(stats.totals?.gross, stats.targets.t_gross) }}%)
             </span>
           </div>
        </el-card>
        <!-- 5. Revenue -->
        <el-card shadow="hover" class="flex flex-col justify-center items-center text-center py-6 border-t-4 border-purple-500">
           <div class="text-slate-500 text-sm mb-2 font-medium">确认收入</div>
           <div class="text-2xl font-bold text-slate-800">¥ {{ format(stats.totals?.revenue) }}</div>
           <div v-if="stats.targets?.t_revenue" class="text-xs text-slate-400 mt-1">
             目标: ¥{{ format(stats.targets.t_revenue) }}
             <span :class="getPercentColor(stats.totals?.revenue, stats.targets.t_revenue)">
                ({{ getPercentage(stats.totals?.revenue, stats.targets.t_revenue) }}%)
             </span>
           </div>
        </el-card>
      </div>

      <!-- Charts Row -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <el-card class="shadow-sm">
            <template #header>
              <div class="font-bold">月度趋势 (新签 vs 回款)</div>
            </template>
            <div v-if="stats.monthly && stats.monthly.length" class="h-64 flex items-end justify-between px-4 gap-2">
                <div v-for="m in stats.monthly" :key="m.month" class="flex-1 flex flex-col items-center group relative">
                    <div class="w-full flex gap-1 items-end justify-center h-full">
                        <div class="w-3 bg-green-500 rounded-t transition-all hover:bg-green-400" :style="{height: Math.min((m.signed / maxVal) * 100, 100) + '%'}"></div>
                        <div class="w-3 bg-emerald-500 rounded-t transition-all hover:bg-emerald-400" :style="{height: Math.min((m.collection / maxVal) * 100, 100) + '%'}"></div>
                    </div>
                    <div class="text-xs text-slate-400 mt-2 transform -rotate-45 origin-top-left translate-y-2">{{ m.month.slice(5) }}</div>
                    <!-- Tooltip -->
                    <div class="absolute bottom-full mb-2 hidden group-hover:block bg-slate-800 text-white text-xs p-2 rounded z-10 whitespace-nowrap">
                        <div>{{ m.month }}</div>
                        <div>新签: ¥{{ format(m.signed) }}</div>
                        <div>回款: ¥{{ format(m.collection) }}</div>
                    </div>
                </div>
            </div>
            <div v-else class="h-64 flex items-center justify-center text-slate-400">暂无趋势数据</div>
          </el-card>

          <el-card class="shadow-sm">
            <template #header>
              <div class="font-bold">商机阶段分布</div>
            </template>
            <el-table :data="stats.status_distribution || []" style="width:100%" height="250">
              <el-table-column prop="status" label="状态" width="120">
                  <template #default="{ row }">
                      <el-tag size="small">{{ row.status }}</el-tag>
                  </template>
              </el-table-column>
              <el-table-column prop="count" label="数量" />
              <el-table-column label="占比">
                  <template #default="{ row }">
                      <el-progress :percentage="Math.round((row.count / (totalCount || 1)) * 100)" />
                  </template>
              </el-table-column>
            </el-table>
          </el-card>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { fetchPerformanceReport } from '../../api';

const department = ref('SALES');
const scope = ref('department'); // department | personal
const timeRange = ref('year'); // year | quarter | month
const selectedYear = ref(new Date().getFullYear());
const selectedQuarter = ref(Math.ceil((new Date().getMonth() + 1) / 3));
const selectedMonth = ref(new Date().getMonth() + 1);

const stats = ref<any>({ totals: {}, monthly: [], status_distribution: [] });

const format = (n: number) => {
  if (!n) return '0';
  return Number(n).toLocaleString();
};

const totalCount = computed(() => {
    return (stats.value.status_distribution || []).reduce((sum: number, item: any) => sum + item.count, 0);
});

const maxVal = computed(() => {
    if (!stats.value.monthly) return 10000;
    return Math.max(...stats.value.monthly.map((m: any) => Math.max(m.signed, m.collection))) || 10000;
});

const getPercentage = (actual: number, target: number) => {
  if (!target) return 0;
  return Math.round((actual / target) * 100);
};

const getPercentColor = (actual: number, target: number) => {
  const p = getPercentage(actual, target);
  if (p >= 100) return 'text-green-600 font-bold';
  if (p >= 80) return 'text-blue-600';
  return 'text-orange-500';
};

const load = async () => {
  try {
    const res = await fetchPerformanceReport({ 
        scope: scope.value,
        department_id: scope.value === 'department' ? department.value : undefined,
        time_range: timeRange.value,
        year: selectedYear.value,
        quarter: timeRange.value === 'quarter' ? selectedQuarter.value : undefined,
        month: timeRange.value === 'month' ? selectedMonth.value : undefined
    });
    stats.value = res.data;
  } catch (e) {
    console.error("Failed to load performance report", e);
  }
};

onMounted(load);
</script>

<style scoped>
.el-card {
    border: none;
    box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
}
</style>
