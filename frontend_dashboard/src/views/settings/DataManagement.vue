<template>
  <div class="h-full flex flex-col bg-slate-50 p-6 space-y-6 overflow-hidden animate-fade-in">
    <!-- Header -->
    <div class="flex justify-between items-center bg-white p-4 rounded-2xl shadow-sm border border-gray-100">
      <div class="flex items-center gap-3">
        <div class="p-2 bg-pomegranate-50 rounded-lg text-pomegranate-600">
          <el-icon size="20"><Management /></el-icon>
        </div>
        <div>
          <h2 class="text-xl font-bold text-gray-900">数据管理</h2>
          <p class="text-xs text-gray-500">备份、导出及系统数据恢复控制台</p>
        </div>
      </div>
      <el-tag type="danger" effect="dark" class="rounded-full px-4">管理员专用权限</el-tag>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Backup Section -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden flex flex-col">
        <div class="p-5 border-b border-gray-50 flex items-center gap-2 bg-slate-50/50">
          <el-icon class="text-blue-500"><Download /></el-icon>
          <span class="font-bold text-gray-800">数据备份与导出</span>
        </div>
        <div class="p-6 flex-1 flex flex-col">
          <p class="text-sm text-gray-500 mb-6 leading-relaxed">
            定期导出系统核心业务数据（客户、商机、项目及日志）是保障数据安全的重要手段。
            建议在进行大规模数据调整前手动执行一次全量备份。
          </p>
          
          <div class="grid grid-cols-1 gap-4">
            <div 
              class="group p-4 rounded-xl border border-gray-100 bg-white hover:border-blue-200 hover:bg-blue-50/30 transition-all cursor-pointer flex items-center gap-4"
              @click="handleExport('all')"
            >
              <div class="p-3 bg-blue-100 text-blue-600 rounded-lg group-hover:scale-110 transition-transform">
                <el-icon size="20"><DocumentChecked /></el-icon>
              </div>
              <div class="flex-1">
                <div class="font-bold text-gray-800">导出全量数据</div>
                <div class="text-xs text-gray-400">包含数据库所有表结构的 JSON/SQL 镜像</div>
              </div>
              <el-icon class="text-gray-300 group-hover:text-blue-500"><ArrowRight /></el-icon>
            </div>

            <div 
              class="group p-4 rounded-xl border border-gray-100 bg-white hover:border-green-200 hover:bg-green-50/30 transition-all cursor-pointer flex items-center gap-4"
              @click="handleExport('business')"
            >
              <div class="p-3 bg-green-100 text-green-600 rounded-lg group-hover:scale-110 transition-transform">
                <el-icon size="20"><List /></el-icon>
              </div>
              <div class="flex-1">
                <div class="font-bold text-gray-800">导出业务报表</div>
                <div class="text-xs text-gray-400">客户、商机等核心业务数据的 Excel 格式导出</div>
              </div>
              <el-icon class="text-gray-300 group-hover:text-green-500"><ArrowRight /></el-icon>
            </div>

            <div 
              class="group p-4 rounded-xl border border-gray-100 bg-white hover:border-purple-200 hover:bg-purple-50/30 transition-all cursor-pointer flex items-center gap-4"
              @click="handleExport('config')"
            >
              <div class="p-3 bg-purple-100 text-purple-600 rounded-lg group-hover:scale-110 transition-transform">
                <el-icon size="20"><Setting /></el-icon>
              </div>
              <div class="flex-1">
                <div class="font-bold text-gray-800">导出系统配置</div>
                <div class="text-xs text-gray-400">包含 AI 提示词、用户部门及职位配置</div>
              </div>
              <el-icon class="text-gray-300 group-hover:text-purple-500"><ArrowRight /></el-icon>
            </div>
          </div>
        </div>
      </div>

      <!-- Restore Section -->
      <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden flex flex-col">
        <div class="p-5 border-b border-gray-50 flex items-center gap-2 bg-slate-50/50">
          <el-icon class="text-pomegranate-500"><Upload /></el-icon>
          <span class="font-bold text-gray-800">数据恢复</span>
        </div>
        <div class="p-6 flex-1 flex flex-col">
          <div class="bg-red-50 border border-red-100 p-4 rounded-xl mb-6 flex gap-3">
            <el-icon class="text-red-500 mt-1"><WarningFilled /></el-icon>
            <div class="text-xs text-red-700 leading-normal">
              <strong class="block mb-1">危险操作警告：</strong>
              数据恢复将会根据上传的文件**覆盖**当前系统中的现有数据。
              此操作不可逆，请务必在操作前确认已做好当前数据的备份。
            </div>
          </div>

          <el-upload
            class="restore-uploader w-full"
            drag
            action="#"
            :auto-upload="false"
            :on-change="handleFileChange"
            accept=".json,.sql"
          >
            <div class="py-4">
              <el-icon class="text-gray-300 mb-2" size="48"><UploadFilled /></el-icon>
              <div class="text-sm text-gray-500">
                将备份文件拖到此处，或 <em class="text-pomegranate-500 font-bold italic">点击上传</em>
              </div>
              <div class="text-xs text-gray-400 mt-2">支持 .json 或 .sql 格式的备份文件</div>
            </div>
          </el-upload>

          <button 
            class="w-full mt-6 py-3 rounded-xl font-bold text-sm transition-all flex items-center justify-center gap-2 active:scale-95"
            :class="selectedFile ? 'bg-pomegranate-600 text-white shadow-lg shadow-red-200 hover:bg-pomegranate-700' : 'bg-gray-100 text-gray-400 cursor-not-allowed'"
            :disabled="!selectedFile"
            @click="handleRestore"
          >
            <el-icon><RefreshRight /></el-icon>
            执行数据恢复程序
          </button>
        </div>
      </div>
    </div>

    <!-- History Section -->
    <div class="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden flex-1 flex flex-col min-h-[300px]">
      <div class="p-5 border-b border-gray-50 flex items-center justify-between bg-slate-50/50">
        <div class="flex items-center gap-2">
          <el-icon class="text-gray-400"><Clock /></el-icon>
          <span class="font-bold text-gray-800">备份与导出历史</span>
        </div>
        <button class="text-xs text-blue-600 hover:underline">清除记录</button>
      </div>
      <div class="p-4 flex-1 overflow-auto">
        <el-table :data="history" style="width: 100%" header-cell-class-name="bg-slate-50 text-gray-500 text-xs uppercase tracking-wider">
          <el-table-column prop="time" label="操作时间" width="200">
            <template #default="{row}">
              <span class="font-mono text-gray-600">{{ row.time }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="type" label="操作类型" width="120">
            <template #default="{ row }">
              <span 
                class="px-2 py-0.5 rounded text-[10px] font-bold"
                :class="row.type === '备份' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'"
              >
                {{ row.type }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="operator" label="执行人" width="120">
            <template #default="{row}">
              <div class="flex items-center gap-2">
                <el-avatar :size="20" class="bg-slate-200 text-[10px]">{{ row.operator[0].toUpperCase() }}</el-avatar>
                <span class="text-sm">{{ row.operator }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <div class="flex items-center gap-1.5">
                <span class="w-1.5 h-1.5 rounded-full" :class="row.status === '成功' ? 'bg-green-500' : 'bg-red-500'"></span>
                <span class="text-sm" :class="row.status === '成功' ? 'text-green-600' : 'text-red-600'">{{ row.status }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="remark" label="备注" />
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * 数据管理组件
 * 实现系统数据的备份、导出与恢复功能 UI 优化版
 */
import { ref } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { 
  Download, Upload, UploadFilled, Management, 
  WarningFilled, RefreshRight, Clock, DocumentChecked, 
  List, Setting, ArrowRight 
} from '@element-plus/icons-vue';

const selectedFile = ref(null);
const history = ref([
  { time: '2025-01-05 10:00:00', type: '备份', operator: 'admin', status: '成功', remark: '系统自动全量备份' },
  { time: '2025-01-04 15:30:00', type: '导出', operator: 'admin', status: '成功', remark: '导出业务数据用于报表' },
]);

/** 处理导出逻辑 */
const handleExport = (type: string) => {
  ElMessage.info(`正在开发中: 导出类型为 ${type}`);
};

/** 处理文件选择 */
const handleFileChange = (file: any) => {
  selectedFile.value = file;
};

/** 处理恢复逻辑 */
const handleRestore = () => {
  ElMessageBox.confirm(
    '数据恢复是一个危险操作，将会覆盖现有数据。建议先执行备份操作。是否继续？',
    '严正警告',
    {
      confirmButtonText: '确认风险并恢复',
      cancelButtonText: '取消',
      confirmButtonClass: 'el-button--danger',
      type: 'error',
    }
  ).then(() => {
    ElMessage.warning('数据恢复模块正在部署中...');
  }).catch(() => {
    ElMessage.info('已取消风险操作');
  });
};
</script>

<style scoped>
.restore-uploader :deep(.el-upload-dragger) {
  background-color: #f8fafc;
  border: 2px dashed #e2e8f0;
  border-radius: 1rem;
  transition: all 0.3s ease;
}
.restore-uploader :deep(.el-upload-dragger:hover) {
  border-color: #D64045;
  background-color: #fff1f2;
}
.animate-fade-in {
  animation: fadeIn 0.4s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
