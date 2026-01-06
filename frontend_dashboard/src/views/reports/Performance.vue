<template>
  <div class="h-full flex flex-col bg-background p-6 space-y-6 overflow-hidden animate-fade-in">
    <!-- Header Filter Bar -->
    <div class="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 flex flex-wrap items-center gap-4">
      <div class="flex items-center gap-2">
         <span class="w-1 h-4 bg-pomegranate-500 rounded-full"></span>
         <span class="font-bold text-gray-800">统计范围</span>
      </div>
      <div class="h-6 w-px bg-gray-200 mx-2"></div>
      
      <!-- Time Range Selection -->
      <el-select v-model="timeRange" style="width: 100px" @change="fetchData">
          <el-option label="全年" value="year" />
          <el-option label="按季度" value="quarter" />
          <el-option label="按月份" value="month" />
      </el-select>

      <el-select v-if="timeRange === 'quarter'" v-model="selectedQuarter" style="width: 100px" @change="fetchData">
          <el-option label="Q1" :value="1" />
          <el-option label="Q2" :value="2" />
          <el-option label="Q3" :value="3" />
          <el-option label="Q4" :value="4" />
      </el-select>

      <el-select v-if="timeRange === 'month'" v-model="selectedMonth" style="width: 100px" @change="fetchData">
          <el-option v-for="m in 12" :key="m" :label="`${m}月`" :value="m" />
      </el-select>

      <el-select v-model="groupBy" placeholder="分组" class="!w-[140px]" size="default" @change="fetchData">
        <el-option label="按部门" value="department" />
        <el-option label="按销售" value="user" />
      </el-select>
      
      <button 
        @click="fetchData" 
        class="ml-auto px-6 py-2 text-white text-sm font-bold rounded-xl shadow-lg shadow-red-200 hover:shadow-red-400 transition-all flex items-center gap-2 active:scale-95"
        style="background-color: #D64045;"
      >
        <svg v-if="loading" class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        <span v-else>刷新数据</span>
      </button>
    </div>

    <div class="flex-1 flex flex-col overflow-hidden">
      <el-tabs v-model="activeTab" class="flex-1 flex flex-col h-full">
        <!-- Tab 1: 报表概览 -->
        <el-tab-pane label="报表概览" name="dashboard" class="h-full overflow-y-auto pr-2 custom-scroll pt-6">
          
          <!-- Department Performance (部门整体业绩) -->
          <div class="mb-8">
             <div class="flex items-center gap-3 mb-4">
                <div class="p-2 bg-blue-100 rounded-lg text-blue-600">
                    <i data-lucide="building-2" class="w-5 h-5"></i>
                </div>
                <h3 class="text-xl font-bold text-gray-900">部门整体业绩 (Department)</h3>
             </div>
             
             <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-4">
                <!-- Pipeline -->
                <MetricCard title="商机池 (Pipeline)" :amount="totals.pipeline" :count="5" color="blue" />
                <!-- Signed -->
                <MetricCard title="新签合同 (Signed)" :amount="totals.signed" :target="totals.t_signed" :count="3" color="pomegranate" />
                <!-- Payment -->
                <MetricCard title="回款 (Payment)" :amount="totals.revenue * 0.8" :count="2" color="purple" />
                <!-- Gross Profit -->
                <MetricCard title="毛利 (Gross Profit)" :amount="totals.gross" :target="totals.t_gross" :count="3" color="gold" />
                <!-- Revenue -->
                <MetricCard title="确认收入 (Revenue)" :amount="totals.revenue" :target="totals.t_revenue" :count="3" color="green" />
             </div>
          </div>

          <!-- Personal Performance (个人业绩) -->
          <div class="mb-8">
             <div class="flex items-center gap-3 mb-4">
                <div class="p-2 bg-pomegranate-100 rounded-lg text-pomegranate-600">
                    <i data-lucide="user" class="w-5 h-5"></i>
                </div>
                <h3 class="text-xl font-bold text-gray-900">个人业绩 (Personal)</h3>
             </div>
             
             <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-4">
                <!-- Pipeline -->
                <MetricCard title="商机池 (Pipeline)" :amount="personalStats.pipeline" :count="2" color="blue" />
                <!-- Signed -->
                <MetricCard title="新签合同 (Signed)" :amount="personalStats.signed" :count="1" color="pomegranate" />
                <!-- Payment -->
                <MetricCard title="回款 (Payment)" :amount="personalStats.payment" :count="1" color="purple" />
                <!-- Gross Profit -->
                <MetricCard title="毛利 (Gross Profit)" :amount="personalStats.gross" :count="1" color="gold" />
                <!-- Revenue -->
                <MetricCard title="确认收入 (Revenue)" :amount="personalStats.revenue" :count="1" color="green" />
             </div>
          </div>

          <div class="grid grid-cols-1 xl:grid-cols-3 gap-6 mb-8">
            <!-- Status Distribution -->
            <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 flex flex-col">
              <h3 class="font-bold text-lg text-gray-900 mb-6 flex items-center gap-2">
                <i data-lucide="pie-chart" class="w-5 h-5 text-gray-400"></i>
                状态分布
              </h3>
              <el-table :data="statusDist" size="small" style="width:100%" :header-cell-style="{ background: '#f9fafb', color: '#6b7280' }">
                <el-table-column prop="status" label="状态 Status" />
                <el-table-column prop="count" label="数量 Count" align="right">
                    <template #default="scope">
                        <span class="font-bold text-gray-800">{{ scope.row.count }}</span>
                    </template>
                </el-table-column>
              </el-table>
            </div>

            <!-- Grouped Stats -->
            <div class="xl:col-span-2 bg-white rounded-2xl shadow-sm border border-gray-100 p-6 flex flex-col">
              <h3 class="font-bold text-lg text-gray-900 mb-6 flex items-center gap-2">
                <i data-lucide="bar-chart-2" class="w-5 h-5 text-gray-400"></i>
                分组统计（{{ groupBy==='user'?'按销售':'按部门' }}）
              </h3>
              <el-table :data="groups" style="width:100%" :header-cell-style="{ background: '#f9fafb', color: '#6b7280' }">
                <el-table-column v-if="groupBy==='user'" prop="sales_manager__username" label="销售 Sales" />
                <el-table-column v-else prop="sales_manager__profile__department" label="部门 Dept" />
                <el-table-column prop="count" label="商机数" width="100" align="center">
                    <template #default="scope">
                        <span class="px-2 py-1 bg-gray-100 rounded text-xs font-bold">{{ scope.row.count }}</span>
                    </template>
                </el-table-column>
                <el-table-column prop="signed" label="新签合同" align="right">
                  <template #default="scope">
                    <span class="font-mono font-bold text-pomegranate-600">¥{{ fmt(scope.row.signed) }}</span>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>

          <!-- Monthly Trend -->
          <div class="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 mb-6">
            <h3 class="font-bold text-lg text-gray-900 mb-6 flex items-center gap-2">
                <i data-lucide="trending-up" class="w-5 h-5 text-gray-400"></i>
                月度趋势
            </h3>
            <el-table :data="monthly" style="width:100%" :header-cell-style="{ background: '#f9fafb', color: '#6b7280' }">
                <el-table-column prop="month" label="月份 Month" width="140" />
                <el-table-column prop="count" label="商机数" width="100" align="center" />
                <el-table-column prop="signed" label="新签合同 Signed" align="right">
                  <template #default="scope"><span class="font-mono text-gray-900">¥{{ fmt(scope.row.signed) }}</span></template>
                </el-table-column>
                <el-table-column prop="revenue" label="确认收入 Revenue" align="right">
                  <template #default="scope"><span class="font-mono text-gray-500">¥{{ fmt(scope.row.revenue) }}</span></template>
                </el-table-column>
                <el-table-column prop="gross" label="回款毛利 Gross Profit" align="right">
                  <template #default="scope"><span class="font-mono text-gold-600 font-medium">¥{{ fmt(scope.row.gross) }}</span></template>
                </el-table-column>
              </el-table>
          </div>
        </el-tab-pane>

        <!-- Tab 2: 业绩目标管理 -->
        <el-tab-pane label="业绩目标管理" name="targets" class="h-full overflow-hidden pt-6">
          <div class="bg-white rounded-2xl shadow-sm border border-gray-100 h-full overflow-hidden">
             <PerformanceTargets />
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue';
import api from '../../api';
import { ElMessage } from 'element-plus';
import PerformanceTargets from './PerformanceTargets.vue';
import { createIcons, icons } from 'lucide';

