const cropSelect = document.getElementById("crop");
const regionSelect = document.getElementById("region");

const predictionForm = document.getElementById("predictionForm");
const predictBtn = document.getElementById("predictBtn");

const emptyResult = document.getElementById("emptyResult");
const resultContent = document.getElementById("resultContent");

const predictedYield = document.getElementById("predictedYield");
const lowerBound = document.getElementById("lowerBound");
const upperBound = document.getElementById("upperBound");

const forecastMessage = document.getElementById("forecastMessage");
const validationNote = document.getElementById("validationNote");

const modelVersion = document.getElementById("modelVersion");
const cacheStatus = document.getElementById("cacheStatus");

const errorBox = document.getElementById("errorBox");

const mixedCropsSelect = document.getElementById("mixedCrops");

const histCropSelect = document.getElementById("histCrop");
const histRegionSelect = document.getElementById("histRegion");
const showTrendBtn = document.getElementById("showTrendBtn");

const trendEmpty = document.getElementById("trendEmpty");
const trendChartCanvas = document.getElementById("trendChart");

const historyTableBody =
    document.getElementById("historyTableBody");

let trendChartInstance = null;

const farmId =
    "farm_" + Date.now();


async function loadOptions() {

    cropSelect.innerHTML =
        '<option value="">Loading...</option>';

    regionSelect.innerHTML =
        '<option value="">Loading...</option>';

    cropSelect.disabled = true;
    regionSelect.disabled = true;

    try {

        const [cropResponse, regionResponse] =
            await Promise.all([
                fetch("/api/crops"),
                fetch("/api/regions")
            ]);

        if (!cropResponse.ok || !regionResponse.ok) {
            throw new Error(
                "Could not load crop or region data."
            );
        }

        const crops =
            await cropResponse.json();

        const regions =
            await regionResponse.json();

        cropSelect.innerHTML =
            '<option value="">Select crop</option>';

        regionSelect.innerHTML =
            '<option value="">Select region</option>';

        mixedCropsSelect.innerHTML = "";


        crops.forEach(crop => {

            const option =
                document.createElement("option");

            option.value = crop.name;
            option.textContent = crop.name;

            cropSelect.appendChild(option);


            const mixedOption =
                document.createElement("option");

            mixedOption.value = crop.name;
            mixedOption.textContent = crop.name;

            mixedCropsSelect.appendChild(
                mixedOption
            );
        });


        regions.forEach(region => {

            const option =
                document.createElement("option");

            option.value = region.name;
            option.textContent = region.name;

            regionSelect.appendChild(option);
        });

    } catch (error) {

        cropSelect.innerHTML =
            '<option value="">Unable to load crops</option>';

        regionSelect.innerHTML =
            '<option value="">Unable to load regions</option>';

        showError(
            "Could not load crop and region information."
        );

    } finally {

        cropSelect.disabled = false;
        regionSelect.disabled = false;
    }
}


async function loadHistoricalOptions() {

    histCropSelect.innerHTML =
        '<option value="">Loading...</option>';

    histRegionSelect.innerHTML =
        '<option value="">Loading...</option>';

    histCropSelect.disabled = true;
    histRegionSelect.disabled = true;

    try {

        const [cropResponse, regionResponse] =
            await Promise.all([
                fetch("/api/crops"),
                fetch("/api/regions")
            ]);

        if (!cropResponse.ok || !regionResponse.ok) {
            throw new Error(
                "Could not load historical data options."
            );
        }

        const crops =
            await cropResponse.json();

        const regions =
            await regionResponse.json();

        histCropSelect.innerHTML =
            '<option value="">Select crop</option>';

        histRegionSelect.innerHTML =
            '<option value="">Select region</option>';


        crops.forEach(crop => {

            const option =
                document.createElement("option");

            option.value = crop.name;
            option.textContent = crop.name;

            histCropSelect.appendChild(option);
        });


        regions.forEach(region => {

            const option =
                document.createElement("option");

            option.value = region.name;
            option.textContent = region.name;

            histRegionSelect.appendChild(option);
        });

    } catch (error) {

        histCropSelect.innerHTML =
            '<option value="">Unable to load crops</option>';

        histRegionSelect.innerHTML =
            '<option value="">Unable to load regions</option>';

    } finally {

        histCropSelect.disabled = false;
        histRegionSelect.disabled = false;
    }
}


