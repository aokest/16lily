<template>
  <div v-if="visible" :class="rootClasses" @click.self="handleOverlayClick">
    <div :class="containerClasses">
      <!-- Global Toolbar -->
      <div class="h-14 border-b border-gray-200 flex items-center justify-between px-4 bg-gray-50 flex-shrink-0 z-50">
          <div class="flex items-center gap-3">
             <button @click="close" class="flex items-center gap-1 text-gray-500 hover:text-gray-800 px-2 py-1 rounded hover:bg-gray-200 transition-colors cursor-pointer" :title="mode==='modal' ? '返回 (Esc)' : '关闭窗口'">
                <i data-lucide="arrow-left" class="w-5 h-5"></i>
                <span class="text-sm font-bold">{{ mode==='modal' ? '返回' : '关闭' }}</span>
             </button>
             <div class="h-6 w-px bg-gray-300"></div>
            <!-- Theme Switcher (Click Toggle via Teleport to body) -->
            <div class="relative z-50">
               <button ref="themeBtnRef" @click="toggleThemeMenu" class="flex items-center gap-1 px-2 py-1 rounded hover:bg-gray-200 text-gray-600 text-sm transition-colors" :class="{'bg-gray-200': showThemeMenu}" title="设置卡片样式">
                   <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4"><circle cx="13.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="10.5" r="2.5"/><circle cx="8.5" cy="7.5" r="2.5"/><circle cx="6.5" cy="12.5" r="2.5"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"/></svg>
                   <span>主题</span>
               </button>
               <Teleport to="body">
                 <div v-if="showThemeMenu" class="fixed inset-0 z-[999]" @click="showThemeMenu = false"></div>
                 <div v-if="showThemeMenu" class="fixed z-[1000] w-48 bg-white rounded-lg shadow-xl border border-gray-200 p-2 animate-in fade-in slide-in-from-top-2 duration-200" :style="menuStyle">
                     <div class="text-xs font-bold text-gray-400 px-2 py-1 mb-1">选择配色风格</div>
                     <button v-for="t in themes" :key="t.name" @click="selectTheme(t)" class="w-full text-left px-2 py-1.5 text-sm hover:bg-gray-50 rounded flex items-center gap-2 transition-colors">
                         <span class="w-3 h-3 rounded-full border border-gray-200 shadow-sm" :style="{ background: t.backgroundColor === '#ffffff' ? t.textColor : t.backgroundColor }"></span>
                         {{ t.name }}
                     </button>
                     <div class="border-t my-1"></div>
                     <div class="px-2 py-1">
                         <label class="text-xs text-gray-500 block mb-1">自定义背景色</label>
                         <input type="color" v-model="currentTheme.backgroundColor" class="w-full h-8 cursor-pointer rounded border border-gray-200 p-0.5">
                     </div>
                 </div>
               </Teleport>
            </div>
             
            <div class="h-6 w-px bg-gray-300"></div>
            <!-- Style Switcher -->
            <div class="relative z-50">
               <button ref="styleBtnRef" @click="toggleStyleMenu" class="flex items-center gap-1 px-2 py-1 rounded hover:bg-gray-200 text-gray-600 text-sm transition-colors" :class="{'bg-gray-200': showStyleMenu}" title="编辑卡片样式">
                   <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4"><path d="M12 20h9"/><path d="M16.5 3.5 12 8l-3 1 1-3 4.5-4.5a2.12 2.12 0 1 1 3 3Z"/><path d="M19 5 15 9"/><path d="m3 21 3-3"/></svg>
                   <span>样式</span>
               </button>
               <Teleport to="body">
                 <div v-if="showStyleMenu" class="fixed inset-0 z-[999]" @click="showStyleMenu = false"></div>
                 <div v-if="showStyleMenu" class="fixed z-[1000] w-64 bg-white rounded-lg shadow-xl border border-gray-200 p-3 animate-in fade-in slide-in-from-top-2 duration-200" :style="styleMenuStyle">
                    <div class="text-xs font-bold text-gray-400 px-1 py-1 mb-2">样式参数</div>
                    <div class="space-y-3">
                      <div>
                        <label class="text-xs text-gray-500">正文字号: {{ cardConfig.fontSize }}px</label>
                        <input type="range" min="12" max="20" step="1" v-model.number="cardConfig.fontSize" class="w-full" />
                      </div>
                      <div>
                        <label class="text-xs text-gray-500">正文行距: {{ cardConfig.lineHeight.toFixed(1) }}</label>
                        <input type="range" min="1.2" max="1.8" step="0.1" v-model.number="cardConfig.lineHeight" class="w-full" />
                      </div>
                      <div>
                        <label class="text-xs text-gray-500">标题字号: {{ cardConfig.titleSize }}px</label>
                        <input type="range" min="18" max="28" step="1" v-model.number="cardConfig.titleSize" class="w-full" />
                      </div>
                      <div>
                        <label class="text-xs text-gray-500">分隔线粗细: {{ cardConfig.borderWidth }}px</label>
                        <input type="range" min="1" max="3" step="1" v-model.number="cardConfig.borderWidth" class="w-full" />
                      </div>
                      <div class="pt-1">
                        <button @click="resetStyles" class="w-full px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 rounded">重置为默认</button>
                      </div>
                    </div>
                    <div class="border-t my-2"></div>
                    <div class="text-xs font-bold text-gray-400 px-1 py-1 mb-2">样式预设</div>
                    <div class="space-y-2">
                      <div class="flex gap-2">
                        <input v-model="presetName" placeholder="输入预设名称" class="flex-1 px-2 py-1 text-xs border rounded" />
                        <button @click="savePreset" class="px-2 py-1 text-xs bg-blue-600 text-white rounded">保存</button>
                      </div>
                      <ul class="max-h-36 overflow-auto space-y-1">
                        <li v-for="p in stylePresets" :key="p.id" class="flex items-center justify-between text-xs px-2 py-1 border rounded">
                          <span class="truncate">{{ p.name }}</span>
                          <div class="flex items-center gap-2">
                            <button @click="applyPreset(p)" class="px-2 py-0.5 bg-gray-100 hover:bg-gray-200 rounded">应用</button>
                            <button @click="deletePreset(p.id)" class="px-2 py-0.5 bg-red-50 text-red-600 hover:bg-red-100 rounded">删除</button>
                          </div>
                        </li>
                        <li v-if="stylePresets.length===0" class="text-gray-400 text-xs px-2 py-1">暂无预设</li>
                      </ul>
                    </div>
                 </div>
               </Teleport>
            </div>
            <div class="flex items-center bg-white rounded border border-gray-300 overflow-hidden shadow-sm">
                <button 
                    @click="handlePrev" 
                    :disabled="!hasPrev"
                    class="px-3 py-1.5 hover:bg-gray-50 disabled:opacity-30 disabled:cursor-not-allowed border-r border-gray-200 flex items-center gap-1 transition-colors cursor-pointer disabled:cursor-not-allowed"
                    title="上一张 (←)">
                    <i data-lucide="chevron-left" class="w-4 h-4"></i>
                    <span class="text-xs font-medium">上一张</span>
                </button>
                <button 
                    @click="handleNext" 
                    :disabled="!hasNext"
                    class="px-3 py-1.5 hover:bg-gray-50 disabled:opacity-30 disabled:cursor-not-allowed flex items-center gap-1 transition-colors cursor-pointer disabled:cursor-not-allowed"
                    title="下一张 (→)">
                    <span class="text-xs font-medium">下一张</span>
                    <i data-lucide="chevron-right" class="w-4 h-4"></i>
                </button>
             </div>
          </div>

          <div class="flex items-center gap-2">
            <button @click="runAI" :disabled="aiLoading" class="flex items-center gap-1 bg-purple-600 text-white px-3 py-1.5 rounded-lg text-sm font-medium hover:bg-purple-700 disabled:opacity-50 transition-all shadow-sm cursor-pointer">
              <svg v-if="aiLoading" class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>
              {{ aiLoading ? 'AI 思考中...' : 'AI 智能优化' }}
            </button>
            <button @click="save" class="flex items-center gap-1 bg-blue-600 text-white px-4 py-1.5 rounded-lg text-sm font-medium hover:bg-blue-700 transition-all shadow-sm cursor-pointer">
              <i data-lucide="save" class="w-4 h-4"></i> 保存
            </button>
            <div class="h-6 w-px bg-gray-300 mx-2"></div>
            <button @click="close" class="flex items-center gap-1 bg-white border border-gray-300 text-gray-700 px-3 py-1.5 rounded-lg text-sm font-medium hover:bg-gray-50 transition-all shadow-sm cursor-pointer">
              <i data-lucide="x" class="w-4 h-4"></i> 关闭
            </button>
          </div>
      </div>

      <!-- Main Content Area with Resizable Splitter -->
      <div class="flex-1 flex overflow-hidden" @mousemove="handleDrag" @mouseup="stopDrag" @mouseleave="stopDrag">
          <!-- Left: Preview (Visual Card) -->
          <div class="relative bg-gray-100 p-8 overflow-hidden flex flex-col items-center justify-center select-none" :style="{ width: splitRatio + '%' }">
             <!-- Card Container with Auto-Scale -->
             <div class="w-full h-full flex items-center justify-center">
                <div class="bg-white shadow-2xl rounded-none relative overflow-hidden transition-all duration-300 origin-center" 
                     :style="[cardStyles, { 
                        aspectRatio: '16/9', 
                        width: '1280px', 
                        height: '720px',
                        transform: `scale(${scaleFactor})`
                     }]">
                  
                  <!-- Card Content Inside Scaled Container -->
                  <div class="w-full h-full p-8 flex flex-col gap-4">
                      <!-- Header -->
                      <header class="relative flex justify-between items-start border-b pb-2 mb-4" :style="{ borderColor: currentTheme.borderColor, borderBottomWidth: cardConfig.borderWidth + 'px' }">
                        <!-- Title (Left) -->
                        <div class="pr-32">
                          <h1 class="font-black tracking-tight leading-snug mb-0" :style="{ color: currentTheme.textColor, fontSize: cardConfig.titleSize + 'px' }">
                            {{ parsedData['项目名称'] || '未命名项目' }}
                          </h1>
                        </div>
                        
                        <!-- Metadata (Top Right Absolute) -->
                        <div class="absolute top-0 right-0 flex flex-col items-end gap-2">
                            <div class="flex items-center gap-2">
                                <div v-if="projectCode" class="text-xs font-bold px-1.5 py-1 rounded inline-flex items-center gap-1 opacity-80" :style="{ backgroundColor: currentTheme.accentColor + '20', color: currentTheme.accentColor }">
                                    所属项目: {{ projectCode }}
                                </div>
                                <div class="text-lg font-mono font-extrabold px-2 py-0.5 rounded-lg opacity-90 shadow-sm whitespace-nowrap" :style="{ borderColor: currentTheme.textColor, color: currentTheme.textColor, backgroundColor: currentTheme.textColor + '10' }">
                                  {{ parsedData['项目编号'] || 'NO.0000' }}
                                </div>
                            </div>
                            
                            <!-- New: Progress & Stage Badge in Preview -->
                            <div v-if="localCardData.sub_stage || localCardData.progress > 0" class="flex items-center gap-2">
                                <div v-if="localCardData.sub_stage" class="text-[10px] font-black uppercase px-1.5 py-0.5 rounded border shadow-sm" :style="{ borderColor: currentTheme.accentColor, color: currentTheme.accentColor, backgroundColor: currentTheme.accentColor + '05' }">
                                    {{ localCardData.sub_stage }}
                                </div>
                                <div v-if="localCardData.progress > 0" class="flex items-center gap-1.5 bg-gray-50 px-2 py-0.5 rounded border border-gray-200 shadow-sm min-w-[80px]">
                                    <div class="flex-1 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                                        <div class="h-full transition-all duration-500" :style="{ width: localCardData.progress + '%', backgroundColor: currentTheme.accentColor }"></div>
                                    </div>
                                    <span class="text-[10px] font-bold text-gray-600">{{ localCardData.progress }}%</span>
                                </div>
                            </div>
                        </div>
                      </header>

                      <!-- Grid Layout -->
                      <div class="flex-1 flex flex-col min-h-0 gap-4">
                        <div class="grid grid-cols-12 gap-4 flex-1 min-h-0">
                            <!-- Left Column (7) -->
                            <div class="col-span-7 flex flex-col gap-4 min-h-0">
                            <div class="grid grid-cols-2 gap-4">
                                <CardSection title="项目目标" :content="parsedData['项目目标'] || ''" :styles="{...currentTheme, borderWidth: cardConfig.borderWidth}" :fontSize="cardConfig.fontSize" :lineHeight="cardConfig.lineHeight" />
                                <CardSection title="现状分析" :content="parsedData['现状分析'] || ''" :styles="{...currentTheme, borderWidth: cardConfig.borderWidth}" :fontSize="cardConfig.fontSize" :lineHeight="cardConfig.lineHeight" />
                            </div>
                            <div class="flex-1 min-h-0">
                                <CardSection title="项目内容" :content="parsedData['项目内容'] || ''" :styles="{...currentTheme, borderWidth: cardConfig.borderWidth}" class="h-full" :fontSize="cardConfig.fontSize" :lineHeight="cardConfig.lineHeight" />
                            </div>
                            <div class="grid grid-cols-2 gap-4 min-h-[100px]">
                                <CardSection title="所需支持" :content="parsedData['所需支持'] || ''" :styles="{...currentTheme, borderWidth: cardConfig.borderWidth}" :fontSize="cardConfig.fontSize" :lineHeight="cardConfig.lineHeight" />
                                <CardSection title="预算投入" :content="parsedData['预算投入'] || ''" :styles="{...currentTheme, borderWidth: cardConfig.borderWidth}" :fontSize="cardConfig.fontSize" :lineHeight="cardConfig.lineHeight" />
                            </div>
                            </div>

                            <!-- Right Column (5) with explicit grid rows -->
                            <div class="col-span-5 grid grid-rows-[auto_auto_1fr] gap-4 min-h-0 h-full">
                                <div class="grid grid-cols-2 gap-4">
                                    <CardSection title="项目周期" :content="parsedData['项目周期'] || ''" :styles="{...currentTheme, borderWidth: cardConfig.borderWidth}" :fontSize="cardConfig.fontSize" :lineHeight="cardConfig.lineHeight" />
                                    <CardSection title="参与部门" :content="parsedData['参与部门'] || ''" :styles="{...currentTheme, borderWidth: cardConfig.borderWidth}" :fontSize="cardConfig.fontSize" :lineHeight="cardConfig.lineHeight" />
                                </div>
                                <CardSection title="相关产品及解决方案" :content="parsedData['相关产品及解决方案'] || ''" :styles="{...currentTheme, borderWidth: cardConfig.borderWidth}" :fontSize="cardConfig.fontSize" :lineHeight="cardConfig.lineHeight" />
                                <div class="min-h-[220px] h-full">
                                    <CardSection title="输出物" :content="parsedData['输出物'] || ''" :styles="{...currentTheme, borderWidth: cardConfig.borderWidth}" class="h-full" :fontSize="cardConfig.fontSize" :lineHeight="cardConfig.lineHeight" />
                                </div>
                            </div>
                        </div>

                        <!-- Bottom Full Width: Deliverables (Removed) -->
                      </div>
                  </div>
                </div>
             </div>
          </div>

          <!-- Resizer Handle -->
          <div class="w-1 bg-gray-300 hover:bg-blue-500 cursor-col-resize z-10 transition-colors flex items-center justify-center" @mousedown="startDrag">
            <div class="h-8 w-1 bg-gray-400 rounded-full"></div>
          </div>

          <!-- Right: Editor -->
          <div class="flex flex-col bg-white relative" :style="{ width: (100 - splitRatio) + '%' }">
            <!-- AI Diff Overlay -->
            <div v-if="showAiDiff" class="absolute inset-0 bg-white z-20 flex flex-col">
                <div class="h-14 border-b border-gray-200 flex items-center justify-between px-4 bg-purple-50 flex-shrink-0">
                    <div class="font-bold text-purple-800 flex items-center gap-2">
                        <i data-lucide="sparkles" class="w-4 h-4"></i> AI 优化建议
                    </div>
                    <div class="flex items-center gap-2">
                        <button @click="applyAiResult()" class="px-3 py-1.5 bg-purple-600 text-white text-sm rounded hover:bg-purple-700 cursor-pointer">应用</button>
                        <button @click="showAiDiff = false" class="px-3 py-1.5 bg-gray-200 text-gray-700 text-sm rounded hover:bg-gray-300 cursor-pointer">取消</button>
                    </div>
                </div>
                <div class="flex-1 grid grid-cols-2 gap-4 p-4 overflow-hidden">
                    <div class="flex flex-col overflow-hidden">
                        <div class="text-xs font-bold text-gray-500 uppercase mb-2">当前内容</div>
                        <div class="flex-1 p-3 bg-gray-50 rounded border border-gray-200 text-sm font-mono overflow-auto whitespace-pre-wrap">{{ rawText }}</div>
                    </div>
                    <div class="flex flex-col overflow-hidden">
                        <div class="text-xs font-bold text-purple-600 uppercase mb-2">AI 建议</div>
                        <div class="flex-1 p-3 bg-purple-50 rounded border border-purple-100 text-sm font-mono text-purple-900 overflow-auto whitespace-pre-wrap">{{ aiResultText }}</div>
                    </div>
                </div>
            </div>
            
            <!-- Inputs -->
            <div class="flex-1 overflow-y-auto p-6 space-y-6">
              <!-- Metadata -->
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block text-xs font-bold text-gray-500 uppercase mb-1">项目名称</label>
                  <input v-model="parsedData['项目名称']" class="w-full p-2 border rounded text-sm focus:ring-2 focus:ring-blue-100 outline-none">
                </div>
                <div>
                  <label class="block text-xs font-bold text-gray-500 uppercase mb-1">项目编号</label>
                  <input v-model="parsedData['项目编号']" class="w-full p-2 border rounded text-sm font-mono focus:ring-2 focus:ring-blue-100 outline-none">
                </div>
              </div>

              <!-- New: Sub-project Progress and Stage -->
              <div class="grid grid-cols-2 gap-4 p-4 bg-blue-50/50 rounded-lg border border-blue-100">
                <div>
                  <label class="block text-xs font-bold text-blue-600 uppercase mb-1">子项目阶段</label>
                  <el-input v-model="localCardData.sub_stage" placeholder="例如：开发中、测试中..." size="default" class="!w-full" />
                </div>
                <div>
                  <label class="block text-xs font-bold text-blue-600 uppercase mb-1">子项目进度 (%)</label>
                  <el-input-number 
                    v-model="localCardData.progress" 
                    :min="0" :max="100" 
                    class="!w-full" 
                    controls-position="right"
                    size="default"
                  />
                </div>
              </div>

              <!-- Raw Text Editor -->
              <div class="flex-1 flex flex-col">
                <div class="flex justify-between items-center mb-2">
                  <label class="block text-xs font-bold text-gray-500 uppercase">原始内容 (自动解析)</label>
                  <span class="text-xs text-gray-400">支持 Markdown 格式</span>
                </div>
                <textarea 
                  v-model="rawText" 
                  class="w-full flex-1 min-h-[400px] p-4 border rounded-lg text-sm font-mono leading-relaxed bg-gray-50 focus:bg-white focus:ring-2 focus:ring-blue-100 outline-none resize-none"
                  placeholder="在此输入项目内容，例如：
