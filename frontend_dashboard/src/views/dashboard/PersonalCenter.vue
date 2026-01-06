<template>
  <div class="space-y-6">
    <!-- Row 1: Targets & Notifications -->
    <el-row :gutter="20">
      <!-- 1. Department Targets -->
      <el-col :span="8">
        <el-card class="shadow-sm h-full flex flex-col">
          <template #header>
            <div class="flex justify-between items-center">
              <span class="font-bold text-lg">部门目标及完成情况</span>
            </div>
          </template>
          <div class="flex-1 flex flex-col justify-center space-y-6 p-6">
            <div class="flex justify-between items-baseline">
              <span class="text-slate-500 text-base">目标金额</span>
              <span class="text-2xl font-bold text-slate-800">¥ 5,000,000</span>
            </div>
            <div class="flex justify-between items-baseline">
              <span class="text-slate-500 text-base">已完成</span>
              <span class="text-2xl font-bold text-green-600">¥ 3,250,000</span>
            </div>
            <el-progress :percentage="65" :stroke-width="12" :format="formatPercentage" status="success" />
          </div>
        </el-card>
      </el-col>

      <!-- 2. Personal Targets -->
      <el-col :span="8">
        <el-card class="shadow-sm h-full flex flex-col">
          <template #header>
            <div class="flex justify-between items-center">
              <span class="font-bold text-lg">个人目标及完成情况</span>
              <el-tag size="small">本季度</el-tag>
            </div>
          </template>
          <div class="flex-1 flex flex-col justify-center space-y-6 p-6">
            <div class="flex justify-between items-baseline">
              <span class="text-slate-500 text-base">个人目标</span>
              <span class="text-2xl font-bold text-slate-800">¥ 1,000,000</span>
            </div>
            <div class="flex justify-between items-baseline">
              <span class="text-slate-500 text-base">当前预测</span>
              <span class="text-2xl font-bold text-blue-600">¥ 850,000</span>
            </div>
            <el-progress :percentage="85" :stroke-width="12" :format="formatPercentage" />
          </div>
        </el-card>
      </el-col>

      <!-- 3. Notifications (Manager Messaging System) -->
      <el-col :span="8">
        <el-card class="shadow-sm h-full flex flex-col overflow-hidden">
          <template #header>
            <div class="flex justify-between items-center">
              <span class="font-bold text-lg">通知消息</span>
              <div class="flex items-center gap-2">
                <!-- Manager Publish Button -->
                <el-button size="small" type="primary" plain @click="showPublishModal = true">
                    <i data-lucide="send" class="w-3 h-3 mr-1"></i>发布
                </el-button>
                <el-button link type="primary" class="!text-sm !font-medium" :class="showAllMessages ? '!text-blue-600 !font-bold' : '!text-slate-400'" @click="showAllMessages = !showAllMessages">
                    {{ showAllMessages ? '收起历史' : '全部消息' }}
                </el-button>
                <el-button link type="primary" class="!text-sm !text-blue-600 hover:!underline !font-medium" @click="markAllRead">全部已读</el-button>
              </div>
            </div>
          </template>
          <!-- Rolling Notification List -->
          <div class="flex-1 overflow-hidden relative bg-slate-50/50">
             <div class="absolute inset-0 overflow-y-auto custom-scroll p-6" ref="notificationContainer">
                <ul class="space-y-4">
                  <li v-for="msg in filteredMessages" :key="msg.id" @click="viewMessage(msg)" class="flex items-start gap-3 pb-3 border-b border-slate-100 last:border-0 animate-in fade-in slide-in-from-right-4 duration-500 cursor-pointer hover:bg-slate-100 p-2 rounded-lg transition-colors">
                    <div class="w-2 h-2 mt-1.5 rounded-full shrink-0" :class="[msg.type === 'SYSTEM' ? 'bg-red-500' : (msg.type === 'MENTION' ? 'bg-purple-500' : 'bg-blue-500'), !msg.read ? 'ring-2 ring-offset-1 ring-blue-200' : 'opacity-50']"></div>
                    <div class="flex-1 overflow-hidden" :class="{'opacity-60': msg.read}">
                      <div class="text-sm text-slate-800 flex items-center gap-2 mb-1">
                        <span v-if="msg.type === 'SYSTEM'" class="text-[10px] px-1.5 py-0.5 rounded bg-red-50 text-red-600 font-bold shrink-0">系统</span>
                        <span v-if="msg.type === 'MENTION'" class="text-[10px] px-1.5 py-0.5 rounded bg-purple-50 text-purple-600 font-bold shrink-0">提及</span>
                        <span class="truncate" :class="msg.read ? 'font-normal' : 'font-bold'">{{ msg.title || '无标题消息' }}</span>
                        <span v-if="!msg.read" class="w-1.5 h-1.5 rounded-full bg-red-500 ml-auto shrink-0"></span>
                      </div>
                      <div class="text-xs text-slate-500 line-clamp-2 leading-relaxed mb-1">{{ msg.content }}</div>
                      <div class="text-[10px] text-slate-400 flex justify-between w-full gap-4">
                          <span>{{ msg.targetLabel || '全体成员' }}</span>
                          <span>{{ msg.time }}</span>
                      </div>
                    </div>
                  </li>
                  <li v-if="filteredMessages.length === 0" class="text-center text-gray-400 text-sm py-4">
                    {{ showAllMessages ? '暂无消息记录' : '暂无今日新消息' }}
                  </li>
                </ul>
             </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Row 2: Projects, Todo, Announcements -->
    <el-row :gutter="20">
      <!-- 4. Ongoing Projects -->
      <el-col :span="8">
        <el-card class="shadow-sm h-96 flex flex-col">
          <template #header>
            <div class="flex justify-between items-center">
              <span class="font-bold text-lg">进行中的项目进展</span>
              <router-link to="/projects" class="text-sm text-blue-600 hover:underline font-medium">查看全部</router-link>
            </div>
          </template>
          <div class="flex-1 overflow-auto p-0">
            <div v-if="loadingProjects" class="h-full flex items-center justify-center text-gray-400 text-sm">
                加载中...
            </div>
            <ul v-else class="divide-y divide-slate-50">
                <li v-for="p in projectList" :key="p.id" class="p-4 hover:bg-slate-50 transition-colors group">
                    <router-link :to="`/projects/${p.id}`" class="block no-underline">
                        <div class="flex justify-between items-start mb-2">
                            <span class="font-bold text-slate-800 group-hover:text-blue-600 transition-colors line-clamp-1">{{ p.name }}</span>
                            <span class="text-xs px-2 py-0.5 rounded bg-blue-50 text-blue-600 font-medium whitespace-nowrap">{{ p.status || '进行中' }}</span>
                        </div>
                        <div class="flex justify-between items-center text-xs text-slate-500">
                            <span>负责人: {{ p.owner_name || '未分配' }}</span>
                            <span>进度: {{ p.progress || 0 }}%</span>
                        </div>
                        <div class="mt-2 w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                            <div class="bg-blue-500 h-1.5 rounded-full transition-all duration-500" :style="{ width: (p.progress || 0) + '%' }"></div>
                        </div>
                    </router-link>
                </li>
                <li v-if="projectList.length === 0" class="p-8 text-center text-gray-400 text-sm">
                    暂无进行中的项目
                </li>
            </ul>
          </div>
        </el-card>
      </el-col>

      <!-- 5. Todo List -->
      <el-col :span="8">
        <el-card class="shadow-sm h-96 flex flex-col">
          <template #header>
            <div class="flex justify-between items-center">
              <span class="font-bold text-lg">待办事项</span>
              <el-badge :value="3" class="item" type="danger">
                <el-button link class="!text-sm !text-blue-600 hover:!underline !font-medium">待办中心</el-button>
              </el-badge>
            </div>
          </template>
          <div class="flex-1 overflow-hidden flex flex-col">
            <el-tabs v-model="activeTab" class="flex-1 flex flex-col custom-tabs">
              <el-tab-pane label="待审批" name="approvals" class="h-full overflow-auto">
                <ul class="space-y-0 px-6 py-4">
                  <li v-for="item in approvalList" :key="item.id" class="flex justify-between items-center py-4 border-b border-slate-50 last:border-0 hover:bg-slate-50 transition-colors -mx-6 px-6">
                    <div>
                      <div class="text-sm font-bold text-slate-800">{{ item.title }}</div>
                      <div class="text-xs text-slate-400 mt-1">申请人: <span class="text-slate-600">{{ item.applicant }}</span></div>
                    </div>
                    <el-button size="small" type="primary" plain class="shadow-sm">审批</el-button>
                  </li>
                </ul>
              </el-tab-pane>
              <el-tab-pane label="待推进" name="tasks">
                <div class="h-full flex items-center justify-center text-slate-400 text-sm">暂无待推进事项</div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </el-card>
      </el-col>

      <!-- 6. Daily Reports Summary -->
      <el-col :span="8">
        <el-card class="shadow-sm h-96 flex flex-col bg-blue-50/30 border-blue-100">
          <template #header>
            <div class="flex justify-between items-center">
              <span class="font-bold text-lg text-blue-900">工作日报</span>
              <router-link to="/daily-reports" class="text-sm text-blue-600 hover:underline font-medium">查看全部</router-link>
            </div>
          </template>
          <div class="flex-1 overflow-auto p-0">
            <div v-if="loadingReports" class="h-full flex items-center justify-center text-gray-400 text-sm">
                加载中...
            </div>
            <div v-else class="space-y-4 p-6">
                <router-link 
                    v-for="report in dailyReports.slice(0, 2)" 
                    :key="report.id" 
                    :to="{ name: 'DailyReportList', query: { date: report.date, edit: 'true' } }"
                    class="block bg-white p-3 rounded-lg border border-blue-100 shadow-sm hover:shadow-md hover:border-blue-300 transition-all cursor-pointer no-underline"
                >
                  <div class="flex justify-between items-center mb-1">
                      <div class="text-xs text-blue-500 font-bold">{{ report.date }}</div>
                      <div class="text-xs px-1.5 py-0.5 rounded" :class="getStatusClass(report.status)">{{ getStatusLabel(report.status) }}</div>
                  </div>
                  <div class="text-sm font-bold text-slate-800 mb-1 line-clamp-1" v-if="report.title">
                      {{ report.title }}
                  </div>
                  <div class="text-sm text-slate-600 line-clamp-3 leading-relaxed whitespace-pre-wrap">
                    {{ report.polished_content || report.raw_content || '暂无内容' }}
                  </div>
                </router-link>
                <div v-if="dailyReports.length === 0" class="text-center text-gray-400 text-sm py-4">
                    暂无最近日报
                </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Publish Message Dialog -->
    <el-dialog v-model="showPublishModal" title="发布消息通知" width="500px">
        <el-form :model="publishForm" label-width="80px">
            <el-form-item label="发送对象">
                <el-select v-model="publishForm.target" placeholder="请选择发送对象" class="w-full">
                    <el-option label="全体成员" value="all" />
                    <el-option label="指定部门" value="dept_specific" />
                    <el-option label="指定用户" value="user_specific" />
                </el-select>
            </el-form-item>
            
            <el-form-item v-if="publishForm.target === 'dept_specific'" label="选择部门">
                <el-select v-model="publishForm.targetDepts" multiple placeholder="请选择部门" class="w-full">
                    <el-option v-for="dept in departmentOptions" :key="dept.id" :label="dept.name" :value="dept.id" />
                </el-select>
            </el-form-item>

            <el-form-item v-if="publishForm.target === 'user_specific'" label="选择用户">
                <el-select v-model="publishForm.targetUsers" multiple filterable placeholder="请选择用户" class="w-full">
                    <el-option v-for="u in userOptions" :key="u.id" :label="u.name" :value="u.id">
                        <span class="float-left">{{ u.name }}</span>
                        <span class="float-right text-gray-400 text-xs">{{ u.department }}</span>
                    </el-option>
                </el-select>
            </el-form-item>

            <el-form-item label="消息类型">
                <el-radio-group v-model="publishForm.type">
                    <el-radio label="normal">普通消息</el-radio>
                    <el-radio label="system">系统通知</el-radio>
                </el-radio-group>
            </el-form-item>
            <el-form-item label="消息标题">
                <el-input v-model="publishForm.title" placeholder="请输入消息标题" />
            </el-form-item>
            <el-form-item label="消息正文">
                <el-input v-model="publishForm.content" type="textarea" :rows="3" placeholder="请输入消息正文..." />
            </el-form-item>
        </el-form>
        <template #footer>
            <span class="dialog-footer">
                <el-button @click="showPublishModal = false">取消</el-button>
                <el-button type="primary" size="large" @click="publishMessage" class="px-6">发布</el-button>
            </span>
        </template>
    </el-dialog>

    <!-- Message Detail Dialog -->
    <el-dialog v-model="showMessageDetail" title="消息详情" width="500px">
        <div v-if="selectedMessage">
            <div class="flex items-center gap-2 mb-4">
                <span v-if="selectedMessage.type === 'SYSTEM'" class="px-2 py-0.5 rounded bg-red-100 text-red-700 text-xs font-bold">系统通知</span>
                <span v-else class="px-2 py-0.5 rounded bg-blue-100 text-blue-700 text-xs font-bold">普通消息</span>
                <span class="text-gray-400 text-xs">{{ selectedMessage.time }}</span>
            </div>
            <h3 class="text-lg font-bold text-gray-800 mb-4">{{ selectedMessage.title }}</h3>
            <div class="bg-gray-50 p-4 rounded-lg text-sm leading-relaxed text-gray-700 whitespace-pre-wrap border border-gray-100">
                {{ selectedMessage.content }}
            </div>
            <div class="mt-4 text-xs text-gray-400 text-right">
                发送给: {{ selectedMessage.targetLabel }}
            </div>
        </div>
        <template #footer>
            <span class="dialog-footer">
                <el-button @click="showMessageDetail = false">关闭</el-button>
            </span>
        </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, reactive, watch, nextTick } from 'vue';