predictionForm.addEventListener(
    "submit",
    async function(event) {

        event.preventDefault();

        hideError();

        const crop = cropSelect.value;
        const region = regionSelect.value;

        const variety =
            document.getElementById("variety").value;

        const croppingType =
            document.getElementById("croppingType").value;


        if (!crop || !region) {

            showError(
                "Please select both crop and region."
            );

            return;
        }


        predictBtn.disabled = true;

        predictBtn.querySelector("span:first-child")
            .textContent = "Generating...";


        try {

            const response =
                await fetch("/api/predict", {

                    method: "POST",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({

                        crop: crop,
                        region: region,
                        variety: variety,
                        cropping_type: croppingType

                    })

                });


            let data;

            const contentType =
                response.headers.get("content-type") || "";

            if (contentType.includes("application/json")) {

                data = await response.json();

            } else {

                const text =
                    await response.text();

                throw new Error(
                    text ||
                    `Prediction request failed with status ${response.status}.`
                );
            }


            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    data.message ||
                    "Prediction failed."
                );
            }


            predictedYield.textContent =
                Number(
                    data.predicted_yield
                ).toFixed(2);


            lowerBound.textContent =
                Number(
                    data.lower_bound
                ).toFixed(2);


            upperBound.textContent =
                Number(
                    data.upper_bound
                ).toFixed(2);


            forecastMessage.textContent =
                data.message;


            validationNote.textContent =
                `This forecast uses the ${region} historical `
                + `yield profile with ${variety} variety and `
                + `${croppingType} cropping.`;



            modelVersion.textContent =
                data.model_version || "Not available";


            cacheStatus.textContent =
                data.cache_hit
                    ? "Cache hit"
                    : "Fresh forecast";


            emptyResult.classList.add(
                "d-none"
            );

            resultContent.classList.remove(
                "d-none"
            );


            if (croppingType !== "single") {

                const selectedMixedCrops =
                    Array.from(
                        mixedCropsSelect.selectedOptions
                    ).map(
                        option => option.value
                    );


                if (
                    selectedMixedCrops.length > 0
                ) {

                    try {

                        await fetch(
                            "/api/mixed-crop",
                            {
                                method: "POST",

                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },

                                body: JSON.stringify({

                                    farm_id: farmId,

                                    relation_type:
                                        croppingType,

                                    crops:
                                        selectedMixedCrops.map(
                                            (
                                                cropName,
                                                index
                                            ) => ({

                                                crop: cropName,

                                                sequence_order:
                                                    index + 1

                                            })
                                        )
                                })
                            }
                        );

                    } catch (mixedError) {

                        console.error(
                            "Mixed crop save failed:",
                            mixedError
                        );
                    }
                }
            }


            await loadPredictionHistory();

        } catch (error) {

            showError(
                error.message
            );

        } finally {

            predictBtn.disabled = false;

            predictBtn.querySelector(
                "span:first-child"
            ).textContent =
                "Generate Prediction";
        }
    }
);


