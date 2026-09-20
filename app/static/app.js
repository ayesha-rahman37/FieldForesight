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

const errorBox = document.getElementById("errorBox");

const mixedCropsSelect = document.getElementById("mixedCrops");
const farmId = "farm_" + Date.now();


async function loadOptions() {

    try {

        const [cropResponse, regionResponse] = await Promise.all([
            fetch("/api/crops"),
            fetch("/api/regions")
        ]);

        if (!cropResponse.ok || !regionResponse.ok) {
            throw new Error("Could not load crop or region data.");
        }

        const crops = await cropResponse.json();
        const regions = await regionResponse.json();

        crops.forEach(crop => {

            const option = document.createElement("option");

            option.value = crop.name;
            option.textContent = crop.name;

            cropSelect.appendChild(option);
        });

        crops.forEach(crop => {
            const mixedOption = document.createElement("option");
            mixedOption.value = crop.name;
            mixedOption.textContent = crop.name;
            mixedCropsSelect.appendChild(mixedOption);
        });

        regions.forEach(region => {

            const option = document.createElement("option");

            option.value = region.name;
            option.textContent = region.name;

            regionSelect.appendChild(option);
        });

    } catch (error) {

        showError("Could not load crop and region information.");
    }
}


predictionForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    hideError();

    const crop = cropSelect.value;
    const region = regionSelect.value;

    const variety = document.getElementById("variety").value;
    const croppingType = document.getElementById("croppingType").value;

    if (!crop || !region) {
        showError("Please select both crop and region.");
        return;
    }

    predictBtn.disabled = true;
    predictBtn.textContent = "Generating...";

    try {

        const response = await fetch("/api/predict", {

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

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Prediction failed.");
        }

        predictedYield.textContent =
            Number(data.predicted_yield).toFixed(2);

        lowerBound.textContent =
            Number(data.lower_bound).toFixed(2);

        upperBound.textContent =
            Number(data.upper_bound).toFixed(2);

        forecastMessage.textContent = data.message;

        validationNote.textContent =
            `এই পূর্বাভাস ${region}-এর ঐতিহাসিক ডেটার ভিত্তিতে, ${variety} জাত ও ${croppingType} পদ্ধতি বিবেচনা করে তৈরি।`;

        emptyResult.classList.add("d-none");
        resultContent.classList.remove("d-none");

        // Cropping type single না হলে ও crop select করা থাকলে mixed-crop data save করা
        if (croppingType !== "single") {
            const selectedMixedCrops = Array.from(mixedCropsSelect.selectedOptions).map(o => o.value);

            if (selectedMixedCrops.length > 0) {
                try {
                    await fetch("/api/mixed-crop", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            farm_id: farmId,
                            relation_type: croppingType,
                            crops: selectedMixedCrops.map((cropName, index) => ({
                                crop: cropName,
                                sequence_order: index + 1
                            }))
                        })
                    });
                } catch (err) {
                    console.error("Mixed crop save failed:", err);
                }
            }
        }

    } catch (error) {

        showError(error.message);

    } finally {

        predictBtn.disabled = false;
        predictBtn.textContent = "Generate Prediction";
    }

});


function showError(message) {

    errorBox.textContent = message;
    errorBox.classList.remove("d-none");
}


function hideError() {

    errorBox.textContent = "";
    errorBox.classList.add("d-none");
}


// ---------- Historical Trend Graph ----------

const histCropSelect = document.getElementById("histCrop");
const histRegionSelect = document.getElementById("histRegion");
const showTrendBtn = document.getElementById("showTrendBtn");
const trendEmpty = document.getElementById("trendEmpty");
const trendChartCanvas = document.getElementById("trendChart");

let trendChartInstance = null;

async function loadHistOptions() {
    try {
        const [cropResponse, regionResponse] = await Promise.all([
            fetch("/api/crops"),
            fetch("/api/regions")
        ]);

        const crops = await cropResponse.json();
        const regions = await regionResponse.json();

        crops.forEach(crop => {
            const option = document.createElement("option");
            option.value = crop.name;
            option.textContent = crop.name;
            histCropSelect.appendChild(option);
        });

        regions.forEach(region => {
            const option = document.createElement("option");
            option.value = region.name;
            option.textContent = region.name;
            histRegionSelect.appendChild(option);
        });
    } catch (error) {
        console.error("Historical dropdown load failed:", error);
    }
}

showTrendBtn.addEventListener("click", async function () {
    const crop = histCropSelect.value;
    const region = histRegionSelect.value;

    if (!crop || !region) {
        alert("Crop ও Region দুটোই সিলেক্ট করুন।");
        return;
    }

    try {
        const response = await fetch(
            `/api/historical-data?crop=${encodeURIComponent(crop)}&region=${encodeURIComponent(region)}`
        );

        if (!response.ok) {
            throw new Error("Historical data পাওয়া যায়নি।");
        }

        const data = await response.json();

        if (!data.years || data.years.length === 0) {
            trendEmpty.textContent = "এই Crop ও Region-এর জন্য কোনো historical data নেই।";
            trendEmpty.classList.remove("d-none");
            trendChartCanvas.classList.add("d-none");
            return;
        }

        trendEmpty.classList.add("d-none");
        trendChartCanvas.classList.remove("d-none");

        if (trendChartInstance) {
            trendChartInstance.destroy();
        }

        trendChartInstance = new Chart(trendChartCanvas, {
            type: "line",
            data: {
                labels: data.years,
                datasets: [
                    {
                        label: "Yield (ton/hectare)",
                        data: data.yield,
                        borderColor: "#22c55e",
                        tension: 0.3
                    },
                    {
                        label: "Rainfall (mm)",
                        data: data.rainfall,
                        borderColor: "#3b82f6",
                        tension: 0.3
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: { legend: { position: "top" } }
            }
        });

    } catch (error) {
        alert(error.message);
    }
});


loadOptions();
loadHistOptions();