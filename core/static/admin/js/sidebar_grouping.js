document.addEventListener('DOMContentLoaded', function () {
    // Sidebar Grouping Logic
    const sidebarMenu = document.querySelector('.nav-sidebar');
    if (sidebarMenu) {
        // Define Groups and their start items (based on href or text)
        const groups = [
            { header: '我的工作台', startModel: 'userprofile' }, // UserProfile, Announcement, Todo, WorkReport
            { header: '商机管理', startModel: 'opportunity' }, // Opportunity, OpportunityLog
            { header: '市场与赛事', startModel: 'marketactivity' }, // MarketActivity, SocialMedia, Competition
            { header: '客户关系', startModel: 'customer' }, // Customer, Contact
            { header: '系统配置', startModel: 'aiconfiguration' }, // AI, Prompt, Dept
            { header: '用户管理', startModel: 'user' } // User, Group
        ];

        groups.forEach(group => {
            // Find the nav-item that corresponds to the startModel
            // Jazzmin links look like /admin/app/model/
            const links = sidebarMenu.querySelectorAll('.nav-link');
            let targetLink = null;
            
            for (let link of links) {
                if (link.href.includes(`/${group.startModel}/`)) {
                    targetLink = link;
                    break;
                }
            }

            if (targetLink) {
                const navItem = targetLink.closest('.nav-item');
                if (navItem) {
                    const headerLi = document.createElement('li');
                    headerLi.className = 'nav-header';
                    headerLi.style.cssText = 'padding: 0.5rem 1rem; font-size: 0.8rem; font-weight: 600; color: #d4ac0d; text-transform: uppercase; letter-spacing: 1px; margin-top: 10px; border-top: 1px solid rgba(255,255,255,0.1);';
                    headerLi.innerText = group.header;
                    navItem.parentNode.insertBefore(headerLi, navItem);
                }
            }
        });
        
        // Hide the default "Core" or "Authentication" headers if Jazzmin added them
        const defaultHeaders = sidebarMenu.querySelectorAll('.nav-header');
        defaultHeaders.forEach(header => {
            const text = header.innerText.trim();
            if (text === 'CORE' || text === 'AUTHENTICATION' || text === '核心业务') {
                header.style.display = 'none';
            }
        });
    }
});
