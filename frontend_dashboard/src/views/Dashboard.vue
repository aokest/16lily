<template>
  <div class="h-screen flex flex-col p-4 md:p-6 gap-4 md:gap-6 bg-slate-900 text-slate-200 overflow-hidden font-sans theme-transition" :class="themeClass">
    <!-- Header -->
    <header class="flex justify-between items-center game-card p-4 shrink-0">
      <div class="flex items-center gap-6">
        <div class="w-1 h-12 bg-blue-500 shadow-[0_0_10px_#3b82f6]"></div>
        <div>
          <h1 class="text-3xl md:text-4xl font-black tracking-tighter gradient-title italic">十六军团战报</h1>
          <div class="flex gap-4 md:gap-6 mt-2 text-sm font-bold tracking-wide overflow-x-auto">
            <span 
              v-for="(tag, index) in departmentTags" 
              :key="tag.code"
              class="cursor-pointer transition-all px-3 py-1 rounded border border-transparent hover:border-blue-500/50 hover:bg-blue-500/10 whitespace-nowrap"
              :class="currentDeptIndex === index ? 'text-blue-400 border-blue-500 bg-blue-500/20 shadow-[0_0_10px_rgba(59,130,246,0.3)]' : 'text-slate-500'"
              @click="lockDepartment(index)"
            >
              <span v-if="currentDeptIndex === index" class="mr-1 animate-pulse">◈</span>
              {{ tag.name }}
            </span>
          </div>
        </div>
      </div>
      <div class="flex items-center gap-4">
        <select v-model="currentTheme" class="bg-transparent border border-slate-600 text-xs rounded p-1 outline-none mr-2">
            <option value="cyberpunk">Classic Game</option>
            <option value="saas">SaaS Light</option>
            <option value="space">Deep Space</option>
        </select>
        
        <div class="text-right border-l pl-6 border-slate-700 ml-2 hidden md:block">
          <div class="text-3xl font-mono font-bold text-blue-400 neon-text tracking-widest">{{ currentTime }}</div>
          <div class="text-[10px] text-slate-500 flex items-center justify-end gap-2 uppercase tracking-widest mt-1">
            SYSTEM ONLINE <span class="w-1.5 h-1.5 bg-green-500 rounded-full animate-ping"></span>
          </div>
        </div>
      </div>
    </header>

    <!-- KPI Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6 h-auto shrink-0">
      <!-- Signed -->
      <div class="game-card p-5 flex flex-col justify-between group overflow-hidden relative">
         <div class="absolute -right-4 -top-4 w-24 h-24 bg-green-500/10 rounded-full blur-xl group-hover:bg-green-500/20 transition-all"></div>
         <div>
            <div class="text-slate-400 text-xs font-bold uppercase tracking-widest">新签合同额 (SIGNED)</div>
            <div class="text-3xl md:text-4xl font-black text-green-400 mt-1 font-mono neon-green">
                <span class="text-xl md:text-2xl text-slate-500 align-top">¥</span>
                {{ formatWan(stats.financials?.actual_signed) }}
                <span class="text-sm text-slate-500 font-medium">万</span>
            </div>
         </div>
         <div class="flex justify-between items-end mt-2 border-t border-slate-700/50 pt-2">
             <div class="text-[10px] text-slate-500 uppercase tracking-wider">Target</div>
             <div class="text-xs font-bold text-slate-400">¥ {{ formatWan(stats.financials?.target_signed) }} 万</div>
         </div>
      </div>

      <!-- Profit -->
      <div class="game-card p-5 flex flex-col justify-between group overflow-hidden relative">
         <div class="absolute -right-4 -top-4 w-24 h-24 bg-purple-500/10 rounded-full blur-xl group-hover:bg-purple-500/20 transition-all"></div>
         <div>
            <div class="text-slate-400 text-xs font-bold uppercase tracking-widest">回款毛利 (RETURN)</div>
            <div class="text-3xl md:text-4xl font-black text-purple-400 mt-1 font-mono neon-purple">
                <span class="text-xl md:text-2xl text-slate-500 align-top">¥</span>
                {{ formatWan(stats.financials?.actual_return_profit) }}
                <span class="text-sm text-slate-500 font-medium">万</span>
            </div>
         </div>
         <div class="flex justify-between items-end mt-2 border-t border-slate-700/50 pt-2">
             <div class="text-[10px] text-slate-500 uppercase tracking-wider">Target</div>
             <div class="text-xs font-bold text-slate-400">¥ {{ formatWan(stats.financials?.target_return_profit) }} 万</div>
         </div>
      </div>

      <!-- Revenue -->
      <div class="game-card p-5 flex flex-col justify-between group overflow-hidden relative">
         <div class="absolute -right-4 -top-4 w-24 h-24 bg-amber-500/10 rounded-full blur-xl group-hover:bg-amber-500/20 transition-all"></div>
         <div>
            <div class="text-slate-400 text-xs font-bold uppercase tracking-widest">确认收入 (REVENUE)</div>
            <div class="text-3xl md:text-4xl font-black text-amber-400 mt-1 font-mono neon-amber">
                <span class="text-xl md:text-2xl text-slate-500 align-top">¥</span>
                {{ formatWan(stats.financials?.actual_revenue) }}
                <span class="text-sm text-slate-500 font-medium">万</span>
            </div>
         </div>
         <div class="flex justify-between items-end mt-2 border-t border-slate-700/50 pt-2">
             <div class="text-[10px] text-slate-500 uppercase tracking-wider">Target</div>
             <div class="text-xs font-bold text-slate-400">¥ {{ formatWan(stats.financials?.target_revenue) }} 万</div>
         </div>
      </div>
    </div>

    <!-- Charts & Feed -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6 flex-1 min-h-0">
        <!-- Charts -->
        <div class="game-card lg:col-span-2 p-5 flex flex-col min-h-[300px]">
            <h3 class="text-lg font-bold text-white mb-4 flex justify-between items-center tracking-wider">
                <span class="flex items-center gap-3">
                    <span class="w-1 h-4 bg-blue-500 shadow-[0_0_8px_#3b82f6]"></span>
                    BATTLEFIELD STATUS
                </span>
                <span class="text-sm text-slate-400 font-mono hidden md:inline">
                    PIPELINE: <span class="text-blue-400 neon-text">¥ {{ formatWan(stats.funnel?.total_pipeline_amount) }} 万</span>
                    <span class="mx-2 text-slate-600">|</span>
                    UNITS: <span class="text-blue-400">{{ stats.funnel?.total_count }}</span>
                </span>
            </h3>
            <div class="flex-1 flex flex-col md:flex-row gap-4 h-full">
                <div ref="gaugeRef" class="w-full md:w-1/3 h-64 md:h-full"></div>
                <div ref="funnelRef" class="w-full md:w-2/3 h-64 md:h-full"></div>
            </div>
        </div>

        <!-- Live Feed -->
        <div class="game-card lg:col-span-1 p-0 flex flex-col overflow-hidden min-h-[300px]">
             <div class="p-5 border-b border-slate-700 bg-slate-800/30 flex justify-between items-center shrink-0">
                <h3 class="text-lg font-bold text-white flex items-center gap-3 tracking-wider">
                    <span class="w-1 h-4 bg-amber-500 shadow-[0_0_8px_#f59e0b]"></span>
                    LIVE INTEL
                </h3>
                <div class="text-xs font-mono text-slate-400 text-right">
                    <div class="text-amber-500">{{ currentNewStat.label }}</div>
                    <div class="text-xl font-bold text-white">{{ currentNewStat.value }}</div>
                </div>
            </div>
            
            <div class="flex-1 feed-scroll-wrapper relative overflow-hidden" ref="feedWrapper">
                <div class="feed-scroll-content absolute w-full p-4 space-y-3 transition-transform ease-linear" :style="{ transform: `translateY(-${scrollTop}px)` }">
                    <template v-for="(log, i) in displayedActivities" :key="log.uniqueKey">
                        <div class="p-3 rounded border-l-2 bg-slate-800/40 hover:bg-slate-700/50 transition-all group relative overflow-hidden" 
                             :class="getBorderColor(log.action)">
                             <div v-if="isMajorEvent(log.action)" class="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent animate-pulse pointer-events-none"></div>
                             
                             <div class="flex justify-between items-start mb-1 relative z-10">
                                <div class="flex items-center gap-2">
                                    <span class="font-bold text-slate-200 text-sm group-hover:text-white">{{ log.operator_name }}</span>
                                    <span class="text-[10px] px-1.5 py-0.5 bg-slate-700/50 text-slate-400 rounded border border-slate-600 font-mono">{{ formatTime(log.created_at) }}</span>
                                </div>
                                <div v-if="getEventIcon(log.action)" class="text-lg filter drop-shadow-[0_0_5px_rgba(255,255,255,0.5)]">
                                    {{ getEventIcon(log.action) }}
                                </div>
                            </div>
                            <div class="text-sm text-slate-400 group-hover:text-slate-300 relative z-10">
                                <span class="font-bold" :class="getTextColor(log.action)">[{{ log.action }}]</span> 
                                <span>{{ log.content }}</span>
                            </div>
                        </div>
                        <div v-if="i === activities.length - 1 && activities.length > 5" class="border-t border-dashed border-slate-700 my-4 pt-4 opacity-30"></div>
                    </template>
                    
                    <div v-if="activities.length === 0" class="text-center text-slate-600 mt-10 font-mono text-xs tracking-widest">
                        // NO ACTIVITY DETECTED //
                    </div>
                </div>
            </div>
        </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch } from 'vue';
