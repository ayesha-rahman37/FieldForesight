const authScreen = document.getElementById("authScreen");
const dashboardScreen = document.getElementById("dashboardScreen");

const loginForm = document.getElementById("loginForm");
const registerForm = document.getElementById("registerForm");

const showLoginBtn = document.getElementById("showLoginBtn");
const showRegisterBtn = document.getElementById("showRegisterBtn");
const authMessage = document.getElementById("authMessage");

let accessToken = sessionStorage.getItem("accessToken");

showLoginBtn.addEventListener("click", () => {
    loginForm.classList.remove("d-none");
    registerForm.classList.add("d-none");
    authMessage.textContent = "";
});

showRegisterBtn.addEventListener("click", () => {
    registerForm.classList.remove("d-none");
    loginForm.classList.add("d-none");
    authMessage.textContent = "";
});

function showAuthMessage(message, isError = false) {
    authMessage.textContent = message;
    authMessage.className = isError
        ? "mt-3 text-danger"
        : "mt-3 text-success";
}

function showDashboard() {
    authScreen.classList.add("d-none");
    dashboardScreen.classList.remove("d-none");
    loadHistory();
    loadProfile();
    checkAdminAccess();
}
function showLogin() {
    accessToken = null;
    sessionStorage.removeItem("accessToken");
    dashboardScreen.classList.add("d-none");
    authScreen.classList.remove("d-none");
}

async function postJson(url, body, token = null) {
    const headers = {
        "Content-Type": "application/json"
    };

    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(url, {
        method: "POST",
        headers,
        body: JSON.stringify(body)
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(data.detail || "Request failed.");
    }

    return data;
}

registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    showAuthMessage("Creating account...");

    try {
        await postJson("/api/auth/register", {
            username: document.getElementById("registerUsername").value.trim(),
            email: document.getElementById("registerEmail").value.trim(),
            password: document.getElementById("registerPassword").value
        });

        registerForm.reset();
        loginForm.classList.remove("d-none");
        registerForm.classList.add("d-none");
        showAuthMessage("Account created! Please log in.");
    } catch (error) {
        showAuthMessage(error.message, true);
    }
});

loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    showAuthMessage("Signing in...");

    try {
        const data = await postJson("/api/auth/login", {
            username: document.getElementById("loginUsername").value.trim(),
            password: document.getElementById("loginPassword").value
        });

        accessToken = data.access_token;
        sessionStorage.setItem("accessToken", accessToken);

        loginForm.reset();
        showDashboard();
        await loadOptions();
    } catch (error) {
        showAuthMessage(error.message, true);
    }
});

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

        cropSelect.replaceChildren(new Option("Select crop", ""));
        regionSelect.replaceChildren(new Option("Select region", ""));

        crops.forEach((crop) => {
            cropSelect.add(new Option(crop.name, crop.name));
        });

        regions.forEach((region) => {
            regionSelect.add(new Option(region.name, region.name));
        });
    } catch (error) {
        showError("Could not load crop and region information.");
    }
}

predictionForm.addEventListener("submit", async (event) => {
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

    if (!accessToken) {
        showLogin();
        showAuthMessage("Please log in to generate a prediction.", true);
        return;
    }

    predictBtn.disabled = true;
    predictBtn.textContent = "Generating...";

    try {
        const response = await fetch("/api/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${accessToken}`
            },
            body: JSON.stringify({
                crop,
                region,
                variety,
                cropping_type: croppingType
            })
        });

        const data = await response.json().catch(() => ({}));

        if (response.status === 401 || response.status === 403) {
            showLogin();
            showAuthMessage("Your session may have expired. Please log in again.", true);
            return;
        }

        if (!response.ok) {
            throw new Error(data.detail || "Prediction failed.");
        }

        predictedYield.textContent = Number(data.predicted_yield).toFixed(2);
        lowerBound.textContent = Number(data.lower_bound).toFixed(2);
        upperBound.textContent = Number(data.upper_bound).toFixed(2);
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


const historyTableBody = document.getElementById("historyTableBody");
const historyMessage = document.getElementById("historyMessage");
const refreshHistoryBtn = document.getElementById("refreshHistoryBtn");

async function loadHistory() {
    if (!accessToken || !historyTableBody || !historyMessage) return;

    historyMessage.textContent = "Loading prediction history...";
    historyTableBody.replaceChildren();

    try {
        const response = await fetch("/api/predictions/history", {
            headers: {
                Authorization: `Bearer ${accessToken}`
            }
        });

        const data = await response.json().catch(() => ({}));

        if (response.status === 401 || response.status === 403) {
            showLogin();
            showAuthMessage("Please log in again to view your history.", true);
            return;
        }

        if (!response.ok) {
            throw new Error(data.detail || "Could not load history.");
        }

        const records = Array.isArray(data) ? data : data.items;

        if (!Array.isArray(records)) {
            throw new Error("Unexpected history response format.");
        }

        if (records.length === 0) {
            historyMessage.textContent = "No predictions yet. Generate your first forecast!";
            return;
        }

        records.forEach(record => {
            const row = document.createElement("tr");

            const values = [
                record.crop,
                record.region,
                record.variety,
                Number(record.predicted_yield).toFixed(2),
                record.created_at
                    ? new Date(record.created_at).toLocaleString()
                    : "—"
            ];

            values.forEach(value => {
                const cell = document.createElement("td");
                cell.textContent = value ?? "—";
                row.appendChild(cell);
            });

            historyTableBody.appendChild(row);
        });

        historyMessage.textContent = `${records.length} prediction(s) found.`;
    } catch (error) {
        historyMessage.textContent = error.message;
    }
}

if (refreshHistoryBtn) {
    refreshHistoryBtn.addEventListener("click", loadHistory);
}
const currentUsername = document.getElementById("currentUsername");
const logoutBtn = document.getElementById("logoutBtn");

async function loadProfile() {
    if (!accessToken || !currentUsername) return;

    try {
        const response = await fetch("/api/auth/me", {
            headers: {
                Authorization: `Bearer ${accessToken}`
            }
        });

        if (response.status === 401 || response.status === 403) {
            showLogin();
            showAuthMessage("Your session has expired. Please log in again.", true);
            return;
        }

        if (!response.ok) {
            throw new Error("Could not load your profile.");
        }

        const user = await response.json();
        currentUsername.textContent = user.username;
    } catch (error) {
        currentUsername.textContent = "Profile unavailable";
        console.error(error);
    }
}

if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
        showLogin();
        showAuthMessage("You have been logged out.");
    });
}
const adminSection = document.getElementById("adminSection");
const adminUsersBody = document.getElementById("adminUsersBody");
const adminMessage = document.getElementById("adminMessage");
const refreshUsersBtn = document.getElementById("refreshUsersBtn");