项目目标：
完成系统上线...

现状分析：
目前..."
                ></textarea>
              </div>
            </div>
          </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed, nextTick, onMounted, onUnmounted } from 'vue';
import { createIcons, icons } from 'lucide';
import api from '../api';
import CardSection from './CardSection.vue';

// Props & Emits
const props = defineProps<{
  visible: boolean;
  cardData: any;
  projectCode: string;
  hasPrev?: boolean;
  hasNext?: boolean;
  mode?: 'modal' | 'page';
}>();

const emit = defineEmits(['update:visible', 'save', 'prev', 'next']);

function handlePrev() {
  if (hasUnsavedChanges.value) {
    if (!confirm('您有未保存的更改，确定要切换吗？')) return;
  }
  emit('prev');
}

function handleNext() {
  if (hasUnsavedChanges.value) {
    if (!confirm('您有未保存的更改，确定要切换吗？')) return;
  }
  emit('next');
}

const mode = computed(() => props.mode || 'modal');

const rootClasses = computed(() => {
  if (mode.value === 'page') return 'w-screen h-screen bg-white flex flex-col fixed inset-0 z-50';
  return 'fixed inset-0 bg-black/50 z-[100] flex items-center justify-center p-4 sm:p-6';
});

const containerClasses = computed(() => {
  if (mode.value === 'page') return 'w-full h-full flex flex-col relative';
  return 'bg-white w-full max-w-[1400px] h-[85vh] rounded-xl shadow-2xl flex flex-col relative';
});

