// Global fallbacks for i18n & language helpers so that offline caching, network lag, or standalone PWA contexts never break app boot or login
window.I18N = window.I18N || {
  lang: "en",
  t: (k) => k,
  onChange: [],
  applyStatic: () => {}
};
window.t = window.t || ((k) => k);
window.LANG = window.LANG || (() => (window.I18N && window.I18N.lang ? window.I18N.lang : "en"));

// Expose in script scope
const I18N = window.I18N;
const t = window.t;
const LANG = () => (typeof window.LANG === "function" ? window.LANG() : (window.I18N && window.I18N.lang ? window.I18N.lang : "en"));

// Units & other core helper bindings with safe proxies and fallbacks
window.UnitsCore = window.UnitsCore || {
  METRIC: 0,
  IMPERIAL: 1,
  isImperial: (u) => u === 1,
  label: (u) => (u === 1 ? "lb" : "kg"),
  unitText: (s) => s,
  fmtTenths: (n) => String(n ?? 0),
  toTenths: (n) => Number(n ?? 0),
  unitFromProfile: () => 1,
  kgToDisplay: (n) => n,
  displayToKg: (n) => n
};

window.Units = window.Units || {
  get: () => 1,
  set: () => {},
  load: () => Promise.resolve(),
  relabel: () => {},
  isLoaded: () => true,
  onChange: (fn) => {},
  isImperial: () => true,
  label: () => "lb",
  text: (s) => s,
  fmtTenths: (n) => String(n ?? 0),
  toTenths: (n) => Number(n ?? 0)
};

const Units = new Proxy({}, {
  get(target, prop) {
    if (window.Units && prop in window.Units) {
      const val = window.Units[prop];
      return typeof val === "function" ? val.bind(window.Units) : val;
    }
    if (prop === "load") return () => Promise.resolve();
    if (prop === "onChange") return () => {};
    if (prop === "get") return () => 1;
    if (prop === "isImperial") return () => true;
    if (prop === "label") return () => "lb";
    if (prop === "fmtTenths") return (n) => String(n ?? 0);
    if (prop === "toTenths") return (n) => Number(n ?? 0);
    if (prop === "text") return (s) => s;
    return () => {};
  }
});

const UnitsCore = new Proxy({}, {
  get(target, prop) {
    if (window.UnitsCore && prop in window.UnitsCore) {
      const val = window.UnitsCore[prop];
      return typeof val === "function" ? val.bind(window.UnitsCore) : val;
    }
    return () => {};
  }
});

const WeightModeCore = new Proxy({}, {
  get(target, prop) {
    if (window.WeightModeCore && prop in window.WeightModeCore) {
      const val = window.WeightModeCore[prop];
      return typeof val === "function" ? val.bind(window.WeightModeCore) : val;
    }
    if (prop === "modeFor") return () => ({ id: 0, label: "", hasWeight: true });
    if (prop === "breakdown") return () => ({ showTotal: false, total: 0 });
    return () => {};
  }
});

const MovementsCore = new Proxy({}, {
  get(target, prop) {
    if (window.MovementsCore && prop in window.MovementsCore) {
      return window.MovementsCore[prop];
    }
    return { normalize: (s) => s };
  }
});

const ProgramIO = new Proxy({}, {
  get(target, prop) {
    if (window.ProgramIO && prop in window.ProgramIO) {
      return window.ProgramIO[prop];
    }
    return () => {};
  }
});

function getAppBase() {
  return window.location.pathname.includes("/gym") ? "/gym/" : "/";
}
function getApiBase() {
  return window.location.pathname.includes("/gym") ? "/gym/api" : "/api";
}

// localStorage can throw (blocked storage, private windows): never let it break the app.
const store = {
  get(k) { try { return localStorage.getItem(k); } catch { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch { /* session-only */ } },
  remove(k) { try { localStorage.removeItem(k); } catch { /* ignore */ } },
};
// Set to your Buy Me a Coffee / Ko-fi page URL to show the tip links; empty hides them.
const TIP_URL = "";
(() => {
  if (!TIP_URL) return;
  document.querySelectorAll(".tip-link").forEach((a) => { a.href = TIP_URL; a.hidden = false; });
  document.querySelectorAll(".tip-card").forEach((c) => { c.hidden = false; });
})();
const TOKEN_KEY = "innodigym_token";
const EMAIL_KEY = "innodigym_email";
const DEFAULT_COVER = "https://power.renhesports.com/filestore/power/course/COVER_RACK_1_4.jpg";

const $ = (id) => document.getElementById(id);

let currentCourse = null; // full object from /course/custom/detail (or a blank template), mutated in place
let currentProfile = null;
let actionLibrary = null; // lazy-loaded, cached full action list
let coverOptions = null;

function toast(msg, isErr) {
  const t = $("toast");
  t.textContent = msg;
  t.hidden = false;
  t.className = isErr ? "err" : "";
  clearTimeout(toast._t);
  toast._t = setTimeout(() => (t.hidden = true), 4000);
}

async function api(path, opts = {}) {
  const token = store.get(TOKEN_KEY) || window.INNO_TOKEN;
  const rawToken = token ? token.replace(/^Bearer\s+/i, "") : null;
  const headers = Object.assign(
    { "Content-Type": "application/json" },
    opts.headers || {},
    rawToken ? { Authorization: rawToken } : {}
  );
  const currentLang = typeof LANG === "function" ? LANG() : (window.LANG ? window.LANG() : "en");
  path += (path.includes("?") ? "&" : "?") + "languageId=" + encodeURIComponent(currentLang);
  const cleanPath = path.startsWith("/") ? path.slice(1) : path;
  const res = await fetch(getApiBase() + "/" + cleanPath, Object.assign({}, opts, { headers }));
  let body;
  try {
    body = await res.json();
  } catch {
    body = null;
  }
  if (!res.ok || (body && body.success === false)) {
    const msg = (body && (body.msg || body.proxyError)) || `HTTP ${res.status}`;
    const err = new Error(msg);
    err.body = body;
    throw err;
  }
  return body;
}

function escapeHtml(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

let currentEmail = null;
let activeTab = "programs";
function showLoggedIn(email) {
  $("login-section").hidden = true;
  $("tabs").hidden = false;
  $("main-section").hidden = false;
  currentEmail = email;
  $("userbar").innerHTML = `
    <span id="user-email">${escapeHtml(email)}</span>
    <button id="logout-btn" class="ios-logout-btn" title="${escapeHtml(t("Log out"))}" aria-label="${escapeHtml(t("Log out"))}">
      <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
      <span class="logout-label">${escapeHtml(t("Log out"))}</span>
    </button>
  `;
  $("logout-btn").onclick = () => {
    if (confirm(t("Are you sure you want to log out?"))) {
      store.remove(TOKEN_KEY);
      store.remove(EMAIL_KEY);
      location.reload();
    }
  };
}

// ---------- tabs ----------
function switchTab(name) {
  activeTab = name;
  document.querySelectorAll(".tab-panel").forEach((el) => (el.hidden = el.id !== `tab-${name}`));
  document.querySelectorAll(".tab-btn").forEach((b) => b.classList.toggle("active", b.dataset.tab === name));
  if (name === "programs") { if (window.CoursesUI) CoursesUI.show(); else { $("editor").hidden = true; $("list-view").hidden = false; loadPrograms(); } }
  if (name === "plans" && window.PlannerUI) PlannerUI.show();
  if (name === "actions") { if (window.MovementsUI) MovementsUI.show(); else loadActions(); }
  if (name === "history") { if (window.DashboardUI) DashboardUI.show(); else loadHistory(); }
  if (name === "fitness" && window.FitnessUI) FitnessUI.show();
  if (name === "profile") loadProfile();
}
document.querySelectorAll(".tab-btn").forEach((b) => b.addEventListener("click", () => switchTab(b.dataset.tab)));

// ---------- action library (shared: used by Programs editor + Actions tab) ----------
async function getActionLibrary() {
  if (actionLibrary) return actionLibrary;
  const res = await api("/action/list");
  actionLibrary = res.data || [];
  return actionLibrary;
}

let coverCategories = null;
async function getCoverCategories() {
  if (coverCategories) return coverCategories;
  const officialRack = [
    "https://power.renhesports.com/filestore/power/course/COVER_RACK_1_4.jpg",
    "https://power.renhesports.com/filestore/power/course/COVER_RACK_2_4.jpg",
    "https://power.renhesports.com/filestore/power/course/COVER_RACK_3_4.jpg",
    "https://power.renhesports.com/filestore/power/course/COVER_RACK_4_4.jpg",
    "https://power.renhesports.com/filestore/power/course/COVER_RACK_5_4.jpg",
    "https://power.renhesports.com/filestore/power/course/COVER_RACK_6_4.jpg",
    "https://power.renhesports.com/filestore/power/course/COVER_RACK_7_4.jpg",
    "https://power.renhesports.com/filestore/power/course/COVER_RACK_8_4.jpg"
  ];
  const movementArt = [];
  for (let i = 1; i <= 75; i++) {
    const num = String(i).padStart(3, "0");
    const v1Suffix = [36, 38, 39, 44, 46, 50, 52, 53, 54].includes(i) ? "_v1" : "";
    movementArt.push(`https://power.renhesports.com/filestore/power/course/LM${num}_common${v1Suffix}.png`);
  }
  coverCategories = {
    x1: officialRack,
    art: movementArt
  };
  return coverCategories;
}

async function getCoverOptions() {
  const cats = await getCoverCategories();
  return [...cats.x1, ...cats.art];
}

// ---------- PROGRAMS: list ----------
function formatAppleDate(dateStr) {
  if (!dateStr) return "";
  try {
    const parts = dateStr.split(" ")[0].split("-");
    if (parts.length === 3) {
      const y = parseInt(parts[0], 10);
      const m = parseInt(parts[1], 10) - 1;
      const d = parseInt(parts[2], 10);
      const dt = new Date(y, m, d);
      const now = new Date();
      if (dt.toDateString() === now.toDateString()) return t("Today");
      const yesterday = new Date(now);
      yesterday.setDate(yesterday.getDate() - 1);
      if (dt.toDateString() === yesterday.toDateString()) return t("Yesterday");
      return dt.toLocaleDateString(undefined, { month: "short", day: "numeric" });
    }
  } catch (e) {}
  return dateStr.split(" ")[0] || dateStr;
}

async function pushCourseToOpenGym(p, btn) {
  const isIconBtn = btn && (btn.classList.contains("ios-icon-btn") || btn.classList.contains("og-card-btn"));
  const origHtml = btn ? btn.innerHTML : "";
  if (btn) {
    btn.disabled = true;
    if (isIconBtn) {
      btn.classList.add("loading");
    } else {
      btn.textContent = t("Syncing…");
    }
  }
  try {
    const res = await fetch(getApiBase() + "/opengym/push-course", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ courseId: p.id })
    });
    const data = await res.json();
    if (data.success) {
      toast(`✔ OpenGym routine synced: "${data.routine_name}" (${data.exercises_count} exercises)`);
      if (btn) {
        if (isIconBtn) {
          btn.classList.remove("loading");
          btn.classList.add("synced");
          setTimeout(() => { btn.classList.remove("synced"); btn.disabled = false; }, 3000);
        } else {
          btn.textContent = "✔ Synced";
          setTimeout(() => { btn.innerHTML = origHtml; btn.disabled = false; }, 3000);
        }
      }
      updateOpenGymStatus();
    } else {
      toast(data.error || "Failed to push to OpenGym", true);
      if (btn) {
        btn.innerHTML = origHtml;
        btn.disabled = false;
        btn.classList.remove("loading");
      }
    }
  } catch (err) {
    toast("OpenGym error: " + err.message, true);
    if (btn) {
      btn.innerHTML = origHtml;
      btn.disabled = false;
      btn.classList.remove("loading");
    }
  }
}

