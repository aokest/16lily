from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OpportunityViewSet, PerformanceTargetViewSet, DashboardViewSet, 
    WeChatLoginView, MeView, competition_kanban_page, marketactivity_kanban_page, 
    CompetitionViewSet, MarketActivityViewSet, AIAnalysisView, CustomerViewSet, ApprovalRequestViewSet, SocialMediaStatsViewSet, SocialMediaAccountViewSet, ContactViewSet, CustomerTagViewSet, OpportunityTeamMemberViewSet, OpportunityLogViewSet, ExternalIdMapViewSet, CustomerCohortViewSet, ChatView, PerformanceReportView, AgentRouterView, SubmissionLogViewSet, AIConfigurationViewSet, UserViewSet, ActivityLogViewSet, ContactDeleteLogViewSet,
    ProjectViewSet, ProjectCardViewSet, DailyReportViewSet, NotificationViewSet, AnnouncementViewSet, DepartmentViewSet, JobTitleViewSet
)
from django.views.generic import TemplateView

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notifications')
router.register(r'announcements', AnnouncementViewSet, basename='announcements')
router.register(r'opportunities', OpportunityViewSet)
router.register(r'daily-reports', DailyReportViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'job-titles', JobTitleViewSet) # New endpoint
router.register(r'customers', CustomerViewSet)
router.register(r'contacts', ContactViewSet)
router.register(r'customer-tags', CustomerTagViewSet)
router.register(r'opportunity-team-members', OpportunityTeamMemberViewSet)
router.register(r'opportunity-logs', OpportunityLogViewSet)
router.register(r'external-ids', ExternalIdMapViewSet)
router.register(r'customer-cohorts', CustomerCohortViewSet)
router.register(r'performance-targets', PerformanceTargetViewSet)
router.register(r'competitions', CompetitionViewSet)
router.register(r'activities', MarketActivityViewSet)
router.register(r'approvals', ApprovalRequestViewSet)
router.register(r'social-stats', SocialMediaStatsViewSet)
router.register(r'social-accounts', SocialMediaAccountViewSet)
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'submission-logs', SubmissionLogViewSet, basename='submission-logs')
router.register(r'activity-logs', ActivityLogViewSet, basename='activity-logs')
router.register(r'contact-delete-logs', ContactDeleteLogViewSet, basename='contact-delete-logs')
router.register(r'admin/ai-configs', AIConfigurationViewSet, basename='admin-ai-configs')
router.register(r'admin/users', UserViewSet, basename='admin-users')
router.register(r'projects', ProjectViewSet)
router.register(r'project-cards', ProjectCardViewSet)

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
