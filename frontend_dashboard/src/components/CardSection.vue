<template>
  <div class="flex flex-col gap-2 h-full">
    <h3 class="font-bold text-lg border-b pb-1 flex items-center gap-2" :style="{ borderColor: styles.borderColor, borderBottomWidth: (styles.borderWidth ?? 2) + 'px' }">
      <span class="w-2 h-2 rounded-full bg-black" :style="{ backgroundColor: styles.borderColor }"></span>
      {{ title }}
    </h3>
    <div 
      class="whitespace-pre-wrap flex-1"
      :style="{ fontSize: (fontSize || 14) + 'px', lineHeight: (lineHeight || 1.5) }"
    >
      {{ content || '暂无内容...' }}
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string;
  content: string;
  fontSize?: number;
  lineHeight?: number;
  styles: {
    borderColor: string;
    textColor: string;
    backgroundColor?: string;
    borderWidth?: number;
  };
}>();
</script>
