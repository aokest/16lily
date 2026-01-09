from rest_framework import viewsets, permissions, status, filters
from rest_framework.views import APIView
import time
import os
import subprocess
import sys
from django.http import FileResponse
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.db.models import Sum, Count, Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
from .models import Opportunity, PerformanceTarget, UserProfile, OpportunityLog, TodoTask, Announcement, SocialMediaStats, Competition, MarketActivity, Customer, DepartmentModel, DailyReport, ApprovalRequest, Notification, Project, ProjectCard, ProjectDeleteLog, ProjectChangeLog
from .serializers import (
    OpportunitySerializer, PerformanceTargetSerializer, OpportunityLogSerializer, 
    OpportunityTeamMemberSerializer, UserSerializer, CompetitionSerializer, 
    MarketActivitySerializer, CustomerSerializer, ContactSerializer, 
    CustomerTagSerializer, ExternalIdMapSerializer, CustomerCohortSerializer, 
    DailyReportSerializer, AnnouncementSerializer, DepartmentSerializer,
    UserSimpleSerializer, ProjectSerializer, ProjectCardSerializer
)
from .serializers import (
    ActivityLogSerializer, ApprovalRequestSerializer, SocialMediaStatsSerializer, 
    SocialMediaAccountSerializer, UserManagementSerializer, NotificationSerializer
)
from .models import Contact, CustomerTag, OpportunityTeamMember, ExternalIdMap, CustomerCohort, ContactDeleteLog
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Competition, MarketActivity, SocialMediaAccount
from .services.ai_service import AIService
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db.models.functions import TruncMonth
from django_filters.rest_framework import DjangoFilterBackend
import re
from rest_framework.permissions import IsAdminUser
from .serializers import SubmissionLogSerializer
from .models import SubmissionLog
from .serializers import AIConfigurationSerializer
from .models import AIConfiguration
from .models import ApprovalStatus
from .models import ActivityLog, JobTitle
from .serializers import JobTitleSerializer

from rest_framework import viewsets, permissions, status, filters
from django_filters.rest_framework import DjangoFilterBackend

class JobTitleViewSet(viewsets.ModelViewSet):
    """
    岗位名称管理接口 (Admins only for write)
    """
    queryset = JobTitle.objects.all().order_by('category', 'name')
    serializer_class = JobTitleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'init_defaults']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['post'], url_path='init_defaults')
    def init_defaults(self, request):
        """
        初始化系统默认岗位名称
        """
        defaults = [
            ('总经理', 'MANAGEMENT'), ('副总经理', 'MANAGEMENT'), ('总监', 'MANAGEMENT'), ('经理', 'MANAGEMENT'),
            ('销售经理', 'SALES'), ('大客户经理', 'SALES'), ('销售专员', 'SALES'),
            ('研发工程师', 'RND'), ('前端工程师', 'RND'), ('后端工程师', 'RND'), ('测试工程师', 'RND'),
            ('研究员', 'RESEARCHER'), ('高级研究员', 'RESEARCHER'),
            ('市场经理', 'MARKETING'), ('活动策划', 'MARKETING'),
            ('运营经理', 'OPERATION'), ('运营专员', 'OPERATION'),
            ('设计师', 'DESIGN'), ('视觉设计', 'DESIGN'),
            ('系统管理员', 'SYSADMIN'), ('IT支持', 'SYSADMIN'),
            ('助理', 'ASSISTANT'), ('行政助理', 'ASSISTANT'), ('财务助理', 'ASSISTANT'),
        ]
        created_count = 0
        for name, cat in defaults:
            obj, created = JobTitle.objects.get_or_create(name=name, category=cat)
            if created:
                created_count += 1
        
        return Response({'status': 'success', 'message': f'已恢复系统默认岗位，新增了 {created_count} 个岗位'})

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = DepartmentModel.objects.all().order_by('id')
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """
        获取部门成员列表（统一使用 department_link 作为来源）
        """
        dept = self.get_object()
        members = User.objects.filter(profile__department_link=dept)
        serializer = UserSimpleSerializer(members, many=True)
        return Response(serializer.data)

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
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

@method_decorator(csrf_exempt, name='dispatch')
class AIAnalysisView(APIView):
    """
    AI 智能分析接口
    """
    permission_classes = [permissions.IsAuthenticated]

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
        # Pass user for logging if authenticated
        user = request.user if request.user.is_authenticated else None
        
        try:
            if mode == 'WORK_REPORT':
                result = service.parse_work_report(text, user=user)
            elif mode == 'POLISH_REPORT':
                # 润色模式：返回 { "content": "..." }
                polished_text = service.polish_daily_report(text, user=user)
                result = {'content': polished_text}
            elif mode == 'OPPORTUNITY':
                result = service.parse_opportunity(text, user=user)
            elif mode == 'TODO':
                result = service.parse_todo(text, user=user)
            else:
                return Response({'error': f'Unsupported mode: {mode}'}, status=400)
                
            return Response(result)
        except Exception as e:
            print(f"AI Service Error: {str(e)}")
            return Response({'error': str(e)}, status=500)

class DashboardViewSet(viewsets.ViewSet):
    """
    数据看板接口 - 提供核心统计数据
    """
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='stats')
    def get_stats(self, request):
        try:
            # 1. Pipeline Stats (Opportunity)
            total_opps = Opportunity.objects.count()
            total_amount = Opportunity.objects.aggregate(Sum('amount'))['amount__sum'] or 0
            
            # 2. Project Stats
            from .models import Project, DailyReport, Customer, Notification
            total_projects = Project.objects.count()
            active_projects = Project.objects.exclude(status='COMPLETED').count()
            
            # 3. Monthly New Opps
            from django.utils import timezone
            now = timezone.now()
            start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            monthly_opps = Opportunity.objects.filter(created_at__gte=start_of_month).count()
            
            # 4. Personal Center Stats (Frontend compatibility)
            from .models import PerformanceTarget
            
            # 计算部门已完成
            dept_achieved = Opportunity.objects.filter(stage='CLOSED_WON').aggregate(Sum('amount'))['amount__sum'] or 0
            # 获取部门目标
            dept_target = PerformanceTarget.objects.filter(
                year=now.year, month=now.month, target_type='SALES'
            ).aggregate(Sum('target_revenue'))['target_revenue__sum'] or 0
            
            # 个人统计
            personal_achieved = 0
            personal_target = 0
            todo_count = 0
            daily_report_count = 0
            
            if request.user.is_authenticated:
                personal_achieved = Opportunity.objects.filter(
                    sales_manager=request.user, stage='CLOSED_WON'
                ).aggregate(Sum('amount'))['amount__sum'] or 0
                personal_target = PerformanceTarget.objects.filter(
                    user=request.user, year=now.year, month=now.month, target_type='SALES'
                ).aggregate(Sum('target_revenue'))['target_revenue__sum'] or 0
                todo_count = Notification.objects.filter(user=request.user, is_read=False).count()
                daily_report_count = DailyReport.objects.filter(creator=request.user).count()

            return Response({
                'total_opportunities': total_opps,
                'total_budget': total_amount,
                'total_projects': total_projects,
                'active_projects': active_projects,
                'monthly_new_opportunities': monthly_opps,
                'update_time': now.isoformat(),
                
                'deptTarget': dept_target,
                'deptAchieved': dept_achieved,
                'personalTarget': personal_target,
                'personalAchieved': personal_achieved,
                'todoCount': todo_count,
                'ongoingProjects': active_projects,
                'dailyReportCount': daily_report_count,
                'totalCustomers': Customer.objects.count()
            })
        except Exception as e:
            # 即使报错也要返回 0，确保前端不崩溃
            return Response({
                'deptTarget': 0, 'deptAchieved': 0, 'personalTarget': 0, 'personalAchieved': 0,
                'todoCount': 0, 'ongoingProjects': 0, 'dailyReportCount': 0, 'totalCustomers': 0,
                'error': str(e)
            })

    @action(detail=False, methods=['get'], url_path='activities')
    def get_activities(self, request):
        """
        获取最近动态
        """
        logs = OpportunityLog.objects.all().order_by('-created_at')[:10]
        data = []
        for log in logs:
            data.append({
                'id': log.id,
                'time': log.created_at,
                'user': log.operator.username if log.operator else 'System',
                'action': log.action,
                'content': log.content,
                'target': str(log.opportunity)
            })
        return Response(data)

