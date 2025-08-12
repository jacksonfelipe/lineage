// Cart Modal Management
document.addEventListener('DOMContentLoaded', function() {
    
    // Modal elements
    const modal = document.getElementById('packageModal');
    const modalBackdrop = document.querySelector('.modal-backdrop');
    const closeButtons = document.querySelectorAll('[data-bs-dismiss="modal"], .btn-close');
    const viewItemsButtons = document.querySelectorAll('.btn-view-items');
    
    // Open modal function
    function openModal() {
        if (modal) {
            modal.classList.add('show');
            modal.style.display = 'block';
            document.body.classList.add('modal-open');
            
            // Remove any backdrop that might interfere
            if (modalBackdrop) {
                modalBackdrop.style.display = 'none';
            }
            
            // Focus on modal for accessibility
            setTimeout(() => {
                const closeBtn = modal.querySelector('.btn-close');
                if (closeBtn) {
                    closeBtn.focus();
                }
            }, 100);
        }
    }
    
    // Close modal function
    function closeModal() {
        if (modal) {
            modal.classList.remove('show');
            modal.style.display = 'none';
            document.body.classList.remove('modal-open');
            
            // Reset modal state
            modal.classList.remove('fade');
            modal.classList.remove('show');
            
            // Remove any backdrop
            if (modalBackdrop) {
                modalBackdrop.style.display = 'none';
            }
        }
    }
    
    // Event listeners for opening modal
    viewItemsButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            openModal();
        });
    });
    
    // Event listeners for closing modal
    closeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            closeModal();
        });
    });
    
    // Close modal when clicking outside
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeModal();
            }
        });
    }
    
    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal && modal.classList.contains('show')) {
            closeModal();
        }
    });
    
    // Prevent modal from being removed from DOM
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                mutation.removedNodes.forEach(function(node) {
                    if (node === modal) {
                        // Modal was removed, add it back
                        document.body.appendChild(modal);
                    }
                });
            }
        });
    });
    
    if (modal) {
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    // Bootstrap compatibility
    if (typeof bootstrap !== 'undefined') {
        // Override Bootstrap modal methods
        const Modal = bootstrap.Modal;
        if (Modal) {
            const originalHide = Modal.prototype.hide;
            Modal.prototype.hide = function() {
                // Call original hide method
                originalHide.call(this);
                
                // Ensure modal can be reopened
                setTimeout(() => {
                    const modalElement = this._element;
                    if (modalElement) {
                        modalElement.classList.remove('show');
                        modalElement.style.display = 'none';
                        document.body.classList.remove('modal-open');
                    }
                }, 150);
            };
        }
    }
});
