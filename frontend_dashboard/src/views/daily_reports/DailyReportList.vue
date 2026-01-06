<template>
  <div class="daily-report-container p-4 h-full flex flex-col">
    <div class="flex flex-1 gap-6 overflow-hidden">
      <!-- Left: Calendar Sidebar -->
      <div class="w-80 bg-white rounded-xl shadow-sm border border-gray-100 flex flex-col">
        <div class="p-4 border-b border-gray-50">
          <h2 class="text-lg font-bold text-gray-800">工作日历</h2>
        </div>
        
        <div class="p-2 flex-1 overflow-y-auto custom-scrollbar">
          <el-calendar v-model="currentDate" class="report-calendar">
            <template #date-cell="{ data }">
              <div class="calendar-day" :class="{ 'is-selected': data.isSelected, 'has-report': hasReport(data.day) }">
                <span class="day-number">{{ data.day.split('-').pop() }}</span>
                <div v-if="hasReport(data.day)" class="report-dot"></div>
              </div>
            </template>
          </el-calendar>
          
          <div class="mt-6 px-2">
            <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">最近动态</h3>
            <div class="space-y-2">
              <div v-for="report in recentReports" :key="report.id" 
                   class="group flex items-center justify-between p-2.5 rounded-lg hover:bg-blue-50 cursor-pointer transition-colors"
                   @click="selectDate(report.date)">
                <div class="flex items-center gap-2">
                   <div class="w-1.5 h-1.5 rounded-full" :class="getStatusColorClass(report.status)"></div>
                   <span class="text-sm font-medium text-gray-700">{{ report.date }}</span>
                </div>
                <span class="text-xs text-gray-400 group-hover:text-blue-600">{{ getStatusLabel(report.status) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right: Report Editor/Viewer -->
      <div class="flex-1 bg-white rounded-xl shadow-sm border border-gray-100 flex flex-col overflow-hidden">
        <!-- Header -->
        <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-white sticky top-0 z-10">
          <div>
            <div class="flex items-center gap-3">
              <h2 class="text-xl font-bold text-gray-800">{{ formatDate(currentDate) }}</h2>
              <el-tag v-if="currentReport" :type="getStatusType(currentReport.status)" effect="plain" round size="small">
                {{ getStatusLabel(currentReport.status) }}
              </el-tag>
              <el-tag v-else type="info" effect="plain" round size="small">未填写</el-tag>
            </div>
            <p class="text-xs text-gray-500 mt-1">记录每日工作进展与心得</p>
          </div>
          
          <div class="flex items-center gap-2">
            <template v-if="!isEditing">
               <el-button v-if="currentReport" type="danger" plain @click="confirmDelete" :icon="Delete">删除</el-button>
               <el-button v-if="currentReport" type="primary" @click="startEditing" :icon="Edit">编辑</el-button>
               <el-button v-else type="primary" @click="startEditing" :icon="Plus">新建日报</el-button>
            </template>
            <template v-else>
              <el-button @click="cancelEditing">取消</el-button>
              <el-button type="primary" :loading="saving" @click="saveReport">保存</el-button>
              <el-button v-if="undoStack.length > 1" type="warning" plain @click="handleUndo">
                <el-icon class="mr-1"><RefreshLeft /></el-icon> 撤销
              </el-button>
              <el-button type="success" plain :loading="polishing" @click="polishReport">
                <el-icon class="mr-1"><MagicStick /></el-icon> AI 润色
              </el-button>
            </template>
          </div>
        </div>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto p-6 relative">
          <div v-if="loading" class="h-full flex justify-center items-center">
            <el-spinner class="text-3xl text-blue-500" />
          </div>

          <div v-else>
            <!-- View Mode -->
            <div v-if="!isEditing && currentReport" class="max-w-4xl mx-auto space-y-8 animate-fade-in">
              <div class="border-b border-gray-100 pb-4 mb-4" v-if="currentReport.title">
                  <h2 class="text-2xl font-bold text-gray-800">{{ currentReport.title }}</h2>
              </div>
              
              <div v-if="currentReport.projects_detail?.length" class="bg-blue-50 p-4 rounded-xl border border-blue-100">
                <h3 class="text-sm font-bold text-blue-800 mb-3 flex items-center gap-2">
                  <el-icon><Folder /></el-icon> 关联项目
                </h3>
                <div class="flex flex-wrap gap-2">
                  <div v-for="proj in currentReport.projects_detail" :key="proj.id" 
                       class="bg-white px-3 py-1 rounded-md text-sm text-blue-700 shadow-sm border border-blue-100 flex items-center gap-2">
                    <span class="w-1.5 h-1.5 rounded-full bg-blue-400"></span>
                    {{ proj.name }}
                  </div>
                </div>
              </div>
              
              <div v-if="currentReport.mentions_detail?.length" class="bg-purple-50 p-4 rounded-xl border border-purple-100 mt-4">
                <h3 class="text-sm font-bold text-purple-800 mb-3 flex items-center gap-2">
                  <el-icon><User /></el-icon> 提及人员
                </h3>
                <div class="flex flex-wrap gap-2">
                  <div v-for="user in currentReport.mentions_detail" :key="user.id" 
                       class="bg-white px-3 py-1 rounded-md text-sm text-purple-700 shadow-sm border border-purple-100 flex items-center gap-2">
                    <span class="w-1.5 h-1.5 rounded-full bg-purple-400"></span>
                    {{ user.name }}
                  </div>
                </div>
              </div>

              <div>
                <h3 class="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                  <el-icon class="text-blue-500"><Document /></el-icon> 工作内容
                </h3>
                <div class="prose max-w-none">
                  <div class="bg-gray-50 p-6 rounded-xl border border-gray-100 text-gray-700 leading-relaxed whitespace-pre-wrap font-sans text-base">
                    {{ currentReport.polished_content || currentReport.raw_content }}
                  </div>
                  <div v-if="currentReport.polished_content" class="mt-2 flex justify-end items-center text-xs text-purple-500 font-medium">
                    <el-icon class="mr-1"><MagicStick /></el-icon> AI 已优化内容结构与表达
                  </div>
                </div>
              </div>
            </div>

            <!-- Edit Mode -->
            <div v-else-if="isEditing" class="max-w-4xl mx-auto space-y-6 animate-fade-in">
              
              <!-- Title Input -->
              <div>
                 <label class="block text-sm font-semibold text-gray-700 mb-2">日报标题</label>
                 <el-input 
                   v-model="form.title" 
                   placeholder="请输入日报标题（可选）"
                   size="large"
                 />
              </div>

              <div class="relative group">
                <label class="block text-sm font-semibold text-gray-700 mb-2">
                  工作内容 <span class="text-xs font-normal text-gray-400 ml-2">(输入 #关联项目，@提及用户)</span>
                </label>
                <el-input
                  id="report-textarea"
                  v-model="form.raw_content"
                  type="textarea"
                  :rows="15"
                  placeholder="请输入今日工作内容..."
                  class="w-full !text-base"
                  @input="handleInput"
                  resize="none"
                />
                
                <!-- Suggestion List (Unified for Projects and Users) -->
                <div v-if="showSuggestions" 
                     class="absolute z-50 bg-white border border-gray-200 rounded-lg shadow-xl mt-1 max-h-60 overflow-y-auto w-64 transform transition-all duration-200"
                     :style="{ top: suggestionTop + 'px', left: suggestionLeft + 'px' }">
                  <div v-if="suggestionLoading" class="p-3 text-center text-gray-400 text-xs">
                    <el-icon class="is-loading mr-1"><Loading /></el-icon> 加载中...
                  </div>
                  <ul v-else class="py-1">
                        <li v-for="item in suggestionOptions" :key="item.id" 
                            class="px-4 py-2.5 hover:bg-blue-50 cursor-pointer text-sm text-gray-700 flex flex-col gap-0.5 border-b border-gray-50 last:border-0"
                            @mousedown.prevent="selectSuggestion(item)">
                            <div class="flex items-center justify-between">
                                <span class="font-medium text-gray-800">{{ item.name }}</span>
                                <el-tag v-if="item.type === 'DEPT'" size="small" type="info" effect="plain">部门</el-tag>
                            </div>
                            <span class="text-xs text-gray-400">{{ suggestionType === 'PROJECT' ? (item.code || '项目') : (item.username || '用户') }}</span>
                        </li>
                        <li v-if="suggestionOptions.length === 0" class="px-4 py-3 text-gray-400 text-sm text-center">无匹配结果</li>
                     </ul>
                </div>
              </div>

              <!-- Project Selection (Moved to Bottom) -->
              <div class="pt-4 border-t border-gray-100">
                <label class="block text-sm font-semibold text-gray-700 mb-2">关联项目 (手动选择)</label>
                <el-select
                  v-model="form.projects"
                  multiple
                  filterable
                  remote
                  :remote-method="searchProjects"
                  placeholder="搜索并选择关联的项目..."
                  class="w-full"
                  :loading="suggestionLoading && suggestionType === 'PROJECT'"
                  size="large"
                >
                  <el-option
                    v-for="item in projectOptions"
                    :key="item.id"
                    :label="item.name"
                    :value="item.id"
                  />
                </el-select>
              </div>
            </div>

            <!-- Empty State -->
            <div v-else class="h-[60vh] flex flex-col justify-center items-center text-gray-400">
              <div class="w-24 h-24 bg-gray-50 rounded-full flex items-center justify-center mb-6">
                <el-icon class="text-4xl text-gray-300"><Calendar /></el-icon>
              </div>
              <p class="text-lg font-medium text-gray-500">该日期暂无日报</p>
              <p class="text-sm text-gray-400 mt-2 mb-8">记录点滴，成就非凡</p>
              <el-button type="primary" size="large" round @click="startEditing" class="px-8">立即填写</el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Calendar, MagicStick, Edit, Plus, Folder, Document, Loading, Delete, User, RefreshLeft } from '@element-plus/icons-vue';
import api from '../../api';

// Interfaces
interface Project {
  id: number;
  name: string;
  code?: string;
}

interface User {
  id: number;
  username: string;
  name: string;
}

interface DailyReport {
  id: number;
  date: string;
  title?: string;
  raw_content: string;
  polished_content?: string;
  projects: number[];
  mentions: number[];
  projects_detail?: Project[];
  mentions_detail?: User[];
  status: string;
}

const route = useRoute();

// State
const currentDate = ref(new Date());
const reports = ref<DailyReport[]>([]);
const currentReport = ref<DailyReport | null>(null);
const loading = ref(false);
const saving = ref(false);
const polishing = ref(false);
const isEditing = ref(false);

const form = ref({
  title: '',
  raw_content: '',
  projects: [] as number[],
  mentions: [] as number[]
});

const suggestionLoading = ref(false);
const suggestionOptions = ref<any[]>([]); // Can be Project[] or User[]
const suggestionType = ref<'PROJECT' | 'USER'>('PROJECT');
const projectOptions = ref<Project[]>([]); // Store separately for the bottom select
const showSuggestions = ref(false);
const suggestionTop = ref(0);
const suggestionLeft = ref(20);
const lastAtPos = ref(0);

// Undo History
const undoStack = ref<string[]>([]);
const MAX_HISTORY = 20;

const pushToHistory = (content: string) => {
  if (undoStack.value.length === 0 || undoStack.value[undoStack.value.length - 1] !== content) {
    undoStack.value.push(content);
    if (undoStack.value.length > MAX_HISTORY) {
      undoStack.value.shift();
    }
  }
};

const handleUndo = () => {
  if (undoStack.value.length > 1) {
    // Current state is at the top, remove it
    undoStack.value.pop();
    // Get previous state
    const previous = undoStack.value[undoStack.value.length - 1];
    if (previous !== undefined) {
      form.value.raw_content = previous;
      ElMessage.info('已撤销');
    }
  } else if (undoStack.value.length === 1) {
    // Only one state, reset to empty or initial
    form.value.raw_content = '';
    undoStack.value.pop();
    ElMessage.info('已重置');
  }
};

// Methods
const selectDate = (date: string) => {
  const targetDate = new Date(date);
  if (!isNaN(targetDate.getTime())) {
    currentDate.value = targetDate;
  }
};

const formatDate = (date: Date) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

// Computed
const recentReports = computed(() => {
  return [...reports.value].sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()).slice(0, 5);
});

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = { 'DRAFT': '草稿', 'SUBMITTED': '已提交', 'APPROVED': '已确认', 'REJECTED': '需修改' };
  return map[status] || status;
};

