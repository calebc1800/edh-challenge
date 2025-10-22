// Enhanced card search functionality with print selection

let searchTimeout;

function initCardSearch() {
    const searchInput = document.getElementById('card-search');
    if (!searchInput) return;

    searchInput.addEventListener('input', debounce(performSearch, 500));
}

async function performSearch() {
    const searchInput = document.getElementById('card-search');
    const query = searchInput.value.trim();

    if (query.length < 2) {
        document.getElementById('search-results').innerHTML = 
            '<p style="padding: 1rem; color: #666;">Enter at least 2 characters to search</p>';
        return;
    }

    // Show loading state
    document.getElementById('search-results').innerHTML = 
        '<p style="padding: 1rem; color: #666;">Searching...</p>';

    try {
        const data = await API.get(`/cards/search?q=${encodeURIComponent(query)}`);
        displaySearchResults(data.cards);
    } catch (error) {
        document.getElementById('search-results').innerHTML = 
            '<p style="padding: 1rem; color: #d3202a;">Error searching cards. Please try again.</p>';
        console.error('Search error:', error);
    }
}

function displaySearchResults(cards) {
    const resultsDiv = document.getElementById('search-results');

    if (!cards || cards.length === 0) {
        resultsDiv.innerHTML = '<p style="padding: 1rem; color: #666;">No cards found</p>';
        return;
    }

    resultsDiv.innerHTML = '';

    cards.forEach(card => {
        const cardEl = document.createElement('div');
        cardEl.className = 'card-result';

        const imageUrl = card.image_url_small || card.image_url;

        cardEl.innerHTML = `
            ${imageUrl ? 
                `<img src="${imageUrl}" 
                      alt="${card.name}"
                      onerror="this.style.display='none'">` 
                : '<div style="width: 50px; height: 70px; background: #ddd; border-radius: 5px; margin-right: 1rem;"></div>'}
            <div class="card-info">
                <div class="card-name">${card.name} ${card.mana_cost || ''}</div>
                <div class="card-type">${card.type_line}</div>
                ${card.is_banned ? '<div style="color: red; font-size: 0.85rem;">⚠ BANNED</div>' : ''}
                ${card.is_legal_commander ? '<div style="color: green; font-size: 0.85rem;">★ Legal Commander</div>' : ''}
            </div>
        `;

        cardEl.onclick = () => addCardWithOptions(card);
        cardEl.style.cursor = 'pointer';

        resultsDiv.appendChild(cardEl);
    });
}

// Initialize on page load
if (document.getElementById('card-search')) {
    document.addEventListener('DOMContentLoaded', initCardSearch);
}