function handleOverlayClick() {
  if (mode.value === 'modal') close();
}

function close() {
  if (hasUnsavedChanges.value) {
    if (!confirm('您有未保存的更改，确定要关闭吗？')) return;
  }
  if (mode.value === 'page') {
      window.close();
  } else {
      emit('update:visible', false);
  }
}

// State
const rawText = ref('');
const hasUnsavedChanges = ref(false);
const localCardData = ref<any>({
    sub_stage: '',
    progress: 0,
    extra_data: {}
});

const parsedData = reactive<Record<string, string>>({
    '项目名称': '',
    '项目编号': '',
    '项目目标': '',
    '现状分析': '',
    '项目内容': '',
    '所需支持': '',
    '预算投入': '',
    '项目周期': '',
    '参与部门': '',
    '相关产品及解决方案': '',
    '输出物': ''
});
const aiLoading = ref(false);
const showAiDiff = ref(false);
const aiResultText = ref('');
const showThemeMenu = ref(false);
const showStyleMenu = ref(false);
const themeBtnRef = ref<HTMLElement | null>(null);
const menuStyle = ref<Record<string, string>>({ top: '0px', left: '0px' });
const styleBtnRef = ref<HTMLElement | null>(null);
const styleMenuStyle = ref<Record<string, string>>({ top: '0px', left: '0px' });
const stylePresets = ref<any[]>([]);
const presetName = ref('');
const cardConfig = reactive({
  fontSize: 14,
  lineHeight: 1.5,
  titleSize: 24,
  borderWidth: 2
});