async function checkAdminAccess() {
    if (!accessToken || !adminSection) return;

    try {
        const response = await fetch("/api/auth/me", {
            headers: {
                Authorization: `Bearer ${accessToken}`
            }
        });

        if (!response.ok) {
            adminSection.classList.add("d-none");
            return;
        }

        const user = await response.json();

        // Adjust if your UserResponse exposes the role differently.
        
if (user.role_id === 2) {
    adminSection.classList.remove("d-none");
    await loadAdminUsers();
} else {
    adminSection.classList.add("d-none");
}

    } catch (error) {
        adminSection.classList.add("d-none");
        console.error("Could not check admin access:", error);
    }
}

async function loadAdminUsers() {
    if (!accessToken || !adminUsersBody || !adminMessage) return;

    adminMessage.textContent = "Loading users...";
    adminUsersBody.replaceChildren();

    try {
        const response = await fetch("/api/admin/users", {
            headers: {
                Authorization: `Bearer ${accessToken}`
            }
        });

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(data.detail || "Could not load users.");
        }

        if (!Array.isArray(data)) {
            throw new Error("Unexpected user list format.");
        }

        if (data.length === 0) {
            adminMessage.textContent = "No users found.";
            return;
        }

        data.forEach(user => {
            const row = document.createElement("tr");

            [user.username, user.email, user.role_id,
             user.is_active ? "Active" : "Inactive"].forEach(value => {
                const cell = document.createElement("td");
                cell.textContent = value ?? "—";
                row.appendChild(cell);
            });

            const actions = document.createElement("td");

            const statusButton = document.createElement("button");
            statusButton.type = "button";
            statusButton.className = "btn btn-sm btn-outline-primary me-2";
            statusButton.textContent = user.is_active ? "Deactivate" : "Activate";
            statusButton.addEventListener("click", () =>
                updateUserStatus(user.id, !user.is_active)
            );

            const roleSelect = document.createElement("select");
            roleSelect.className = "form-select form-select-sm d-inline-block";
            roleSelect.style.width = "110px";

            [
                { value: "farmer", label: "Farmer" },
                { value: "admin", label: "Admin" }
            ].forEach(role => {
                const option = new Option(role.label, role.value);
                roleSelect.add(option);
            });

            roleSelect.value = user.role_id === 2 ? "admin" : "farmer";

            const roleButton = document.createElement("button");
            roleButton.type = "button";
            roleButton.className = "btn btn-sm btn-outline-secondary mt-1";
            roleButton.textContent = "Update role";
            roleButton.addEventListener("click", () =>
                updateUserRole(user.id, roleSelect.value)
            );

            actions.append(statusButton, roleSelect, roleButton);
            row.appendChild(actions);
            adminUsersBody.appendChild(row);
        });

        adminMessage.textContent = `${data.length} user(s) loaded.`;
    } catch (error) {
        adminMessage.textContent = error.message;
    }
}

async function updateUserStatus(userId, isActive) {
    try {
        const response = await fetch(`/api/admin/users/${userId}/status`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${accessToken}`
            },
            body: JSON.stringify({ is_active: isActive })
        });

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(data.detail || "Could not update user status.");
        }

        adminMessage.textContent = data.message || "User status updated.";
        await loadAdminUsers();
    } catch (error) {
        adminMessage.textContent = error.message;
    }
}

async function updateUserRole(userId, roleName) {
    try {
        const response = await fetch(`/api/admin/users/${userId}/role`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${accessToken}`
            },
            body: JSON.stringify({ role_name: roleName })
        });

        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            throw new Error(data.detail || "Could not update user role.");
        }

        adminMessage.textContent = data.message || "User role updated.";
        await loadAdminUsers();
    } catch (error) {
        adminMessage.textContent = error.message;
    }
}

if (refreshUsersBtn) {
    refreshUsersBtn.addEventListener("click", loadAdminUsers);
}
if (accessToken) {
    showDashboard();
    loadOptions();
}