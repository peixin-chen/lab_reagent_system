/**
 * 实验室试剂管理系统 - 全局 JS
 */

// 密码显示/隐藏切换
function togglePwd(inputId, btn) {
    const input = document.getElementById(inputId);
    if (!input) return;
    if (input.type === 'password') {
        input.type = 'text';
        btn.innerHTML = '<i class="bi bi-eye-slash"></i>';
    } else {
        input.type = 'password';
        btn.innerHTML = '<i class="bi bi-eye"></i>';
    }
}

// 表单防重复提交
document.addEventListener('DOMContentLoaded', function () {
    // 所有表单提交后禁用提交按钮
    document.querySelectorAll('form').forEach(function (form) {
        form.addEventListener('submit', function () {
            const btn = form.querySelector('button[type="submit"]');
            if (btn && !btn.classList.contains('no-disable')) {
                btn.disabled = true;
                btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>处理中…';
            }
        });
    });

    // 5秒后自动关闭 Flash 消息
    setTimeout(function () {
        document.querySelectorAll('.flash-messages .alert').forEach(function (el) {
            var bsAlert = bootstrap.Alert.getOrCreateInstance(el);
            if (bsAlert) {
                try { bsAlert.close(); } catch (e) { el.remove(); }
            }
        });
    }, 5000);

    // 模态框打开后自动聚焦第一个输入框
    document.querySelectorAll('.modal').forEach(function (modal) {
        modal.addEventListener('shown.bs.modal', function () {
            var firstInput = modal.querySelector('input:not([type="hidden"]):not([disabled])');
            if (firstInput) firstInput.focus();
        });
        // 模态框关闭后重置表单
        modal.addEventListener('hidden.bs.modal', function () {
            var form = modal.querySelector('form');
            if (form) {
                // 恢复禁用的按钮
                form.querySelectorAll('button[type="submit"]').forEach(function (btn) {
                    btn.disabled = false;
                    // 通过 data 属性恢复原始文本
                    if (btn.dataset.origHtml) {
                        btn.innerHTML = btn.dataset.origHtml;
                    }
                });
            }
        });
    });

    // 保存按钮原始内容
    document.querySelectorAll('.modal button[type="submit"]').forEach(function (btn) {
        btn.dataset.origHtml = btn.innerHTML;
    });

    // 初始化 Bootstrap 工具提示
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
        new bootstrap.Tooltip(el);
    });
});
