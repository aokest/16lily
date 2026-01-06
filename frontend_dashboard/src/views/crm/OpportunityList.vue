<template>
  <div class="h-full flex flex-col bg-background animate-fade-in">
    <!-- Header Actions -->
    <div class="mb-6 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div class="relative group">
        <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400 group-focus-within:text-pomegranate-500 transition-colors" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd" />
          </svg>
        </div>
        <input 
          v-model="search" 
          @keyup.enter="fetchData"
          type="text" 
          placeholder="搜索商机名称 / 客户..." 
          class="pl-10 pr-4 py-2.5 w-[300px] bg-white border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-pomegranate-500/20 focus:border-pomegranate-500 transition-all shadow-sm hover:border-gray-300"
        >
      </div>
      <button 
        @click="handleCreate"
        class="px-5 py-2.5 text-white text-sm font-bold rounded-xl shadow-lg shadow-red-200 hover:shadow-red-400 transition-all flex items-center gap-2 active:scale-95"
        style="background-color: #D64045;"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        新建商机
      </button>
    </div>

    <!-- Modern Card Table -->
    <div class="bg-white rounded-2xl shadow-card border border-gray-100 overflow-hidden flex flex-col flex-1">
      <el-table 
        :data="opportunities" 
        style="width: 100%" 
        v-loading="loading" 
        :header-cell-style="{ background: '#F9FAFB', color: '#1A1A1A', fontWeight: '700', borderBottom: '1px solid #E5E7EB' }"
        :row-class-name="'hover:bg-gray-50 transition-colors cursor-pointer'"
        @row-click="handleEdit"
      >
        <el-table-column prop="name" label="商机名称" min-width="200">
          <template #default="{ row }">
            <div class="font-bold text-graphite">{{ row.name }}</div>
            <div class="text-xs text-gray-500 mt-0.5 truncate">{{ row.customer_company }}</div>
          </template>
        </el-table-column>
        
        <el-table-column prop="amount" label="预计金额" width="160" sortable>
          <template #default="{ row }">
            <span class="font-mono font-bold text-pomegranate-600">¥{{ row.amount?.toLocaleString() }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="stage" label="阶段" width="140">
           <template #default="{ row }">
              <span 
                class="px-2.5 py-1 rounded-lg text-xs font-bold inline-flex items-center gap-1.5"
                :class="{
                  'bg-green-50 text-green-700': row.stage === 'COMPLETED' || row.stage === 'WON',
                  'bg-blue-50 text-blue-700': ['REQ_ANALYSIS', 'INITIATION', 'BIDDING', 'DELIVERY', 'AFTER_SALES'].includes(row.stage),
                  'bg-yellow-50 text-yellow-700': row.stage === 'SUSPENDED',
                  'bg-red-50 text-red-700': row.stage === 'TERMINATED' || row.stage === 'LOST',
                  'bg-gray-100 text-gray-600': row.stage === 'CONTACT'
                }"
              >
                <span class="w-1.5 h-1.5 rounded-full" :class="{
                  'bg-green-500': row.stage === 'COMPLETED' || row.stage === 'WON',
                  'bg-blue-500': ['REQ_ANALYSIS', 'INITIATION', 'BIDDING', 'DELIVERY', 'AFTER_SALES'].includes(row.stage),
                  'bg-yellow-500': row.stage === 'SUSPENDED',
                  'bg-red-500': row.stage === 'TERMINATED' || row.stage === 'LOST',
                  'bg-gray-400': row.stage === 'CONTACT'
                }"></span>
                {{ row.stage_display || getStageLabel(row.stage) }}
              </span>
           </template>
        </el-table-column>
        
        <el-table-column prop="sales_manager_name" label="负责人" width="120">
          <template #default="{ row }">
            <div class="flex items-center gap-2">
              <div class="w-6 h-6 rounded-full bg-gradient-to-br from-gold-400 to-gold-600 text-white text-xs flex items-center justify-center font-bold">
                {{ row.sales_manager_name?.[0] || 'U' }}
              </div>
              <span class="text-sm text-gray-700">{{ row.sales_manager_name }}</span>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
              <span class="text-xs text-gray-400 font-mono">
                {{ row.created_at ? new Date(row.created_at).toLocaleDateString() : '-' }}
              </span>
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="100" fixed="right" align="center">
          <template #default="{ row }">
            <div class="flex items-center justify-center gap-2" @click.stop>
              <button 
                @click.stop="handleEdit(row)"
                class="p-1.5 text-gray-400 hover:text-pomegranate-500 hover:bg-pomegranate-50 rounded-lg transition-all"
                title="编辑"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/></svg>
              </button>
              <button 
                @click.stop="handleDelete(row)"
                class="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all"
                title="删除"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/></svg>
              </button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- Pagination -->
      <div class="p-4 border-t border-gray-100 flex justify-end bg-gray-50/50">
          <el-pagination 
              layout="total, prev, pager, next" 
              :total="total" 
              :page-size="pageSize" 
              background
              @current-change="handlePageChange"
          />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../../api';
import { ElMessage, ElMessageBox } from 'element-plus';

const router = useRouter();
const opportunities = ref<any[]>([]);
const loading = ref(false);
const search = ref('');
const total = ref(0);
const pageSize = ref(20);
const currentPage = ref(1);

const getStageLabel = (stage: string) => {
    const labels: Record<string, string> = {
        'CONTACT': '接触阶段',
        'REQ_ANALYSIS': '需求分析',
        'INITIATION': '客户立项',
        'BIDDING': '招采阶段',
        'DELIVERY': '交付实施',
        'AFTER_SALES': '售后阶段',
        'COMPLETED': '项目完成',
        'SUSPENDED': '商机暂停',
        'TERMINATED': '商机终止',
        'WON': '赢单',
        'LOST': '输单'
    };
    return labels[stage] || stage;
};

const fetchData = async () => {
  loading.value = true;
  console.log('Fetching opportunities with page:', currentPage.value, 'search:', search.value);
  try {
    const params = {
        page: currentPage.value,
        search: search.value
    };
    const res = await api.get('opportunities/', { params });
    console.log('Opportunities API response:', res.status, res.data);
    
    // DRF default pagination returns { count: 100, next: '...', previous: '...', results: [] }
    if (res.data && res.data.results) {
        opportunities.value = res.data.results;
        total.value = res.data.count;
    } else if (Array.isArray(res.data)) {
        // If no pagination (returns array directly)
        opportunities.value = res.data;
        total.value = res.data.length;
    } else {
        console.warn('Unexpected API response structure:', res.data);
        opportunities.value = [];
        total.value = 0;
    }
  } catch (e: any) {
    console.error('Fetch opportunities error:', e);
    const errorMsg = e.response?.data?.detail || e.message || '获取商机列表失败';
    ElMessage.error(errorMsg);
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
// @ts-ignore
const _useLogout = logout;

onMounted(() => {
    fetchData();
});
</script>
