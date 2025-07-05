// ===== FUNCIONALIDADES INTERATIVAS PARA TABELAS TOPS =====

document.addEventListener('DOMContentLoaded', function() {
    
    // Inicializar funcionalidades das tabelas
    initTopsTables();
    
    // Adicionar efeitos de hover personalizados
    initHoverEffects();
    
    // Adicionar animações de entrada
    initEntryAnimations();
    
    // Adicionar funcionalidade de busca (se necessário)
    initSearchFunctionality();
    
    // Adicionar funcionalidade de ordenação
    initSortingFunctionality();
});

function initTopsTables() {
    const tables = document.querySelectorAll('.table-dark');
    
    tables.forEach(table => {
        // Adicionar classes para melhor estilização
        table.classList.add('tops-table-enhanced');
        
        // Adicionar efeito de loading se não houver dados
        const tbody = table.querySelector('tbody');
        if (tbody && tbody.children.length === 0) {
            table.parentElement.classList.add('table-loading');
        }
        
        // Adicionar tooltips para badges
        const badges = table.querySelectorAll('.badge');
        badges.forEach(badge => {
            if (badge.textContent.trim()) {
                badge.title = badge.textContent.trim();
            }
        });
    });
}

function initHoverEffects() {
    const tableRows = document.querySelectorAll('.table-dark tbody tr');
    
    tableRows.forEach((row, index) => {
        // Adicionar delay de animação baseado na posição
        row.style.animationDelay = `${index * 0.1}s`;
        
        // Adicionar efeito de destaque ao hover
        row.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.01)';
            this.style.zIndex = '10';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.zIndex = '1';
        });
        
        // Adicionar efeito de clique
        row.addEventListener('click', function() {
            // Remover destaque de outras linhas
            tableRows.forEach(r => r.classList.remove('selected-row'));
            // Adicionar destaque à linha clicada
            this.classList.add('selected-row');
        });
    });
}

function initEntryAnimations() {
    // Animar elementos quando entram na viewport
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // Observar tabelas e elementos importantes
    const elementsToAnimate = document.querySelectorAll('.table-responsive, .tops-header-section, .tops-category-card');
    elementsToAnimate.forEach(el => observer.observe(el));
}

function initSearchFunctionality() {
    // Adicionar campo de busca se não existir
    const contentSections = document.querySelectorAll('.tops-content-section');
    
    contentSections.forEach(section => {
        const table = section.querySelector('.table-responsive');
        if (table && !section.querySelector('.tops-search')) {
            addSearchField(section, table);
        }
    });
}

