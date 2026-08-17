/**
 * FieldForesight Frontend Application Logic
 * Integrates REST APIs, Real-time WebSockets, Chart.js Visualizations & UI State Management
 */

// Application State
const state = {
  varieties: [],
  selectedVarietyId: 1,
  currentVariety: null,
  scenario: {
    temperature: 28.5,
    humidity: 72.0,
    rainfall: 160.0,
    wind_speed: 12.0,
    pest_density: 8.0
  },
  lastRiskResult: null,
  ws: null,
  wsConnected: false,
  forecastChartInstance: null,
  isGeneratingAdvisory: false
};

// Scenario Preset Configurations
const SCENARIO_PRESETS = {
  normal: {
    temperature: 28.5,
    humidity: 72.0,
    rainfall: 160.0,
    wind_speed: 12.0,
    pest_density: 8.0
  },
  heatwave: {
    temperature: 39.0,
    humidity: 55.0,
    rainfall: 10.0,
    wind_speed: 18.0,
    pest_density: 22.0
  },
  flood: {
    temperature: 26.0,
    humidity: 95.0,
    rainfall: 380.0,
    wind_speed: 28.0,
    pest_density: 15.0
  },
  cyclone: {
    temperature: 25.0,
    humidity: 92.0,
    rainfall: 260.0,
    wind_speed: 68.0,
    pest_density: 12.0
  },
  pest: {
    temperature: 31.0,
    humidity: 88.0,
    rainfall: 140.0,
    wind_speed: 10.0,
    pest_density: 55.0
  },
  drought: {
    temperature: 37.0,
    humidity: 38.0,
    rainfall: 15.0,
    wind_speed: 14.0,
    pest_density: 28.0
  }
};

// DOM References
const DOM = {
  varietySelect: document.getElementById('variety-select'),
  vpBanglaName: document.getElementById('vp-bangla-name'),
  vpEngName: document.getElementById('vp-eng-name'),
  vpCropBadge: document.getElementById('vp-crop-badge'),
  vpDescription: document.getElementById('vp-description'),
  vpOptimalTemp: document.getElementById('vp-optimal-temp'),
  vpMaxTemp: document.getElementById('vp-max-temp'),
  vpRainfall: document.getElementById('vp-rainfall'),
  vpDuration: document.getElementById('vp-duration'),
  vpYield: document.getElementById('vp-yield'),
  vpPestSusceptibility: document.getElementById('vp-pest-susceptibility'),

  // Sliders & Number inputs
  tempSlider: document.getElementById('temp-slider'),
  tempNum: document.getElementById('temp-num'),
  humSlider: document.getElementById('humidity-slider'),
  humNum: document.getElementById('humidity-num'),
  rainSlider: document.getElementById('rainfall-slider'),
  rainNum: document.getElementById('rainfall-num'),
  windSlider: document.getElementById('wind-slider'),
  windNum: document.getElementById('wind-num'),
  pestSlider: document.getElementById('pest-slider'),
  pestNum: document.getElementById('pest-num'),

  // Risk UI
  riskBadge: document.getElementById('risk-badge'),
  riskScoreValue: document.getElementById('risk-score-value'),
  riskLevelBn: document.getElementById('risk-level-bn'),
  gaugeArc: document.getElementById('gauge-progress-arc'),
  scoreTemp: document.getElementById('score-temp'),
  barTemp: document.getElementById('bar-temp'),
  scoreRain: document.getElementById('score-rain'),
  barRain: document.getElementById('bar-rain'),
  scoreHum: document.getElementById('score-hum'),
  barHum: document.getElementById('bar-hum'),
  scorePest: document.getElementById('score-pest'),
  barPest: document.getElementById('bar-pest'),
  scoreWind: document.getElementById('score-wind'),
  barWind: document.getElementById('bar-wind'),
  warningsList: document.getElementById('warnings-list'),

  // Advisory Elements
  genAdvisoryBtn: document.getElementById('generate-advisory-btn'),
  genBtnText: document.getElementById('gen-btn-text'),
  advVarietyTitle: document.getElementById('adv-variety-title'),
  advEngineBadge: document.getElementById('adv-engine-badge'),
  advTime: document.getElementById('adv-time'),
  advMainText: document.getElementById('adv-main-text'),
  advActionItems: document.getElementById('adv-action-items'),
  advIrrigation: document.getElementById('adv-irrigation'),
  advPest: document.getElementById('adv-pest'),
  copyAdvisoryBtn: document.getElementById('copy-advisory-btn'),
  printAdvisoryBtn: document.getElementById('print-advisory-btn'),

  // Forecast Elements
  forecastDays: document.getElementById('forecast-days'),
  forecastMetric: document.getElementById('forecast-metric'),
  refreshForecastBtn: document.getElementById('refresh-forecast-btn'),
  fMeanVal: document.getElementById('f-mean-val'),
  fMinVal: document.getElementById('f-min-val'),
  fMaxVal: document.getElementById('f-max-val'),
  chartCanvas: document.getElementById('forecastChart'),

  // History Elements
  historyContainer: document.getElementById('history-list-container'),
  refreshHistoryBtn: document.getElementById('refresh-history-btn'),

  // WebSocket elements
  wsBadge: document.getElementById('ws-status-badge'),
  wsText: document.getElementById('ws-status-text'),
  realtimeWsToggle: document.getElementById('realtime-ws-toggle'),

  // Modals & Tools
  addVarietyModal: document.getElementById('add-variety-modal'),
  addVarietyModalBtn: document.getElementById('add-variety-modal-btn'),
  closeModalBtn: document.getElementById('close-modal-btn'),
  cancelModalBtn: document.getElementById('cancel-modal-btn'),
  addVarietyForm: document.getElementById('add-variety-form'),
  themeToggleBtn: document.getElementById('theme-toggle-btn'),
  toastContainer: document.getElementById('toast-container')
};

