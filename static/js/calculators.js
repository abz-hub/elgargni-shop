document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("calc-form");
  if (!form) return;

  const PROTEIN_PER_KG = { muscle: 2.2, lose: 1.8, cut: 2.0, performance: 1.6 };
  const CALORIE_ADJUSTMENT = { muscle: 300, lose: -500, cut: -300, performance: 0 };

  const proteinTargetEl = document.getElementById("calc-protein-target-value");
  const caloriesEl = document.getElementById("calc-calories");
  const proteinEl = document.getElementById("calc-protein");
  const carbsEl = document.getElementById("calc-carbs");
  const fatsEl = document.getElementById("calc-fats");
  const donutEl = document.getElementById("macro-donut");

  function renderDonut(proteinKcal, carbKcal, fatKcal) {
    const total = proteinKcal + carbKcal + fatKcal;
    if (!donutEl || total <= 0) return;
    const proteinEnd = (proteinKcal / total) * 100;
    const carbEnd = proteinEnd + (carbKcal / total) * 100;
    donutEl.style.background =
      `conic-gradient(var(--macro-color-protein) 0% ${proteinEnd}%, ` +
      `var(--macro-color-carbs) ${proteinEnd}% ${carbEnd}%, ` +
      `var(--macro-color-fats) ${carbEnd}% 100%)`;
  }

  function calculate(e) {
    if (e) e.preventDefault();

    const genderInput = form.querySelector('input[name="gender"]:checked');
    const age = parseFloat(document.getElementById("calc-age").value);
    const weight = parseFloat(document.getElementById("calc-weight").value);
    const height = parseFloat(document.getElementById("calc-height").value);
    const activityMultiplier = parseFloat(document.getElementById("calc-activity").value);
    const goal = document.getElementById("calc-goal").value;

    if (!genderInput || !age || !weight || !height) return;
    const gender = genderInput.value;

    const bmr =
      gender === "male"
        ? 10 * weight + 6.25 * height - 5 * age + 5
        : 10 * weight + 6.25 * height - 5 * age - 161;

    const tdee = bmr * activityMultiplier;
    const calories = Math.max(1200, Math.round(tdee + CALORIE_ADJUSTMENT[goal]));

    const proteinGrams = Math.round(weight * 2);
    const proteinKcal = proteinGrams * 4;
    const fatKcal = calories * 0.25;
    const fatGrams = Math.round(fatKcal / 9);
    const carbKcal = Math.max(0, calories - proteinKcal - fatKcal);
    const carbGrams = Math.round(carbKcal / 4);

    caloriesEl.textContent = calories.toLocaleString();
    proteinEl.textContent = `${proteinGrams} g`;
    carbsEl.textContent = `${carbGrams} g`;
    fatsEl.textContent = `${fatGrams} g`;
    renderDonut(proteinKcal, carbKcal, fatKcal);

    const proteinTarget = Math.round(weight * PROTEIN_PER_KG[goal]);
    proteinTargetEl.textContent = proteinTarget;

    document.querySelectorAll(".recommendation-set").forEach((el) => {
      el.hidden = el.dataset.goal !== goal;
    });

    document.querySelectorAll(".calc-panel-body").forEach((el) => {
      el.hidden = false;
    });
    document.querySelectorAll(".calc-empty-state").forEach((el) => {
      el.hidden = true;
    });
  }

  function hasResults() {
    return !!document.querySelector(".calc-panel-body:not([hidden])");
  }

  function initTabs() {
    const tabs = document.querySelectorAll(".calc-tab");
    tabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        tabs.forEach((t) => t.classList.remove("active"));
        tab.classList.add("active");
        document.querySelectorAll(".calc-panel").forEach((panel) => {
          panel.classList.toggle("active", panel.id === `panel-${tab.dataset.tab}`);
        });
      });
    });
  }

  function initShare() {
    const shareBtn = document.getElementById("calc-share-btn");
    if (!shareBtn) return;

    shareBtn.addEventListener("click", () => {
      const text =
        `${caloriesEl.textContent} kcal | ${proteinEl.textContent} protein | ` +
        `${carbsEl.textContent} carbs | ${fatsEl.textContent} fats — Elgargni Shop`;

      if (navigator.share) {
        navigator.share({ text }).catch(() => {});
        return;
      }

      if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
          const original = shareBtn.textContent;
          shareBtn.textContent = shareBtn.dataset.copiedLabel || original;
          window.setTimeout(() => {
            shareBtn.textContent = original;
          }, 2000);
        });
      }
    });
  }

  form.addEventListener("submit", calculate);
  form.querySelectorAll("input, select").forEach((el) => {
    el.addEventListener("change", () => {
      if (hasResults()) calculate();
    });
  });

  initTabs();
  initShare();
});
