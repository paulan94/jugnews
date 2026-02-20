let categories = [];
let activeCategory = "";
const API_BASE = (window.JUGNEWS_API_BASE || "").replace(/\/+$/, "");

function apiUrl(pathAndQuery) {
  return `${API_BASE}${pathAndQuery}`;
}

async function fetchJson(pathAndQuery) {
  const res = await fetch(apiUrl(pathAndQuery));
  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`);
  }
  return res.json();
}

async function init() {
  try {
    await loadCategories();
    bindActions();
    if (categories.length) {
      setCategory(categories[0]);
      await fetchCategory();
    }
  } catch (err) {
    showError(
      "Unable to reach the API. If this site is on GitHub Pages, set window.JUGNEWS_API_BASE to your backend URL."
    );
  }
}

function bindActions() {
  document.getElementById("fetch").addEventListener("click", fetchCategory);
  document.getElementById("refresh-all").addEventListener("click", fetchDashboardSnapshot);
  document.getElementById("category").addEventListener("change", (e) => {
    setCategory(e.target.value);
    fetchCategory();
  });
}

async function loadCategories() {
  const data = await fetchJson("/api/categories");
  categories = data.categories || [];
  const select = document.getElementById("category");
  const nav = document.getElementById("category-nav");
  select.innerHTML = "";
  nav.innerHTML = "";

  categories.forEach((category) => {
    const option = document.createElement("option");
    option.value = category;
    option.textContent = category;
    select.appendChild(option);

    const button = document.createElement("button");
    button.className = "category-btn";
    button.type = "button";
    button.dataset.category = category;
    button.textContent = category;
    button.addEventListener("click", () => {
      select.value = category;
      setCategory(category);
      fetchCategory();
    });
    nav.appendChild(button);
  });
}

function setCategory(category) {
  activeCategory = category;
  document.querySelectorAll(".category-btn").forEach((button) => {
    button.classList.toggle("active", button.dataset.category === category);
  });
}

async function fetchCategory() {
  const max = Number(document.getElementById("max-articles").value || 8);
  const endpoint = `/api/scrape?category=${encodeURIComponent(activeCategory)}&max_articles=${max}&summary_sentences=3`;
  const payload = await fetchJson(endpoint);
  renderInsights(payload.insights || {});
  renderArticles(payload.articles || []);
}

async function fetchDashboardSnapshot() {
  const max = Number(document.getElementById("max-articles").value || 6);
  const data = await fetchJson(`/api/dashboard?max_articles_per_category=${max}&summary_sentences=2`);
  const categoriesPayload = data.categories || {};

  const insights = document.getElementById("insights");
  insights.innerHTML = "";
  Object.entries(categoriesPayload).forEach(([category, section]) => {
    const row = document.createElement("div");
    row.className = "insight-row";
    row.innerHTML = `
      <span class="chip">${category}</span>
      <span class="chip">articles: ${section.insights?.article_count ?? 0}</span>
      <span class="chip">sources: ${section.insights?.source_count ?? 0}</span>
    `;
    insights.appendChild(row);
  });
}

function renderInsights(insights) {
  const host = document.getElementById("insights");
  host.innerHTML = "";

  const counts = document.createElement("div");
  counts.className = "insight-row";
  counts.innerHTML = `
    <span class="chip">articles: ${insights.article_count || 0}</span>
    <span class="chip">sources: ${insights.source_count || 0}</span>
    <span class="chip">category: ${insights.category || activeCategory}</span>
  `;
  host.appendChild(counts);

  if ((insights.top_keywords || []).length) {
    const keywords = document.createElement("div");
    keywords.className = "insight-row";
    keywords.innerHTML = (insights.top_keywords || [])
      .map((item) => `<span class="chip">${item}</span>`)
      .join("");
    host.appendChild(keywords);
  }

  if ((insights.mentioned_tickers || []).length) {
    const tickers = document.createElement("div");
    tickers.className = "insight-row";
    tickers.innerHTML = `<span class="chip">tickers</span>${insights.mentioned_tickers
      .map((item) => `<span class="chip">${item}</span>`)
      .join("")}`;
    host.appendChild(tickers);
  }
}

function renderArticles(items) {
  const out = document.getElementById("results");
  out.innerHTML = "";
  if (!items.length) {
    out.textContent = "No results.";
    return;
  }

  items.forEach((it) => {
    const card = document.createElement("article");
    card.className = "card";
    const stubWarning = it.stub ? `<div class="warn">Connector setup required</div>` : "";
    card.innerHTML = `
      <div class="meta">${escapeHtml(it.source || "")} ${it.published ? `| ${escapeHtml(it.published)}` : ""}</div>
      <div class="title">${escapeHtml(it.title || "Untitled")}</div>
      ${stubWarning}
      <div class="summary">${escapeHtml(it.summary || "")}</div>
      ${it.url ? `<a class="link" target="_blank" href="${encodeURI(it.url)}">Read original</a>` : ""}
    `;
    out.appendChild(card);
  });
}

function showError(message) {
  const insights = document.getElementById("insights");
  const results = document.getElementById("results");
  if (insights) {
    insights.innerHTML = `<div class="warn">${escapeHtml(message)}</div>`;
  }
  if (results) {
    results.textContent = "No results.";
  }
}

function escapeHtml(value) {
  return (value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

window.addEventListener("DOMContentLoaded", init);
