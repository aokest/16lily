<template>
  <div class="h-screen w-screen flex bg-background font-sans">
    <!-- Modern Sidebar -->
    <aside class="w-[260px] bg-gradient-to-b from-gray-900 to-gray-800 text-white flex flex-col shrink-0 shadow-2xl transition-all duration-300 z-50">
      <!-- Brand Logo Area -->
      <div class="h-[70px] flex items-center px-6 bg-gradient-to-r from-pomegranate-600 to-pomegranate-700 border-b-2 border-gold-500 shadow-md relative overflow-hidden group cursor-pointer" @click="router.push('/')">
        <div class="absolute inset-0 bg-white/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
        <div class="flex items-center gap-3 relative z-10">
          <div class="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center border border-white/20 shadow-inner group-hover:scale-110 transition-transform duration-300">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5 text-gold-400"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
          </div>
          <div class="flex flex-col">
            <span class="font-black text-lg tracking-wide text-white leading-none">石榴粒粒</span>
            <span class="text-[10px] font-bold text-gold-400 tracking-[0.2em] uppercase mt-0.5">Intelligence</span>
          </div>
        </div>
      </div>
      
      <!-- Navigation Menu -->
      <nav class="flex-1 overflow-y-auto py-6 px-3 space-y-1 custom-scrollbar">
        
        <div v-for="(group, gIndex) in menuGroups" :key="gIndex" class="mb-6">
          <!-- Group Title Removed as per request -->
          
          <div v-for="item in group.items" :key="item.path">
            <!-- Submenu Parent -->
            <div v-if="item.children" class="space-y-1">
              <button 
                @click="toggleSubmenu(item.path)"
                class="w-full flex items-center justify-between px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 group relative overflow-hidden"
                :class="isSubmenuOpen(item.path) ? 'text-white bg-white/5' : 'text-gray-400 hover:text-white hover:bg-white/5'"
              >
                <div class="flex items-center gap-3">
                  <component :is="item.icon" class="w-5 h-5 transition-colors duration-200" :class="isSubmenuOpen(item.path) ? 'text-gold-400' : 'text-gray-500 group-hover:text-gold-400'"></component>
                  <span>{{ item.label }}</span>
                </div>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4 transition-transform duration-200" :class="isSubmenuOpen(item.path) ? 'rotate-90 text-white' : 'text-gray-600'"><path d="m9 18 6-6-6-6"/></svg>
              </button>
              
              <!-- Submenu Children -->
              <div v-show="isSubmenuOpen(item.path)" class="pl-4 space-y-1 overflow-hidden transition-all duration-300">
                <router-link 
                  v-for="child in item.children" 
                  :key="child.path"
                  :to="child.path"
                  class="flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm transition-all duration-200 border-l-2 border-transparent relative group"
                  :class="isActive(child.path) ? 'bg-gradient-to-r from-pomegranate-500/20 to-transparent text-white border-pomegranate-500 font-bold shadow-sm' : 'text-gray-400 hover:text-white hover:bg-white/5'"
                >
                  <span class="w-1.5 h-1.5 rounded-full transition-all duration-200" :class="isActive(child.path) ? 'bg-pomegranate-500 scale-125' : 'bg-gray-600 group-hover:bg-gray-400'"></span>
                  {{ child.label }}
                  <div v-if="isActive(child.path)" class="absolute right-3 w-1.5 h-1.5 rounded-full bg-gold-400 animate-pulse"></div>
                </router-link>
              </div>
            </div>

            <!-- Single Link -->
            <router-link 
              v-else
              :to="item.path"
              class="flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 group relative overflow-hidden"
              :class="isActive(item.path) ? 'bg-gradient-to-r from-pomegranate-600 to-pomegranate-500 text-white shadow-lg shadow-pomegranate-900/20' : 'text-gray-400 hover:text-white hover:bg-white/5'"
            >
              <component :is="item.icon" class="w-5 h-5 transition-colors duration-200" :class="isActive(item.path) ? 'text-white' : 'text-gray-500 group-hover:text-gold-400'"></component>
              <span>{{ item.label }}</span>
              <div v-if="isActive(item.path)" class="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            </router-link>
          </div>
        </div>

      </nav>

      <!-- User Profile Bottom -->
      <div class="p-4 border-t border-gray-800 bg-gray-900/50 backdrop-blur-sm">
        <div class="flex items-center gap-3 p-2 rounded-xl hover:bg-white/5 cursor-pointer transition-colors group">
          <div class="w-10 h-10 rounded-full bg-gradient-to-br from-pomegranate-400 to-pomegranate-600 flex items-center justify-center text-white font-bold shadow-lg ring-2 ring-gray-800 group-hover:ring-gold-500/50 transition-all">
            A
          </div>
          <div class="flex-1 min-w-0">
            <div class="text-sm font-bold text-white truncate group-hover:text-gold-400 transition-colors">Admin User</div>
            <div class="text-xs text-gray-500 truncate">System Administrator</div>
          </div>
          <button @click="logout" class="text-gray-500 hover:text-white transition-colors" title="Logout">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
          </button>
        </div>
      </div>
    </aside>

    <!-- Main Content Area -->
    <main class="flex-1 overflow-hidden flex flex-col relative">
      <!-- Top Header -->
      <header class="h-[70px] bg-white border-b border-gray-100 px-8 flex items-center justify-between shrink-0 shadow-sm z-40">
        <div class="flex items-center gap-4">
          <h2 class="text-xl font-extrabold text-graphite tracking-tight">{{ currentRouteName }}</h2>
          <div class="h-6 w-px bg-gray-200 mx-2"></div>
          <div class="text-sm text-gray-400 flex items-center gap-2">
            <span class="hover:text-pomegranate-500 cursor-pointer transition-colors">首页</span>
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-gray-300"><path d="m9 18 6-6-6-6"/></svg>
            <span class="text-gray-600 font-medium">{{ currentRouteName }}</span>
          </div>
        </div>
        
        <div class="flex items-center gap-4">
          <!-- Notification Bell -->
          <div class="relative z-50">
            <button @click="toggleNotifications" class="p-2 text-gray-400 hover:text-pomegranate-500 hover:bg-pomegranate-50 rounded-full transition-all relative">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>
              <span v-if="unreadCount > 0" class="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></span>
            </button>

            <!-- Dropdown -->
            <div v-if="showNotificationDropdown" class="absolute top-full right-0 mt-2 w-80 bg-white rounded-xl shadow-2xl border border-gray-100 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200">
                <div class="px-4 py-3 border-b border-gray-50 flex justify-between items-center bg-gray-50/50">
                    <span class="text-sm font-bold text-gray-700">通知消息</span>
                    <button @click="markAllRead" class="text-xs text-blue-600 hover:underline">全部已读</button>
                </div>
                <div class="max-h-[400px] overflow-y-auto custom-scrollbar">
                    <ul class="divide-y divide-gray-50">
                        <li v-for="msg in recentMessages" :key="msg.id" class="p-3 hover:bg-gray-50 cursor-pointer transition-colors flex gap-3 group relative">
                            <div @click="handleMessageClick(msg)" class="flex-1 flex gap-3 overflow-hidden">
                                <div class="w-2 h-2 mt-1.5 rounded-full shrink-0 transition-colors" :class="msg.read ? 'bg-gray-200' : (msg.type === 'system' ? 'bg-red-500' : 'bg-blue-500')"></div>
                                <div class="flex-1 overflow-hidden">
                                    <div class="flex justify-between items-start mb-1">
                                        <span class="text-xs font-bold truncate pr-6" :class="msg.read ? 'text-gray-500 font-normal' : 'text-gray-800'">{{ msg.title }}</span>
                                        <span class="text-[10px] text-gray-400 whitespace-nowrap">{{ formatTime(msg.time || msg.created_at) }}</span>
                                    </div>
                                    <div class="text-xs text-gray-500 line-clamp-2" :class="{'opacity-60': msg.read}">{{ msg.content }}</div>
                                </div>
                            </div>
                            <!-- 删除按钮 -->
                            <button @click.stop="deleteMessage(msg.id)" class="absolute right-2 top-3 p-1 text-gray-300 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all">
                                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/><line x1="10" x2="10" y1="11" y2="17"/><line x1="14" x2="14" y1="11" y2="17"/></svg>
                            </button>
                        </li>
                        <li v-if="recentMessages.length === 0" class="p-4 text-center text-xs text-gray-400">暂无消息</li>
                    </ul>
                </div>
                <div class="p-2 border-t border-gray-50 bg-gray-50 text-center">
                    <button @click="goToCenter" class="text-xs font-bold text-pomegranate-600 hover:text-pomegranate-700 flex items-center justify-center gap-1 w-full py-1">
                        查看更多通知消息
                        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
                    </button>
                </div>
            </div>
            
            <!-- Backdrop -->
            <div v-if="showNotificationDropdown" class="fixed inset-0 z-[-1]" @click="showNotificationDropdown = false"></div>
          </div>
          
          <div class="flex items-center gap-2">
            <button class="px-4 py-2 text-sm font-bold text-gray-600 bg-gray-50 hover:bg-gray-100 rounded-lg border border-gray-200 transition-all flex items-center gap-2" @click="openWindow('/')">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><line x1="3" x2="21" y1="9" y2="9"/><path d="m9 16 2 2 4-4"/></svg>
              战报大屏
            </button>
            <button class="px-4 py-2 text-sm font-bold text-white rounded-lg shadow-md shadow-red-200 transition-all flex items-center gap-2" style="background-color: #D64045;" @click="router.push('/crm')">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
              CRM工作台
            </button>
          </div>
        </div>
      </header>

      <!-- Content -->
      <section class="flex-1 overflow-y-auto p-8 bg-background relative scroll-smooth">
        <!-- Background Decoration -->
        <div class="absolute top-0 left-0 w-full h-64 bg-gradient-to-b from-white to-transparent pointer-events-none"></div>
        <div class="relative z-10 max-w-7xl mx-auto">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import api from '../api';
