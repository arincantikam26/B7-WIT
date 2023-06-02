const filterInput = document.getElementById('filter-input');
const galeriList = document.getElementById('galeri-list');

filterInput.addEventListener('input', () => {
    const filterValue = filterInput.value.toLowerCase();
    const galeriItems = galeriList.getElementById('data-galeri');
    
    for (let i = 0; i < galeriItems.length; i++) {
        const galeriItem = galeriItems[i];
        const textContent = galeriItem.textContent.toLowerCase();
        
        if (textContent.includes(filterValue)) {
            galeriItem.style.display = 'block';
        } else {
            galeriItem.style.display = 'none';
        }
    }
});