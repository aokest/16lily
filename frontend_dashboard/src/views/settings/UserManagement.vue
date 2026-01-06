<template>
  <div class="h-full flex flex-col bg-slate-50">
    <header class="bg-white border-b border-slate-200 px-8 py-6 flex justify-between items-center shrink-0">
      <div class="flex flex-col gap-1">
        <h1 class="text-2xl font-bold text-slate-800 tracking-tight">用户管理</h1>
        <div class="text-sm text-slate-500">管理系统用户、角色权限与组织归属</div>
      </div>
      <el-button type="primary" size="large" @click="handleCreate">
        <el-icon class="mr-1"><Plus /></el-icon> 新增用户
      </el-button>
    </header>

    <main class="flex-1 p-8 overflow-auto">
      <div class="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
        <div class="p-4 border-b border-slate-50 flex justify-between items-center">
           <div class="flex gap-2">
             <el-input v-model="search" placeholder="搜索用户名/邮箱..." style="width: 240px" clearable @clear="fetchData" @keyup.enter="fetchData">
                <template #prefix><el-icon><Search /></el-icon></template>
             </el-input>
             <el-button @click="fetchData">搜索</el-button>
           </div>
        </div>

        <el-table :data="items" v-loading="loading" style="width: 100%" :header-cell-style="{background:'#f8fafc', color:'#475569', fontWeight:'600'}">
          <el-table-column prop="username" label="用户名" width="150" />
          <el-table-column label="姓名" width="120">
            <template #default="{row}">{{ row.last_name }}{{ row.first_name }}</template>
          </el-table-column>
          <el-table-column label="部门" width="120">
            <template #default="{row}">
               <el-tag effect="plain" size="small">{{ row.department || '-' }}</el-tag>
            </template>
          </el-table-column>
           <el-table-column label="角色" width="120">
            <template #default="{row}">
               <el-tag v-if="row.is_superuser" type="danger" size="small">超级管理员</el-tag>
               <el-tag v-else-if="row.is_staff" type="warning" size="small">后台职员</el-tag>
               <el-tag v-else type="info" size="small">普通用户</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="email" label="邮箱" min-width="180" />
          <el-table-column prop="date_joined" label="加入时间" width="180">
             <template #default="{row}">{{ new Date(row.date_joined).toLocaleDateString() }}</template>
          </el-table-column>
          <el-table-column label="状态" width="100">
             <template #default="{row}">
               <el-switch v-model="row.is_active" size="small" @change="toggleStatus(row)" />
             </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{row}">
              <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
              <el-popconfirm title="确定重置该用户密码?" @confirm="handleResetPwd(row)">
                 <template #reference>
                   <el-button link type="warning">重置密码</el-button>
                 </template>
              </el-popconfirm>
              <el-popconfirm title="确定要删除该用户吗？此操作不可恢复。" @confirm="handleDelete(row)">
                 <template #reference>
                   <el-button link type="danger">删除</el-button>
                 </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
        <div class="p-4 flex justify-end">
           <el-pagination background layout="prev, pager, next" :total="total" :page-size="pageSize" @current-change="handlePageChange" />
        </div>
      </div>
    </main>

    <!-- Dialog -->
    <el-dialog v-model="dialogVisible" :title="isEdit?'编辑用户':'新增用户'" width="600px">
      <el-form :model="form" label-width="80px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="用户名">
              <el-input v-model="form.username" :disabled="isEdit" placeholder="登录账号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
             <el-form-item label="密码" v-if="!isEdit">
              <el-input v-model="form.password" type="password" show-password placeholder="初始密码" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="姓氏">
              <el-input v-model="form.last_name" placeholder="例如：张" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="名字">
              <el-input v-model="form.first_name" placeholder="例如：三" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="邮箱">
          <el-input v-model="form.email" placeholder="Email" />
        </el-form-item>
        
        <el-divider content-position="left">详细信息</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="部门">
              <el-tree-select
                v-model="form.profile_write.department_link"
                :data="departmentTree"
                check-strictly
                :render-after-expand="false"
                placeholder="选择部门"
                clearable
                filterable
                style="width: 100%"
                :props="{ label: 'name', value: 'id', children: 'children' }"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
             <el-form-item label="岗位属性">
              <el-select v-model="form.profile_write.job_category" placeholder="选择属性" @change="handleCategoryChange">
                 <el-option v-for="(label, key) in categoryMap" :key="key" :label="label" :value="key" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="岗位名称">
              <el-select v-model="form.profile_write.job_title" placeholder="选择岗位名称" :disabled="!form.profile_write.job_category">
                 <el-option v-for="t in filteredJobTitles" :key="t.id" :label="t.name" :value="t.id" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="职级">
              <el-select v-model="form.profile_write.job_rank" placeholder="选择职级" clearable>
                 <el-option v-for="(label, key) in rankMap" :key="key" :label="label" :value="key" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20" v-if="showRankLevel">
          <el-col :span="12">
            <el-form-item label="职级等级">
              <el-radio-group v-model="form.profile_write.job_rank_level">
                <el-radio label="NORMAL">普通</el-radio>
                <el-radio label="SENIOR">高级</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="汇报对象">
          <el-select v-model="form.profile_write.report_to" placeholder="选择汇报对象" clearable filterable style="width: 100%" :disabled="!canSkipReportTo && false">
            <el-option v-for="u in allUsers" :key="u.id" :label="`${u.last_name}${u.first_name} (${u.username})`" :value="u.id" :disabled="u.id === form.id" />
          </el-select>
          <div class="text-xs text-slate-400 mt-1" v-if="!canSkipReportTo">非高层管理人员必填</div>
          <div class="text-xs text-green-600 mt-1" v-else>高层管理人员可选填</div>
        </el-form-item>

        <el-form-item label="权限">
           <div class="flex flex-col gap-2">
             <div class="flex items-center gap-6">
               <el-checkbox v-model="form.is_staff">后台登录权限</el-checkbox>
               <el-checkbox v-model="form.is_superuser">超级管理员</el-checkbox>
             </div>
             <div class="flex items-center gap-4">
               <el-checkbox v-model="assistantProxyEnabled" :disabled="!isAssistant">助理同权（启用后等同汇报对象权限）</el-checkbox>
               <span class="text-xs text-slate-400">需要岗位属性为“助理”且填写“汇报对象”</span>
             </div>
           </div>
        </el-form-item>

      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitting">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import api from '../../api';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, Search } from '@element-plus/icons-vue';