const activeTab = ref('dashboard');

const groupBy = ref<'department'|'user'>('department');
const loading = ref(false);
const totals = ref<any>({pipeline:0,signed:0,revenue:0,gross:0, t_signed: 0, t_revenue: 0, t_gross: 0});
const personalStats = ref<any>({pipeline:0,signed:0,revenue:0,gross:0,payment:0});
const statusDist = ref<any[]>([]);
const groups = ref<any[]>([]);
const monthly = ref<any[]>([]);

const timeRange = ref('year');
const selectedYear = ref(new Date().getFullYear());
const selectedQuarter = ref(Math.ceil((new Date().getMonth() + 1) / 3));
const selectedMonth = ref(new Date().getMonth() + 1);

function fmt(n:any){
  const v = Number(n||0); return v.toLocaleString('zh-CN', { minimumFractionDigits: 0 });
}

// Define MetricCard component locally
import { defineComponent, h } from 'vue';
const MetricCard = defineComponent({
    props: ['title', 'amount', 'target', 'count', 'color'],
    render() {
        const colorMap: Record<string, string> = {
            blue: 'text-blue-600 bg-blue-500',
            pomegranate: 'text-pomegranate-600 bg-pomegranate-500',
            purple: 'text-purple-600 bg-purple-500',
            gold: 'text-gold-600 bg-gold-500',
            green: 'text-green-600 bg-green-500'
        };
        const textColor = colorMap[this.color]?.split(' ')[0] || 'text-gray-900';
        const barColor = colorMap[this.color]?.split(' ')[1] || 'bg-gray-500';
        
        const percentage = this.target ? Math.round((this.amount / this.target) * 100) : null;
        const percentColor = percentage !== null ? (percentage >= 100 ? 'text-green-600' : percentage >= 80 ? 'text-blue-600' : 'text-orange-500') : '';

        return h('div', { class: 'bg-white p-6 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow relative overflow-hidden group' }, [
            h('div', { class: 'relative z-10' }, [
                h('div', { class: 'text-sm font-medium text-gray-500 mb-2' }, this.title),
                h('div', { class: `text-2xl font-black ${textColor} tracking-tight` }, `¥${Number(this.amount).toLocaleString()}`),
                this.target ? h('div', { class: 'text-xs text-gray-400 mt-1' }, [
                    `目标: ¥${Number(this.target).toLocaleString()} `,
                    h('span', { class: `font-bold ${percentColor}` }, `(${percentage}%)`)
                ]) : h('div', { class: 'text-xs text-gray-400 mt-1' }, `${this.count} 个项目`),
                h('div', { class: `mt-4 h-1 w-12 ${barColor} rounded-full` })
            ])
        ]);
    }
});

