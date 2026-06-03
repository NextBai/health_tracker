const form = document.getElementById('bp-form');
let bpChart;

async function fetchBPData() {
    const res = await fetch('/api/bp');
    const data = await res.json();
    return data;
}

function renderChart(data) {
    const ctx = document.getElementById('bpChart').getContext('2d');
    
    // Sort data by timestamp ascending
    const sortedData = data.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    
    const labels = sortedData.map(d => {
        const dt = new Date(d.timestamp);
        return `${dt.getMonth()+1}/${dt.getDate()} ${dt.getHours()}:${dt.getMinutes()}`;
    });
    
    const systolicData = sortedData.map(d => d.systolic);
    const diastolicData = sortedData.map(d => d.diastolic);
    const hrData = sortedData.map(d => d.heart_rate);

    if(bpChart) {
        bpChart.destroy();
    }

    bpChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: '收縮壓',
                    data: systolicData,
                    borderColor: '#ff4444',
                    backgroundColor: '#ff4444',
                    tension: 0.3
                },
                {
                    label: '舒張壓',
                    data: diastolicData,
                    borderColor: '#00ffaa',
                    backgroundColor: '#00ffaa',
                    tension: 0.3
                },
                {
                    label: '心率',
                    data: hrData,
                    borderColor: '#0088ff',
                    backgroundColor: '#0088ff',
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: false,
                    grid: { color: '#2a2d35' },
                    ticks: { color: '#e0e0e0' }
                },
                x: {
                    grid: { color: '#2a2d35' },
                    ticks: { color: '#e0e0e0', maxTicksLimit: 5 }
                }
            },
            plugins: {
                legend: { labels: { color: '#e0e0e0' } }
            }
        }
    });
}

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
        systolic: document.getElementById('systolic').value,
        diastolic: document.getElementById('diastolic').value,
        heart_rate: document.getElementById('heart_rate').value
    };
    
    const res = await fetch('/api/bp', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    });
    
    if (res.ok) {
        form.reset();
        init();
    }
});

async function init() {
    const data = await fetchBPData();
    renderChart(data);
}

init();
