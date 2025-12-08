from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.db.models import Sum, Count, Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
from .models import Opportunity, PerformanceTarget, UserProfile, JobRole, OpportunityLog, Department, TodoTask, Announcement, SocialMediaStats, Competition, MarketActivity
from .serializers import OpportunitySerializer, PerformanceTargetSerializer, OpportunityLogSerializer, UserSerializer, CompetitionSerializer, MarketActivitySerializer
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Competition, MarketActivity, ApprovalStatus
from .services.ai_service import AIService
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

class WeChatLoginView(APIView):
    """
    微信登录/绑定接口 (Mock实现)
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        code = request.data.get('code')
        
        if not code:
            return Response({'error': 'Code is required'}, status=status.HTTP_400_BAD_REQUEST)

        # 模拟环境逻辑
        if code.startswith('mock_'):
            # 格式: mock_username (例如: mock_admin, mock_aoke)
            username = code.replace('mock_', '')
            try:
                user = User.objects.get(username=username)
                token, _ = Token.objects.get_or_create(user=user)
                return Response({
                    'token': token.key,
                    'user_id': user.id,
                    'username': user.username,
                    'is_staff': user.is_staff
                })
            except User.DoesNotExist:
                return Response({'error': 'User not found for mock login'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'error': 'Real WeChat login not configured yet'}, status=status.HTTP_501_NOT_IMPLEMENTED)

class MeView(APIView):
    """
    获取当前用户信息
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

@method_decorator(csrf_exempt, name='dispatch')
class AIAnalysisView(APIView):
    """
    AI 智能分析接口
    """
    authentication_classes = [] # Disable Auth for AI temporarily to test network
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        text = request.data.get('text')
        mode = request.data.get('mode', 'WORK_REPORT') # WORK_REPORT, OPPORTUNITY, etc.
        config_id = request.data.get('config_id') # New: support selecting specific model
        
        # DEBUG LOG
        print(f"AI Request: Mode={mode}, ConfigID={config_id}, User={request.user}")
        
        if not text:
            return Response({'error': 'No text provided'}, status=400)
            
        service = AIService(config_id=config_id)
        result = None
        
        try:
            if mode == 'WORK_REPORT':
                result = service.parse_work_report(text)
            elif mode == 'OPPORTUNITY':
                result = service.parse_opportunity(text)
            elif mode == 'TODO':
                result = service.parse_todo_task(text)
            elif mode == 'COMPETITION':
                result = service.parse_competition(text)
            elif mode == 'CUSTOMER':
                result = service.parse_customer(text)
            else:
                return Response({'error': 'Invalid mode'}, status=400)
        except Exception as e:
            # Log the full error for debugging
            print(f"AI Analysis Error: {str(e)}")
            return Response({'error': f"Internal Server Error: {str(e)}"}, status=500)
            
        if result:
            # If service returned an error dict, pass it through with 200 OK so frontend can display it nicely
            if 'error' in result:
                return Response(result)
            return Response(result)
            
        return Response({'error': 'AI processing failed or returned empty'}, status=500)

