document.getElementById('searchButton').addEventListener('click', searchConditions);

// Modal logic
const modal = document.getElementById('imageModal');
const modalImage = document.getElementById('modalImage');
const closeModal = document.getElementById('closeModal');

function searchConditions() {
    const waveHeight = document.getElementById('waveHeight').value;
    const wavePeriod = document.getElementById('wavePeriod').value;
    const waveDirection = document.getElementById('waveDirection').value;
    const windSpeed = document.getElementById('windSpeed').value;
    const windDirection = document.getElementById('windDirection').value;

    const params = new URLSearchParams();
    if (waveHeight) params.append('wave_height', waveHeight);
    if (wavePeriod) params.append('wave_period', wavePeriod);
    if (waveDirection) params.append('wave_direction', waveDirection);
    if (windSpeed) params.append('wind_speed', windSpeed);
    if (windDirection) params.append('wind_direction', windDirection);

    fetch('/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: params.toString()
    })
        .then(response => response.json())
        .then(data => {
            const { matches, total_images } = data; // Destructure the response
            const resultsList = document.getElementById('results');
            const resultsSummary = document.getElementById('results-summary');
            const resultsSummaryText = document.getElementById('results-summary-text');

            // Update the summary text and display it
            resultsSummaryText.textContent = `Out of ${total_images} pics, these are the best:`;
            resultsSummary.style.display = 'block';

            // Clear previous results
            resultsList.innerHTML = '';

            // Populate results
            matches.forEach(match => {
                const item = document.createElement('li');
                item.className = 'result-item';

                const img = document.createElement('img');
                img.src = `/serve/${match.folder}/${match.filename}`;
                img.alt = match.filename;
                img.onclick = () => showModal(`/serve/${match.folder}/${match.filename}`);

                const details = document.createElement('div');
                details.className = 'result-details';
                details.innerHTML = `
                <strong>Image:</strong> ${match.filename}<br>
                <strong>Score:</strong> ${match.score.toFixed(2)}<br>
                <strong>Wave Height Diff:</strong> ${match.differences.wave_height_diff !== null ? match.differences.wave_height_diff.toFixed(2) : 'N/A'}<br>
                <strong>Wave Period Diff:</strong> ${match.differences.wave_period_diff !== null ? match.differences.wave_period_diff.toFixed(2) : 'N/A'}<br>
                <strong>Wave Direction Match:</strong> ${match.differences.wave_direction_diff ? 'No' : 'Yes'}<br>
                <strong>Wind Speed Diff:</strong> ${match.differences.wind_speed_diff !== null ? match.differences.wind_speed_diff.toFixed(2) : 'N/A'}<br>
                <strong>Wind Direction Match:</strong> ${match.differences.wind_direction_diff ? 'No' : 'Yes'}<br>
            `;

                item.appendChild(img);
                item.appendChild(details);
                resultsList.appendChild(item);
            });
        })
        .catch(error => console.error("Error fetching results:", error));
}

// Show the modal
function showModal(imageSrc) {
    modalImage.src = imageSrc;
    modal.style.display = 'flex';
}

// Close the modal
closeModal.onclick = () => {
    modal.style.display = 'none';
};

window.onclick = (event) => {
    if (event.target === modal) {
        modal.style.display = 'none';
    }
};

window.onkeydown = (event) => {
    if (event.key === 'Escape') {
        modal.style.display = 'none';
    }
};