// -----------------------------------------------------------------------------
// Initialization
// -----------------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', async () => {
  setupEventListeners();
  initWebSocket();
  await loadVarieties();
  triggerRiskEvaluation();
  loadForecast();
});

// -----------------------------------------------------------------------------
// Event Listeners
// -----------------------------------------------------------------------------
function setupEventListeners() {
  // Variety Selector
  DOM.varietySelect.addEventListener('change', (e) => {
    const id = parseInt(e.target.value, 10);
    selectVariety(id);
  });

  // Slider <-> Number Inputs 2-way sync
  setupSliderSync(DOM.tempSlider, DOM.tempNum, 'temperature');
  setupSliderSync(DOM.humSlider, DOM.humNum, 'humidity');
  setupSliderSync(DOM.rainSlider, DOM.rainNum, 'rainfall');
  setupSliderSync(DOM.windSlider, DOM.windNum, 'wind_speed');
  setupSliderSync(DOM.pestSlider, DOM.pestNum, 'pest_density');

  // Preset Chips
  document.querySelectorAll('.preset-chip').forEach((chip) => {
    chip.addEventListener('click', () => {
      document.querySelectorAll('.preset-chip').forEach((c) => c.classList.remove('active'));
      chip.classList.add('active');
      const presetKey = chip.getAttribute('data-scenario');
      applyPreset(presetKey);
    });
  });

  // Tabs Navigation
  document.querySelectorAll('.tab-btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach((b) => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach((c) => c.classList.remove('active'));

      btn.classList.add('active');
      const tabId = btn.getAttribute('data-tab');
      document.getElementById(tabId)?.classList.add('active');

      if (tabId === 'forecast-tab') {
        loadForecast();
      } else if (tabId === 'history-tab') {
        loadAdvisoryHistory();
      }
    });
  });

  // Advisory Generator
  DOM.genAdvisoryBtn.addEventListener('click', generateAdvisory);
  DOM.copyAdvisoryBtn.addEventListener('click', copyAdvisoryToClipboard);
  DOM.printAdvisoryBtn.addEventListener('click', () => window.print());

  // Forecast options
  DOM.forecastDays.addEventListener('change', loadForecast);
  DOM.forecastMetric.addEventListener('change', loadForecast);
  DOM.refreshForecastBtn.addEventListener('click', loadForecast);

  // History Refresh
  DOM.refreshHistoryBtn.addEventListener('click', loadAdvisoryHistory);

  // Modal handlers
  DOM.addVarietyModalBtn.addEventListener('click', () => DOM.addVarietyModal.classList.remove('hidden'));
  DOM.closeModalBtn.addEventListener('click', () => DOM.addVarietyModal.classList.add('hidden'));
  DOM.cancelModalBtn.addEventListener('click', () => DOM.addVarietyModal.classList.add('hidden'));
  DOM.addVarietyForm.addEventListener('submit', handleAddVarietySubmit);

  // Theme Toggle
  DOM.themeToggleBtn.addEventListener('click', () => {
    document.documentElement.classList.toggle('light');
    showToast('Theme switched', 'success');
  });
}