let activeActionSheetProgram = null;
function openProgramActionSheet(p, anchorEl) {
  activeActionSheetProgram = p;
  const backdrop = $("ios-actionsheet-backdrop");
  if (!backdrop) return;

  const thumb = $("as-thumb");
  const title = $("as-title");
  const meta = $("as-meta");
  if (thumb) thumb.src = p.smallImg || DEFAULT_COVER;
  if (title) title.textContent = p.name;
  if (meta) meta.textContent = `${p.actionNum ?? "?"} ${t("exercises")} · ${p.duration || 0} min`;

  backdrop.hidden = false;
  requestAnimationFrame(() => backdrop.classList.add("open"));

  const close = () => {
    backdrop.classList.remove("open");
    setTimeout(() => { backdrop.hidden = true; activeActionSheetProgram = null; }, 200);
  };

  $("as-cancel").onclick = close;
  backdrop.onclick = (e) => {
    if (e.target === backdrop) close();
  };

  const handleKeydown = (e) => {
    if (e.key === "Escape" && !backdrop.hidden) {
      close();
      window.removeEventListener("keydown", handleKeydown);
    }
  };
  window.addEventListener("keydown", handleKeydown);

  $("as-edit").onclick = () => {
    close();
    openEditor(p.id);
  };
  $("as-opengym").onclick = () => {
    close();
    pushCourseToOpenGym(p, anchorEl);
  };
  $("as-clone").onclick = () => {
    close();
    ProgramIO.cloneOne(p, anchorEl);
  };
  $("as-export").onclick = () => {
    close();
    ProgramIO.exportOne(p, anchorEl);
  };
  $("as-delete").onclick = () => {
    close();
    deleteProgram(p.id, p.name);
  };
}

async function loadPrograms() {
  updateOpenGymStatus();
  const list = $("program-list");
  list.textContent = t("Loading…");
  try {
    const res = await api("/course/custom/list");
    const programs = res.data || [];
    const countBadge = $("programs-count-badge");
    if (countBadge) {
      countBadge.textContent = `${programs.length} ${programs.length === 1 ? t("routine") : t("routines")}`;
    }
    if (!programs.length) {
      list.innerHTML = `<p class="empty-state">${escapeHtml(t('No custom programs yet. Use "New Program" to create one.'))}</p>`;
      return;
    }
    list.innerHTML = "";
    for (const p of programs) {
      const el = document.createElement("div");
      el.className = "program-card";
      const dateText = formatAppleDate(p.updateTime);
      el.innerHTML = `
        <div class="card-left clickable" role="button" tabindex="0" aria-label="${escapeHtml(t("View summary of {name}", { name: p.name }))}">
          <img class="thumb" src="${escapeHtml(p.smallImg || DEFAULT_COVER)}" alt="" loading="lazy">
          <div class="card-info">
            <div class="name">${escapeHtml(p.name)}</div>
            <div class="card-meta-row">
              <span class="meta-pill"><svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path d="M6.5 6.5v11M17.5 6.5v11M3 9v6M21 9v6M6.5 12h11"/></svg>${escapeHtml(p.actionNum ?? "?")} ${t("exercises")}</span>
              <span class="meta-pill"><svg viewBox="0 0 24 24" width="11" height="11" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>${escapeHtml(p.duration || 0)}m</span>
              ${dateText ? `<span class="meta-date">${dateText}</span>` : ""}
            </div>
          </div>
        </div>
        <div class="card-actions">
          <button data-act="edit" data-id="${p.id}" class="ios-action-pill" title="${t("Edit")}">
            <svg viewBox="0 0 20 20" width="13" height="13" fill="currentColor" aria-hidden="true"><path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z"/></svg>
            <span>${t("Edit")}</span>
          </button>
          <button data-act="more" data-id="${p.id}" class="ios-icon-btn more-btn" title="${t("More actions")}" aria-label="${escapeHtml(t("More actions for {name}", { name: p.name }))}">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true"><circle cx="5" cy="12" r="2.2"/><circle cx="12" cy="12" r="2.2"/><circle cx="19" cy="12" r="2.2"/></svg>
          </button>
        </div>
      `;

      el.querySelector('[data-act="edit"]').onclick = (e) => {
        e.stopPropagation();
        openEditor(p.id);
      };
      el.querySelector('[data-act="more"]').onclick = (e) => {
        e.stopPropagation();
        openProgramActionSheet(p, e.currentTarget);
      };

      // click anywhere on the row (not the buttons / thumbnail) -> read-only summary card
      const left = el.querySelector(".card-left");
      const openSummary = () => window.CoursesUI && CoursesUI.openCustomDetail(p, left);
      left.addEventListener("click", (e) => {
        if (!e.target.closest("button, img.thumb")) openSummary();
      });
      left.addEventListener("keydown", (e) => {
        if ((e.key === "Enter" || e.key === " ") && e.target === left) {
          e.preventDefault();
          openSummary();
        }
      });
      el.querySelector("img.thumb").addEventListener("click", (e) => {
        e.stopPropagation();
        openLightbox(p.smallImg, null, p.name);
      });
      list.appendChild(el);
    }
  } catch (e) {
    list.innerHTML = `<p class="server-error">${escapeHtml(t("Failed to load: {msg}", { msg: e.message }))}</p>`;
  }
}

