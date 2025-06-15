// Custom Admin JavaScript inspired by Volt Pro

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Add fade-in animation to cards
    document.querySelectorAll('.card').forEach(function(card) {
        card.classList.add('fade-in');
    });

    // Sidebar toggle functionality
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.body.classList.toggle('sidebar-collapsed');
            localStorage.setItem('sidebarCollapsed', document.body.classList.contains('sidebar-collapsed'));
        });
    }

    // Check for saved sidebar state
    if (localStorage.getItem('sidebarCollapsed') === 'true') {
        document.body.classList.add('sidebar-collapsed');
    }

    // Add hover effect to table rows
    document.querySelectorAll('table tbody tr').forEach(function(row) {
        row.addEventListener('mouseenter', function() {
            this.classList.add('hover-shadow');
        });
        row.addEventListener('mouseleave', function() {
            this.classList.remove('hover-shadow');
        });
    });

    // Form validation enhancement
    document.querySelectorAll('form').forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Add loading state to buttons
    document.querySelectorAll('button[type="submit"]').forEach(function(button) {
        button.addEventListener('click', function() {
            if (this.form && this.form.checkValidity()) {
                this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
                this.disabled = true;
            }
        });
    });

    // Smooth scroll to top
    const scrollToTop = document.createElement('button');
    scrollToTop.innerHTML = '<i class="fas fa-arrow-up"></i>';
    scrollToTop.className = 'btn btn-primary scroll-to-top';
    scrollToTop.style.cssText = 'position: fixed; bottom: 20px; right: 20px; display: none; z-index: 1000;';
    document.body.appendChild(scrollToTop);

    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 100) {
            scrollToTop.style.display = 'block';
        } else {
            scrollToTop.style.display = 'none';
        }
    });

    scrollToTop.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });

    // Add active state to current nav item
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(function(link) {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Add responsive table wrapper
    document.querySelectorAll('table').forEach(function(table) {
        const wrapper = document.createElement('div');
        wrapper.className = 'table-responsive';
        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
    });

    // Add confirmation to delete buttons
    document.querySelectorAll('a[href*="delete"]').forEach(function(link) {
        link.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });

    // Add focus effect to form inputs
    document.querySelectorAll('.form-control').forEach(function(input) {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focus-primary');
        });
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focus-primary');
        });
    });

    // Add notification system
    function showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} notification fade-in`;
        notification.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 1050; min-width: 300px;';
        notification.innerHTML = message;
        document.body.appendChild(notification);

        setTimeout(function() {
            notification.remove();
        }, 5000);
    }

    // Expose notification function globally
    window.showNotification = showNotification;
}); 