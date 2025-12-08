<template>
  <div class="h-screen flex items-center justify-center bg-slate-900">
    <div class="bg-slate-800 p-8 rounded-lg shadow-xl w-96 border border-slate-700">
      <h1 class="text-2xl font-bold text-white mb-6 text-center">登录 CRM 系统</h1>
      <el-form :model="form" @submit.prevent="handleLogin">
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名" size="large" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码" size="large" show-password />
        </el-form-item>
        <el-button type="primary" class="w-full mt-4" size="large" @click="handleLogin" :loading="loading">
          登录
        </el-button>
      </el-form>
      <div v-if="error" class="text-red-400 text-sm mt-4 text-center">{{ error }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '../api';

const router = useRouter();
const form = ref({ username: '', password: '' });
const loading = ref(false);
const error = ref('');

const handleLogin = async () => {
  loading.value = true;
  error.value = '';
  try {
    // URL is now relative to baseURL (/api) so just 'api-token-auth/'
    const res = await api.post('api-token-auth/', form.value);
    const token = res.data.token;
    localStorage.setItem('auth_token', token);
    // Set default header for subsequent requests
    api.defaults.headers.common['Authorization'] = `Token ${token}`;
    router.push('/crm/opportunities');
  } catch (e: any) {
    error.value = '登录失败，请检查用户名或密码';
    console.error(e);
  } finally {
    loading.value = false;
  }
};
</script>
