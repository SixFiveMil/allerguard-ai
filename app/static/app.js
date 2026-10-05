let currentAudioObj = null;
let allergenCatalog = [];
let selectedAllergenIds = ["tree_nuts", "peanuts", "coconut", "sesame"];

document.addEventListener('DOMContentLoaded', async () => {
  await loadAllergenCatalog();
  await loadDemoPresets();
  setupFormHandler();
});

async function loadAllergenCatalog() {
  const grid = document.getElementById('allergen-checkbox-grid');
  try {
    const res = await fetch('/api/allergen-catalog');
    allergenCatalog = await res.json();
    renderAllergenCheckboxes();
  } catch (err) {
    console.error('Failed to load allergen catalog:', err);
  }
}

function renderAllergenCheckboxes() {
  const grid = document.getElementById('allergen-checkbox-grid');
  if (!grid) return;
  grid.innerHTML = allergenCatalog.map(item => {
    const isChecked = selectedAllergenIds.includes(item.id);
    return `
      <label class="flex items-center gap-2 p-2 rounded-xl border transition cursor-pointer select-none ${
        isChecked 
          ? 'bg-emerald-500/10 border-emerald-500/40 text-emerald-200' 
          : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700'
      }">
        <input 
          type="checkbox" 
          value="${item.id}" 
          ${isChecked ? 'checked' : ''} 
          onchange="toggleAllergenSelection('${item.id}', this.checked)"
          class="w-3.5 h-3.5 rounded text-emerald-500 focus:ring-0 bg-slate-900 border-slate-700"
        >
        <span class="text-xs font-semibold truncate">${item.label}</span>
      </label>
    `;
  }).join('');
  updateActiveProfileSummary();
}

function toggleAllergenSelection(id, checked) {
  if (checked) {
    if (!selectedAllergenIds.includes(id)) selectedAllergenIds.push(id);
  } else {
    selectedAllergenIds = selectedAllergenIds.filter(x => x !== id);
  }
  renderAllergenCheckboxes();
}

function loadPresetProfile(type) {
  const nameInput = document.getElementById('profile_name_input');
  const customInput = document.getElementById('custom_allergen_input');

  if (type === 'joshua') {
    nameInput.value = 'Joshua';
    selectedAllergenIds = ['tree_nuts', 'peanuts', 'coconut', 'sesame'];
    customInput.value = '';
  } else if (type === 'celiac') {
    nameInput.value = 'Maya (Celiac Friend)';
    selectedAllergenIds = ['gluten_celiac', 'tree_nuts'];
    customInput.value = '';
  } else if (type === 'top9') {
    nameInput.value = 'Top-9 Safe Profile';
    selectedAllergenIds = ['tree_nuts', 'peanuts', 'sesame', 'gluten_celiac', 'dairy', 'eggs', 'soy', 'fish', 'shellfish'];
    customInput.value = '';
  } else if (type === 'dairy_egg') {
    nameInput.value = 'Alex (Dairy & Egg Allergy)';
    selectedAllergenIds = ['dairy', 'eggs'];
    customInput.value = '';
  }
  renderAllergenCheckboxes();
}

function updateActiveProfileSummary() {
  const nameInput = document.getElementById('profile_name_input');
  const badge = document.getElementById('active-user-badge');
  const countBadge = document.getElementById('active-trigger-count');

  const name = nameInput ? nameInput.value.trim() || 'Custom User' : 'Joshua';
  if (badge) badge.innerText = name;
  if (countBadge) countBadge.innerText = `${selectedAllergenIds.length} allergens active`;
}