async function deleteProgram(id, name) {
  if (!confirm(t('Delete "{name}"? This cannot be undone.', { name }))) return;
  try {
    await api(`/course/custom/delete/${id}`, { method: "POST" });
    toast(t("Deleted."));
    loadPrograms();
  } catch (e) {
    toast(t("Delete failed: {msg}", { msg: e.message }), true);
  }
}

// ---------- PROGRAMS: editor (shared between create + edit) ----------
function blankCourseTemplate() {
  return {
    name: t("New Program"),
    level: 1,
    courseType: 1,
    smallImg: DEFAULT_COVER,
    detailsImg: DEFAULT_COVER,
    deviceCategory: 7,
    sportType: 2,
    muscleParts: "1",
    tags: null,
    custom: null,
    duration: 0,
    capacity: 0,
    heartRateMin: 0,
    heartRateMax: 0,
    actionNum: null,
    collected: false,
    description: "",
    deviceTypeList: ["35"],
    partsList: ["1"],
    warmUpStepList: [],
    mainStepList: [],
    relaxStepList: [],
  };
}

async function openEditor(id) {
  try {
    const res = await api(`/course/custom/detail?id=${id}`);
    currentCourse = res.data;
    await renderEditor(false);
    $("list-view").hidden = true;
    $("editor").hidden = false;
  } catch (e) {
    toast(t("Failed to load program: {msg}", { msg: e.message }), true);
  }
}

async function openNewProgramEditor() {
  currentCourse = blankCourseTemplate();
  await renderEditor(true);
  $("list-view").hidden = true;
  $("editor").hidden = false;
}

$("new-program-btn").addEventListener("click", openNewProgramEditor);

function updateCoverThumb() {
  $("cover-thumb").src = (currentCourse && currentCourse.smallImg) || DEFAULT_COVER;
}

// ---------- cover picker modal ----------
let coverModalOpener = null;
let selectedCoverUrl = null;
let activeCoverCategory = "x1";

async function openCoverModal() {
  coverModalOpener = document.activeElement;
  const cats = await getCoverCategories();
  selectedCoverUrl = (currentCourse && currentCourse.smallImg) || DEFAULT_COVER;

  // Determine starting category
  if (cats.art && cats.art.includes(selectedCoverUrl)) {
    activeCoverCategory = "art";
  } else {
    activeCoverCategory = "x1";
  }

  updateCoverPreview(selectedCoverUrl);
  renderCoverCategoryTabs();
  renderCoverGrid();

  $("cover-modal-backdrop").hidden = false;
  $("cover-modal-close-btn").focus();
}

function updateCoverPreview(url) {
  selectedCoverUrl = url;
  const img = $("cover-preview-img");
  const label = $("cover-preview-label");
  if (img) img.src = url;
  if (label) {
    if (url.includes("COVER_RACK")) {
      const match = url.match(/COVER_RACK_(\d+)/);
      label.textContent = match ? `X1 Setup #${match[1]} (Official Photo)` : "Official X1 Setup";
    } else if (url.includes("LM")) {
      const match = url.match(/LM(\d+)/);
      label.textContent = match ? `Movement Art #${parseInt(match[1])}` : "Movement Artwork";
    } else {
      label.textContent = "Selected Cover";
    }
  }
}

function renderCoverCategoryTabs() {
  document.querySelectorAll(".cover-tab-btn").forEach((btn) => {
    const cat = btn.dataset.cat;
    btn.classList.toggle("active", cat === activeCoverCategory);
    btn.onclick = () => {
      activeCoverCategory = cat;
      renderCoverCategoryTabs();
      renderCoverGrid();
    };
  });
}

async function renderCoverGrid() {
  const grid = $("cover-grid");
  if (!grid) return;
  grid.innerHTML = "";
  const cats = await getCoverCategories();
  const list = cats[activeCoverCategory] || cats.x1;

  for (const url of list) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "cover-option" + (url === selectedCoverUrl ? " selected" : "");
    btn.setAttribute("aria-label", "Select cover photo");
    btn.setAttribute("title", "Click to preview, double-click to select");

    const img = document.createElement("img");
    img.src = url;
    img.alt = "";
    img.loading = "lazy";
    btn.appendChild(img);

    // Single click / tap -> update featured preview
    btn.onclick = () => {
      updateCoverPreview(url);
      grid.querySelectorAll(".cover-option").forEach((el) => el.classList.remove("selected"));
      btn.classList.add("selected");
    };

    // Double click -> select and close
    btn.ondblclick = () => {
      applyCoverSelection(url);
    };

    grid.appendChild(btn);
  }
}

function applyCoverSelection(url) {
  if (currentCourse) {
    currentCourse.smallImg = url;
    currentCourse.detailsImg = url;
  }
  updateCoverThumb();
  closeCoverModal();
}

function closeCoverModal() {
  if ($("cover-modal-backdrop").hidden) return;
  $("cover-modal-backdrop").hidden = true;
  if (coverModalOpener && coverModalOpener.focus) coverModalOpener.focus();
  coverModalOpener = null;
}

$("cover-thumb-btn").addEventListener("click", openCoverModal);
$("cover-modal-close-btn").addEventListener("click", closeCoverModal);
$("cover-modal-backdrop").addEventListener("click", (e) => {
  if (e.target.id === "cover-modal-backdrop") closeCoverModal();
});

// Fullscreen zoom button on featured preview
if ($("cover-zoom-btn")) {
  $("cover-zoom-btn").addEventListener("click", (e) => {
    e.stopPropagation();
    if (selectedCoverUrl) openLightbox(selectedCoverUrl, null, "Cover Photo Preview");
  });
}
if ($("cover-preview-wrap")) {
  $("cover-preview-wrap").addEventListener("click", () => {
    if (selectedCoverUrl) openLightbox(selectedCoverUrl, null, "Cover Photo Preview");
  });
}

// "Use This Cover" button
if ($("cover-confirm-btn")) {
  $("cover-confirm-btn").addEventListener("click", () => {
    if (selectedCoverUrl) applyCoverSelection(selectedCoverUrl);
  });
}

// Expand button in Program Editor
if ($("cover-expand-btn")) {
  $("cover-expand-btn").addEventListener("click", () => {
    const currentImg = (currentCourse && currentCourse.smallImg) || DEFAULT_COVER;
    openLightbox(currentImg, null, (currentCourse && currentCourse.name) || "Cover Photo");
  });
}
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !$("lightbox-backdrop").hidden) { e.stopImmediatePropagation(); closeLightbox(); }
  else if (e.key === "Escape" && !$("cover-modal-backdrop").hidden) closeCoverModal();
});

async function renderEditor(isNew) {
  $("editor-title").textContent = isNew ? t("New Program") : t("Edit Program");
  $("delete-program-btn").style.display = isNew ? "none" : "";
  $("edit-name").value = currentCourse.name || "";

  updateCoverThumb();

  renderStepsTable();
}

// Weight input + read-only weight-mode badge (from sideNum: Per side / Combined / No weight).
// A step stores exactly what the input shows; sideNum 0 has no weight, so the input is
// disabled (its stored value is left untouched).
// Same badge under the exercise name: shown instead of the one in the weight cell on narrow
// screens (the 4-column card grid is too tight for "Combined"); hidden on desktop by CSS.
function weightModeInline(step) {
  const mode = WeightModeCore.modeFor(step.sideNum);
  const badge = mode.label ? `<span class="wm-badge wm-badge-inline wm-${mode.key}" aria-hidden="true">${escapeHtml(t(mode.label))}</span>` : "";
  // Combined: same live total under the name on narrow screens (aria-hidden; the one in the
  // weight cell stays the accessible, announced copy and is only visually hidden there).
  const total = mode.key === "combined" ? `<span class="wm-total wm-total-inline" aria-hidden="true">${escapeHtml(combinedTotalText(step))}</span>` : "";
  return badge + total;
}