const items = ref([]);
const allUsers = ref<any[]>([]);
const departmentTree = ref<any[]>([]);
const jobTitles = ref<any[]>([]);
const loading = ref(false);
const dialogVisible = ref(false);
const submitting = ref(false);
const isEdit = ref(false);
const search = ref('');
const currentPage = ref(1);
const pageSize = ref(15);
const total = ref(0);
const assistantProxyEnabled = ref(false);

const categoryMap: Record<string, string> = {
  'MANAGEMENT': '管理',
  'RND': '研发',
  'SALES': '销售',
  'RESEARCHER': '研究员',
  'MARKETING': '市场',
  'OPERATION': '运营',
  'DESIGN': '设计',
  'SYSADMIN': '系统管理员',
  'ASSISTANT': '助理',
  'OTHER': '其他'
};

const rankMap: Record<string, string> = {
  'ASSISTANT': '助理',
  'SPECIALIST': '专员',
  'SUPERVISOR': '主任',
  'MANAGER': '经理',
  'DIRECTOR': '总监',
  'DEPUTY_DIRECTOR': '副总监',
  'VP': '副总裁',
  'SVP': '高级副总裁',
  'AP': '助理总裁',
  'PRESIDENT': '总裁'
};

const form = ref<any>({
  id: null,
  username: '',
  password: '',
  first_name: '',
  last_name: '',
  email: '',
  is_staff: false,
  is_superuser: false,
  is_active: true,
  profile_write: {
    department_link: null,
    job_category: '',
    job_title: null,
    job_rank: '',
    job_rank_level: 'NORMAL',
    report_to: null,
    job_position: '', // Keep for compatibility if needed
  }
});

