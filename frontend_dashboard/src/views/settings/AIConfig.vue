<template>
  <div class="h-full flex flex-col bg-slate-50">
    <header class="bg-white border-b border-slate-200 px-8 py-6 flex justify-between items-center shrink-0">
      <div class="flex flex-col gap-1">
        <h1 class="text-2xl font-bold text-slate-800 tracking-tight">AI 模型配置</h1>
        <div class="text-sm text-slate-500">管理系统接入的大模型参数与优先级</div>
      </div>
      <el-button type="primary" size="large" @click="handleCreate">
        <el-icon class="mr-1"><Plus /></el-icon> 新增配置
      </el-button>
    </header>

    <main class="flex-1 p-8 overflow-auto">
      <div class="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
        <el-table :data="items" v-loading="loading" style="width: 100%" :header-cell-style="{background:'#f8fafc', color:'#475569', fontWeight:'600'}">
          <el-table-column prop="name" label="配置名称" min-width="150">
            <template #default="{row}">
              <div class="font-medium text-slate-800">{{ row.name }}</div>
              <div class="text-xs text-slate-400" v-if="row.model_name">Model: {{ row.model_name }}</div>
            </template>
          </el-table-column>
          <el-table-column prop="provider" label="提供商" width="120">
            <template #default="{row}">
              <el-tag effect="plain" :type="getProviderTag(row.provider)">{{ row.provider }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{row}">
              <el-tag v-if="row.is_active" type="success" effect="dark">默认激活</el-tag>
              <el-tag v-else type="info">备用</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="能力" width="120">
            <template #default="{row}">
               <el-tag v-if="row.supports_vision" type="warning" size="small" effect="plain">视觉能力</el-tag>
               <span v-else class="text-slate-400 text-xs">-</span>
            </template>
          </el-table-column>
          <el-table-column prop="updated_at" label="更新时间" width="180">
             <template #default="{row}">{{ new Date(row.updated_at).toLocaleString() }}</template>
          </el-table-column>
          <el-table-column label="操作" width="260" fixed="right">
            <template #default="{row}">
              <div class="flex items-center gap-2">
                <el-button link type="warning" @click="testConnection(row)" :loading="testing">测试</el-button>
                <el-button v-if="!row.is_active" link type="success" @click="setDefault(row)">设为默认</el-button>
                <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
                <el-popconfirm title="确定删除该配置?" @confirm="handleDelete(row)">
                  <template #reference>
                    <el-button link type="danger">删除</el-button>
                  </template>
                </el-popconfirm>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </main>

    <!-- Dialog -->
    <el-dialog v-model="dialogVisible" :title="isEdit?'编辑配置':'新增配置'" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="配置名称">
          <el-input v-model="form.name" placeholder="例如：DeepSeek V3" />
        </el-form-item>
        <el-form-item label="提供商">
          <el-select v-model="form.provider" placeholder="选择厂商">
            <el-option label="OpenAI (兼容)" value="OPENAI" />
            <el-option label="DeepSeek" value="DEEPSEEK" />
            <el-option label="Google Gemini" value="GEMINI" />
            <el-option label="Anthropic Claude" value="ANTHROPIC" />
            <el-option label="Azure OpenAI" value="AZURE" />
            <el-option label="Ollama (本地)" value="OLLAMA" />
          </el-select>
        </el-form-item>
        <el-form-item label="模型名称">
          <el-input v-model="form.model_name" placeholder="例如：deepseek-chat" />
        </el-form-item>
        <el-form-item label="Base URL">
          <el-input v-model="form.base_url" placeholder="API 基础地址" />
        </el-form-item>
        <el-form-item label="API Key">
          <el-input v-model="form.api_key" type="password" show-password placeholder="密钥" />
        </el-form-item>
        <el-form-item label="视觉支持">
          <el-switch v-model="form.supports_vision" />
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
import { ref, onMounted } from 'vue';
import api from '../../api';
import { ElMessage } from 'element-plus';
import { Plus } from '@element-plus/icons-vue';

const items = ref([]);
const loading = ref(false);
const dialogVisible = ref(false);
const submitting = ref(false);
const isEdit = ref(false);

const form = ref({
  id: null,
  name: '',
  provider: 'OPENAI',
  model_name: '',
  base_url: '',
  api_key: '',
  supports_vision: false
});

const testing = ref(false);

async function testConnection(row: any) {
  testing.value = true;
  try {
    // 修正接口路径和参数传递方式，符合后端 DRF Action 规范
    const res = await api.post(`admin/ai-configs/${row.id}/test_connection/`);
    if (res.data.status === 'success') {
      ElMessage.success('连接测试成功: ' + (res.data.message || 'AI 响应正常'));
    } else {
      ElMessage.error('连接测试失败: ' + (res.data.detail || res.data.message));
    }
  } catch (e: any) {
    console.error('AI Test Error:', e);
    const detail = e.response?.data?.detail || e.response?.data?.message || e.message;
    ElMessage.error('测试出错: ' + detail);
  } finally {
    testing.value = false;
  }
}

async function fetchData(){
  loading.value = true;
  try{
    const res = await api.get('admin/ai-configs/');
    items.value = res.data.results || res.data;
  }catch(e){
    ElMessage.error('加载配置失败');
  }finally{ loading.value = false; }
}

function handleCreate(){
  isEdit.value = false;
  form.value = { id:null, name:'', provider:'openai', model_name:'', base_url:'', api_key:'', supports_vision:false };
  dialogVisible.value = true;
}

function handleEdit(row:any){
  isEdit.value = true;
  form.value = { ...row }; // Copy fields
  dialogVisible.value = true;
}

async function submitForm(){
  if(!form.value.name || !form.value.api_key) return ElMessage.warning('请完善必填信息');
  submitting.value = true;
  try{
    if(isEdit.value){
      await api.patch(`admin/ai-configs/${form.value.id}/`, form.value);
      ElMessage.success('更新成功');
    }else{
      await api.post('admin/ai-configs/', form.value);
      ElMessage.success('创建成功');
    }
    dialogVisible.value = false;
    fetchData();
  }catch(e:any){
    console.error('AI配置保存详情错误:', e.response || e);
    const msg = e.response?.data ? JSON.stringify(e.response.data) : '请检查网络或权限';
    ElMessage.error('保存失败: ' + msg);
  }finally{ submitting.value = false; }
}

async function handleDelete(row:any){
  try{
    await api.delete(`admin/ai-configs/${row.id}/`);
    ElMessage.success('已删除');
    fetchData();
  }catch(e){ ElMessage.error('删除失败'); }
}

async function setDefault(row:any){
  try{
    await api.post(`admin/ai-configs/${row.id}/set_default/`);
    ElMessage.success('已设为默认');
    fetchData();
  }catch(e){ ElMessage.error('设置失败'); }
}

function getProviderTag(p:string){
  const provider = (p || '').toLowerCase();
  const map:any = { deepseek:'primary', openai:'success', gemini:'warning', anthropic:'danger', ollama:'info' };
  return map[provider] || 'info';
}

onMounted(fetchData);
</script>