// Combined (sideNum 2): both cables work at once, the entered number is the resistance on
// EACH cable and the machine's workout screen shows the total. Readout is computed from the
// stored tenths (see WeightModeCore.totalTenths) in the account unit.
function combinedTotalText(step) {
  const b = WeightModeCore.breakdown(step.sideNum, step.sideWeight);
  return b.showTotal ? t("×2 cables = {total} total", { total: `${Units.fmtTenths(b.total)} ${Units.label()}` }) : "";
}

function weightCell(step, i) {
  const mode = WeightModeCore.modeFor(step.sideNum);
  const combined = mode.key === "combined";
  const badge = mode.label
    ? `<span class="wm-badge wm-${mode.key}" id="step-${i}-wm"${combined ? ` title="${escapeHtml(t("Resistance on each cable; both cables work at once"))}"` : ""}>${escapeHtml(t(mode.label))}</span>`
    : "";
  const total = combined ? `<span class="wm-total" id="step-${i}-total" aria-live="polite">${escapeHtml(combinedTotalText(step))}</span>` : "";
  const aria = Units.text(t(combined ? "Load per cable (kg)" : "Load (kg)"));
  const describedBy = [mode.label ? `step-${i}-wm` : "", combined ? `step-${i}-total` : ""].filter(Boolean).join(" ");
  return `<input type="number" min="0" step="0.1" id="step-${i}-sideWeight" name="step-${i}-sideWeight" data-field="sideWeight" aria-label="${escapeHtml(aria)}"${combined ? ` title="${escapeHtml(aria)}"` : ""}${describedBy ? ` aria-describedby="${describedBy}"` : ""}${mode.hasWeight ? "" : " disabled"} value="${Units.fmtTenths(step.sideWeight ?? 0)}">${badge}${total}`;
}