const getStatusType = (status: string) => {
  const map: Record<string, string> = { 'DRAFT': 'info', 'SUBMITTED': 'primary', 'APPROVED': 'success', 'REJECTED': 'danger' };
  return map[status] || 'info';
};

const getStatusColorClass = (status: string) => {
  const map: Record<string, string> = { 'DRAFT': 'bg-gray-400', 'SUBMITTED': 'bg-blue-500', 'APPROVED': 'bg-green-500', 'REJECTED': 'bg-red-500' };
  return map[status] || 'bg-gray-400';
};

const hasReport = (day: string) => {
  return reports.value.some(r => r.date === day);
};

const checkCurrentDateReport = () => {
  const dateStr = formatDate(currentDate.value);
  const found = reports.value.find(r => r.date === dateStr);
  currentReport.value = found || null;
};

const fetchReports = async () => {
  loading.value = true;
  try {
    const res = await api.get('daily-reports/');
    reports.value = res.data.results || res.data;
    checkCurrentDateReport();
  } catch (error) {
    console.error('Failed to fetch reports:', error);
    ElMessage.error('获取日报失败');
  } finally {
    loading.value = false;
  }
};

const startEditing = () => {
  if (currentReport.value) {
    form.value = {
      title: currentReport.value.title || '',
      // 优先使用润色后的内容，确保“所见即所得”的编辑体验
      raw_content: currentReport.value.polished_content || currentReport.value.raw_content,
      projects: currentReport.value.projects,
      mentions: currentReport.value.mentions || []
    };
    if (currentReport.value.projects_detail) {
      projectOptions.value = currentReport.value.projects_detail;
    }
  } else {
    form.value = {
      title: '',
      raw_content: '',
      projects: [],
      mentions: []
    };
  }
  isEditing.value = true;
  // Initialize undo stack
  undoStack.value = [form.value.raw_content];
  
  // Initialize project list for search suggestions if empty
  if (projectOptions.value.length === 0) {
      searchProjects('');
  }
};

