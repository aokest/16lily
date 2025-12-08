import { createRouter, createWebHistory } from 'vue-router';
import Dashboard from '../views/Dashboard.vue';
import Login from '../views/Login.vue';
import OpportunityList from '../views/crm/OpportunityList.vue';
import OpportunityForm from '../views/crm/OpportunityForm.vue';
import CustomerList from '../views/crm/CustomerList.vue';
import CustomerForm from '../views/crm/CustomerForm.vue';

const routes = [
    {
        path: '/',
        name: 'Dashboard',
        component: Dashboard
    },
    {
        path: '/login',
        name: 'Login',
        component: Login
    },
    {
        path: '/crm/opportunities',
        name: 'OpportunityList',
        component: OpportunityList,
        meta: { requiresAuth: true }
    },
    {
        path: '/crm/opportunities/create',
        name: 'OpportunityCreate',
        component: OpportunityForm,
        meta: { requiresAuth: true }
    },
    {
        path: '/crm/opportunities/:id/edit',
        name: 'OpportunityEdit',
        component: OpportunityForm,
        meta: { requiresAuth: true }
    },
    {
        path: '/crm/customers',
        name: 'CustomerList',
        component: CustomerList,
        meta: { requiresAuth: true }
    },
    {
        path: '/crm/customers/create',
        name: 'CustomerCreate',
        component: CustomerForm,
        meta: { requiresAuth: true }
    },
    {
        path: '/crm/customers/:id/edit',
        name: 'CustomerEdit',
        component: CustomerForm,
        meta: { requiresAuth: true }
    }
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('auth_token');
    if (to.meta.requiresAuth && !token) {
        next('/login');
    } else {
        next();
    }
});

export default router;