function renderStepsTable() {
  const body = $("steps-body");
  body.innerHTML = "";
  const total = (currentCourse.mainStepList || []).length;
  (currentCourse.mainStepList || []).forEach((step, i) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td class="reorder">
        <button type="button" class="reorder-btn drag-handle" data-reorder="handle" aria-label="${escapeHtml(t("Drag to reorder step {n} (or use arrow keys)", { n: i + 1 }))}" title="${escapeHtml(t("Drag to reorder"))}">⠿</button>
      </td>
      <td class="thumb">${step.picUrl ? `<img src="${escapeHtml(step.picUrl)}" alt="">` : ""}</td>
      <td class="num">${i + 1}</td>
      <td class="action-name">${escapeHtml(step.actionName || "")}${weightModeInline(step)}</td>
      <td class="field" data-label="${t("Reps")}"><input type="number" min="0" id="step-${i}-count" name="step-${i}-count" data-field="count" aria-label="${t("Reps")}" value="${step.count ?? 0}"></td>
      <td class="field" data-label="${escapeHtml(Units.text(t("Load (kg)")))}">${weightCell(step, i)}</td>
      <td class="field" data-label="${t("Rest (s)")}"><input type="number" min="0" id="step-${i}-restTime" name="step-${i}-restTime" data-field="restTime" aria-label="${t("Rest (s)")}" value="${step.restTime ?? 0}"></td>
      <td class="field" data-label="${t("Sets")}"><input type="number" min="0" id="step-${i}-groupNum" name="step-${i}-groupNum" data-field="groupNum" aria-label="${t("Sets")}" value="${step.groupNum ?? 0}"></td>
      <td class="row-actions">
        <button type="button" class="secondary row-menu-btn" aria-haspopup="menu" aria-expanded="false" aria-label="${escapeHtml(t("Actions for {name}", { name: step.actionName || t("step {n}", { n: i + 1 }) }))}" title="${escapeHtml(t("Row actions"))}">⋯</button>
      </td>
    `;
    const thumb = tr.querySelector("td.thumb img");
    if (thumb) thumb.addEventListener("click", () => openLightbox(step.picUrl, step.videoUrl, step.actionName));
    tr.querySelectorAll("input").forEach((input) => {
      input.addEventListener("input", () => {
        const val = Number(input.value);
        if (!Number.isFinite(val)) return;
        // sideWeight is stored by the server in tenths of a kg (50 == 5.0kg); the input
        // shows/accepts the account unit (kg or lb), so convert back to tenths of kg here.
        step[input.dataset.field] = input.dataset.field === "sideWeight" ? Units.toTenths(val) : val;
        if (input.dataset.field === "sideWeight") {
          tr.querySelectorAll(".wm-total").forEach((el) => { el.textContent = combinedTotalText(step); });
        }
      });
    });
    const menuBtn = tr.querySelector(".row-menu-btn");
    menuBtn.addEventListener("click", () => toggleRowMenu(i, menuBtn, total));
    setupReorder(tr, i);
    body.appendChild(tr);
  });
}

// Move step `from` to index `to`, renumber, re-render. `focusKind` ("up" | "down" |
// "handle") keeps focus on the matching control of the moved row.
function moveStep(from, to, focusKind) {
  const list = currentCourse && currentCourse.mainStepList;
  if (!list || from === to || from < 0 || to < 0 || from >= list.length || to >= list.length) return;
  const x = window.scrollX, y = window.scrollY;
  const [item] = list.splice(from, 1);
  list.splice(to, 0, item);
  list.forEach((s, j) => (s.sort = j + 1));
  renderStepsTable();
  window.scrollTo(x, y);
  if (focusKind) {
    const row = $("steps-body").children[to];
    const btn = row && row.querySelector(`[data-reorder="${focusKind}"]`);
    if (btn) {
      btn.focus({ preventScroll: true });
      if (btn.scrollIntoView) btn.scrollIntoView({ block: "nearest" });
    }
  }
}

function removeStep(i) {
  currentCourse.mainStepList.splice(i, 1);
  currentCourse.mainStepList.forEach((s, j) => (s.sort = j + 1));
  renderStepsTable();
}

// One shared popover for the per-row "⋯" menu. Lives on <body> with fixed
// positioning so the table's overflow container can't clip it.
let rowMenu = null;
function closeRowMenu(restoreFocus) {
  if (!rowMenu) return;
  const { el, btn } = rowMenu;
  rowMenu = null;
  el.remove();
  btn.setAttribute("aria-expanded", "false");
  document.removeEventListener("pointerdown", onRowMenuOutside, true);
  window.removeEventListener("scroll", onRowMenuDismiss, true);
  window.removeEventListener("resize", onRowMenuDismiss);
  if (restoreFocus && btn.isConnected) btn.focus({ preventScroll: true });
}
function onRowMenuOutside(e) {
  if (rowMenu && !rowMenu.el.contains(e.target) && !rowMenu.btn.contains(e.target)) closeRowMenu(false);
}
function onRowMenuDismiss() { closeRowMenu(false); }
function toggleRowMenu(i, btn, total) {
  if (rowMenu && rowMenu.btn === btn) { closeRowMenu(true); return; }
  closeRowMenu(false);
  const el = document.createElement("div");
  el.className = "row-menu";
  el.setAttribute("role", "menu");
  const items = [
    ["up", t("Move up"), i === 0, () => moveStep(i, i - 1, "handle")],
    ["down", t("Move down"), i === total - 1, () => moveStep(i, i + 1, "handle")],
    ["duplicate", t("Duplicate"), false, () => duplicateStep(i)],
    ["remove", t("Remove"), false, () => removeStep(i)],
  ];
  items.forEach(([key, label, disabled, fn]) => {
    const b = document.createElement("button");
    b.type = "button";
    b.setAttribute("role", "menuitem");
    b.className = "row-menu-item" + (key === "remove" ? " danger" : "");
    b.textContent = label;
    b.disabled = disabled;
    b.addEventListener("click", () => { closeRowMenu(false); fn(); });
    el.appendChild(b);
  });
  el.addEventListener("keydown", (e) => {
    const enabled = Array.from(el.querySelectorAll("button:not(:disabled)"));
    const k = enabled.indexOf(document.activeElement);
    if (e.key === "Escape") { e.preventDefault(); closeRowMenu(true); }
    else if (e.key === "ArrowDown") { e.preventDefault(); enabled[(k + 1) % enabled.length].focus(); }
    else if (e.key === "ArrowUp") { e.preventDefault(); enabled[(k - 1 + enabled.length) % enabled.length].focus(); }
    else if (e.key === "Tab") closeRowMenu(true);
  });
  document.body.appendChild(el);
  const r = btn.getBoundingClientRect();
  const h = el.offsetHeight, w = el.offsetWidth;
  const top = r.bottom + 4 + h > window.innerHeight ? Math.max(8, r.top - 4 - h) : r.bottom + 4;
  el.style.top = top + "px";
  el.style.left = Math.max(8, Math.min(r.right - w, window.innerWidth - w - 8)) + "px";
  btn.setAttribute("aria-expanded", "true");
  rowMenu = { el, btn };
  document.addEventListener("pointerdown", onRowMenuOutside, true);
  window.addEventListener("scroll", onRowMenuDismiss, true);
  window.addEventListener("resize", onRowMenuDismiss);
  const first = el.querySelector("button:not(:disabled)");
  if (first) first.focus({ preventScroll: true });
}

function setupReorder(tr, i) {
  const handle = tr.querySelector('[data-reorder="handle"]');
  handle.addEventListener("keydown", (e) => {
    if (e.key === "ArrowUp") { e.preventDefault(); moveStep(i, i - 1, "handle"); }
    else if (e.key === "ArrowDown") { e.preventDefault(); moveStep(i, i + 1, "handle"); }
  });

  // Pointer-event drag (mouse + touch + pen); only the handle starts a drag so
  // number inputs keep normal behaviour.
  let drag = null;
  const rows = () => Array.from($("steps-body").children);
  const clearMarks = () => rows().forEach((r) => r.classList.remove("drop-before", "drop-after"));
  const slotAt = (clientY) => {
    // insertion slot 0..n based on row midpoints
    const rs = rows();
    for (let k = 0; k < rs.length; k++) {
      const r = rs[k].getBoundingClientRect();
      if (clientY < r.top + r.height / 2) return k;
    }
    return rs.length;
  };
  handle.addEventListener("pointerdown", (e) => {
    if (e.button !== undefined && e.button !== 0) return;
    e.preventDefault();
    drag = { slot: i };
    handle.setPointerCapture(e.pointerId);
    tr.classList.add("dragging");
    document.body.classList.add("reordering");
  });
  handle.addEventListener("pointermove", (e) => {
    if (!drag) return;
    drag.slot = slotAt(e.clientY);
    clearMarks();
    const rs = rows();
    if (drag.slot < rs.length) rs[drag.slot].classList.add("drop-before");
    else rs[rs.length - 1].classList.add("drop-after");
    // auto-scroll near viewport edges
    if (e.clientY < 60) window.scrollBy(0, -12);
    else if (e.clientY > window.innerHeight - 60) window.scrollBy(0, 12);
  });
  const end = (e, cancel) => {
    if (!drag) return;
    const slot = drag.slot;
    drag = null;
    clearMarks();
    tr.classList.remove("dragging");
    document.body.classList.remove("reordering");
    if (cancel) return;
    const to = slot > i ? slot - 1 : slot;
    if (to !== i) moveStep(i, to, "handle");
  };
  handle.addEventListener("pointerup", (e) => end(e, false));
  handle.addEventListener("pointercancel", (e) => end(e, true));
}

function duplicateStep(i) {
  const list = currentCourse.mainStepList;
  if (!list[i]) return;
  const copy = structuredClone(list[i]);
  // Server-assigned identity: steps added from the library carry neither, so
  // strip them and let the server treat the clone as a new step.
  delete copy.id;
  delete copy.courseId;
  list.splice(i + 1, 0, copy);
  list.forEach((s, j) => (s.sort = j + 1));
  renderStepsTable();
  const row = $("steps-body").children[i + 1];
  if (!row) return;
  row.classList.add("row-new");
  setTimeout(() => row.classList.remove("row-new"), 1500);
  const reps = row.querySelector('input[data-field="count"]');
  if (reps) {
    reps.focus({ preventScroll: true });
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    row.scrollIntoView({ block: "nearest", behavior: reduce ? "auto" : "smooth" });
  }
}

function addStepFromAction(a) {
  // Action-library sideWeight is plain kg (e.g. "5"); course-step sideWeight is
  // in tenths of a kg (e.g. 50 == 5.0kg) — confirmed by comparing the two for
  // the same action. Convert on the way in or saved programs end up 10x too light.
  const libKg = typeof a.sideWeight === "string" ? parseFloat(a.sideWeight) : a.sideWeight;
  const sideWeight = Number.isFinite(libKg) ? Math.round(libKg * 10) : 50;
  currentCourse.mainStepList.push({
    sort: currentCourse.mainStepList.length + 1,
    actionLibraryId: a.id,
    actionName: a.name,
    actionNo: a.actionNo,
    actionType: a.actionType,
    picUrl: a.picUrl,
    videoUrl: a.videoUrl,
    stage: 2,
    count: 12,
    consume: a.consume ?? null,
    sideNum: a.sideNum ?? 0,
    countType: a.countType ?? 1,
    sideWeight,
    muscleGroups: a.muscleGroups,
    muscleParts: a.muscleParts,
    trainingPoint: a.trainingPoint,
    reqParts: a.reqParts,
    restTime: 30,
    groupNum: 1,
    mode: 0,
    modeParam: "{}",
    breathTip: a.breathTip,
    custom: false,
    duration: 12,
  });
  renderStepsTable();
}

async function saveProgram() {
  if (!currentCourse) return;
  currentCourse.name = $("edit-name").value;
  // Recompute rough aggregates so the list view isn't wildly stale. Not an exact
  // formula match to the server's own calculation, purely cosmetic.
  currentCourse.duration = currentCourse.mainStepList.reduce((s, st) => s + (st.duration || 1), 0);
  currentCourse.capacity = currentCourse.mainStepList.reduce((s, st) => s + (st.consume || 0) * 10, 0);

  const status = $("save-status");
  status.textContent = t("Saving…");
  status.className = "";
  try {
    await api("/course/custom/save", { method: "POST", body: JSON.stringify(currentCourse) });
    status.textContent = t("Saved.");
    status.className = "ok";
    toast(t("Saved — {name}", { name: currentCourse.name }));
    $("editor").hidden = true;
    $("list-view").hidden = false;
    loadPrograms();
  } catch (e) {
    status.textContent = t("Failed: {msg}", { msg: e.message });
    status.className = "err";
    toast(t("Save failed: {msg}", { msg: e.message }), true);
  }
}

// ---------- image/video lightbox (shared by every thumbnail in the app) ----------
let lightboxOpener = null;
function openLightbox(picUrl, videoUrl, title) {
  if (!picUrl && !videoUrl) return;
  $("lightbox-title").textContent = title || "";
  const media = $("lightbox-media");
  if (videoUrl) {
    media.innerHTML = `<video controls autoplay ${picUrl ? `poster="${escapeHtml(picUrl)}"` : ""}>
      <source src="${escapeHtml(videoUrl)}" type="video/mp4"></video>`;
  } else {
    media.innerHTML = `<img src="${escapeHtml(picUrl)}" alt="">`;
  }
  lightboxOpener = document.activeElement;
  $("lightbox-backdrop").hidden = false;
  $("lightbox-close-btn").focus({ preventScroll: true });
}
function closeLightbox() {
  $("lightbox-backdrop").hidden = true;
  $("lightbox-media").innerHTML = ""; // stop any playing video
  if (lightboxOpener && lightboxOpener.isConnected && lightboxOpener.focus) lightboxOpener.focus({ preventScroll: true });
  lightboxOpener = null;
}
$("lightbox-close-btn").addEventListener("click", closeLightbox);
$("lightbox-backdrop").addEventListener("click", (e) => {
  if (e.target.id === "lightbox-backdrop") closeLightbox();
});

// ---------- action picker modal ----------
// Inferred from the data itself (there's no labeled lookup in the API): grouped
// all 268 library actions by their numeric muscleParts id against exercise names
// (e.g. id 1 only ever appears on chest presses/flys) and matched the result
// against the body-part strings the app itself ships in its translations.
const MUSCLE_GROUPS = [
  { id: "1", label: "Chest" },
  { id: "2", label: "Shoulder" },
  { id: "3", label: "Back" },
  { id: "4", label: "Arm" },
  { id: "5", label: "Hips" },
  { id: "6", label: "Legs" },
  { id: "7", label: "Abdomen" },
  { id: "8", label: "Full-Body" },
];

// Muscle-group names live in the language packs as "muscle.<id>"; English is the fallback label.
function muscleName(g) {
  const s = t("muscle." + g.id);
  return s === "muscle." + g.id ? g.label : s;
}

let pickerResults = [];
let pickerActiveGroups = new Set();

async function openActionPicker() {
  $("action-picker-backdrop").hidden = false;
  $("picker-search").value = "";
  pickerActiveGroups = new Set();
  $("picker-results").innerHTML = t("Loading…");
  try {
    pickerResults = await getActionLibrary();
    renderPickerChips();
    applyPickerFilter();
    $("picker-search").focus();
  } catch (e) {
    $("picker-results").innerHTML = `<p class="server-error">${escapeHtml(e.message)}</p>`;
  }
}

function renderPickerChips() {
  const el = $("picker-chips");
  el.innerHTML = "";
  const allChip = document.createElement("button");
  allChip.type = "button";
  allChip.className = "chip" + (pickerActiveGroups.size === 0 ? " active" : "");
  allChip.textContent = t("All");
  allChip.onclick = () => {
    pickerActiveGroups.clear();
    renderPickerChips();
    applyPickerFilter();
  };
  el.appendChild(allChip);
  for (const g of MUSCLE_GROUPS) {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "chip" + (pickerActiveGroups.has(g.id) ? " active" : "");
    chip.textContent = muscleName(g);
    chip.onclick = () => {
      if (pickerActiveGroups.has(g.id)) pickerActiveGroups.delete(g.id);
      else pickerActiveGroups.add(g.id);
      renderPickerChips();
      applyPickerFilter();
    };
    el.appendChild(chip);
  }
}

function applyPickerFilter() {
  const norm = MovementsCore.normalize;
  const q = norm($("picker-search").value.trim());
  let items = pickerResults;
  if (pickerActiveGroups.size) {
    items = items.filter((a) => (a.muscleParts || "").split(",").some((p) => pickerActiveGroups.has(p)));
  }
  if (q) {
    items = items.filter((a) => norm(a.name || "").includes(q));
  }
  renderPickerResults(items);
}

function renderPickerResults(items) {
  const el = $("picker-results");
  if (!items.length) {
    el.innerHTML = `<p class="empty-state">${t("No matches.")}</p>`;
    return;
  }
  el.innerHTML = "";
  for (const a of items.slice(0, 80)) {
    const row = document.createElement("div");
    row.className = "picker-row";
    row.innerHTML = `
      <img src="${escapeHtml(a.picUrl || "")}" alt="">
      <div><div>${escapeHtml(a.name)}</div><div class="meta">${escapeHtml((a.muscleParts || ""))}</div></div>
    `;
    row.onclick = () => {
      addStepFromAction(a);
      $("action-picker-backdrop").hidden = true;
    };
    row.querySelector("img").addEventListener("click", (e) => {
      e.stopPropagation();
      openLightbox(a.picUrl, a.videoUrl, a.name);
    });
    el.appendChild(row);
  }
}
$("add-action-btn").addEventListener("click", openActionPicker);
$("picker-close-btn").addEventListener("click", () => ($("action-picker-backdrop").hidden = true));
$("action-picker-backdrop").addEventListener("click", (e) => {
  if (e.target.id === "action-picker-backdrop") $("action-picker-backdrop").hidden = true;
});
let pickerSearchTimer = null;
$("picker-search").addEventListener("input", () => {
  clearTimeout(pickerSearchTimer);
  pickerSearchTimer = setTimeout(applyPickerFilter, 150);
});

$("delete-program-btn").addEventListener("click", async () => {
  if (!currentCourse || !currentCourse.id) return;
  if (!confirm(t('Delete "{name}"? This cannot be undone.', { name: currentCourse.name }))) return;
  try {
    await api(`/course/custom/delete/${currentCourse.id}`, { method: "POST" });
    toast(t("Deleted."));
    $("editor").hidden = true;
    $("list-view").hidden = false;
    loadPrograms();
  } catch (e) {
    toast(t("Delete failed: {msg}", { msg: e.message }), true);
  }
});

// ---------- ACTIONS tab (your custom actions, separate from the shared library) ----------
async function loadActions() {
  const list = $("actions-list");
  list.textContent = t("Loading…");
  try {
    // The default /action/list omits custom actions; they only come back with ?custom=true.
    const res = await api("/action/list?custom=true");
    const custom = (res.data || []).filter((a) => a.custom);
    if (!custom.length) {
      list.innerHTML = `<p class="empty-state">${escapeHtml(t("No custom actions yet. Add one below."))}</p>`;
      return;
    }
    list.innerHTML = "";
    for (const a of custom) {
      const el = document.createElement("div");
      el.className = "action-card";
      el.innerHTML = `
        <div class="card-left">
          <img class="thumb" src="${escapeHtml(a.picUrl || "")}" alt="">
          <div><div class="name">${escapeHtml(a.name)}</div><div class="meta">id ${a.id}${WeightModeCore.modeFor(a.sideNum).label ? ` · ${escapeHtml(t(WeightModeCore.modeFor(a.sideNum).label))}` : ""}</div></div>
        </div>
        <button class="secondary" data-id="${a.id}">${t("Delete")}</button>
      `;
      el.querySelector("button").onclick = () => deleteAction(a.id);
      el.querySelector("img.thumb").addEventListener("click", () => openLightbox(a.picUrl, a.videoUrl, a.name));
      list.appendChild(el);
    }
  } catch (e) {
    list.innerHTML = `<p class="server-error">${escapeHtml(t("Failed to load: {msg}", { msg: e.message }))}</p>`;
  }
}

async function deleteAction(id) {
  if (!confirm(t("Delete this custom action?"))) return;
  try {
    await api(`/action/delete/${id}`, { method: "POST" });
    toast(t("Deleted."));
    loadActions();
  } catch (e) {
    toast(t("Delete failed: {msg}", { msg: e.message }), true);
  }
}

$("action-add-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const status = $("action-add-status");
  const body = {
    name: $("new-action-name").value.trim(),
    countType: Number($("new-action-counttype").value),
    consume: Number($("new-action-consume").value) || 0,
    actionType: 3,
  };
  if (!body.name) return;
  status.textContent = t("Adding…");
  try {
    const res = await api("/action/add", { method: "POST", body: JSON.stringify(body) });
    status.textContent = t("Added (id {id}).", { id: res.data });
    toast(t("Action added."));
    $("action-add-form").reset();
    actionLibrary = null; // invalidate cache so the new action shows up in the picker too
    loadActions();
  } catch (e) {
    status.textContent = t("Failed: {msg}", { msg: e.message });
    toast(t("Add failed: {msg}", { msg: e.message }), true);
  }
});

// ---------- HISTORY ----------
async function loadHistory() {
  const list = $("history-list");
  list.textContent = t("Loading…");
  const end = new Date();
  const start = new Date(end.getTime() - 180 * 86400000);
  const fmt = (d) => d.toISOString().slice(0, 19).replace("T", " ");
  try {
    const res = await api(
      `/sport/record/list?startTime=${encodeURIComponent(fmt(start))}&endTime=${encodeURIComponent(fmt(end))}&size=50`
    );
    const records = res.data || [];
    if (!records.length) {
      list.innerHTML = `<p class="empty-state">${escapeHtml(t("No workout records in the last 180 days."))}</p>`;
      return;
    }
    list.innerHTML = "";
    for (const r of records) {
      const el = document.createElement("div");
      el.className = "record-card";
      el.innerHTML = `
        <div>
          <div class="name">${escapeHtml(r.name || t("(unnamed)"))}</div>
          <div class="meta">${r.startTime} · ${r.duration}s · ${r.consume} kcal</div>
        </div>
        <button class="secondary" data-id="${r.sportRecordId}">${t("Delete")}</button>
      `;
      el.querySelector("button").onclick = () => deleteRecord(r.sportRecordId);
      list.appendChild(el);
    }
  } catch (e) {
    list.innerHTML = `<p class="server-error">${escapeHtml(t("Failed to load: {msg}", { msg: e.message }))}</p>`;
  }
}

async function deleteRecord(id) {
  if (!confirm(t("Delete this workout record? This cannot be undone."))) return;
  try {
    await api(`/sport/record/delete/${id}`, { method: "POST" });
    toast(t("Deleted."));
    loadHistory();
  } catch (e) {
    toast(t("Delete failed: {msg}", { msg: e.message }), true);
  }
}

// ---------- FITNESS ---------- (see fitness.js / fitness-core.js)

// ---------- PROFILE ----------
async function loadProfile() {
  const status = $("profile-status");
  status.textContent = "";
  try {
    const res = await api("/app/getInfo");
    currentProfile = res.data;
    Units.set(UnitsCore.unitFromProfile(currentProfile));
    $("p-nickName").value = currentProfile.nickName || "";
    $("p-birthday").value = currentProfile.birthday || "";
    $("p-sex").value = currentProfile.sex ?? 1;
    $("p-unit").value = currentProfile.unit ?? 0;
    $("p-trainingTime").value = currentProfile.trainingTime ?? "";
    $("p-targetWeight").value = profileKgShown(currentProfile.targetWeight);
    $("p-height").value = currentProfile.height ?? "";
    $("p-weight").value = profileKgShown(currentProfile.weight);
  } catch (e) {
    status.textContent = t("Failed to load profile: {msg}", { msg: e.message });
    status.className = "err";
  }
}

// Profile weights are plain kg from the API. Metric shows them untouched; Imperial shows lb.
const profileKgShown = (kg) => (kg == null ? "" : Units.isImperial() ? UnitsCore.kgToDisplay(kg, Units.get()) : kg);

// The target weight input shows the unit the profile was LOADED with (Units.get()), not the
// Units dropdown, so a unit change saved in the same submit never reinterprets the number.
// Untouched input -> send the stored kg value as is (no conversion round-trip noise).
function targetWeightKg() {
  const typed = Number($("p-targetWeight").value);
  if (!Units.isImperial()) return typed;
  const orig = currentProfile ? currentProfile.targetWeight : null;
  if (orig != null && typed === UnitsCore.kgToDisplay(orig, Units.get())) return orig;
  return UnitsCore.displayToKg(typed, Units.get());
}

$("profile-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const status = $("profile-status");
  // Confirmed: the server 500s on several fields (height/weight/trainingConsume) no
  // matter what, and on a full combined-object update. Sending one changed field per
  // request is what's confirmed to work reliably.
  const fields = {
    nickName: $("p-nickName").value,
    birthday: $("p-birthday").value,
    sex: Number($("p-sex").value),
    unit: Number($("p-unit").value),
    trainingTime: Number($("p-trainingTime").value),
    targetWeight: targetWeightKg(),
  };
  const changed = Object.entries(fields).filter(([k, v]) => String(currentProfile?.[k] ?? "") !== String(v));
  if (!changed.length) {
    status.textContent = t("Nothing changed.");
    status.className = "";
    return;
  }
  status.textContent = t("Saving…");
  const failures = [];
  for (const [k, v] of changed) {
    try {
      await api("/app/updateInfo", { method: "POST", body: JSON.stringify({ [k]: v }) });
    } catch (e) {
      failures.push(`${k}: ${e.message}`);
    }
  }
  if (failures.length) {
    status.textContent = t("Some fields failed to save: {list}", { list: failures.join("; ") });
    status.className = "err";
    toast(t("Profile partially saved — see details."), true);
  } else {
    status.textContent = t("Saved.");
    status.className = "ok";
    toast(t("Profile saved."));
  }
  loadProfile();
});

// ---------- login / init ----------
async function login(email, password) {
  store.remove("innodigym_manual_logout");
  const currentLang = typeof LANG === "function" ? LANG() : (window.LANG ? window.LANG() : "en");
  const res = await api("/app/login", {
    method: "POST",
    body: JSON.stringify({
      accountType: 2, accountVal: email, password,
      device: "Web", deviceId: "innodigym-web-editor", languageId: currentLang,
    }),
  });
  if (res && res.data && res.data.token) {
    store.set(TOKEN_KEY, res.data.token);
    store.set(EMAIL_KEY, email);
    fetch(getApiBase() + "/token", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token: res.data.token, email: email })
    }).catch(() => {});
  } else {
    throw new Error((res && (res.msg || res.proxyError)) || "Login failed — please check your credentials.");
  }
}

$("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = $("login-email").value.trim();
  const password = $("login-password").value;
  const err = $("login-error");
  err.hidden = true;
  try {
    if (!password && (window.INNO_TOKEN || store.get(TOKEN_KEY))) {
      const tok = window.INNO_TOKEN || store.get(TOKEN_KEY);
      const em = email || window.INNO_EMAIL || "TheITGuru";
      store.remove("innodigym_manual_logout");
      store.set(TOKEN_KEY, tok);
      store.set(EMAIL_KEY, em);
      try { Units.load(api); } catch (_) {}
      showLoggedIn(em);
      switchTab("programs");
      return;
    }
    await login(email, password);
    try { Units.load(api); } catch (_) {}
    showLoggedIn(email);
    switchTab("programs");
  } catch (ex) {
    err.textContent = ex.message;
    err.hidden = false;
  }
});

const autoBtn = $("auto-login-btn");
if (autoBtn) {
  autoBtn.addEventListener("click", () => {
    store.remove("innodigym_manual_logout");
    const tok = window.INNO_TOKEN || store.get(TOKEN_KEY);
    const em = window.INNO_EMAIL || store.get(EMAIL_KEY) || "TheITGuru";
    if (tok) {
      store.set(TOKEN_KEY, tok);
      store.set(EMAIL_KEY, em);
      try { Units.load(api); } catch (_) {}
      showLoggedIn(em);
      switchTab("programs");
    }
  });
}

$("save-btn").addEventListener("click", saveProgram);
$("refresh-btn").addEventListener("click", loadPrograms);
$("back-btn").addEventListener("click", () => {
  $("editor").hidden = true;
  $("list-view").hidden = false;
  currentCourse = null;
});
$("actions-refresh-btn").addEventListener("click", loadActions);
$("history-refresh-btn").addEventListener("click", loadHistory);

// Re-render whatever is on screen in the new language. Open editors keep their
// unsaved state (only the chrome/labels are redrawn); lists reload from the API
// because action/course names come back translated for the requested languageId.
I18N.onChange.push(() => {
  actionLibrary = null;
  coverOptions = null;
  if (currentEmail) showLoggedIn(currentEmail);
  if (activeTab === "programs" && currentCourse && !$("editor").hidden) {
    // keep a hidden-but-open editor's labels in the new language even while Courses is shown
    $("editor-title").textContent = currentCourse.id ? t("Edit Program") : t("New Program");
    renderStepsTable();
  }
  const editorOpen = activeTab === "programs" && currentCourse && !$("editor").hidden;
  if (activeTab === "programs" && window.CoursesUI && CoursesUI.view() === "courses") CoursesUI.relang();
  else if (editorOpen) { /* labels already redrawn above */ }
  else if (activeTab === "plans" && window.PlannerUI) PlannerUI.relang();
  else if (activeTab === "actions" && window.MovementsUI) MovementsUI.relang();
  else if (activeTab === "fitness" && window.FitnessUI) FitnessUI.relang();
  else if (activeTab === "history" && window.DashboardUI) { /* dashboard, explorer, report and medals re-render themselves on I18N.onChange; switchTab would reset to the dashboard */ }
  else if (!$("main-section").hidden) switchTab(activeTab);
});

try {
  Units.onChange(() => {
    if (currentCourse && !$("editor").hidden) renderStepsTable();
  });
} catch (_) {}

(function init() {
  const token = store.get(TOKEN_KEY) || window.INNO_TOKEN;
  const email = store.get(EMAIL_KEY) || window.INNO_EMAIL || "TheITGuru";
  if (token) {
    store.set(TOKEN_KEY, token);
    store.set(EMAIL_KEY, email);
    try { Units.load(api); } catch (_) {}
    showLoggedIn(email);
    switchTab("programs");
    return;
  }
  fetch(getAppBase() + "token.json?t=" + Date.now())
    .then((r) => r.json())
    .then((d) => {
      if (d && d.token) {
        store.set(TOKEN_KEY, d.token);
        store.set(EMAIL_KEY, d.email || "TheITGuru");
        try { Units.load(api); } catch (_) {}
        showLoggedIn(d.email || "TheITGuru");
        switchTab("programs");
      }
    })
    .catch(() => {});
})();

// ==========================================
// OpenGym Bridge Integration
// ==========================================
async function updateOpenGymStatus() {
  const ind = $("og-indicator");
  const txt = $("og-status-text");
  const badge = $("og-routines-badge");
  const syncBadge = $("og-last-sync-badge");
  if (!ind || !txt) return;
  try {
    const res = await fetch(getApiBase() + "/opengym/status");
    const data = await res.json();
    if (data.url) window.openGymWebUrl = data.url;
    if (data.connected) {
      ind.classList.remove("offline");
      txt.textContent = "Connected";
      badge.textContent = `${data.routines_count} routines in OpenGym`;

      if (syncBadge) {
        let text = "Up to date";
        if (data.last_sync && typeof data.last_sync === "object") {
          const ls = data.last_sync;
          const sTime = ls.last_sync_time || "Recently";
          const wName = ls.workout_name ? ` · ${ls.workout_name}` : "";
          const uCount = ls.updates_count != null ? ` (${ls.updates_count} updated)` : "";
          text = `Synced: ${sTime}${wName}${uCount}`;
        } else if (typeof data.last_sync === "string" && data.last_sync !== "Never") {
          text = `Synced: ${data.last_sync}`;
        } else {
          text = "Synced: Up to date";
        }
        syncBadge.innerHTML = `
          <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 2v6h-6"/><path d="M3 12a9 9 0 0 1 15-6.7L21 8"/><path d="M3 22v-6h6"/><path d="M21 12a9 9 0 0 1-15 6.7L3 16"/></svg>
          <span>${escapeHtml(text)}</span>
        `;
        syncBadge.hidden = false;
      }
    } else {
      ind.classList.add("offline");
      txt.textContent = "Disconnected";
      badge.textContent = data.error || "Offline";
      if (syncBadge) syncBadge.hidden = true;
    }
  } catch (err) {
    ind.classList.add("offline");
    txt.textContent = "Offline";
    badge.textContent = "--";
    if (syncBadge) syncBadge.hidden = true;
  }
}

async function showSyncHistoryModal() {
  const backdrop = $("pio-modal-backdrop");
  const title = $("pio-modal-title");
  const body = $("pio-modal-body");
  if (!backdrop || !title || !body) return;

  title.textContent = "Recent Weight Syncs (OpenGym ➔ InnoX1)";
  body.innerHTML = "<p>Loading sync history…</p>";
  backdrop.hidden = false;

  try {
    const res = await fetch(getApiBase() + "/opengym/sync-history");
    const list = await res.json();

    if (!list || !list.length) {
      body.innerHTML = `<p class="empty-state">No syncs recorded yet. Sync runs automatically in the background after workouts.</p>`;
      return;
    }

    let html = `<div class="sync-history-list">`;
    for (const item of list) {
      const wName = escapeHtml(item.workout_name || "Workout");
      const src = escapeHtml(item.source || "OpenGym");
      const timeStr = escapeHtml(item.sync_time || item.synced_at || "Recently");
      const updates = item.updates || [];

      html += `
        <div class="sync-history-card">
          <div class="sync-history-header">
            <span class="sync-history-title">🏋️ ${wName}</span>
            <div>
              <span class="sync-history-badge">${src}</span>
            </div>
          </div>
          <div class="sync-history-time">⏱ Synced on ${timeStr}</div>
      `;

      if (updates.length > 0) {
        html += `<div class="sync-history-updates">`;
        for (const u of updates) {
          html += `
            <div class="sync-history-row">
              <span>${escapeHtml(u.name)}</span>
              <span>
                <span class="old-val">${u.old_lbs} lb</span>
                ➔
                <span class="new-val">${u.new_lbs} lb</span>
              </span>
            </div>
          `;
        }
        html += `</div>`;
      } else {
        html += `<div style="font-size:12px;color:var(--text-muted);">All weights were already matched with machine template.</div>`;
      }

      html += `
          <div class="sync-history-footer">
            <span>✔ Machine resistance active</span>
            <span>${updates.length} exercise${updates.length === 1 ? '' : 's'} updated</span>
          </div>
        </div>
      `;
    }
    html += `</div>`;
    body.innerHTML = html;
  } catch (err) {
    body.innerHTML = `<p class="server-error">Failed to load sync history: ${escapeHtml(err.message)}</p>`;
  }
}

async function syncOpenGymWeights() {
  const btn = $("og-sync-weights-btn");
  if (!btn) return;
  const original = btn.textContent;
  btn.textContent = "⏳ Syncing Weights…";
  btn.disabled = true;
  try {
    const res = await fetch(getApiBase() + "/opengym/sync-weights", { method: "POST" });
    const data = await res.json();
    if (data.success) {
      toast("✔ Machine updated with your latest workout weights!");
      loadPrograms();
    } else {
      toast(data.error || "Sync completed with warning", true);
    }
  } catch (err) {
    toast("Sync failed: " + err.message, true);
  } finally {
    btn.textContent = original;
    btn.disabled = false;
  }
}

async function showOpenGymRoutinesModal() {
  const backdrop = $("pio-modal-backdrop");
  const title = $("pio-modal-title");
  const body = $("pio-modal-body");
  if (!backdrop || !title || !body) return;
  title.textContent = "OpenGym Routines Library";
  body.innerHTML = "<p>Loading OpenGym routines…</p>";
  backdrop.hidden = false;

  try {
    const res = await fetch(getApiBase() + "/opengym/routines");
    const routines = await res.json();

    if (!routines || !routines.length) {
      body.innerHTML = `<p class="empty-state">No routines found in OpenGym.</p>`;
      return;
    }

    let html = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
        <span class="meta">${routines.length} routines in your self-hosted OpenGym</span>
        <a href="${escapeHtml(window.openGymWebUrl || 'http://localhost:8080')}" target="_blank" style="font-size:12px; color:var(--primary); font-weight:600; text-decoration:none;">Open OpenGym Web ↗</a>
      </div>
      <div class="pio-rows">
    `;

    for (const r of routines) {
      html += `
        <div class="pio-row" style="display:flex; justify-content:space-between; align-items:center; gap:8px;">
          <div>
            <div style="font-weight:600; color:var(--text);">${escapeHtml(r.name || "Untitled")}</div>
            <div class="meta">${r.exercise_count} exercises</div>
          </div>
          <div style="display:flex; gap:8px; align-items:center; flex:none;">
            <span class="og-badge" style="background:rgba(13, 148, 136, 0.15); color:#0d9488; font-weight:600;">In OpenGym</span>
            <button type="button" class="primary og-import-btn" data-rid="${r.id}" style="padding:4px 10px; font-size:12px; border-radius:6px; cursor:pointer;" title="Add this routine to Innodigym X1 Pro machine">📥 Add to Machine</button>
          </div>
        </div>
      `;
    }
    html += `</div>`;
    body.innerHTML = html;

    body.querySelectorAll(".og-import-btn").forEach((btn) => {
      btn.onclick = async (e) => {
        const b = e.currentTarget;
        const rid = b.dataset.rid;
        const orig = b.textContent;
        b.textContent = "Adding…";
        b.disabled = true;
        try {
          const res = await fetch(getApiBase() + "/opengym/import-routine", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ routineId: rid })
          });
          const d = await res.json();
          if (d.success) {
            toast(`✔ Added "${d.course_name}" to Innodigym X1 Pro! Pull down on the machine console to refresh.`);
            b.textContent = "✔ On Machine";
            loadPrograms();
            setTimeout(() => { b.textContent = orig; b.disabled = false; }, 3500);
          } else {
            toast(d.error || "Failed to add to Innodigym", true);
            b.textContent = orig;
            b.disabled = false;
          }
        } catch (err) {
          toast("Error: " + err.message, true);
          b.textContent = orig;
          b.disabled = false;
        }
      };
    });
  } catch (err) {
    body.innerHTML = `<p class="server-error">Failed to load OpenGym routines: ${escapeHtml(err.message)}</p>`;
  }
}

// Wire up OpenGym bar actions
setTimeout(() => {
  if ($("og-sync-weights-btn")) {
    $("og-sync-weights-btn").addEventListener("click", syncOpenGymWeights);
  }
  if ($("og-browse-btn")) {
    $("og-browse-btn").addEventListener("click", showOpenGymRoutinesModal);
  }
  if ($("og-sync-history-btn")) {
    $("og-sync-history-btn").addEventListener("click", showSyncHistoryModal);
  }
  if ($("og-last-sync-badge")) {
    $("og-last-sync-badge").addEventListener("click", showSyncHistoryModal);
  }
  updateOpenGymStatus();
}, 200);
