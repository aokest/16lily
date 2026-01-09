<template>
  <div class="h-screen flex flex-col bg-slate-50 overflow-hidden font-sans">
    <!-- Modern Gradient Header -->
    <header class="bg-gradient-to-r from-blue-600 to-indigo-700 shadow-lg px-8 py-5 flex justify-between items-center shrink-0 z-20">
      <div class="flex items-center gap-4">
        <div class="p-2 bg-white/10 rounded-lg backdrop-blur-sm">
           <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
             <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
           </svg>
        </div>
        <div>
            <h1 class="text-xl font-bold text-white tracking-wide">AI 智能中枢</h1>
            <p class="text-xs text-blue-100 opacity-90">全能业务助手 & 决策大脑</p>
        </div>
      </div>
       <el-breadcrumb separator="/" class="!text-blue-100">
          <el-breadcrumb-item :to="{ path: '/' }" class="!text-blue-200 hover:!text-white transition-colors">大屏首页</el-breadcrumb-item>
          <el-breadcrumb-item :to="{ path: '/crm' }" class="!text-blue-200 hover:!text-white transition-colors">CRM首页</el-breadcrumb-item>
          <el-breadcrumb-item class="!text-white font-medium">AI对话窗</el-breadcrumb-item>
        </el-breadcrumb>
    </header>
    
    <main class="flex-1 p-6 overflow-auto bg-slate-50/50">
      <div class="max-w-7xl mx-auto h-full">
      <el-tabs v-model="tab" class="custom-tabs h-full flex flex-col">
        <el-tab-pane label="智能体协作" name="agent" class="h-full">
          <!-- 2-Column Layout -->
          <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 h-full">
            
            <!-- Column 1: Input & Analysis (35%) -->
            <div class="lg:col-span-4 flex flex-col gap-6 h-full overflow-hidden">
                <el-card class="border-0 shadow-md hover:shadow-xl transition-all duration-300 rounded-2xl bg-white flex flex-col h-full">
                  <template #header>
                    <div class="flex items-center gap-2 border-l-4 border-blue-500 pl-3">
                       <span class="font-bold text-lg text-slate-800">指令与分析</span>
                       <span class="text-xs px-2 py-0.5 bg-blue-50 text-blue-600 rounded-full">自然语言</span>
                    </div>
                  </template>
                  <div class="flex-1 flex flex-col gap-4 overflow-y-auto p-1">
                    <!-- Input Area -->
                    <div class="relative">
                        <el-input 
                            v-model="agentText" 
                            type="textarea" 
                            :rows="6" 
                            placeholder="试试这样说：&#10;“帮我创建一个新的销售商机，客户是腾讯科技，预计金额500万”&#10;或&#10;“审批通过所有待办任务”" 
                            class="custom-textarea transition-all duration-300 focus-within:ring-2 ring-blue-100 rounded-lg"
                            resize="none"
                            @keydown.meta.enter="analyzeAgent"
                            @keydown.ctrl.enter="analyzeAgent"
                        />
                        <div class="absolute bottom-3 right-3 text-xs text-slate-400 pointer-events-none">按 Cmd/Ctrl + Enter 发送</div>
                    </div>

                    <!-- AI Intent Analysis Result (Moved from Right) -->
                    <div class="bg-blue-50/50 rounded-xl p-4 border border-blue-100">
                        <div class="flex items-center gap-2 mb-2">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                            <span class="text-sm font-bold text-slate-700">AI 意图识别</span>
                            <el-tag v-if="chosen.intent" type="success" effect="dark" round size="small" class="!px-2 scale-90">已就绪</el-tag>
                            <el-tag v-else type="info" effect="plain" round size="small" class="!px-2 scale-90">等待中</el-tag>
                        </div>
                        
                        <div class="text-sm text-slate-600 font-medium pl-6">
                            {{ humanLabel(chosen) || '等待指令输入...' }}
                        </div>

                        <!-- Alternatives -->
                        <div v-if="agentAlternatives.length > 0" class="mt-3 pl-6">
                            <div class="text-xs text-slate-400 mb-1">其他推测:</div>
                            <div class="flex flex-wrap gap-2">
                                <div 
                                    v-for="(alt,i) in agentAlternatives" 
                                    :key="i" 
                                    class="cursor-pointer px-2 py-0.5 rounded-full border text-xs transition-colors"
                                    :class="chosen === alt ? 'bg-blue-50 border-blue-500 text-blue-700' : 'bg-white border-slate-200 text-slate-600 hover:border-blue-300'"
                                    @click="chooseAlternative(alt)"
                                >
                                    {{ humanLabel(alt) }}
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Model Config & Templates -->
                    <div class="bg-slate-50 p-4 rounded-xl border border-slate-100 space-y-3 mt-auto">
                      <div class="flex items-center justify-between">
                         <span class="text-xs font-semibold text-slate-500 uppercase tracking-wider">模型配置</span>
                         <el-tag size="small" type="info" effect="plain" class="!rounded-full">自动检测</el-tag>
                      </div>
                      <div class="flex flex-col gap-1">
                        <div class="flex gap-2">
                            <el-select 
                                v-model="agentConfigId" 
                                placeholder="请选择AI模型" 
                                class="flex-1 !w-full"
                                no-data-text="暂无可用模型，请联系管理员配置"
                                empty-text="暂无可用模型，请联系管理员配置"
                            >
                            <el-option v-for="c in aiConfigs" :key="c.id" :label="cLabel(c)" :value="String(c.id)" />
                            </el-select>
                            <el-tooltip content="测试模型连通性" placement="top">
                                <el-button @click="testAI" circle plain type="primary" class="!px-3">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                                </el-button>
                            </el-tooltip>
                        </div>
                        <div class="text-[10px] text-slate-400 px-1 flex justify-between">
                            <span>当前可用模型: {{ aiConfigs.length }}</span>
                            <router-link to="/ai/configs" class="text-blue-400 hover:text-blue-600">管理模型</router-link>
                        </div>
                      </div>
                      
                       <div class="grid grid-cols-3 gap-2">
                        <button @click="fillTemplate('approve')" class="text-xs py-1.5 px-2 bg-white border border-slate-200 rounded-lg hover:border-blue-400 hover:text-blue-600 transition-colors text-slate-600 shadow-sm">审批模板</button>
                        <button @click="fillTemplate('customer')" class="text-xs py-1.5 px-2 bg-white border border-slate-200 rounded-lg hover:border-blue-400 hover:text-blue-600 transition-colors text-slate-600 shadow-sm">客户模板</button>
                        <button @click="fillTemplate('opportunity')" class="text-xs py-1.5 px-2 bg-white border border-slate-200 rounded-lg hover:border-blue-400 hover:text-blue-600 transition-colors text-slate-600 shadow-sm">商机模板</button>
                      </div>
                    </div>
    
                    <el-button type="primary" @click="analyzeAgent" :loading="loading" class="w-full !h-12 !text-base !rounded-xl !shadow-lg !shadow-blue-200 hover:!shadow-blue-300 transition-all transform hover:-translate-y-0.5 bg-gradient-to-r from-blue-600 to-indigo-600 border-none">
                        <span class="flex items-center gap-2">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.384-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" /></svg>
                            开始智能分析
                        </span>
                    </el-button>
                  </div>
                </el-card>
            </div>

            <!-- Column 2: Execution (65%) - Pure Execution Panel -->
            <div class="lg:col-span-8 h-full overflow-hidden flex flex-col">
                <el-card class="flex-1 flex flex-col border-0 shadow-lg ring-1 ring-blue-100 rounded-2xl bg-white overflow-hidden" :body-style="{ padding: '0', display: 'flex', flexDirection: 'column', height: '100%' }">
                    <!-- Minimal Header -->
                    <div class="px-5 py-3 border-b border-slate-100 bg-slate-50/50 flex items-center justify-between shrink-0">
                        <div class="flex items-center gap-2">
                            <div class="p-1.5 bg-green-100 text-green-600 rounded-lg">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" /></svg>
                            </div>
                            <h2 class="font-bold text-slate-800 text-base">智能执行面板</h2>
                        </div>
                        <el-button text size="small" @click="showRaw = !showRaw" class="!text-slate-400 hover:!text-blue-500">
                            {{ showRaw ? '隐藏数据' : '查看数据' }}
                        </el-button>
                    </div>

                    <!-- Debug Data Overlay -->
                    <div v-if="showRaw" class="bg-slate-900 p-3 overflow-auto max-h-32 text-xs border-b border-slate-800">
                        <pre class="text-green-400 font-mono whitespace-pre-wrap">{{ JSON.stringify(agentResult, null, 2) }}</pre>
                    </div>

                    <!-- Main Execution Body -->
                    <div class="flex-1 overflow-y-auto p-6 relative bg-white">
                         <!-- Empty State -->
                         <div v-if="!chosen.intent" class="absolute inset-0 flex flex-col items-center justify-center text-slate-300 select-none">
                             <div class="w-32 h-32 bg-slate-50 rounded-full flex items-center justify-center mb-4">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-slate-200" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" /></svg>
                             </div>
                             <p class="text-lg font-medium text-slate-400">请在左侧输入业务指令</p>
                             <p class="text-sm text-slate-400 mt-2">例如：“创建腾讯科技商机” 或 “审批所有请求”</p>
                         </div>
                         
                         <!-- Active Form -->
                         <div v-else class="max-w-4xl mx-auto space-y-6">
                            <div v-if="warnings.length" class="space-y-2">
                              <el-alert v-for="(w, i) in warnings" :key="i" :title="w" type="warning" show-icon :closable="false" />
                            </div>
                            
                            <!-- Dynamic Forms -->
                            <div v-if="chosen.entity==='customer' && chosen.intent==='create'" class="space-y-4">
                              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                                  <div><div class="text-sm font-medium text-slate-700 mb-1.5">客户名称</div><el-input v-model="execFields.name" placeholder="客户名称" size="large" /></div>
                                  <div><div class="text-sm font-medium text-slate-700 mb-1.5">行业</div><el-input v-model="execFields.industry" placeholder="行业" size="large" /></div>
                                  <div><div class="text-sm font-medium text-slate-700 mb-1.5">区域</div><el-input v-model="execFields.region" placeholder="区域" size="large" /></div>
                                  <div><div class="text-sm font-medium text-slate-700 mb-1.5">客户状态</div>
                                  <el-select v-model="execFields.status" placeholder="客户状态" class="w-full" size="large">
                                    <el-option label="潜在客户" value="POTENTIAL" />
                                    <el-option label="合作中" value="ACTIVE" />
                                    <el-option label="重点客户" value="KEY" />
                                    <el-option label="流失客户" value="CHURNED" />
                                  </el-select></div>
                              </div>
                            </div>
                            <div v-else-if="chosen.entity==='approvals' && (chosen.intent==='approve' || chosen.intent==='reject')" class="space-y-4">
                               <div><div class="text-sm font-medium text-slate-700 mb-1.5">审批ID</div><el-input v-model="execFields.id" placeholder="审批ID" disabled size="large" /></div>
                               <div><div class="text-sm font-medium text-slate-700 mb-1.5">审批备注</div><el-input v-model="execFields.reason" placeholder="审批备注" type="textarea" :rows="3" size="large" /></div>
                            </div>
                            <div v-else-if="chosen.entity==='activity' && chosen.intent==='create'" class="space-y-4">
                              <div><div class="text-sm font-medium text-slate-700 mb-1.5">活动名称</div><el-input v-model="execFields.name" placeholder="活动名称" size="large" /></div>
                              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                                  <div><div class="text-sm font-medium text-slate-700 mb-1.5">活动时间</div><el-date-picker v-model="execFields.time" type="date" placeholder="活动时间" class="!w-full" size="large" /></div>
                                  <div><div class="text-sm font-medium text-slate-700 mb-1.5">活动地点</div><el-input v-model="execFields.location" placeholder="活动地点" size="large" /></div>
                                  <div><div class="text-sm font-medium text-slate-700 mb-1.5">活动类型</div><el-input v-model="execFields.type" placeholder="活动类型" size="large" /></div>
                                  <div><div class="text-sm font-medium text-slate-700 mb-1.5">规模</div><el-input v-model="execFields.scale" placeholder="规模（可选）" size="large" /></div>
                              </div>
                            </div>
                            <div v-else-if="chosen.entity==='competition' && chosen.intent==='create'" class="space-y-4">
                              <div><div class="text-sm font-medium text-slate-700 mb-1.5">赛事名称</div><el-input v-model="execFields.name" size="large" /></div>
                              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                                  <div><div class="text-sm font-medium text-slate-700 mb-1.5">开始时间</div><el-date-picker v-model="execFields.time" type="date" class="!w-full" size="large" /></div>
                                  <div><div class="text-sm font-medium text-slate-700 mb-1.5">结束时间</div><el-date-picker v-model="execFields.end_time" type="date" class="!w-full" size="large" /></div>
                                  <div><div class="text-sm font-medium text-slate-700 mb-1.5">地点</div><el-input v-model="execFields.location" size="large" /></div>
                                  <div><div class="text-sm font-medium text-slate-700 mb-1.5">类型</div><el-input v-model="execFields.type" size="large" /></div>
                                  <div><div class="text-sm font-medium text-slate-700 mb-1.5">队伍数量</div><el-input v-model="execFields.team_count" size="large" /></div>
                                  <div><div class="text-sm font-medium text-slate-700 mb-1.5">题目数量</div><el-input v-model="execFields.challenge_count" size="large" /></div>
                                  <div><div class="text-sm font-medium text-slate-700 mb-1.5">赛制</div><el-select v-model="execFields.system_format" class="!w-full" size="large">
                                    <el-option label="夺旗赛" value="CTF" />
                                <el-option label="攻防赛" value="AWD" />
                                <el-option label="攻防演练" value="攻防演练" />
                                  </el-select></div>
                                  <div><div class="text-sm font-medium text-slate-700 mb-1.5">主办类型</div><el-select v-model="execFields.host_type" class="!w-full" size="large">
                                    <el-option label="集团" value="Group" />
                                    <el-option label="学校" value="School" />
                                    <el-option label="政府/协会" value="Gov" />
                                  </el-select></div>
                                  <div><div class="text-sm font-medium text-slate-700 mb-1.5">级别</div><el-select v-model="execFields.level" class="!w-full" size="large">
                                    <el-option label="国家级" value="National" />
                                    <el-option label="省级" value="Province" />
                                    <el-option label="市级" value="City" />
                                  </el-select></div>
                                  <div><div class="text-sm font-medium text-slate-700 mb-1.5">影响力</div><el-select v-model="execFields.impact_level" class="!w-full" size="large">
                                    <el-option label="国家级" value="国家级" />
                                    <el-option label="省级" value="省级" />
                                    <el-option label="市级" value="市级" />
                                  </el-select></div>
                                  <div><div class="text-sm font-medium text-slate-700 mb-1.5">面向对象</div><el-select v-model="execFields.target_audience" class="!w-full" size="large">
                                    <el-option label="高校" value="高校" />
                                    <el-option label="企业" value="企业" />
                                    <el-option label="政府" value="政府" />
                                  </el-select></div>
                                  <div><div class="text-sm font-medium text-slate-700 mb-1.5">行业</div><el-select v-model="execFields.industry" class="!w-full" size="large">
                                    <el-option label="能源" value="能源" />
                                    <el-option label="教育" value="教育" />
                                    <el-option label="政府" value="政府" />
                                    <el-option label="其他" value="其他" />
                                  </el-select></div>
                              </div>
                            </div>
                            <div v-else-if="chosen.entity==='opportunity' && chosen.intent==='create'" class="space-y-4">
                              <div>
                                <div class="text-sm font-medium text-slate-700 mb-1.5">商机名称</div>
                                <el-input v-model="execFields.name" size="large" />
                              </div>
                              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                                  <div>
                                    <div class="text-sm font-medium text-slate-700 mb-1.5">客户名称</div>
                                    <el-input v-model="execFields.customer_name" size="large" />
                                  </div>
                                  <div>
                                    <div class="text-sm font-medium text-slate-700 mb-1.5">预估金额</div>
                                    <el-input v-model="execFields.amount" size="large" />
                                  </div>
                                  <div>
                                    <div class="text-sm font-medium text-slate-700 mb-1.5">阶段</div>
                                    <el-select v-model="execFields.stage" class="!w-full" size="large">
                                      <el-option label="初步接触" value="INITIAL" />
                                      <el-option label="需求分析" value="QUALIFICATION" />
                                      <el-option label="方案制定" value="PROPOSAL" />
                                      <el-option label="商务谈判" value="NEGOTIATION" />
                                      <el-option label="赢单" value="CLOSED_WON" />
                                    </el-select>
                                  </div>
                                  <div>
                                      <div class="text-sm font-medium text-slate-700 mb-1.5">预计签约</div>
                                      <el-date-picker v-model="execFields.expected_sign_date" type="date" class="!w-full" size="large" />
                                  </div>
                              </div>
                            </div>
        
                            <!-- Actions -->
                            <div class="flex flex-col gap-4 pt-6 border-t border-slate-100 mt-6">
                              <el-input v-model="refineText" placeholder="补充说明（如：行业改为教育，区域北京）" class="w-full" size="large">
                                  <template #append>
                                      <el-button @click="refineFields">AI修正</el-button>
                                  </template>
                              </el-input>
                              <div class="flex items-center gap-4">
                                  <el-button type="success" size="large" @click="executeChosenWithFields" :loading="loading" class="flex-1 !px-6 shadow-md shadow-green-100 !h-12 !text-base !rounded-xl">确认执行</el-button>
                                  <el-button v-if="chosen.entity==='customer' && chosen.intent==='create'" @click="openOriginalForm" text size="large">打开原表单</el-button>
                              </div>
                            </div>
                         </div>
                    </div>
                </el-card>
            </div>

          </div>
        </el-tab-pane>
        <el-tab-pane label="审批助手" name="approvals">
          <div class="flex items-center gap-3 mb-3">
            <el-select v-model="approvalStatus" placeholder="状态" clearable style="width: 160px">
              <el-option label="待确认" value="PENDING" />
              <el-option label="已确认" value="APPROVED" />
              <el-option label="已驳回" value="REJECTED" />
            </el-select>
            <el-button type="primary" @click="loadApprovals" :loading="loading">加载审批</el-button>
            <el-button @click="presetPending">我的待办</el-button>
            <el-button @click="presetHandled">我已处理</el-button>
            <el-input v-model="bulkReason" placeholder="批量备注" style="width: 240px" />
            <el-button type="success" :disabled="!selectedApprovalIds.length" @click="bulkApprove">批量通过</el-button>
            <el-button type="danger" :disabled="!selectedApprovalIds.length" @click="bulkReject">批量驳回</el-button>
          </div>
          <el-table :data="approvals" v-loading="loading" @selection-change="onApprovalSelection" style="width:100%">
            <el-table-column type="selection" width="48" />
            <el-table-column prop="id" label="编号" width="80" />
            <el-table-column prop="model_name" label="业务类型" width="120">
              <template #default="{row}">
                <el-tag effect="plain" size="small">{{ row.model_name || row.model_key }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="object_summary" label="审批内容" min-width="200">
              <template #default="{row}">
                <div class="font-medium text-slate-800">{{ row.object_summary }}</div>
                <div class="text-xs text-slate-400">ID: {{ row.object_id }}</div>
              </template>
            </el-table-column>
            <el-table-column prop="applicant_name" label="申请人" width="120" />
            <el-table-column prop="approver_name" label="审批人" width="120" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{row}">
                <el-tag v-if="row.status==='PENDING'" type="warning">待确认</el-tag>
                <el-tag v-else-if="row.status==='APPROVED'" type="success">已通过</el-tag>
                <el-tag v-else-if="row.status==='REJECTED'" type="danger">已驳回</el-tag>
                <el-tag v-else type="info">{{ formatStatus(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="reason" label="理由" />
            <el-table-column label="操作" width="220" fixed="right">
              <template #default="scope">
                <div class="flex items-center gap-2">
                  <el-input v-model="rowOpinion[scope.row.id]" placeholder="备注" size="small" style="width: 140px" />
                  <el-button size="small" type="success" @click="approve(scope.row)">通过</el-button>
                  <el-button size="small" type="danger" @click="reject(scope.row)">驳回</el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        <el-tab-pane label="客户助手" name="customers">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <el-card>
              <template #header>新建客户</template>
              <div class="space-y-3">
                <el-input v-model="custForm.name" placeholder="客户名称" />
                <div class="flex gap-3">
                  <el-input v-model="custForm.industry" placeholder="行业" />
                  <el-input v-model="custForm.region" placeholder="区域" />
                </div>
                <el-select v-model="custForm.status" placeholder="客户状态">
                  <el-option label="潜在客户" value="POTENTIAL" />
                  <el-option label="合作中" value="ACTIVE" />
                  <el-option label="重点客户" value="KEY" />
                  <el-option label="流失客户" value="CHURNED" />
                </el-select>
                <el-button type="primary" @click="createCustomer" :loading="loading">创建客户</el-button>
              </div>
            </el-card>
            <el-card>
              <template #header>客户查询</template>
              <div class="flex items-center gap-3 mb-3">
                <el-input v-model="custSearch" placeholder="搜索名称/行业/区域" />
                <el-button type="primary" @click="listCustomers" :loading="loading">搜索</el-button>
              </div>
              <el-table :data="customerList" size="small" v-loading="loading">
                <el-table-column prop="name" label="客户名称" />
                <el-table-column prop="industry" label="行业" width="140" />
                <el-table-column prop="region" label="区域" width="120" />
                <el-table-column prop="status" label="状态" width="120">
                  <template #default="{row}">{{ formatStatus(row.status) }}</template>
                </el-table-column>
              </el-table>
            </el-card>
          </div>
        </el-tab-pane>
        <el-tab-pane label="商机助手" name="opportunities">
          <el-card>
            <template #header>智能识别新商机</template>
            <div class="space-y-3">
              <el-input v-model="oppText" type="textarea" :rows="6" placeholder="输入商机描述，系统自动识别关键字段并生成商机" />
              <div class="flex items-center gap-3">
                <el-button type="primary" @click="aiParseOpportunity" :loading="loading">AI识别</el-button>
                <el-button @click="createOpportunity" :disabled="!oppParsed?.name" :loading="loading">创建商机</el-button>
              </div>
              <div v-if="oppParsed" class="bg-slate-50 p-3 rounded border text-sm">
                识别结果：名称 {{ oppParsed.name || '-' }}，金额 {{ oppParsed.amount || '-' }}，客户 {{ oppParsed.customer_name || '-' }}，阶段 {{ oppParsed.stage || '-' }}
              </div>
            </div>
          </el-card>
        </el-tab-pane>
        <el-tab-pane label="活动助手" name="activities">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <el-card>
              <template #header>创建活动</template>
              <div class="space-y-3">
                <el-input v-model="actForm.name" placeholder="活动名称" />
                <div class="flex gap-3">
                  <el-date-picker v-model="actForm.time" type="date" placeholder="活动时间" style="width: 180px" />
                  <el-input v-model="actForm.location" placeholder="活动地点" />
                </div>
                <el-input v-model="actForm.type" placeholder="活动类型" />
                <el-input v-model="actForm.scale" placeholder="规模" />
                <el-button type="primary" @click="createActivity" :loading="loading">创建活动</el-button>
              </div>
            </el-card>
            <el-card>
              <template #header>活动查询</template>
              <div class="flex items-center gap-3 mb-3">
                <el-select v-model="actFilters.status" placeholder="状态" clearable style="width: 160px">
                  <el-option label="草稿" value="DRAFT" />
                  <el-option label="待确认" value="PENDING" />
                  <el-option label="已确认" value="APPROVED" />
                  <el-option label="已驳回" value="REJECTED" />
                </el-select>
                <el-input v-model="actFilters.name" placeholder="名称包含" />
                <el-button type="primary" @click="loadActivities" :loading="loading">搜索</el-button>
              </div>
              <el-table :data="actList" size="small" v-loading="loading">
                <el-table-column prop="name" label="活动名称" />
                <el-table-column prop="status" label="状态" width="120">
                  <template #default="{row}">{{ formatStatus(row.status) }}</template>
                </el-table-column>
                <el-table-column prop="time" label="时间" width="160" />
                <el-table-column prop="location" label="地点" />
                <el-table-column prop="type" label="类型" width="120" />
              </el-table>
            </el-card>
          </div>
        </el-tab-pane>
        <el-tab-pane label="赛事助手" name="competitions">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <el-card>
              <template #header>创建赛事</template>
              <div class="space-y-3">
                <el-input v-model="compForm.name" placeholder="赛事名称" />
                <div class="flex gap-3">
                  <el-date-picker v-model="compForm.time" type="date" placeholder="开始时间" style="width: 180px" />
                  <el-date-picker v-model="compForm.end_time" type="date" placeholder="结束时间" style="width: 180px" />
                </div>
                <el-input v-model="compForm.location" placeholder="地点" />
                <el-input v-model="compForm.type" placeholder="类型" />
                <el-button type="primary" @click="createCompetition" :loading="loading">创建赛事</el-button>
              </div>
            </el-card>
            <el-card>
              <template #header>赛事查询</template>
              <div class="flex items-center gap-3 mb-3">
                <el-select v-model="compFilters.status" placeholder="状态" clearable style="width: 160px">
                  <el-option label="草稿" value="DRAFT" />
                  <el-option label="待确认" value="PENDING" />
                  <el-option label="已确认" value="APPROVED" />
                  <el-option label="已驳回" value="REJECTED" />
                </el-select>
                <el-input v-model="compFilters.name" placeholder="名称包含" />
                <el-button type="primary" @click="loadCompetitions" :loading="loading">搜索</el-button>
              </div>
              <el-table :data="compList" size="small" v-loading="loading">
                <el-table-column prop="name" label="赛事名称" />
                <el-table-column prop="status" label="状态" width="120">
                  <template #default="{row}">{{ formatStatus(row.status) }}</template>
                </el-table-column>
                <el-table-column prop="time" label="开始时间" width="160" />
                <el-table-column prop="end_time" label="结束时间" width="160" />
                <el-table-column prop="location" label="地点" />
                <el-table-column prop="type" label="类型" width="120">
                  <template #default="{row}">{{ formatStatus(row.type) }}</template>
                </el-table-column>
              </el-table>
            </el-card>
          </div>
        </el-tab-pane>
        <el-tab-pane label="日报助手" name="daily_reports">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <el-card>
              <template #header>生成日报</template>
              <div class="space-y-3">
                <div class="text-sm text-slate-500 mb-2">请输入今日工作要点、关键词或草稿，AI将为您生成结构化日报。</div>
                <el-input v-model="dailyReportInput" type="textarea" :rows="8" placeholder="例如：
1. 完成了商机跟进模块的API开发
2. 修复了首页加载慢的问题
3. 明日计划：联调前端页面" />
                <el-button type="primary" @click="generateDailyReport" :loading="loading" class="w-full">生成日报</el-button>
              </div>
            </el-card>
            <el-card>
              <template #header>日报预览与保存</template>
              <div v-if="dailyReportResult" class="space-y-4">
                 <div>
                    <div class="text-xs text-slate-500 mb-1">标题</div>
                    <el-input v-model="dailyReportResult.title" />
                 </div>
                 <div>
                    <div class="text-xs text-slate-500 mb-1">内容 (Markdown)</div>
                    <el-input v-model="dailyReportResult.content" type="textarea" :rows="10" />
                 </div>
                 <div class="flex items-center gap-3">
                    <el-date-picker v-model="dailyReportResult.date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" style="width: 160px" />
                    <el-button type="success" @click="saveGeneratedReport" :loading="loading">保存日报</el-button>
                 </div>
              </div>
              <div v-else class="h-64 flex items-center justify-center text-slate-400 text-sm border-2 border-dashed border-slate-200 rounded">
                生成结果将显示在这里
              </div>
            </el-card>
          </div>
        </el-tab-pane>
      </el-tabs>
      </div>
    </main>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import api from '../../api';
import { ElMessage } from 'element-plus';

const tab = ref('agent');
const loading = ref(false);

// 审批
const approvals = ref<any[]>([]);
const approvalStatus = ref<string>('');
const selectedApprovalIds = ref<number[]>([]);
const rowOpinion = ref<Record<number,string>>({});
const bulkReason = ref('');
function onApprovalSelection(rows:any[]){ selectedApprovalIds.value = rows.map(r => r.id); }
const preset = ref<string>('');
function presetPending(){ preset.value = 'pending'; approvalStatus.value=''; loadApprovals(); }
function presetHandled(){ preset.value = 'handled'; approvalStatus.value=''; loadApprovals(); }
async function loadApprovals(){
  loading.value = true;
  try{
    const params:any = {}; 
    if (approvalStatus.value) params.status = approvalStatus.value;
    if (preset.value === 'handled') params.status = ['APPROVED','REJECTED'];
    if (preset.value === 'pending') params.status = ['PENDING'];
    const res = await api.get('approvals/', { params });
    approvals.value = res.data.results || res.data || [];
  }catch(e){ console.error(e); ElMessage.error('加载失败'); } finally{ loading.value = false; }
}
async function approve(row:any){
  try{ await api.post(`approvals/${row.id}/approve/`, { reason: rowOpinion.value[row.id] || '' }); ElMessage.success('已通过'); loadApprovals(); }catch(e){ ElMessage.error('操作失败'); }
}
async function reject(row:any){
  try{ await api.post(`approvals/${row.id}/reject/`, { reason: rowOpinion.value[row.id] || '' }); ElMessage.success('已驳回'); loadApprovals(); }catch(e){ ElMessage.error('操作失败'); }
}
async function bulkApprove(){
  try{
    await api.post('approvals/bulk_approve/', { ids: selectedApprovalIds.value, reason: bulkReason.value });
    ElMessage.success('批量通过完成'); loadApprovals();
  }catch(e){ ElMessage.error('批量失败'); }
}
async function bulkReject(){
  try{
    await api.post('approvals/bulk_reject/', { ids: selectedApprovalIds.value, reason: bulkReason.value });
    ElMessage.success('批量驳回完成'); loadApprovals();
  }catch(e){ ElMessage.error('批量失败'); }
}

// 客户
const custForm = ref<any>({ name:'', industry:'', region:'', status:'POTENTIAL' });
const custSearch = ref(''); const customerList = ref<any[]>([]);
async function createCustomer(){
  if (!custForm.value.name){ ElMessage.warning('请输入客户名称'); return; }
  loading.value = true;
  try{
    // @ts-ignore
    const res = await api.post('chat/', { intent: 'create', entity: 'customer', fields: { ...custForm.value } });
    if (res) {
        // use res
    }
    ElMessage.success('创建成功');
  }catch(e){ console.error(e); ElMessage.error('创建失败'); }
  finally{ loading.value = false; }
}
async function listCustomers(){
  loading.value = true;
  try{
    const res = await api.post('chat/', { intent: 'list', entity: 'customer', filters: { name: custSearch.value, industry: custSearch.value } });
    customerList.value = res.data.result || [];
  }catch(e){ console.error(e); ElMessage.error('查询失败'); }
  finally{ loading.value = false; }
}

// 商机（AI识别）
const oppText = ref(''); const oppParsed = ref<any>(null);
async function aiParseOpportunity(){
  if (!oppText.value){ ElMessage.warning('请输入商机描述'); return; }
  loading.value = true;
  try{
    const res = await api.post('ai/analyze/', { text: oppText.value, mode: 'OPPORTUNITY' });
    if (res.data.error){ ElMessage.error(res.data.error); } else { oppParsed.value = res.data; ElMessage.success('识别成功'); }
  }catch(e){ console.error(e); ElMessage.error('识别失败'); } finally{ loading.value = false; }
}
async function createOpportunity(){
  if (!oppParsed.value){ ElMessage.warning('请先识别商机'); return; }
  loading.value = true;
  try{
    const payload:any = { ...oppParsed.value };
    if (!payload.description && oppText.value) payload.description = oppText.value;
    // @ts-ignore
    const res = await api.post('opportunities/', payload);
    if (res) {
        // use res
    }
    ElMessage.success('商机创建成功');
  }catch(e){ console.error(e); ElMessage.error('创建失败'); } finally{ loading.value = false; }
}
const actFilters = ref<any>({ status: '', name: '' });
const actList = ref<any[]>([]);
const actForm = ref<any>({ name:'', time:'', location:'', type:'', scale:'' });
async function loadActivities(){
  loading.value = true;
  try{
    const res = await api.post('chat/', { intent: 'list', entity: 'activity', filters: { ...actFilters.value } });
    actList.value = res.data.result || [];
  }catch(e){ console.error(e); ElMessage.error('查询失败'); } finally{ loading.value = false; }
}
async function createActivity(){
  if (!actForm.value.name){ ElMessage.warning('请输入活动名称'); return; }
  loading.value = true;
  try{
    await api.post('chat/', { intent: 'create', entity: 'activity', fields: { ...actForm.value } });
    ElMessage.success('创建成功');
    await loadActivities();
  }catch(e){ console.error(e); ElMessage.error('创建失败'); } finally{ loading.value = false; }
}
const compFilters = ref<any>({ status: '', name: '' });
const compList = ref<any[]>([]);
const compForm = ref<any>({ name:'', time:'', end_time:'', location:'', type:'' });
async function loadCompetitions(){
  loading.value = true;
  try{
    const res = await api.post('chat/', { intent: 'list', entity: 'competition', filters: { ...compFilters.value } });
    compList.value = res.data.result || [];
  }catch(e){ console.error(e); ElMessage.error('查询失败'); } finally{ loading.value = false; }
}
async function createCompetition(){
  if (!compForm.value.name){ ElMessage.warning('请输入赛事名称'); return; }
  loading.value = true;
  try{
    await api.post('chat/', { intent: 'create', entity: 'competition', fields: { ...compForm.value } });
    ElMessage.success('创建成功');
    await loadCompetitions();
  }catch(e){ console.error(e); ElMessage.error('创建失败'); } finally{ loading.value = false; }
}
// 智能体
const agentText = ref('');
const agentAlternatives = ref<any[]>([]);
const agentResult = ref<any>(null);
const warnings = ref<string[]>([]);
const chosen = ref<any>({ intent:'', entity:'', fields:{}, filters:{} });
const agentConfigId = ref<string>('');
const showRaw = ref(false);
const aiConfigs = ref<any[]>([]);
function cLabel(c:any){ return `${c.name} · ${c.model_name}${c.is_active ? '（默认）' : ''}`; }

// AI配置加载：修复空列表和错误处理
async function loadAIConfigs(){
  try{
    let res = await api.get('ai/configs/');
    let results = res.data.results || res.data || [];
    
    // Fallback to admin endpoint if empty (in case of permission/url issues)
    if (!results.length) {
        try {
            res = await api.get('admin/ai-configs/');
            results = res.data.results || res.data || [];
        } catch (e) { /* ignore fallback error */ }
    }

    aiConfigs.value = results;
    
    if (aiConfigs.value.length > 0){
        // 如果有配置，优先选中已激活的，否则选第一个
        const active = aiConfigs.value.find((c:any)=>c.is_active);
        agentConfigId.value = String((active || aiConfigs.value[0]).id);
    } else {
        // 无配置时，保持空
        agentConfigId.value = '';
    }
  }catch(e){ 
      console.error('Failed to load AI configs', e);
  }
}
onMounted(loadAIConfigs);

async function testAI(){
  // Auto-select first if not selected but available
  if (!agentConfigId.value && aiConfigs.value.length > 0) {
      agentConfigId.value = String(aiConfigs.value[0].id);
  }

  if (!agentConfigId.value) {
    ElMessage.warning('请先选择一个AI模型配置');
    return;
  }
  loading.value = true;
  try{
    const params:any = {};
    if (agentConfigId.value) params.config_id = agentConfigId.value;
    const res = await api.post('ai/test-connection/', params);
    const r = res.data || {};
    ElMessage.success(`连接成功：${r.provider === 'OPENAI' ? 'OpenAI' : r.provider} · ${r.model || '默认模型'}`);
    showRaw.value = true;
    agentResult.value = r;
  }catch(e:any){
    const msg = (e.response && e.response.data && (e.response.data.error || e.response.data.detail || e.response.data.message)) ? (e.response.data.error || e.response.data.detail || e.response.data.message) : '连接失败';
    ElMessage.error(typeof msg==='string'?msg:JSON.stringify(msg));
  } finally { loading.value = false; }
}
// @ts-ignore
function needsForm(a:any){
  // 所有动作都需要进入“智能执行面板”确认后提交，避免自动执行
  return true;
}
const execFields = ref<any>({});
const execFieldsJson = ref('');
const refineText = ref('');

function syncJsonToFields(){
    try {
        execFields.value = JSON.parse(execFieldsJson.value);
    } catch(e) { /* ignore */ }
}
watch(execFields, (val) => {
    execFieldsJson.value = JSON.stringify(val, null, 2);
}, { deep: true });

async function analyzeAgent(){
  if (!agentText.value){ ElMessage.warning('请输入需求'); return; }
  loading.value = true;
  try{
    const payload:any = { task: agentText.value };
    if (agentConfigId.value) payload.config_id = agentConfigId.value;
    const res = await api.post('agent/route/', payload);
    const data = res.data || {};
    agentResult.value = data;
    if (data.error){
      // 服务器返回错误但HTTP成功 → 启用兜底
      const t = agentText.value;
      if (/商机|机会/.test(t)){
        chosen.value = { intent:'create', entity:'opportunity', fields:{}, filters:{} };
        await autoRefineOpportunity(t);
        ElMessage.warning('模型错误，已使用本地兜底识别商机并填表');
      } else if (/赛事|比赛/.test(t)){
        chosen.value = { intent:'create', entity:'competition', fields:{}, filters:{} };
        await autoRefineCompetition(t);
        ElMessage.warning('模型错误，已使用本地兜底识别赛事并填表');
      } else if (/客户/.test(t) && (/新建|创建/.test(t) || /名称/.test(t))){
        chosen.value = { intent:'create', entity:'customer', fields:{}, filters:{} };
        await autoRefineCustomer(t);
        ElMessage.warning('模型错误，已使用本地兜底识别客户并填表');
      } else if (/活动/.test(t) && (/新建|创建/.test(t) || /名称/.test(t))){
        chosen.value = { intent:'create', entity:'activity', fields:{}, filters:{} };
        await autoRefineActivity(t);
        ElMessage.warning('模型错误，已使用本地兜底识别活动并填表');
      } else {
        ElMessage.error(typeof data.error==='string'?data.error:JSON.stringify(data.error));
      }
    } else {
      chosen.value = { intent: data.intent, entity: data.entity, fields: data.fields || {}, filters: data.filters || {} };
      agentAlternatives.value = data.alternatives || [];
      warnings.value = data.warnings || [];
      // 自动填充建议字段到表单
      execFields.value = { ...(data.fields || {}) };
      // 商机创建：自动进行一次AI补全（金额/客户等）
      if (chosen.value.entity === 'opportunity' && chosen.value.intent === 'create'){
        await autoRefineOpportunity(agentText.value);
      }
      // 赛事创建：自动进行一次AI补全（时间/地点/赛制等）
      if (chosen.value.entity === 'competition' && chosen.value.intent === 'create'){
        await autoRefineCompetition(agentText.value);
      }
      // 如果没有候选且选择为空，兜底
      if ((!chosen.value.intent || !chosen.value.entity) && (!agentAlternatives.value || !agentAlternatives.value.length)){
        const t = agentText.value;
        if (/商机|机会/.test(t)){
          chosen.value = { intent:'create', entity:'opportunity', fields:{}, filters:{} };
          await autoRefineOpportunity(t);
          ElMessage.warning('未识别到明确动作，已兜底为“新建·商机”');
        } else if (/赛事|比赛/.test(t)){
          chosen.value = { intent:'create', entity:'competition', fields:{}, filters:{} };
          await autoRefineCompetition(t);
          ElMessage.warning('未识别到明确动作，已兜底为“新建·赛事”');
        } else if (/客户/.test(t) && (/新建|创建/.test(t) || /名称/.test(t))){
          chosen.value = { intent:'create', entity:'customer', fields:{}, filters:{} };
          await autoRefineCustomer(t);
          ElMessage.warning('未识别到明确动作，已兜底为“新建·客户”');
        } else if (/活动/.test(t) && (/新建|创建/.test(t) || /名称/.test(t))){
          chosen.value = { intent:'create', entity:'activity', fields:{}, filters:{} };
          await autoRefineActivity(t);
          ElMessage.warning('未识别到明确动作，已兜底为“新建·活动”');
        }
      }
      ElMessage.success('分析完成');
    }
  }catch(e:any){ 
    console.error(e); 
    const msg = (e.response && e.response.data && (e.response.data.error || e.response.data.detail)) ? (e.response.data.error || e.response.data.detail) : '分析失败';
    ElMessage.error(typeof msg==='string'?msg:JSON.stringify(msg));
    // 本地兜底：根据文本关键词给出可执行候选并自动填表
    try{
      const t = agentText.value;
      if (/商机|机会/.test(t)){
        chosen.value = { intent:'create', entity:'opportunity', fields:{}, filters:{} };
        await autoRefineOpportunity(t);
        agentResult.value = { fallback: true, intent: 'create', entity: 'opportunity' };
        ElMessage.warning('已使用本地兜底识别商机并填表，请确认后提交');
      } else if (/赛事|比赛/.test(t)){
        chosen.value = { intent:'create', entity:'competition', fields:{}, filters:{} };
        await autoRefineCompetition(t);
        agentResult.value = { fallback: true, intent: 'create', entity: 'competition' };
        ElMessage.warning('已使用本地兜底识别赛事并填表，请确认后提交');
      } else if (/客户/.test(t) && (/新建|创建/.test(t) || /名称/.test(t))){
        chosen.value = { intent:'create', entity:'customer', fields:{}, filters:{} };
        await autoRefineCustomer(t);
        agentResult.value = { fallback: true, intent: 'create', entity: 'customer' };
        ElMessage.warning('已使用本地兜底识别客户并填表，请确认后提交');
      } else if (/活动/.test(t) && (/新建|创建/.test(t) || /名称/.test(t))){
        chosen.value = { intent:'create', entity:'activity', fields:{}, filters:{} };
        await autoRefineActivity(t);
        agentResult.value = { fallback: true, intent: 'create', entity: 'activity' };
        ElMessage.warning('已使用本地兜底识别活动并填表，请确认后提交');
      }
    }catch(_){}
  } finally{ loading.value = false; }
}
function chooseAlternative(alt:any){
  chosen.value = { intent: alt.intent, entity: alt.entity, fields: alt.fields || {}, filters: alt.filters || {} };
}
async function autoRefineCustomer(text:string){
   // 增强正则：支持 "客户名称: XX" 或 "新建客户 XX" 或 "创建客户 XX" 或 "创建一个客户 XX"
   // 排除 。 ; ； 等标点
   const mName = text.match(/客户名称[:：]\s*([^\s，,。;；]+)/) || 
                 text.match(/(?:新建|创建)(?:一个|一项)?客户[，, ]\s*([^\s，,。;；]{2,40})/) ||
                 text.match(/客户[，, ]\s*([^\s，,。;；]{2,40})/);
   if (mName) execFields.value.name = mName[1];

   const mInd = text.match(/行业[:：]\s*([^\s，,。;；]+)/) || text.match(/([^\s，,。;；]+)行业/);
   if (mInd) execFields.value.industry = mInd[1];

   const mReg = text.match(/(?:区域|地点)[:：]\s*([^\s，,。;；]+)/) || 
                text.match(/在([^\s，,。;；]{1,10})/) ||
                text.match(/地点\s*([^\s，,。;；]{1,10})/);
   if (mReg) execFields.value.region = mReg[1];
}
async function autoRefineActivity(text:string){
   const mName = text.match(/活动名称[:：]\s*([^\s，,]+)/) || text.match(/新建(?:一个|一项)?([^\s，,]{2,40})/);
   if (mName) execFields.value.name = mName[1];
   const mLoc = text.match(/(?:地点|在)[:：]\s*([^\s，,]+)/) || text.match(/在([^\s，,]{1,10})/);
   if (mLoc) execFields.value.location = mLoc[1];
   const mType = text.match(/类型[:：]\s*([^\s，,]+)/);
   if (mType) execFields.value.type = mType[1];
   const mDate = text.match(/(\d{4})[-年](\d{1,2})[-月](\d{1,2})/);
   if (mDate) execFields.value.time = `${mDate[1]}-${String(mDate[2]).padStart(2,'0')}-${String(mDate[3]).padStart(2,'0')}`;
}
async function autoRefineOpportunity(text:string){
  try{
    const payload:any = { text, mode: 'OPPORTUNITY' };
    if (agentConfigId.value) payload.config_id = agentConfigId.value;
    let data:any = {};
    try{
      const res = await api.post('ai/analyze/', payload);
      data = res.data || {};
    }catch{}
    execFields.value = { ...(execFields.value || {}), ...(data.error ? {} : data) };
    // 本地兜底：客户名/名称
    if (!execFields.value.customer_name){
      const m = text.match(/客户名称[:：]\s*([^\s，,]+)/) || text.match(/新增(?:一个|一条|一项)?([^\s，,]{2,40})的商机/) || text.match(/([^\s，,]{2,40})商机/);
      if (m) execFields.value.customer_name = m[1];
    }
    if (!execFields.value.name){
      const cname = execFields.value.customer_name || '';
      execFields.value.name = cname ? `${cname}-咨询比赛与演武场` : '咨询比赛与演武场';
    }
    // 金额
    if (!execFields.value.amount){
      const m = text.match(/(预算|金额)\s*([0-9]+(?:\.[0-9]+)?)\s*(千|万|百万|亿)?/);
      if (m){
        // @ts-ignore
        const num = parseFloat(m[2]); const unit = m[3] || '';
        const unitMap:any = { '千':1000,'万':10000,'百万':1000000,'亿':100000000 };
        execFields.value.amount = Math.round(num * (unitMap[unit] || 1));
      } else { execFields.value.amount = 0; }
    }
    // 销售经理
    if (!execFields.value.sales_manager_name){
        const m = text.match(/销售([^\s，,]{2,10})/);
        if (m) execFields.value.sales_manager_name = m[1];
    }
    // 季度 → 预计签约日期
    if (!execFields.value.expected_sign_date){
      const mq = text.match(/明年?\s*Q([1-4])/i) || text.match(/Q([1-4])/i);
      if (mq){
      // @ts-ignore
      const q = parseInt(mq[1],10);
      const middleMonth:any = {1:2,2:5,3:8,4:11}[q];
      const now = new Date(); const y = /明年/.test(text) ? now.getFullYear()+1 : now.getFullYear();
        const pad = (n:number)=>String(n).padStart(2,'0');
        execFields.value.expected_sign_date = `${y}-${pad(middleMonth)}-15`;
      }
    }
    // 阶段/状态
    if (!execFields.value.stage){
      if (/演示/.test(text)) execFields.value.stage = 'DEMO';
      else if (/方案/.test(text)) execFields.value.stage = 'PROPOSAL';
      else if (/谈判/.test(text)) execFields.value.stage = 'NEGOTIATION';
      else if (/临门|签约/.test(text)) execFields.value.stage = 'CLOSING';
      else execFields.value.stage = 'CONTACT';
    }
    // 区域
    if (!execFields.value.customer_region){
      const r1 = text.match(/区域[:：]\s*([^\s，,]+)/);
      const r2 = text.match(/在([^\s，,]{1,10})/);
      if (r1) execFields.value.customer_region = r1[1];
      else if (r2) execFields.value.customer_region = r2[1];
    }
  }catch(e){ /* 忽略失败 */ }
}
async function autoRefineCompetition(text:string){
  try{
    const payload:any = { text, mode: 'COMPETITION' };
    if (agentConfigId.value) payload.config_id = agentConfigId.value;
    let data:any = {};
    try{
      const res = await api.post('ai/analyze/', payload);
      data = res.data || {};
    }catch{}
    execFields.value = { ...(execFields.value || {}), ...(data.error ? {} : data) };
    // 名称
    if (!execFields.value.name){
      const m = text.match(/赛事名称[:：]\s*([^\s，,]+)/) || text.match(/新建(?:一个|一项)?([^\s，,]{2,40})/);
      if (m) execFields.value.name = m[1];
    }
    // 兜底解析模糊时间（上旬/中旬/下旬）
    const fuzzy = text.match(/(\d{1,2})月(上旬|中旬|下旬)/);
    if (fuzzy){
      // @ts-ignore
      const m = parseInt(fuzzy[1],10); const mp:any = { '上旬':5,'中旬':15,'下旬':25 };
      // @ts-ignore
      const d = mp[fuzzy[2]];
      const now = new Date(); const y = /明年/.test(text) ? now.getFullYear()+1 : now.getFullYear();
      const pad = (n:number)=>String(n).padStart(2,'0');
      const ds = `${y}-${pad(m)}-${pad(d)}`;
      if (!execFields.value.time) execFields.value.time = ds;
      if (!execFields.value.end_time) execFields.value.end_time = ds;
    }
    // 兜底解析季度（Q1/Q2/Q3/Q4 → 当季中期）
    const mq = text.match(/Q([1-4])/i);
    if (mq){
      // @ts-ignore
      const q = parseInt(mq[1],10);
      const middleMonth:any = {1:2,2:5,3:8,4:11}[q];
      const now = new Date(); const y = /明年/.test(text) ? now.getFullYear()+1 : now.getFullYear();
      const pad = (n:number)=>String(n).padStart(2,'0');
      const ds = `${y}-${pad(middleMonth)}-15`;
      if (!execFields.value.time) execFields.value.time = ds;
      if (!execFields.value.end_time) execFields.value.end_time = ds;
    }
    // 兜底解析“X天”并根据开始时间自动计算结束时间
    if (execFields.value.time && !execFields.value.end_time){
      const dmatch = text.match(/(\d+)\s*天/);
      if (dmatch){
        // @ts-ignore
        const dur = parseInt(dmatch[1],10);
        const d0 = new Date(execFields.value.time);
        const dEnd = new Date(d0.getTime() + (Math.max(dur-1,0))*24*3600*1000);
        const pad = (n:number)=>String(n).padStart(2,'0');
        execFields.value.end_time = `${dEnd.getFullYear()}-${pad(dEnd.getMonth()+1)}-${pad(dEnd.getDate())}`;
      }
    }
    // 面向对象/行业/影响力标签兜底
    if (!execFields.value.target_audience){
      if (/高校|大学/.test(text)) execFields.value.target_audience = '高校';
      else if (/企业/.test(text)) execFields.value.target_audience = '企业';
      else if (/政府/.test(text)) execFields.value.target_audience = '政府';
    }
    if (!execFields.value.industry){
      if (/电力|能源/.test(text)) execFields.value.industry = '能源';
    }
    if (!execFields.value.impact_level){
      if (/全国/.test(text)) execFields.value.impact_level = '国家级';
      else if (/省/.test(text)) execFields.value.impact_level = '省级';
      else if (/市/.test(text)) execFields.value.impact_level = '市级';
    }
    // 兜底解析地点：匹配“在XX”
    const ml = text.match(/在([^\s，,]{1,10})/);
    if (ml && !execFields.value.location) execFields.value.location = ml[1];
  }catch(e){ /* 忽略失败 */ }
}
async function refineFields(){
  if (!refineText.value){ ElMessage.warning('请输入补充说明'); return; }
  loading.value = true;
  try{
    if (chosen.value.entity === 'opportunity'){
      const payload:any = { text: refineText.value, mode: 'OPPORTUNITY' };
      if (agentConfigId.value) payload.config_id = agentConfigId.value;
      const res = await api.post('ai/analyze/', payload);
      const data = res.data || {};
      if (!data.error){
        execFields.value = { ...(execFields.value || {}), ...data };
        ElMessage.success('已合并AI识别结果');
      } else {
        ElMessage.warning('AI识别失败');
      }
    } else {
      const payload:any = { text: refineText.value };
      if (agentConfigId.value) payload.config_id = agentConfigId.value;
      const res = await api.post('agent/route/', payload);
      const data = res.data || {};
      if (data.entity && data.entity === chosen.value.entity && data.fields){
        execFields.value = { ...(execFields.value || {}), ...data.fields };
        ElMessage.success('已合并补充字段');
      } else {
        ElMessage.warning('补充内容与当前动作不一致，未合并');
      }
    }
  }catch(e){ console.error(e); ElMessage.error('解析失败'); } finally { loading.value = false; }
}
async function executeChosenWithFields(){
  if (!chosen.value.intent || !chosen.value.entity){ ElMessage.warning('请选择动作'); return; }
  loading.value = true;
  try{
    const fields = normalizeFields(chosen.value.entity, execFields.value || {});
    // 如果是创建操作，直接调用对应实体的创建API，确保数据保存
    if (chosen.value.intent === 'create') {
        let url = '';
        if (chosen.value.entity === 'customer') url = 'customers/';
        else if (chosen.value.entity === 'opportunity') url = 'opportunities/';
        else if (chosen.value.entity === 'competition') url = 'competitions/';
        else if (chosen.value.entity === 'activity') url = 'activities/';
        
        if (url) {
            const res = await api.post(url, fields);
            agentResult.value = res.data;
            ElMessage.success('已保存到系统');
            // 清空表单或重置状态? 暂不重置，方便用户继续操作
            loading.value = false;
            return;
        }
    }

    // 默认走 Chat/Agent 路由
    const payload = { 
      intent: chosen.value.intent, 
      entity: chosen.value.entity, 
      fields: fields, 
      filters: chosen.value.filters || {}, 
      text: agentText.value || '',
      message: agentText.value || '执行操作'
    };
    const res = await api.post('chat/', payload);
    agentResult.value = res.data;
    ElMessage.success('执行完成');
  }catch(e:any){ 
    console.error(e); 
    const msg = (e.response && e.response.data && (e.response.data.error || e.response.data.detail)) ? JSON.stringify(e.response.data.error || e.response.data.detail) : '执行失败';
    ElMessage.error(typeof msg==='string'?msg:JSON.stringify(msg));
  } finally { loading.value = false; }
}
// @ts-ignore
function openOriginalForm(){
  // 仅支持客户新建表单的预填
  const q:any = {};
  if (execFields.value.name) q.name = execFields.value.name;
  if (execFields.value.industry) q.industry = execFields.value.industry;
  if (execFields.value.region) q.region = execFields.value.region;
  if (execFields.value.status) q.status = execFields.value.status;
  // 跳到客户创建页并附加 query
  window.location.hash = `#/crm/customers/create?` + new URLSearchParams(q).toString();
}
/** 统一日期/数字等字段的规范化，避免后端校验失败 */
// @ts-ignore
function normalizeFields(entity:string, fields:any){
  const f = { ...(fields || {}) };
  const toDate = (v:any) => {
    if (!v) return v;
    try{
      if (typeof v === 'string') return v; // 可能已是'YYYY-MM-DD'
      if (v instanceof Date) {
        const y = v.getFullYear(); const m = String(v.getMonth()+1).padStart(2,'0'); const d = String(v.getDate()).padStart(2,'0');
        return `${y}-${m}-${d}`;
    }
    }catch(_e){ return v; }
    return v;
  };
  // competition/activity/opportunity日期字段
  f.time = toDate(f.time);
  f.end_time = toDate(f.end_time);
  f.expected_sign_date = toDate(f.expected_sign_date);
  // 金额确保为数字
  if (f.amount && typeof f.amount === 'string'){
    const n = Number(f.amount.replace(/[^\d.]/g,''));
    if (!isNaN(n)) f.amount = n;
  }
  return f;
}

async function genCustomerCode(){
  try {
    const res = await api.get('customers/generate_code/');
    execFields.value.customer_code = res.data.code;
  } catch(e){
    ElMessage.error('生成代号失败');
  }
}

const statusMap: Record<string,string> = {
  'POTENTIAL': '潜在', 'ACTIVE': '合作中', 'KEY': '重点', 'CHURNED': '流失',
  'PENDING': '待确认', 'APPROVED': '已通过', 'REJECTED': '已驳回',
  'INITIAL': '初步接触', 'QUALIFICATION': '需求分析', 'PROPOSAL': '方案制定', 'NEGOTIATION': '商务谈判', 'CLOSED_WON': '赢单', 'CLOSED_LOST': '输单',
  'DRAFT': '草稿',
  'National': '国家级', 'Province': '省级', 'City': '市级',
  'Group': '集团', 'School': '学校', 'Gov': '政府/协会',
  'CTF': '夺旗赛', 'AWD': '攻防赛', '攻防演练': '攻防演练'
};

function formatStatus(val: string) {
    return statusMap[val] || val;
}

function humanLabel(a:any){
  if (!a) return '';
  const intentMap: Record<string,string> = { list:'查看', get:'查看详情', create:'新建', update:'更新', approve:'审批通过', reject:'审批驳回' };
  const entityMap: Record<string,string> = { approvals:'审批', customer:'客户', activity:'活动', competition:'赛事', opportunity:'商机' };
  
  const intentLabel = intentMap[a.intent] || a.intent;
  const entityLabel = entityMap[a.entity] || a.entity;
  // status hint
  const status = a.filters?.status || a.fields?.status;
  let statusLabel = '';
  if (status) {
      if (Array.isArray(status)) {
          statusLabel = `（${status.map(s => statusMap[s] || s).join('/')}）`;
      } else {
          statusLabel = `（${statusMap[status] || status}）`;
      }
  }
  return `${intentLabel} · ${entityLabel}${statusLabel}`;
}
function humanDesc(a:any){
  if (!a) return '';
  const parts:string[] = [];
  if (a.filters && Object.keys(a.filters).length) parts.push(`筛选：${JSON.stringify(a.filters)}`);
  if (a.fields && Object.keys(a.fields).length) parts.push(`参数：${JSON.stringify(a.fields)}`);
  return parts.join('；');
}
function fillTemplate(type:string){
  if (type === 'approve'){
    agentText.value = '审批通过 123，原因：资料齐全';
  } else if (type === 'customer'){
    agentText.value = '新建客户，客户名称：示例公司，行业：教育，区域：北京';
  } else if (type === 'opportunity'){
    agentText.value = '新增一个三峡职业技术学院的商机，他们是老师，想了解一下比赛怎么搞，了解一下演武场。销售魏晶晶';
  }
}
async function executeChosen(){
  if (!chosen.value.intent || !chosen.value.entity){ ElMessage.warning('请选择动作'); return; }
  
  // Sync UI fields back to chosen payload
  chosen.value.fields = { ...chosen.value.fields, ...execFields.value };

  loading.value = true;
  try{
    const payload = { ...chosen.value, message: agentText.value || '执行操作' }; // FIX: Add message
    const res = await api.post('chat/', payload);
    agentResult.value = res.data;
    ElMessage.success('执行完成');
  }catch(e:any){ console.error(e); ElMessage.error('执行失败'); } finally { loading.value = false; }
}

// 日报助手
const dailyReportInput = ref('');
const dailyReportResult = ref<any>(null);

async function generateDailyReport() {
  if (!dailyReportInput.value) {
    ElMessage.warning('请输入工作内容');
    return;
  }
  loading.value = true;
  try {
    const payload: any = { text: dailyReportInput.value, mode: 'DAILY_REPORT' };
    if (agentConfigId.value) payload.config_id = agentConfigId.value;
    const res = await api.post('ai/analyze/', payload);
    const data = res.data;
    if (data.error) {
       ElMessage.error(data.error);
    } else {
       dailyReportResult.value = {
         title: data.title || `${new Date().getFullYear()}-${new Date().getMonth()+1}-${new Date().getDate()} 日报`,
         content: data.content || data.polished_content || dailyReportInput.value,
         date: new Date().toISOString().split('T')[0]
       };
       ElMessage.success('生成成功，请预览并保存');
    }
  } catch (e: any) {
    console.error(e);
    ElMessage.error('生成失败');
  } finally {
    loading.value = false;
  }
}

async function saveGeneratedReport() {
  if (!dailyReportResult.value) return;
  loading.value = true;
  try {
    // Save as daily report
    await api.post('daily-reports/', {
      title: dailyReportResult.value.title,
      content: dailyReportResult.value.content,
      report_date: dailyReportResult.value.date,
      type: 'DAILY'
    });
    ElMessage.success('保存成功');
  } catch (e) {
    ElMessage.error('保存失败');
  } finally {
    loading.value = false;
  }
}
</script>
<style scoped>
.custom-tabs :deep(.el-tabs__header) {
  margin-bottom: 20px;
}
.custom-tabs :deep(.el-tabs__content) {
  height: calc(100% - 60px);
  overflow: hidden;
}
.animate-fade-in-up {
  animation: fadeInUp 0.3s ease-out;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