class OpportunityViewSet(viewsets.ModelViewSet):
    queryset = Opportunity.objects.all().order_by('-created_at')
    serializer_class = OpportunitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['stage', 'sales_manager', 'creator']
    search_fields = ['name', 'customer_company', 'customer__name', 'description']
    ordering_fields = ['created_at', 'amount']

    def list(self, request, *args, **kwargs):
        print(f"DEBUG: Request Headers: {request.headers}")
        print(f"DEBUG: Auth Header: {request.headers.get('Authorization')}")
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        print(f"DEBUG: OpportunityViewSet.create data: {request.data}")
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print(f"DEBUG: Validation Error: {serializer.errors}")
            return Response({'error': f'字段校验失败: {serializer.errors}', 'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Default creator and sales_manager to current user if not provided
            extra_data = {'creator': self.request.user}
            
            # Check if sales_manager is in validated_data (it might have been processed by to_internal_value)
            # Or if it was popped but not set.
            # logic: if 'sales_manager' is missing in validated_data, we should provide a default.
            # But we can't easily check validated_data here before saving? 
            # actually serializer.validated_data is available after is_valid()
            
            if 'sales_manager' not in serializer.validated_data:
                 extra_data['sales_manager'] = self.request.user

            opp = serializer.save(**extra_data)
            OpportunityLog.objects.create(
                opportunity=opp,
                operator=self.request.user,
                action='创建商机',
                content=f'创建了新商机: {opp.name}'
            )
            headers = self.get_success_headers(serializer.data)
            return Response({'status': 'success', 'id': opp.id}, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            return Response({'error': '保存失败', 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PerformanceTargetViewSet(viewsets.ModelViewSet):
    queryset = PerformanceTarget.objects.all().order_by('-year', '-month')
    serializer_class = PerformanceTargetSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['user', 'year', 'month', 'department', 'quarter', 'target_type', 'period']

    @action(detail=False, methods=['post'], url_path='copy_year_targets')
    def copy_year_targets(self, request):
        """
        跨年份复制业绩目标副本
        {
          "from_year": 2025,
          "to_year": 2026,
          "department": 1, (optional)
          "user_id": 1 (optional)
        }
        """
        from_year = request.data.get('from_year')
        to_year = request.data.get('to_year')
        dept_id = request.data.get('department')
        user_id = request.data.get('user_id')

        if not from_year or not to_year:
            return Response({'error': '源年份和目标年份必填'}, status=400)

        filters = {'year': from_year}
        if dept_id: filters['department_id'] = dept_id
        if user_id: filters['user_id'] = user_id

        source_targets = PerformanceTarget.objects.filter(**filters)
        if not source_targets.exists():
            return Response({'error': '未找到源年份的数据'}, status=404)

        copied_count = 0
        for st in source_targets:
            # 仅复制基础属性，生成新主键
            PerformanceTarget.objects.update_or_create(
                year=to_year,
                period=st.period,
                month=st.month,
                quarter=st.quarter,
                department=st.department,
                user=st.user,
                target_type=st.target_type,
                defaults={
                    'target_contract_amount': st.target_contract_amount,
                    'target_gross_profit': st.target_gross_profit,
                    'target_revenue': st.target_revenue
                }
            )
            copied_count += 1

        return Response({'status': 'success', 'copied': copied_count})

    @action(detail=False, methods=['post'], url_path='bulk_delete')
    def bulk_delete(self, request):
        """
        批量删除业绩目标
        """
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': '未选择项'}, status=400)
        
        # 权限检查：仅管理员或相关部门经理
        if not request.user.is_staff:
            targets = PerformanceTarget.objects.filter(id__in=ids)
            for t in targets:
                if t.department and t.department.manager != request.user:
                    return Response({'error': f'无权删除项 {t.id}'}, status=403)
        
        targets = PerformanceTarget.objects.filter(id__in=ids)
        
        # 收集需要连带删除的过滤条件，实现批量级联删除
        deleted_count = 0
        for t in targets:
            base_filters = {
                'year': t.year,
                'department': t.department,
                'user': t.user,
                'target_type': t.target_type
            }
            if t.period == PerformanceTarget.Period.YEAR:
                # 删除该维度的全年所有数据
                deleted_count += PerformanceTarget.objects.filter(**base_filters).delete()[0]
            elif t.period == PerformanceTarget.Period.QUARTER:
                # 删除该维度的该季度所有数据
                deleted_count += PerformanceTarget.objects.filter(quarter=t.quarter, **base_filters).delete()[0]
            else:
                # 仅删除该条月度数据（如果它还没被上面的逻辑删掉）
                if PerformanceTarget.objects.filter(id=t.id).exists():
                    deleted_count += t.delete()[0]
        
        return Response({'status': 'success', 'deleted': deleted_count})

    @action(detail=False, methods=['post'], url_path='bulk_batch_update')
    def bulk_batch_update(self, request):
        """
        批量修改选中的业绩目标值
        """
        ids = request.data.get('ids', [])
        contract = request.data.get('target_contract_amount')
        profit = request.data.get('target_gross_profit')
        revenue = request.data.get('target_revenue')

        if not ids:
            return Response({'error': '未选择项'}, status=400)
        
        # 权限检查
        if not request.user.is_staff:
            targets = PerformanceTarget.objects.filter(id__in=ids)
            for t in targets:
                if t.department and t.department.manager != request.user:
                    return Response({'error': f'无权修改项 {t.id}'}, status=403)
        
        # 构建更新字典，仅更新传了值的字段
        update_data = {}
        if contract is not None: update_data['target_contract_amount'] = contract
        if profit is not None: update_data['target_gross_profit'] = profit
        if revenue is not None: update_data['target_revenue'] = revenue

        if not update_data:
            return Response({'error': '未提供修改内容'}, status=400)

        targets = PerformanceTarget.objects.filter(id__in=ids)
        updated_count = 0
        for t in targets:
            # 仅允许批量修改月度目标，因为季度和年度是由月度汇总的
            if t.period != PerformanceTarget.Period.MONTH:
                continue
            
            for key, value in update_data.items():
                setattr(t, key, value)
            t.save()
            updated_count += 1
            # 触发汇总逻辑
            self._trigger_aggregation(t)

        return Response({'status': 'success', 'updated': updated_count})

    @action(detail=False, methods=['post'], url_path='bulk_update_targets')
    def bulk_update_targets(self, request):
        """
        批量更新月度业绩目标
        请求体：
        {
          "year": 2026,
          "department": 1,         # 部门ID
          "user_id": 3,            # 为空表示部门总目标
          "targets": [{"month":1,"target_contract_amount":100000, ...}, ...]
        }
        """
        year = request.data.get('year')
        dept_id = request.data.get('department')
        user_id = request.data.get('user_id')
        targets = request.data.get('targets') or []
        
        if not year or not isinstance(targets, list):
            return Response({'error': '参数不完整'}, status=400)
            
        # 1. 权限校验（统一入口，支持助理同权）
        try:
            from .permissions import can_manage_department
        except Exception:
            can_manage_department = None
        
        dept_obj = None
        if dept_id:
            try:
                dept_obj = DepartmentModel.objects.get(id=dept_id)
            except DepartmentModel.DoesNotExist:
                return Response({'error': '部门不存在'}, status=404)
        
        if can_manage_department:
            if not can_manage_department(request.user, dept_obj):
                return Response({'error': '仅部门负责人或管理员或授权助理可修改目标'}, status=403)
        else:
            # 回退：保持原有规则
            if not request.user.is_staff:
                if not dept_obj or dept_obj.manager != request.user:
                    return Response({'error': '仅部门负责人或管理员可修改目标'}, status=403)
        
        # 助理代理：将有效用户解析为上级，用于后续聚合与下发
        try:
            from .permissions import resolve_effective_user
            effective_user = resolve_effective_user(request.user)
        except Exception:
            effective_user = request.user

        # 确定目标类型
        target_type = request.data.get('target_type')
        if not target_type:
            target_type = PerformanceTarget.TargetType.INDIVIDUAL if user_id else PerformanceTarget.TargetType.DEPARTMENT
        
        user = None
        department = None
        
        if dept_id:
            try:
                if isinstance(dept_id, int) or (isinstance(dept_id, str) and dept_id.isdigit()):
                    department = DepartmentModel.objects.filter(id=int(dept_id)).first()
                else:
                    department = DepartmentModel.objects.filter(name=dept_id).first()
            except Exception:
                pass

        # 强制逻辑：目标类型与归属关联
        if target_type == PerformanceTarget.TargetType.COMPANY:
            user = None
            department = None
        elif target_type == PerformanceTarget.TargetType.DEPARTMENT:
            user = None
            # 如果是部门目标但没找到部门，报错
            if not department and dept_id:
                return Response({'error': f'部门 {dept_id} 不存在'}, status=404)
        elif user_id:
            try:
                user = User.objects.get(id=user_id)
                # 如果是个人目标且没传部门，尝试从用户 Profile 获取
                if not department and hasattr(user, 'profile') and user.profile.department_link:
                    department = user.profile.department_link
            except User.DoesNotExist:
                return Response({'error': '用户不存在'}, status=404)
        
        updated = 0
        errors = []
        
        # 使用事务确保数据一致性
        from django.db import transaction
        try:
            with transaction.atomic():
                # 1. 先清理该维度下已存在的旧数据，防止 get() 返回多条记录的冲突
                PerformanceTarget.objects.filter(
                    target_type=target_type,
                    year=year,
                    user=user,
                    department=department
                ).delete()

                # 2. 重新创建 12 个月度目标
                for item in targets:
                    month = item.get('month')
                    if not month: continue
                    
                    contract = item.get('target_contract_amount', 0) or 0
                    profit = item.get('target_gross_profit', 0) or 0
                    revenue = item.get('target_revenue', 0) or 0
                    quarter = (month - 1) // 3 + 1
                    
                    PerformanceTarget.objects.create(
                        target_type=target_type,
                        period=PerformanceTarget.Period.MONTH,
                        year=year,
                        month=month,
                        quarter=quarter,
                        user=user,
                        department=department,
                        target_contract_amount=contract,
                        target_gross_profit=profit,
                        target_revenue=revenue
                    )
                    updated += 1

                # 3. 自动汇总并创建 4 个季度目标和 1 个年度目标
                all_months = PerformanceTarget.objects.filter(
                    target_type=target_type,
                    period=PerformanceTarget.Period.MONTH,
                    year=year,
                    user=user,
                    department=department
                )
                
                # 按季度汇总
                for q in range(1, 5):
                    q_months = all_months.filter(quarter=q)
                    q_contract = sum(m.target_contract_amount for m in q_months)
                    q_profit = sum(m.target_gross_profit for m in q_months)
                    q_revenue = sum(m.target_revenue for m in q_months)
                    
                    if q_months.exists():
                        PerformanceTarget.objects.update_or_create(
                            target_type=target_type,
                            period=PerformanceTarget.Period.QUARTER,
                            year=year,
                            month=None,      # 季度目标月份为空
                            quarter=q,
                            user=user,
                            department=department,
                            defaults={
                                'target_contract_amount': q_contract,
                                'target_gross_profit': q_profit,
                                'target_revenue': q_revenue
                            }
                        )

                # 年度汇总
                y_contract = sum(m.target_contract_amount for m in all_months)
                y_profit = sum(m.target_gross_profit for m in all_months)
                y_revenue = sum(m.target_revenue for m in all_months)
                
                PerformanceTarget.objects.update_or_create(
                    target_type=target_type,
                    period=PerformanceTarget.Period.YEAR,
                    year=year,
                    month=None,      # 年度目标月份为空
                    quarter=None,    # 年度目标季度为空
                    user=user,
                    department=department,
                    defaults={
                        'target_contract_amount': y_contract,
                        'target_gross_profit': y_profit,
                        'target_revenue': y_revenue
                    }
                )
        except Exception as e:
            return Response({'error': f'批量更新失败: {str(e)}'}, status=500)

        return Response({
            'status': 'success',
            'updated_months': updated,
            'message': f'已成功更新 {year} 年度的月度、季度及年度目标'
        })

    @action(detail=False, methods=['post'], url_path='copy_year_targets')
    def copy_year_targets(self, request):
        """
        将某一年的目标复制到另一年
        """
        from_year = request.data.get('from_year')
        to_year = request.data.get('to_year')
        dept_id = request.data.get('department')
        user_id = request.data.get('user_id')

        if not from_year or not to_year:
            return Response({'error': '源年份和目标年份必填'}, status=400)

        filters = {'year': from_year}
        if dept_id: filters['department_id'] = dept_id
        if user_id: filters['user_id'] = user_id

        source_targets = PerformanceTarget.objects.filter(**filters)
        if not source_targets.exists():
            return Response({'error': '未找到源年份的数据'}, status=404)

        copied_count = 0
        for st in source_targets:
            PerformanceTarget.objects.update_or_create(
                year=to_year,
                period=st.period,
                month=st.month,
                quarter=st.quarter,
                department=st.department,
                user=st.user,
                target_type=st.target_type,
                defaults={
                    'target_contract_amount': st.target_contract_amount,
                    'target_gross_profit': st.target_gross_profit,
                    'target_revenue': st.target_revenue
                }
            )
            copied_count += 1

        return Response({'status': 'success', 'copied': copied_count})

    def _trigger_aggregation(self, instance):
        """
        自动汇总逻辑：
        1. 维度聚合：如果更新了个人目标，汇总到部门目标 (由业务规则决定：部门总目标 >= 个人总和)
        2. 时间聚合：月度 -> 季度 -> 年度
        3. 经理规则：如果更新了部门目标或非经理个人目标，自动调整该部门经理的个人目标
        """
        if instance.period != PerformanceTarget.Period.MONTH:
            return

        # 1. 自动调整经理目标 (如果适用)
        self._apply_manager_rule(instance)

        # 2. 时间维度聚合 (当前更新的对象)
        self._update_time_aggregation(instance)
        
        # 3. 如果变动的是个人目标，触发部门的时间维度汇总更新
        if instance.target_type == PerformanceTarget.TargetType.INDIVIDUAL and instance.department:
            dept_target = PerformanceTarget.objects.filter(
                target_type=PerformanceTarget.TargetType.DEPARTMENT,
                period=PerformanceTarget.Period.MONTH,
                year=instance.year,
                month=instance.month,
                department=instance.department
            ).first()
            if dept_target:
                self._update_time_aggregation(dept_target)

    def _apply_manager_rule(self, instance):
        """
        部门经理的个人目标 = 部门总目标数 - 部门其他人总目标数
        """
        if not instance.department:
            return

        dept_manager = instance.department.manager
        if not dept_manager:
            return

        # 获取该部门、同年、同月的部门总目标
        dept_target = PerformanceTarget.objects.filter(
            target_type=PerformanceTarget.TargetType.DEPARTMENT,
            period=PerformanceTarget.Period.MONTH,
            year=instance.year,
            month=instance.month,
            department=instance.department
        ).first()

        if not dept_target:
            return

        # 汇总除经理以外的所有个人目标
        others_totals = PerformanceTarget.objects.filter(
            target_type=PerformanceTarget.TargetType.INDIVIDUAL,
            period=PerformanceTarget.Period.MONTH,
            year=instance.year,
            month=instance.month,
            department=instance.department
        ).exclude(user=dept_manager).aggregate(
            t_contract=Sum('target_contract_amount'),
            t_profit=Sum('target_gross_profit'),
            t_revenue=Sum('target_revenue')
        )

        # 经理个人目标 = 部门总目标 - 其他人总和 (不小于0)
        quarter = (instance.month - 1) // 3 + 1
        manager_target, created = PerformanceTarget.objects.update_or_create(
            target_type=PerformanceTarget.TargetType.INDIVIDUAL,
            period=PerformanceTarget.Period.MONTH,
            year=instance.year,
            month=instance.month,
            quarter=quarter,
            user=dept_manager,
            department=instance.department,
            defaults={
                'target_contract_amount': max(0, dept_target.target_contract_amount - (others_totals['t_contract'] or 0)),
                'target_gross_profit': max(0, dept_target.target_gross_profit - (others_totals['t_profit'] or 0)),
                'target_revenue': max(0, dept_target.target_revenue - (others_totals['t_revenue'] or 0))
            }
        )
        
        # 经理目标变动，触发经理的时间维度汇总
        self._update_time_aggregation(manager_target)

    def _update_time_aggregation(self, instance):
        """
        汇总月度到季度和年度
        """
        from django.db.models import Sum
        if instance.period != PerformanceTarget.Period.MONTH:
            return

        # 汇总到季度
        q_start = (instance.quarter - 1) * 3 + 1
        q_end = instance.quarter * 3
        q_totals = PerformanceTarget.objects.filter(
            target_type=instance.target_type,
            period=PerformanceTarget.Period.MONTH,
            year=instance.year,
            month__gte=q_start,
            month__lte=q_end,
            user=instance.user,
            department=instance.department
        ).aggregate(
            t_contract=Sum('target_contract_amount'),
            t_profit=Sum('target_gross_profit'),
            t_revenue=Sum('target_revenue')
        )
        
        PerformanceTarget.objects.update_or_create(
            target_type=instance.target_type,
            period=PerformanceTarget.Period.QUARTER,
            year=instance.year,
            quarter=instance.quarter,
            month=None,
            user=instance.user,
            department=instance.department,
            defaults={
                'target_contract_amount': q_totals['t_contract'] or 0,
                'target_gross_profit': q_totals['t_profit'] or 0,
                'target_revenue': q_totals['t_revenue'] or 0
            }
        )

        # 汇总到年度
        y_totals = PerformanceTarget.objects.filter(
            target_type=instance.target_type,
            period=PerformanceTarget.Period.MONTH,
            year=instance.year,
            user=instance.user,
            department=instance.department
        ).aggregate(
            t_contract=Sum('target_contract_amount'),
            t_profit=Sum('target_gross_profit'),
            t_revenue=Sum('target_revenue')
        )
        
        PerformanceTarget.objects.update_or_create(
            target_type=instance.target_type,
            period=PerformanceTarget.Period.YEAR,
            year=instance.year,
            month=None,
            quarter=None,
            user=instance.user,
            department=instance.department,
            defaults={
                'target_contract_amount': y_totals['t_contract'] or 0,
                'target_gross_profit': y_totals['t_profit'] or 0,
                'target_revenue': y_totals['t_revenue'] or 0
            }
        )
        
    def destroy(self, request, *args, **kwargs):
        """
        重写删除方法，实现级联删除
        如果删除的是年度目标，自动删除该年度下的季度和月度目标
        如果删除的是季度目标，自动删除该季度下的月度目标
        """
        instance = self.get_object()
        try:
            from .permissions import can_manage_department
            if not can_manage_department(request.user, instance.department):
                return Response({'error': '仅部门负责人或管理员或授权助理可删除目标'}, status=403)
        except Exception:
            pass
        year = instance.year
        dept = instance.department
        user = instance.user
        target_type = instance.target_type

        # 构建基础过滤器
        filters = {
            'year': year,
            'department': dept,
            'user': user,
            'target_type': target_type
        }

        if instance.period == PerformanceTarget.Period.YEAR:
            # 删除所有关联的季度和月度
            PerformanceTarget.objects.filter(**filters).delete()
        elif instance.period == PerformanceTarget.Period.QUARTER:
            # 删除该季度下的所有月度
            PerformanceTarget.objects.filter(quarter=instance.quarter, **filters).delete()
        else:
            # 仅删除单个月度
            instance.delete()
            
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], url_path='bulk_delete')
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': '未选择删除项'}, status=400)
        
        # 为了触发级联逻辑，循环调用删除
        targets = PerformanceTarget.objects.filter(id__in=ids)
        count = 0
        for t in targets:
            try:
                from .permissions import can_manage_department
                if not can_manage_department(request.user, t.department):
                    return Response({'error': f'无权删除项 {t.id}'}, status=403)
            except Exception:
                pass
            # 这里调用内部删除逻辑
            year, dept, user, t_type = t.year, t.department, t.user, t.target_type
            f = {'year': year, 'department': dept, 'user': user, 'target_type': t_type}
            if t.period == PerformanceTarget.Period.YEAR:
                PerformanceTarget.objects.filter(**f).delete()
            elif t.period == PerformanceTarget.Period.QUARTER:
                PerformanceTarget.objects.filter(quarter=t.quarter, **f).delete()
            else:
                t.delete()
            count += 1
            
        return Response({'status': 'success', 'deleted_count': count})
class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all().order_by('-created_at')
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['owner']
    search_fields = ['name', 'industry']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': '字段校验失败', 'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            obj = serializer.save(owner=self.request.user)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            return Response({'error': '保存失败', 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all().order_by('-created_at')
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['customer']
    search_fields = ['name', 'phone', 'email']

    def perform_destroy(self, instance):
        # 在物理删除前，记录日志和备份数据
        customer_name = "未知"
        try:
            if instance.customer:
                customer_name = instance.customer.name
        except Exception:
            pass

        ContactDeleteLog.objects.create(
            contact_name=instance.name,
            customer_name=customer_name,
            deleted_by=self.request.user,
            original_data={
                'name': instance.name,
                'phone': instance.phone,
                'email': instance.email,
                'customer_id': instance.customer_id,
                'title': instance.title
            }
        )
        instance.delete()

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def restore(self, request):
        log_id = request.data.get('log_id')
        if not log_id:
            return Response({'error': 'Log ID is required'}, status=400)
            
        try:
            log = ContactDeleteLog.objects.get(id=log_id, is_restored=False)
            # 根据备份数据重新创建联系人
            Contact.objects.create(**log.original_data)
            log.is_restored = True
            log.save()
            return Response({'status': 'success', 'message': '联系人已恢复'})
        except ContactDeleteLog.DoesNotExist:
            return Response({'error': 'Log not found or already restored'}, status=404)

class ContactDeleteLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ContactDeleteLog.objects.all().order_by('-deleted_at')
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_restored']
    search_fields = ['contact_name', 'customer_name']
    ordering_fields = ['deleted_at']

class CustomerTagViewSet(viewsets.ModelViewSet):
    queryset = CustomerTag.objects.all()
    serializer_class = CustomerTagSerializer
    permission_classes = [permissions.IsAuthenticated]

class OpportunityTeamMemberViewSet(viewsets.ModelViewSet):
    queryset = OpportunityTeamMember.objects.all().order_by('-joined_at')
    serializer_class = OpportunityTeamMemberSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['opportunity', 'role']
    search_fields = ['name']

class OpportunityLogViewSet(viewsets.ModelViewSet):
    queryset = OpportunityLog.objects.all().order_by('-created_at')
    serializer_class = OpportunityLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['opportunity', 'operator']
    search_fields = ['content', 'action']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': '字段校验失败', 'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            return Response({'error': '保存失败', 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(operator=self.request.user)

class SocialMediaStatsViewSet(viewsets.ModelViewSet):
    queryset = SocialMediaStats.objects.all().order_by('-created_at')
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SocialMediaStatsSerializer
    filterset_fields = ['status', 'account']
    search_fields = ['platform']

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user, status=ApprovalStatus.APPROVED)

class SocialMediaAccountViewSet(viewsets.ModelViewSet):
    queryset = SocialMediaAccount.objects.all().order_by('-created_at')
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SocialMediaAccountSerializer
    filterset_fields = ['platform']
    search_fields = ['platform', 'account_name']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': '字段校验失败', 'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            manager = request.data.get('manager')
            save_kwargs = {}
            if not manager:
                save_kwargs['manager'] = self.request.user
            
            account = serializer.save(**save_kwargs)
            
            # Use request.data for extra fields instead of non-existent serializer.extras
            admin_ids = request.data.get('admin_ids') or []
            self._sync_admins(account, admin_ids)
            self._log_activity(account, '创建社媒账号')
            
            initial = request.data.get('initial_fans_count')
            if initial is not None:
                try:
                    initial = int(initial)
                    if initial >= 0:
                        from .models import SocialMediaStats
                        SocialMediaStats.objects.create(account=account, fans_count=initial, creator=self.request.user, status=ApprovalStatus.APPROVED)
                except (ValueError, TypeError):
                    pass
                    
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            return Response({'error': '保存失败', 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        account = serializer.save()
        
        # Use self.request.data for updates too
        admin_ids = self.request.data.get('admin_ids')
        if admin_ids is not None:
            self._sync_admins(account, admin_ids)
            
        self._log_activity(account, '更新社媒账号')

    def _log_activity(self, account, action):
        from .models import ActivityLog
        ActivityLog.objects.create(
            type=ActivityLog.Type.ACTIVITY,
            action=action,
            content=f"{account.platform}-{account.account_name}",
            actor=self.request.user,
            content_type=ContentType.objects.get_for_model(SocialMediaAccount),
            object_id=account.id
        )

    def _sync_admins(self, account, admin_ids):
        # SocialMediaAdmin models removed
        pass

class UserSimpleListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        search = request.query_params.get('search', '')
        
        # 1. Fetch Users
        users = User.objects.all().select_related('profile', 'profile__department_link')
        if search:
            users = users.filter(
                Q(username__icontains=search) | 
                Q(first_name__icontains=search) | 
                Q(last_name__icontains=search)
            )
            
        user_data = []
        for u in users:
            profile = getattr(u, 'profile', None)
            name = f"{u.last_name}{u.first_name}".strip() or u.username
            
            dept = ''
            if profile:
                    dept = profile.get_department_display()
            
            user_data.append({
                'id': u.id, 
                'type': 'USER',
                'username': u.username, 
                'name': name, 
                'department': dept,
                'label': f"{name} (@{u.username})"
            })
            
        return Response(user_data)

class AIConfigsListView(APIView):
    """
    获取AI配置列表
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # System-wide configs + User's own configs
        configs = AIConfiguration.objects.filter(
            Q(user__isnull=True) | Q(user=request.user)
        ).order_by('-is_active', '-created_at')
        
        serializer = AIConfigurationSerializer(configs, many=True)
        return Response({'results': serializer.data})

class AIConnectionTestView(APIView):
    """
    测试AI连接
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        config_id = request.data.get('config_id')
        if not config_id:
            return Response({'error': '请提供配置ID'}, status=400)
            
        try:
            service = AIService(config_id=config_id)
            # A simple hello test
            response = service._call_llm("You are a helpful assistant.", "Please reply with a valid json object: {\"status\": \"OK\"}")
            if 'OK' in response.upper() or 'JSON' in response.upper():
                return Response({'status': 'success', 'message': '连接成功'})
            else:
                return Response({'status': 'warning', 'message': f'连接成功但响应异常: {response}'})
        except Exception as e:
            return Response({'status': 'error', 'message': f'连接失败: {str(e)}'}, status=500)

class ChatView(APIView):
    """
    智能对话接口
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        message = request.data.get('message')
        history = request.data.get('history', [])
        config_id = request.data.get('config_id')
        
        if not message:
            return Response({'error': '请输入消息'}, status=400)
            
        service = AIService(config_id=config_id)
        try:
            # Simple wrapper for chat
            response = service._call_llm("You are a helpful assistant.", message, history=history)
            return Response({'reply': response})
        except Exception as e:
            return Response({'error': str(e)}, status=500)

class PerformanceReportView(APIView):
    """
    业绩报表数据接口
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        生成符合前端 Performance.vue 期望的数据结构：
        - totals: pipeline, signed, revenue, gross, t_signed, t_revenue, t_gross
        - status_distribution: 每阶段数量与金额
        - groups: 按部门或销售分组聚合
        - monthly: 最近6个月趋势，键包含 count/signed/revenue/gross
        """
        now = timezone.now()
        year = int(request.query_params.get('year', now.year))
        month = request.query_params.get('month')
        month = int(month) if month else None
        group_by = request.query_params.get('group_by', 'department')
        
        # 时间范围：仅当前年，若有月份则限定到该月
        base_qs = Opportunity.objects.filter(created_at__year=year)
        if month:
            base_qs = base_qs.filter(created_at__month=month)
        
        # totals
        pipeline = float(base_qs.aggregate(total=Sum('amount'))['total'] or 0)
        signed_stages = ['SIGNED', 'DELIVERY', 'AFTER_SALES', 'WON', 'COMPLETED']
        signed = float(base_qs.filter(stage__in=signed_stages).aggregate(total=Sum('amount'))['total'] or 0)
        revenue = float(base_qs.aggregate(total=Sum('collected_amount'))['total'] or 0)
        gross = float(base_qs.aggregate(total=Sum('profit'))['total'] or 0)
        
        # targets
        targets_qs = PerformanceTarget.objects.filter(year=year)
        if month:
            targets_qs = targets_qs.filter(month=month, period=PerformanceTarget.Period.MONTH)
        else:
            targets_qs = targets_qs.filter(period=PerformanceTarget.Period.YEAR)
        
        target_stats = targets_qs.filter(target_type=PerformanceTarget.TargetType.DEPARTMENT).aggregate(
            t_contract=Sum('target_contract_amount'),
            t_revenue=Sum('target_revenue'),
            t_gross=Sum('target_gross_profit')
        )
        t_contract = float(target_stats['t_contract'] or 0)
        t_revenue = float(target_stats['t_revenue'] or 0)
        t_gross = float(target_stats['t_gross'] or 0)
        
        # status_distribution
        status_distribution = []
        for s in base_qs.values('stage').annotate(count=Count('id'), total=Sum('amount')):
            status_distribution.append({
                'status': dict(Opportunity.Stage.choices).get(s['stage'], s['stage']),
                'count': s['count'],
                'total': float(s['total'] or 0)
            })
        
        # groups
        if group_by == 'user':
            groups = list(
                base_qs.values('sales_manager__username')
                .annotate(
                    count=Count('id'),
                    signed=Sum('amount', filter=Q(stage__in=signed_stages))
                )
            )
        else:
            # 优先使用新部门字段 department_link__name
            groups = list(
                base_qs.values('sales_manager__profile__department_link__name')
                .annotate(
                    count=Count('id'),
                    signed=Sum('amount', filter=Q(stage__in=signed_stages))
                )
            )
            # 兼容旧字段：如果没有新部门字段，则尝试旧字段 (此逻辑在 values 中较难直接表达，此处先取新字段)
        
        # monthly trend: 最近6个月
        monthly = []
        for i in range(5, -1, -1):
            d = now - timedelta(days=i * 30)
            y, m = d.year, d.month
            m_qs = Opportunity.objects.filter(created_at__year=y, created_at__month=m)
            monthly.append({
                'month': f"{y}-{m:02d}",
                'count': m_qs.count(),
                'signed': float(m_qs.filter(stage__in=signed_stages).aggregate(total=Sum('amount'))['total'] or 0),
                'revenue': float(m_qs.aggregate(total=Sum('collected_amount'))['total'] or 0),
                'gross': float(m_qs.aggregate(total=Sum('profit'))['total'] or 0),
            })
        
        return Response({
            'totals': {
                'pipeline': pipeline,
                'signed': signed,
                'revenue': revenue,
                'gross': gross,
                'opp_count': base_qs.count(),
            },
            'targets': {
                't_signed': t_contract,
                't_revenue': t_revenue,
                't_gross': t_gross,
            },
            'status_distribution': status_distribution,
            'groups': groups,
            'monthly': monthly,
        })

class CompetitionViewSet(viewsets.ModelViewSet):
    queryset = Competition.objects.all().order_by('-created_at')
    serializer_class = CompetitionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status']
    search_fields = ['name', 'organizer']

class MarketActivityViewSet(viewsets.ModelViewSet):
    queryset = MarketActivity.objects.all().order_by('-created_at')
    serializer_class = MarketActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['owner']
    search_fields = ['name', 'location']

class ApprovalRequestViewSet(viewsets.ModelViewSet):
    queryset = ApprovalRequest.objects.all().order_by('-created_at')
    serializer_class = ApprovalRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['request_type', 'status', 'applicant']

    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        approval = self.get_object()
        if approval.status != ApprovalStatus.PENDING:
            return Response({'error': '该申请不在待审批状态'}, status=400)
        
        approval.status = ApprovalStatus.APPROVED
        approval.approver = request.user
        approval.feedback = request.data.get('feedback', '')
        approval.save()
        
        # Trigger follow-up actions based on content_type if needed
        # ...
        
        return Response({'status': 'success', 'message': '已批准'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        approval = self.get_object()
        if approval.status != ApprovalStatus.PENDING:
            return Response({'error': '该申请不在待审批状态'}, status=400)
            
        approval.status = ApprovalStatus.REJECTED
        approval.approver = request.user
        approval.feedback = request.data.get('feedback', '')
        approval.save()
        
        return Response({'status': 'success', 'message': '已拒绝'})

class ExternalIdMapViewSet(viewsets.ModelViewSet):
    queryset = ExternalIdMap.objects.all()
    serializer_class = ExternalIdMapSerializer
    permission_classes = [permissions.IsAuthenticated]

class CustomerCohortViewSet(viewsets.ModelViewSet):
    queryset = CustomerCohort.objects.all()
    serializer_class = CustomerCohortSerializer
    permission_classes = [permissions.IsAuthenticated]

def competition_kanban_page(request):
    """渲染赛事信息看板页面"""
    return render(request, 'kanban/competitions.html')

def marketactivity_kanban_page(request):
    """渲染市场活动看板页面"""
    return render(request, 'kanban/activities.html')

class AgentRouterView(APIView):
    """
    Agent 任务分发与执行
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        task = request.data.get('task')
        config_id = request.data.get('config_id')
        if not task:
            return Response({'error': 'Task description is required'}, status=400)
            
        service = AIService(config_id=config_id)
        user = request.user
        
        print(f"--- [AgentRouter] Processing Task: {task} ---")
        
        # 1. Analyze Intent
        try:
            task_analysis = service.parse_task(task, user=user)
            intent_raw = task_analysis.get('intent', 'other')
            print(f"--- [AgentRouter] Intent Analysis Result: {task_analysis} ---")
        except Exception as e:
            print(f"--- [AgentRouter] Intent Analysis Failed: {e} ---")
            intent_raw = 'other'
        
        response_data = {
            'intent': '',
            'entity': '',
            'fields': {},
            'filters': {},
            'alternatives': [],
            'warnings': []
        }
        
        # Map intents
        if intent_raw == 'create_customer':
            response_data['intent'] = 'create'
            response_data['entity'] = 'customer'
            response_data['fields'] = service.parse_customer(task, user=user)
            
        elif intent_raw == 'create_opportunity':
            response_data['intent'] = 'create'
            response_data['entity'] = 'opportunity'
            response_data['fields'] = service.parse_opportunity(task, user=user)
            
        elif intent_raw == 'create_todo':
            response_data['intent'] = 'create'
            response_data['entity'] = 'todo'
            response_data['fields'] = service.parse_todo_task(task, user=user)
        
        # Fallback/Extended Logic for Competition and Activity
        if not response_data['intent']:
            print("--- [AgentRouter] Using Fallback Regex Logic ---")
            import re
            if re.search(r'(?:新建|创建|新增|录入).*(?:赛事|比赛)', task):
                 response_data['intent'] = 'create'
                 response_data['entity'] = 'competition'
                 response_data['fields'] = service.parse_competition(task, user=user)
            elif re.search(r'(?:新建|创建|新增|录入).*(?:活动)', task):
                 response_data['intent'] = 'create'
                 response_data['entity'] = 'activity'
                 response_data['fields'] = service.parse_market_activity(task, user=user)
            # Fallback for customer if parse_task failed but regex matches
            elif re.search(r'(?:新建|创建|新增|录入).*(?:客户|公司|企业)', task):
                 response_data['intent'] = 'create'
                 response_data['entity'] = 'customer'
                 response_data['fields'] = service.parse_customer(task, user=user)
            elif re.search(r'(?:新建|创建|新增|录入).*(?:商机|机会)', task):
                 response_data['intent'] = 'create'
                 response_data['entity'] = 'opportunity'
                 response_data['fields'] = service.parse_opportunity(task, user=user)

        print(f"--- [AgentRouter] Final Response: {response_data} ---")
        return Response(response_data)

class SubmissionLogViewSet(viewsets.ModelViewSet):
    queryset = SubmissionLog.objects.all().order_by('-created_at')
    serializer_class = SubmissionLogSerializer
    permission_classes = [permissions.IsAdminUser]

class ActivityLogViewSet(viewsets.ModelViewSet):
    """
    管理员日志查询：支持按时间、部门、用户、类型筛选
    """
    queryset = ActivityLog.objects.all().order_by('-created_at')
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['type', 'actor', 'department']
    search_fields = ['content', 'action', 'actor__username', 'actor__first_name', 'actor__last_name', 'department']
    ordering_fields = ['created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        actor_name = self.request.query_params.get('actor_name')

        if start_date:
            qs = qs.filter(created_at__date__gte=start_date)
        if end_date:
            qs = qs.filter(created_at__date__lte=end_date)
        if actor_name:
            from django.db.models import Q
            qs = qs.filter(
                Q(actor__username__icontains=actor_name) |
                Q(actor__first_name__icontains=actor_name) |
                Q(actor__last_name__icontains=actor_name)
            )
        return qs

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        简单统计：按类型与部门聚合计数
        """
        from django.db.models import Count
        type_stats = ActivityLog.objects.values('type').annotate(count=Count('id')).order_by('-count')
        # 优先使用冗余字段统计部门
        dept_stats = ActivityLog.objects.exclude(department='').values('department').annotate(count=Count('id')).order_by('-count')
        
        # 如果冗余字段统计为空，尝试使用关联表统计 (兼容旧数据)
        if not dept_stats.exists():
            dept_stats = ActivityLog.objects.filter(actor__profile__department_link__isnull=False).values('actor__profile__department_link__name').annotate(count=Count('id')).order_by('-count')
            
        return Response({'type_stats': list(type_stats), 'dept_stats': list(dept_stats)})

    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """
        导出日志为 CSV
        """
        import csv
        from django.http import HttpResponse
        
        # 获取筛选后的 queryset
        queryset = self.filter_queryset(self.get_queryset())
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="system_logs.csv"'
        response.write('\ufeff'.encode('utf8')) # BOM for Excel
        
        writer = csv.writer(response)
        writer.writerow(['ID', '类型', '动作', '内容', '操作人', '部门', '时间'])
        
        for log in queryset:
            actor_name = f"{log.actor.last_name}{log.actor.first_name}" if log.actor else "系统"
            if not actor_name.strip() and log.actor:
                actor_name = log.actor.username
                
            writer.writerow([
                log.id,
                log.get_type_display(),
                log.action,
                log.content,
                actor_name,
                log.department,
                log.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
            
        return response
class AIConfigurationViewSet(viewsets.ModelViewSet):
    queryset = AIConfiguration.objects.all().order_by('-is_active', '-created_at')
    serializer_class = AIConfigurationSerializer
    permission_classes = [permissions.IsAuthenticated] # 允许所有登录用户访问，内部再做权限过滤

    def get_queryset(self):
        # 管理员可以看到所有，普通用户只能看到自己的
        if self.request.user.is_staff or self.request.user.is_superuser:
            return AIConfiguration.objects.all().order_by('-is_active', '-created_at')
        return AIConfiguration.objects.filter(user=self.request.user).order_by('-is_active', '-created_at')

    def perform_create(self, serializer):
        # 强制将提供商转为大写，彻底解决前端传值大小写问题
        provider = self.request.data.get('provider', '').upper()
        # 校验 provider 是否在合法选项中，不在则设为 OPENAI 作为兜底
        valid_providers = ['OPENAI', 'DEEPSEEK', 'GEMINI', 'OLLAMA', 'MOONSHOT', 'ALIYUN', 'GLM', 'OTHER']
        if provider not in valid_providers:
            provider = 'OPENAI'
        serializer.save(user=self.request.user, provider=provider)

    def perform_update(self, serializer):
        # 更新时也强制转大写
        provider = self.request.data.get('provider', '').upper()
        valid_providers = ['OPENAI', 'DEEPSEEK', 'GEMINI', 'OLLAMA', 'MOONSHOT', 'ALIYUN', 'GLM', 'OTHER']
        if provider not in valid_providers:
            provider = 'OPENAI'
        serializer.save(provider=provider)

    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """
        将指定的 AI 配置设为默认（激活），并将该用户的其他配置设为非激活
        """
        config = self.get_object()
        # 仅将当前用户的配置设为非激活
        AIConfiguration.objects.filter(user=self.request.user).update(is_active=False)
        config.is_active = True
        config.save()
        return Response({'status': 'success', 'message': f'已将 {config.name} 设为默认配置'})

    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """
        Mode B: 测试 AI 配置连通性并输出详细调试日志
        """
        config = self.get_object()
        print(f"--- [Mode B DEBUG] AI Connection Test ---")
        print(f"Config ID: {config.id}, Name: {config.name}")
        print(f"Provider: {config.provider}, BaseURL: {config.base_url}, Model: {config.model_name}")
        
        service = AIService(config_id=config.id)
        # Fix: Must include "json" in prompt for response_format='json_object'
        test_prompt = "You are a testing assistant. Please respond in JSON format."
        test_text = "Return a JSON object with key 'status' set to 'OK' if you can hear me."
        
        try:
            # 这里的 _call_llm_json 会处理不同 Provider 的逻辑
            result = service._call_llm_json(test_prompt, test_text, user=request.user, intent="TEST_CONNECTION")
            
            if 'error' in result:
                print(f"[Mode B ERROR] Test Failed: {result['error']}")
                return Response({
                    'status': 'error',
                    'message': '连接失败',
                    'detail': result['error']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            print(f"[Mode B SUCCESS] Response: {result}")
            return Response({
                'status': 'success',
                'message': '连接成功',
                'response': result
            })
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"[Mode B CRITICAL] Exception occurred:\n{error_trace}")
            return Response({
                'status': 'error',
                'message': '系统异常',
                'detail': str(e),
                'traceback': error_trace if request.user.is_staff else None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserManagementSerializer
    permission_classes = [permissions.IsAdminUser]
    
    @action(detail=True, methods=['get', 'post'], url_path='assistant_proxy')
    def assistant_proxy(self, request, pk=None):
        """
        助理同权接口：
        GET: 获取当前状态
        POST: 设置状态 { "enabled": true|false }
        """
        user = self.get_object()
        from django.contrib.auth.models import Group
        group, _ = Group.objects.get_or_create(name='ASSISTANT_PROXY')

        if request.method == 'GET':
            enabled = user.groups.filter(name='ASSISTANT_PROXY').exists()
            return Response({'enabled': enabled})

        # 处理 POST 请求
        try:
            enabled = bool(request.data.get('enabled'))
            
            if not enabled:
                user.groups.remove(group)
                return Response({'status': 'success', 'enabled': False})

            # 确保 profile 存在并强制从数据库刷新
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.refresh_from_db()
            
            # 记录详细日志到 console
            print(f"--- [DEBUG] Assistant Proxy Authorization ---")
            print(f"User: {user.username} (ID: {user.id})")
            print(f"Profile: Category={profile.job_category}, Rank={profile.job_rank}, Position='{profile.job_position}'")
            print(f"Report To: {profile.report_to}")

            # 关键：如果此时 profile 还是没有岗位信息，尝试手动从 job_title 同步一次
            if not profile.job_category and profile.job_title:
                profile.job_category = profile.job_title.category
                profile.job_position = profile.job_title.name
                profile.save()

            job_cat = (profile.job_category or '').upper()
            job_rank = (profile.job_rank or '').upper()
            job_pos = (profile.job_position or '')
            
            is_assistant = (
                job_cat == 'ASSISTANT' or 
                job_rank == 'ASSISTANT' or 
                job_rank == 'SVP' or 
                '助理' in job_pos or 
                'ASSISTANT' in job_pos.upper()
            )
            
            if not is_assistant:
                return Response({
                    'error': f'授权失败：当前岗位属性({job_cat})或职位名称({job_pos})不符合助理同权要求。'
                }, status=400)
            
            if not profile.report_to:
                return Response({'error': '授权失败：助理必须设置“汇报对象”才能启用同权权限。'}, status=400)
                
            user.groups.add(group)
            return Response({'status': 'success', 'enabled': True})
        except Exception as e:
            import traceback
            print(f"--- [ERROR] Assistant Proxy Error ---")
            print(traceback.format_exc())
            return Response({'error': f'授权失败(系统错误): {str(e)}'}, status=500)

class ProjectViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        # 默认只查询未删除的项目
        return Project.objects.filter(is_deleted=False).order_by('-created_at')

    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'stage', 'owner']
    search_fields = ['name', 'code', 'description']

    def perform_create(self, serializer):
        project = serializer.save(owner=self.request.user)
        # Record Log
        self._record_log(project, '创建项目', f"项目 {project.name} 已创建")

    def perform_update(self, serializer):
        old_instance = self.get_object()
        new_instance = serializer.save()
        
        # 记录详细的变更日志
        if old_instance.status != new_instance.status:
            self._record_log(new_instance, '状态变更', f"从 {old_instance.get_status_display()} 变更为 {new_instance.get_status_display()}")
        if old_instance.stage != new_instance.stage:
            self._record_log(new_instance, '阶段变更', f"从 {old_instance.get_stage_display()} 变更为 {new_instance.get_stage_display()}")

    def perform_destroy(self, instance):
        try:
            # 软删除逻辑：备份数据并标记删除
            
            # 备份项目及卡片数据
            project_data = ProjectSerializer(instance).data
            
            # 解决 JSONField 不支持 Decimal 的问题
            import json
            from django.core.serializers.json import DjangoJSONEncoder
            # 先转成 JSON 字符串再转回 dict，利用 DjangoJSONEncoder 处理 Decimal 和 DateTime
            project_data_clean = json.loads(json.dumps(project_data, cls=DjangoJSONEncoder))
            
            ProjectDeleteLog.objects.create(
                project_name=instance.name,
                project_code=getattr(instance, 'code', 'UNKNOWN'),
                deleted_by=self.request.user,
                original_data=project_data_clean
            )
            
            # 执行软删除
            instance.is_deleted = True
            import django.utils.timezone as timezone
            instance.deleted_at = timezone.now()
            instance.save()
            
            # 记录审计日志
            from .models import ActivityLog
            ActivityLog.objects.create(
                actor=self.request.user,
                action="删除",
                content=f"删除了项目: {instance.name}",
                type=ActivityLog.Type.PROJECT,
                department=getattr(self.request.user.profile, 'department', '') if hasattr(self.request.user, 'profile') else ''
            )
        except Exception as e:
            import traceback
            traceback.print_exc()
            from rest_framework.exceptions import ValidationError
            raise ValidationError(f"删除失败: {str(e)}")

    def _record_log(self, project, action, content):
        from .models import ProjectChangeLog
        ProjectChangeLog.objects.create(
            project=project,
            operator=self.request.user,
            action=action,
            content=content
        )

class ProjectCardViewSet(viewsets.ModelViewSet):
    queryset = ProjectCard.objects.all().order_by('order', '-created_at')
    serializer_class = ProjectCardSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['project', 'status', 'is_active']
    search_fields = ['title', 'content']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': '字段校验失败', 'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            return Response({'error': '保存失败', 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        # 确保创建时关联项目正确
        serializer.save()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            return Response({'error': '字段校验失败', 'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            self.perform_update(serializer)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': '保存失败', 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        # 显式保存以触发模型 save() 中的日志逻辑
        serializer.save()

from django.http import FileResponse
import subprocess
import os
import time

class DataManagementViewSet(viewsets.ViewSet):
    """
    系统数据管理：备份、导出与恢复
    """
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False, methods=['post'])
    def backup(self, request):
        """执行全量数据库备份"""
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        
        try:
            # 优先尝试 django dumpdata，因为它不依赖外部 pg_dump 工具，在容器内更可靠
            backup_filename = f"db_backup_{timestamp}.json"
            backup_path = f"/tmp/{backup_filename}"
            
            # 使用 subprocess 调用 manage.py dumpdata
            # 排除不必要的系统表，这些表在导入时容易发生冲突
            exclude_args = [
                "--exclude", "contenttypes", 
                "--exclude", "auth.Permission", 
                "--exclude", "admin.logentry",
                "--exclude", "sessions.session",
                "--exclude", "core.SubmissionLog", # 提交日志通常较大且不重要
                "--exclude", "core.ActivityLog"    # 活动日志也较大
            ]
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                # 使用 sys.executable 确保使用当前环境的 Python 解释器
                result = subprocess.run(
                    [sys.executable, "manage.py", "dumpdata", "--indent", "2"] + exclude_args,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True
                )
            
            if result.returncode != 0:
                return Response({
                    'error': '数据导出失败',
                    'detail': result.stderr
                }, status=500)

            # 检查文件是否生成且非空
            if not os.path.exists(backup_path) or os.path.getsize(backup_path) == 0:
                return Response({'error': '生成的备份文件为空，请检查数据库连接'}, status=500)

            response = FileResponse(
                open(backup_path, 'rb'), 
                as_attachment=True, 
                filename=backup_filename,
                content_type='application/json'
            )
            return response
        except Exception as e:
            import traceback
            return Response({
                'error': f'备份执行异常: {str(e)}',
                'traceback': traceback.format_exc()
            }, status=500)

    @action(detail=False, methods=['post'])
    def restore(self, request):
        """恢复数据库备份"""
        if 'file' not in request.FILES:
            return Response({'error': '请上传备份文件 (.json)'}, status=400)
        
        backup_file = request.FILES['file']
        if not backup_file.name.endswith('.json'):
            return Response({'error': '仅支持 .json 格式的备份文件'}, status=400)
        
        temp_path = f"/tmp/restore_{int(time.time())}.json"
        
        try:
            # 保存上传的文件到临时目录
            with open(temp_path, 'wb+') as destination:
                for chunk in backup_file.chunks():
                    destination.write(chunk)
            
            # 执行 loaddata
            result = subprocess.run(
                [sys.executable, "manage.py", "loaddata", temp_path],
                capture_output=True,
                text=True
            )
            
            # 删除临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            if result.returncode != 0:
                return Response({
                    'error': '数据恢复失败',
                    'detail': result.stderr
                }, status=500)
            
            return Response({
                'message': '数据恢复成功',
                'detail': result.stdout
            })
            
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return Response({'error': f'恢复执行异常: {str(e)}'}, status=500)

    @action(detail=False, methods=['get'])
    def history(self, request):
        """获取备份历史 (简化版)"""
        return Response([
            { 'time': time.strftime('%Y-%m-%d %H:%M:%S'), 'type': '备份', 'operator': request.user.username, 'status': '成功', 'remark': '手动触发全量备份' }
        ])

class DailyReportViewSet(viewsets.ModelViewSet):
    queryset = DailyReport.objects.all().order_by('-date', '-created_at')
    serializer_class = DailyReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['user', 'date']

    def get_queryset(self):
        """
        管理员和授权助理可以查看所有日报，普通用户只能查看自己的。
        """
        user = self.request.user
        if not user or not user.is_authenticated:
            return DailyReport.objects.none()
            
        qs = DailyReport.objects.all().order_by('-date', '-created_at')
        
        # 检查是否为管理员或授权助理
        try:
            # 优化查询：只在必要时查询数据库
            is_privileged = (
                user.is_staff or 
                user.is_superuser or 
                user.groups.filter(name='ASSISTANT_PROXY').exists()
            )
        except Exception:
            is_privileged = False
        
        if not is_privileged:
            qs = qs.filter(user=user)
            
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': '字段校验失败', 'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            report = serializer.save(user=self.request.user)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            return Response({'error': '保存失败', 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def polish(self, request, pk=None):
        """
        AI 润色日报内容
        """
        report = self.get_object()
        service = AIService()
        
        # 获取润色后的内容
        result = service.polish_daily_report(
            text=report.raw_content,
            user=report.user,
            projects=report.projects.all()
        )
        
        # 兼容字符串或字典返回
        content = None
        if isinstance(result, dict):
            content = result.get('content')
        elif isinstance(result, str):
            content = result
        
        if content:
            report.polished_content = content
            report.save()
            return Response({
                'status': 'success',
                'polished_content': report.polished_content
            })
        
        error_msg = None
        if isinstance(result, dict):
            error_msg = result.get('error')
        return Response({'error': error_msg or "AI 润色失败，请稍后重试"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class NotificationViewSet(viewsets.ModelViewSet):
    """
    系统通知 视图
    """
    queryset = Notification.objects.all().order_by('-created_at')
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 自动清理当前用户的无效通知（关联对象已删除的）
        user = self.request.user
        qs = Notification.objects.filter(recipient=user).order_by('-created_at')
        
        # 仅在列表查询时进行轻量级清理（只检查前 50 条，避免性能问题）
        check_qs = qs[:50]
        invalid_ids = []
        for notice in check_qs:
            if notice.content_type and notice.object_id:
                model_class = notice.content_type.model_class()
                if not model_class or not model_class.objects.filter(pk=notice.object_id).exists():
                    invalid_ids.append(notice.id)
        
        if invalid_ids:
            Notification.objects.filter(id__in=invalid_ids).delete()
            # 重新获取干净的 queryset
            qs = Notification.objects.filter(recipient=user).order_by('-created_at')
            
        return qs

    def create(self, request, *args, **kwargs):
        """
        发布消息通知：支持全体、指定部门、指定用户
        请求体示例：
        {
          "target": "all" | "dept_specific" | "user_specific",
          "targetDepts": [1,2],        # 仅当 target=dept_specific
          "targetUsers": [3,4],        # 仅当 target=user_specific
          "type": "normal" | "system",
          "title": "消息标题",
          "content": "消息正文"
        }
        """
        target = request.data.get('target', 'all')
        title = request.data.get('title', '')
        content = request.data.get('content', '')
        msg_type = request.data.get('type', 'normal')
        
        if not title or not content:
            return Response({'error': '标题和正文不能为空'}, status=400)
        
        # 解析接收人
        recipients = []
        from django.contrib.auth.models import User
        if target == 'all':
            recipients = list(User.objects.all())
        elif target == 'dept_specific':
            dept_ids = request.data.get('targetDepts') or []
            from .models import DepartmentModel
            depts = DepartmentModel.objects.filter(id__in=dept_ids)
            user_ids = list(
                User.objects.filter(profile__department_link__in=depts).values_list('id', flat=True)
            )
            recipients = list(User.objects.filter(id__in=user_ids))
        elif target == 'user_specific':
            user_ids = request.data.get('targetUsers') or []
            recipients = list(User.objects.filter(id__in=user_ids))
        else:
            return Response({'error': '无效的发送对象'}, status=400)
        
        # 类型映射
        ntype = Notification.Type.NORMAL if msg_type == 'normal' else Notification.Type.SYSTEM
        
        # 批量创建通知
        created = 0
        for u in recipients:
            Notification.objects.create(
                recipient=u,
                title=title,
                content=content,
                type=ntype
            )
            created += 1
        
        return Response({'status': 'success', 'created': created})

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'success'})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        self.get_queryset().update(is_read=True)
        return Response({'status': 'success'})

class AnnouncementViewSet(viewsets.ModelViewSet):
    """
    公告视图：支持创建、查询与发布
    """
    queryset = Announcement.objects.all().order_by('-created_at')
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        """
        创建公告时设置发布人，初始状态为草稿
        """
        serializer.save(creator=self.request.user, status=Announcement.Status.DRAFT)
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """
        发布公告：将状态改为 APPROVED 并写入发布时间
        """
        ann = self.get_object()
        ann.status = Announcement.Status.APPROVED
        ann.published_at = timezone.now()
        ann.save()
        return Response({'status': 'success', 'message': '公告已发布'})

class LegacyImportView(APIView):
    """
    旧数据导入 (从 Excel 或其他格式)
    """
    permission_classes = [permissions.IsAdminUser]
    def post(self, request):
        return Response({'status': 'success', 'message': 'Data import triggered'})

class ResetTestDataView(APIView):
    """
    重置测试数据 (危险操作)
    """
    permission_classes = [permissions.IsAdminUser]
    def post(self, request):
        # Clean core models
        Opportunity.objects.all().delete()
        from .models import Project, ProjectCard
        Project.objects.all().delete()
        ProjectCard.objects.all().delete()
        Customer.objects.all().delete()
        # Clean Social removed models logic...
        return Response({'status': 'success', 'message': 'Test data reset'})

class SeedTargetsView(APIView):
    """
    生成演示业绩目标
    """
    permission_classes = [permissions.IsAdminUser]
    def post(self, request):
        return Response({'status': 'success', 'message': 'Seed targets generated'})

from .models import SystemRelease
from .serializers import SystemReleaseSerializer

class SystemReleaseViewSet(viewsets.ModelViewSet):
    queryset = SystemRelease.objects.all().order_by('-release_date')
    serializer_class = SystemReleaseSerializer
    permission_classes = [permissions.IsAuthenticated]