async function loadHistoricalTrend() {

    const crop =
        histCropSelect.value;

    const region =
        histRegionSelect.value;


    if (!crop || !region) {

        alert(
            "Please select both crop and region."
        );

        return;
    }


    showTrendBtn.disabled = true;
    showTrendBtn.textContent = "Loading...";


    try {

        const response =
            await fetch(
                `/api/historical-data?crop=${encodeURIComponent(crop)}&region=${encodeURIComponent(region)}`
            );


        if (!response.ok) {

            throw new Error(
                "Historical data could not be loaded."
            );
        }


            let data;

            const contentType =
                response.headers.get("content-type") || "";

            if (contentType.includes("application/json")) {

                data = await response.json();

            } else {

                const text =
                    await response.text();

                throw new Error(
                    text ||
                    `Historical data request failed with status ${response.status}.`
                );
            }

            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    data.message ||
                    "Historical data could not be loaded."
                );
            }


        if (
            !data.years ||
            data.years.length === 0
        ) {

            trendEmpty.innerHTML = `
                <div class="empty-illustration">↗</div>
                <h4>No historical records found</h4>
                <p>
                    No historical records are available for
                    the selected crop and region.
                </p>
            `;

            trendEmpty.classList.remove(
                "d-none"
            );

            trendChartCanvas.classList.add(
                "d-none"
            );

            return;
        }


        trendEmpty.classList.add(
            "d-none"
        );

        trendChartCanvas.classList.remove(
            "d-none"
        );


        if (trendChartInstance) {

            trendChartInstance.destroy();
        }


        trendChartInstance =
            new Chart(
                trendChartCanvas,
                {
                    type: "line",

                    data: {

                        labels: data.years,

                        datasets: [

                            {
                                label:
                                    "Yield (tons/hectare)",

                                data:
                                    data.yield,

                                borderColor:
                                    "#16834a",

                                backgroundColor:
                                    "rgba(22, 131, 74, 0.08)",

                                fill: true,

                                tension: 0.35,

                                yAxisID:
                                    "yieldAxis"
                            },

                            {
                                label:
                                    "Rainfall (mm)",

                                data:
                                    data.rainfall,

                                borderColor:
                                    "#3174d8",

                                backgroundColor:
                                    "rgba(49, 116, 216, 0.05)",

                                fill: false,

                                tension: 0.35,

                                yAxisID:
                                    "rainfallAxis"
                            }
                        ]
                    },


                    options: {

                        responsive: true,

                        maintainAspectRatio: false,

                        interaction: {
                            mode: "index",
                            intersect: false
                        },

                        plugins: {

                            legend: {
                                position: "top",

                                labels: {
                                    usePointStyle: true,

                                    boxWidth: 8,

                                    color: "#66736b",

                                    font: {
                                        family:
                                            "Inter",
                                        size: 10,
                                        weight: "600"
                                    }
                                }
                            }
                        },

                        scales: {

                            x: {
                                grid: {
                                    display: false
                                },

                                ticks: {
                                    color: "#8a968f",

                                    font: {
                                        family:
                                            "Inter",
                                        size: 9
                                    }
                                }
                            },

                            yieldAxis: {

                                position: "left",

                                grid: {
                                    color:
                                        "rgba(23, 35, 28, 0.06)"
                                },

                                ticks: {
                                    color: "#8a968f",

                                    font: {
                                        family:
                                            "Inter",
                                        size: 9
                                    }
                                }
                            },

                            rainfallAxis: {

                                position: "right",

                                grid: {
                                    drawOnChartArea:
                                        false
                                },

                                ticks: {
                                    color: "#8a968f",

                                    font: {
                                        family:
                                            "Inter",
                                        size: 9
                                    }
                                }
                            }
                        }
                    }
                }
            );

    } catch (error) {

        alert(
            error.message
        );

    } finally {

        showTrendBtn.disabled = false;
        showTrendBtn.textContent =
            "Show Trend";
    }
}


async function loadPredictionHistory() {

    try {

        const response =
            await fetch(
                "/api/predictions/history"
            );


        if (!response.ok) {
            throw new Error(
                "Could not load prediction history."
            );
        }


        const predictions =
            await response.json();


        if (
            !predictions ||
            predictions.length === 0
        ) {

            historyTableBody.innerHTML = `
                <tr>
                    <td
                        colspan="7"
                        class="table-empty"
                    >
                        No prediction history available.
                    </td>
                </tr>
            `;

            return;
        }


        historyTableBody.innerHTML =
            predictions.map(
                prediction => {

                    const createdAt =
                        new Date(
                            prediction.created_at
                        );


                    const dateText =
                        createdAt.toLocaleDateString(
                            "en-US",
                            {
                                year: "numeric",
                                month: "short",
                                day: "numeric"
                            }
                        );


                    const rangeText =
                        `${Number(
                            prediction.lower_bound
                        ).toFixed(2)} - `
                        + `${Number(
                            prediction.upper_bound
                        ).toFixed(2)}`;


                    return `
                        <tr>

                            <td>
                                ${dateText}
                            </td>

                            <td>
                                <strong>
                                    ${escapeHtml(
                                        prediction.crop
                                    )}
                                </strong>
                            </td>

                            <td>
                                ${escapeHtml(
                                    prediction.region
                                )}
                            </td>

                            <td>
                                ${escapeHtml(
                                    prediction.variety
                                )}
                            </td>

                            <td>
                                ${escapeHtml(
                                    prediction.cropping_type
                                )}
                            </td>

                            <td>
                                <strong>
                                    ${Number(
                                        prediction.predicted_yield
                                    ).toFixed(2)}
                                </strong>
                            </td>

                            <td>
                                ${rangeText}
                            </td>

                        </tr>
                    `;
                }
            ).join("");

    } catch (error) {

        historyTableBody.innerHTML = `
            <tr>
                <td
                    colspan="7"
                    class="table-empty"
                >
                    Prediction history is unavailable.
                </td>
            </tr>
        `;
    }
}


function escapeHtml(value) {

    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function showError(message) {

    errorBox.textContent =
        message;

    errorBox.classList.remove(
        "d-none"
    );
}


function hideError() {

    errorBox.textContent = "";

    errorBox.classList.add(
        "d-none"
    );
}


showTrendBtn.addEventListener(
    "click",
    loadHistoricalTrend
);


loadOptions();
loadHistoricalOptions();
loadPredictionHistory();