<template>
  <div class="min-h-screen flex flex-col bg-[#f8fafc] font-sans">
    <!-- Navbar -->
    <nav class="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center gap-4">
            <a href="#" @click.prevent="router.push('/projects')" class="text-gray-500 hover:text-gray-900 flex items-center gap-1" title="返回项目看板">
              <i data-lucide="layout-dashboard" class="w-5 h-5"></i> 看板
            </a>
            <div class="h-6 w-px bg-gray-200"></div>
            <div class="font-bold text-xl text-gray-900">{{ project?.name || '加载中...' }}</div>
          </div>
          <div class="flex items-center gap-3">
            <button @click="deleteCurrentProject" class="flex items-center gap-2 px-4 py-2 bg-white border border-red-200 text-red-600 rounded-lg hover:bg-red-50 transition-colors text-sm font-medium">
              <i data-lucide="trash-2" class="w-4 h-4"></i>
              删除项目
            </button>
            <div class="w-px h-6 bg-gray-200 mx-1"></div>
            <button @click="exportProjectData" class="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium">
              <i data-lucide="download" class="w-4 h-4 text-gray-500"></i>
              JSON 备份
            </button>
            <button @click="saveProject" class="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium shadow-sm">
              <i data-lucide="save" class="w-4 h-4"></i>
              保存变更
            </button>
          </div>
        </div>
      </div>
    </nav>

    <main v-if="project" class="flex-1 max-w-[1600px] w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 flex flex-col lg:flex-row gap-8">
      
      <!-- Left: Meta Info Editor -->
      <div class="w-full lg:w-1/3 flex flex-col gap-6">
        <!-- Basic Info -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 class="font-bold text-gray-900 mb-4 flex items-center gap-2">
            <i data-lucide="info" class="w-5 h-5 text-blue-500"></i> 基础信息
          </h3>
          <div class="space-y-4">
            <div>
              <label class="block text-xs font-bold text-gray-500 uppercase">项目名称</label>
              <input v-model="project.name" type="text" class="mt-1 w-full p-2 border rounded text-sm bg-gray-50 focus:bg-white focus:ring-2 focus:ring-blue-100 outline-none">
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-bold text-gray-500 uppercase">客户名称</label>
                <input v-model="project.customer_name" type="text" class="mt-1 w-full p-2 border rounded text-sm bg-gray-50 focus:bg-white focus:ring-2 focus:ring-blue-100 outline-none">
              </div>
              <div>
                <label class="block text-xs font-bold text-gray-500 uppercase">关联商机</label>
                <el-select
                  v-model="project.opportunity"
                  filterable
                  remote
                  clearable
                  placeholder="搜索商机"
                  :remote-method="searchOpportunities"
                  @focus="searchOpportunities('')"
                  :loading="opportunityLoading"
                  class="w-full mt-1 !h-[38px]"
                  size="default"
                >
                  <el-option
                    v-for="item in opportunityOptions"
                    :key="item.id"
                    :label="item.name"
                    :value="item.id"
                  />
                </el-select>
              </div>
              <div>
                <label class="block text-xs font-bold text-gray-500 uppercase">客户代号</label>
                <input v-model="project.extra_data.customer_code" type="text" class="mt-1 w-full p-2 border rounded text-sm font-mono uppercase bg-white focus:ring-2 focus:ring-blue-100 outline-none">
              </div>
              <div>
                <label class="block text-xs font-bold text-gray-500 uppercase">项目代号</label>
                <input v-model="project.code" type="text" class="mt-1 w-full p-2 border rounded text-sm font-mono uppercase bg-white focus:ring-2 focus:ring-blue-100 outline-none">
              </div>
            </div>
            <div>
              <label class="block text-xs font-bold text-gray-500 uppercase">项目简介</label>
              <textarea v-model="project.description" rows="2" class="mt-1 w-full p-2 border rounded text-sm bg-gray-50 focus:bg-white focus:ring-2 focus:ring-blue-100 outline-none resize-none"></textarea>
            </div>
          </div>
        </div>

        <!-- Project Status & Progress -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 class="font-bold text-gray-900 mb-4 flex items-center gap-2">
            <i data-lucide="trending-up" class="w-5 h-5 text-orange-500"></i> 状态与进度
          </h3>
          <div class="space-y-4">
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-bold text-gray-500 uppercase">当前状态</label>
                <el-select v-model="project.status" class="w-full mt-1" size="default">
                  <el-option v-for="opt in statusOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
                </el-select>
              </div>
              <div>
                <label class="block text-xs font-bold text-gray-500 uppercase">具体阶段</label>
                <el-select v-model="project.stage" class="w-full mt-1" size="default">
                  <el-option v-for="opt in stageOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
                </el-select>
              </div>
            </div>

            <div v-if="project.status === 'COMPLETED'" class="p-3 bg-gray-50 rounded-lg border border-gray-100 space-y-2">
              <label class="block text-[10px] font-bold text-gray-400 uppercase">结项清单</label>
              <div class="flex flex-wrap gap-4">
                <el-checkbox v-model="project.is_revenue_confirmed" label="已经确收" size="small" />
                <el-checkbox v-model="project.is_fully_paid" label="完全回款" size="small" />
                <el-checkbox v-model="project.is_maintenance_finished" label="维保完成" size="small" />
              </div>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-bold text-gray-500 uppercase">跟进节奏</label>
                <el-select v-model="project.followup_rhythm" class="w-full mt-1" size="default">
                  <el-option v-for="opt in rhythmOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
                </el-select>
              </div>
              <div>
                <div class="flex justify-between items-center mb-1">
                  <label class="block text-xs font-bold text-gray-500 uppercase">完成度 (%)</label>
                  <span class="text-[10px] text-gray-400">{{ project.auto_update_progress ? '自动' : '手动' }}</span>
                </div>
                <div class="flex items-center gap-2">
                  <el-input-number 
                    v-if="project.auto_update_progress"
                    v-model="project.progress" 
                    :disabled="true"
                    class="!w-full" 
                    controls-position="right"
                    size="default"
                  />
                  <el-input-number 
                    v-else
                    v-model="project.progress_manual" 
                    :min="0" :max="100" 
                    class="!w-full" 
                    controls-position="right"
                    size="default"
                  />
                  <el-tooltip :content="project.auto_update_progress ? '当前为自动计算 (基于卡片)' : '当前为手动维护'" placement="top">
                    <button @click="project.auto_update_progress = !project.auto_update_progress" class="p-2 border rounded hover:bg-gray-50 transition-colors" :class="project.auto_update_progress ? 'text-blue-500 bg-blue-50' : 'text-orange-500 bg-orange-50'">
                      <i :data-lucide="project.auto_update_progress ? 'refresh-cw' : 'user'" class="w-4 h-4"></i>
                    </button>
                  </el-tooltip>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Team & Finance -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 class="font-bold text-gray-900 mb-4 flex items-center gap-2">
            <i data-lucide="users" class="w-5 h-5 text-purple-500"></i> 团队与预算
          </h3>
          <div class="space-y-4">
            <div class="grid grid-cols-2 gap-3">
              <!-- Sales Team -->
              <div>
                <label class="block text-xs font-bold text-gray-500 uppercase">销售负责人</label>
                <div class="mt-1 w-full border rounded text-sm bg-gray-50 focus-within:bg-white focus-within:ring-2 focus-within:ring-blue-100 min-h-[38px] flex flex-wrap gap-1 p-1" @click="focusInput('sales_manager_input')">
                    <div v-for="(tag, index) in (project.extra_data.sales_managers || [])" :key="tag + '-' + index" class="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-0.5 rounded flex items-center gap-1">
                        {{ tag }}
                        <button type="button" @click.stop.prevent="removeTag('sales_managers', index)" class="hover:text-blue-900 cursor-pointer"><i data-lucide="x" class="w-3 h-3"></i></button>
                    </div>
                   <input 
                    ref="sales_manager_input"
                    v-model="inputState.sales_managers" 
                    @keydown.enter.prevent="addTag('sales_managers')" 
                    @blur="addTag('sales_managers')"
                    type="text" 
                    list="sales-user-suggestions"
                    class="flex-1 bg-transparent outline-none min-w-[60px]" 
                    placeholder="输入后回车">
                </div>
              </div>
              <!-- Delivery Team -->
              <div>
                <label class="block text-xs font-bold text-gray-500 uppercase">交付负责人</label>
                <div class="mt-1 w-full border rounded text-sm bg-gray-50 focus-within:bg-white focus-within:ring-2 focus-within:ring-blue-100 min-h-[38px] flex flex-wrap gap-1 p-1" @click="focusInput('delivery_managers_input')">
                    <div v-for="(tag, index) in (project.extra_data.delivery_managers || [])" :key="tag + '-' + index" class="bg-purple-100 text-purple-800 text-xs font-medium px-2 py-0.5 rounded flex items-center gap-1">
                        {{ tag }}
                        <button type="button" @click.stop.prevent="removeTag('delivery_managers', index)" class="hover:text-purple-900 cursor-pointer"><i data-lucide="x" class="w-3 h-3"></i></button>
                    </div>
                    <input 
                    ref="delivery_managers_input"
                    v-model="inputState.delivery_managers" 
                    @keydown.enter.prevent="addTag('delivery_managers')" 
                    @blur="addTag('delivery_managers')"
                    type="text" 
                    list="delivery-user-suggestions"
                    class="flex-1 bg-transparent outline-none min-w-[60px]" 
                    placeholder="输入后回车">
                </div>
              </div>
               <!-- Product Team -->
              <div class="col-span-2">
                <label class="block text-xs font-bold text-gray-500 uppercase">产品负责人</label>
                 <div class="mt-1 w-full border rounded text-sm bg-gray-50 focus-within:bg-white focus-within:ring-2 focus-within:ring-blue-100 min-h-[38px] flex flex-wrap gap-1 p-1" @click="focusInput('product_managers_input')">
                    <div v-for="(tag, index) in (project.extra_data.product_managers || [])" :key="tag + '-' + index" class="bg-indigo-100 text-indigo-800 text-xs font-medium px-2 py-0.5 rounded flex items-center gap-1">
                        {{ tag }}
                        <button type="button" @click.stop.prevent="removeTag('product_managers', index)" class="hover:text-indigo-900 cursor-pointer"><i data-lucide="x" class="w-3 h-3"></i></button>
                    </div>
                    <input 
                    ref="product_managers_input"
                    v-model="inputState.product_managers" 
                    @keydown.enter.prevent="addTag('product_managers')" 
                    @blur="addTag('product_managers')"
                    type="text" 
                    list="product-user-suggestions"
                    class="flex-1 bg-transparent outline-none min-w-[60px]" 
                    placeholder="输入后回车">
                </div>
              </div>
            </div>
            <!-- Datalist for autocomplete -->
            <datalist id="sales-user-suggestions">
                <option v-for="u in salesOptions" :key="u.id" :value="u.name || u.username" />
            </datalist>
            <datalist id="delivery-user-suggestions">
                <option v-for="u in deliveryOptions" :key="u.id" :value="u.name || u.username" />
            </datalist>
            <datalist id="product-user-suggestions">
                <option v-for="u in productOptions" :key="u.id" :value="u.name || u.username" />
            </datalist>
            <div>
                <label class="block text-xs font-bold text-gray-500 uppercase mb-2">财务概览 (CNY)</label>
                <div class="flex items-center justify-between mb-2">
                    <span class="text-xs text-gray-400">自动聚合子卡片预算?</span>
                    <label class="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" v-model="project.extra_data.budget_auto_calc" class="sr-only peer">
                        <div class="w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                </div>
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="text-xs text-gray-400">预计收入</label>
                        <div class="relative">
                            <span class="absolute left-2 top-2 text-gray-400">¥</span>
                            <input v-model="project.budget" type="number" class="w-full pl-6 p-2 border rounded text-sm bg-gray-50 focus:bg-white outline-none">
                        </div>
                    </div>
                    <div>
                        <label class="text-xs text-gray-400">预计成本</label>
                        <div class="relative">
                            <span class="absolute left-2 top-2 text-gray-400">¥</span>
                            <input v-model="project.extra_data.cost" type="number" class="w-full pl-6 p-2 border rounded text-sm bg-gray-50 focus:bg-white outline-none">
                        </div>
                    </div>
                </div>
            </div>
          </div>
        </div>

         <!-- Deliverables -->
         <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex-1">
            <div class="flex justify-between items-center mb-4">
                <h3 class="font-bold text-gray-900 flex items-center gap-2">
                    <i data-lucide="package" class="w-5 h-5 text-green-500"></i> 货架清单
                </h3>
                <button @click="addDeliverable" class="text-xs text-blue-600 hover:underline">+ 添加</button>
            </div>
            <div class="space-y-2 max-h-60 overflow-y-auto custom-scroll">
                <div v-for="(_item, idx) in (project.extra_data.deliverables || [])" :key="idx" class="flex gap-2">
                   <input v-model="project.extra_data.deliverables[idx]" class="flex-1 text-sm border-b border-gray-200 focus:border-blue-500 outline-none" placeholder="输入交付物...">
                   <button @click="removeDeliverable(idx)" class="text-gray-400 hover:text-red-500"><i data-lucide="x" class="w-3 h-3"></i></button>
                </div>
                <div v-if="!(project.extra_data.deliverables && project.extra_data.deliverables.length)" class="text-xs text-gray-400 text-center py-4">暂无交付物</div>
            </div>
        </div>
      </div>

      <!-- Right: Linked Cards -->
      <div class="flex-1 flex flex-col gap-6 min-w-0">
        <!-- Summary Stats -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div class="p-4 bg-gray-50 border-b border-gray-200 flex justify-between items-center">
                <h3 class="font-bold text-gray-800 flex items-center gap-2">
                    <i data-lucide="calculator" class="w-4 h-4 text-blue-500"></i>
                    预算与工时概览
                </h3>
            </div>
            <div class="p-6">
                <div class="grid grid-cols-3 gap-6">
                    <div class="bg-blue-50 rounded-lg p-4 border border-blue-100">
                        <div class="text-xs text-blue-600 mb-1 font-medium">子卡片总预算</div>
                        <div class="text-2xl font-bold text-blue-900">¥{{ formatNumber(stats.totalBudget) }}</div>
                        <div class="text-[10px] text-blue-400 mt-1">基于关联卡片“预算投入”自动汇总</div>
                    </div>
                    <div class="bg-indigo-50 rounded-lg p-4 border border-indigo-100">
                        <div class="text-xs text-indigo-600 mb-1 font-medium">预估总工时</div>
                        <div class="text-2xl font-bold text-indigo-900">{{ stats.totalManDays }} 人天</div>
                        <div class="text-[10px] text-indigo-400 mt-1">自动识别“人天”或“d”关键字</div>
                    </div>
                    <div class="bg-emerald-50 rounded-lg p-4 border border-emerald-100">
                        <div class="text-xs text-emerald-600 mb-1 font-medium">关联卡片数</div>
                        <div class="text-2xl font-bold text-emerald-900">{{ cards.length }} 个</div>
                        <div class="text-[10px] text-emerald-400 mt-1">当前项目关联的子项总数</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="flex justify-between items-center">
            <h2 class="text-2xl font-black text-gray-900">关联项目卡片</h2>
            <div class="flex items-center gap-4">
                <!-- Bulk Actions -->
                <div v-if="selectedCards.length > 0" class="flex items-center gap-2 bg-blue-50 px-3 py-1.5 rounded-lg border border-blue-100 animate-in fade-in slide-in-from-right-4">
                    <span class="text-xs font-bold text-blue-800 mr-2">已选 {{ selectedCards.length }} 项</span>
                    <button @click="batchToggleStatus" class="text-xs flex items-center gap-1 text-gray-700 hover:text-gray-900 bg-white border border-gray-200 px-2 py-1 rounded shadow-sm">
                        <i data-lucide="power" class="w-3 h-3"></i> 启/停
                    </button>
                    <div class="h-4 w-px bg-gray-300 mx-1"></div>
                    <button @click="importMD" class="text-xs flex items-center gap-1 text-gray-700 hover:text-gray-900 bg-white border border-gray-200 px-2 py-1 rounded shadow-sm">
                        <i data-lucide="file-input" class="w-3 h-3"></i> 导入MD
                    </button>
                    <button @click="exportMD" class="text-xs flex items-center gap-1 text-gray-700 hover:text-gray-900 bg-white border border-gray-200 px-2 py-1 rounded shadow-sm">
                        <i data-lucide="file-output" class="w-3 h-3"></i> 导出MD
                    </button>
                    <button @click="exportExcel" class="text-xs flex items-center gap-1 text-green-700 hover:text-green-900 bg-white border border-green-200 px-2 py-1 rounded shadow-sm">
                        <i data-lucide="sheet" class="w-3 h-3"></i> 导出Excel
                    </button>
                    <div class="h-4 w-px bg-gray-300 mx-1"></div>
                    <button @click="showBudgetStats" class="text-xs flex items-center gap-1 text-purple-700 hover:text-purple-900 bg-white border border-purple-200 px-2 py-1 rounded shadow-sm">
                        <i data-lucide="calculator" class="w-3 h-3"></i> 预算统计
                    </button>
                    <button @click="batchDelete" class="text-xs flex items-center gap-1 text-red-600 hover:text-red-800 bg-white border border-red-200 px-2 py-1 rounded shadow-sm">
                        <i data-lucide="trash" class="w-3 h-3"></i> 删除
                    </button>
                </div>

                <!-- View Mode Switcher -->
                <div class="flex bg-gray-100 p-1 rounded-lg border border-gray-200">
                    <button @click="viewMode = 'grid'" :class="{'bg-white shadow-sm text-blue-600': viewMode==='grid', 'text-gray-500 hover:text-gray-700': viewMode!=='grid'}" class="p-1.5 rounded-md transition-all" title="网格视图">
                        <i data-lucide="layout-grid" class="w-4 h-4"></i>
                    </button>
                    <button @click="viewMode = 'list'" :class="{'bg-white shadow-sm text-blue-600': viewMode==='list', 'text-gray-500 hover:text-gray-700': viewMode!=='list'}" class="p-1.5 rounded-md transition-all" title="列表视图">
                        <i data-lucide="list" class="w-4 h-4"></i>
                    </button>
                </div>

                <div class="flex items-center gap-2">
                    <button @click="openTimeline" class="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-100 flex items-center gap-2 shadow-sm">
                        <i data-lucide="calendar" class="w-4 h-4"></i> 查看推进表 (新窗口)
                    </button>
                    <button @click="openCardCreator" class="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50 flex items-center gap-2 shadow-sm">
                        <i data-lucide="plus-circle" class="w-4 h-4"></i> 新增卡片
                    </button>
                </div>
            </div>
        </div>

        <!-- Cards Container -->
        <div :class="{'grid grid-cols-1 gap-4': viewMode === 'list', 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-6': viewMode === 'grid'}">
            <div v-for="card in cards" :key="card.id" 
                class="bg-white rounded-2xl border-0 shadow-card p-5 hover:shadow-card-hover transition-all duration-300 relative cursor-pointer group animate-fade-in flex flex-col"
                :class="{'ring-2 ring-pomegranate-500 border-pomegranate-200 bg-pomegranate-50/20': selectedCards.includes(card.id), 'border-0': !selectedCards.includes(card.id), 'opacity-50 grayscale': card.is_active === false}"
                @click="openCardEditor(card)">
                
                <!-- Selection Checkbox -->
                <div class="absolute top-4 right-4 z-10" @click.stop>
                    <input type="checkbox" :value="card.id" v-model="selectedCards" class="w-5 h-5 text-pomegranate-500 rounded-full border-gray-300 focus:ring-pomegranate-500 focus:ring-2 cursor-pointer transition-all">
                </div>

                <div class="flex justify-between items-start mb-3 pr-8">
                    <h4 class="font-bold text-graphite line-clamp-2 text-base tracking-tight">
                        <span v-if="card.is_active === false" class="text-xs bg-red-100 text-red-600 px-2 py-1 rounded-full mr-2 border border-red-200 inline-flex items-center gap-1">
                            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-3 h-3"><circle cx="12" cy="12" r="10"/><line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/></svg>
                            已禁用
                        </span>
                        {{ card.title }}
                    </h4>
                    <span class="text-[10px] font-mono font-bold text-pomegranate-600 bg-pomegranate-50 px-2 py-1 rounded-lg">#{{ card.id }}</span>
                </div>
                <div class="text-xs text-dark-gray mb-4 line-clamp-3 leading-relaxed">{{ card.content }}</div>
                <div class="flex justify-between items-center text-[10px] mb-3">
                    <span :class="{'text-green-600 font-semibold bg-green-50 px-2 py-1 rounded-lg': card.status==='DONE', 'text-blue-600 font-semibold bg-blue-50 px-2 py-1 rounded-lg': card.status==='DOING', 'text-gray-500 font-semibold bg-gray-50 px-2 py-1 rounded-lg': card.status==='TODO'}">{{ card.status }}</span>
                    <span class="font-bold text-sm text-graphite">¥{{ formatNumber(card.budget) }}</span>
                </div>
                <!-- Progress Bar -->
                <div class="mt-2 w-full bg-gray-100 rounded-full h-2">
                    <div class="bg-gradient-to-r from-pomegranate-400 to-pomegranate-600 h-2 rounded-full-all transition duration-500" :style="{ width: (card.progress || 0) + '%' }"></div>
                </div>
            </div>
            <div v-if="cards.length === 0" class="col-span-full text-center py-16 text-medium-gray">
                <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="mx-auto mb-4 text-light-gray"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="9" y1="9" x2="15" y2="15"/><line x1="15" y1="9" x2="9" y2="15"/></svg>
                <p class="text-lg font-medium">暂无关联卡片</p>
                <p class="text-sm mt-1">点击上方"新增卡片"按钮开始创建</p>
            </div>
        </div>
      </div>
    </main>
    <div v-else class="flex-1 flex items-center justify-center">
        <div class="text-gray-500">加载中...</div>
    </div>

    <!-- Card Editor modal is no longer used, as we use StandaloneCardEditor in a new window -->
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { createIcons, icons } from 'lucide';
import { ElMessage } from 'element-plus';
import api from '../../api';

