# core/models.py addition

from django.db import models
from django.contrib.auth.models import User
from .models import Opportunity, ApprovalRequest, ApprovalStatus

class OpportunityTransferApplication(models.Model):
    """
    商机转移申请
    """
    class TransferType(models.TextChoices):
        VOLUNTARY = 'VOLUNTARY', '主动移交'
        ASSIGN = 'ASSIGN', '上级指派'
        
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='transfer_applications', verbose_name='关联商机')
    applicant = models.ForeignKey(User, on_delete=models.PROTECT, related_name='applied_transfers', verbose_name='申请人')
    
    current_owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='transfers_from', verbose_name='当前负责人')
    target_owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='transfers_to', verbose_name='目标负责人')
    
    reason = models.TextField(verbose_name='移交原因')
    status = models.CharField(max_length=20, choices=ApprovalStatus.choices, default=ApprovalStatus.PENDING, verbose_name='审批状态')
    
    # Approval
    approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_transfers', verbose_name='审批人')
    approval_note = models.TextField(blank=True, verbose_name='审批意见')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='申请时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return f"Transfer {self.opportunity.name}: {self.current_owner} -> {self.target_owner}"

    class Meta:
        verbose_name = '商机移交申请'
        verbose_name_plural = '商机移交申请'
