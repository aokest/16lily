from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OpportunityViewSet, PerformanceTargetViewSet, DashboardViewSet, 
    WeChatLoginView, MeView, competition_kanban_page, marketactivity_kanban_page, 
    CompetitionViewSet, MarketActivityViewSet, AIAnalysisView, CustomerViewSet
)
from django.views.generic import TemplateView

router = DefaultRouter()
router.register(r'opportunities', OpportunityViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'targets', PerformanceTargetViewSet)
router.register(r'competitions', CompetitionViewSet)
router.register(r'activities', MarketActivityViewSet)
router.register(r'dashboard', DashboardViewSet, basename='dashboard')

from rest_framework.authtoken import views as auth_views

urlpatterns = [
    path('', include(router.urls)),
    path('api-token-auth/', auth_views.obtain_auth_token), # Login endpoint
    path('auth/wechat/login/', WeChatLoginView.as_view(), name='wechat-login'),
    path('ai/analyze/', AIAnalysisView.as_view(), name='ai-analyze'), # AI Endpoint
    path('auth/me/', MeView.as_view(), name='me'),
    # AI Analysis Endpoint
    # Changed from 'api/ai/analyze/' to 'ai/analyze/' because this file is included under 'api/'
    path('ai/analyze/', AIAnalysisView.as_view(), name='ai-analyze'),
    # Dashboard Screen View
    path('dashboard/screen/', TemplateView.as_view(template_name='dashboard/index.html'), name='dashboard-screen'),
    # Public Kanban Pages (login required in views)
    path('kanban/competitions/', competition_kanban_page, name='competition-kanban-page'),
    path('kanban/activities/', marketactivity_kanban_page, name='marketactivity-kanban-page'),
]