const route = useRoute();
const router = useRouter();
const projectId = route.params.id;

const project = ref<any>(null);
const cards = ref<any[]>([]);
const viewMode = ref('grid');

const opportunityLoading = ref(false);
const opportunityOptions = ref<any[]>([]);

const statusOptions = [
  { value: 'PLANNING', label: '规划中' },
  { value: 'IN_PROGRESS', label: '进行中' },
  { value: 'COMPLETED', label: '已完成' },
  { value: 'PAUSED', label: '项目暂停' },
  { value: 'TERMINATED', label: '项目终止' }
];

const stageOptions = computed(() => {
  if (!project.value) return [];
  const status = project.value.status;
  if (status === 'PLANNING') {
    return [
      { value: 'OPPORTUNITY', label: '商机阶段' },
      { value: 'PROPOSAL', label: '规划阶段' },
      { value: 'INITIATION', label: '立项阶段' }
    ];
  } else if (status === 'IN_PROGRESS') {
    return [
      { value: 'CONTRACT_SIGNED', label: '已签合同' },
      { value: 'IMPLEMENTING', label: '实施阶段' },
      { value: 'ACCEPTANCE', label: '验收阶段' },
      { value: 'AFTER_SALES', label: '售后阶段' },
      { value: 'PAYMENT_IN_PROGRESS', label: '已经回款' }
    ];
  } else if (status === 'COMPLETED') {
    return [
      { value: 'ARCHIVED', label: '已归档' }
    ];
  }
  return [];
});