import api from '../../api';
import { createIcons, icons } from 'lucide';
import { ElMessage } from 'element-plus';

const activeTab = ref('approvals');
const projectList = ref<any[]>([]);
const loadingProjects = ref(false);

// Daily Reports
const dailyReports = ref<any[]>([]);
const loadingReports = ref(false);

function getStatusLabel(status: string) {
    const map: Record<string, string> = { 'DRAFT': '草稿', 'SUBMITTED': '已提交', 'APPROVED': '已确认', 'REJECTED': '需修改' };
    return map[status] || status;
}

function getStatusClass(status: string) {
    const map: Record<string, string> = { 
        'DRAFT': 'bg-gray-100 text-gray-600', 
        'SUBMITTED': 'bg-blue-50 text-blue-600', 
        'APPROVED': 'bg-green-50 text-green-600', 
        'REJECTED': 'bg-red-50 text-red-600' 
    };
    return map[status] || 'bg-gray-100';
}

async function fetchDailyReports() {
    loadingReports.value = true;
    try {
        const res = await api.get('daily-reports/');
        console.log('Daily Reports fetched:', res.data);
        // Sort by date desc just in case
        const list = res.data.results || res.data;
        list.sort((a: any, b: any) => new Date(b.date).getTime() - new Date(a.date).getTime());
        dailyReports.value = list;
    } catch (e) {
        console.error("Failed to fetch daily reports", e);
    } finally {
        loadingReports.value = false;
    }
}