import * as echarts from 'echarts';
import { fetchStats, fetchActivities } from '../api'; // Corrected Import Path

// --- State ---
const currentTheme = ref(localStorage.getItem('dashboard_theme') || 'cyberpunk');
const stats = ref<any>({ financials: {}, funnel: {}, new_counts: {} });
const activities = ref<any[]>([]);
const currentTime = ref('');
const departmentTags = [
    { name: '销售部', code: 'SALES' },
    { name: '春秋GAME', code: 'GAME' },
    { name: '集团市场部', code: 'GROUP_MARKETING' },
    { name: '标准实践实验室', code: 'LAB' }
];
const currentDeptIndex = ref(0);
const isDeptLocked = ref(false);

// Scroll
const scrollTop = ref(0);
const feedWrapper = ref<HTMLElement | null>(null);
let scrollInterval: any = null;

// Charts
const gaugeRef = ref<HTMLElement | null>(null);
const funnelRef = ref<HTMLElement | null>(null);
let gaugeChart: echarts.ECharts | null = null;
let funnelChart: echarts.ECharts | null = null;

// New Stats Carousel
const newStatsOptions = ['today', 'week', 'month', 'quarter', 'year'];
const newStatsLabels: Record<string, string> = {
    'today': '今日新增',
    'week': '本周新增',
    'month': '本月新增',
    'quarter': '本季新增',
    'year': '今年新增'
};
const currentNewStatIndex = ref(0);