async function loadDemoPresets() {
  const container = document.getElementById('demo-presets-container');
  try {
    const res = await fetch('/api/demo-samples');
    const samples = await res.json();
    
    container.innerHTML = samples.map(sample => {
      const badgeColor = sample.expected_verdict === 'DANGER' 
        ? 'border-rose-500/30 bg-rose-500/10 text-rose-300 hover:border-rose-500'
        : sample.expected_verdict === 'CAUTION'
        ? 'border-amber-500/30 bg-amber-500/10 text-amber-300 hover:border-amber-500'
        : 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300 hover:border-emerald-500';

      const icon = sample.expected_verdict === 'DANGER' ? 'fa-triangle-exclamation' : sample.expected_verdict === 'CAUTION' ? 'fa-eye' : 'fa-circle-check';

      return `
        <button 
          type="button" 
          onclick="applyPreset(${JSON.stringify(sample).replace(/"/g, '&quot;')})"
          class="p-3 rounded-xl border text-left transition hover:scale-[1.02] cursor-pointer flex flex-col justify-between h-full ${badgeColor}"
        >
          <div>
            <div class="flex items-center justify-between mb-1.5">
              <span class="text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-slate-900/60 border border-slate-700/50">
                ${sample.category}
              </span>
              <i class="fa-solid ${icon} text-xs"></i>
            </div>
            <div class="font-bold text-xs text-white line-clamp-1">${sample.name}</div>
          </div>
          <div class="text-[11px] text-slate-400 mt-2 line-clamp-2">${sample.rationale}</div>
        </button>
      `;
    }).join('');
  } catch (err) {
    console.error('Failed to load presets:', err);
  }
}

function applyPreset(sample) {
  document.getElementById('product_name').value = sample.name;
  document.getElementById('category').value = sample.category;
  document.getElementById('ingredients_text').value = sample.ingredients;
  document.getElementById('certified_allergen_free').checked = Boolean(sample.certified_allergen_free);
  document.getElementById('dedicated_facility').checked = Boolean(sample.dedicated_facility);
  
  // Auto trigger analysis
  document.getElementById('analyze-btn').click();
}

function setupFormHandler() {
  const form = document.getElementById('analyze-form');
  const nameInput = document.getElementById('profile_name_input');
  if (nameInput) {
    nameInput.addEventListener('input', updateActiveProfileSummary);
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const productName = document.getElementById('product_name').value.trim();
    const ingredientsText = document.getElementById('ingredients_text').value.trim();
    const category = document.getElementById('category').value;
    const certifiedAllergenFree = document.getElementById('certified_allergen_free').checked;
    const dedicatedFacility = document.getElementById('dedicated_facility').checked;
    
    const userName = (document.getElementById('profile_name_input')?.value || 'Joshua').trim();
    const customAllergensRaw = document.getElementById('custom_allergen_input')?.value || '';
    const customAllergens = customAllergensRaw.split(',').map(s => s.trim()).filter(Boolean);

    if (!productName || !ingredientsText) return;

    showLoadingState();

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_name: productName,
          ingredients_text: ingredientsText,
          category: category,
          certified_allergen_free: certifiedAllergenFree,
          dedicated_facility: dedicatedFacility,
          user_name: userName,
          selected_allergens: selectedAllergenIds,
          custom_allergens: customAllergens
        })
      });

      if (!response.ok) throw new Error('Analysis failed');

      const data = await response.json();
      renderResults(data);
    } catch (err) {
      alert('Error running analysis: ' + err.message);
      hideLoadingState();
    }
  });
}

function showLoadingState() {
  document.getElementById('empty-state').classList.add('hidden');
  document.getElementById('results-state').classList.add('hidden');
  document.getElementById('loading-state').classList.remove('hidden');

  const stepText = document.getElementById('pipeline-step-text');
  const steps = [
    '1/4: TabPFN evaluating tabular manufacturing and ambiguity features...',
    '2/4: SerpApi checking FDA recall notices & brand disclosures...',
    '3/4: Google Gemma 2 clinical synthesis for nut/sesame/coconut triggers...',
    '4/4: ElevenLabs generating hands-free audio briefing...'
  ];

  let i = 0;
  window.loadingInterval = setInterval(() => {
    i = (i + 1) % steps.length;
    stepText.innerText = steps[i];
  }, 400);
}

function hideLoadingState() {
  clearInterval(window.loadingInterval);
  document.getElementById('loading-state').classList.add('hidden');
}