// Messaging System Logic
const showPublishModal = ref(false);
const showMessageDetail = ref(false);
const selectedMessage = ref<any>(null);

const publishForm = reactive({
    target: 'all',
    targetDepts: [] as number[],
    targetUsers: [] as number[],
    type: 'normal',
    title: '',
    content: ''
});

const userOptions = ref<any[]>([]);
const departmentOptions = ref<any[]>([]);
const showAllMessages = ref(false);
const messages = ref<any[]>([]);

// Fetch Users and Departments when specific targets selected
watch(() => publishForm.target, (newVal) => {
    if (newVal === 'user_specific' && userOptions.value.length === 0) {
        fetchUsers();
    }
    if (newVal === 'dept_specific' && departmentOptions.value.length === 0) {
        fetchDepartments();
    }
});

// Watch for data changes to refresh icons
watch([projectList, dailyReports], async () => {
    await nextTick();
    createIcons({ icons });
});

async function fetchNotifications() {
    try {
        const res = await api.get('notifications/');
        const list = res.data.results || res.data;
        messages.value = list.map((n: any) => ({
            id: n.id,
            // 兼容多种类型显示：SYSTEM, NORMAL, MENTION 均在列表中展示
            type: n.type, 
            title: n.title,
            content: n.content,
            time: new Date(n.created_at).toLocaleString('zh-CN', { hour12: false }),
            targetLabel: n.sender_name || '系统', 
            read: n.is_read
        }));
    } catch (e) {
        console.error("Failed to fetch notifications", e);
    }
}

