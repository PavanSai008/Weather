document.addEventListener("DOMContentLoaded", () => {
  fetchCurrentWeather(getCityFromURL());
  fetchForecast(getCityFromURL());
  fetchPopularCities(); // optional if you want live data
  fetchTodayWeather(getCityFromURL()); // Fetch today's weather on load

  function fetchCurrentWeather(city) {
    // If no city is provided, get it from the input field or use default
    if (!city) {
      city = document.getElementById('city-input')?.value.trim() || 'Hyderabad';
    }
    fetch(`/api/current?city=${encodeURIComponent(city)}`)
      .then(res => res.json())
      .then(data => {
        document.getElementById("temp").textContent = `${data.current.temp_c}°C`;
        document.getElementById("condition").textContent = data.current.condition.text;
        document.getElementById("pressure").textContent = `${data.current.pressure_mb} mb`;
        document.getElementById("humidity").textContent = `${data.current.humidity}%`;
        document.getElementById("wind").textContent = `${data.current.wind_kph} km/h`;
        document.getElementById("uv").textContent = `${data.current.uv}`;
        document.getElementById("weather-icon").src = data.current.condition.icon;

        // Update the city name
        document.getElementById("city-name").textContent = data.location.name;
      })
      .catch(err => console.error("Error fetching current weather:", err));
  }

  function fetchForecast() {
    fetch('/api/forecast')
      .then(res => res.json())
      .then(data => {
        const forecastContainer = document.getElementById("forecast");
        forecastContainer.innerHTML = "";

        data.forEach(day => {
          const max = day.day.maxtemp_c;
          const min = day.day.mintemp_c;
          const date = new Date(day.date);
          const formattedDate = date.toLocaleDateString('en-GB', {
            day: '2-digit', month: 'short', weekday: 'short'
          });

          const div = document.createElement("div");
          div.innerHTML = `${max}° / ${min}° <span>${formattedDate}</span>`;
          forecastContainer.appendChild(div);
        });
      })
      .catch(err => console.error("Error fetching forecast:", err));
  }

  function fetchPopularCities() {
    fetch('/api/popular')
      .then(res => res.json())
      .then(data => {
        const listItems = document.querySelectorAll(".popular-cities ul li");
        let i = 0;

        for (const [city, info] of Object.entries(data)) {
          if (listItems[i]) {
            const img = listItems[i].querySelector("img");
            const text = `${city} - ${info.condition}`;
            img.src = info.icon;
            listItems[i].innerHTML = `<img src="${info.icon}" /> ${text}`;
          }
          i++;
        }
      })
      .catch(err => console.error("Error fetching popular cities:", err));
  }

  function updateDateTime() {
    const now = new Date();
    const options = { 
      year: 'numeric', month: 'short', day: 'numeric', 
      hour: '2-digit', minute: '2-digit', second: '2-digit' 
    };
    document.getElementById('datetime').textContent = now.toLocaleString(undefined, options);
  }

  // Call once on load and then every second
  updateDateTime();
  setInterval(updateDateTime, 1000);

  document.getElementById('city-search-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    const city = document.getElementById('city-input').value.trim();
    if (!city) return;
    fetchCurrentWeather(city);
    // Fetch forecast and update chart as well
    fetchForecast(city);
    drawTemperatureChart(city);
    fetchTodayWeather(city); // Fetch today's weather for the searched city
  });

  // On page load, set city name to default
  window.addEventListener('DOMContentLoaded', async () => {
    const res = await fetch('/api/current');
    const data = await res.json();
    document.getElementById('city-name').textContent = data.location ? data.location.name : 'City';
  });

  async function drawTemperatureChart(city) {
    const res = await fetch(`/api/hourly?city=${encodeURIComponent(city || 'Hyderabad')}`);
    const hours = await res.json();

    const labels = hours.map(h => h.time.split(' ')[1]); // "HH:MM"
    const temps = hours.map(h => h.temp_c);

    if (window.tempChartInstance) window.tempChartInstance.destroy();

    const ctx = document.getElementById('tempChart').getContext('2d');
    window.tempChartInstance = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'Temperature (°C)',
          data: temps,
          borderColor: '#fff',
          backgroundColor: 'rgba(255,255,255,0.1)',
          tension: 0.3,
          pointRadius: 2
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { 
            display: true,
            labels: { color: '#fff' }
          }
        },
        scales: {
          x: { 
            title: { display: true, text: 'Time', color: '#fff' },
            ticks: { color: '#fff' },
            grid: { color: 'rgba(255,255,255,0.1)' }
          },
          y: { 
            title: { display: true, text: '°C', color: '#fff' },
            ticks: { color: '#fff' },
            grid: { color: 'rgba(255,255,255,0.1)' }
          }
        }
      }
    });
  }

  // On page load, draw for default city
  window.addEventListener('DOMContentLoaded', () => {
    drawTemperatureChart('Hyderabad');
  });

  // On search, update chart for searched city
  document.getElementById('city-search-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const city = document.getElementById('city-input').value.trim();
    if (city) drawTemperatureChart(city);
  });

  async function populateForecast(city) {
    const res = await fetch(`/api/forecast?city=${encodeURIComponent(city)}`);
    const forecastData = await res.json();

    const forecastContainer = document.getElementById('forecast');
    forecastContainer.innerHTML = ''; // Clear existing content

    forecastData.forEach(day => {
      const dayElement = document.createElement('div');
      dayElement.className = 'forecast-day';

      const icon = document.createElement('img');
      icon.src = day.day.condition.icon; // Use the icon URL from the API
      icon.alt = day.day.condition.text;
      icon.className = 'forecast-icon';

      const dayName = document.createElement('span');
      dayName.className = 'forecast-day-name';
      dayName.textContent = new Date(day.date).toLocaleDateString(undefined, { weekday: 'long' });

      const temp = document.createElement('span');
      temp.className = 'forecast-temp';
      temp.textContent = `${day.day.avgtemp_c}°C`;

      dayElement.appendChild(icon);
      dayElement.appendChild(dayName);
      dayElement.appendChild(temp);

      forecastContainer.appendChild(dayElement);
    });
  }

  // Call this function when the page loads or when a city is searched
  populateForecast('Hyderabad');

  document.getElementById('city-search-form').addEventListener('submit', async function (e) {
    e.preventDefault(); // Prevent the form from reloading the page
    const city = document.getElementById('city-input').value.trim();

    if (!city) {
      alert('Please enter a city name.');
      return;
    }

    // Fetch and update the forecast for the searched city
    await populateForecast(city);
  });

  function fetchTodayWeather(city) {
    // If no city is provided, use the default city
    if (!city) {
      city = document.getElementById('city-input')?.value.trim() || 'Hyderabad';
    }

    fetch(`/api/forecast?city=${encodeURIComponent(city)}`)
      .then(res => res.json())
      .then(data => {
        // Get today's forecast data
        const today = data[0]; // Assuming the first day is today

        // Update sunrise and sunset times
        document.getElementById('sunrise').textContent = today.astro.sunrise;
        document.getElementById('sunset').textContent = today.astro.sunset;

        // You can also update the temperature chart here if needed
      })
      .catch(err => console.error("Error fetching today's weather:", err));
  }

  // Call this function when the page loads or when a city is searched
  document.addEventListener("DOMContentLoaded", () => {
    fetchTodayWeather("Hyderabad");
  });

  document.getElementById('city-search-form').addEventListener('submit', function (e) {
    e.preventDefault();
    const city = document.getElementById('city-input').value.trim();
    if (city) {
      fetchTodayWeather(city);
    }
  });

  document.getElementById('city-search-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const city = document.getElementById('city-input').value.trim();
    if (city) {
      // Reload the page with the city as a query parameter
      window.location.href = `/?city=${encodeURIComponent(city)}`;
    }
  });

  function getCityFromURL() {
    const params = new URLSearchParams(window.location.search);
    return params.get('city') || 'Hyderabad';
  }
});
