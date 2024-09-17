document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-search]').forEach(searchBar => {
        searchBar.addEventListener('input', () => {
            const searchInput = searchBar.value.toLowerCase();
            const tableId = searchBar.getAttribute('data-search');
            const tableBody = document.querySelector(`#${tableId}`);

            if (!tableBody) return;

            tableBody.querySelectorAll('tr').forEach(row => {
                const cells = row.querySelectorAll('td');
                let match = false;

                cells.forEach(cell => {
                    if (cell.textContent.toLowerCase().includes(searchInput)) {
                        match = true;
                    }
                });

                row.style.display = match ? '' : 'none';
            });
        });
    });
});
