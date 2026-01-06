<template>
  <div class="space-y-6">
    <el-card>
      <template #header>系统工具</template>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <el-card>
          <template #header>重置测试数据</template>
          <div class="space-y-3">
            <el-input v-model="keepYear" placeholder="保留的目标年份" />
            <el-button type="danger" @click="resetData" :loading="loading">重置（保留该年业绩目标）</el-button>
          </div>
        </el-card>
        <el-card>
          <template #header>种子数据 · 业绩目标</template>
          <div class="space-y-3">
            <el-input v-model="seedYear" placeholder="年份" />
            <el-input v-model="seedRows" type="textarea" :rows="8" placeholder='可选：自定义JSON数组，不填则使用内置默认' />
            <el-button type="primary" @click="seedTargets" :loading="loading">写入业绩目标</el-button>
          </div>
        </el-card>
        <el-card>
          <template #header>AI模型配置</template>
          <div class="space-y-3">
            <div class="flex items-center gap-3">
              <el-select v-model="selConfigId" placeholder="已配置模型" style="width: 260px" @change="syncSelected">
                <el-option v-for="c in configs" :key="c.id" :label="`${c.name} · ${c.model_name}${c.is_active?'（默认）':''}`" :value="c.id" />
              </el-select>
              <el-button @click="refreshConfigs">刷新</el-button>
              <el-button type="success" @click="setDefault" :disabled="!selConfigId">设为默认</el-button>
            </div>
            <el-input v-model="conf.name" placeholder="配置名称" />
            <el-select v-model="conf.provider" placeholder="提供商">
              <el-option label="OpenAI兼容" value="OPENAI" />
              <el-option label="DeepSeek" value="DEEPSEEK" />
              <el-option label="Ollama" value="OLLAMA" />
              <el-option label="Kimi(Moonshot)" value="MOONSHOT" />
              <el-option label="通义千问" value="ALIYUN" />
              <el-option label="GLM" value="GLM" />
            </el-select>
            <el-input v-model="conf.base_url" placeholder="Base URL（如：https://api.deepseek.com/v1 或 http://host.docker.internal:11434/v1）" />
            <el-input v-model="conf.api_key" placeholder="API Key（Ollama不需要）" />
            <el-input v-model="conf.model_name" placeholder="模型名称（如：deepseek-chat, qwen3:8b）" />
            <el-checkbox v-model="conf.supports_vision">支持视觉/OCR</el-checkbox>
            <div class="flex items-center gap-3">
              <el-button type="primary" @click="saveConfig" :loading="loading">保存/新增</el-button>
            </div>
          </div>
        </el-card>
      </div>
      <div class="mt-4">
        <div class="text-sm text-slate-500 mb-2">结果</div>
        <pre class="text-xs bg-slate-50 border rounded p-3 whitespace-pre-wrap">{{ resultText }}</pre>
      </div>
    </el-card>
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue';
import api from '../../api';
import { ElMessage } from 'element-plus';
const keepYear = ref('2025');
const seedYear = ref('2025');
const seedRows = ref('');
const loading = ref(false);
const resultText = ref('尚未执行');
const configs = ref<any[]>([]);
const selConfigId = ref<number|null>(null);
const conf = ref<any>({ name:'', provider:'DEEPSEEK', base_url:'', api_key:'', model_name:'', supports_vision:false });
async function resetData(){
  loading.value = true;
  try{
    const res = await api.post('admin/reset-test-data/', { keep_year: parseInt(keepYear.value || '2025') });
    resultText.value = JSON.stringify(res.data, null, 2);
    ElMessage.success('已重置');
  }catch(e:any){
    const msg = (e.response && e.response.data) ? JSON.stringify(e.response.data) : (e?.message || '失败');
    resultText.value = msg; ElMessage.error('失败');
  } finally { loading.value = false; }
}
async function seedTargets(){
  loading.value = true;
  try{
    let rows:any = undefined;
    if (seedRows.value) rows = JSON.parse(seedRows.value);
    const res = await api.post('admin/seed-targets/', { year: parseInt(seedYear.value || '2025'), rows });
    resultText.value = JSON.stringify(res.data, null, 2);
    ElMessage.success('已写入');
  }catch(e:any){
    const msg = (e.response && e.response.data) ? JSON.stringify(e.response.data) : (e?.message || '失败');
    resultText.value = msg; ElMessage.error('失败');
  } finally { loading.value = false; }
}
async function refreshConfigs(){
  try{
    const res = await api.get('admin/ai-configs/');
    configs.value = res.data.results || res.data || [];
    if (!selConfigId.value && configs.value.length) selConfigId.value = configs.value[0].id;
    syncSelected();
  }catch(e:any){ ElMessage.error('加载模型失败'); }
}
function syncSelected(){
  const c = configs.value.find((x:any)=>x.id===selConfigId.value);
  if (c){
    conf.value = { ...c };
  }
}
async function saveConfig(){
  loading.value = true;
  try{
    let res;
    if (conf.value.id){
      res = await api.put(`admin/ai-configs/${conf.value.id}/`, conf.value);
    } else {
      res = await api.post('admin/ai-configs/', conf.value);
    }
    resultText.value = JSON.stringify(res.data, null, 2);
    ElMessage.success('保存成功'); 
    await refreshConfigs();
  }catch(e:any){
    const msg = (e.response && e.response.data) ? JSON.stringify(e.response.data) : (e?.message || '失败');
    resultText.value = msg; ElMessage.error('保存失败');
  } finally { loading.value = false; }
}
async function setDefault(){
  if (!selConfigId.value){ ElMessage.warning('请选择模型'); return; }
  loading.value = true;
  try{
    const res = await api.post(`admin/ai-configs/${selConfigId.value}/set_default/`, {});
    resultText.value = JSON.stringify(res.data, null, 2);
    ElMessage.success('已设为默认');
    await refreshConfigs();
  }catch(e:any){
    const msg = (e.response && e.response.data) ? JSON.stringify(e.response.data) : (e?.message || '失败');
    resultText.value = msg; ElMessage.error('设置失败');
  } finally { loading.value = false; }
}
refreshConfigs();
</script>
<style scoped>
</style>
