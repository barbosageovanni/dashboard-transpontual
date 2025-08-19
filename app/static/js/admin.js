// Sistema de Administração - Dashboard Baker
$(document).ready(function() {
    console.log('🔧 Sistema de Administração carregado');
    
    // Inicializar página
    loadUsers();
    loadSystemStats();
    
    // Configurar eventos
    setupEventListeners();
    
    // Auto-refresh a cada 5 minutos
    setInterval(loadSystemStats, 300000);
});

// Variáveis globais
let currentPage = 1;
let currentFilters = {
    search: '',
    role: '',
    status: ''
};
let selectedUserId = null;
let selectedUsername = '';

// ============================================================================
// FUNÇÕES DE CARREGAMENTO DE DADOS
// ============================================================================

function loadUsers(page = 1) {
    console.log('📋 Carregando usuários...');
    
    currentPage = page;
    
    // Mostrar loading
    $('#loadingContainer').show();
    $('#usersTable').hide();
    $('#paginationContainer').hide();
    
    // Preparar parâmetros
    const params = {
        page: page,
        per_page: 20,
        search: currentFilters.search,
        role: currentFilters.role,
        status: currentFilters.status
    };
    
    $.ajax({
        url: '/admin/api/users',
        method: 'GET',
        data: params,
        timeout: 10000,
        success: function(response) {
            if (response.success) {
                displayUsers(response.users);
                updatePagination(response.pagination);
                updateUserStats(response.pagination.total);
            } else {
                showError('Erro ao carregar usuários: ' + response.error);
            }
        },
        error: function(xhr) {
            console.error('Erro AJAX ao carregar usuários:', xhr);
            showError('Erro de conexão ao carregar usuários');
        },
        complete: function() {
            $('#loadingContainer').hide();
            $('#usersTable').show();
            $('#paginationContainer').show();
        }
    });
}

function loadSystemStats() {
    console.log('📊 Carregando estatísticas do sistema...');
    
    $.ajax({
        url: '/admin/api/system-stats',
        method: 'GET',
        success: function(response) {
            if (response.success) {
                updateStatsCards(response.stats);
            }
        },
        error: function(xhr) {
            console.error('Erro ao carregar estatísticas:', xhr);
        }
    });
}

function updateStatsCards(stats) {
    // Atualizar cards de estatísticas
    $('#totalUsers').text(stats.users.total);
    $('#activeUsers').text(stats.users.active);
    $('#adminUsers').text(stats.users.admins);
    $('#recentLogins').text(stats.users.recent_logins);
}

function updateUserStats(total) {
    $('#totalUsers').text(total);
}

// ============================================================================
// FUNÇÕES DE EXIBIÇÃO
// ============================================================================

function displayUsers(users) {
    const tbody = $('#usersTableBody');
    tbody.empty();
    
    if (users.length === 0) {
        tbody.append(`
            <tr>
                <td colspan="5" style="text-align: center; padding: 3rem; color: #666;">
                    <i class="fas fa-user-slash fa-3x mb-3"></i><br>
                    Nenhum usuário encontrado com os filtros aplicados
                </td>
            </tr>
        `);
        return;
    }
    
    users.forEach(user => {
        const row = createUserRow(user);
        tbody.append(row);
    });
    
    // Inicializar tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();
}

function createUserRow(user) {
    const statusClass = user.ativo ? 'status-active' : 'status-inactive';
    const statusText = user.ativo ? 'Ativo' : 'Inativo';
    const statusIcon = user.ativo ? 'fas fa-circle' : 'fas fa-circle';
    
    const roleClass = `role-${user.tipo_usuario}`;
    const roleIcon = {
        'admin': 'fas fa-crown',
        'moderator': 'fas fa-user-tie',
        'user': 'fas fa-user'
    }[user.tipo_usuario] || 'fas fa-user';
    
    return `
        <tr data-user-id="${user.id}">
            <td>
                <div class="user-info">
                    <div class="user-avatar">${user.avatar_letter}</div>
                    <div class="user-details">
                        <div class="user-name">${user.nome_completo || user.username}</div>
                        <div class="user-email">${user.email}</div>
                    </div>
                </div>
            </td>
            <td>
                <span class="role-badge ${roleClass}">
                    <i class="${roleIcon}"></i> ${user.role_label}
                </span>
            </td>
            <td>
                <span class="status-badge ${statusClass}">
                    <i class="${statusIcon}"></i> ${statusText}
                </span>
            </td>
            <td>
                <div>${user.last_login_formatted}</div>
                <small style="color: #666;">Total logins: ${user.total_logins || 0}</small>
            </td>
            <td>
                <div class="actions-dropdown">
                    <button class="dropdown-toggle" onclick="toggleDropdown(this)" 
                            data-bs-toggle="tooltip" title="Ações">
                        <i class="fas fa-ellipsis-v"></i>
                    </button>
                    <div class="dropdown-menu">
                        <a class="dropdown-item" onclick="editUser(${user.id})">
                            <i class="fas fa-edit"></i> Editar
                        </a>
                        <a class="dropdown-item" onclick="resetPassword(${user.id}, '${user.username}')">
                            <i class="fas fa-key"></i> Reset Senha
                        </a>
                        <a class="dropdown-item" onclick="toggleUserStatus(${user.id}, ${!user.ativo})">
                            <i class="fas fa-${user.ativo ? 'user-slash' : 'user-check'}"></i> 
                            ${user.ativo ? 'Desativar' : 'Ativar'}
                        </a>
                        <div style="border-top: 1px solid #eee; margin: 0.5rem 0;"></div>
                        <a class="dropdown-item danger" onclick="deleteUser(${user.id}, '${user.username}')">
                            <i class="fas fa-trash"></i> Excluir
                        </a>
                    </div>
                </div>
            </td>
        </tr>
    `;
}