// -----------------------------------------------------------------------------
// Slider & Input Sync
// -----------------------------------------------------------------------------
function setupSliderSync(slider, numberInput, stateKey) {
  let debounceTimeout = null;

  const updateVal = (val) => {
    const num = parseFloat(val);
    state.scenario[stateKey] = num;
    slider.value = num;
    numberInput.value = num;

    clearTimeout(debounceTimeout);
    debounceTimeout = setTimeout(() => {
      triggerRiskEvaluation();
    }, 60);
  };

  slider.addEventListener('input', (e) => updateVal(e.target.value));
  numberInput.addEventListener('input', (e) => updateVal(e.target.value));
}

function applyPreset(presetKey) {
  const p = SCENARIO_PRESETS[presetKey];
  if (!p) return;

  state.scenario = { ...p };
  DOM.tempSlider.value = p.temperature;
  DOM.tempNum.value = p.temperature;
  DOM.humSlider.value = p.humidity;
  DOM.humNum.value = p.humidity;
  DOM.rainSlider.value = p.rainfall;
  DOM.rainNum.value = p.rainfall;
  DOM.windSlider.value = p.wind_speed;
  DOM.windNum.value = p.wind_speed;
  DOM.pestSlider.value = p.pest_density;
  DOM.pestNum.value = p.pest_density;

  triggerRiskEvaluation();
}

// -----------------------------------------------------------------------------
// API & WebSocket Communication
// -----------------------------------------------------------------------------
async function loadVarieties() {
  try {
    const res = await fetch('/api/varieties');
    if (!res.ok) throw new Error('Failed to load crop varieties');
    const data = await res.json();
    state.varieties = data;

    DOM.varietySelect.innerHTML = '';
    data.forEach((v) => {
      const opt = document.createElement('option');
      opt.value = v.id;
      opt.textContent = `${v.name} (${v.crop_type})`;
      DOM.varietySelect.appendChild(opt);
    });

    if (data.length > 0) {
      selectVariety(data[0].id);
    }
  } catch (err) {
    console.error('Error loading varieties:', err);
    showToast('Failed to load crop varieties.', 'error');
  }
}

function selectVariety(id) {
  state.selectedVarietyId = id;
  const v = state.varieties.find((item) => item.id === id);
  if (!v) return;

  state.currentVariety = v;
  DOM.varietySelect.value = id;

  // Update Profile Card
  DOM.vpBanglaName.textContent = v.name;
  DOM.vpEngName.textContent = v.crop_type;
  DOM.vpCropBadge.textContent = v.crop_type;
  DOM.vpDescription.textContent = v.description_bn || 'No description available.';
  DOM.vpOptimalTemp.textContent = `${v.optimal_temp_min}° - ${v.optimal_temp_max}°C`;
  DOM.vpMaxTemp.textContent = `${v.max_temp_threshold}°C`;
  DOM.vpRainfall.textContent = `${v.rainfall_min_mm} - ${v.rainfall_max_mm} mm`;
  DOM.vpDuration.textContent = `${v.growth_duration_days} Days`;
  DOM.vpYield.textContent = `${v.yield_potential_ton_ha} ton/ha`;
  DOM.vpPestSusceptibility.textContent = `${v.pest_susceptibility}`;

  // Update advisory preview title
  DOM.advVarietyTitle.textContent = v.name;

  triggerRiskEvaluation();
  loadForecast();
}

function initWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws/scenario`;

  try {
    state.ws = new WebSocket(wsUrl);

    state.ws.onopen = () => {
      state.wsConnected = true;
      DOM.wsBadge.className = 'status-pill status-online';
      DOM.wsText.textContent = 'Live Streaming Active';
      triggerRiskEvaluation();
    };

    state.ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.type === 'RISK_UPDATE' && payload.result) {
          renderRiskEvaluation(payload.result);
        }
      } catch (e) {
        console.error('WebSocket JSON parse error:', e);
      }
    };

    state.ws.onclose = () => {
      state.wsConnected = false;
      DOM.wsBadge.className = 'status-pill status-connecting';
      DOM.wsText.textContent = 'Reconnecting...';
      setTimeout(initWebSocket, 3000);
    };

    state.ws.onerror = () => {
      state.wsConnected = false;
    };
  } catch (err) {
    console.warn('WebSocket init failed:', err);
  }
}

function triggerRiskEvaluation() {
  const payload = {
    variety_id: state.selectedVarietyId,
    scenario: state.scenario
  };

  const useWs = DOM.realtimeWsToggle.checked && state.wsConnected && state.ws.readyState === WebSocket.OPEN;

  if (useWs) {
    state.ws.send(JSON.stringify(payload));
  } else {
    // REST API fallback
    fetch('/api/risk/evaluate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then((res) => res.json())
      .then((data) => renderRiskEvaluation(data))
      .catch((err) => console.error('REST evaluation error:', err));
  }
}

function renderRiskEvaluation(data) {
  if (!data) return;
  state.lastRiskResult = data;

  const score = data.overall_risk_score || 0;
  const level = data.risk_level || 'LOW';

  DOM.riskScoreValue.textContent = score.toFixed(1);

  // Radial Gauge Math
  // Total arc length = 251.2
  // dashoffset from 251.2 (0%) to 0 (100%)
  const maxDash = 251.2;
  const offset = maxDash - (score / 100) * maxDash;
  DOM.gaugeArc.style.strokeDashoffset = Math.max(0, Math.min(maxDash, offset));

  // Risk Badges & Color styling
  const pillClasses = {
    LOW: { class: 'risk-pill pill-low', text: 'LOW RISK', textDesc: 'No Risk (Favorable)' },
    MEDIUM: { class: 'risk-pill pill-medium', text: 'MEDIUM RISK', textDesc: 'Moderate Risk (Watch)' },
    HIGH: { class: 'risk-pill pill-high', text: 'HIGH RISK', textDesc: 'High Risk (Action Needed)' },
    CRITICAL: { class: 'risk-pill pill-critical', text: 'CRITICAL RISK', textDesc: 'Emergency Alert (Immediate Action)' }
  };

  const currentPill = pillClasses[level] || pillClasses.LOW;
  DOM.riskBadge.className = currentPill.class;
  DOM.riskBadge.textContent = currentPill.text;
  DOM.riskLevelBn.textContent = currentPill.textDesc;

  // Breakdown progress bars
  const scores = data.metric_scores || {};
  const levels = data.metric_levels || {};

  updateMetricBar(DOM.scoreTemp, DOM.barTemp, scores.temperature, levels.temperature);
  updateMetricBar(DOM.scoreRain, DOM.barRain, scores.rainfall, levels.rainfall);
  updateMetricBar(DOM.scoreHum, DOM.barHum, scores.humidity, levels.humidity);
  updateMetricBar(DOM.scorePest, DOM.barPest, scores.pest_density, levels.pest_density);
  updateMetricBar(DOM.scoreWind, DOM.barWind, scores.wind_speed, levels.wind_speed);

  // Warnings list
  DOM.warningsList.innerHTML = '';
  const warnings = data.triggered_warnings || [];
  if (warnings.length === 0 || (warnings.length === 1 && warnings[0].toLowerCase().includes('normal'))) {
    DOM.warningsList.innerHTML = '<li class="warning-safe">✓ Weather conditions are normal and favorable.</li>';
  } else {
    warnings.forEach((w) => {
      const li = document.createElement('li');
      li.className = level === 'CRITICAL' ? 'warning-crit' : '';
      li.textContent = `⚠️ ${w}`;
      DOM.warningsList.appendChild(li);
    });
  }
}

function updateMetricBar(numElem, barElem, scoreVal = 0, levelStr = 'LOW') {
  numElem.textContent = `${scoreVal}%`;
  barElem.style.width = `${Math.min(100, Math.max(5, scoreVal))}%`;

  const fillClasses = {
    LOW: 'fill-low',
    MEDIUM: 'fill-medium',
    HIGH: 'fill-high',
    CRITICAL: 'fill-critical'
  };

  barElem.className = `prog-fill ${fillClasses[levelStr] || 'fill-low'}`;
}

// -----------------------------------------------------------------------------
// AI English Advisory Generation
// -----------------------------------------------------------------------------
async function generateAdvisory() {
  if (state.isGeneratingAdvisory) return;

  state.isGeneratingAdvisory = true;
  DOM.genBtnText.textContent = 'Generating Advisory...';
  DOM.genAdvisoryBtn.disabled = true;

  try {
    const payload = {
      variety_id: state.selectedVarietyId,
      scenario: state.scenario
    };

    const res = await fetch('/api/advisory/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) throw new Error('Advisory generation failed');
    const data = await res.json();

    DOM.advVarietyTitle.textContent = data.variety_name || (state.currentVariety ? state.currentVariety.name : 'Crop');
    DOM.advEngineBadge.textContent = data.llm_provider || 'Agronomic AI Engine';
    DOM.advTime.textContent = new Date().toLocaleTimeString('en-US');
    DOM.advMainText.textContent = data.advisory_text_bn;

    // Action items
    DOM.advActionItems.innerHTML = '';
    const actions = data.action_items_bn || [];
    actions.forEach((act) => {
      const li = document.createElement('li');
      li.textContent = act;
      DOM.advActionItems.appendChild(li);
    });

    DOM.advIrrigation.textContent = data.irrigation_advice_bn || 'Maintain normal soil moisture levels. Supplemental irrigation is not required.';
    DOM.advPest.textContent = data.pest_advice_bn || 'Pest risk is currently within manageable thresholds.';

    showToast('Agricultural advisory generated successfully!', 'success');
  } catch (err) {
    console.error('Generate advisory error:', err);
    showToast('Failed to generate advisory. Please try again.', 'error');
  } finally {
    state.isGeneratingAdvisory = false;
    DOM.genBtnText.textContent = 'Generate Advisory';
    DOM.genAdvisoryBtn.disabled = false;
  }
}

function copyAdvisoryToClipboard() {
  const text = `${DOM.advVarietyTitle.textContent}\n${DOM.advMainText.textContent}\n\nAction Plan:\n${Array.from(DOM.advActionItems.children).map((li) => '- ' + li.textContent).join('\n')}\n\nIrrigation: ${DOM.advIrrigation.textContent}\nPest Management: ${DOM.advPest.textContent}`;
  navigator.clipboard.writeText(text).then(() => {
    showToast('Advisory copied to clipboard!', 'success');
  });
}

// -----------------------------------------------------------------------------
// Yield & Stress Forecaster (Chart.js)
// -----------------------------------------------------------------------------
async function loadForecast() {
  const varietyId = state.selectedVarietyId;
  const days = DOM.forecastDays.value || 30;
  const metric = DOM.forecastMetric.value || 'yield_index';

  try {
    const res = await fetch(`/api/forecast?variety_id=${varietyId}&days=${days}&metric_type=${metric}`);
    if (!res.ok) throw new Error('Forecast API failed');
    const data = await res.json();

    renderForecastChart(data.points, metric);
  } catch (err) {
    console.error('Forecast load error:', err);
  }
}

function renderForecastChart(points = [], metricType = 'yield_index') {
  if (!points || points.length === 0) return;

  const labels = points.map((p) => p.ds);
  const yhatValues = points.map((p) => p.yhat);
  const yhatUpper = points.map((p) => p.yhat_upper);
  const yhatLower = points.map((p) => p.yhat_lower);

  const mean = (yhatValues.reduce((a, b) => a + b, 0) / yhatValues.length).toFixed(2);
  const min = Math.min(...yhatLower).toFixed(2);
  const max = Math.max(...yhatUpper).toFixed(2);

  const unit = metricType === 'yield_index' ? 'ton/ha' : 'Index';
  DOM.fMeanVal.textContent = `${mean} ${unit}`;
  DOM.fMinVal.textContent = `${min} ${unit}`;
  DOM.fMaxVal.textContent = `${max} ${unit}`;

  if (state.forecastChartInstance) {
    state.forecastChartInstance.destroy();
  }

  const ctx = DOM.chartCanvas.getContext('2d');

  // Gradient fill for confidence band
  const gradient = ctx.createLinearGradient(0, 0, 0, 300);
  gradient.addColorStop(0, 'rgba(16, 185, 129, 0.35)');
  gradient.addColorStop(1, 'rgba(16, 185, 129, 0.02)');

  state.forecastChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Upper Confidence Bound',
          data: yhatUpper,
          borderColor: 'rgba(56, 189, 248, 0.4)',
          borderDash: [5, 5],
          borderWidth: 1.5,
          pointRadius: 0,
          fill: false
        },
        {
          label: 'Expected Yield / Trend Line',
          data: yhatValues,
          borderColor: '#10b981',
          backgroundColor: gradient,
          borderWidth: 3,
          pointRadius: 2,
          pointHoverRadius: 6,
          pointBackgroundColor: '#10b981',
          fill: true,
          tension: 0.35
        },
        {
          label: 'Lower Confidence Bound',
          data: yhatLower,
          borderColor: 'rgba(245, 158, 11, 0.4)',
          borderDash: [5, 5],
          borderWidth: 1.5,
          pointRadius: 0,
          fill: false
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false
      },
      plugins: {
        legend: {
          labels: {
            color: '#94a3b8',
            font: { family: 'Outfit, Inter, sans-serif', size: 11 }
          }
        },
        tooltip: {
          backgroundColor: 'rgba(15, 23, 42, 0.95)',
          titleFont: { family: 'Outfit, Inter, sans-serif', size: 12 },
          bodyFont: { family: 'Outfit, Inter, sans-serif', size: 12 },
          padding: 10,
          borderColor: 'rgba(255, 255, 255, 0.1)',
          borderWidth: 1
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: { color: '#64748b', font: { family: 'Outfit, Inter, sans-serif', size: 10 }, maxTicksLimit: 10 }
        },
        y: {
          grid: { color: 'rgba(255, 255, 255, 0.05)' },
          ticks: { color: '#64748b', font: { family: 'Outfit, Inter, sans-serif', size: 10 } }
        }
      }
    }
  });
}

// -----------------------------------------------------------------------------
// History Loader
// -----------------------------------------------------------------------------
async function loadAdvisoryHistory() {
  DOM.historyContainer.innerHTML = '<div class="history-loading">Loading advisory logs...</div>';

  try {
    const res = await fetch(`/api/advisory/history?limit=15`);
    if (!res.ok) throw new Error('Failed to load history');
    const records = await res.json();

    if (records.length === 0) {
      DOM.historyContainer.innerHTML = '<div style="color: var(--text-muted); font-size: 0.9rem;">No historical advisories found.</div>';
      return;
    }

    DOM.historyContainer.innerHTML = '';
    records.forEach((r) => {
      const item = document.createElement('div');
      item.className = 'history-item';

      const timeStr = r.created_at ? new Date(r.created_at).toLocaleString('en-US') : '';

      item.innerHTML = `
        <div class="history-item-top">
          <span class="hist-variety">🌾 ${r.variety_name}</span>
          <span class="engine-badge">${r.risk_level} • ${r.llm_provider || 'AI'}</span>
        </div>
        <div class="hist-text">${r.advisory_text_bn}</div>
        <div style="font-size: 0.72rem; color: var(--text-muted);">${timeStr}</div>
      `;
      DOM.historyContainer.appendChild(item);
    });
  } catch (err) {
    console.error('History load error:', err);
    DOM.historyContainer.innerHTML = '<div style="color: var(--accent-red);">Failed to load advisory logs.</div>';
  }
}

// -----------------------------------------------------------------------------
// Add Variety Modal Handler
// -----------------------------------------------------------------------------
async function handleAddVarietySubmit(e) {
  e.preventDefault();

  const payload = {
    name: document.getElementById('new-var-name').value.trim(),
    name_bangla: document.getElementById('new-var-name-bn').value.trim(),
    crop_type: document.getElementById('new-var-crop').value.trim(),
    optimal_temp_min: parseFloat(document.getElementById('new-var-temp-min').value),
    optimal_temp_max: parseFloat(document.getElementById('new-var-temp-max').value),
    max_temp_threshold: parseFloat(document.getElementById('new-var-temp-threshold').value),
    rainfall_min_mm: parseFloat(document.getElementById('new-var-rain-min').value),
    rainfall_max_mm: parseFloat(document.getElementById('new-var-rain-max').value),
    pest_susceptibility: document.getElementById('new-var-pest').value,
    growth_duration_days: parseInt(document.getElementById('new-var-duration').value, 10),
    yield_potential_ton_ha: parseFloat(document.getElementById('new-var-yield').value),
    description_bn: document.getElementById('new-var-desc-bn').value.trim()
  };

  try {
    const res = await fetch('/api/varieties', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) throw new Error('Failed to create variety');
    const created = await res.json();

    DOM.addVarietyModal.classList.add('hidden');
    DOM.addVarietyForm.reset();
    showToast(`Variety "${created.name}" saved successfully!`, 'success');

    await loadVarieties();
    selectVariety(created.id);
  } catch (err) {
    console.error('Save variety error:', err);
    showToast('Failed to create crop variety.', 'error');
  }
}

// -----------------------------------------------------------------------------
// Toast Notifications
// -----------------------------------------------------------------------------
function showToast(message, type = 'success') {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;

  DOM.toastContainer.appendChild(toast);
  setTimeout(() => {
    toast.remove();
  }, 3500);
}
