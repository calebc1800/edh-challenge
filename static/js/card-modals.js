// Modal functionality for card details, print selection, and options

// ============================================================================
// Card Details Modal
// ============================================================================

async function showCardModal(cardId) {
    const modal = document.getElementById('card-modal');
    const modalBody = document.getElementById('modal-body');

    try {
        const card = await API.get(`/cards/${cardId}`);

        modalBody.innerHTML = `
            <div class="card-detail">
                <div style="display: flex; gap: 2rem;">
                    <div>
                        <img src="${card.image_url || ''}" 
                             alt="${card.name}" 
                             style="width: 300px; border-radius: 10px;">
                    </div>
                    <div style="flex: 1;">
                        <h2>${card.name} ${card.mana_cost || ''}</h2>
                        <p><strong>Type:</strong> ${card.type_line}</p>
                        ${card.oracle_text ? `<p><strong>Text:</strong><br>${card.oracle_text.replace(/\n/g, '<br>')}</p>` : ''}
                        ${card.power ? `<p><strong>P/T:</strong> ${card.power}/${card.toughness}</p>` : ''}
                        ${card.loyalty ? `<p><strong>Loyalty:</strong> ${card.loyalty}</p>` : ''}
                        <p><strong>Set:</strong> ${card.set_name || 'Unknown'} (${card.set_code || '?'})</p>
                        <p><strong>Rarity:</strong> ${card.rarity || 'Unknown'}</p>
                        ${card.is_legal_commander ? '<p style="color: green;">✓ Legal Commander</p>' : ''}
                        ${card.is_banned ? '<p style="color: red;">⚠ Banned in Commander</p>' : ''}
                    </div>
                </div>
            </div>
        `;

        modal.classList.add('active');
    } catch (error) {
        console.error('Failed to load card details:', error);
        showNotification('Failed to load card details', 'error');
    }
}

function closeCardModal() {
    const modal = document.getElementById('card-modal');
    modal.classList.remove('active');
}

// ============================================================================
// Print Selection Modal
// ============================================================================

async function showPrintSelection(cardName, onSelectCallback) {
    const modal = document.getElementById('print-modal');
    const printSelection = document.getElementById('print-selection');

    printSelection.innerHTML = '<p>Loading printings...</p>';
    modal.classList.add('active');

    try {
        const response = await API.get(`/cards/${encodeURIComponent(cardName)}/printings`);
        const printings = response.printings;

        if (!printings || printings.length === 0) {
            printSelection.innerHTML = '<p>No printings found.</p>';
            return;
        }

        printSelection.innerHTML = '<div class="print-grid"></div>';
        const grid = printSelection.querySelector('.print-grid');

        printings.forEach(printing => {
            const printDiv = document.createElement('div');
            printDiv.className = 'print-option';
            printDiv.innerHTML = `
                ${printing.image_url ? `<img src="${printing.image_url}" alt="${printing.name}">` : ''}
                <div class="print-set-info">
                    <strong>${printing.set_name}</strong><br>
                    ${printing.set_code.toUpperCase()} #${printing.collector_number}<br>
                    <em>${printing.rarity}</em>
                </div>
            `;

            printDiv.onclick = () => {
                // Remove previous selection
                grid.querySelectorAll('.print-option').forEach(el => 
                    el.classList.remove('selected')
                );
                printDiv.classList.add('selected');

                // Call the callback after a short delay
                setTimeout(() => {
                    onSelectCallback(printing);
                    closePrintModal();
                }, 300);
            };

            grid.appendChild(printDiv);
        });
    } catch (error) {
        console.error('Failed to load printings:', error);
        printSelection.innerHTML = '<p>Failed to load printings.</p>';
    }
}

function closePrintModal() {
    const modal = document.getElementById('print-modal');
    modal.classList.remove('active');
}

// ============================================================================
// Card Options Modal
// ============================================================================

