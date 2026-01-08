<template>
  <div class="min-h-screen flex flex-col bg-[#f8fafc] font-sans">
    <!-- Main Content -->
    <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
      
      <!-- Stats Overview -->
      <div class="grid grid-cols-1 gap-5 sm:grid-cols-4 mb-8">
        <div class="bg-white overflow-hidden shadow rounded-xl border border-gray-100">
          <div class="px-4 py-5 sm:p-6">
            <dt class="text-sm font-medium text-gray-500 truncate">项目总数</dt>
            <dd class="mt-1 text-3xl font-semibold text-gray-900">{{ stats.total }}</dd>
          </div>
        </div>
        <div class="bg-white overflow-hidden shadow rounded-xl border border-gray-100">
          <div class="px-4 py-5 sm:p-6">
            <dt class="text-sm font-medium text-gray-500 truncate">进行中</dt>
            <dd class="mt-1 text-3xl font-semibold text-green-600">{{ stats.active }}</dd>
          </div>
        </div>
        <div class="bg-white overflow-hidden shadow rounded-xl border border-gray-100">
          <div class="px-4 py-5 sm:p-6">
            <dt class="text-sm font-medium text-gray-500 truncate">总预算 (CNY)</dt>
            <dd class="mt-1 text-3xl font-semibold text-blue-600">¥{{ formatNumber(stats.budget) }}</dd>
          </div>
        </div>
        <div class="bg-white overflow-hidden shadow rounded-xl border border-gray-100">
          <div class="px-4 py-5 sm:p-6">
            <dt class="text-sm font-medium text-gray-500 truncate">关联卡片</dt>
            <dd class="mt-1 text-3xl font-semibold text-purple-600">{{ stats.cards }}</dd>
          </div>
        </div>
      </div>

      <!-- Filter & Search Bar -->
      <div class="bg-white p-4 rounded-xl border border-gray-100 shadow-sm mb-6">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div class="flex items-center gap-4 flex-1">
            <div class="relative flex-1 max-w-lg">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <i data-lucide="search" class="text-gray-400 w-5 h-5"></i>
              </div>
              <input 
                type="text" 
                v-model="searchQuery" 
                class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-blue-500 focus:border-blue-500 transition-all" 
                placeholder="搜索项目名称、编号、客户..."
              >
            </div>
            <select 
              v-model="statusFilter" 
              class="pl-3 pr-10 py-2 border border-gray-300 rounded-lg text-sm focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">全部状态</option>
              <option value="active">进行中</option>
              <option value="planning">规划中</option>
              <option value="completed">已完成</option>
            </select>
          </div>
          <div class="flex items-center gap-2 text-sm text-gray-600">
            <span v-if="loading">正在加载数据...</span>
            <span v-else>已加载 {{ projects.length }} 个项目</span>
            <button @click="router.push('/projects/timeline/global')" class="ml-4 bg-white border border-gray-200 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors flex items-center gap-2 shadow-sm">
              <i data-lucide="calendar" class="w-4 h-4 text-gray-500"></i> 全局时间轴
            </button>
            <button @click="showCreateModal = true" class="ml-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors flex items-center gap-2 shadow-sm shadow-blue-200">
              <i data-lucide="plus" class="w-4 h-4"></i> 新建项目
            </button>
          </div>
        </div>
      </div>

      <!-- Project Grid -->
      <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div 
          v-for="project in filteredProjects" 
          :key="project.id"
          @click="navigateToProject(project.id)"
          class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-lg transition-all cursor-pointer relative group card-hover"
        >
          <div class="flex justify-between items-start mb-4 gap-4">
            <div class="flex items-center gap-3 min-w-0">
              <div class="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center text-blue-600 font-bold text-lg flex-shrink-0">
                {{ project.name ? project.name.substring(0, 1) : 'P' }}
              </div>
              <div class="min-w-0">
                <h3 class="text-lg font-bold text-gray-900 group-hover:text-blue-600 transition-colors line-clamp-1 truncate">{{ project.name }}</h3>
                <div class="text-xs text-gray-500 font-mono truncate">{{ project.code }}</div>
              </div>
            </div>
            <span 
              class="px-2.5 py-0.5 rounded-full text-xs font-medium border flex-shrink-0 whitespace-nowrap"
              :class="getStatusClass(project.status)"
            >
              {{ getStatusLabel(project.status) }}
            </span>
          </div>
          
          <div class="space-y-3 mb-6">
            <div class="flex justify-between text-sm">
              <span class="text-gray-500">客户</span>
              <span class="font-medium text-gray-900 truncate max-w-[120px]">{{ project.customer_name || '-' }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-gray-500">关联商机</span>
              <span class="font-medium text-gray-900 truncate max-w-[120px]">{{ project.opportunity_name || '-' }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-gray-500">预算</span>
              <span class="font-medium text-gray-900">¥{{ formatNumber(project.budget) }}</span>
            </div>
            <div class="flex justify-between text-sm">
              <span class="text-gray-500">负责人</span>
              <span class="flex items-center gap-1">
                <div class="w-5 h-5 rounded-full bg-gray-200 flex items-center justify-center text-[10px] text-gray-600">
                  {{ project.owner_name ? project.owner_name.substring(0, 1) : 'M' }}
                </div>
                <span class="text-gray-700">{{ project.owner_name || '未分配' }}</span>
              </span>
            </div>
          </div>

          <div class="pt-4 border-t border-gray-100 flex items-center justify-between text-xs text-gray-500">
            <div class="flex items-center gap-1">
              <i data-lucide="layers" class="w-3.5 h-3.5"></i>
              {{ getProjectCardCount(project.id) }} 张卡片
            </div>
            <div class="flex items-center gap-1">
              <i data-lucide="clock" class="w-3.5 h-3.5"></i>
              {{ formatDate(project.updated_at) }}
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Create Project Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-xl shadow-2xl w-full max-w-2xl transform transition-all">
        <div class="flex justify-between items-center p-6 border-b border-gray-100">
          <h3 class="text-xl font-bold text-gray-900">新建项目</h3>
          <button @click="showCreateModal = false" class="text-gray-400 hover:text-gray-500 transition-colors">
            <i data-lucide="x" class="w-6 h-6"></i>
          </button>
        </div>
        <div class="p-6 space-y-4">
          <!-- Row 1: Opportunity & Customer -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">关联商机 *</label>
              <el-select
                v-model="createForm.opportunity"
                filterable
                remote
                clearable
                placeholder="搜索商机"
                :remote-method="searchOpportunities"
                :loading="opportunityLoading"
                @change="handleOpportunitySelect"
                class="w-full"
              >
                <el-option
                  v-for="item in opportunityOptions"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                />
              </el-select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">客户名称</label>
              <el-select
                v-model="createForm.customer"
                filterable
                remote
                clearable
                placeholder="搜索客户"
                :remote-method="searchCustomers"
                :loading="customerLoading"
                @change="handleCustomerSelect"
                class="w-full"
              >
                <el-option
                  v-for="item in customerOptions"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                />
              </el-select>
            </div>
          </div>
          
          <!-- Row 2: Name & Code -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">项目名称 *</label>
              <input v-model="createForm.name" type="text" class="w-full border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm p-2 border">
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">项目编号 *</label>
              <input v-model="createForm.code" type="text" class="w-full border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm p-2 border" placeholder="PROJ-2024-001">
            </div>
          </div>

          <!-- Row 3: Customer Code & Budget -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">客户编号</label>
              <input v-model="createForm.customer_code" type="text" class="w-full border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm p-2 border" placeholder="CUST-001">
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">预算收入 (元)</label>
              <input v-model="createForm.budget" type="number" class="w-full border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm p-2 border">
            </div>
          </div>

          <!-- Description -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">项目描述</label>
            <textarea v-model="createForm.description" rows="3" class="w-full border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm p-2 border"></textarea>
          </div>

          <!-- Row 4: Status & Owner -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">状态</label>
              <select v-model="createForm.status" class="w-full border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm p-2 border">
                <option value="planning">规划中</option>
                <option value="active">进行中</option>
                <option value="completed">已完成</option>
                <option value="suspended">暂停</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">负责人</label>
              <el-select
                v-model="createForm.owner"
                filterable
                remote
                clearable
                placeholder="搜索负责人"
                :remote-method="searchUsers"
                :loading="userLoading"
                class="w-full"
              >
                <el-option
                  v-for="item in userOptions"
                  :key="item.id"
                  :label="item.full_name || item.username"
                  :value="item.id"
                />
              </el-select>
            </div>
          </div>
        </div>
        <div class="p-6 border-t border-gray-100 bg-gray-50 rounded-b-xl flex justify-end gap-3">
          <button @click="showCreateModal = false" class="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50">取消</button>
          <button @click="submitCreateProject" class="px-4 py-2 bg-blue-600 border border-transparent rounded-lg text-sm font-medium text-white hover:bg-blue-700">创建项目</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick, watch } from 'vue';
import { useRouter } from 'vue-router';
import { createIcons, icons } from 'lucide';
import { ElMessage, ElMessageBox } from 'element-plus';
import api from '../../api';

const router = useRouter();

// State
const projects = ref<any[]>([]);
const cards = ref<any[]>([]);
const loading = ref(true);
const searchQuery = ref('');
const statusFilter = ref('all');
const showCreateModal = ref(false);

const createForm = reactive({
  name: '',
  code: '',
  opportunity: undefined as number | undefined,
  customer: undefined as number | undefined,
  customer_name: '', // Optional fallback
  customer_code: '',
  description: '',
  budget: 0,
  status: 'active',
  owner: undefined as number | undefined,
  owner_name: '' // Optional fallback
});

// Autocomplete State
const customerLoading = ref(false);
const customerOptions = ref<any[]>([]);
const userLoading = ref(false);
const userOptions = ref<any[]>([]);
const opportunityLoading = ref(false);
const opportunityOptions = ref<any[]>([]);

// Autocomplete Methods
async function searchCustomers(query: string) {
  customerLoading.value = true;
  try {
    const params: any = { limit: 20 };
    if (query) params.name = query;
    const res = await api.post('chat/', { intent: 'list', entity: 'customer', filters: params });
    customerOptions.value = res.data.result || [];
  } catch (e) {
    console.error(e);
  } finally {
    customerLoading.value = false;
  }
}

function handleCustomerSelect(val: any) {
  const selected = customerOptions.value.find(c => c.id === val);
  if (selected) {
    createForm.customer_code = selected.customer_code || '';
    createForm.customer_name = selected.name;
  }
}

async function searchOpportunities(query: string) {
  opportunityLoading.value = true;
  try {
    const res = await api.get('opportunities/', { params: { search: query } });
    opportunityOptions.value = (res.data.results || res.data || []);
  } catch (e) {
    console.error("Failed to search opportunities", e);
  } finally {
    opportunityLoading.value = false;
  }
}

async function handleOpportunitySelect(val: any) {
  if (!val) {
    createForm.opportunity = undefined;
    createForm.customer = undefined;
    createForm.customer_name = '';
    createForm.customer_code = '';
    return;
  }

  const selected = opportunityOptions.value.find(o => o.id === val);
  if (selected) {
    if (selected.customer) {
        // Check if customer is object or ID
        const customerId = typeof selected.customer === 'object' ? selected.customer.id : selected.customer;
        
        createForm.customer = customerId;
        
        // If we have the object, use it directly
        if (typeof selected.customer === 'object') {
             createForm.customer_name = selected.customer.name;
             if (selected.customer.code) createForm.customer_code = selected.customer.code;
             
             // Add to options if not present
             if (!customerOptions.value.some(c => c.id === customerId)) {
                 customerOptions.value.push(selected.customer);
             }
        } else {
             // It's an ID, check if we have it in options
             const existing = customerOptions.value.find(c => c.id === customerId);
             if (existing) {
                 createForm.customer_name = existing.name;
                 if (existing.code) createForm.customer_code = existing.code;
             } else {
                 // Fetch from API
                 try {
                     const res = await api.get(`customers/${customerId}/`);
                     const cust = res.data;
                     createForm.customer_name = cust.name;
                     createForm.customer_code = cust.code || '';
                     if (!customerOptions.value.some(c => c.id === cust.id)) {
                         customerOptions.value.push(cust);
                     }
                 } catch (e) {
                     console.error("Failed to fetch customer", e);
                     ElMessage.warning('无法自动获取客户信息，请手动选择');
                 }
             }
        }
    } else {
        createForm.customer = undefined;
        createForm.customer_name = '';
        createForm.customer_code = '';
    }
  }
}

async function searchUsers(query: string) {
  userLoading.value = true;
  try {
    // Try simple list endpoint first
    const res = await api.get('users/simple/', { params: { search: query } });
    userOptions.value = (res.data.results || res.data).map((u: any) => ({
      id: u.id,
      username: u.username,
      full_name: u.name || `${u.last_name}${u.first_name}`.trim() || u.username
    }));
  } catch (e) {
    console.error("Failed to fetch users from simple list, trying admin endpoint", e);
    try {
      const res = await api.get('admin/users/', { params: { search: query } });
      userOptions.value = (res.data.results || res.data).map((u: any) => ({
        id: u.id,
        username: u.username,
        full_name: `${u.last_name}${u.first_name}`.trim() || u.username
      }));
    } catch (e2) {
      console.error("Failed to fetch users from admin endpoint", e2);
      userOptions.value = [];
    }
  } finally {
    userLoading.value = false;
  }
}

// Initial fetch for options (optional)
onMounted(() => {
  searchCustomers('');
  searchUsers('');
  searchOpportunities('');
});

// Computed Stats
const stats = computed(() => {
  const active = projects.value.filter(p => p.status === 'active' || p.status === 'IN_PROGRESS').length;
  const totalBudget = projects.value.reduce((sum, p) => sum + (Number(p.budget) || 0), 0);
  return {
    total: projects.value.length,
    active: active,
    budget: totalBudget,
    cards: cards.value.length
  };
});

// Filtered Projects
const filteredProjects = computed(() => {
  if (!projects.value) return [];
  
  return projects.value.filter(p => {
    // Status Filter
    if (statusFilter.value && statusFilter.value !== 'all') {
      const pStatus = (p.status || '').toLowerCase();
      const filter = statusFilter.value.toLowerCase();
      
      // 特殊处理：前端 'active' 对应后端的 'in_progress'
      if (filter === 'active') {
        if (pStatus !== 'in_progress' && pStatus !== 'active') return false;
      } else if (pStatus !== filter) {
        return false;
      }
    }
    
    // Search Filter
    if (searchQuery.value) {
      const q = searchQuery.value.toLowerCase();
      const matchName = (p.name || '').toLowerCase().includes(q);
      const matchCode = (p.code || '').toLowerCase().includes(q);
      const matchCust = (p.customer_name || '').toLowerCase().includes(q);
      const matchOpp = (p.opportunity_name || '').toLowerCase().includes(q);
      if (!matchName && !matchCode && !matchCust && !matchOpp) return false;
    }
    
    return true;
  });
});

// Initial Load
onMounted(async () => {
  await loadData();
});

// Watch for DOM updates to refresh icons
watch([filteredProjects, showCreateModal], async () => {
  await nextTick();
  createIcons({ icons });
});

async function loadData() {
  loading.value = true;
  try {
    const [pRes, cRes] = await Promise.all([
      api.get('projects/'),
      api.get('project-cards/')
    ]);
    
    // Handle DRF pagination if present
    projects.value = Array.isArray(pRes.data) ? pRes.data : (pRes.data.results || []);
    cards.value = Array.isArray(cRes.data) ? cRes.data : (cRes.data.results || []);
    
    await nextTick();
    createIcons({ icons });
  } catch (e) {
    console.error("Failed to load data", e);
  } finally {
    loading.value = false;
  }
}

async function submitCreateProject() {
  if (!createForm.opportunity) {
      ElMessage.warning('请选择关联商机');
      return;
  }
  try {
    const { customer_name, owner_name, ...rest } = createForm;
    const payload = {
      ...rest,
      status: createForm.status === 'active' ? 'IN_PROGRESS' : createForm.status.toUpperCase()
    };
    
    await api.post('projects/', payload);
    showCreateModal.value = false;
    ElMessage.success('项目创建成功');
    // Reset form
    Object.assign(createForm, {
      name: '',
      code: '',
      opportunity: undefined,
      customer: undefined,
      customer_name: '',
      customer_code: '',
      description: '',
      budget: 0,
      status: 'active',
      owner: undefined,
      owner_name: ''
    });
    await loadData();
  } catch (e) {
    console.error("Failed to create project", e);
    ElMessage.error('创建项目失败，请检查输入');
  }
}

// Helpers
function formatNumber(num: any) {
  return Number(num).toLocaleString('zh-CN');
}

function formatDate(dateStr: any) {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('zh-CN');
}

function getStatusLabel(status: any) {
  const map: any = {
    'active': '进行中',
    'IN_PROGRESS': '进行中',
    'planning': '规划中',
    'PLANNING': '规划中',
    'completed': '已完成',
    'COMPLETED': '已完成',
    'suspended': '暂停',
    'SUSPENDED': '暂停'
  };
  return map[status] || status;
}

function getStatusClass(status: any) {
  const s = (status || '').toLowerCase();
  if (s === 'active' || s === 'in_progress') return 'bg-green-100 text-green-800';
  if (s === 'planning') return 'bg-blue-100 text-blue-800';
  if (s === 'completed') return 'bg-gray-100 text-gray-800';
  return 'bg-gray-100 text-gray-800';
}

function getProjectCardCount(projectId: any) {
  return cards.value.filter(c => c.project === projectId).length;
}

async function handleDeleteProject(project: any) {
  try {
    await ElMessageBox.confirm(
      `确定要删除项目 "${project.name}" 吗？此操作不可逆，且可能关联删除相关数据。`,
      '删除确认',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    );

    await api.delete(`projects/${project.id}/`);
    ElMessage.success('项目删除成功');
    await loadData(); // 刷新列表
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Delete project failed:', error);
      ElMessage.error('删除失败，请稍后重试');
    }
  }
}

function navigateToProject(id: number) {
  router.push(`/projects/${id}`);
}
</script>

<style scoped>
.card-hover:hover { 
  transform: translateY(-2px); 
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05); 
}
.custom-scroll::-webkit-scrollbar { width: 6px; }
.custom-scroll::-webkit-scrollbar-track { background: #f1f1f1; }
</style>