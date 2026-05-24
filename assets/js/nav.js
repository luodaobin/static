/**
 * 主题列表（按创建时间排序）
 * 新增主题时，在此数组末尾追加对象即可
 */
const themes = [
    // 格式: { name: "主题目录名", label: "展示名称", desc: "简短描述" }
    // 示例: { name: "portfolio", label: "作品集", desc: "展示个人项目与经历" }
    { name: "learn-rmb", label: "认识人民币", desc: "小学一年级数学课件，认识中国钱币" },
];

/**
 * 渲染导航栏链接
 */
function renderNav() {
    const navLinks = document.getElementById('navLinks');
    if (!navLinks) return;

    // 先清空现有内容（除了可能存在的其他固定链接）
    navLinks.innerHTML = '';

    themes.forEach(theme => {
        const a = document.createElement('a');
        a.href = `./${theme.name}/index.html`;
        a.textContent = theme.label || theme.name;
        navLinks.appendChild(a);
    });
}

/**
 * 渲染主题卡片网格
 */
function renderThemeCards() {
    const grid = document.getElementById('themesGrid');
    if (!grid) return;

    if (themes.length === 0) {
        grid.innerHTML = `
            <div class="theme-empty">
                <p>暂无主题，点击下方按钮创建你的第一个主题</p>
            </div>
        `;
        return;
    }

    grid.innerHTML = themes.map(theme => `
        <a class="theme-card" href="./${theme.name}/index.html">
            <h3>${escapeHtml(theme.label || theme.name)}</h3>
            <p>${escapeHtml(theme.desc || '')}</p>
            <div class="theme-arrow">→</div>
        </a>
    `).join('');
}

/**
 * 简单的 HTML 转义
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * 导航栏滚动效果
 */
function initScrollEffect() {
    const navbar = document.getElementById('navbar');
    if (!navbar) return;

    window.addEventListener('scroll', () => {
        if (window.scrollY > 10) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
}

/**
 * 移动端菜单切换
 */
function initMobileMenu() {
    const toggle = document.getElementById('navToggle');
    const links = document.getElementById('navLinks');
    if (!toggle || !links) return;

    toggle.addEventListener('click', () => {
        links.classList.toggle('open');
        const isOpen = links.classList.contains('open');
        toggle.setAttribute('aria-expanded', String(isOpen));
    });

    // 点击导航链接后关闭菜单
    links.addEventListener('click', (e) => {
        if (e.target.tagName === 'A') {
            links.classList.remove('open');
            toggle.setAttribute('aria-expanded', 'false');
        }
    });
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    renderNav();
    renderThemeCards();
    initScrollEffect();
    initMobileMenu();
});