const rhythmOptions = [
  { value: 'DAILY', label: '每日跟进' },
  { value: 'WEEKLY', label: '每周跟进' },
  { value: 'BIWEEKLY', label: '两周一跟' },
  { value: 'MONTHLY', label: '每月跟进' },
  { value: 'AS_NEEDED', label: '按需跟进' }
];

watch(() => project.value?.status, (newStatus, oldStatus) => {
  if (newStatus && oldStatus && newStatus !== oldStatus) {
    // Reset stage to the first valid option for the new status
    if (newStatus === 'PLANNING') project.value.stage = 'OPPORTUNITY';
    else if (newStatus === 'IN_PROGRESS') project.value.stage = 'CONTRACT_SIGNED';
    else if (newStatus === 'COMPLETED') project.value.stage = 'ARCHIVED';
  }
});

async function searchOpportunities(query: string) {
  opportunityLoading.value = true;
  try {
    const res = await api.get('opportunities/', { params: { search: query } });
    opportunityOptions.value = (res.data.results || res.data || []);
  } catch (e) {
    console.error("Failed to search opportunities", e);
  } finally {
    opportunityLoading.value = false;
  }
}



const inputState = ref({
    sales_managers: '',
    delivery_managers: '',
    product_managers: ''
});

const sales_manager_input = ref<HTMLInputElement|null>(null);
const delivery_managers_input = ref<HTMLInputElement|null>(null);
const product_managers_input = ref<HTMLInputElement|null>(null);