const cancelEditing = () => {
  isEditing.value = false;
  checkCurrentDateReport();
  showSuggestions.value = false;
};

const searchProjects = async (query: string) => {
  suggestionLoading.value = true;
  try {
    const response = await api.get(`projects/?search=${encodeURIComponent(query)}`);
    const results = response.data.results || response.data;
    projectOptions.value = results; // Update bottom select options
    if (suggestionType.value === 'PROJECT') {
        suggestionOptions.value = results;
    }
  } catch (error) {
    console.error('Failed to search projects:', error);
  } finally {
    suggestionLoading.value = false;
  }
};

const searchUsers = async (query: string) => {
  suggestionLoading.value = true;
  try {
    // 强制使用全局 api 实例，并确保 query 编码
    const response = await api.get(`users/simple/?search=${encodeURIComponent(query)}`);
    console.log('Search Users Result:', response.data);
    
    const results = response.data.results || response.data;
    if (Array.isArray(results)) {
      suggestionOptions.value = results.map((item: any) => ({
        ...item,
        name: item.name || item.username || item.label,
        type: item.type || 'USER'
      }));
    } else {
      suggestionOptions.value = [];
    }
  } catch (error) {
    console.error('Failed to search users:', error);
    suggestionOptions.value = [];
  } finally {
    suggestionLoading.value = false;
  }
};

