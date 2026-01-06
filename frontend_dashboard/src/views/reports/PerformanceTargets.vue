<template>
  <div class="performance-targets-container p-6 space-y-6 bg-slate-50 min-h-screen">
    <!-- Header Section -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">业绩目标管理</h1>
        <p class="text-slate-500 text-sm mt-1">设置并管理部门及个人的年度、季度、月度业绩指标</p>
      </div>
      <div class="flex gap-3">
        <template v-if="selectedIds.length > 0">
          <el-button type="warning" plain @click="handleBatchEdit">
            <el-icon class="mr-1"><Edit /></el-icon> 批量修改 ({{ selectedIds.length }})
          </el-button>
          <el-button type="danger" plain @click="handleBatchDelete">
            <el-icon class="mr-1"><Delete /></el-icon> 批量删除 ({{ selectedIds.length }})
          </el-button>
        </template>
        <el-button type="primary" @click="handleAdd">
          <el-icon class="mr-1"><Plus /></el-icon> 新增业绩目标
        </el-button>
      </div>
    </div>

    <!-- Filter Card -->
    <el-card shadow="never" class="border-none">
      <div class="flex flex-wrap items-center gap-4">
        <div class="filter-item">
          <span class="text-xs text-slate-400 block mb-1">年份</span>
          <el-select v-model="filters.year" placeholder="年份" style="width: 100px" @change="fetchData">
            <el-option v-for="y in [2024, 2025, 2026]" :key="y" :label="y" :value="y" />
          </el-select>
        </div>
        
        <div class="filter-item">
          <span class="text-xs text-slate-400 block mb-1">展示维度</span>
          <el-select v-model="filters.period" placeholder="全部" style="width: 120px" clearable @change="fetchData">
            <el-option label="年度目标" value="YEAR" />
            <el-option label="季度目标" value="QUARTER" />
            <el-option label="月度目标" value="MONTH" />
          </el-select>
        </div>

        <div class="filter-item">
          <span class="text-xs text-slate-400 block mb-1">部门</span>
          <el-select v-model="filters.department" placeholder="所有部门" style="width: 160px" clearable @change="fetchData">
            <el-option v-for="d in departmentOptions" :key="d.id" :label="d.name" :value="d.id" />
          </el-select>
        </div>

        <div class="filter-item">
          <span class="text-xs text-slate-400 block mb-1">目标对象</span>
          <el-select 
            v-model="filters.user" 
            placeholder="所有人员" 
            style="width: 160px" 
            clearable 
            filterable
            remote
            :remote-method="searchUsersForFilter"
            :loading="userSearchLoading"
            @change="fetchData"
          >
            <el-option v-for="u in filterUserOptions" :key="u.id" :label="u.full_name || u.username" :value="u.id" />
          </el-select>
        </div>

        <div class="filter-item pt-5">
          <el-button type="primary" @click="fetchData">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </div>
      </div>
    </el-card>

    <!-- Data Table Card -->
    <el-card shadow="never" class="border-none overflow-hidden" :body-style="{ padding: '0' }">
      <el-table 
        :data="treeItems" 
        v-loading="loading" 
        style="width: 100%" 
        row-key="id"
        :tree-props="{ children: 'children', hasChildren: 'hasChildren' }"
        @selection-change="handleSelectionChange"
        class="modern-table"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column label="名称" min-width="220">
          <template #default="{row}">
            <div class="flex items-center gap-2">
              <el-icon v-if="row.period === 'YEAR'" color="#409EFF"><Calendar /></el-icon>
              <el-icon v-else-if="row.period === 'QUARTER'" color="#E6A23C"><PieChart /></el-icon>
              <el-icon v-else color="#909399"><Clock /></el-icon>
              <span class="font-medium text-slate-700">{{ formatTitle(row) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="周期" width="100">
          <template #default="{row}">
            <el-tag v-if="row.month" size="small" type="info">{{ row.month }}月</el-tag>
            <el-tag v-else-if="row.quarter" size="small" type="warning">Q{{ row.quarter }}</el-tag>
            <el-tag v-else size="small" type="success">全年</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="department_name" label="部门" width="130" show-overflow-tooltip />
        <el-table-column label="人员" width="120">
          <template #default="{row}">
            <span v-if="row.user" class="text-slate-600">{{ row.user.full_name || row.user.username }}</span>
            <el-tag v-else size="small" effect="plain" type="info">全员</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="新签合同目标" width="160" align="right">
          <template #default="{row}">
            <span class="font-mono text-slate-700">{{ formatCurrency(row.target_contract_amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="回款毛利目标" width="160" align="right">
          <template #default="{row}">
            <span class="font-mono text-slate-700">{{ formatCurrency(row.target_gross_profit) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="确认收入目标" width="160" align="right">
          <template #default="{row}">
            <span class="font-mono text-slate-700">{{ formatCurrency(row.target_revenue) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{row}">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-divider direction="vertical" />
            <el-button link type="primary" @click="handleCopy(row)">复制</el-button>
            <el-divider direction="vertical" />
            <el-button 
              v-if="row.period === 'YEAR' && !row.user" 
              link 
              type="warning" 
              @click="handleSplit(row)"
            >
              拆分
            </el-button>
            <el-divider v-if="row.period === 'YEAR' && !row.user" direction="vertical" />
            <el-popconfirm title="确定删除该目标及其所有子项吗?" @confirm="handleDelete(row)">
              <template #reference>
                <el-button link type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="p-4 flex justify-between items-center bg-slate-50">
        <span class="text-xs text-slate-400 italic">* 季度和年度目标根据月度目标自动汇总</span>
        <el-pagination 
          background 
          layout="total, prev, pager, next" 
          :total="total" 
          :page-size="pageSize"
          v-model:current-page="currentPage"
          @current-change="fetchData"
        />
      </div>
    </el-card>

    <!-- Edit/Create Dialog -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="isEdit ? '编辑业绩目标' : '批量设置业绩目标'" 
      width="1000px" 
      top="5vh"
      class="modern-dialog"
    >
      <div class="dialog-content space-y-6">
        <!-- Configuration Row -->
        <div class="grid grid-cols-3 gap-6 bg-slate-50 p-4 rounded-lg border border-slate-100">
          <div>
            <span class="text-xs text-slate-400 block mb-1">目标年份</span>
            <el-select v-model="form.year" placeholder="选择年份" class="w-full" :disabled="isEdit">
              <el-option v-for="y in [2024, 2025, 2026]" :key="y" :label="y" :value="y" />
            </el-select>
          </div>
          <div>
            <span class="text-xs text-slate-400 block mb-1">所属部门</span>
            <el-select v-model="form.department" placeholder="选择部门" class="w-full" :disabled="isEdit">
              <el-option v-for="d in departmentOptions" :key="d.id" :label="d.name" :value="d.id" />
            </el-select>
          </div>
          <div>
            <span class="text-xs text-slate-400 block mb-1">目标对象 (留空为部门整体目标)</span>
            <el-select 
              v-model="form.user" 
              filterable 
              remote 
              clearable
              placeholder="搜索个人" 
              :remote-method="searchUsers"
              :loading="userSearchLoading"
              class="w-full"
              :disabled="isEdit">
              <el-option v-for="item in userOptions" :key="item.id" :label="item.full_name || item.username" :value="item.id">
                <span>{{ item.full_name || item.username }}</span>
                <span class="text-xs text-slate-400 ml-2">{{ item.email }}</span>
              </el-option>
            </el-select>
          </div>
        </div>

        <!-- Quick Tools -->
        <div class="bg-slate-50 p-4 rounded-lg border border-slate-200 mb-6">
          <div class="flex items-center justify-between mb-3">
            <span class="text-sm font-bold text-slate-700 flex items-center">
              <el-icon class="mr-1"><MagicStick /></el-icon>数据快速同步工具
            </span>
            <div class="flex gap-2">
              <el-button-group size="small">
                <el-button @click="quickSelectMonths('ALL')">全选</el-button>
                <el-button @click="quickSelectMonths('Q1')">Q1</el-button>
                <el-button @click="quickSelectMonths('Q2')">Q2</el-button>
                <el-button @click="quickSelectMonths('Q3')">Q3</el-button>
                <el-button @click="quickSelectMonths('Q4')">Q4</el-button>
              </el-button-group>
              <el-button size="small" link @click="copyTool.targetMonths = []">清空</el-button>
            </div>
          </div>
          
          <div class="flex items-center gap-4">
            <div class="flex-1 flex items-center gap-2">
              <span class="text-xs text-slate-500 whitespace-nowrap">将</span>
              <el-select v-model="copyTool.sourceMonth" placeholder="源月份" style="width: 120px">
                <el-option v-for="m in 12" :key="m" :label="`${m}月数据`" :value="m" />
              </el-select>
              <span class="text-xs text-slate-500 whitespace-nowrap">同步至</span>
              <el-select 
                v-model="copyTool.targetMonths" 
                multiple 
                collapse-tags 
                placeholder="目标月份(多选)" 
                class="flex-1"
                :teleported="true"
              >
                <el-option v-for="m in 12" :key="m" :label="`${m}月`" :value="m" :disabled="m === copyTool.sourceMonth" />
              </el-select>
            </div>
            <el-button type="primary" @click="applyCopyToMonths" :disabled="!copyTool.sourceMonth || copyTool.targetMonths.length === 0" icon="CopyDocument">
              执行同步
            </el-button>
          </div>
        </div>

        <!-- Monthly Table -->
        <div class="border rounded-lg overflow-hidden">
          <el-table :data="monthlyTargets" height="400" stripe border v-loading="dialogLoading">
            <el-table-column label="月份" width="100" align="center">
              <template #default="{row}">
                <span class="font-bold text-slate-700">{{ row.month }}月</span>
              </template>
            </el-table-column>
            <el-table-column label="新签合同目标">
              <template #default="{row}">
                <el-input-number v-model="row.target_contract_amount" :min="0" :step="10000" class="w-full" :controls="false" />
              </template>
            </el-table-column>
            <el-table-column label="回款毛利目标">
              <template #default="{row}">
                <el-input-number v-model="row.target_gross_profit" :min="0" :step="10000" class="w-full" :controls="false" />
              </template>
            </el-table-column>
            <el-table-column label="确认收入目标">
              <template #default="{row}">
                <el-input-number v-model="row.target_revenue" :min="0" :step="10000" class="w-full" :controls="false" />
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitBulkForm" :loading="submitting">保存全部目标</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Batch Edit Dialog -->
    <el-dialog 
      v-model="batchEditDialogVisible" 
      title="批量修改业绩目标值" 
      width="500px" 
      class="modern-dialog"
    >
      <div class="space-y-4">
        <el-alert 
          title="批量修改仅对选中的「月度目标」生效。季度和年度目标将根据修改后的月度数据自动汇总。" 
          type="info" 
          show-icon 
          :closable="false" 
        />
        
        <div>
          <span class="text-xs text-slate-400 block mb-1">新签合同目标</span>
          <el-input-number v-model="batchEditForm.target_contract_amount" :min="0" :step="10000" class="w-full" placeholder="输入统一的数值" />
        </div>
        <div>
          <span class="text-xs text-slate-400 block mb-1">回款毛利目标</span>
          <el-input-number v-model="batchEditForm.target_gross_profit" :min="0" :step="10000" class="w-full" placeholder="输入统一的数值" />
        </div>
        <div>
          <span class="text-xs text-slate-400 block mb-1">确认收入目标</span>
          <el-input-number v-model="batchEditForm.target_revenue" :min="0" :step="10000" class="w-full" placeholder="输入统一的数值" />
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="batchEditDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitBatchEdit" :loading="submitting">确认修改</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Target Splitting Dialog -->
    <el-dialog 
      v-model="splittingDialogVisible" 
      title="年度目标下发与拆分" 
      width="1100px" 
      top="5vh"
      class="modern-dialog"
    >
      <div v-loading="splitLoading" class="space-y-6">
        <!-- Dept Summary -->
        <div class="bg-slate-800 text-white p-6 rounded-xl shadow-lg flex justify-between items-center">
          <div>
            <div class="text-slate-400 text-xs mb-1 uppercase tracking-wider font-bold">正在为部门设定目标</div>
            <div class="text-2xl font-black">{{ currentSplitTarget?.department_name }} ({{ currentSplitTarget?.year }}年度)</div>
          </div>
          <div class="flex gap-8 text-right">
            <div>
              <div class="text-slate-400 text-xs mb-1">合同总额</div>
              <div class="text-xl font-mono text-blue-400">{{ formatCurrency(currentSplitTarget?.target_contract_amount) }}</div>
            </div>
            <div>
              <div class="text-slate-400 text-xs mb-1">毛利总额</div>
              <div class="text-xl font-mono text-emerald-400">{{ formatCurrency(currentSplitTarget?.target_gross_profit) }}</div>
            </div>
          </div>
        </div>

        <el-alert 
          title="拆分逻辑说明：此处设置的是各成员的「年度总目标」。系统将根据设置的总额，平均拆分到该成员全年的 12 个月中。如果需要精细调整各月，请在保存后针对个人目标点击“编辑”。" 
          type="warning" 
          show-icon 
          :closable="false" 
        />

        <div class="border rounded-xl overflow-hidden shadow-sm">
          <el-table :data="teamMembers" max-height="450" stripe>
            <el-table-column label="成员姓名" min-width="120">
              <template #default="{row}">
                <div class="font-bold text-slate-700">{{ row.full_name || row.username }}</div>
                <div class="text-xs text-slate-400">@{{ row.username }}</div>
              </template>
            </el-table-column>
            <el-table-column label="年度合同目标">
              <template #default="{row}">
                <el-input-number v-model="row.year_contract" :min="0" :step="100000" class="w-full" :controls="false" placeholder="0.00" />
              </template>
            </el-table-column>
            <el-table-column label="年度毛利目标">
              <template #default="{row}">
                <el-input-number v-model="row.year_profit" :min="0" :step="100000" class="w-full" :controls="false" placeholder="0.00" />
              </template>
            </el-table-column>
            <el-table-column label="年度收入目标">
              <template #default="{row}">
                <el-input-number v-model="row.year_revenue" :min="0" :step="100000" class="w-full" :controls="false" placeholder="0.00" />
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="flex justify-end items-center gap-6 p-4 bg-slate-50 rounded-lg">
          <div class="text-sm text-slate-500">
            已分配总额：
            <span class="font-mono text-blue-600 font-bold ml-2">合同 {{ formatCurrency(totalAllocated.contract) }}</span>
            <span class="mx-2">|</span>
            <span class="font-mono text-emerald-600 font-bold">毛利 {{ formatCurrency(totalAllocated.profit) }}</span>
          </div>
          <div v-if="allocationStatus.warning" class="text-red-500 text-sm flex items-center gap-1">
            <el-icon><Warning /></el-icon> {{ allocationStatus.message }}
          </div>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="splittingDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitSplitForm" :loading="submitting" :disabled="allocationStatus.warning">确认下发</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from 'vue';
import { Plus, Edit, Delete, Calendar, PieChart, Clock, CopyDocument, Warning, MagicStick } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import api from '../../api';

const loading = ref(false);
const submitting = ref(false);
const items = ref<any[]>([]);
const departmentOptions = ref<any[]>([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(100); 
const selectedIds = ref<number[]>([]);
const filters = reactive({
  year: 2026, 
  period: '',
  department: '',
  user: null as number | null,
  target_type: ''
});

const filterUserOptions = ref<any[]>([]);

const resetFilters = () => {
  filters.year = 2026;
  filters.period = '';
  filters.department = '';
  filters.user = null;
  filters.target_type = '';
  fetchData();
};

const searchUsersForFilter = async (query: string) => {
  if (query) {
    userSearchLoading.value = true;
    try {
      const res = await api.get('admin/users/', { params: { search: query } });
      filterUserOptions.value = res.data.results || res.data;
    } catch (e) {
      console.error(e);
    } finally {
      userSearchLoading.value = false;
    }
  } else {
    filterUserOptions.value = [];
  }
};

// Copy tool state
const copyTool = reactive({
  sourceMonth: 1,
  targetMonths: [] as number[]
});

const handleSelectionChange = (selection: any[]) => {
    selectedIds.value = selection.map(item => item.id);
};

const handleBatchDelete = async () => {
    if (selectedIds.value.length === 0) return;
    
    try {
        await ElMessageBox.confirm(`确定要批量删除选中的 ${selectedIds.value.length} 项业绩目标吗？`, '批量删除确认', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
        });
        
        loading.value = true;
        await api.post('performance-targets/bulk_delete/', { ids: selectedIds.value });
        ElMessage.success('批量删除成功');
        selectedIds.value = [];
        fetchData();
    } catch (e) {
        if (e !== 'cancel') {
            ElMessage.error('批量删除失败');
        }
    } finally {
        loading.value = false;
    }
};

const applyCopyToMonths = () => {
    if (copyTool.targetMonths.length === 0) {
        ElMessage.warning('请选择目标月份');
        return;
    }
    
    const sourceData = monthlyTargets.value.find(m => m.month === copyTool.sourceMonth);
    if (!sourceData) return;
    
    monthlyTargets.value.forEach(m => {
        if (copyTool.targetMonths.includes(m.month)) {
            m.target_contract_amount = sourceData.target_contract_amount;
            m.target_gross_profit = sourceData.target_gross_profit;
            m.target_revenue = sourceData.target_revenue;
        }
    });
    
    ElMessage.success(`已将 ${copyTool.sourceMonth} 月数据同步至选定月份`);
};

const quickSelectMonths = (type: 'ALL' | 'Q1' | 'Q2' | 'Q3' | 'Q4') => {
    if (type === 'ALL') {
        copyTool.targetMonths = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
    } else if (type === 'Q1') {
        copyTool.targetMonths = [1, 2, 3];
    } else if (type === 'Q2') {
        copyTool.targetMonths = [4, 5, 6];
    } else if (type === 'Q3') {
        copyTool.targetMonths = [7, 8, 9];
    } else if (type === 'Q4') {
        copyTool.targetMonths = [10, 11, 12];
    }
};

const treeItems = computed(() => {
  const tree: any[] = [];
  const items_list = items.value;
  
  // 1. 先按 维度（部门+人员+年份+类型）分组
  const dimensionGroups: Record<string, any[]> = {};
  
  items_list.forEach(item => {
    // 关键修复：确保维度识别唯一，部门ID和人员ID需要严格区分
    const deptId = item.department || 'no_dept';
    const userId = item.user?.id || 'no_user';
    const key = `${deptId}-${userId}-${item.year}-${item.target_type}`;
    if (!dimensionGroups[key]) dimensionGroups[key] = [];
    dimensionGroups[key].push(item);
  });
  
  // 2. 对每个维度组构建树形
  Object.values(dimensionGroups).forEach(groupItems => {
    // 找到该维度的年度目标作为根
    let yearTarget = groupItems.find(i => i.period === 'YEAR');
    
    // 如果没有年度目标，创建一个虚拟年度根，或者直接以季度为根
    const quarters = groupItems.filter(i => i.period === 'QUARTER').sort((a, b) => a.quarter - b.quarter);
    const months = groupItems.filter(i => i.period === 'MONTH').sort((a, b) => a.month - b.month);

    if (yearTarget) {
      const row = { ...yearTarget, children: [] as any[] };
      
      // 找季度目标或创建虚拟季度
      for (let q = 1; q <= 4; q++) {
        let qRow = quarters.find(i => i.quarter === q);
        const qMonths = months.filter(m => {
          const calcQ = Math.floor((m.month - 1) / 3) + 1;
          return calcQ === q;
        });

        // 只要是年度目标的子节点，我们就展示 4 个季度，即使没有数据
        const quarterNode = qRow ? { ...qRow, children: qMonths } : {
          id: `v-q-${q}-${yearTarget.id}`,
          period: 'QUARTER',
          quarter: q,
          year: yearTarget.year,
          department: yearTarget.department,
          department_name: yearTarget.department_name,
          user: yearTarget.user,
          target_type: yearTarget.target_type,
          target_contract_amount: qMonths.reduce((sum, m) => sum + parseFloat(m.target_contract_amount || 0), 0),
          target_gross_profit: qMonths.reduce((sum, m) => sum + parseFloat(m.target_gross_profit || 0), 0),
          target_revenue: qMonths.reduce((sum, m) => sum + parseFloat(m.target_revenue || 0), 0),
          is_virtual: !qRow,
          children: qMonths
        };
        row.children.push(quarterNode);
      }
      tree.push(row);
    } else if (quarters.length > 0) {
      // 没有年度目标，以季度为顶层
      quarters.forEach(q => {
        const qMonths = months.filter(m => Math.floor((m.month - 1) / 3) + 1 === q.quarter);
        tree.push({ ...q, children: qMonths });
      });
      // 处理不在这些季度里的月份
      const monthsInQuarters = new Set(quarters.flatMap(q => months.filter(m => Math.floor((m.month - 1) / 3) + 1 === q.quarter).map(m => m.id)));
      months.filter(m => !monthsInQuarters.has(m.id)).forEach(m => tree.push(m));
    } else {
      // 只有月度目标
      tree.push(...months);
    }
  });
  
  return tree.sort((a, b) => {
    if (a.year !== b.year) return b.year - a.year;
    const deptA = a.department_name || '';
    const deptB = b.department_name || '';
    if (deptA !== deptB) return deptA.localeCompare(deptB);
    const userA = a.user?.username || '';
    const userB = b.user?.username || '';
    return userA.localeCompare(userB);
  });
});

const handleCopy = (row: any) => {
  ElMessageBox.prompt('请输入目标年份', '复制业绩目标', {
    confirmButtonText: '开始复制',
    cancelButtonText: '取消',
    inputValue: (row.year + 1).toString(),
    inputPattern: /^\d{4}$/,
    inputErrorMessage: '请输入有效的4位年份'
  }).then(async ({ value }) => {
    try {
      submitting.value = true;
      await api.post('performance-targets/copy_year_targets/', {
        from_year: row.year,
        to_year: parseInt(value),
        department: row.department,
        user_id: row.user?.id
      });
      ElMessage.success(`成功复制 ${row.year} 目标至 ${value} 年`);
      fetchData();
    } catch (e: any) {
      ElMessage.error(e.response?.data?.error || '复制失败');
    } finally {
      submitting.value = false;
    }
  }).catch(() => {});
};

const isEdit = ref(false);
const batchEditDialogVisible = ref(false);
const batchEditForm = reactive({
    target_contract_amount: null as number | null,
    target_gross_profit: null as number | null,
    target_revenue: null as number | null
});

const handleBatchEdit = () => {
    batchEditForm.target_contract_amount = null;
    batchEditForm.target_gross_profit = null;
    batchEditForm.target_revenue = null;
    batchEditDialogVisible.value = true;
};

const submitBatchEdit = async () => {
    if (batchEditForm.target_contract_amount === null && 
        batchEditForm.target_gross_profit === null && 
        batchEditForm.target_revenue === null) {
        ElMessage.warning('请至少输入一项修改值');
        return;
    }

    submitting.value = true;
    try {
        await api.post('performance-targets/bulk_batch_update/', {
            ids: selectedIds.value,
            ...batchEditForm
        });
        ElMessage.success('批量修改成功');
        batchEditDialogVisible.value = false;
        selectedIds.value = [];
        fetchData();
    } catch (e) {
        ElMessage.error('批量修改失败');
    } finally {
        submitting.value = false;
    }
};

const dialogLoading = ref(false);
const dialogVisible = ref(false);
const form = reactive({
  year: 2026,
  department: null as number | null,
  user: null as number | null,
  target_type: 'DEPARTMENT' as 'DEPARTMENT' | 'INDIVIDUAL'
});

// Monthly Targets Table Data
const monthlyTargets = ref<any[]>([]);

watch(() => form.user, (val) => {
    form.target_type = val ? 'INDIVIDUAL' : 'DEPARTMENT';
});

const generateMonthlyRows = async (isNew = false) => {
    dialogLoading.value = true;
    try {
        // 尝试从后端获取该维度的所有月度目标，确保数据完整性
        const params: any = {
            year: form.year,
            period: 'MONTH',
            page_size: 100
        };
        if (form.department) params.department = form.department;
        if (form.user) params.user = form.user;
        // 如果是个人目标，明确 target_type
        params.target_type = form.user ? 'INDIVIDUAL' : 'DEPARTMENT';

        const res = await api.get('performance-targets/', { params });
        const existingData = res.data.results || res.data;

        monthlyTargets.value = Array.from({length: 12}, (_, i) => {
            const m = i + 1;
            const exist = existingData.find((e: any) => e.month === m);
            return {
                month: m,
                target_contract_amount: exist ? parseFloat(exist.target_contract_amount) : 0,
                target_gross_profit: exist ? parseFloat(exist.target_gross_profit) : 0,
                target_revenue: exist ? parseFloat(exist.target_revenue) : 0
            };
        });
    } catch (e) {
        ElMessage.error('获取月度数据失败');
    } finally {
        dialogLoading.value = false;
    }
};

const handleAdd = () => {
    isEdit.value = false;
    form.year = filters.year; 
    form.department = filters.department || (departmentOptions.value.length > 0 ? departmentOptions.value[0].id : null);
    form.user = filters.user || null;
    form.target_type = form.user ? 'INDIVIDUAL' : 'DEPARTMENT';
    dialogVisible.value = true;
    generateMonthlyRows(true);
};

const splittingDialogVisible = ref(false);
const splitLoading = ref(false);
const currentSplitTarget = ref<any>(null);
const teamMembers = ref<any[]>([]);

const totalAllocated = computed(() => {
    return teamMembers.value.reduce((acc, m) => {
        acc.contract += (m.year_contract || 0);
        acc.profit += (m.year_profit || 0);
        acc.revenue += (m.year_revenue || 0);
        return acc;
    }, { contract: 0, profit: 0, revenue: 0 });
});

const allocationStatus = computed(() => {
    if (!currentSplitTarget.value) return { warning: false, message: '' };
    
    const overContract = totalAllocated.value.contract > currentSplitTarget.value.target_contract_amount;
    const overProfit = totalAllocated.value.profit > currentSplitTarget.value.target_gross_profit;
    
    if (overContract || overProfit) {
        return { 
            warning: true, 
            message: `已分配额度超过了部门总额度 (${overContract ? '合同' : ''}${overContract && overProfit ? '和' : ''}${overProfit ? '毛利' : ''})` 
        };
    }
    return { warning: false, message: '' };
});

const handleSplit = async (row: any) => {
    currentSplitTarget.value = row;
    splittingDialogVisible.value = true;
    splitLoading.value = true;
    try {
        // 1. 获取部门成员
        const deptId = row.department;
        const resMembers = await api.get(`departments/${deptId}/members/`);
        const members = resMembers.data;
        
        // 2. 获取这些成员已有的年度目标
        const resExisting = await api.get('performance-targets/', {
            params: {
                year: row.year,
                period: 'YEAR',
                department: deptId,
                target_type: 'INDIVIDUAL'
            }
        });
        const existingTargets = resExisting.data.results || resExisting.data;
        
        teamMembers.value = members.map((m: any) => {
            const target = existingTargets.find((t: any) => t.user?.id === m.id);
            return {
                id: m.id,
                username: m.username,
                full_name: m.full_name,
                year_contract: target ? parseFloat(target.target_contract_amount) : 0,
                year_profit: target ? parseFloat(target.target_gross_profit) : 0,
                year_revenue: target ? parseFloat(target.target_revenue) : 0
            };
        });
    } catch (e) {
        ElMessage.error('获取成员信息失败');
    } finally {
        splitLoading.value = false;
    }
};

const submitSplitForm = async () => {
    submitting.value = true;
    try {
        // 确保部门 ID 存在
        const deptId = currentSplitTarget.value.department_id || currentSplitTarget.value.department;
        if (!deptId) throw new Error('部门信息缺失');

        // 为每个成员提交批量更新
        const promises = teamMembers.value.map(m => {
            const monthlyContract = (m.year_contract || 0) / 12;
            const monthlyProfit = (m.year_profit || 0) / 12;
            const monthlyRevenue = (m.year_revenue || 0) / 12;
            
            const targets = Array.from({length: 12}, (_, i) => ({
                month: i + 1,
                target_contract_amount: monthlyContract,
                target_gross_profit: monthlyProfit,
                target_revenue: monthlyRevenue
            }));
            
            return api.post('performance-targets/bulk_update_targets/', {
                year: currentSplitTarget.value.year,
                department: deptId,
                user_id: m.id,
                target_type: 'INDIVIDUAL',
                targets: targets
            });
        });
        
        await Promise.all(promises);
        ElMessage.success('目标拆分并下发成功');
        splittingDialogVisible.value = false;
        fetchData();
    } catch (e: any) {
        console.error('Split error:', e);
        const errorMsg = e.response?.data?.error || e.message || '拆分下发失败';
        ElMessage.error(errorMsg);
    } finally {
        submitting.value = false;
    }
};

const handleEdit = (row: any) => {
    isEdit.value = true;
    form.year = row.year;
    form.department = row.department;
    form.target_type = row.target_type;
    
    // 强制逻辑：部门目标不关联用户
    if (form.target_type === 'DEPARTMENT') {
        form.user = null;
    } else {
        form.user = (row.user && typeof row.user === 'object') ? row.user.id : (row.user || null);
        if (row.user) {
            userOptions.value = [row.user];
        }
    }
    
    dialogVisible.value = true;
    generateMonthlyRows();
};

const handleTypeChange = () => {
    if (form.target_type === 'DEPARTMENT') {
        form.user = null;
    }
    generateMonthlyRows();
};

const submitBulkForm = async () => {
    submitting.value = true;
    try {
        await api.post('performance-targets/bulk_update_targets/', {
            year: form.year,
            department: form.department,
            user_id: form.user,
            target_type: form.target_type, // 明确发送目标类型，防止误判
            targets: monthlyTargets.value
        });
        ElMessage.success('业绩目标已更新');
        dialogVisible.value = false;
        fetchData();
    } catch (e: any) {
        ElMessage.error(e.response?.data?.error || '保存失败');
    } finally {
        submitting.value = false;
    }
};

const userSearchLoading = ref(false);
const userOptions = ref<any[]>([]);

// Mappings
const departmentMap: Record<string, string> = {
  'SALES': '销售部',
  'GAME': '春秋GAME',
  'GROUP_MARKETING': '集团市场部',
  'LAB': '实验室',
  'RND': '研发中心'
};

const formatDepartment = (code: string) => departmentMap[code] || code;
const formatCurrency = (val: number) => Number(val || 0).toLocaleString('zh-CN', { minimumFractionDigits: 0 });
const formatTitle = (row: any) => {
  const dept = row.department_name || formatDepartment(row.department);
  const user = row.user ? ` - ${row.user.full_name || row.user.username}` : '';
  let time = `${row.year}年`;
  if (row.month) time += ` ${row.month}月`;
  else if (row.quarter) time += ` Q${row.quarter}`;
  else time += ' 全年';
  return `${dept}${user} ${time} 业绩目标`;
};

const searchUsers = async (query: string) => {
  if (query) {
    userSearchLoading.value = true;
    try {
      const res = await api.get('admin/users/', { params: { search: query } });
      userOptions.value = res.data.results || res.data;
    } catch (e) {
      console.error(e);
    } finally {
      userSearchLoading.value = false;
    }
  } else {
    userOptions.value = [];
  }
};

const fetchData = async () => {
  loading.value = true;
  try {
    const params: any = { 
        page: currentPage.value, 
        page_size: 1000, 
        year: filters.year 
    };
    if (filters.department) params.department = filters.department;
    if (filters.user) params.user = filters.user;
    if (filters.period) params.period = filters.period;
    if (filters.target_type) params.target_type = filters.target_type;
    
    const res = await api.get('performance-targets/', { params });
    items.value = res.data.results || res.data;
    total.value = res.data.count || items.value.length;
  } catch (e) {
    ElMessage.error('获取数据失败');
  } finally {
    loading.value = false;
  }
};

const fetchDepartments = async () => {
  try {
    const res = await api.get('departments/');
    departmentOptions.value = res.data.results || res.data;
  } catch (e) {
    console.error('获取部门列表失败', e);
  }
};

const handleDelete = async (row: any) => {
    try {
        await api.delete(`performance-targets/${row.id}/`);
        ElMessage.success('删除成功');
        fetchData();
    } catch (e) {
        ElMessage.error('删除失败');
    }
};

onMounted(() => {
  fetchDepartments();
  fetchData();
});
</script>

<style scoped>
.modern-dialog :deep(.el-dialog__body) {
  padding-top: 10px;
}

.sync-month-popper {
  max-height: 300px;
  overflow-y: auto;
}

:deep(.el-table__placeholder) {
  display: none;
}

:deep(.el-table__indent) {
  padding-left: 10px !important;
}
</style>
