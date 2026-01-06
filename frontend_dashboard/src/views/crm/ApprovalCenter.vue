<template>
  <div class="h-screen flex flex-col bg-slate-50 overflow-hidden">
    <main class="flex-1 p-8 overflow-auto">
      <div class="mb-6 flex justify-between items-center">
        <h1 class="text-2xl font-bold text-slate-800 tracking-tight">审批中心</h1>
        <div class="flex items-center gap-3">
          <el-radio-group v-model="viewMode" size="large" @change="handleViewModeChange">
            <el-radio-button label="all">全部</el-radio-button>
            <el-radio-button label="pending">待我审批</el-radio-button>
            <el-radio-button label="handled">我已处理</el-radio-button>
            <el-radio-button label="my_request">我发起的</el-radio-button>
          </el-radio-group>
          <el-button :icon="Refresh" circle @click="fetchData" :loading="loading" class="ml-2" />
        </div>
      </div>

      <div class="bg-white rounded-xl shadow-sm border border-slate-100 p-6 transition-all hover:shadow-md">
        <div class="mb-6 flex items-center justify-between">
           <div class="flex gap-2">
             <el-button type="success" plain :disabled="!selectedIds.length" @click="bulkApprove">
               <el-icon class="mr-1"><Check /></el-icon> 批量通过
             </el-button>
             <el-button type="danger" plain :disabled="!selectedIds.length" @click="bulkReject">
               <el-icon class="mr-1"><Close /></el-icon> 批量驳回
             </el-button>
           </div>
           <div class="flex gap-2 items-center">
             <span class="text-sm text-slate-500">状态筛选：</span>
             <el-select v-model="statusFilter" placeholder="全部状态" style="width: 140px" clearable @change="fetchData">
                <el-option label="待确认" value="PENDING" />
                <el-option label="已通过" value="APPROVED" />
                <el-option label="已驳回" value="REJECTED" />
             </el-select>
           </div>
        </div>

        <el-table :data="items" v-loading="loading" @selection-change="onApprovalSelection" 
                  style="width:100%" :header-cell-style="{background:'#f8fafc', color:'#475569', fontWeight:'600'}"
                  row-class-name="hover:bg-slate-50 transition-colors">
            <el-table-column type="selection" width="48" />
            <!-- ID对于业务人员无意义，隐藏或仅作为tooltip -->
            <el-table-column prop="model_name" label="业务类型" width="120">
              <template #default="{row}">
                <el-tag effect="plain" size="small">{{ row.model_name || row.model_key || '未知' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="object_summary" label="审批事项" min-width="240">
              <template #default="{row}">
                <div class="font-medium text-slate-800 text-base">{{ row.object_summary }}</div>
                <div class="text-xs text-slate-400 mt-0.5" v-if="row.object_id">编号: {{ row.object_id }}</div>
              </template>
            </el-table-column>
            <el-table-column prop="applicant_name" label="申请人" width="120">
              <template #default="{row}">
                 <span>{{ formatName(row.applicant_name) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="approver_name" label="审批人" width="120">
              <template #default="{row}">
                 <span>{{ formatName(row.approver_name) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
            <template #default="{row}">
              <el-tag v-if="row.status==='PENDING'" type="warning">待确认</el-tag>
              <el-tag v-else-if="row.status==='APPROVED'" type="success">已通过</el-tag>
              <el-tag v-else-if="row.status==='REJECTED'" type="danger">已驳回</el-tag>
              <el-tag v-else type="info">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="reason" label="理由" />
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="scope">{{ new Date(scope.row.created_at).toLocaleString() }}</template>
          </el-table-column>
          <el-table-column label="操作" width="220" fixed="right">
            <template #default="scope">
              <div class="flex items-center gap-2">
                <el-input v-model="opinion[scope.row.id]" placeholder="审批备注" size="small" style="width: 120px" />
                <el-button-group>
                   <el-button size="small" type="success" :icon="Check" circle @click="approve(scope.row)" />
                   <el-button size="small" type="danger" :icon="Close" circle @click="reject(scope.row)" />
                </el-button-group>
              </div>
            </template>
          </el-table-column>
        </el-table>
        <div class="mt-6 flex justify-end">
          <el-pagination background layout="prev, pager, next" :total="total" :page-size="pageSize" @current-change="handlePageChange" />
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../../api';
import { ElMessage } from 'element-plus';
import { Check, Close, Refresh } from '@element-plus/icons-vue';

const items = ref<any[]>([]);
const loading = ref(false);
const statusFilter = ref<string>('');
const viewMode = ref<string>('all'); // all, pending, handled, my_request
const pageSize = ref(20);
const currentPage = ref(1);
const total = ref(0);
const opinion = ref<Record<number, string>>({});
const selectedIds = ref<number[]>([]);

async function fetchData(){
  loading.value = true;
  try{
    const params:any = { page: currentPage.value };
    if (statusFilter.value) params.status = statusFilter.value;
    
    // View Mode Logic (requires backend support or simple filter)
    // Note: Backend currently returns "My Approvals" by default. 
    // We might need to adjust backend filter or just use 'status' for now.
    // For 'my_request', we need backend support or user ID filter.
    // Assuming backend handles basic listing for now.
    
    if (viewMode.value === 'pending') params.status = 'PENDING';
    if (viewMode.value === 'handled') params.status_in = 'APPROVED,REJECTED';
    
    const res = await api.get('approvals/', { params });
    if (res.data.results){
      items.value = res.data.results;
      total.value = res.data.count;
    }else{
      items.value = res.data;
      total.value = res.data.length || 0;
    }
  }catch(e){
    console.error(e); ElMessage.error('获取审批列表失败');
  }finally{ loading.value = false; }
}

function handleViewModeChange(){
  currentPage.value = 1;
  statusFilter.value = ''; // Reset specific status filter when changing mode
  fetchData();
}

function handlePageChange(p:number){ currentPage.value = p; fetchData(); }
function formatName(n:string){
  if (!n) return '-';
  if (n === 'admin') return '管理员';
  if (n.startsWith('manager_')) return '某经理'; // 简单处理mock数据
  if (n.startsWith('employee_')) return '某员工';
  return n;
}
function onApprovalSelection(rows:any[]){ selectedIds.value = rows.map(r => r.id); }

async function approve(row:any){
  try{
    await api.post(`approvals/${row.id}/approve/`, { reason: opinion.value[row.id] || '' });
    row.status = 'APPROVED';
    ElMessage.success('已通过');
    fetchData();
  }catch(e){ console.error(e); ElMessage.error('操作失败'); }
}

async function reject(row:any){
  try{
    await api.post(`approvals/${row.id}/reject/`, { reason: opinion.value[row.id] || '' });
    row.status = 'REJECTED';
    ElMessage.success('已驳回');
    fetchData();
  }catch(e){ console.error(e); ElMessage.error('操作失败'); }
}

async function bulkApprove(){
  try{
    await api.post('approvals/bulk_approve/', { ids: selectedIds.value, reason: '' });
    ElMessage.success('批量通过完成');
    fetchData();
  }catch(e){ console.error(e); ElMessage.error('批量操作失败'); }
}
async function bulkReject(){
  try{
    await api.post('approvals/bulk_reject/', { ids: selectedIds.value, reason: '' });
    ElMessage.success('批量驳回完成');
    fetchData();
  }catch(e){ console.error(e); ElMessage.error('批量操作失败'); }
}
onMounted(fetchData);
// Removed presetPending and presetHandled since they are replaced by viewMode
</script>
