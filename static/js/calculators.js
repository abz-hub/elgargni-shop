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
  const isArabic = document.documentElement.lang === "ar";
  let lastBodyScan = null;

  function bodyFatCategory(percent, gender) {
    const levels = gender === "male" ? [6, 14, 18, 25] : [14, 21, 25, 32];
    if (percent < levels[0]) return isArabic ? "منخفض جدًا" : "Very low";
    if (percent < levels[1]) return isArabic ? "رياضي" : "Athletic";
    if (percent < levels[2]) return isArabic ? "ممتاز" : "Fitness";
    if (percent < levels[3]) return isArabic ? "متوسط" : "Average";
    return isArabic ? "مرتفع" : "High";
  }

  function bmiCategory(bmi) {
    if (bmi < 18.5) return isArabic ? "أقل من الطبيعي" : "Underweight";
    if (bmi < 25) return isArabic ? "طبيعي" : "Normal";
    if (bmi < 30) return isArabic ? "زائد" : "Overweight";
    return isArabic ? "مرتفع" : "High";
  }

  function setBodyValue(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
  }

  function runBodyScan() {
    const gender = form.querySelector('input[name="gender"]:checked').value;
    const age = Number(document.getElementById("calc-age").value);
    const weight = Number(document.getElementById("calc-weight").value);
    const height = Number(document.getElementById("calc-height").value);
    const advanced = !document.getElementById("bodyscan-advanced").hidden;
    const waist = Number(document.getElementById("body-waist").value);
    const neck = Number(document.getElementById("body-neck").value);
    const hip = Number(document.getElementById("body-hip").value);
    if (!age || !weight || !height) return;
    if (advanced && (!waist || !neck || waist <= neck || (gender === "female" && !hip))) return;
    const bmi = weight / Math.pow(height / 100, 2);
    let bodyFat;
    if (advanced) {
      const denominator = gender === "male"
        ? 1.0324 - 0.19077 * Math.log10(waist - neck) + 0.15456 * Math.log10(height)
        : 1.29579 - 0.35004 * Math.log10(waist + hip - neck) + 0.221 * Math.log10(height);
      bodyFat = 495 / denominator - 450;
    } else {
      bodyFat = 1.2 * bmi + 0.23 * age - 10.8 * (gender === "male" ? 1 : 0) - 5.4;
    }
    bodyFat = Math.max(3, Math.min(55, bodyFat));
    const fatMass = weight * bodyFat / 100;
    const leanMass = weight - fatMass;
    const muscleFactor = gender === "male" ? 0.52 : 0.46;
    const muscleMass = leanMass * muscleFactor;
    const water = leanMass * 0.73;
    const bmr = gender === "male" ? 10 * weight + 6.25 * height - 5 * age + 5 : 10 * weight + 6.25 * height - 5 * age - 161;
    const whtr = advanced ? waist / height : Math.max(0.35, Math.min(0.7, 0.42 + (bmi - 18.5) * 0.008));
    const idealBf = gender === "male" ? 15 : 23;
    const score = Math.round(Math.max(55, Math.min(98, 92 - Math.abs(bodyFat - idealBf) * 1.15 - Math.abs(bmi - 22) * 1.1)));
    const protein = Math.round(weight * 2);
    lastBodyScan = {bodyFat, fatMass, leanMass, muscleMass, water, bmi, bmr, whtr, score, protein, weight};
    const progress = document.getElementById("bodyscan-progress");
    const report = document.getElementById("bodyscan-report");
    progress.hidden = false; report.hidden = true;
    document.getElementById("bodyscan-run").disabled = true;
    window.setTimeout(() => {
      setBodyValue("body-weight", weight.toFixed(1)); setBodyValue("body-fat-mass", fatMass.toFixed(1));
      setBodyValue("body-lean-mass", leanMass.toFixed(1)); setBodyValue("body-muscle-mass", muscleMass.toFixed(1));
      setBodyValue("body-water", water.toFixed(1)); setBodyValue("body-bmi", bmi.toFixed(1));
      setBodyValue("body-fat-percent", bodyFat.toFixed(1)); setBodyValue("body-bmr", Math.round(bmr).toLocaleString());
      setBodyValue("body-protein", protein); setBodyValue("body-score", score); setBodyValue("body-whtr", whtr.toFixed(2));
      setBodyValue("body-bmi-label", bmiCategory(bmi)); setBodyValue("body-fat-label", bodyFatCategory(bodyFat, gender));
      setBodyValue("body-status", score >= 85 ? (isArabic ? "تركيب جسم ممتاز" : "Excellent composition") : score >= 70 ? (isArabic ? "تركيب جسم متوازن" : "Balanced composition") : (isArabic ? "قابل للتحسين" : "Room to improve"));
      document.getElementById("body-score-ring").style.setProperty("--score", `${score * 3.6}deg`);
      document.getElementById("body-whtr-marker").style.left = `${Math.max(3, Math.min(97, (whtr - .35) / .35 * 100))}%`;
      [["bar-weight", weight / 1.4], ["bar-fat", bodyFat * 2], ["bar-lean", leanMass], ["bar-muscle", muscleMass * 1.8], ["bar-water", water * 1.5]].forEach(([id, width]) => document.getElementById(id).style.width = `${Math.min(100, width)}%`);
      progress.hidden = true; report.hidden = false; document.getElementById("bodyscan-run").disabled = false;
      report.scrollIntoView({behavior:"smooth", block:"start"});
    }, window.matchMedia("(prefers-reduced-motion: reduce)").matches ? 50 : 1600);
  }

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
  const accuracyToggle = document.getElementById("bodyscan-accuracy-toggle");
  if (accuracyToggle) accuracyToggle.addEventListener("click", () => {
    const advanced = document.getElementById("bodyscan-advanced");
    const willOpen = advanced.hidden;
    advanced.hidden = !willOpen;
    accuracyToggle.setAttribute("aria-expanded", String(willOpen));
    accuracyToggle.classList.toggle("is-open", willOpen);
    accuracyToggle.querySelector("span").textContent = willOpen ? "−" : "+";
    document.querySelector("#bodyscan-run span").textContent = willOpen
      ? (isArabic ? "ابدأ التحليل المحسّن" : "Run enhanced body scan")
      : (isArabic ? "ابدأ التحليل السريع" : "Run quick body scan");
  });
  const bodyRun = document.getElementById("bodyscan-run");
  if (bodyRun) bodyRun.addEventListener("click", runBodyScan);
  form.querySelectorAll('input[name="gender"]').forEach((radio) => radio.addEventListener("change", () => {
    document.getElementById("body-hip-label").classList.toggle("is-required", radio.value === "female" && radio.checked);
  }));
  const bodyShare = document.getElementById("bodyscan-share");
  if (bodyShare) bodyShare.addEventListener("click", () => {
    if (!lastBodyScan) return;
    const text = `ELGARGNI BodyScan — Body fat ${lastBodyScan.bodyFat.toFixed(1)}% | BMI ${lastBodyScan.bmi.toFixed(1)} | Lean mass ${lastBodyScan.leanMass.toFixed(1)} kg | Score ${lastBodyScan.score}/100`;
    if (navigator.share) navigator.share({title:"ELGARGNI BodyScan", text}).catch(() => {});
    else if (navigator.clipboard) navigator.clipboard.writeText(text).then(() => {
      const old = bodyShare.textContent; bodyShare.textContent = isArabic ? "تم نسخ التقرير" : "Report copied";
      setTimeout(() => bodyShare.textContent = old, 1800);
    });
  });
  form.querySelectorAll("input, select").forEach((el) => {
    el.addEventListener("change", () => {
      if (hasResults()) calculate();
    });
  });

  initTabs();
  initShare();
});