const filteredJobTitles = computed(() => {
  if (!form.value.profile_write.job_category) return [];
  return jobTitles.value.filter(t => t.category === form.value.profile_write.job_category);
});

const showRankLevel = computed(() => {
  const r = form.value.profile_write.job_rank;
  // President/VP ranks usually don't have levels
  return !['PRESIDENT', 'VP', 'SVP'].includes(r);
});

const isAssistant = computed(() => {
  const cat = form.value.profile_write.job_category;
  const rank = form.value.profile_write.job_rank;
  // 增加对 SVP (助理总裁) 的支持
  return cat === 'ASSISTANT' || rank === 'ASSISTANT' || rank === 'SVP';
});

watch(isAssistant, (val) => {
  if (!val) assistantProxyEnabled.value = false;
});

const canSkipReportTo = computed(() => {
  // Logic: Management category with Rank = President/VP/SVP or SysAdmin
  const isMgmtHigh = form.value.profile_write.job_category === 'MANAGEMENT' && 
                     ['PRESIDENT', 'VP', 'SVP'].includes(form.value.profile_write.job_rank);
  const isSysAdmin = form.value.profile_write.job_category === 'SYSADMIN';
  const isSuper = form.value.is_superuser;
  return isMgmtHigh || isSysAdmin || isSuper;
});

function handleCategoryChange() {
  form.value.profile_write.job_title = null;
}

// Build department tree
function buildDeptTree(list: any[]) {
  const map: Record<number, any> = {};
  const roots: any[] = [];
  list.forEach(item => {
    map[item.id] = { ...item, children: [] };
  });
  list.forEach(item => {
    if (item.parent && map[item.parent]) {
      map[item.parent].children.push(map[item.id]);
    } else {
      roots.push(map[item.id]);
    }
  });
  return roots;
}

async function fetchData(){
  loading.value = true;
  try{
    const params:any = { page: currentPage.value, search: search.value };
    const res = await api.get('admin/users/', { params });
    items.value = res.data.results;
    total.value = res.data.count;
    
    // Load metadata
    const allRes = await api.get('admin/users/', { params: { size: 1000 } });
    allUsers.value = allRes.data.results;
    
    const deptRes = await api.get('departments/', { params: { page_size: 1000 } });
    departmentTree.value = buildDeptTree(deptRes.data.results || deptRes.data);
    
    const jobRes = await api.get('job-titles/', { params: { page_size: 1000 } });
    jobTitles.value = jobRes.data.results || jobRes.data;
    
  }catch(e){
    ElMessage.error('加载数据失败');
  }finally{ loading.value = false; }
}

function handlePageChange(p:number){ currentPage.value = p; fetchData(); }

function handleCreate() {
  dialogVisible.value = true;
  isEdit.value = false;
  form.value = {
    id: null,
    username: '',
    password: '',
    first_name: '',
    last_name: '',
    email: '',
    is_staff: false,
    is_superuser: false,
    is_active: true,
    profile_write: { 
      department_link: null, 
      job_category: '',
      job_title: null,
      job_rank: '',
      job_rank_level: 'NORMAL',
      report_to: null 
    }
  };
}

function handleEdit(row: any) {
  dialogVisible.value = true;
  isEdit.value = true;
  form.value = {
    id: row.id,
    username: row.username,
    first_name: row.first_name,
    last_name: row.last_name,
    email: row.email,
    is_staff: row.is_staff,
    is_superuser: row.is_superuser,
    is_active: row.is_active,
    profile_write: {
       department_link: row.profile?.department_link || null,
       job_category: row.profile?.job_category || '',
       job_title: row.profile?.job_title || null,
       job_rank: row.profile?.job_rank || '',
       job_rank_level: row.profile?.job_rank_level || 'NORMAL',
       report_to: row.profile?.report_to || null
    }
  };
  getAssistantProxy(row.id);
}