class OpportunityViewSet(viewsets.ModelViewSet):
    """
    商机 API
    """
    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        根据角色过滤商机
        """
        user = self.request.user
        if user.is_staff or user.profile.job_role == JobRole.MANAGER:
            return Opportunity.objects.all()
        # 销售只看自己负责的 + 参与的
        return Opportunity.objects.filter(sales_manager=user) | Opportunity.objects.filter(team_members=user)

    def perform_create(self, serializer):
        # Default sales_manager to creator if not provided
        save_kwargs = {'creator': self.request.user}
        if 'sales_manager' not in serializer.validated_data:
            save_kwargs['sales_manager'] = self.request.user
        serializer.save(**save_kwargs)

class PerformanceTargetViewSet(viewsets.ModelViewSet):
    """
    业绩目标 API
    """
    queryset = PerformanceTarget.objects.all()
    serializer_class = PerformanceTargetSerializer
    permission_classes = [permissions.IsAuthenticated]

class CompetitionViewSet(viewsets.ModelViewSet):
    queryset = Competition.objects.all().order_by('-created_at')
    serializer_class = CompetitionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'type', 'location']

class MarketActivityViewSet(viewsets.ModelViewSet):
    queryset = MarketActivity.objects.all().order_by('-created_at')
    serializer_class = MarketActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'type', 'location']

class DashboardViewSet(viewsets.ViewSet):
    """
    仪表盘数据聚合 API
    """
    # [Security Risk] AllowAny for local dashboard dev convenience.
    # In production, use TokenAuthentication or IP whitelist.
    permission_classes = [permissions.AllowAny]

    def _filter_opportunities_by_dept(self, qs, dept_code):
        if not dept_code:
            return qs
        
        if dept_code == Department.SALES:
            # 销售部看所有? 或者看销售经理是销售部的
            # 假设所有商机都归销售部管
            return qs
        else:
            # 其他部门（GAME, RND, LAB...）看他们参与的商机
            # 检查 team_members 或 detailed_members 中是否有该部门的人员
            # 也可以检查 sales_manager 是否属于该部门（虽然少见）
            return qs.filter(
                Q(team_members__profile__department=dept_code) |
                Q(detailed_members__user__profile__department=dept_code) |
                Q(sales_manager__profile__department=dept_code)
            ).distinct()

    @action(detail=False, methods=['get'])
    def stats(self, request):
        dept_code = request.query_params.get('department')
        
        # Base QuerySet
        qs = Opportunity.objects.all()
        qs = self._filter_opportunities_by_dept(qs, dept_code)

        # 1. 总体漏斗数据
        total_opportunities = qs.count()
        total_amount = qs.aggregate(Sum('amount'))['amount__sum'] or 0
        
        # 2. 按阶段分布
        stage_distribution = qs.values('stage').annotate(count=Count('id'))
        
        # 3. 业绩完成情况 (Actuals)
        current_year = timezone.now().year
        
        # 有效的赢单/完成项目
        won_qs = qs.filter(status__in=[Opportunity.Status.WON, Opportunity.Status.COMPLETED])
        
        actual_signed = won_qs.aggregate(Sum('signed_amount'))['signed_amount__sum'] or 0
        actual_profit = won_qs.aggregate(Sum('profit'))['profit__sum'] or 0
        actual_gross_profit = won_qs.aggregate(Sum('gross_profit'))['gross_profit__sum'] or 0
        actual_revenue = won_qs.aggregate(Sum('revenue'))['revenue__sum'] or 0
        
        # 获取目标
        target_qs = PerformanceTarget.objects.filter(year=current_year, quarter=PerformanceTarget.Quarter.FULL_YEAR)
        if dept_code:
            target_qs = target_qs.filter(department=dept_code)
        
        targets = target_qs.aggregate(
            t_amount=Sum('target_amount'),
            # t_profit removed
            t_gross=Sum('target_gross_profit'),
            t_revenue=Sum('target_revenue')
        )
        
        # 4. 新增统计 (Today, Week, Month, Quarter, Year)
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())
        month_start = today_start.replace(day=1)
        quarter_start = today_start.replace(month=((today_start.month - 1) // 3) * 3 + 1, day=1)
        year_start = today_start.replace(month=1, day=1)

        new_counts = {
            'today': qs.filter(created_at__gte=today_start).count(),
            'week': qs.filter(created_at__gte=week_start).count(),
            'month': qs.filter(created_at__gte=month_start).count(),
            'quarter': qs.filter(created_at__gte=quarter_start).count(),
            'year': qs.filter(created_at__gte=year_start).count(),
        }

        return Response({
            "funnel": {
                "total_count": total_opportunities,
                "total_pipeline_amount": total_amount
            },
            "stages": stage_distribution,
            "financials": {
                "year": current_year,
                # Signed Amount
                "target_signed": targets['t_amount'] or 0,
                "actual_signed": actual_signed,
                # Profit (Contract Profit)
                # "target_profit": targets['t_profit'] or 0, # Removed
                "actual_profit": actual_profit,
                # Gross Profit (Return Profit)
                "target_return_profit": targets['t_gross'] or 0,
                "actual_return_profit": actual_gross_profit,
                # Revenue
                "target_revenue": targets['t_revenue'] or 0,
                "actual_revenue": actual_revenue
            },
            "new_counts": new_counts
        })

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Dashboard Summary API for Admin Home
        """
        user = request.user
        
        # 1. Todo Count
        todo_count = TodoTask.objects.filter(assignee=user, is_completed=False).count()
        
        # 2. My Opportunity Count (Managed + Participated)
        opp_count = Opportunity.objects.filter(
            Q(sales_manager=user) | Q(team_members=user)
        ).distinct().count()
        
        # 3. New Fans (Latest record sum)
        # Get latest date recorded
        latest_date = SocialMediaStats.objects.order_by('-record_date').values_list('record_date', flat=True).first()
        new_fans_count = 0
        if latest_date:
            new_fans_count = SocialMediaStats.objects.filter(record_date=latest_date).aggregate(Sum('fans_count'))['fans_count__sum'] or 0
        
        # 4. Announcements
        # Logic: System announcements + Department announcements for user's departments
        # Note: Since we changed department to target_departments (JSON/List), filtering is tricky with standard ORM if using JSONField without Postgres features.
        # But we can fetch relevant ones.
        
        # For System:
        anns = Announcement.objects.filter(status='APPROVED', type='SYSTEM')
        
        # For Department:
        # If user has profile
        if hasattr(user, 'profile'):
            user_dept = user.profile.department # This is a single string e.g. 'SALES'
            
            # We need to find announcements where 'target_departments' contains user_dept
            # Since it's a JSON list or text, we can use __contains if using JSONField on supported DB, 
            # or do python filtering if list is small.
            # Assuming JSONField on SQLite (which supports it in modern Django/SQLite), __contains might work or not depending on version.
            # Safe fallback: fetch all DEPARTMENT approved announcements and filter in python.
            
            dept_anns = Announcement.objects.filter(status='APPROVED', type='DEPARTMENT')
            # Filter in python
            valid_dept_anns = [a for a in dept_anns if user_dept in (a.target_departments or [])]
            
            # Combine
            all_anns = list(anns) + valid_dept_anns
        else:
            all_anns = list(anns)
            
        # Sort by published_at desc
        all_anns.sort(key=lambda x: x.published_at or x.created_at, reverse=True)
        
        # Serialize top 5
        ann_data = []
        for a in all_anns[:5]:
            ann_data.append({
                'title': a.title,
                'content': a.content,
                'type': a.type,
                'type_display': a.get_type_display(),
                'date': (a.published_at or a.created_at).strftime('%Y-%m-%d')
            })

        return Response({
            "todo_count": todo_count,
            "opp_count": opp_count,
            "new_fans_count": new_fans_count,
            "announcements": ann_data
        })

    @action(detail=False, methods=['get'])
    def activities(self, request):
        """获取最新的动态/战报"""
        dept_code = request.query_params.get('department')
        
        # Filter logs based on opportunity department
        logs = OpportunityLog.objects.all()
        if dept_code:
            # Reuse the filter logic but apply to the related opportunity
            opp_ids = self._filter_opportunities_by_dept(Opportunity.objects.all(), dept_code).values_list('id', flat=True)
            logs = logs.filter(opportunity_id__in=opp_ids)

        # 获取最新的20条记录
        logs = logs.select_related('opportunity', 'operator').order_by('-created_at')[:20]
        serializer = OpportunityLogSerializer(logs, many=True)
        return Response(serializer.data)

# --- Kanban Pages (Non-admin, login required) ---

@login_required
def competition_kanban_page(request):
    stages = ApprovalStatus.choices
    kanban_data = {}
    for stage_code, stage_label in stages:
        kanban_data[stage_label] = Competition.objects.filter(status=stage_code).order_by('-created_at')
    return render(request, 'admin/core/competition/kanban.html', {
        'kanban_data': kanban_data,
        'title': '赛事看板'
    })

@login_required
def marketactivity_kanban_page(request):
    stages = ApprovalStatus.choices
    kanban_data = {}
    for stage_code, stage_label in stages:
        kanban_data[stage_label] = MarketActivity.objects.filter(status=stage_code).order_by('-created_at')
    return render(request, 'admin/core/marketactivity/kanban.html', {
        'kanban_data': kanban_data,
        'title': '市场活动看板'
    })