const userOptions = ref<any[]>([]);

const salesOptions = computed(() => {
    return userOptions.value.filter(u => {
        return u.job_series === 'S' || u.department_category === 'SALES' || u.department === '销售部';
    });
});

const deliveryOptions = computed(() => {
    return userOptions.value.filter(u => {
        const isPOC = u.department_category === 'POC' || u.department === '春秋GAME';
        const isPresales = (u.job_position || '').includes('售前') || (u.job_position || '').includes('实施') || (u.job_position || '').includes('交付');
        return isPOC || isPresales;
    });
});

const productOptions = computed(() => {
    return userOptions.value.filter(u => {
        // Exclude Marketing from Product (User request)
        if (u.department && u.department.includes('市场')) return false;
        
        const isRND = u.department_category === 'RND' || u.department === '研发中心';
        const isProduct = u.job_position === 'PRODUCT_MANAGER' || (u.job_position || '').includes('产品');
        return isRND || isProduct;
    });
});

function addTag(field: 'sales_managers' | 'delivery_managers' | 'product_managers') {
    const val = inputState.value[field].trim();
    if (!val) return;
    
    if (!project.value.extra_data) project.value.extra_data = {};
    if (!project.value.extra_data[field]) project.value.extra_data[field] = [];
    
    const arr = project.value.extra_data[field];
    if (!arr.includes(val)) {
        project.value.extra_data[field].push(val);
        // Force reactivity with new object ref
        project.value = { ...project.value };
        
        // Frontend Sync: If updating sales_managers, update owner_name for display
        if (field === 'sales_managers' && project.value.extra_data.sales_managers.length > 0) {
            project.value.owner_name = project.value.extra_data.sales_managers[0];
        }
    }
    inputState.value[field] = '';
}