const handleInput = (val: string) => {
  // 1. Push to undo history
  pushToHistory(val);

  // Suggestion logic
  const elInput = document.getElementById('report-textarea');
  // 兼容性处理：如果 ID 直接在 textarea 上，或者在包装器上
  const textarea = (elInput?.tagName === 'TEXTAREA' ? elInput : elInput?.querySelector('textarea')) as HTMLTextAreaElement;
  
  if (!textarea) {
    console.warn('Textarea not found for suggestions');
    return;
  }

  const { selectionStart } = textarea;
  const textBeforeCursor = val.substring(0, selectionStart);
  
  // Check for # (Project) or @ (User) before the cursor
  const pattern = /([#@])([^#@\s]*)$/;
  const match = textBeforeCursor.match(pattern);
  
  if (match) {
    const symbol = match[1];
    const query = match[2] || '';
    
    lastAtPos.value = match.index!;
    showSuggestions.value = true;
    
    // Position logic
    const lines = textBeforeCursor.split('\n');
    const currentLineIndex = lines.length - 1;
    const currentLine = lines[currentLineIndex] || '';
    const currentCharIndex = currentLine.length;
    
    suggestionTop.value = Math.min(currentLineIndex * 24 + 40, 500); 
    suggestionLeft.value = Math.min(currentCharIndex * 9 + 20, 600);
    
    suggestionType.value = symbol === '#' ? 'PROJECT' : 'USER';
    
    if (suggestionType.value === 'PROJECT') {
        searchProjects(query);
    } else {
        suggestionOptions.value = [];
        searchUsers(query);
    }
  } else {
    showSuggestions.value = false;
  }
};

const selectSuggestion = (item: any) => {
    const elInput = document.getElementById('report-textarea');
    const textarea = (elInput?.tagName === 'TEXTAREA' ? elInput : elInput?.querySelector('textarea')) as HTMLTextAreaElement;
    
    if (!textarea) return;

    const { selectionStart } = textarea;
    const textBeforeCursor = form.value.raw_content.substring(0, selectionStart);
    const textAfterCursor = form.value.raw_content.substring(selectionStart);
    
    const pattern = /([#@])([^#@\s]*)$/;
    const match = textBeforeCursor.match(pattern);
    
    if (match) {
        const prefix = textBeforeCursor.substring(0, match.index);
        const trigger = match[1] || '';
        
        // Replace the trigger and query with the selected item name
        const name = suggestionType.value === 'PROJECT' ? item.name : (item.name || item.username);
        form.value.raw_content = prefix + `${trigger}${name} ` + textAfterCursor;
        
        // 关键修复：选中后立即关闭列表
        showSuggestions.value = false;
        
        if (suggestionType.value === 'PROJECT') {
            if (!form.value.projects.includes(item.id)) {
                form.value.projects.push(item.id);
            }
        } else {
            // It's a USER or DEPT mention
            if (item.type === 'USER') {
                if (!form.value.mentions.includes(item.id)) {
                    form.value.mentions.push(item.id);
                }
            } else if (item.type === 'DEPT') {
                // For departments, we might want to expand to all users in dept or just keep as is
                // For now, just add the name to content, which is already done above
            }
        }
        
        // Push updated content to history
        pushToHistory(form.value.raw_content);
        
        // Refocus textarea and place cursor after the inserted name
        nextTick(() => {
            textarea.focus();
            const newPos = prefix.length + trigger.length + name.length + 1;
            textarea.setSelectionRange(newPos, newPos);
        });
    }
};

const saveReport = async () => {
  saving.value = true;
  const dateStr = formatDate(currentDate.value);
  const payload = {
    date: dateStr,
    title: form.value.title,
    raw_content: form.value.raw_content,
    projects: form.value.projects,
    mentions: form.value.mentions,
    // IMPORTANT: Clear polished_content when saving manually. 
    // This ensures that the manually edited content is what gets displayed in "View" mode 
    // and on the Personal Center dashboard.
    polished_content: '',
    status: 'SUBMITTED' // Ensure status is set to SUBMITTED when saving
  };


  try {
    // If we have an existing report for this date (from checkCurrentDateReport logic), 
    // we should update it.
    // The backend now supports UPSERT on create if date matches, 
    // but explicit PATCH is safer if we know the ID.
    if (currentReport.value && currentReport.value.id) {
       await api.patch(`daily-reports/${currentReport.value.id}/`, payload);
    } else {
       // Check if there's a report in the list that matches the date but currentReport wasn't set (unlikely)
       // Or just rely on backend UPSERT logic
       await api.post('daily-reports/', payload);
    }
    
    ElMessage.success('保存成功');
    isEditing.value = false; // 保存后退出编辑模式
    await fetchReports();
  } catch (error) {
    console.error('Failed to save report:', error);
    ElMessage.error('保存失败');
  } finally {
    saving.value = false;
  }
};

const polishReport = async () => {
  if (!form.value.raw_content) {
    ElMessage.warning('请先输入工作内容');
    return;
  }

  polishing.value = true;
  try {
            // 直接调用 AI 分析接口进行润色，不触发保存和退出
            const res = await api.post('ai/analyze/', {
              text: form.value.raw_content,
              mode: 'POLISH_REPORT'
            });
    
    if (res.data && res.data.content) {
      // 记录撤销历史
      pushToHistory(form.value.raw_content);
      // 直接更新当前编辑器内容
      form.value.raw_content = res.data.content;
      ElMessage.success('AI 润色完成');
    } else {
      ElMessage.warning('AI 润色未能返回有效内容');
    }
  } catch (error) {
    console.error('Failed to polish report:', error);
    ElMessage.error('AI 润色失败');
  } finally {
    polishing.value = false;
  }
};

const confirmDelete = () => {
  ElMessageBox.confirm(
    '确定要删除这条日报吗？删除后无法恢复。',
    '删除确认',
    {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(() => {
      deleteReport();
    })
    .catch(() => {});
};

const deleteReport = async () => {
  if (!currentReport.value) return;
  try {
    await api.delete(`daily-reports/${currentReport.value.id}/`);
    ElMessage.success('删除成功');
    // Remove from local list to update UI immediately
    reports.value = reports.value.filter(r => r.id !== currentReport.value!.id);
    currentReport.value = null;
    checkCurrentDateReport();
  } catch (error) {
    console.error('Failed to delete report:', error);
    ElMessage.error('删除失败');
  }
};

// Watchers
watch(() => route.fullPath, () => {
  // 如果没有任何编辑参数，且当前正在编辑，则退出编辑模式
  if (!route.query.edit && isEditing.value) {
    isEditing.value = false;
    checkCurrentDateReport();
  }
});

watch(currentDate, () => {
  isEditing.value = false;
  undoStack.value = []; // Clear undo stack on date change
  checkCurrentDateReport();
});

// Lifecycle
onMounted(async () => {
  await fetchReports();
  
  // Handle navigation from other pages (e.g., Personal Center)
  if (route.query.date) {
    const queryDate = new Date(route.query.date as string);
    // Ensure the date is valid
    if (!isNaN(queryDate.getTime())) {
      currentDate.value = queryDate;
      checkCurrentDateReport();
      
      // Auto-start editing if requested
      if (route.query.edit === 'true') {
        startEditing();
      }
    }
  }
});
</script>

<style scoped>
/* Calendar Customization */
.report-calendar {
  --el-calendar-border: none;
  background: transparent;
}

.report-calendar :deep(.el-calendar__header) {
  display: none; /* Hide default header, we use our own title */
}

.report-calendar :deep(.el-calendar__body) {
  padding: 0;
}

.report-calendar :deep(.el-calendar-table) {
  border: none;
}

.report-calendar :deep(.el-calendar-table thead th) {
  color: #94a3b8;
  font-size: 12px;
  font-weight: 600;
  padding: 12px 0;
}

.report-calendar :deep(.el-calendar-table td) {
  border: none;
  padding: 4px;
}

.report-calendar :deep(.el-calendar-table .el-calendar-day) {
  height: 36px; /* Compact height */
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%; /* Circle shape */
  transition: all 0.2s;
}

.report-calendar :deep(.el-calendar-table td:hover .el-calendar-day) {
  background-color: #f1f5f9;
}

/* Selected Day */
.report-calendar :deep(.el-calendar-table td.is-selected .el-calendar-day) {
  background-color: #2563eb;
  color: white;
  box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.3);
}

/* Today */
.report-calendar :deep(.el-calendar-table td.is-today .el-calendar-day) {
  color: #2563eb;
  font-weight: bold;
}

.report-calendar :deep(.el-calendar-table td.is-selected.is-today .el-calendar-day) {
  color: white;
}

/* Custom Day Content */
.calendar-day {
  display: flex;
  flex-col: column;
  align-items: center;
  justify-content: center;
  position: relative;
  width: 100%;
  height: 100%;
}

.report-dot {
  position: absolute;
  bottom: 4px;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background-color: #10b981; /* Green dot */
}

.is-selected .report-dot {
  background-color: white;
}

/* Scrollbar */
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #e2e8f0;
  border-radius: 20px;
}

/* Animation */
.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