function addSearchField(container, table) {
    const searchHTML = `
        <div class="tops-search mb-4" data-aos="fade-down" data-aos-duration="800">
            <div class="input-group">
                <span class="input-group-text">
                    <i class="fas fa-search"></i>
                </span>
                <input type="text" class="form-control" 
                       placeholder="Buscar jogador..." 
                       id="search-${Date.now()}"
                       autocomplete="off">
                <button class="btn btn-outline-warning" type="button" id="clear-search-${Date.now()}">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="search-info mt-2">
                <small class="text-muted">
                    <i class="fas fa-info-circle"></i>
                    Digite o nome do jogador para filtrar os resultados
                </small>
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('afterbegin', searchHTML);
    
    const searchInput = container.querySelector('input[type="text"]');
    const clearButton = container.querySelector('button[type="button"]');
    const tbody = table.querySelector('tbody');
    const searchInfo = container.querySelector('.search-info');
    
    if (searchInput && tbody) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            
            searchTimeout = setTimeout(() => {
                const searchTerm = this.value.toLowerCase().trim();
                const rows = tbody.querySelectorAll('tr');
                let visibleCount = 0;
                
                rows.forEach((row, index) => {
                    const playerName = row.querySelector('td:nth-child(2)')?.textContent.toLowerCase() || '';
                    const clanName = row.querySelector('td:nth-child(3)')?.textContent.toLowerCase() || '';
                    const className = row.querySelector('td:nth-child(6)')?.textContent.toLowerCase() || '';
                    
                    const matches = playerName.includes(searchTerm) || 
                                  clanName.includes(searchTerm) || 
                                  className.includes(searchTerm);
                    
                    if (matches || searchTerm === '') {
                        row.style.display = '';
                        row.style.animation = 'fadeInUp 0.3s ease';
                        row.style.animationDelay = `${index * 0.05}s`;
                        visibleCount++;
                    } else {
                        row.style.display = 'none';
                    }
                });
                
                // Atualizar informações de busca
                updateSearchInfo(searchInfo, visibleCount, rows.length, searchTerm);
                
                // Mostrar/esconder botão de limpar
                if (searchTerm) {
                    clearButton.style.display = 'block';
                } else {
                    clearButton.style.display = 'none';
                }
            }, 300); // Delay para melhor performance
        });
        
        // Funcionalidade do botão limpar
        clearButton.addEventListener('click', function() {
            searchInput.value = '';
            searchInput.dispatchEvent(new Event('input'));
            searchInput.focus();
        });
        
        // Foco automático no campo de busca
        searchInput.focus();
        
        // Atalho de teclado para limpar (Ctrl+L)
        document.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'l' && document.activeElement === searchInput) {
                e.preventDefault();
                searchInput.value = '';
                searchInput.dispatchEvent(new Event('input'));
            }
        });
    }
}

function updateSearchInfo(searchInfo, visibleCount, totalCount, searchTerm) {
    if (searchTerm) {
        searchInfo.innerHTML = `
            <small style="color: #e6c77d;">
                <i class="fas fa-search" style="color: #d1a44f;"></i>
                ${visibleCount} de ${totalCount} resultados encontrados para "${searchTerm}"
            </small>
        `;
    } else {
        searchInfo.innerHTML = `
            <small style="color: rgba(230, 199, 125, 0.7);">
                <i class="fas fa-info-circle" style="color: #e6c77d;"></i>
                Digite o nome do jogador para filtrar os resultados
            </small>
        `;
    }
}

function initSortingFunctionality() {
    const tableHeaders = document.querySelectorAll('.table-dark thead th');
    
    tableHeaders.forEach((header, index) => {
        // Pular a primeira coluna (ranking)
        if (index === 0) return;
        
        header.style.cursor = 'pointer';
        header.addEventListener('click', function() {
            sortTable(this, index);
        });
        
        // Adicionar ícone de ordenação
        const sortIcon = document.createElement('i');
        sortIcon.className = 'fas fa-sort ms-2 text-muted';
        sortIcon.style.fontSize = '12px';
        header.appendChild(sortIcon);
    });
}

function sortTable(header, columnIndex) {
    const table = header.closest('table');
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const sortIcon = header.querySelector('i');
    
    // Alternar direção de ordenação
    const isAscending = !header.classList.contains('sort-desc');
    
    // Atualizar ícone
    sortIcon.className = isAscending ? 'fas fa-sort-up ms-2 text-warning' : 'fas fa-sort-down ms-2 text-warning';
    
    // Remover classes de ordenação de outros cabeçalhos
    table.querySelectorAll('th').forEach(th => {
        th.classList.remove('sort-asc', 'sort-desc');
        th.querySelector('i').className = 'fas fa-sort ms-2 text-muted';
    });
    
    // Adicionar classe de ordenação
    header.classList.add(isAscending ? 'sort-asc' : 'sort-desc');
    
    // Ordenar linhas
    rows.sort((a, b) => {
        const aValue = getCellValue(a, columnIndex);
        const bValue = getCellValue(b, columnIndex);
        
        if (isAscending) {
            return aValue > bValue ? 1 : -1;
        } else {
            return aValue < bValue ? 1 : -1;
        }
    });
    
    // Reordenar linhas na tabela
    rows.forEach((row, index) => {
        tbody.appendChild(row);
        row.style.animation = 'fadeInUp 0.3s ease';
        row.style.animationDelay = `${index * 0.05}s`;
    });
}

function getCellValue(row, columnIndex) {
    const cell = row.cells[columnIndex];
    if (!cell) return '';
    
    // Extrair valor numérico se possível
    const text = cell.textContent.trim();
    const number = parseFloat(text.replace(/[^\d.-]/g, ''));
    
    return isNaN(number) ? text.toLowerCase() : number;
}

// Função para atualizar dados em tempo real (se necessário)
function updateLiveData() {
    const liveElements = document.querySelectorAll('[data-live="true"]');
    
    liveElements.forEach(element => {
        // Adicionar efeito de atualização
        element.style.animation = 'pulse 0.5s ease';
        setTimeout(() => {
            element.style.animation = '';
        }, 500);
    });
}

// Função para exportar dados da tabela
function exportTableData(tableId, format = 'csv') {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    let data = [];
    
    // Obter cabeçalhos
    const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent.trim());
    data.push(headers);
    
    // Obter dados das linhas
    rows.forEach(row => {
        const rowData = Array.from(row.querySelectorAll('td')).map(td => td.textContent.trim());
        data.push(rowData);
    });
    
    if (format === 'csv') {
        const csvContent = data.map(row => row.join(',')).join('\n');
        downloadFile(csvContent, 'tops-data.csv', 'text/csv');
    }
}

function downloadFile(content, filename, contentType) {
    const blob = new Blob([content], { type: contentType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
}

// Adicionar estilos CSS dinâmicos
const dynamicStyles = `
    .selected-row {
        background: linear-gradient(135deg, rgba(230, 199, 125, 0.2), rgba(155, 117, 48, 0.2)) !important;
        border-left: 4px solid #e6c77d !important;
    }
    
    .tops-search .form-control:focus {
        box-shadow: 0 0 0 0.2rem rgba(230, 199, 125, 0.25);
        border-color: #e6c77d;
    }
    
    .animate-in {
        animation: fadeInUp 0.6s ease forwards;
    }
    
    .tops-table-enhanced {
        position: relative;
    }
`;

const styleSheet = document.createElement('style');
styleSheet.textContent = dynamicStyles;
document.head.appendChild(styleSheet); 