async function fetchUsers() {
    try {
        // Try simple list endpoint first as it is more likely to be accessible to regular users
        const res = await api.get('users/simple/');
        userOptions.value = (res.data.results || res.data).map((u: any) => ({
            id: u.id,
            name: u.name || u.username,
            department: u.department || '未分配'
        }));
    } catch (e) {
        console.error("Failed to fetch users from simple list, trying admin endpoint", e);
        try {
            const res = await api.get('admin/users/');
            userOptions.value = (res.data.results || res.data).map((u: any) => ({
                id: u.id,
                name: u.name || u.username,
                department: u.department || '未分配'
            }));
        } catch (e2) {
            console.error("Failed to fetch users from admin endpoint", e2);
            userOptions.value = [];
        }
    }
}

async function fetchDepartments() {
    try {
        // Try admin endpoint
        const res = await api.get('departments/'); // Assuming standard viewset
        departmentOptions.value = (res.data.results || res.data).map((d: any) => ({
            id: d.id,
            name: d.name
        }));
    } catch (e) {
         console.error("Failed to fetch departments", e);
         departmentOptions.value = [];
    }
}

async function viewMessage(msg: any) {
    selectedMessage.value = msg;
    showMessageDetail.value = true;
    // Mark as read if not already
    if (!msg.read) {
        try {
            await api.post(`notifications/${msg.id}/mark_read/`);
            msg.read = true;
        } catch (e) {
            console.error("Failed to mark notification as read", e);
        }
    }
}

