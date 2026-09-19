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

const errorBox = document.getElementById("errorBox");


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

        emptyResult.classList.add("d-none");
        resultContent.classList.remove("d-none");

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


loadOptions();