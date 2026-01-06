<template>
  <div class="min-h-screen flex flex-col bg-[#f8fafc] font-sans">
    <!-- Navbar -->
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center gap-4">
            <button @click="router.back()" class="text-gray-500 hover:text-gray-900 flex items-center gap-1" title="返回">
              <i data-lucide="arrow-left" class="w-5 h-5"></i> 返回
            </button>
            <div class="h-6 w-px bg-gray-200"></div>
            <div class="font-bold text-xl text-gray-900">全局项目推进表</div>
          </div>
        </div>
      </div>
    </nav>

    <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div v-if="loading" class="text-center py-12 text-gray-500">加载中...</div>
        
        <div v-else class="space-y-8">
            <div v-for="project in projects" :key="project.id" class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div class="flex justify-between items-center mb-6 border-b border-gray-100 pb-4">
                    <div>
                        <h3 class="font-bold text-lg text-gray-900 flex items-center gap-2">
                            <span class="text-sm font-mono text-gray-400 bg-gray-100 px-2 py-0.5 rounded">{{ project.code }}</span>
                            {{ project.name }}
                        </h3>
                        <div class="text-xs text-gray-500 mt-1">
                            负责人: {{ project.owner_name }} | 进度: {{ project.progress }}%
                        </div>
                    </div>
                    <button @click="router.push(`/projects/${project.id}`)" class="text-blue-600 hover:text-blue-800 text-sm font-medium">
                        进入看板 <i data-lucide="arrow-right" class="w-4 h-4 inline"></i>
                    </button>
                </div>
                
                <!-- Timeline Scroll Area -->
                <div class="overflow-x-auto pb-4 custom-scroll">
                    <div class="flex gap-4 min-w-max px-2">
                        <div v-if="!project.cards || project.cards.length === 0" class="text-sm text-gray-400 italic p-4">
                            暂无启用卡片
                        </div>
                        
                        <div v-for="card in project.cards" :key="card.id" class="w-64 flex-shrink-0 bg-gray-50 rounded-lg p-3 border border-gray-100 relative group">
                            <!-- Status Line -->
                            <div class="absolute top-0 left-0 w-full h-1 rounded-t-lg"
                                :class="{
                                    'bg-gray-300': card.status === 'TODO',
                                    'bg-blue-500': card.status === 'DOING',
                                    'bg-green-500': card.status === 'DONE',
                                    'bg-red-500': card.status === 'BLOCKED'
                                }"
                            ></div>
                            
                            <div class="mt-2">
                                <div class="flex justify-between items-start">
                                    <h5 class="font-bold text-sm text-gray-900 line-clamp-1" :title="card.title">{{ card.title }}</h5>
                                </div>
                                <div class="text-xs text-gray-500 mt-1 mb-2">
                                    {{ card.start_date || 'TBD' }} ~ {{ card.deadline || 'TBD' }}
                                </div>
                                <div class="flex items-center gap-2 text-[10px] text-gray-400">
                                    <span :class="{
                                        'text-gray-600': card.status === 'TODO',
                                        'text-blue-600': card.status === 'DOING',
                                        'text-green-600': card.status === 'DONE',
                                        'text-red-600': card.status === 'BLOCKED'
                                    }" class="font-medium uppercase">{{ card.status }}</span>
                                    <span>•</span>
                                    <span>{{ card.progress }}%</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { createIcons, icons } from 'lucide';
import api from '../../api';

const router = useRouter();
const projects = ref<any[]>([]);
const loading = ref(true);

async function loadData() {
    loading.value = true;
    try {
        // 1. Fetch all projects
        const pRes = await api.get('projects/');
        const allProjects = pRes.data.results || [];
        
        // 2. Fetch all active cards (optimized: fetch all active cards in one go if API allows filtering by multiple projects, or fetch all and filter locally)
        // Since we don't have a complex backend filter for "cards in these projects", we'll fetch all active cards.
        // Assuming the dataset isn't massive for now.
        const cRes = await api.get('project-cards/', { params: { is_active: true, limit: 1000 } });
        const allCards = cRes.data.results || [];
        
        // 3. Map cards to projects
        projects.value = allProjects.map((p:any) => {
            const pCards = allCards.filter((c:any) => c.project === p.id);
            // Sort cards by date
            pCards.sort((a:any, b:any) => {
                 const dateA = a.start_date || a.created_at;
                 const dateB = b.start_date || b.created_at;
                 return new Date(dateA).getTime() - new Date(dateB).getTime();
            });
            return { ...p, cards: pCards };
        });

        await nextTick();
        createIcons({ icons });
    } catch (e) {
        console.error("Failed to load global timeline", e);
    } finally {
        loading.value = false;
    }
}

onMounted(() => {
    loadData();
});
</script>

<style scoped>
.custom-scroll::-webkit-scrollbar { height: 6px; }
.custom-scroll::-webkit-scrollbar-track { background: #f1f1f1; }
.custom-scroll::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
</style>