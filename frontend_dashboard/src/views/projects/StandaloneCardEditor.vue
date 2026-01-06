<template>
  <div class="w-screen h-screen bg-white flex flex-col">
    <div v-if="loading" class="flex items-center justify-center h-full">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
    </div>
    <div v-else-if="error" class="flex flex-col items-center justify-center h-full text-red-600 gap-4">
      <div class="text-xl font-bold">{{ error }}</div>
      <button @click="closeWindow" class="px-4 py-2 bg-gray-100 rounded hover:bg-gray-200">关闭窗口</button>
    </div>
    <CardEditor 
      v-else
      :visible="true" 
      mode="page"
      :card-data="cardData"
      :project-code="projectCode"
      :has-prev="hasPrev"
      :has-next="hasNext"
      @save="handleSave"
      @prev="handlePrev"
      @next="handleNext"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../../api';
import CardEditor from '../../components/CardEditor.vue';

const route = useRoute();
const router = useRouter();
const cardId = ref(Number(route.params.id));
const loading = ref(true);
const error = ref('');
const cardData = ref<any>(null);
const projectCode = ref('');

// Pagination State
const projectCardIds = ref<number[]>([]);
const currentIndex = computed(() => projectCardIds.value.indexOf(cardId.value));
const hasPrev = computed(() => currentIndex.value > 0);
const hasNext = computed(() => currentIndex.value >= 0 && currentIndex.value < projectCardIds.value.length - 1);

function closeWindow() {
    window.close();
}

function handlePrev() {
    if (hasPrev.value) {
        const prevId = projectCardIds.value[currentIndex.value - 1];
        router.push(`/standalone/card/${prevId}`);
    }
}

function handleNext() {
    if (hasNext.value) {
        const nextId = projectCardIds.value[currentIndex.value + 1];
        router.push(`/standalone/card/${nextId}`);
    }
}

// Watch for route changes to reload data
watch(() => route.params.id, (newId) => {
    if (newId) {
        cardId.value = Number(newId);
        loadData();
    }
});

async function loadData() {
  loading.value = true;
  try {
    const res = await api.get(`/project-cards/${cardId.value}/`);
    cardData.value = res.data;
    
    // Fetch project info to get code and sibling cards
    if (cardData.value.project) {
        try {
            const pRes = await api.get(`/projects/${cardData.value.project}/`);
            projectCode.value = pRes.data.code;
            
            // Fetch all card IDs for this project for pagination
            // Optimize: Only fetch IDs if not already fetched or if project changed
            if (projectCardIds.value.length === 0) {
                const cRes = await api.get(`/project-cards/`, { params: { project: cardData.value.project } });
                const cards = Array.isArray(cRes.data) ? cRes.data : (cRes.data.results || []);
                // Sort by order if available, else by ID
                projectCardIds.value = cards
                    .sort((a: any, b: any) => (a.order - b.order) || (a.id - b.id))
                    .map((c: any) => c.id);
            }
        } catch(e) {
            console.warn("Failed to fetch project info", e);
        }
    }
  } catch (e) {
    console.error(e);
    error.value = "加载卡片失败，请检查链接或权限";
  } finally {
    loading.value = false;
  }
}

async function handleSave(payload: any) {
  try {
    await api.patch(`/project-cards/${cardId.value}/`, payload);
    alert("保存成功");
    // Reload data to ensure consistency
    await loadData();
  } catch (e) {
    console.error(e);
    alert("保存失败");
  }
}

onMounted(() => {
  loadData();
});
</script>