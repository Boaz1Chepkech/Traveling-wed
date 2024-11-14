document.addEventListener('DOMContentLoaded', () => {
    const accommodationForm = document.getElementById('accommodationForm');
    const accommodationList = document.getElementById('accommodationList');
    const sortSelect = document.getElementById('sort');

    // Sample data for accommodation listings
    const accommodations = [
        {
            name: 'Luxury Grand Hotel',
            price: 500,
            rating: 5,
            image: 'luxury-hotel1.jpg',
            description: 'A luxurious experience with all amenities.',
        },
        {
            name: 'Comfort Suites',
            price: 300,
            rating: 4,
            image: 'comfort-suites.jpg',
            description: 'Affordable comfort with great service.',
        },
        // Add more accommodation entries here...
    ];

    function displayAccommodations(data) {
        accommodationList.innerHTML = '';
        data.forEach(acc => {
            const card = document.createElement('div');
            card.classList.add('accommodation-card');

            card.innerHTML = `
                <img src="${acc.image}" alt="${acc.name}" class="accommodation-image">
                <div class="accommodation-info">
                    <h3>${acc.name}</h3>
                    <p class="price">$${acc.price} per night</p>
                    <p class="rating">⭐⭐⭐⭐⭐</p>
                    <p class="description">${acc.description}</p>
                    <button class="book-now">Book Now</button>
                </div>
            `;
            accommodationList.appendChild(card);
        });
    }

    accommodationForm.addEventListener('submit', event => {
        event.preventDefault();

        // Filter accommodation based on form inputs (for now, we will just show all)
        displayAccommodations(accommodations);
    });

    // Handle Sorting
    sortSelect.addEventListener('change', () => {
        const sortBy = sortSelect.value;
        let sortedAccommodations = [...accommodations];

        if (sortBy === 'price-asc') {
            sortedAccommodations.sort((a, b) => a.price - b.price);
        } else if (sortBy === 'price-desc') {
            sortedAccommodations.sort((a, b) => b.price - a.price);
        } else if (sortBy === 'rating') {
            sortedAccommodations.sort((a, b) => b.rating - a.rating);
        }

        displayAccommodations(sortedAccommodations);
    });

    // Initially display all accommodations
    displayAccommodations(accommodations);
});
