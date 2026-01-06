<template>
  <div class="space-y-6">
    <el-card>
      <template #header>迁移工具 · 快速导入</template>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="space-y-3">
          <el-select v-model="type" placeholder="选择数据类型">
            <el-option label="客户" value="customers" />
            <el-option label="赛事" value="competitions" />
            <el-option label="活动" value="activities" />
            <el-option label="商机" value="opportunities" />
          </el-select>
          <el-input v-model="jsonText" type="textarea" :rows="12" placeholder='粘贴 JSON 数组，如：[{"name":"示例","time":"2025-01-01"}]' />
          <div class="flex items-center gap-3">
            <el-button type="primary" @click="submit" :loading="loading">提交导入</el-button>
            <el-button @click="fillExample">示例数据</el-button>
          </div>
        </div>
        <div class="md:col-span-2">
          <div class="text-sm text-slate-500 mb-2">导入结果</div>
          <pre class="text-xs bg-slate-50 border rounded p-3 whitespace-pre-wrap">{{ resultText }}</pre>
        </div>
      </div>
    </el-card>
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue';
import api from '../../api';
import { ElMessage } from 'element-plus';

const type = ref<string>('');
const jsonText = ref<string>('');
const loading = ref(false);
const resultText = ref<string>('尚未导入');

async function submit(){
  if (!type.value){ ElMessage.warning('请选择类型'); return; }
  let rows:any[] = [];
  try{
    rows = JSON.parse(jsonText.value || '[]');
    if (!Array.isArray(rows)){ throw new Error('JSON必须是数组'); }
  }catch(e:any){
    ElMessage.error('JSON解析失败：' + (e?.message || ''));
    return;
  }
  loading.value = true;
  try{
    const res = await api.post('migrate/legacy/', { type: type.value, rows });
    resultText.value = JSON.stringify(res.data, null, 2);
    ElMessage.success('导入完成');
  }catch(e:any){
    const msg = (e.response && e.response.data) ? JSON.stringify(e.response.data) : (e?.message || '导入失败');
    resultText.value = msg;
    ElMessage.error('导入失败');
  }finally{ loading.value = false; }
}

function fillExample(){
  if (type.value === 'competitions'){
    jsonText.value = JSON.stringify([{ name:'示例高校赛', time:'2025-02-15', end_time:'2025-02-17', location:'南京', type:'CTF', team_count:'42', challenge_count:'10', host_type:'School', level:'Province' }], null, 2);
  } else if (type.value === 'activities'){
    jsonText.value = JSON.stringify([{ name:'示例活动', time:'2025-03-20', location:'北京', type:'沙龙', scale:'200人' }], null, 2);
  } else if (type.value === 'customers'){
    jsonText.value = JSON.stringify([{ name:'示例公司', industry:'教育', region:'北京', status:'POTENTIAL' }], null, 2);
  } else if (type.value === 'opportunities'){
    jsonText.value = JSON.stringify([{ name:'示例商机', customer_name:'示例公司', amount:200000, stage:'CONTACT', status:'ACTIVE', expected_sign_date:'2025-05-15', description:'示例说明' }], null, 2);
  } else {
    jsonText.value = JSON.stringify([{ name:'示例' }], null, 2);
  }
}
</script>
<style scoped>
</style>