const filteredMessages = computed(() => {
    // If showAllMessages is true, return all
    if (showAllMessages.value) return messages.value;

    // Filter: Today's messages OR Unread messages
    return messages.value.filter(m => {
        // Parse time string back to date object for comparison is tricky with locale string
        // So we rely on "read" status primarily for the default view
        // Or strictly check date if format is consistent
        return !m.read; 
    });
});

async function markAllRead() {
    try {
        await api.post('notifications/mark_all_read/');
        messages.value.forEach(m => m.read = true);
    } catch (e) {
        console.error("Failed to mark all notifications as read", e);
    }
}

// Remove local storage loading/saving for messages since we use backend now
function loadMessages() {
    fetchNotifications();
}

async function publishMessage() {
    if (!publishForm.title || !publishForm.content) {
        ElMessage.warning('请填写标题和正文');
        return;
    }
    
    try {
        const payload = {
            target: publishForm.target,
            targetDepts: publishForm.targetDepts,
            targetUsers: publishForm.targetUsers,
            type: publishForm.type,
            title: publishForm.title,
            content: publishForm.content
        };
        
        await api.post('notifications/', payload);
        ElMessage.success('发布成功');
        showPublishModal.value = false;
        
        // Reset form
        publishForm.title = '';
        publishForm.content = '';
        
        // Refresh notifications
        fetchNotifications();
    } catch (e: any) {
        console.error("Failed to publish message", e);
        ElMessage.error(e.response?.data?.error || '发布失败');
    }
}


// Mock Data for Todo List (Refactored from hardcoded HTML)
const approvalList = ref<any[]>([]);

// Refresh icons after approvals list changes
watch([approvalList], async () => {
    await nextTick();
    createIcons({ icons });
});

async function fetchApprovals() {
    try {
        const res = await api.get('approvals/');
        const list = res.data.results || res.data;
        approvalList.value = list.map((a: any) => ({
            id: a.id,
            title: a.reason || '无标题申请',
            applicant: a.applicant_name
        }));
    } catch (e) {
        console.error("Failed to fetch approvals", e);
    }
}

const formatPercentage = (percentage: number) => {
  return `${percentage}%`;
};

async function fetchProjects() {
    loadingProjects.value = true;
    try {
        const res = await api.get('projects/');
        const rawList = Array.isArray(res.data) ? res.data : (res.data.results || []);
        projectList.value = rawList.slice(0, 5).map((p: any) => ({
            id: p.id,
            name: p.name,
            owner_name: p.owner_name,
            status: p.status_display || p.status || '进行中', 
            progress: typeof p.progress === 'number' ? p.progress : 0
        }));
    } catch (e) {
        console.error("Failed to fetch projects", e);
    } finally {
        loadingProjects.value = false;
    }
}

onMounted(() => {
    fetchProjects();
    fetchDailyReports();
    fetchApprovals();
    loadMessages();
    // Initialize icons
    createIcons({ icons });
});
</script>

<style scoped>
:deep(.el-card__header) {
  padding: 15px 20px;
  border-bottom: 1px solid #f1f5f9;
}
:deep(.el-card__body) {
  padding: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
}
/* Fix tab header padding */
:deep(.custom-tabs .el-tabs__header) {
  padding-left: 24px; /* Match content padding */
  margin-bottom: 0;
}
:deep(.custom-tabs .el-tabs__nav-wrap::after) {
  height: 1px;
}
.custom-scroll::-webkit-scrollbar { width: 4px; }
.custom-scroll::-webkit-scrollbar-track { background: transparent; }
.custom-scroll::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
</style>