function updatePagination(pagination) {
    const info = $('#paginationInfo');
    const controls = $('#paginationControls');
    
    // Informações da paginação
    const start = pagination.total > 0 ? ((pagination.page - 1) * pagination.per_page) + 1 : 0;
    const end = Math.min(pagination.page * pagination.per_page, pagination.total);
    
    info.text(`Exibindo ${start} a ${end} de ${pagination.total} usuários`);
    
    // Controles de paginação
    controls.empty();
    
    // Botão Anterior
    const prevButton = $(`
        <button class="page-btn ${!pagination.has_prev ? 'disabled' : ''}" 
                onclick="loadUsers(${pagination.page - 1})" 
                ${!pagination.has_prev ? 'disabled' : ''}>
            <i class="fas fa-chevron-left"></i> Anterior
        </button>
    `);
    controls.append(prevButton);
    
    // Páginas
    const startPage = Math.max(1, pagination.page - 2);
    const endPage = Math.min(pagination.pages, pagination.page + 2);
    
    for (let i = startPage; i <= endPage; i++) {
        const pageButton = $(`
            <button class="page-btn ${i === pagination.page ? 'active' : ''}" 
                    onclick="loadUsers(${i})">${i}</button>
        `);
        controls.append(pageButton);
    }
    
    // Botão Próximo
    const nextButton = $(`
        <button class="page-btn ${!pagination.has_next ? 'disabled' : ''}" 
                onclick="loadUsers(${pagination.page + 1})" 
                ${!pagination.has_next ? 'disabled' : ''}>
            Próximo <i class="fas fa-chevron-right"></i>
        </button>
    `);
    controls.append(nextButton);
}

// ============================================================================
// FUNÇÕES DE FILTROS E BUSCA
// ============================================================================

function setupEventListeners() {
    // Filtro de busca com debounce
    let searchTimeout;
    $('#searchInput').on('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            currentFilters.search = $(this).val().trim();
            filterUsers();
        }, 500);
    });
    
    // Enter para buscar imediatamente
    $('#searchInput').on('keypress', function(e) {
        if (e.which === 13) {
            currentFilters.search = $(this).val().trim();
            filterUsers();
        }
    });
    
    // Fechar dropdowns ao clicar fora
    $(document).on('click', function(e) {
        if (!$(e.target).closest('.actions-dropdown').length) {
            $('.dropdown-menu.show').removeClass('show');
        }
    });
    
    // Fechar modais com ESC
    $(document).on('keydown', function(e) {
        if (e.key === 'Escape') {
            $('.modal.show').removeClass('show');
        }
    });
}

function filterUsers() {
    // Atualizar filtros
    currentFilters.role = $('#roleFilter').val();
    currentFilters.status = $('#statusFilter').val();
    
    // Resetar para primeira página
    currentPage = 1;
    
    // Carregar usuários com filtros
    loadUsers(1);
}

function toggleDropdown(button) {
    const dropdown = $(button).parent();
    const menu = dropdown.find('.dropdown-menu');
    
    // Fechar todos os outros dropdowns
    $('.dropdown-menu.show').removeClass('show');
    
    // Alternar o dropdown atual
    menu.toggleClass('show');
}

// ============================================================================
// FUNÇÕES DE CRUD DE USUÁRIOS
// ============================================================================