function removeTag(field: 'sales_managers' | 'delivery_managers' | 'product_managers', index: any) {
    if (project.value.extra_data && project.value.extra_data[field]) {
        project.value.extra_data[field].splice(index, 1);
        // Force reactivity with new object ref
        project.value = { ...project.value };
    }
}

function focusInput(refName: string) {
    const el = {
        'sales_manager_input': sales_manager_input,
        'delivery_managers_input': delivery_managers_input,
        'product_managers_input': product_managers_input
    }[refName];
    el?.value?.focus();
}

const stats = computed(() => {
    const totalBudget = cards.value.reduce((sum, c) => sum + (Number(c.budget) || 0), 0);
    const totalManDays = cards.value.reduce((sum, c) => sum + (Number(c.man_days) || 0), 0);
    return { totalBudget, totalManDays };
});

async function fetchUsers() {
    try {
        const res = await api.get('users/simple/');
        userOptions.value = res.data.results || [];
    } catch (e) { console.error(e); }
}

onMounted(async () => {
    fetchUsers();
    await loadData();
});

watch([project, cards, viewMode], async () => {
    await nextTick();
    createIcons({ icons });
});

async function loadData() {
    try {
        const pRes = await api.get(`/projects/${projectId}/`);
        project.value = pRes.data;
        // Ensure extra_data exists
        if (!project.value.extra_data) project.value.extra_data = {};
        if (!project.value.extra_data.deliverables) project.value.extra_data.deliverables = [];

        // Pre-load associated opportunity if exists
        if (project.value.opportunity) {
            try {
                // If opportunity is just an ID, fetch details
                // If API returns object, use it directly (but usually DRF returns ID)
                const oppId = typeof project.value.opportunity === 'object' ? project.value.opportunity.id : project.value.opportunity;
                const oppRes = await api.get(`/opportunities/${oppId}/`);
                opportunityOptions.value = [oppRes.data];
                
                // Ensure v-model binds to ID
                if (typeof project.value.opportunity === 'object') {
                    project.value.opportunity = project.value.opportunity.id;
                }
            } catch (e) {
                console.error("Failed to load associated opportunity", e);
            }
        }

        const cRes = await api.get(`/project-cards/`, { params: { project: projectId } });
        cards.value = Array.isArray(cRes.data) ? cRes.data : (cRes.data.results || []);
        
        await nextTick();
        createIcons({ icons });
    } catch (e) {
        console.error("Failed to load project", e);
        // alert("加载失败");
    }
}