// Styles (Mock from cardv8)
const styles = reactive({
  borderColor: '#000000',
  textColor: '#000000',
  accentColor: '#3b82f6',
  backgroundColor: '#ffffff'
});

const currentTheme = reactive({ ...styles, name: '默认白' });

const themes = [
    { name: '默认白', borderColor: '#000000', textColor: '#000000', accentColor: '#3b82f6', backgroundColor: '#ffffff' },
    { name: '深邃黑金', borderColor: '#D4AF37', textColor: '#F8F9FA', accentColor: '#D4AF37', backgroundColor: '#1A1A1A' },
    { name: '商务蓝灰', borderColor: '#334155', textColor: '#1e293b', accentColor: '#3b82f6', backgroundColor: '#f1f5f9' },
    { name: '活力橙', borderColor: '#f97316', textColor: '#431407', accentColor: '#f97316', backgroundColor: '#fff7ed' },
    { name: '石榴红', borderColor: '#D64045', textColor: '#4a0404', accentColor: '#D64045', backgroundColor: '#fff1f2' }
];

function selectTheme(t: any) {
    Object.assign(currentTheme, t);
    showThemeMenu.value = false;
}

const cardStyles = computed(() => ({
  fontFamily: '"Noto Sans SC", sans-serif',
  color: currentTheme.textColor,
  backgroundColor: currentTheme.backgroundColor
}));