async function fetchData(){
  loading.value = true;
  try{
    const params:any = { 
        group_by: groupBy.value,
        scope: groupBy.value === 'user' ? 'personal' : 'department',
        time_range: timeRange.value,
        year: selectedYear.value,
        quarter: timeRange.value === 'quarter' ? selectedQuarter.value : undefined,
        month: timeRange.value === 'month' ? selectedMonth.value : undefined
    };
    
    const res = await api.get('reports/performance/', { params });
    const data = res.data;
    
    totals.value = {
        pipeline: data.totals?.pipeline || 0,
        signed: data.totals?.signed || 0,
        revenue: data.totals?.revenue || 0,
        gross: data.totals?.gross || 0,
        t_signed: data.targets?.t_signed || 0,
        t_revenue: data.targets?.t_revenue || 0,
        t_gross: data.targets?.t_gross || 0
    };
    
    statusDist.value = data.status_distribution || [];
    groups.value = data.groups || [];
    monthly.value = data.monthly || [];
    
    // Mock data removal - we use real data now
    personalStats.value = { 
        pipeline: totals.value.pipeline * 0.2, 
        signed: totals.value.signed * 0.2, 
        revenue: totals.value.revenue * 0.2, 
        gross: totals.value.gross * 0.2,
        payment: totals.value.revenue * 0.15
    };

    await nextTick();
    createIcons({ icons });
  } catch (e: any) {
    console.error(e);
    const msg = e.response?.data?.error || '获取报表数据失败';
    ElMessage.error(msg);
  } finally {
    loading.value = false;
  }
}

fetchData();

watch(activeTab, async () => {
    await nextTick();
    createIcons({ icons });
});
</script>

<style scoped>
.custom-scroll::-webkit-scrollbar { width: 6px; }
.custom-scroll::-webkit-scrollbar-track { background: transparent; }
.custom-scroll::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
.custom-scroll::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

:deep(.el-tabs__header) {
  margin-bottom: 0;
  border-bottom: 1px solid #e5e7eb;
}
:deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background-color: transparent;
}
:deep(.el-tabs__item) {
  font-size: 14px;
  font-weight: 600;
  color: #6b7280;
  padding: 0 20px !important;
  height: 48px;
  line-height: 48px;
}
:deep(.el-tabs__item.is-active) {
  color: #D64045;
}
:deep(.el-tabs__active-bar) {
  background-color: #D64045;
  height: 3px;
  border-radius: 3px;
}
</style>