async function showCardOptions(cardId) {
    if (!currentDeck) return;

    const deckCard = currentDeck.cards.find(dc => dc.card_id === cardId);
    if (!deckCard) return;

    const modal = document.getElementById('options-modal');
    const optionsBody = document.getElementById('options-body');

    optionsBody.innerHTML = `
        <div class="options-form">
            <div class="form-group">
                <label>Card Name:</label>
                <div><strong>${deckCard.card.name}</strong></div>
            </div>

            <div class="form-group">
                <label for="card-quantity">Quantity:</label>
                <input type="number" 
                       id="card-quantity" 
                       min="1" 
                       max="100" 
                       value="${deckCard.quantity}">
            </div>

            <div class="form-group">
                <label>Current Printing:</label>
                <div class="current-printing">
                    ${deckCard.selected_image_url ? 
                        `<img src="${deckCard.selected_image_url}" 
                              style="width: 150px; border-radius: 5px; margin-bottom: 0.5rem;">` 
                        : ''}
                    <div>${deckCard.selected_set_code ? 
                        `${deckCard.selected_set_code.toUpperCase()} #${deckCard.selected_collector_number}` 
                        : 'Default printing'}</div>
                </div>
                <button type="button" 
                        class="btn-secondary" 
                        onclick="changePrinting('${cardId}', '${deckCard.card.name}')">
                    Change Printing
                </button>
            </div>

            <div class="form-actions">
                <button type="button" class="btn-primary" onclick="saveCardOptions('${cardId}')">
                    Save Changes
                </button>
                <button type="button" class="btn-secondary" onclick="closeOptionsModal()">
                    Cancel
                </button>
            </div>
        </div>
    `;

    modal.classList.add('active');
}

async function changePrinting(cardId, cardName) {
    await showPrintSelection(cardName, async (printing) => {
        // Update the deck card with new printing
        await updateDeckCard(cardId, {
            selected_printing_id: printing.id,
            selected_image_url: printing.image_url,
            selected_set_code: printing.set_code,
            selected_collector_number: printing.collector_number
        });

        closeOptionsModal();
    });
}

async function saveCardOptions(cardId) {
    const quantity = parseInt(document.getElementById('card-quantity').value);

    if (quantity < 1 || quantity > 100) {
        showNotification('Quantity must be between 1 and 100', 'error');
        return;
    }

    await updateDeckCard(cardId, { quantity });
    closeOptionsModal();
}

function closeOptionsModal() {
    const modal = document.getElementById('options-modal');
    modal.classList.remove('active');
}

// ============================================================================
// Enhanced Add Card Flow
// ============================================================================

async function addCardWithOptions(card) {
    // Check if card is legendary for commander selection
    const isLegendary = card.is_legal_commander;
    const hasCommander = currentDeck && currentDeck.cards && 
                        currentDeck.cards.some(dc => dc.is_commander);

    // Show print selection first
    await showPrintSelection(card.name, async (printing) => {
        // Then show quantity selection
        const quantity = prompt('Enter quantity (1-99):', '1');
        if (!quantity) return;

        const qty = parseInt(quantity);
        if (isNaN(qty) || qty < 1 || qty > 99) {
            showNotification('Invalid quantity', 'error');
            return;
        }

        // Determine if should be commander
        let isCommander = false;
        if (isLegendary && !hasCommander) {
            isCommander = confirm(`Make ${card.name} the commander?`);
        }

        // Add card with selected options
        await addCardToDeck(card, {
            quantity: qty,
            is_commander: isCommander,
            selected_printing_id: printing.id,
            selected_image_url: printing.image_url,
            selected_set_code: printing.set_code,
            selected_collector_number: printing.collector_number
        });
    });
}

// Close modals when clicking outside
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.classList.remove('active');
    }
}

// Make functions globally available
window.showCardModal = showCardModal;
window.closeCardModal = closeCardModal;
window.showPrintSelection = showPrintSelection;
window.closePrintModal = closePrintModal;
window.showCardOptions = showCardOptions;
window.closeOptionsModal = closeOptionsModal;
window.addCardWithOptions = addCardWithOptions;
window.changePrinting = changePrinting;
window.saveCardOptions = saveCardOptions;