// Resizer Logic
const splitRatio = ref(65); // Initial 65% for better 16:9 presentation
const isDragging = ref(false);
const scaleFactor = ref(1);

/**
 * 计算并设置主题菜单在页面中的绝对位置
 * 依赖按钮的 getBoundingClientRect 来确保菜单不受父容器布局影响
 */
function positionThemeMenu() {
    const el = themeBtnRef.value;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    menuStyle.value = {
        top: `${rect.bottom + 6}px`,
        left: `${rect.left}px`
    };
}

/**
 * 切换主题菜单的显示状态，并在显示时进行定位
 */
function toggleThemeMenu() {
    showThemeMenu.value = !showThemeMenu.value;
    if (showThemeMenu.value) {
        nextTick(() => positionThemeMenu());
    }
}

/**
 * 计算并设置样式菜单的绝对位置
 */
function positionStyleMenu() {
    const el = styleBtnRef.value;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    styleMenuStyle.value = {
        top: `${rect.bottom + 6}px`,
        left: `${rect.left}px`
    };
}

/**
 * 切换样式菜单的显示状态，并在显示时进行定位
 */
function toggleStyleMenu() {
    showStyleMenu.value = !showStyleMenu.value;
    if (showStyleMenu.value) {
        nextTick(() => positionStyleMenu());
    }
}

