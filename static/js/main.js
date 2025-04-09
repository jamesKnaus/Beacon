document.addEventListener('DOMContentLoaded', () => {
    // Get the start chat button
    const startChatBtn = document.getElementById('start-chat-btn');
    
    // Add click event listener
    if (startChatBtn) {
        startChatBtn.addEventListener('click', () => {
            // Redirect to chat page
            window.location.href = '/chat';
        });
    }
    
    // Add smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('nav a');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Get the target section id from the href attribute
            const targetId = this.getAttribute('href');
            
            // If it's an anchor link (starts with #) and not just #
            if (targetId.startsWith('#') && targetId.length > 1) {
                e.preventDefault();
                
                // Get the target element
                const targetElement = document.querySelector(targetId);
                
                // Scroll to target element smoothly
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
    
    // Optional: Add some animation for the hero section
    const heroSection = document.querySelector('.hero');
    if (heroSection) {
        // Add a class after a small delay to trigger animation
        setTimeout(() => {
            heroSection.classList.add('active');
        }, 300);
    }
});
