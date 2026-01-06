<template>
  <div class="h-screen flex flex-col bg-slate-50 overflow-hidden">
    <header class="bg-white shadow-sm px-6 py-4 flex justify-between items-center shrink-0 z-10">
      <div class="flex items-center gap-4">
        <h1 class="text-xl font-bold text-slate-800">CRM 首页</h1>
        <el-breadcrumb separator="/">
          <el-breadcrumb-item :to="{ path: '/' }">大屏首页</el-breadcrumb-item>
          <el-breadcrumb-item>CRM</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div class="flex items-center gap-4">
        <router-link to="/">
          <el-button>战报大屏</el-button>
        </router-link>
      </div>
    </header>

    <main class="flex-1 p-6 overflow-auto">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto">
        <el-card class="hover:shadow-lg transition">
          <template #header>
            <div class="card-header">销售管理</div>
          </template>
          <div class="text-slate-600 mb-4">统一入口：商机、审批、CRM首页</div>
          <div class="flex flex-wrap gap-3">
            <router-link to="/crm/opportunities"><el-button type="primary">商机列表</el-button></router-link>
            <router-link to="/crm/approvals"><el-button>审批中心</el-button></router-link>
            <router-link to="/crm"><el-button>CRM首页</el-button></router-link>
          </div>
        </el-card>

        <el-card class="hover:shadow-lg transition">
          <template #header>
            <div class="card-header">审批中心</div>
          </template>
          <div class="text-slate-600 mb-4">统一查看与处理审批请求</div>
          <router-link to="/crm/approvals">
            <el-button type="primary">打开审批中心</el-button>
          </router-link>
        </el-card>

        <el-card class="hover:shadow-lg transition">
          <template #header>
            <div class="card-header">AI对话窗</div>
          </template>
          <div class="text-slate-600 mb-4">对话式查询与处理业务数据</div>
          <router-link to="/ai/chat">
            <el-button type="primary">打开AI对话窗</el-button>
          </router-link>
        </el-card>

        <el-card class="hover:shadow-lg transition">
          <template #header>
            <div class="card-header">客户关系</div>
          </template>
          <div class="text-slate-600 mb-4">客户与联系人管理</div>
          <div class="flex flex-wrap gap-3">
            <router-link to="/crm/customers"><el-button type="primary">客户列表</el-button></router-link>
            <router-link to="/crm/contacts"><el-button>联系人列表</el-button></router-link>
          </div>
        </el-card>

        <el-card class="hover:shadow-lg transition">
          <template #header>
            <div class="card-header">业绩报表</div>
          </template>
          <div class="text-slate-600 mb-4">目标与实际对比，阶段分布</div>
          <router-link to="/reports/performance">
            <el-button type="primary">打开业绩报表</el-button>
          </router-link>
        </el-card>

        <el-card class="hover:shadow-lg transition">
          <template #header>
            <div class="card-header">社媒管理</div>
          </template>
          <div class="text-slate-600 mb-4">账号与管理员维护，粉丝数据关联</div>
          <div class="flex gap-3">
            <router-link to="/social/accounts">
              <el-button type="primary">账号列表</el-button>
            </router-link>
            <router-link to="/social/stats">
              <el-button>粉丝列表</el-button>
            </router-link>
          </div>
        </el-card>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
// Simple landing page for CRM
</script>

<style scoped>
.card-header { font-weight: 600; }
</style>
