<template>
  <div class="h-screen w-screen bg-white overflow-hidden flex flex-col">
     <!-- Simple Header -->
     <div class="h-14 border-b border-gray-200 flex items-center justify-between px-6 bg-white shrink-0 z-50">
        <div class="font-bold text-lg text-gray-800 flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-blue-600"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            项目推进时间轴
        </div>
        <button @click="close" class="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm font-medium transition-colors">关闭窗口</button>
     </div>
     <div class="flex-1 overflow-hidden relative">
        <ProjectTimeline />
     </div>
  </div>
</template>

<script setup lang="ts">
import ProjectTimeline from './ProjectTimeline.vue';

function close() { 
    window.close(); 
}
</script>