/**
 * 重置样式参数为默认值
 */
function resetStyles() {
    cardConfig.fontSize = 14;
    cardConfig.lineHeight = 1.5;
    cardConfig.titleSize = 24;
    cardConfig.borderWidth = 2;
}

// 在窗口尺寸变化时，若菜单展开则重新定位
onMounted(() => {
    window.addEventListener('resize', positionThemeMenu);
    window.addEventListener('resize', positionStyleMenu);
    loadPresets();
});
onUnmounted(() => {
    window.removeEventListener('resize', positionThemeMenu);
    window.removeEventListener('resize', positionStyleMenu);
});

function loadPresets() {
  const saved = localStorage.getItem('crm_card_style_presets');
  if (saved) {
    try { stylePresets.value = JSON.parse(saved); } catch(e) { stylePresets.value = []; }
  }
}

function persistPresets() {
  localStorage.setItem('crm_card_style_presets', JSON.stringify(stylePresets.value));
}

function savePreset() {
  const name = presetName.value.trim();
  if (!name) return;
  const preset = {
    id: Date.now(),
    name,
    fontSize: cardConfig.fontSize,
    lineHeight: cardConfig.lineHeight,
    titleSize: cardConfig.titleSize,
    borderWidth: cardConfig.borderWidth,
    theme: { ...currentTheme }
  };
  stylePresets.value.unshift(preset);
  persistPresets();
  presetName.value = '';
}

function applyPreset(p: any) {
  cardConfig.fontSize = p.fontSize;
  cardConfig.lineHeight = p.lineHeight;
  cardConfig.titleSize = p.titleSize;
  cardConfig.borderWidth = p.borderWidth;
  Object.assign(currentTheme, p.theme || {});
}

function deletePreset(id: number) {
  stylePresets.value = stylePresets.value.filter(x => x.id !== id);
  persistPresets();
}
function startDrag() { isDragging.value = true; }
function stopDrag() { isDragging.value = false; }

function handleDrag(e: MouseEvent) {
    if (!isDragging.value) return;
    const containerWidth = document.body.clientWidth; // Use window width for full screen
    const newRatio = (e.clientX / containerWidth) * 100;
    if (newRatio > 20 && newRatio < 80) {
        splitRatio.value = newRatio;
    }
}

// Auto Scale Logic
watch(splitRatio, () => {
    calculateScale();
});