import { ElMessage } from 'element-plus';

const router = useRouter();
const route = useRoute();
const openSubmenus = ref<string[]>(['business', 'customer', 'system']);

interface MenuItem {
  label: string;
  path: string;
  icon?: string | any;
  children?: MenuItem[];
}

interface MenuGroup {
  title: string;
  items: MenuItem[];
}

const menuGroups: MenuGroup[] = [
  {
    title: '个人中心',
    items: [
      { label: '个人中心', path: '/home', icon: 'svg-user' },
      { label: '工作日报', path: '/daily-reports', icon: 'svg-calendar' },
      { label: 'AI中枢', path: '/ai/chat', icon: 'svg-sparkles' },
    ]
  },
  {
    title: '业务管理',
    items: [
      { 
        label: '经营管理', 
        path: 'business', 
        icon: 'svg-briefcase',
        children: [
          { label: '业绩报表', path: '/reports/performance' },
          { label: '项目管理', path: '/projects' },
          { label: '商机列表', path: '/crm/opportunities' },
          { label: '审批中心', path: '/crm/approvals' },
          { label: '社媒管理', path: '/social/accounts' },
        ]
      },
      {
        label: '客户管理',
        path: 'customer',
        icon: 'svg-users',
        children: [
          { label: '客户列表', path: '/crm/customers' },
          { label: '联系人列表', path: '/crm/contacts' },
        ]
      }
    ]
  },
  {
    title: '系统设置',
    items: [
      {
        label: '系统配置',
        path: 'system',
        icon: 'svg-settings',
        children: [
          { label: '用户管理', path: '/settings/users' },
          { label: '部门管理', path: '/settings/departments' },
          { label: '岗位管理', path: '/settings/jobs' },
          { label: '系统日志', path: '/settings/logs' },
          { label: '数据管理', path: '/settings/data' },
          { label: 'AI模型配置', path: '/settings/ai' },
          { label: '数据迁移', path: '/admin/migrate' },
        ]
      }
    ]
  }
];

