const ctx = document.getElementById("findingChart");
const dataElement = document.getElementById("finding-data");

let findingCounts = {};

if (dataElement) {
    try {
        const rawJson = dataElement.textContent.trim();
        findingCounts = rawJson ? JSON.parse(rawJson) : {};
    } catch (error) {
        console.error("Could not parse finding data:", error);
        findingCounts = {};
    }
}

const findingLabels = Object.keys(findingCounts);
const findingValues = Object.values(findingCounts);

if (ctx && findingLabels.length > 0) {
    new Chart(ctx, {
        type: "bar",
        data: {
            labels: findingLabels,
            datasets: [
                {
                    label: "Finding Count",
                    data: findingValues
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
} else if (ctx) {
    ctx.insertAdjacentHTML(
        "afterend",
        "<p class='text-muted mt-3'>No findings available yet. Seed synthetic cases or upload a bill.</p>"
    );
}