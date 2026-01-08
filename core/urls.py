from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OpportunityViewSet, PerformanceTargetViewSet, DashboardViewSet, 
    WeChatLoginView, MeView, competition_kanban_page, marketactivity_kanban_page, 
    CompetitionViewSet, MarketActivityViewSet, AIAnalysisView, CustomerViewSet, ApprovalRequestViewSet, SocialMediaStatsViewSet, SocialMediaAccountViewSet, ContactViewSet, CustomerTagViewSet, OpportunityTeamMemberViewSet, OpportunityLogViewSet, ExternalIdMapViewSet, CustomerCohortViewSet, ChatView, PerformanceReportView, AgentRouterView, SubmissionLogViewSet, AIConfigurationViewSet, UserViewSet, ActivityLogViewSet, ContactDeleteLogViewSet,
    ProjectViewSet, ProjectCardViewSet, DailyReportViewSet, NotificationViewSet, AnnouncementViewSet, DepartmentViewSet, JobTitleViewSet, DataManagementViewSet
)
from django.views.generic import TemplateView

router = DefaultRouter()
router.register(r'data-management', DataManagementViewSet, basename='data-management')
router.register(r'notifications', NotificationViewSet, basename='notifications')
router.register(r'announcements', AnnouncementViewSet, basename='announcements')
router.register(r'opportunities', OpportunityViewSet, basename='opportunities')
router.register(r'daily-reports', DailyReportViewSet, basename='daily-reports')
router.register(r'departments', DepartmentViewSet, basename='departments')
router.register(r'job-titles', JobTitleViewSet, basename='job-titles')
router.register(r'customers', CustomerViewSet, basename='customers')
router.register(r'contacts', ContactViewSet, basename='contacts')
router.register(r'customer-tags', CustomerTagViewSet, basename='customer-tags')
router.register(r'opportunity-team-members', OpportunityTeamMemberViewSet, basename='opportunity-team-members')
router.register(r'opportunity-logs', OpportunityLogViewSet, basename='opportunity-logs')
router.register(r'external-ids', ExternalIdMapViewSet, basename='external-ids')
router.register(r'customer-cohorts', CustomerCohortViewSet, basename='customer-cohorts')
router.register(r'performance-targets', PerformanceTargetViewSet, basename='performance-targets')
router.register(r'competitions', CompetitionViewSet, basename='competitions')
router.register(r'activities', MarketActivityViewSet, basename='activities')
router.register(r'approvals', ApprovalRequestViewSet, basename='approvals')
router.register(r'social-stats', SocialMediaStatsViewSet, basename='social-stats')
router.register(r'social-accounts', SocialMediaAccountViewSet, basename='social-accounts')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'submission-logs', SubmissionLogViewSet, basename='submission-logs')
router.register(r'activity-logs', ActivityLogViewSet, basename='activity-logs')
router.register(r'contact-delete-logs', ContactDeleteLogViewSet, basename='contact-delete-logs')
router.register(r'admin/ai-configs', AIConfigurationViewSet, basename='admin-ai-configs')
router.register(r'admin/users', UserViewSet, basename='admin-users')
router.register(r'projects', ProjectViewSet, basename='projects')
router.register(r'project-cards', ProjectCardViewSet, basename='project-cards')

from rest_framework.authtoken import views as auth_views
from .views import UserSimpleListView, AIAnalysisView, AgentRouterView, AIConfigsListView, AIConnectionTestView, LegacyImportView, ResetTestDataView, SeedTargetsView

urlpatterns = [
    path('', include(router.urls)),
    path('api-token-auth/', auth_views.obtain_auth_token), # Login endpoint
    path('auth/wechat/login/', WeChatLoginView.as_view(), name='wechat-login'),
    path('auth/me/', MeView.as_view(), name='me'),
    path('chat/', ChatView.as_view(), name='chat'),
    path('agent/route/', AgentRouterView.as_view(), name='agent-route'),
    path('reports/performance/', PerformanceReportView.as_view(), name='reports-performance'),
    path('users/simple/', UserSimpleListView.as_view(), name='users-simple'),
    path('ai/analyze/', AIAnalysisView.as_view(), name='ai-analyze'),
    path('ai/configs/', AIConfigsListView.as_view(), name='ai-configs'),
    path('ai/test-connection/', AIConnectionTestView.as_view(), name='ai-test-connection'),
    path('migrate/legacy/', LegacyImportView.as_view(), name='migrate-legacy'),
    path('admin/reset-test-data/', ResetTestDataView.as_view(), name='admin-reset-test-data'),
    path('admin/seed-targets/', SeedTargetsView.as_view(), name='admin-seed-targets'),
    # Dashboard Screen View
    path('dashboard/screen/', TemplateView.as_view(template_name='dashboard/index.html'), name='dashboard-screen'),
    # Public Kanban Pages (login required in views)
    path('kanban/competitions/', competition_kanban_page, name='competition-kanban-page'),
    path('kanban/activities/', marketactivity_kanban_page, name='marketactivity-kanban-page'),
]