onMounted(() => {
    window.addEventListener('resize', calculateScale);
    // Initial calculation after mount
    setTimeout(calculateScale, 100);
});

onUnmounted(() => {
    window.removeEventListener('resize', calculateScale);
});

function calculateScale() {
    // Target width 1280px + some padding (e.g. 64px)
    const targetWidth = 1280;
    const containerW = window.innerWidth * (splitRatio.value / 100);
    const availableW = containerW - 64; // Minus padding
    // Scale down if available space is smaller than target
    // Also scale up if space is huge? Maybe limit max scale to 1.5
    let scale = availableW / targetWidth;
    scale = Math.min(Math.max(scale, 0.2), 1.5); 
    scaleFactor.value = scale;
}

// Logic
const KEYS = [
  '项目名称', '项目编号', '项目目标', '现状分析', '项目内容', 
  '所需支持', '预算投入', '项目周期', '参与部门', '相关产品及解决方案', '输出物'
];

async function loadData() {
  if (props.visible && props.cardData) {
    console.log("CardEditor loading data:", props.cardData);
    
    // Sync local copy
    localCardData.value = JSON.parse(JSON.stringify(props.cardData));
    
    // 1. Initial Load from Props
    const content = props.cardData.content || '';
    // Always load from props first
    if (content && content.trim().length > 0) {
        rawText.value = content;
    } else {
        rawText.value = generateTemplate(props.cardData);
    }
    
    // Reset hasUnsavedChanges after initial load
    hasUnsavedChanges.value = false;
    
    // Parse immediately
    parseRawText();
    
    nextTick(() => createIcons({ icons }));

    // 2. Async Fetch Detail
    if (props.cardData.id) {
        try {
            const res = await api.get(`/project-cards/${props.cardData.id}/`);
            if (res.data) {
                console.log("Fetched detail content:", res.data.content);
                // Always trust the detail API as the source of truth
                // Do not check for length, because user might have deleted text
                if (res.data.content !== undefined) {
                    rawText.value = res.data.content;
                }
                localCardData.value = JSON.parse(JSON.stringify(res.data));
                // Re-parse after fetching
                parseRawText();
                // Reset dirty flag again after fetch
                hasUnsavedChanges.value = false;
            }
        } catch (e) {
            console.error("Failed to fetch card detail:", e);
        }
    }
  }
}

// Watchers
// 1. Watch visible and cardData ID changes to reload data
watch(
  [() => props.visible, () => props.cardData?.id], 
  ([newVisible, newId], [oldVisible, oldId]) => {
    // Only load if visible is true
    // And if it's either a visibility toggle OR a card ID change
    if (newVisible) {
        if (newVisible !== oldVisible || newId !== oldId) {
            loadData();
        }
    }
  }, 
  { immediate: true }
);

// 2. Watch rawText for changes to sync left preview
watch(rawText, () => {
    parseRawText();
    // Only mark as unsaved if we are not loading data
    // We can add a flag isloading if needed, but for now simple check:
    // If rawText is empty, it might be initialization.
    if (rawText.value) {
        hasUnsavedChanges.value = true;
    }
});

// Unsaved changes warning
const confirmLeave = (e: BeforeUnloadEvent) => {
  if (hasUnsavedChanges.value) {
    e.preventDefault();
    e.returnValue = '';
  }
};

onMounted(() => {
  window.addEventListener('beforeunload', confirmLeave);
  // loadData is triggered by watch immediate
});

onUnmounted(() => {
  window.removeEventListener('beforeunload', confirmLeave);
});

function generateTemplate(card: any) {
  return `项目名称：${card.title || ''}
项目编号：${card.extra_data?.code || card.id || ''}

项目目标：
${card.extra_data?.goal || ''}

现状分析：
${card.extra_data?.analysis || ''}

项目内容：
${card.content || ''}

所需支持：
${card.extra_data?.support || ''}

预算投入：
${card.budget || ''}

项目周期：
${card.start_date || ''} ~ ${card.deadline || ''}

参与部门：
${card.extra_data?.departments || ''}

相关产品及解决方案：
${card.extra_data?.products || ''}

输出物：
${card.extra_data?.deliverables || ''}
`;
}