function addUser() {
    const form = $('#addUserForm');
    const formData = getFormData(form);
    
    // Validação
    if (!form[0].checkValidity()) {
        form[0].reportValidity();
        return;
    }
    
    // Converter boolean
    formData.ativo = formData.ativo === 'true';
    
    console.log('➕ Criando usuário:', formData);
    
    $.ajax({
        url: '/admin/api/users',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function(response) {
            if (response.success) {
                showSuccess(response.message);
                closeModal('addUserModal');
                form[0].reset();
                
                // Mostrar senha temporária se foi gerada
                if (response.temp_password) {
                    showGeneratedPassword(response.temp_password);
                }
                
                loadUsers(currentPage);
            } else {
                showError(response.error);
            }
        },
        error: function(xhr) {
            const response = xhr.responseJSON;
            showError(response ? response.error : 'Erro ao criar usuário');
        }
    });
}

function editUser(userId) {
    console.log('✏️ Editando usuário:', userId);
    
    // Encontrar o usuário na tabela atual
    const row = $(`tr[data-user-id="${userId}"]`);
    if (row.length === 0) {
        showError('Usuário não encontrado');
        return;
    }
    
    // Buscar dados completos do usuário
    $.ajax({
        url: `/admin/api/users?user_id=${userId}`,
        method: 'GET',
        success: function(response) {
            if (response.success && response.users.length > 0) {
                const user = response.users[0];
                populateEditForm(user);
                openModal('editUserModal');
            } else {
                showError('Erro ao carregar dados do usuário');
            }
        },
        error: function() {
            showError('Erro ao carregar dados do usuário');
        }
    });
}

function populateEditForm(user) {
    $('#editUserId').val(user.id);
    $('#editNomeCompleto').val(user.nome_completo || '');
    $('#editUsername').val(user.username);
    $('#editEmail').val(user.email);
    $('#editTipoUsuario').val(user.tipo_usuario);
    $('#editAtivo').val(user.ativo.toString());
}

function updateUser() {
    const form = $('#editUserForm');
    const formData = getFormData(form);
    const userId = formData.user_id;
    
    // Validação
    if (!form[0].checkValidity()) {
        form[0].reportValidity();
        return;
    }
    
    // Converter boolean
    formData.ativo = formData.ativo === 'true';
    delete formData.user_id; // Remover ID dos dados
    
    console.log('💾 Atualizando usuário:', userId, formData);
    
    $.ajax({
        url: `/admin/api/users/${userId}`,
        method: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify(formData),
        success: function(response) {
            if (response.success) {
                showSuccess(response.message);
                closeModal('editUserModal');
                loadUsers(currentPage);
            } else {
                showError(response.error);
            }
        },
        error: function(xhr) {
            const response = xhr.responseJSON;
            showError(response ? response.error : 'Erro ao atualizar usuário');
        }
    });
}

function resetPassword(userId, username) {
    selectedUserId = userId;
    selectedUsername = username;
    
    $('#resetUsername').text(username);
    openModal('resetPasswordModal');
}

function confirmResetPassword() {
    if (!selectedUserId) {
        showError('Usuário não selecionado');
        return;
    }
    
    console.log('🔑 Resetando senha do usuário:', selectedUserId);
    
    $.ajax({
        url: `/admin/api/users/${selectedUserId}/reset-password`,
        method: 'POST',
        success: function(response) {
            if (response.success) {
                showSuccess(response.message);
                closeModal('resetPasswordModal');
                
                // Mostrar senha temporária
                showGeneratedPassword(response.temp_password);
            } else {
                showError(response.error);
            }
        },
        error: function(xhr) {
            const response = xhr.responseJSON;
            showError(response ? response.error : 'Erro ao resetar senha');
        }
    });
}

function toggleUserStatus(userId, newStatus) {
    const statusText = newStatus ? 'ativar' : 'desativar';
    
    if (!confirm(`Deseja ${statusText} este usuário?`)) {
        return;
    }
    
    console.log(`🔄 ${statusText} usuário:`, userId);
    
    $.ajax({
        url: `/admin/api/users/${userId}/toggle-status`,
        method: 'POST',
        success: function(response) {
            if (response.success) {
                showSuccess(response.message);
                loadUsers(currentPage);
            } else {
                showError(response.error);
            }
        },
        error: function(xhr) {
            const response = xhr.responseJSON;
            showError(response ? response.error : 'Erro ao alterar status');
        }
    });
}

function deleteUser(userId, username) {
    if (!confirm(`Tem certeza que deseja excluir o usuário "${username}"?\n\nEsta ação não pode ser desfeita.`)) {
        return;
    }
    
    console.log('🗑️ Excluindo usuário:', userId);
    
    $.ajax({
        url: `/admin/api/users/${userId}`,
        method: 'DELETE',
        success: function(response) {
            if (response.success) {
                showSuccess(response.message);
                loadUsers(currentPage);
            } else {
                showError(response.error);
            }
        },
        error: function(xhr) {
            const response = xhr.responseJSON;
            showError(response ? response.error : 'Erro ao excluir usuário');
        }
    });
}

