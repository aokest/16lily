根据您的反馈，我将对系统进行以下关键调整和优化：

## 📅 优化开发计划

### **Phase 1: UI 细节与导航重构 (🔥 优先)**
1.  **登录界面文案修正**：
    *   将 "欢迎回到十六军团作战指挥中心" 修改为 "欢迎回到石榴经营"。
2.  **导航栏重构 (Sidebar Organization)**：
    *   使用 Jazzmin 的 `custom_links` 和 `app_groups` 功能，将左侧混乱的菜单重新分组：
        *   **个人中心**：公告通知、我的待办、工作日报/周报、个人资料。
        *   **商机管理**：商机列表、商机跟进。
        *   **市场活动管理**：活动列表、粉丝数据统计（媒体矩阵）。
        *   **赛事管理**：赛事列表。
        *   **客户关系管理**：客户管理、联系人管理。
        *   **认证和授权**：用户、组、组织结构（Profile）、令牌。
3.  **公告发布优化**：
    *   将 `Announcement` 模型的 `department` 字段改为 `departments` (多对多字段)，支持多选。
    *   增加“所有部门”选项或逻辑，实现全员群发。

### **Phase 2: 个人中心公告栏 (Dashboard Widget)**
1.  **公告展示组件**：
    *   在 Django Admin 的首页（Dashboard）顶部增加一个显著的“公告通知栏”。
    *   逻辑：显示最新发布的系统公告 + 当前用户所属部门的部门公告。
    *   样式：使用卡片或跑马灯形式，确保一登录就能看到。

### **Phase 3: 系统功能微调**
1.  **组织架构数据**：确保 UserProfile 中的部门信息能被正确用于公告筛选。

---

## 🚀 立即执行：UI 与导航重构
我将按照您的分组要求，修改 `jazzmin_settings.py` 和相关模型。

1.  修改 `jazzmin_settings.py`：调整 `site_header` 和 `welcome_sign`。
2.  重构 `jazzmin_settings.py` 中的菜单配置，实现分组折叠效果。
3.  修改 `core/models.py`：将 `Announcement.department` 改为 `ManyToManyField`。
4.  自定义 Dashboard 模板：插入公告栏组件。