function openAddModal() {
    const modal = document.getElementById('transactionModal');
    const form = document.getElementById('transactionForm');
    const title = document.getElementById('modalTitle');
    
    // Reset form
    form.reset();
    form.action = '/transactions/add'; // Set route for adding
    document.getElementById('methodInput').value = 'POST'; // Normal POST
    title.textContent = 'Add Transaction';
    
    // Set default date to today
    document.getElementById('date').valueAsDate = new Date();
    
    // Show modal
    modal.classList.remove('hidden');
    // small delay for transition
    setTimeout(() => {
        modal.children[0].classList.remove('opacity-0');
        modal.children[1].classList.remove('opacity-0', 'scale-95');
        modal.children[1].classList.add('opacity-100', 'scale-100');
    }, 10);
}

function openEditModal(id, date, description, amount, type, category, payment_mode, notes) {
    const modal = document.getElementById('transactionModal');
    const form = document.getElementById('transactionForm');
    const title = document.getElementById('modalTitle');
    
    // Populate form
    title.textContent = 'Edit Transaction';
    form.action = `/transactions/edit/${id}`; // Set route for editing (depends on backend setup, might use API)
    document.getElementById('methodInput').value = 'PUT'; // If using method override or API
    
    document.getElementById('date').value = date;
    document.getElementById('description').value = description;
    document.getElementById('amount').value = amount;
    
    // Select correct radio button
    if(type === 'Income') {
        document.getElementById('typeIncome').checked = true;
    } else {
        document.getElementById('typeExpense').checked = true;
    }
    
    // Trigger change event to update categories if dynamic
    document.getElementById('typeExpense').dispatchEvent(new Event('change'));
    
    document.getElementById('category').value = category;
    document.getElementById('payment_mode').value = payment_mode;
    document.getElementById('notes').value = notes || '';
    
    // Show modal
    modal.classList.remove('hidden');
    setTimeout(() => {
        modal.children[0].classList.remove('opacity-0');
        modal.children[1].classList.remove('opacity-0', 'scale-95');
        modal.children[1].classList.add('opacity-100', 'scale-100');
    }, 10);
}

function closeModal() {
    const modal = document.getElementById('transactionModal');
    
    modal.children[0].classList.add('opacity-0');
    modal.children[1].classList.remove('opacity-100', 'scale-100');
    modal.children[1].classList.add('opacity-0', 'scale-95');
    
    setTimeout(() => {
        modal.classList.add('hidden');
    }, 300);
}

function deleteTransaction(id) {
    if (confirm('Are you sure you want to delete this transaction?')) {
        // Implement deletion logic. Could be a form submission or fetch API.
        // Using form submission to a route /transactions/delete/<id>
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/transactions/delete/${id}`;
        document.body.appendChild(form);
        form.submit();
    }
}

function resetFilters() {
    const form = document.getElementById('filterForm');
    const inputs = form.querySelectorAll('input, select');
    inputs.forEach(input => {
        if (input.type !== 'submit' && input.type !== 'button') {
            input.value = '';
        }
    });
    form.submit();
}

// Optional: Toggle categories based on type
document.addEventListener('DOMContentLoaded', () => {
    const typeRadios = document.querySelectorAll('input[name="type"]');
    // Assuming backend passes a categories map or we manage it here
    
    typeRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            // Logic to filter category dropdown based on e.target.value ('Income' or 'Expense')
            // This requires having category groups available in JS or DOM.
            console.log('Type changed to:', e.target.value);
        });
    });
});
