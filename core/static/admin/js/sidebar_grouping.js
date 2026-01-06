// Jazzmin: Sidebar grouping / quick links injection
(function() {
  document.addEventListener('DOMContentLoaded', function() {
    try {
      // Add quick external links section at top of sidebar
      const sidebar = document.querySelector('.sidebar .nav-sidebar');
      if (!sidebar) return;
      const quick = document.createElement('li');
      quick.className = 'nav-item';
      quick.innerHTML = `
        <a href="http://127.0.0.1:8080/#/crm" class="nav-link" target="_blank">
          <i class="nav-icon fas fa-home"></i>
          <p>CRM首页</p>
        </a>
        <a href="http://127.0.0.1:8080/#/reports/performance" class="nav-link" target="_blank">
          <i class="nav-icon fas fa-chart-line"></i>
          <p>业绩报表</p>
        </a>
        <a href="http://127.0.0.1:8080/#/ai/chat" class="nav-link" target="_blank">
          <i class="nav-icon fas fa-robot"></i>
          <p>AI对话窗</p>
        </a>
        <a href="http://127.0.0.1:8000/api/dashboard/screen/" class="nav-link" target="_blank">
          <i class="nav-icon fas fa-tv"></i>
          <p>大屏战报</p>
        </a>
      `;
      sidebar.insertBefore(quick, sidebar.firstChild);
    } catch (e) {
      console.warn('Sidebar grouping script error:', e);
    }
  });
})(); 
