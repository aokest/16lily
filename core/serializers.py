from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Opportunity, OpportunityLog, PerformanceTarget, Competition, MarketActivity

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['department', 'job_role', 'avatar']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'profile']

    def get_full_name(self, obj):
        # 如果有last_name + first_name (中文习惯通常是last_name+first_name，但Django默认是first+last)
        # 这里我们简单处理：如果有last_name或first_name，就拼起来，否则返回username
        name = f"{obj.last_name}{obj.first_name}".strip()
        return name if name else obj.username

class OpportunityLogSerializer(serializers.ModelSerializer):
    operator_name = serializers.SerializerMethodField()
    opportunity_name = serializers.CharField(source='opportunity.name', read_only=True)
    opportunity_amount = serializers.DecimalField(source='opportunity.amount', max_digits=12, decimal_places=2, read_only=True)
    opportunity_status = serializers.CharField(source='opportunity.status', read_only=True)
    
    class Meta:
        model = OpportunityLog
        fields = ['id', 'action', 'content', 'stage_snapshot', 'created_at', 'operator', 'operator_name', 'opportunity_name', 'opportunity_amount', 'opportunity_status']

    def get_operator_name(self, obj):
        if not obj.operator:
            return "Unknown"
        name = f"{obj.operator.last_name}{obj.operator.first_name}".strip()
        return name if name else obj.operator.username

class OpportunitySerializer(serializers.ModelSerializer):
    logs = OpportunityLogSerializer(many=True, read_only=True)
    creator_name = serializers.SerializerMethodField()
    sales_manager_name = serializers.SerializerMethodField()
    project_manager_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Opportunity
        fields = '__all__'
        read_only_fields = ['creator', 'created_at', 'updated_at', 'revenue', 'profit', 'gross_profit']
        extra_kwargs = {
            'sales_manager': {'required': False}, # Allow backend to set default
        }

    def get_creator_name(self, obj):
        if not obj.creator:
            return "Unknown"
        name = f"{obj.creator.last_name}{obj.creator.first_name}".strip()
        return name if name else obj.creator.username

    def get_sales_manager_name(self, obj):
        if not obj.sales_manager:
            return "Unknown"
        name = f"{obj.sales_manager.last_name}{obj.sales_manager.first_name}".strip()
        return name if name else obj.sales_manager.username

    def get_project_manager_name(self, obj):
        if not obj.project_manager:
            return ""
        name = f"{obj.project_manager.last_name}{obj.project_manager.first_name}".strip()
        return name if name else obj.project_manager.username

class PerformanceTargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerformanceTarget
        fields = '__all__'


class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = [
            'id', 'name', 'status', 'time', 'end_time', 'location', 'type',
            'project_name', 'project_code', 'contact_person', 'owner_name', 'department_name',
            'duration', 'team_count', 'leader_count', 'participant_count',
            'challenge_count', 'challenge_type', 'impact_level', 'level', 'target_audience',
            'host_type', 'organizers', 'description', 'created_at'
        ]

class MarketActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketActivity
        fields = [
            'id', 'name', 'status', 'time', 'location', 'type', 'scale',
            'description', 'created_at'
        ]
