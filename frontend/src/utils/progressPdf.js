import { jsPDF } from 'jspdf';

// Generate a GetFit progress report as a PDF, drawn with jsPDF vector primitives
// (no html2canvas — the app's Tailwind v4 oklch colors break canvas capture).
// All data comes from the Dashboard's existing state, so no extra requests.

const ORANGE = [249, 115, 22];
const PURPLE = [168, 85, 247];
const INK = [30, 30, 40];
const MUTED = [120, 120, 130];
const LINE = [225, 225, 230];
const AMBER = [180, 130, 20];

export function generateProgressPdf({
  user,
  nutritionPlan,
  todayCalories,
  stepData,
  calorieHistory = [],
  weightHistory = [],
  range = null,
}) {
  const doc = new jsPDF({ unit: 'pt', format: 'a4' });
  const pageW = doc.internal.pageSize.getWidth();
  const pageH = doc.internal.pageSize.getHeight();
  const margin = 40;
  const contentW = pageW - margin * 2;
  let y = 0;

  const ensure = (needed) => {
    if (y + needed > pageH - margin) {
      doc.addPage();
      y = margin;
    }
  };

  // ── Header band ──
  const bandH = range ? 84 : 70;
  doc.setFillColor(...ORANGE);
  doc.rect(0, 0, pageW, bandH, 'F');
  doc.setTextColor(255, 255, 255);
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(20);
  doc.text('GetFit — Progress Report', margin, 34);
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(10);
  const generated = new Date().toLocaleString('en-US', {
    weekday: 'short', year: 'numeric', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
  doc.text(`${user?.username || 'Athlete'}  ·  ${user?.email || ''}`, margin, 52);
  doc.text(`Generated ${generated}`, pageW - margin, 52, { align: 'right' });
  if (range) {
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(9.5);
    doc.text(`Reporting period:  ${fmtDate(range.from)}  to  ${fmtDate(range.to)}`, margin, 70);
    doc.setFont('helvetica', 'normal');
  }
  y = bandH + 26;

  // ── Section: Snapshot stat cards ──
  sectionTitle(doc, 'Snapshot', margin, y); y += 20;

  const currentWeight = weightHistory.length ? weightHistory[weightHistory.length - 1].weight : null;
  const firstWeight = weightHistory.length ? weightHistory[0].weight : null;
  const weightDelta = currentWeight != null && firstWeight != null
    ? +(currentWeight - firstWeight).toFixed(1) : null;
  const consumed = Math.round(todayCalories?.totals?.calories || 0);
  const goal = nutritionPlan?.calorie_goal ?? '—';

  const cards = [
    { label: 'Current Weight', value: currentWeight != null ? `${currentWeight} kg` : '—',
      sub: weightDelta != null ? `${weightDelta >= 0 ? '+' : ''}${weightDelta} kg overall` : 'no history' },
    { label: 'Calorie Goal', value: `${goal}`, sub: 'kcal / day' },
    { label: 'Calories Today', value: `${consumed}`, sub: `of ${goal} goal` },
    { label: 'Steps Today', value: `${(stepData?.steps || 0).toLocaleString()}`,
      sub: `${Math.round(stepData?.calories_from_steps || 0)} kcal burned` },
    { label: 'Workout Days', value: `${user?.workout_frequency || '—'}`, sub: 'per week' },
  ];
  y = drawCards(doc, cards, margin, y, contentW);
  y += 18;

  // ── Section: Nutrition targets ──
  if (nutritionPlan) {
    ensure(120);
    sectionTitle(doc, 'Nutrition Targets', margin, y); y += 20;
    const m = nutritionPlan.macros || {};
    const nCards = [
      { label: 'BMR', value: `${nutritionPlan.bmr}`, sub: 'kcal' },
      { label: 'TDEE', value: `${nutritionPlan.tdee}`, sub: 'kcal' },
      { label: 'Protein', value: `${m.protein_g ?? '—'} g`, sub: `${m.protein_pct ?? '—'}%` },
      { label: 'Carbs', value: `${m.carbs_g ?? '—'} g`, sub: `${m.carbs_pct ?? '—'}%` },
      { label: 'Fat', value: `${m.fat_g ?? '—'} g`, sub: `${m.fat_pct ?? '—'}%` },
    ];
    y = drawCards(doc, nCards, margin, y, contentW);
    y += 12;

    if (nutritionPlan.notes?.length) {
      ensure(20 + nutritionPlan.notes.length * 14);
      doc.setFont('helvetica', 'italic');
      doc.setFontSize(9);
      doc.setTextColor(...AMBER);
      nutritionPlan.notes.forEach((note) => {
        const lines = doc.splitTextToSize(`• ${note}`, contentW);
        doc.text(lines, margin, y);
        y += lines.length * 12;
      });
      doc.setFont('helvetica', 'normal');
    }
    y += 14;
  }

  // ── Section: Weight trend ──
  ensure(200);
  sectionTitle(doc, 'Weight Progress', margin, y); y += 12;
  if (weightHistory.length > 1) {
    drawLineChart(doc, {
      x: margin, y, w: contentW, h: 150,
      data: weightHistory, key: 'weight', color: PURPLE, unit: 'kg',
    });
    y += 168;
  } else {
    emptyNote(doc, 'Log your weight on more than one day to chart a trend.', margin, y);
    y += 28;
  }

  // ── Section: calorie intake ──
  ensure(200);
  sectionTitle(doc, range ? 'Calorie Intake' : 'Calorie Intake (recent)', margin, y); y += 12;
  if (calorieHistory.length > 1) {
    drawLineChart(doc, {
      x: margin, y, w: contentW, h: 150,
      data: calorieHistory, key: 'calories', color: ORANGE, unit: 'kcal',
    });
    y += 168;
  } else {
    emptyNote(doc, 'Log meals across multiple days to chart intake.', margin, y);
    y += 28;
  }

  // ── Table: full calorie history ──
  if (calorieHistory.length) {
    ensure(60);
    sectionTitle(doc, 'Daily Log', margin, y); y += 18;
    const rows = calorieHistory.map((d) => [
      d.date,
      `${Math.round(d.calories || 0)}`,
      `${Math.round(d.protein || 0)}`,
      `${Math.round(d.carbs || 0)}`,
      `${Math.round(d.fat || 0)}`,
    ]);
    y = drawTable(doc, {
      head: ['Date', 'Calories', 'Protein (g)', 'Carbs (g)', 'Fat (g)'],
      rows, x: margin, y, w: contentW, ensure,
    });
  }

  // ── Footer on every page ──
  const pages = doc.getNumberOfPages();
  for (let i = 1; i <= pages; i++) {
    doc.setPage(i);
    doc.setFontSize(8);
    doc.setTextColor(...MUTED);
    doc.text('GetFit — your personal fitness companion', margin, pageH - 20);
    doc.text(`Page ${i} of ${pages}`, pageW - margin, pageH - 20, { align: 'right' });
  }

  const fileTag = range ? `_${range.from}_to_${range.to}` : '';
  doc.save(`getfit-progress${fileTag}.pdf`);
}

// ── drawing helpers ──────────────────────────────────────────────────────────

// Format an ISO YYYY-MM-DD as "Mon DD, YYYY" without timezone drift.
function fmtDate(iso) {
  if (!iso) return '—';
  const [yr, mo, da] = String(iso).split('-').map(Number);
  if (!yr || !mo || !da) return String(iso);
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  return `${months[mo - 1]} ${da}, ${yr}`;
}

function sectionTitle(doc, text, x, y) {
  doc.setFont('helvetica', 'bold');
  doc.setFontSize(13);
  doc.setTextColor(...INK);
  doc.text(text, x, y);
  doc.setDrawColor(...ORANGE);
  doc.setLineWidth(2);
  doc.line(x, y + 4, x + 28, y + 4);
}

function drawCards(doc, cards, x, y, totalW) {
  const gap = 10;
  const w = (totalW - gap * (cards.length - 1)) / cards.length;
  const h = 58;
  cards.forEach((c, i) => {
    const cx = x + i * (w + gap);
    doc.setFillColor(248, 248, 250);
    doc.setDrawColor(...LINE);
    doc.setLineWidth(0.5);
    doc.roundedRect(cx, y, w, h, 6, 6, 'FD');
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(7.5);
    doc.setTextColor(...MUTED);
    doc.text(c.label.toUpperCase(), cx + 8, y + 16);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(14);
    doc.setTextColor(...INK);
    doc.text(String(c.value), cx + 8, y + 36);
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(7.5);
    doc.setTextColor(...MUTED);
    doc.text(String(c.sub || ''), cx + 8, y + 50);
  });
  return y + h;
}

function drawLineChart(doc, { x, y, w, h, data, key, color, unit }) {
  // Frame
  doc.setDrawColor(...LINE);
  doc.setLineWidth(0.5);
  doc.roundedRect(x, y, w, h, 6, 6, 'S');

  const padL = 44, padR = 14, padT = 14, padB = 22;
  const plotX = x + padL, plotY = y + padT;
  const plotW = w - padL - padR, plotH = h - padT - padB;

  const values = data.map((d) => Number(d[key]) || 0);
  let min = Math.min(...values), max = Math.max(...values);
  if (min === max) { min -= 1; max += 1; }
  const range = max - min;

  const px = (i) => plotX + (data.length === 1 ? plotW / 2 : (i / (data.length - 1)) * plotW);
  const py = (v) => plotY + plotH - ((v - min) / range) * plotH;

  // Y gridlines + labels (min, mid, max)
  doc.setFontSize(7);
  doc.setTextColor(...MUTED);
  [min, (min + max) / 2, max].forEach((v) => {
    const gy = py(v);
    doc.setDrawColor(...LINE);
    doc.setLineWidth(0.3);
    doc.line(plotX, gy, plotX + plotW, gy);
    doc.text(`${Math.round(v)}`, x + padL - 6, gy + 2, { align: 'right' });
  });

  // Line
  doc.setDrawColor(...color);
  doc.setLineWidth(1.6);
  for (let i = 1; i < data.length; i++) {
    doc.line(px(i - 1), py(values[i - 1]), px(i), py(values[i]));
  }
  // Dots
  doc.setFillColor(...color);
  data.forEach((_, i) => doc.circle(px(i), py(values[i]), 1.6, 'F'));

  // X labels (first, middle, last) — MM-DD
  const idxs = data.length <= 3 ? data.map((_, i) => i) : [0, Math.floor((data.length - 1) / 2), data.length - 1];
  idxs.forEach((i) => {
    const label = String(data[i].date || '').slice(5);
    doc.text(label, px(i), y + h - 8, { align: 'center' });
  });

  // Unit caption
  doc.setTextColor(...MUTED);
  doc.text(unit, x + 6, y + 10);
}

function drawTable(doc, { head, rows, x, y, w, ensure }) {
  const colW = w / head.length;
  const rowH = 18;

  const header = () => {
    doc.setFillColor(...ORANGE);
    doc.rect(x, y, w, rowH, 'F');
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(8.5);
    doc.setTextColor(255, 255, 255);
    head.forEach((c, i) => doc.text(c, x + i * colW + 6, y + 12));
    y += rowH;
  };

  header();
  doc.setFont('helvetica', 'normal');
  doc.setTextColor(...INK);
  rows.forEach((row, r) => {
    if (ensure) {
      const before = y;
      ensure(rowH + 4);
      if (y !== before) header(); // repeat header after a page break
    }
    if (r % 2 === 0) {
      doc.setFillColor(248, 248, 250);
      doc.rect(x, y, w, rowH, 'F');
    }
    doc.setFontSize(8.5);
    doc.setTextColor(...INK);
    row.forEach((cell, i) => doc.text(String(cell), x + i * colW + 6, y + 12));
    y += rowH;
  });
  return y;
}

function emptyNote(doc, text, x, y) {
  doc.setFont('helvetica', 'italic');
  doc.setFontSize(9);
  doc.setTextColor(...MUTED);
  doc.text(text, x, y + 12);
  doc.setFont('helvetica', 'normal');
}
