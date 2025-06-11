// Comments data storage
let commentsData = {};

// Initialize comments system
document.addEventListener('DOMContentLoaded', function() {
    const phases = document.querySelectorAll('.phase-container');

    // Load comments from localStorage
    loadCommentsFromStorage();

    // Initialize each card
    phases.forEach(phase => {
        const cardId = phase.getAttribute('data-card-id');
        if (cardId) {
            initializeCard(phase, cardId);
            updateCommentIndicator(phase, cardId);
        }

        // Hover effects
        phase.addEventListener('mouseenter', function() {
            if (!this.classList.contains('card-flipped')) {
                this.style.zIndex = '10';
            }
        });

        phase.addEventListener('mouseleave', function() {
            if (!this.classList.contains('card-flipped')) {
                this.style.zIndex = '1';
            }
        });
    });

    // Responsive timeline adjustment
    function adjustTimeline() {
        const timeline = document.querySelector('.timeline-track');
        if (timeline) {
            if (window.innerWidth <= 768) {
                timeline.style.flexDirection = 'column';
            } else {
                timeline.style.flexDirection = 'row';
            }
        }
    }

    window.addEventListener('resize', adjustTimeline);
    adjustTimeline();
});

function initializeCard(cardElement, cardId) {
    // Card flip functionality
    cardElement.addEventListener('click', function(e) {
        // Don't flip if clicking on buttons or form elements
        if (e.target.tagName === 'BUTTON' || e.target.tagName === 'TEXTAREA') {
            return;
        }

        if (!this.classList.contains('card-flipped')) {
            flipCard(this);
        }
    });

    // Close comments button
    const closeBtn = cardElement.querySelector('.close-comments');
    if (closeBtn) {
        closeBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            unflipCard(cardElement);
        });
    }

    // Comment submission
    const submitBtn = cardElement.querySelector('.comment-submit');
    const textarea = cardElement.querySelector('.comment-input');

    if (submitBtn && textarea) {
        submitBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            addComment(cardId, textarea.value.trim());
            textarea.value = '';
        });

        // Submit on Ctrl+Enter
        textarea.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                addComment(cardId, this.value.trim());
                this.value = '';
            }
        });
    }

    // Render existing comments
    renderComments(cardId);
}

function flipCard(cardElement) {
    cardElement.classList.add('card-flipped');
    cardElement.style.zIndex = '100';
    cardElement.style.transform = 'scale(1.05)';

    // Focus on textarea after flip animation
    setTimeout(() => {
        const textarea = cardElement.querySelector('.comment-input');
        if (textarea) {
            textarea.focus();
        }
    }, 300);
}

function unflipCard(cardElement) {
    cardElement.classList.remove('card-flipped');
    cardElement.style.zIndex = '1';
    cardElement.style.transform = '';
}

function addComment(cardId, commentText) {
    if (!commentText) {
        alert('Por favor, digite um comentário antes de enviar.');
        return;
    }

    if (!commentsData[cardId]) {
        commentsData[cardId] = [];
    }

    const comment = {
        id: Date.now(),
        text: commentText,
        timestamp: new Date(),
        author: 'Usuário' // Could be enhanced with user authentication
    };

    commentsData[cardId].push(comment);
    saveCommentsToStorage();
    renderComments(cardId);
    updateCommentIndicator(document.querySelector(`[data-card-id="${cardId}"]`), cardId);
}

function renderComments(cardId) {
    const commentsList = document.getElementById(`comments-${cardId}`);
    if (!commentsList) return;

    const comments = commentsData[cardId] || [];

    if (comments.length === 0) {
        commentsList.innerHTML = '<div class="no-comments">Nenhum comentário ainda. Seja o primeiro!</div>';
        return;
    }

    commentsList.innerHTML = comments.map(comment => `
        <div class="comment-item">
            <div class="comment-meta">
                ${comment.author} • ${formatDate(comment.timestamp)}
            </div>
            <div class="comment-text">${escapeHtml(comment.text)}</div>
        </div>
    `).join('');

    // Scroll to bottom
    commentsList.scrollTop = commentsList.scrollHeight;
}

function updateCommentIndicator(cardElement, cardId) {
    if (!cardElement) return;

    const indicator = cardElement.querySelector('.comment-indicator');
    const count = commentsData[cardId] ? commentsData[cardId].length : 0;

    if (indicator) {
        indicator.textContent = count;
        if (count > 0) {
            cardElement.classList.add('has-comments');
        } else {
            cardElement.classList.remove('has-comments');
        }
    }
}

function formatDate(date) {
    const now = new Date();
    const diff = now - new Date(date);
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'agora';
    if (minutes < 60) return `${minutes}m atrás`;
    if (hours < 24) return `${hours}h atrás`;
    return `${days}d atrás`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function saveCommentsToStorage() {
    try {
        localStorage.setItem('aim-framework-comments', JSON.stringify(commentsData));
    } catch (e) {
        console.warn('Failed to save comments to localStorage:', e);
    }
}

function loadCommentsFromStorage() {
    try {
        const stored = localStorage.getItem('aim-framework-comments');
        if (stored) {
            commentsData = JSON.parse(stored);
        }
    } catch (e) {
        console.warn('Failed to load comments from localStorage:', e);
        commentsData = {};
    }
}
