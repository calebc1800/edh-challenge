// Enhanced Deck builder functionality with print selection and quantity

let currentDeck = null;
let deckId = null;
let selectedCardForOptions = null;

// Get deck ID from URL
function getDeckId() {
    const path = window.location.pathname;
    const match = path.match(/\/deck-builder\/(\d+)/);
    return match ? parseInt(match[1]) : null;
}

async function loadDeck() {
    deckId = getDeckId();
    if (!deckId) {
        showNotification('Invalid deck ID', 'error');
        return;
    }

    try {
        currentDeck = await API.get(`/decks/${deckId}`);
        displayDeck();
    } catch (error) {
        console.error('Failed to load deck:', error);
        showNotification('Failed to load deck', 'error');
    }
}

function displayDeck() {
    if (!currentDeck) return;

    // Update deck name
    document.getElementById('deck-name').textContent = currentDeck.name;

    // Calculate total card count
    const totalCards = currentDeck.cards ? 
        currentDeck.cards.reduce((sum, dc) => sum + dc.quantity, 0) : 0;
    document.getElementById('card-count').textContent = totalCards;

    // Display validation status
    const validationDiv = document.getElementById('validation-status');
    if (currentDeck.validation) {
        validationDiv.className = 'validation-status ' + 
            (currentDeck.validation.valid ? 'valid' : 'invalid');
        validationDiv.textContent = currentDeck.validation.valid ? '✓ Valid Deck' : '✗ Invalid Deck';

        if (currentDeck.validation.errors.length > 0) {
            validationDiv.title = currentDeck.validation.errors.join('\n');
        }
    }

    // Display commander
    const commanderSlot = document.getElementById('commander-slot');
    const commander = currentDeck.cards ? currentDeck.cards.find(c => c.is_commander) : null;

    if (commander && commander.card) {
        const imageUrl = commander.selected_image_url || commander.card.image_url;
        commanderSlot.innerHTML = `
            <div class="commander-card">
                <img src="${imageUrl}" 
                     alt="${commander.card.name}"
                     onclick="showCardModal('${commander.card_id}')"
                     title="Click to view card details">
                <div>
                    <strong>${commander.card.name}</strong><br>
                    <small>${commander.card.type_line}</small><br>
                    ${commander.selected_set_code ? 
                        `<small class="deck-card-set">${commander.selected_set_code.toUpperCase()} #${commander.selected_collector_number}</small>` 
                        : ''}
                </div>
                <div style="margin-left: auto;">
                    <button class="btn-edit" onclick="showCardOptions('${commander.card_id}')">Options</button>
                    <button class="btn-remove" onclick="removeCardFromDeck('${commander.card_id}')">Remove</button>
                </div>
            </div>
        `;
    } else {
        commanderSlot.innerHTML = '<p>No commander selected (search for a legendary creature)</p>';
    }

    // Display deck list
    const deckList = document.getElementById('deck-list');
    deckList.innerHTML = '';

    if (currentDeck.cards) {
        const nonCommanderCards = currentDeck.cards
            .filter(dc => !dc.is_commander)
            .sort((a, b) => a.card.name.localeCompare(b.card.name));

        nonCommanderCards.forEach(dc => {
            const cardEl = createDeckCardElement(dc);
            deckList.appendChild(cardEl);
        });
    }
}

function createDeckCardElement(deckCard) {
    const div = document.createElement('div');
    div.className = 'deck-card-item';

    const imageUrl = deckCard.selected_image_url || deckCard.card.image_url;
    const imageUrlSmall = deckCard.card.image_url_small || imageUrl;

    div.innerHTML = `
        <img src="${imageUrlSmall}" 
             alt="${deckCard.card.name}" 
             class="card-image-thumb"
             onclick="showCardModal('${deckCard.card_id}')">

        <div class="deck-card-details" onclick="showCardOptions('${deckCard.card_id}')">
            <div>
                <span class="deck-card-quantity">${deckCard.quantity}x</span>
                <span class="deck-card-name">${deckCard.card.name}</span>
            </div>
            <div class="deck-card-type">${deckCard.card.type_line}</div>
            ${deckCard.selected_set_code ? 
                `<div class="deck-card-set">${deckCard.selected_set_code.toUpperCase()} #${deckCard.selected_collector_number}</div>` 
                : ''}
        </div>

        <div class="card-hover-preview">
            <img src="${imageUrl}" alt="${deckCard.card.name}">
        </div>

        <div class="deck-card-actions">
            <button class="btn-edit" onclick="event.stopPropagation(); showCardOptions('${deckCard.card_id}')">
                ⚙️
            </button>
            <button class="btn-remove" onclick="event.stopPropagation(); removeCardFromDeck('${deckCard.card_id}')">
                ✕
            </button>
        </div>
    `;

    return div;
}

async function addCardToDeck(card, options = {}) {
    if (!deckId) return;

    try {
        await API.post(`/decks/${deckId}/cards`, {
            card_id: card.id,
            quantity: options.quantity || 1,
            is_commander: options.is_commander || false,
            selected_printing_id: options.selected_printing_id || card.id,
            selected_image_url: options.selected_image_url || card.image_url,
            selected_set_code: options.selected_set_code || card.set_code,
            selected_collector_number: options.selected_collector_number || card.collector_number
        });

        showNotification(`Added ${card.name} to deck`, 'success');
        await loadDeck();
    } catch (error) {
        console.error('Failed to add card:', error);
        showNotification('Failed to add card. It may already be in the deck.', 'error');
    }
}

async function removeCardFromDeck(cardId) {
    if (!deckId) return;

    const deckCard = currentDeck.cards.find(dc => dc.card_id === cardId);
    if (!deckCard) return;

    if (!confirm(`Remove ${deckCard.card.name} from deck?`)) {
        return;
    }

    try {
        await API.delete(`/decks/${deckId}/cards/${cardId}`);
        showNotification('Card removed', 'success');
        await loadDeck();
    } catch (error) {
        console.error('Failed to remove card:', error);
        showNotification('Failed to remove card', 'error');
    }
}

async function updateDeckCard(cardId, updates) {
    if (!deckId) return;

    try {
        await API.put(`/decks/${deckId}/cards/${cardId}`, updates);
        showNotification('Card updated', 'success');
        await loadDeck();
    } catch (error) {
        console.error('Failed to update card:', error);
        showNotification('Failed to update card', 'error');
    }
}

// Initialize deck builder
if (window.location.pathname.includes('/deck-builder/')) {
    document.addEventListener('DOMContentLoaded', loadDeck);
}

// Make functions globally available
window.addCardToDeck = addCardToDeck;
window.removeCardFromDeck = removeCardFromDeck;
window.updateDeckCard = updateDeckCard;
window.loadDeck = loadDeck;
