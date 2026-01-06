<template>
  <div class="h-full flex flex-col bg-slate-50">
    <header class="bg-white border-b border-slate-200 px-8 py-6 flex justify-between items-center shrink-0">
      <div class="flex flex-col gap-1">
        <h1 class="text-2xl font-bold text-slate-800 tracking-tight">岗位名称配置</h1>
        <div class="text-sm text-slate-500">管理系统中的岗位属性与标准名称字典</div>
      </div>
      <div class="flex gap-2">
        <el-button type="warning" plain icon="Refresh" @click="handleInitDefaults" :loading="loading">恢复系统默认岗位</el-button>
        <el-button type="primary" @click="handleCreate">
          <el-icon class="mr-1"><Plus /></el-icon> 新增岗位名称
        </el-button>
      </div>
    </header>

    <main class="flex-1 p-8 overflow-auto">
      <div class="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
        <div class="p-4 border-b border-slate-50 flex justify-between items-center">
           <div class="flex gap-2">
             <el-input v-model="search" placeholder="搜索岗位名称..." style="width: 240px" clearable @clear="fetchData" @keyup.enter="fetchData">
                <template #prefix><el-icon><Search /></el-icon></template>
             </el-input>
             <el-select v-model="categoryFilter" placeholder="按属性筛选" clearable @change="fetchData" style="width: 160px">
                <el-option v-for="(label, key) in categoryMap" :key="key" :label="label" :value="key" />
             </el-select>
             <el-button @click="fetchData">搜索</el-button>
           </div>
        </div>

        <el-table :data="items" v-loading="loading" style="width: 100%" :header-cell-style="{background:'#f8fafc', color:'#475569', fontWeight:'600'}">
          <el-table-column prop="name" label="岗位名称" min-width="150" sortable />
          <el-table-column prop="category" label="岗位属性" width="150" sortable>
            <template #default="{row}">
               <el-tag :type="getCategoryTagType(row.category)" effect="light">{{ row.category_display }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{row}">
              <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
              <el-popconfirm title="确定删除该岗位名称？" @confirm="handleDelete(row)">
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
    <el-dialog v-model="dialogVisible" :title="isEdit?'编辑岗位':'新增岗位'" width="500px">
      <el-form :model="form" label-width="100px" :rules="rules" ref="formRef">
        <el-form-item label="岗位属性" prop="category">
          <el-select v-model="form.category" placeholder="选择岗位属性" style="width: 100%">
             <el-option v-for="(label, key) in categoryMap" :key="key" :label="label" :value="key" />
          </el-select>
        </el-form-item>
        <el-form-item label="岗位名称" prop="name">
          <el-input v-model="form.name" placeholder="例如：高级产品经理" />
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
import { ref, onMounted, reactive } from 'vue';
import api from '../../api';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, Search, Refresh } from '@element-plus/icons-vue';

const items = ref([]);
const loading = ref(false);
const restoring = ref(false);
const dialogVisible = ref(false);
const submitting = ref(false);
const isEdit = ref(false);
const search = ref('');
const categoryFilter = ref('');
const currentPage = ref(1);
const pageSize = ref(20);
const total = ref(0);
const formRef = ref();

const categoryMap = {
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

const form = reactive({
  id: null,
  name: '',
  category: ''
});

const rules = {
  category: [{ required: true, message: '请选择岗位属性', trigger: 'change' }],
  name: [{ required: true, message: '请输入岗位名称', trigger: 'blur' }]
};

function getCategoryTagType(cat: string) {
  const map: Record<string, string> = {
    'MANAGEMENT': 'danger',
    'RND': 'primary',
    'SALES': 'success',
    'RESEARCHER': 'info',
    'ASSISTANT': 'warning'
  };
  return map[cat] || '';
}

async function fetchData(){
  loading.value = true;
  try{
    const params:any = { page: currentPage.value, search: search.value, page_size: pageSize.value };
    if (categoryFilter.value) params.category = categoryFilter.value;
    
    const res = await api.get('job-titles/', { params });
    // 兼容分页与不分页的情况
    items.value = res.data.results || res.data;
    total.value = res.data.count || items.value.length;
  }catch(e){
    ElMessage.error('加载数据失败');
  }finally{ loading.value = false; }
}

function handlePageChange(p:number){ currentPage.value = p; fetchData(); }

function handleCreate() {
  dialogVisible.value = true;
  isEdit.value = false;
  form.id = null;
  form.name = '';
  form.category = '';
}

function handleEdit(row: any) {
  dialogVisible.value = true;
  isEdit.value = true;
  form.id = row.id;
  form.name = row.name;
  form.category = row.category;
}

async function handleInitDefaults() {
  try {
    await ElMessageBox.confirm('此操作将恢复系统预设的 24 个标准岗位，是否继续？', '提示', {
      type: 'warning',
      confirmButtonText: '立即恢复',
      cancelButtonText: '取消'
    });
    loading.value = true;
    const res = await api.post('job-titles/init_defaults/');
    ElMessage.success(res.data.message || '恢复成功');
    fetchData();
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error(e.response?.data?.error || '恢复失败');
    }
  } finally {
    loading.value = false;
  }
}

async function handleDelete(row: any) {
  try {
    await api.delete(`job-titles/${row.id}/`);
    ElMessage.success('删除成功');
    fetchData();
  } catch (e) {
    ElMessage.error('删除失败，可能已被用户引用');
  }
}

async function handleRestoreDefaults() {
  try {
    await ElMessageBox.confirm('确定要恢复系统默认岗位吗？已存在的岗位不会被删除。', '提示', { type: 'warning' });
    restoring.value = true;
    const res = await api.post('job-titles/init_defaults/');
    ElMessage.success(res.data.message);
    fetchData();
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('恢复失败');
    }
  } finally {
    restoring.value = false;
  }
}

async function submitForm() {
  if (!formRef.value) return;
  await formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      submitting.value = true;
      try {
        if (isEdit.value) {
          await api.patch(`job-titles/${form.id}/`, form);
          ElMessage.success('更新成功');
        } else {
          await api.post('job-titles/', form);
          ElMessage.success('创建成功');
        }
        dialogVisible.value = false;
        fetchData();
      } catch (e: any) {
        const msg = e.response?.data?.name ? '岗位名称在该属性下已存在' : '保存失败';
        ElMessage.error(msg);
      } finally {
        submitting.value = false;
      }
    }
  });
}

onMounted(fetchData);
</script>