// --- Computed ---
const themeClass = computed(() => `theme-${currentTheme.value}`);

const currentNewStat = computed(() => {
    const key = newStatsOptions[currentNewStatIndex.value];
    const val = stats.value.new_counts ? stats.value.new_counts[key] : 0;
    return { label: newStatsLabels[key], value: val };
});

const displayedActivities = computed(() => {
    // Duplicate list for seamless scrolling if enough items
    if (activities.value.length <= 5) return activities.value.map(x => ({...x, uniqueKey: x.id}));
    const original = activities.value.map(x => ({...x, uniqueKey: x.id}));
    const clone = activities.value.map(x => ({...x, uniqueKey: 'clone-' + x.id}));
    return [...original, ...clone];
});

// --- Watchers ---
watch(currentTheme, (val) => {
    localStorage.setItem('dashboard_theme', val);
    setTimeout(renderCharts, 100);
});

// --- Methods ---
const formatWan = (num: any) => {
    if (!num) return '0';
    return (Number(num) / 10000).toLocaleString(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 2 });
};

const formatTime = (timeStr: string) => {
    if (!timeStr) return '';
    try {
        return new Date(timeStr).toLocaleTimeString('zh-CN', { hour12: false });
    } catch { return timeStr; }
};

const isMajorEvent = (action: string) => {
    if (!action) return false;
    return ['赢单', '中标', '签合同', '签约', '交付', '完成'].some(k => action.includes(k));
};

const getEventIcon = (action: string) => {
    if (!action) return '';
    if (action.includes('赢单') || action.includes('中标')) return '🏆';
    if (action.includes('签合同') || action.includes('签约')) return '✍️';
    if (action.includes('交付') || action.includes('完成')) return '🚀';
    if (action.includes('输单')) return '💔';
    if (action.includes('创建')) return '✨';
    return '';
};

const getBorderColor = (action: string) => {
    if (!action) return 'border-blue-500/50';
    if (action.includes('赢单') || action.includes('中标')) return 'border-yellow-500/50 bg-yellow-900/20';
    if (action.includes('签合同') || action.includes('签约')) return 'border-green-500/50 bg-green-900/20';
    if (action.includes('交付') || action.includes('完成')) return 'border-cyan-500/50 bg-cyan-900/20';
    if (action.includes('输单')) return 'border-red-500/50 bg-red-900/10';
    return 'border-blue-500/50';
};

