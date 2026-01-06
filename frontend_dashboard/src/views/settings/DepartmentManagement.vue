<template>
  <div class="h-full flex flex-col bg-slate-50">
    <header class="bg-white border-b border-slate-200 px-8 py-6 flex justify-between items-center shrink-0">
      <div class="flex flex-col gap-1">
        <h1 class="text-2xl font-bold text-slate-800 tracking-tight">部门管理</h1>
        <div class="text-sm text-slate-500">管理组织架构、部门属性与负责人</div>
      </div>
      <el-button type="primary" size="large" @click="handleCreate">
        <el-icon class="mr-1"><Plus /></el-icon> 新增部门
      </el-button>
    </header>

    <main class="flex-1 p-8 overflow-auto">
      <div class="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
        <el-table :data="items" row-key="id" v-loading="loading" default-expand-all style="width: 100%" :header-cell-style="{background:'#f8fafc', color:'#475569', fontWeight:'600'}">
          <el-table-column prop="name" label="部门名称" min-width="200" />
          <el-table-column prop="category" label="部门性质" width="150">
            <template #default="{row}">
               <el-tag :type="getCategoryTagType(row.category)" effect="light">{{ getCategoryLabel(row.category) }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="manager_name" label="负责人" width="150">
             <template #default="{row}">
               <div v-if="row.manager_name" class="flex items-center gap-1">
                 <el-avatar :size="24" class="bg-blue-100 text-blue-600 text-xs">{{ row.manager_name.charAt(0) }}</el-avatar>
                 <span>{{ row.manager_name }}</span>
               </div>
               <span v-else class="text-slate-400 text-sm">-</span>
             </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{row}">
              <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
              <el-button link type="primary" @click="handleAddSub(row)">添加下级</el-button>
              <el-popconfirm title="确定删除该部门？" @confirm="handleDelete(row)">
                 <template #reference>
                   <el-button link type="danger">删除</el-button>
                 </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </main>

    <!-- Dialog -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="form" label-width="100px" :rules="rules" ref="formRef">
        <el-form-item label="部门名称" prop="name">
          <el-input v-model="form.name" placeholder="例如：销售一部" />
        </el-form-item>
        
        <el-form-item label="上级部门" prop="parent">
          <el-tree-select
            v-model="form.parent"
            :data="items"
            check-strictly
            :render-after-expand="false"
            placeholder="无（作为顶级部门）"
            clearable
            style="width: 100%"
            :props="{ label: 'name', value: 'id', children: 'children' }"
          />
        </el-form-item>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="部门性质" prop="category">
              <el-select v-model="form.category" placeholder="选择性质" style="width: 100%">
                 <el-option v-for="(label, key) in categoryMap" :key="key" :label="label" :value="key" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="负责人" prop="manager">
              <el-select 
                v-model="form.manager" 
                placeholder="搜索负责人" 
                filterable 
                clearable 
                remote 
                :remote-method="searchUsers" 
                :loading="userLoading"
                style="width: 100%"
              >
                <el-option v-for="u in userOptions" :key="u.id" :label="`${u.last_name}${u.first_name} (${u.username})`" :value="u.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
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
import { ref, onMounted, computed } from 'vue';
import api from '../../api';
import { ElMessage } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';

const items = ref([]);
const loading = ref(false);
const dialogVisible = ref(false);
const submitting = ref(false);
const isEdit = ref(false);
const formRef = ref();
const userLoading = ref(false);
const userOptions = ref<any[]>([]);

const categoryMap: Record<string, string> = {
  'MANAGEMENT': '管理',
  'POC': 'POC',
  'RND': '研发',
  'LAB': '实验室',
  'FUNCTION': '职能',
  'SALES': '销售'
};

const form = ref<any>({
  id: null,
  name: '',
  parent: null,
  manager: null,
  category: 'FUNCTION'
});

const rules = {
  name: [{ required: true, message: '请输入部门名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择部门性质', trigger: 'change' }]
};

const dialogTitle = computed(() => {
  if (isEdit.value) return '编辑部门';
  if (form.value.parent) return '添加下级部门';
  return '新增顶级部门';
});

function getCategoryLabel(cat: string) {
  return categoryMap[cat] || cat;
}

function getCategoryTagType(cat: string) {
  if (['SALES', 'MANAGEMENT'].includes(cat)) return 'success';
  if (['RND', 'LAB', 'POC'].includes(cat)) return 'primary';
  if (['FUNCTION'].includes(cat)) return 'warning';
  return 'info';
}

// Transform flat list to tree
function buildTree(list: any[]) {
  const map: Record<number, any> = {};
  const roots: any[] = [];
  
  // First pass: create nodes
  list.forEach(item => {
    map[item.id] = { ...item, children: [] };
  });
  
  // Second pass: link parents
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
    const res = await api.get('departments/', { params: { page_size: 1000 } });
    const rawList = res.data.results || res.data;
    items.value = buildTree(rawList);
  }catch(e){
    ElMessage.error('加载数据失败');
  }finally{ loading.value = false; }
}

async function searchUsers(query: string) {
  if (!query) return;
  userLoading.value = true;
  try {
    const res = await api.get('users/simple/', { params: { search: query } });
    userOptions.value = res.data.map((u: any) => ({
      id: u.id,
      username: u.username,
      last_name: u.name.substring(0, 1), // approximate
      first_name: u.name.substring(1)
    }));
  } finally {
    userLoading.value = false;
  }
}

// Initial load of some users
async function loadInitialUsers() {
  const res = await api.get('users/simple/');
  userOptions.value = res.data.map((u: any) => ({
      id: u.id,
      username: u.username,
      last_name: u.name.substring(0, 1), 
      first_name: u.name.substring(1)
  }));
}

function handleCreate() {
  dialogVisible.value = true;
  isEdit.value = false;
  form.value = { id: null, name: '', parent: null, manager: null, category: 'OTHER' };
}

function handleAddSub(row: any) {
  dialogVisible.value = true;
  isEdit.value = false;
  form.value = { id: null, name: '', parent: row.id, manager: null, category: row.category }; // Inherit category by default
}

function handleEdit(row: any) {
  dialogVisible.value = true;
  isEdit.value = true;
  form.value = { 
    id: row.id, 
    name: row.name, 
    parent: row.parent, 
    manager: row.manager, 
    category: row.category 
  };
}

async function handleDelete(row: any) {
  if (row.children && row.children.length > 0) {
    return ElMessage.warning('请先删除下级部门');
  }
  try {
    await api.delete(`departments/${row.id}/`);
    ElMessage.success('删除成功');
    fetchData();
  } catch (e) {
    ElMessage.error('删除失败');
  }
}

async function submitForm() {
  if (!formRef.value) return;
  await formRef.value.validate(async (valid: boolean) => {
    if (valid) {
      submitting.value = true;
      try {
        if (form.value.id) {
          await api.patch(`departments/${form.value.id}/`, form.value);
          ElMessage.success('更新成功');
        } else {
          await api.post('departments/', form.value);
          ElMessage.success('创建成功');
        }
        dialogVisible.value = false;
        fetchData();
      } catch (e) {
        ElMessage.error('保存失败');
      } finally {
        submitting.value = false;
      }
    }
  });
}

onMounted(() => {
  fetchData();
  loadInitialUsers();
});
</script>