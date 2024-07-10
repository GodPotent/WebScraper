document.getElementById('scrape-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const searchTerm = document.getElementById('search-term').value;

    fetch('/scrape', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ search_term: searchTerm }),
    })
    .then(response => response.json())
    .then(data => {
        let resultsTable = document.getElementById('results-table').getElementsByTagName('tbody')[0];
        resultsTable.innerHTML = '';
        if (data.error) {
            let row = resultsTable.insertRow();
            let cell = row.insertCell(0);
            cell.colSpan = 3;
            cell.style.color = 'red';
            cell.textContent = `Error: ${data.error}`;
        } else {
            data.content.forEach(product => {
                let row = resultsTable.insertRow();
                let titleCell = row.insertCell(0);
                let priceCell = row.insertCell(1);
                let linkCell = row.insertCell(2);
                
                titleCell.textContent = product.title;
                priceCell.textContent = `$${product.price}`;
                let link = document.createElement('a');
                link.href = product.link;
                link.textContent = 'View Product';
                link.target = '_blank';
                linkCell.appendChild(link);
            });
        }
    })
    .catch(error => {
        let resultsTable = document.getElementById('results-table').getElementsByTagName('tbody')[0];
        resultsTable.innerHTML = '';
        let row = resultsTable.insertRow();
        let cell = row.insertCell(0);
        cell.colSpan = 3;
        cell.style.color = 'red';
        cell.textContent = `Error: ${error}`;
        console.error('Error:', error);
    });
});