const getTextColor = (action: string) => {
    if (!action) return 'text-blue-400';
    if (action.includes('赢单') || action.includes('中标')) return 'neon-gold font-black';
    if (action.includes('签合同') || action.includes('签约')) return 'neon-green font-black';
    if (action.includes('交付') || action.includes('完成')) return 'neon-cyan font-black';
    if (action.includes('输单')) return 'text-red-400';
    if (action.includes('创建')) return 'text-white';
    return 'text-blue-400';
};

const lockDepartment = (index: number) => {
    if (currentDeptIndex.value === index) {
        isDeptLocked.value = !isDeptLocked.value;
    } else {
        currentDeptIndex.value = index;
        isDeptLocked.value = true;
        loadData();
    }
};

const loadData = async () => {
    try {
        const deptCode = departmentTags[currentDeptIndex.value].code;
        const [statsRes, activitiesRes] = await Promise.all([
            fetchStats({ department: deptCode }),
            fetchActivities()
        ]);
        stats.value = statsRes.data;
        activities.value = activitiesRes.data;
        renderCharts();
    } catch (e) {
        console.error("Data load failed", e);
    }
};

const renderCharts = () => {
    if (!gaugeRef.value || !funnelRef.value) return;
    
    if (!gaugeChart) gaugeChart = echarts.init(gaugeRef.value);
    if (!funnelChart) funnelChart = echarts.init(funnelRef.value);

    const isLight = currentTheme.value === 'saas';
    const actual = stats.value.financials?.actual_signed || 0;
    const target = stats.value.financials?.target_signed || 1;
    let rate = (actual / target) * 100;
    if (rate > 100) rate = 100;

    gaugeChart.setOption({
        series: [{
            type: 'gauge',
            startAngle: 180, endAngle: 0,
            min: 0, max: 100,
            splitNumber: 5,
            itemStyle: { color: '#3b82f6', shadowBlur: isLight ? 0 : 10, shadowColor: '#3b82f6' },
            progress: { show: true, width: 8 },
            pointer: { show: false },
            axisLine: { lineStyle: { width: 8, color: [[1, isLight ? '#e2e8f0' : '#1e293b']] } },
            axisTick: { show: false },
            splitLine: { length: 12, lineStyle: { width: 2, color: isLight ? '#cbd5e1' : '#475569' } },
            axisLabel: { color: '#64748b', fontSize: 10, distance: -20 },
            detail: {
                valueAnimation: true, offsetCenter: [0, '-20%'], fontSize: 30, fontWeight: 'bolder',
                formatter: '{value}%', color: isLight ? '#0f172a' : '#fff'
            },
            data: [{ value: rate.toFixed(1) }]
        }]
    });

    const funnelData = (stats.value.stages || []).map((s: any) => ({ value: s.count, name: s.stage }));
    funnelChart.setOption({
        tooltip: { trigger: 'item', formatter: '{b} : {c}' },
        color: ['#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe', '#dbeafe'],
        series: [{
            name: 'Pipeline', type: 'funnel', left: '10%', top: 10, bottom: 10, width: '80%',
            sort: 'descending', gap: 2,
            label: { show: true, position: 'inside', color: '#0f172a', fontWeight: 'bold' },
            itemStyle: { borderColor: isLight ? '#fff' : '#0f172a', borderWidth: 2, opacity: 0.8 },
            data: funnelData
        }]
    });
};

// --- Lifecycle ---
onMounted(() => {
    // Time
    setInterval(() => currentTime.value = new Date().toLocaleTimeString('en-GB'), 1000);
    
    // Auto Cycle
    setInterval(() => {
        if (!isDeptLocked.value) {
            currentDeptIndex.value = (currentDeptIndex.value + 1) % departmentTags.length;
            loadData();
        }
        currentNewStatIndex.value = (currentNewStatIndex.value + 1) % newStatsOptions.length;
    }, 5000);

    // Initial Load
    loadData();
    setInterval(loadData, 10000);

    // Resize
    window.addEventListener('resize', () => {
        gaugeChart?.resize();
        funnelChart?.resize();
    });

    // Scroll Logic
    scrollInterval = setInterval(() => {
        if (!feedWrapper.value || activities.value.length <= 5) return;
        scrollTop.value += 0.5;
        // Reset when scrolled half way (since content is duplicated)
        // Approximate height calculation - better to use actual DOM height if possible
        // For simplicity:
        if (scrollTop.value > (feedWrapper.value.scrollHeight / 2)) {
             scrollTop.value = 0;
        }
    }, 50);
});

onUnmounted(() => {
    if (scrollInterval) clearInterval(scrollInterval);
});
</script>

<style scoped>
/* Scoped styles from App.vue */
</style>