async function submitForm(){
  if(!form.value.username) return ElMessage.warning('用户名必填');
  
  if (!canSkipReportTo.value && !form.value.profile_write.report_to) {
    return ElMessage.warning('该岗位必须选择汇报对象');
  }

  submitting.value = true;
  try{
    let targetUserId = form.value.id;
    if(isEdit.value){
      await api.patch(`admin/users/${form.value.id}/`, form.value);
    }else{
      if(!form.value.password) {
        submitting.value = false;
        return ElMessage.warning('初始密码必填');
      }
      const res = await api.post('admin/users/', form.value);
      targetUserId = res.data.id;
    }
    
    // 如果是助理，且勾选了同权，则设置同权
    if (isAssistant.value && assistantProxyEnabled.value) {
      if (targetUserId) {
        // 增加重试逻辑，确保 Profile 已被完全创建和同步
        try {
          await setAssistantProxy(targetUserId, true);
        } catch (err) {
          console.warn('First attempt failed, retrying assistant proxy...', err);
          await new Promise(resolve => setTimeout(resolve, 800)); // 略微延长等待时间
          await setAssistantProxy(targetUserId, true);
        }
      }
    } else if (isEdit.value && targetUserId) {
      await setAssistantProxy(targetUserId, false);
    }
    
    ElMessage.success(isEdit.value ? '更新成功' : '创建成功');
    dialogVisible.value = false;
    fetchData();
  }catch(e: any){
    let msg = '保存失败';
    if (e.response?.data) {
       // ... (Keep existing error handling)
       msg = JSON.stringify(e.response.data);
    }
    ElMessage.error(msg);
  }finally{ submitting.value = false; }
}

// ... (Keep existing toggleStatus, handleDelete, handleResetPwd, getAssistantProxy, setAssistantProxy, refreshLastUserId)
async function toggleStatus(row:any){
  try{
    await api.patch(`admin/users/${row.id}/`, { is_active: row.is_active });
    ElMessage.success('状态已更新');
  }catch(e){ 
    row.is_active = !row.is_active; // revert
    ElMessage.error('更新失败'); 
  }
}

async function handleDelete(row: any) {
  try {
    await api.delete(`admin/users/${row.id}/`);
    ElMessage.success('删除成功');
    fetchData();
  } catch (e) {
    ElMessage.error('删除失败，该用户可能关联了业务数据，无法直接删除');
  }
}

function handleResetPwd(row:any){
  ElMessageBox.prompt('请输入新密码', '重置密码', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputPattern: /.{6,}/,
    inputErrorMessage: '密码长度至少6位'
  }).then(async ({ value }) => {
    try {
       await api.patch(`admin/users/${row.id}/`, { password: value });
       ElMessage.success('密码重置成功');
    } catch (e) {
       ElMessage.error('重置失败');
    }
  }).catch(() => {});
}

async function getAssistantProxy(userId: number){
  try{
    const res = await api.get(`admin/users/${userId}/assistant_proxy/`);
    assistantProxyEnabled.value = !!res.data.enabled;
  }catch(e){
    assistantProxyEnabled.value = false;
  }
}

async function setAssistantProxy(userId: number, enabled: boolean){
  try{
    await api.post(`admin/users/${userId}/assistant_proxy/`, { enabled });
  }catch(e:any){
    const msg = e.response?.data?.error || '助理同权设置失败';
    ElMessage.error(msg);
  }
}

async function refreshLastUserId(): Promise<number>{
  const res = await api.get('admin/users/', { params: { page: 1, size: 1 } });
  const last = res.data.results?.[0];
  return last?.id;
}

onMounted(fetchData);
</script>
