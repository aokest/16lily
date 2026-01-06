import { createRouter, createWebHistory } from 'vue-router';
import Dashboard from '../views/Dashboard.vue';
import Login from '../views/Login.vue';
import OpportunityList from '../views/crm/OpportunityList.vue';
import OpportunityForm from '../views/crm/OpportunityForm.vue';
import CustomerList from '../views/crm/CustomerList.vue';
import CustomerForm from '../views/crm/CustomerForm.vue';
import CRMHome from '../views/crm/CRMHome.vue';
import SocialStatsList from '../views/social/SocialStatsList.vue';
import SocialStatsForm from '../views/social/SocialStatsForm.vue';
import SocialAccountsList from '../views/social/SocialAccountsList.vue';
import SocialAccountForm from '../views/social/SocialAccountForm.vue';
import PerformanceReport from '../views/reports/Performance.vue';
import ApprovalCenter from '../views/crm/ApprovalCenter.vue';
import ContactsList from '../views/crm/ContactsList.vue';
import ContactForm from '../views/crm/ContactForm.vue';
import ChatWindow from '../views/ai/ChatWindow.vue';
import MainLayout from '../layout/MainLayout.vue';
import LegacyImport from '../views/admin/LegacyImport.vue';
import AdminTools from '../views/admin/AdminTools.vue';
import AIConfig from '../views/settings/AIConfig.vue';
import UserManagement from '../views/settings/UserManagement.vue';
import SystemLogs from '../views/settings/SystemLogs.vue';
import DataManagement from '../views/settings/DataManagement.vue';
import PersonalCenter from '../views/dashboard/PersonalCenter.vue';

const routes = [
    {
        path: '/login',
        name: 'Login',
        component: Login
    },
    // Standalone Routes (Independent Windows)
    {
        path: '/standalone/card/:id',
        name: 'StandaloneCardEditor',
        component: () => import('../views/projects/StandaloneCardEditor.vue')
    },
    {
        path: '/standalone/projects/:id/timeline',
        name: 'StandaloneProjectTimeline',
        component: () => import('../views/projects/StandaloneTimeline.vue')
    },
    {
        path: '/',
        name: 'Dashboard',
        component: Dashboard
    },
    {
        path: '/app', // Base path for admin interface
        component: MainLayout,
        meta: { requiresAuth: true },
        redirect: '/home', // Redirect to Personal Center by default
        children: [
            {
                path: '/home', 
                name: 'PersonalCenter',
                component: PersonalCenter
            },
            {
                path: '/daily-reports',
                name: 'DailyReportList',
                component: () => import('../views/daily_reports/DailyReportList.vue')
            },
            {
                path: '/settings/ai',
                name: 'AIConfig',
                component: AIConfig
            },
            {
                path: '/settings/users',
                name: 'UserManagement',
                component: UserManagement
            },
            {
                path: '/settings/departments',
                name: 'DepartmentManagement',
                component: () => import('../views/settings/DepartmentManagement.vue')
            },
            {
                path: '/settings/jobs',
                name: 'JobConfig',
                component: () => import('../views/settings/JobConfig.vue')
            },
            {
                path: '/settings/logs',
                name: 'SystemLogs',
                component: SystemLogs
            },
            {
                path: '/settings/data',
                name: 'DataManagement',
                component: DataManagement
            },
            {
                path: '/crm',
                name: 'CRMHome',
                component: CRMHome
            },
            {
                path: '/crm/approvals',
                name: 'ApprovalCenter',
                component: ApprovalCenter
            },
            {
                path: '/crm/contacts',
                name: 'ContactsList',
                component: ContactsList
            },
            {
                path: '/crm/contacts/create',
                name: 'ContactCreate',
                component: ContactForm
            },
            {
                path: '/crm/contacts/:id/edit',
                name: 'ContactEdit',
                component: ContactForm
            },
            {
                path: '/ai/chat',
                name: 'ChatWindow',
                component: ChatWindow
            },
            {
                path: '/crm/opportunities',
                name: 'OpportunityList',
                component: OpportunityList
            },
            {
                path: '/crm/opportunities/create',
                name: 'OpportunityCreate',
                component: OpportunityForm
            },
            {
                path: '/crm/opportunities/:id/edit',
                name: 'OpportunityEdit',
                component: OpportunityForm
            },
            {
                path: '/crm/customers',
                name: 'CustomerList',
                component: CustomerList
            },
            {
                path: '/crm/customers/create',
                name: 'CustomerCreate',
                component: CustomerForm
            },
            {
                path: '/crm/customers/:id/edit',
                name: 'CustomerEdit',
                component: CustomerForm
            },
            {
                path: '/reports/performance',
                name: 'PerformanceReport',
                component: PerformanceReport
            },
            {
                path: '/social/stats',
                name: 'SocialStatsList',
                component: SocialStatsList
            },
            {
                path: '/social/stats/create',
                name: 'SocialStatsCreate',
                component: SocialStatsForm
            },
            {
                path: '/social/stats/:id/edit',
                name: 'SocialStatsEdit',
                component: SocialStatsForm
            },
            {
                path: '/social/accounts',
                name: 'SocialAccountsList',
                component: SocialAccountsList
            },
            {
                path: '/social/accounts/create',
                name: 'SocialAccountCreate',
                component: SocialAccountForm
            },
            {
                path: '/social/accounts/:id/edit',
                name: 'SocialAccountEdit',
                component: SocialAccountForm
            },
            {
                path: '/admin/migrate',
                name: 'LegacyImport',
                component: LegacyImport
            },
            {
                path: '/admin/tools',
                name: 'AdminTools',
                component: AdminTools
            },
            {
                path: '/projects',
                name: 'ProjectList',
                component: () => import('../views/projects/ProjectList.vue')
            },
            {
                path: '/projects/timeline/global',
                name: 'GlobalTimeline',
                component: () => import('../views/projects/GlobalTimeline.vue')
            },
            {
                path: '/projects/:id',
                name: 'ProjectBoard',
                component: () => import('../views/projects/ProjectBoard.vue')
            },
            {
                path: '/projects/:id/timeline',
                name: 'ProjectTimeline',
                component: () => import('../views/projects/ProjectTimeline.vue')
            }
        ]
    }
];

const router = createRouter({
    history: createWebHistory(),
    routes
});

router.beforeEach((to, _from, next) => {
    const token = localStorage.getItem('auth_token');
    if (to.meta.requiresAuth && !token) {
        next('/login');
    } else {
        next();
    }
});

export default router;