// Helper components for icons (You can extract these to separate files later)
const IconMap: Record<string, any> = {
  'svg-user': { template: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>' },
  'svg-calendar': { template: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>' },
  'svg-sparkles': { template: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/><path d="M5 3v4"/><path d="M9 3v4"/><path d="M3 5h4"/><path d="M3 9h4"/></svg>' },
  'svg-briefcase': { template: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="14" x="2" y="7" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>' },
  'svg-users': { template: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>' },
  'svg-settings': { template: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.38a2 2 0 0 0-.73-2.73l-.15-.1a2 2 0 0 1-1-1.72v-.51a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>' },
};

// Register components locally (hacky but works for script setup without external files)
// In a real app, these should be separate files.
menuGroups.forEach(g => g.items.forEach(i => {
  if (typeof i.icon === 'string' && IconMap[i.icon]) {
    i.icon = IconMap[i.icon];
  }
}));

const currentRouteName = computed(() => {
  const map: Record<string, string> = {
    '/home': '个人中心',
    '/daily-reports': '工作日报',
    '/ai/chat': 'AI中枢',
    '/reports/performance': '业绩报表',
    '/projects': '项目管理',
    '/crm/opportunities': '商机列表',
    '/crm/approvals': '审批中心',
    '/crm/customers': '客户列表',
    '/crm/contacts': '联系人列表',
    '/social/accounts': '社媒账号列表',
    '/settings/users': '用户管理',
    '/settings/logs': '系统日志',
    '/settings/data': '数据管理',
    '/settings/ai': 'AI模型配置',
    '/admin/migrate': '数据迁移'
  };
  return map[route.path] || 'CRM工作台';
});

function toggleSubmenu(path: string) {
  const index = openSubmenus.value.indexOf(path);
  if (index === -1) {
    openSubmenus.value.push(path);
  } else {
    openSubmenus.value.splice(index, 1);
  }
}

function isSubmenuOpen(path: string) {
  return openSubmenus.value.includes(path);
}

function isActive(path: string) {
  if (path === '/admin') return false;
  return route.path === path || route.path.startsWith(path + '/');
}

function openWindow(url: string) {
    window.open(url, '_blank');
}

// Logout function
const logout = () => {
  localStorage.removeItem('auth_token');
  router.push('/login');
};

// Notification System Logic
const showNotificationDropdown = ref(false);
const messages = ref<any[]>([]);

const unreadCount = computed(() => messages.value.filter(m => !m.read).length);
const recentMessages = computed(() => messages.value.slice(0, 10));

async function loadMessages() {
  try {
    const res = await api.get('/notifications/');
    messages.value = res.data.results || res.data;
  } catch (e) {
    console.error("Failed to load notifications:", e);
  }
}

function toggleNotifications() {
  showNotificationDropdown.value = !showNotificationDropdown.value;
  if (showNotificationDropdown.value) {
    loadMessages();
  }
}

async function markAllRead() {
    try {
        await api.post('/notifications/mark_all_read/');
        messages.value.forEach(m => m.read = true);
        ElMessage.success('全部标记为已读');
    } catch (e) {
        ElMessage.error('操作失败');
    }
}

async function handleMessageClick(msg: any) {
    if (!msg.read) {
        try {
            await api.post(`/notifications/${msg.id}/mark_read/`);
            msg.read = true;
        } catch (e) {
            console.error("Failed to mark message as read:", e);
        }
    }
}

async function deleteMessage(id: number) {
    try {
        await api.delete(`/notifications/${id}/`);
        messages.value = messages.value.filter(m => m.id !== id);
        ElMessage.success('删除成功');
    } catch (e) {
        ElMessage.error('删除失败');
    }
}

function goToCenter() {
    showNotificationDropdown.value = false;
    router.push('/home');
}

function formatTime(t: string) {
    if (!t) return '';
    // Tries to slice "YYYY-MM-DD HH:MM" to "MM-DD HH:MM"
    return t.length > 10 ? t.slice(5, 16) : t;
}

onMounted(async () => {
    // Auto-Login Check for Demo/Dev
    const token = localStorage.getItem('auth_token');
    if (!token) {
        try {
            // Try default admin credentials
            const res = await fetch('/api/api-token-auth/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: 'admin', password: 'admin123' })
            });
            if (res.ok) {
                const data = await res.json();
                localStorage.setItem('auth_token', data.token);
                // Force reload or just continue (axios interceptor reads from storage)
                window.location.reload(); 
            } else {
                console.warn('Auto-login failed. Please login manually.');
            }
        } catch (e) {
            console.error('Auto-login error', e);
        }
    }

    loadMessages();
});

</script>

<style scoped>
/* Custom Scrollbar for Sidebar */
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>