// ============================================================================
// FUNÇÕES DE MODAL
// ============================================================================

function openAddUserModal() {
    openModal('addUserModal');
    
    // Focar no primeiro campo
    setTimeout(() => {
        $('#addUserForm input[name="nome_completo"]').focus();
    }, 300);
}

function openModal(modalId) {
    $(`#${modalId}`).addClass('show');
    $('body').addClass('modal-open');
}

function closeModal(modalId) {
    $(`#${modalId}`).removeClass('show');
    $('body').removeClass('modal-open');
    
    // Limpar formulários
    $(`#${modalId} form`)[0]?.reset();
}

// ============================================================================
// FUNÇÕES DE GERAÇÃO DE SENHA
// ============================================================================

function generatePassword() {
    $.ajax({
        url: '/admin/api/generate-password',
        method: 'GET',
        success: function(response) {
            if (response.success) {
                $('#passwordInput').val(response.password);
                showSuccess('Senha gerada com sucesso!');
            } else {
                showError('Erro ao gerar senha');
            }
        },
        error: function() {
            showError('Erro ao gerar senha');
        }
    });
}

function showGeneratedPassword(password) {
    $('#generatedPassword').text(password);
    openModal('showPasswordModal');
}

function copyPassword() {
    const password = $('#generatedPassword').text();
    
    // Usar a API moderna de clipboard se disponível
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(password).then(() => {
            showSuccess('Senha copiada para a área de transferência!');
        }).catch(() => {
            fallbackCopyPassword(password);
        });
    } else {
        fallbackCopyPassword(password);
    }
}

function fallbackCopyPassword(password) {
    // Fallback para navegadores mais antigos
    const textArea = document.createElement('textarea');
    textArea.value = password;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showSuccess('Senha copiada para a área de transferência!');
    } catch (err) {
        showError('Erro ao copiar senha. Copie manualmente.');
    } finally {
        document.body.removeChild(textArea);
    }
}

// ============================================================================
// FUNÇÕES UTILITÁRIAS
// ============================================================================

function getFormData(form) {
    const formData = {};
    form.find('input, select, textarea').each(function() {
        const field = $(this);
        const name = field.attr('name');
        const value = field.val();
        
        if (name && value !== undefined) {
            formData[name] = value;
        }
    });
    return formData;
}

function showSuccess(message) {
    console.log('✅', message);
    
    // Criar toast de sucesso
    const toast = $(`
        <div class="toast align-items-center text-white bg-success border-0" role="alert" 
             style="position: fixed; top: 20px; right: 20px; z-index: 9999;">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-check-circle"></i> ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                        onclick="$(this).closest('.toast').fadeOut()"></button>
            </div>
        </div>
    `);
    
    $('body').append(toast);
    
    // Auto-remove após 5 segundos
    setTimeout(() => {
        toast.fadeOut(() => toast.remove());
    }, 5000);
}

function showError(message) {
    console.error('❌', message);
    
    // Criar toast de erro
    const toast = $(`
        <div class="toast align-items-center text-white bg-danger border-0" role="alert"
             style="position: fixed; top: 20px; right: 20px; z-index: 9999;">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-exclamation-triangle"></i> ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                        onclick="$(this).closest('.toast').fadeOut()"></button>
            </div>
        </div>
    `);
    
    $('body').append(toast);
    
    // Auto-remove após 7 segundos
    setTimeout(() => {
        toast.fadeOut(() => toast.remove());
    }, 7000);
}

function showInfo(message) {
    console.log('ℹ️', message);
    
    const toast = $(`
        <div class="toast align-items-center text-white bg-info border-0" role="alert"
             style="position: fixed; top: 20px; right: 20px; z-index: 9999;">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-info-circle"></i> ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                        onclick="$(this).closest('.toast').fadeOut()"></button>
            </div>
        </div>
    `);
    
    $('body').append(toast);
    
    setTimeout(() => {
        toast.fadeOut(() => toast.remove());
    }, 5000);
}

// ============================================================================
// FUNÇÕES DE DEBUG E DESENVOLVIMENTO
// ============================================================================

function debugUserSystem() {
    console.log('🐛 Debug do Sistema de Usuários');
    console.log('Página atual:', currentPage);
    console.log('Filtros atuais:', currentFilters);
    console.log('Usuário selecionado:', selectedUserId);
    
    // Testar conexão com API
    $.ajax({
        url: '/admin/api/system-stats',
        method: 'GET',
        success: function(response) {
            console.log('✅ API funcionando:', response);
        },
        error: function(xhr) {
            console.error('❌ Erro na API:', xhr);
        }
    });
}

// Expor função de debug globalmente para desenvolvimento
window.debugUserSystem = debugUserSystem;