async function saveProject() {
    try {
        await api.put(`/projects/${projectId}/`, project.value);
        // Force refresh to update header
        await loadData();
        ElMessage.success('保存成功');
    } catch (e) {
        console.error("Failed to save", e);
        ElMessage.error('保存失败');
    }
}

async function deleteCurrentProject() {
    if(!confirm('确定要删除该项目吗？此操作不可恢复。')) return;
    try {
        await api.delete(`/projects/${projectId}/`);
        router.push('/projects');
    } catch (e) {
        console.error("Failed to delete", e);
        ElMessage.error('删除失败'); 
    }
}

function exportProjectData() {
    const data = {
        project: project.value,
        cards: cards.value
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `project_${project.value.code}.json`;
    a.click();
}

const selectedCards = ref<number[]>([]);

function openTimeline() {
    const url = router.resolve({ name: 'StandaloneProjectTimeline', params: { id: projectId } }).href;
    window.open(url, '_blank');
}

async function batchDelete() {
    if (!selectedCards.value.length) return;
    if (!confirm(`确定要删除选中的 ${selectedCards.value.length} 个卡片吗？`)) return;
    
    try {
        await Promise.all(selectedCards.value.map(id => api.delete(`/project-cards/${id}/`)));
        alert("批量删除成功");
        selectedCards.value = [];
        await loadData();
    } catch(e) {
        console.error(e);
        alert("删除失败");
    }
}

async function batchToggleStatus() {
    if (!selectedCards.value.length) return;
    try {
        // Toggle based on the first card's status (simplify logic)
        const firstCard = cards.value.find(c => c.id === selectedCards.value[0]);
        const targetStatus = !(firstCard?.is_active ?? true);
        
        await Promise.all(selectedCards.value.map(id => 
            api.patch(`/project-cards/${id}/`, { is_active: targetStatus })
        ));
        
        alert(`已${targetStatus ? '启用' : '停用'}选中卡片`);
        selectedCards.value = [];
        await loadData();
    } catch(e) {
        console.error(e);
        alert("操作失败");
    }
}

function importMD() {
    alert("导入Markdown功能开发中...");
}

function exportMD() {
    // Basic Markdown export logic
    if (!selectedCards.value.length) return;
    const targets = cards.value.filter(c => selectedCards.value.includes(c.id));
    let md = `# ${project.value.name}\n\n`;
    targets.forEach(c => {
        md += `## ${c.title} (${c.id})\n`;
        md += `> Status: ${c.status} | Budget: ${c.budget}\n\n`;
        md += `${c.content || 'No content'}\n\n---\n\n`;
    });
    const blob = new Blob([md], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `cards_export_${new Date().toISOString().slice(0,10)}.md`;
    a.click();
}

function exportExcel() {
    alert("导出Excel功能开发中...");
}

function showBudgetStats() {
    alert("预算统计功能开发中...");
}

async function openCardCreator() {
    // 立即打开一个空白窗口，以保留“用户操作”上下文，防止被浏览器拦截
    const newWindow = window.open('about:blank', '_blank');
    if (!newWindow) {
        ElMessage.error('弹出窗口被拦截，请允许浏览器弹出窗口以使用独立编辑器');
        return;
    }

    try {
        // 创建一个带有基本信息的临时卡片
        const payload = {
            title: '新项目卡片',
            content: '',
            budget: 0,
            status: 'TODO',
            project: projectId,
            extra_data: {}
        };
        const res = await api.post(`/project-cards/`, payload);
        if (res.data && res.data.id) {
            // 为新创建的卡片生成独立编辑器的 URL
            const url = router.resolve({ name: 'StandaloneCardEditor', params: { id: res.data.id } }).href;
            // 更新新窗口的地址
            newWindow.location.href = url;
            // 刷新本地数据以显示新卡片
            await loadData();
        } else {
            newWindow.close();
        }
    } catch (e) {
        newWindow.close();
        console.error("Failed to create new card", e);
        ElMessage.error('创建卡片失败');
    }
}

// import CardEditor from '../../components/CardEditor.vue';
// 
// // Card Editor modal state is deprecated in favor of standalone window
// // but we keep refs if needed for other logic (though currently none)
// const showCardEditor = ref(false);
// const editingCard = ref<any>(null);

function openCardEditor(card: any) {
    const url = router.resolve({ name: 'StandaloneCardEditor', params: { id: card.id } }).href;
    window.open(url, '_blank');
}

// Unused handlers since we moved to standalone editor
// async function handleCardSave(updatedData: any) {
//     // Deprecated
// }
// 
// function handlePrevCard() {
//     // Deprecated
// }
// 
// function handleNextCard() {
//     // Deprecated
// }

function addDeliverable() {
    if (!project.value.extra_data.deliverables) project.value.extra_data.deliverables = [];
    project.value.extra_data.deliverables.push('');
}

function removeDeliverable(idx: any) {
    project.value.extra_data.deliverables.splice(idx, 1);
}

function formatNumber(num: any) {
    return Number(num).toLocaleString('zh-CN');
}
</script>

<style scoped>
.custom-scroll::-webkit-scrollbar { width: 6px; }
.custom-scroll::-webkit-scrollbar-track { background: #f1f1f1; }
.custom-scroll::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
</style>