function renderResults(data) {
  hideLoadingState();
  document.getElementById('results-state').classList.remove('hidden');

  const verdict = data.verdict;
  const banner = document.getElementById('verdict-banner');
  const icon = document.getElementById('verdict-icon');
  const title = document.getElementById('verdict-title');
  const subtitle = document.getElementById('verdict-subtitle');

  const condList = data.conditions ? data.conditions.join(', ') : 'Protected Allergens';
  if (verdict === 'DANGER') {
    banner.className = 'p-5 rounded-2xl border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-xl bg-rose-950/30 border-rose-500/50 text-rose-200';
    icon.className = 'w-12 h-12 rounded-xl flex items-center justify-center text-xl shrink-0 bg-rose-500 text-white';
    icon.innerHTML = '<i class="fa-solid fa-ban"></i>';
    title.innerText = 'DANGER — DO NOT EAT';
    subtitle.innerText = `Critical Allergen Triggered for ${data.user_name || 'User'} (${condList})`;
  } else if (verdict === 'CAUTION') {
    banner.className = 'p-5 rounded-2xl border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-xl bg-amber-950/30 border-amber-500/50 text-amber-200';
    icon.className = 'w-12 h-12 rounded-xl flex items-center justify-center text-xl shrink-0 bg-amber-500 text-slate-950';
    icon.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i>';
    title.innerText = 'CAUTION — INVESTIGATE';
    subtitle.innerText = `Ambiguous Ingredients / Unconfirmed Lines (${condList})`;
  } else {
    banner.className = 'p-5 rounded-2xl border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-xl bg-emerald-950/30 border-emerald-500/50 text-emerald-200';
    icon.className = 'w-12 h-12 rounded-xl flex items-center justify-center text-xl shrink-0 bg-emerald-500 text-slate-950';
    icon.innerHTML = '<i class="fa-solid fa-circle-check"></i>';
    title.innerText = 'SAFE TO CONSUME';
    subtitle.innerText = `Zero Prohibited Allergens Detected for ${data.user_name || 'User'} (${condList})`;
  }

  // Setup Audio playback
  const audioBtn = document.getElementById('audio-speak-btn');
  audioBtn.onclick = () => playSafetyAudio(data);

  // TabPFN Cards
  document.getElementById('prob-safe').innerText = data.tabpfn.probabilities.safe + '%';
  document.getElementById('prob-caution').innerText = data.tabpfn.probabilities.caution + '%';
  document.getElementById('prob-danger').innerText = data.tabpfn.probabilities.danger + '%';
  document.getElementById('tabpfn-engine-badge').innerText = data.tabpfn.engine;

  const driversList = document.getElementById('tabpfn-drivers');
  driversList.innerHTML = data.tabpfn.risk_drivers.map(d => `<li>${d}</li>`).join('');

  // Gemma Card
  document.getElementById('gemma-engine-badge').innerText = data.gemma_analysis.execution_mode;
  document.getElementById('gemma-content').innerText = data.gemma_analysis.analysis;

  // SerpApi Card
  document.getElementById('serpapi-source').innerText = data.web_grounding.source;
  const findingsContainer = document.getElementById('serpapi-findings');
  if (data.web_grounding.findings && data.web_grounding.findings.length > 0) {
    findingsContainer.innerHTML = data.web_grounding.findings.map(f => `
      <div class="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
        <a href="${f.link}" target="_blank" class="font-bold text-teal-400 hover:underline block">${f.title}</a>
        <p class="text-slate-400 text-[11px] mt-0.5">${f.snippet}</p>
      </div>
    `).join('');
  } else {
    findingsContainer.innerHTML = '<div class="text-slate-500">No active FDA allergen recalls found on file.</div>';
  }

  // Sentry Traces Telemetry Card
  document.getElementById('total-latency').innerText = `Total: ${data.telemetry.total_latency_ms}ms`;
  const traceContainer = document.getElementById('trace-breakdown');
  traceContainer.innerHTML = data.telemetry.traces.map(t => `
    <div class="flex items-center justify-between p-2 rounded-lg bg-slate-950 border border-slate-850">
      <div class="flex items-center gap-2">
        <span class="w-5 h-5 rounded-md bg-slate-800 text-[10px] font-mono flex items-center justify-center text-slate-300">
          ${t.step}
        </span>
        <div>
          <span class="font-semibold text-white">${t.name}</span>
          <span class="text-slate-500 text-[11px] block">${t.details}</span>
        </div>
      </div>
      <span class="font-mono text-emerald-400 font-bold shrink-0">${t.latency_ms}ms</span>
    </div>
  `).join('');

  banner.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function playSafetyAudio(data) {
  if (currentAudioObj) {
    currentAudioObj.pause();
    currentAudioObj = null;
  }

  const voice = data.voice_guidance;
  if (voice.audio_base64) {
    currentAudioObj = new Audio(voice.audio_base64);
    currentAudioObj.play();
  } else if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(voice.text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
  } else {
    alert(voice.text);
  }
}