function parseRawText() {
  if (!rawText.value) return;
  
  // Reset
  KEYS.forEach(k => parsedData[k] = '');
  
  const lines = rawText.value.split('\n');
  let currentKey: string | null = null;
  
  // Helper to normalize key (remove **, spaces)
  const normalize = (s: string) => s.replace(/\*/g, '').replace(/\s+/g, '').trim();
  
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) {
        if (currentKey) parsedData[currentKey] += '\n'; // Preserve paragraph breaks
        continue;
    }
    
    // Match Key: Value (Support: "Key:", "**Key**:", "Key：")
    // Regex: Start with optional **, capture Key, optional **, then : or ：
    const match = trimmed.match(/^(\*\*)?([^*：:]{2,20})(\*\*)?\s*[:：]\s*(.*)/);
    
    if (match) {
        const potentialKey = normalize(match[2] || '');
        // Fuzzy match with defined KEYS
        const foundKey = KEYS.find(k => normalize(k) === potentialKey);
        
        if (foundKey) {
            currentKey = foundKey;
            const val = (match[4] || '').trim();
            parsedData[currentKey] = val;
            continue;
        }
    }
    
    // If not a key, append to current key
    if (currentKey) {
        parsedData[currentKey] += (parsedData[currentKey] ? '\n' : '') + trimmed;
    }
  }
}

async function runAI() {
  if (!rawText.value) return;
  aiLoading.value = true;
  await nextTick();
  createIcons({ icons }); // Re-render icons (loader)

  try {
    const res = await api.post('chat/', {
      intent: 'optimize_card',
      text_input: rawText.value,
    }, {
      timeout: 30000 // 30s timeout
    });
    
    // Mock response for now if backend logic isn't ready for 'optimize_card'
    // But ideally backend returns optimized text
    console.log("AI Response Payload:", res.data);
    
    if (res.data && res.data.result_payload && res.data.result_payload.optimized_text) {
        aiResultText.value = res.data.result_payload.optimized_text;
        showAiDiff.value = true;
    } else {
        const errMsg = res.data?.error || "未返回有效内容";
        console.error("AI Error:", errMsg);
        alert(`AI 优化请求失败: ${errMsg}`);
    }
  } catch (e: any) {
    console.error("AI Request Failed:", e);
    const msg = e.response?.data?.error || e.message || "未知错误";
    alert(`AI 服务暂时不可用: ${msg}`);
  } finally {
    aiLoading.value = false;
    await nextTick();
    createIcons({ icons }); // Re-render icons (sparkles)
  }
}

function parseCurrency(str: string): number {
  if (!str) return 0;
  
  // Strategy 1: Try to find specific "Budget" line if the input is a full text block
  // e.g. "预算投入：35万"
  const budgetLineMatch = str.match(/(?:预算|投入|金额)[:：]\s*([^\n]+)/);
  if (budgetLineMatch && budgetLineMatch[1]) {
      str = budgetLineMatch[1] as string;
  }

  // Strategy 2: Extract all money values from the string (or the specific line)
  // Matches: 35万, 4.8万, 1000, 100.5
  const regex = /([0-9.]+)\s*(万|亿|千)?/g;
  let total = 0;
  let match;
  
  while ((match = regex.exec(str)) !== null) {
      if (!match[1]) continue;
      let val = parseFloat(match[1] as string);
      const unit = match[2];
      
      if (unit === '亿') val *= 100000000;
      else if (unit === '万') val *= 10000;
      else if (unit === '千') val *= 1000;
      
      // Filter out likely non-money numbers (e.g. years "2025", days "10人天") unless they look like money
      // Heuristic: If it has a unit, it's money. If no unit, it's risky.
      // For now, let's assume if the user put it in "Budget" field, it's money.
      // If we are parsing raw text, we rely on the "Budget" line extraction above.
      
      total += val;
  }
  
  return total;
}

function applyAiResult() {
    rawText.value = aiResultText.value;
    showAiDiff.value = false;
    hasUnsavedChanges.value = true;
}

async function save() {
  // Sync parsed data back to card object structure
  const payload = {
    title: parsedData['项目名称'],
    content: rawText.value, // Save full raw text
    budget: parseCurrency(parsedData['预算投入'] || '0'),
    sub_stage: localCardData.value.sub_stage,
    progress: localCardData.value.progress,
    // extra_data mapping
    extra_data: {
      ...localCardData.value.extra_data,
      code: parsedData['项目编号'],
      goal: parsedData['项目目标'],
      analysis: parsedData['现状分析'],
      support: parsedData['所需支持'],
      departments: parsedData['参与部门'],
      products: parsedData['相关产品及解决方案'],
      deliverables: parsedData['输出物']
    }
  };
  
  emit('save', payload);
  // Do NOT close on save
  // emit('update:visible', false); 
  
  // Optional: show a small toast or visual feedback
  // For now, rely on parent component to handle save success/failure feedback if any
  // But we reset unsaved changes flag
  hasUnsavedChanges.value = false;
}

</script>

<style scoped>
.custom-scroll::-webkit-scrollbar { width: 6px; }
.custom-scroll::-webkit-scrollbar-track { background: #f1f1f1; }
.custom-scroll::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
</style>
