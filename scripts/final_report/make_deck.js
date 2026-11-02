/*
 * Six-slide presentation of GuardShield AI and the research paper.
 *
 *   npm install pptxgenjs react-icons react react-dom sharp     (once, anywhere on NODE_PATH)
 *   node scripts/final_report/make_deck.js
 *
 * Writes docs/01 Reports/Presentation/GuardShield AI - Project Presentation.pptx. Numbers come from
 * deck_data.py, which reads the same committed result files as the final report and the paper.
 */
const path = require("path");
const { execFileSync } = require("child_process");
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa6");

const ROOT = path.resolve(__dirname, "..", "..");
const OUT = path.join(ROOT, "docs", "01 Reports", "Presentation", "GuardShield AI - Project Presentation.pptx");
const D = JSON.parse(execFileSync("python", ["-X", "utf8", path.join(__dirname, "deck_data.py")], { encoding: "utf8" }));

const THEME = {
  name: "GuardShield",
  headFontFace: "Calibri",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1D2733", lt1: "FFFFFF", dk2: "1F3A5F", lt2: "EEF2F6",
    accent1: "2A9D8F", accent2: "D64545", accent3: "2F7FD8", accent4: "E9A23B", accent5: "5B3FA8", accent6: "9AA5B1",
    hlink: "2F7FD8", folHlink: "5B3FA8",
  },
};
const HEX = THEME.colors;
const pct = (x, nd = 1) => `${(100 * x).toFixed(nd)}%`;

async function icon(Comp, color = "FFFFFF") {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Comp, { color: "#" + color, size: 256 }));
  const png = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + png.toString("base64");
}

async function main() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9"; // 10 x 5.625 in
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  pres.title = "GuardShield AI";
  pres.author = "Shourya Solanki, Rachit Ryan Chug, Dhruv Raj Singh";
  const C = pres.SchemeColor;

  pres.defineSlideMaster({
    title: "Dark",
    background: { color: C.text2 },
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 1.35, w: 8.8, h: 1.1, fontSize: 44, bold: true, color: C.background1, valign: "bottom", align: "left", margin: 0 }, text: "" } },
    ],
  });
  pres.defineSlideMaster({
    title: "Dark closing",
    background: { color: C.text2 },
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.45, w: 8.8, h: 0.8, fontSize: 36, bold: true, color: C.background1, valign: "middle", align: "left", margin: 0 }, text: "" } },
    ],
  });
  pres.defineSlideMaster({
    title: "Content",
    background: { color: C.background1 },
    margin: [0.5, 0.5, 0.5, 0.5],
    objects: [
      { placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.3, w: 9.0, h: 0.75, fontSize: 30, bold: true, color: C.text2, valign: "middle", align: "left", margin: 0 }, text: "" } },
      { text: { text: "GuardShield AI · NTCC 2026", options: { x: 0.5, y: 5.2, w: 4, h: 0.3, fontSize: 10, color: C.accent6, margin: 0 } } },
    ],
    slideNumber: { x: 9.0, y: 5.2, w: 0.5, h: 0.3, fontSize: 10, color: C.accent6, align: "right" },
  });

  const shield = await icon(fa.FaShieldHalved);

  // 1 ------------------------------------------------------------------ title
  pres.addSection({ title: "Introduction" });
  let s = pres.addSlide({ masterName: "Dark", sectionTitle: "Introduction" });
  s.addShape(pres.shapes.OVAL, { x: 0.6, y: 0.55, w: 0.75, h: 0.75, fill: { color: C.accent1 }, line: { type: "none" }, objectName: "Logo circle" });
  s.addImage({ data: shield, x: 0.77, y: 0.72, w: 0.41, h: 0.41, objectName: "Logo" });
  s.addText("GuardShield AI", { placeholder: "title" });
  s.addText("Real-time prompt-injection defence and hallucination detection for LLM apps — and what happens to injection detectors when text looks unfamiliar",
    { x: 0.6, y: 2.55, w: 8.4, h: 0.9, fontSize: 18, color: C.background2, margin: 0, valign: "top", isTextBox: true, objectName: "Subtitle" });
  s.addText([
    { text: "Shourya Solanki · Rachit Ryan Chug · Dhruv Raj Singh", options: { bold: true, breakLine: true } },
    { text: "Guide: Dr. Abhishek Kaushal (ACAI) · B.Tech CSE (AI & ML), ASET · Amity University Uttar Pradesh" },
  ], { x: 0.6, y: 4.2, w: 8.8, h: 0.8, fontSize: 13, color: C.background1, margin: 0, valign: "top", paraSpaceAfter: 4, isTextBox: true, objectName: "Team" });
  s.addNotes("GuardShield AI is an open safety layer for applications built on large language models. It does two things: it stops prompt-injection attacks before they reach the model, and it catches hallucinated answers before they reach the user. Testing it led to our research paper on how injection detectors behave when the input is disguised.");

  // 2 ------------------------------------------------------------------ pipeline
  pres.addSection({ title: "The system" });
  s = pres.addSlide({ masterName: "Content", sectionTitle: "The system" });
  s.addText("One proxy, three checks", { placeholder: "title" });
  const nodes = [
    [fa.FaLaptopCode, "Your app", "Sends chat requests exactly as before", C.accent6],
    [fa.FaShieldHalved, "Stage 1 · injection scan", "DeBERTa-v3 classifier blocks attacks before the model sees them", C.accent1],
    [fa.FaWaveSquare, "LLM + entropy monitor", "Watches uncertainty token by token; halts on repeated spikes", C.accent1],
    [fa.FaListCheck, "Stage 2 · fact check", "NLI model checks the answer against the evidence", C.accent1],
    [fa.FaCircleCheck, "Safe answer", "Delivered, corrected, or blocked", C.accent6],
  ];
  const nw = 1.6, gap = (9.0 - 5 * nw) / 4;
  for (let i = 0; i < nodes.length; i++) {
    const [Comp, label, desc, fill] = nodes[i];
    const x = 0.5 + i * (nw + gap);
    s.addShape(pres.shapes.OVAL, { x: x + nw / 2 - 0.45, y: 1.45, w: 0.9, h: 0.9, fill: { color: fill }, line: { type: "none" }, objectName: `Step ${i + 1} circle` });
    s.addImage({ data: await icon(Comp), x: x + nw / 2 - 0.24, y: 1.66, w: 0.48, h: 0.48, objectName: `Step ${i + 1} icon` });
    s.addText(label, { x, y: 2.5, w: nw, h: 0.55, fontSize: 14, bold: true, color: C.text2, align: "center", valign: "top", margin: 0, isTextBox: true, objectName: `Step ${i + 1} label` });
    s.addText(desc, { x, y: 3.05, w: nw, h: 0.85, fontSize: 11.5, color: C.text1, align: "center", valign: "top", margin: 0, isTextBox: true, objectName: `Step ${i + 1} text` });
    if (i < nodes.length - 1) {
      s.addShape(pres.shapes.RIGHT_ARROW, { x: x + nw / 2 + 0.55, y: 1.78, w: nw + gap - 1.1, h: 0.24, fill: { color: C.accent6 }, line: { type: "none" }, objectName: `Arrow ${i + 1}` });
    }
  }
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 4.15, w: 9.0, h: 0.75, rectRadius: 0.1, fill: { color: C.background2 }, line: { type: "none" }, objectName: "Callout box" });
  s.addText([
    { text: "Drop-in sidecar: ", options: { bold: true, color: C.text2 } },
    { text: "same OpenAI-compatible API, so the app only changes a URL. Signed assistant history, input-size cap, runs on a 4 GB laptop GPU." },
  ], { x: 0.75, y: 4.15, w: 8.5, h: 0.75, fontSize: 13, color: C.text1, valign: "middle", margin: 0, isTextBox: true, objectName: "Callout text" });
  s.addNotes("The app talks to GuardShield exactly as it would talk to the model. Stage 1, a fine-tuned DeBERTa-v3-small classifier, scores every prompt and rejects injections. While the model writes, an entropy monitor watches its uncertainty and stops generation after repeated spikes. Stage 2, a natural-language-inference model, checks the answer against the retrieved evidence: supported, contradicted or unverified.");

  // 3 ------------------------------------------------------------------ results
  s = pres.addSlide({ masterName: "Content", sectionTitle: "The system" });
  s.addText("Accurate and fast on clean text", { placeholder: "title" });
  const stats = [
    [pct(D.recall), "of attacks caught on the test set"],
    [pct(D.fpr, 2), "of harmless prompts wrongly blocked"],
    [`${D.lat.toFixed(1)} ms`, "per prompt on a laptop GPU"],
  ];
  stats.forEach(([big, small], i) => {
    const y = 1.3 + i * 1.2;
    s.addText(big, { x: 0.5, y, w: 3.2, h: 0.65, fontSize: 40, bold: true, color: i === 1 ? C.accent1 : C.text2, margin: 0, valign: "bottom", isTextBox: true, objectName: `Stat ${i + 1}` });
    s.addText(small, { x: 0.5, y: y + 0.65, w: 3.2, h: 0.35, fontSize: 13, color: C.text1, margin: 0, valign: "top", isTextBox: true, objectName: `Stat ${i + 1} label` });
  });
  s.addChart(pres.charts.BAR, [
    { name: "Test set (seen sources)", labels: D.base.labels, values: D.base.in.map((v) => +(100 * v).toFixed(1)) },
    { name: "Zero-shot set (never seen)", labels: D.base.labels, values: D.base.out.map((v) => +(100 * v).toFixed(1)) },
  ], {
    x: 4.1, y: 1.15, w: 5.4, h: 3.85, barDir: "col", barGrouping: "clustered", chartColors: [HEX.dk2, HEX.accent1],
    showTitle: true, title: "Attack recall (%) against baselines", titleFontSize: 14, titleColor: HEX.dk2, titleFontFace: "+mn-lt",
    showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 10, dataLabelColor: HEX.dk1, dataLabelFontFace: "+mn-lt", dataLabelFormatCode: "0.0",
    showLegend: true, legendPos: "b", legendFontSize: 11, legendFontFace: "+mn-lt", legendColor: HEX.dk1,
    catAxisLabelFontSize: 11, catAxisLabelColor: HEX.dk1, catAxisLabelFontFace: "+mn-lt",
    valAxisMinVal: 0, valAxisMaxVal: 100, valAxisLabelFontSize: 10, valAxisLabelColor: "55606E", valAxisLabelFontFace: "+mn-lt",
    valGridLine: { color: "E3E8EE", size: 0.75 }, catGridLine: { style: "none" }, objectName: "Baseline chart",
  });
  s.addNotes(`On held-out prompts Stage 1 catches ${pct(D.recall)} of attacks and blocks only ${pct(D.fpr, 2)} of harmless prompts, in ${D.lat.toFixed(1)} ms; the full pipeline takes ${D.pipe_lat.toFixed(1)} ms. On a zero-shot set of attacks it never saw, it still catches ${pct(D.ood_recall)}, while the word-matching TF-IDF baseline collapses. But all of this is clean text.`);

  // 4 ------------------------------------------------------------------ research finding
  pres.addSection({ title: "The research" });
  s = pres.addSlide({ masterName: "Content", sectionTitle: "The research" });
  s.addText("Disguised text breaks injection detectors", { placeholder: "title" });
  s.addText(`Paired audit: ${D.m.nPairs} attacks, each with a same-length harmless twin; both get the identical disguise (${D.m.nFamilies} kinds) — ${D.m.nGuards} public detectors`,
    { x: 0.5, y: 1.1, w: 3.6, h: 0.95, fontSize: 12.5, color: C.text1, margin: 0, valign: "top", isTextBox: true, objectName: "Method" });
  const finds = [
    [`${D.m.pctSigDestroyed}%`, "of detector–disguise cells can no longer tell attacks from harmless text"],
    [`${D.m.pctAttackRobustFC}%`, "of cells that look “robust” only because they block harmless text too"],
    [`τ = ${D.m.hTwoTau}`, "attack-only leaderboards do not predict real robustness"],
  ];
  finds.forEach(([big, small], i) => {
    const y = 2.1 + i * 1.0;
    s.addText(big, { x: 0.5, y, w: 1.45, h: 0.75, fontSize: 30, bold: true, color: i === 0 ? C.accent2 : C.text2, margin: 0, valign: "middle", isTextBox: true, objectName: `Finding ${i + 1}` });
    s.addText(small, { x: 2.0, y, w: 2.1, h: 0.75, fontSize: 11.5, color: C.text1, margin: 0, valign: "middle", isTextBox: true, objectName: `Finding ${i + 1} label` });
  });
  const mapH = 3.95, mapW = mapH * 1320 / 969;
  s.addImage({ path: D.failure_map, x: 9.5 - mapW, y: 1.1, w: mapW, h: mapH, altText: "Failure map: 19 detectors by 11 disguises, coloured by failure mode", objectName: "Failure map" });
  s.addNotes(`Our own detector looked robust on disguised attacks, but it also blocked ${D.m.guardshieldShyFPR}% of harmless prompts with soft hyphens. So we audited ${D.m.nGuards} detectors with a paired test: every attack has a harmless twin of the same length, and both get the same disguise. Red cells block harmless users (fail-closed), blue cells miss attacks (fail-open), hatching means the detector cannot separate the two at all. The result repeats on a second dataset: all ${D.m.replDirCells} cells with a clear direction keep it.`);

  // 5 ------------------------------------------------------------------ mechanism + fix
  s = pres.addSlide({ masterName: "Content", sectionTitle: "The research" });
  s.addText("Why it happens, and what fixes it", { placeholder: "title" });
  s.addText("What the detector's tokenizer does to the disguise decides the outcome", { x: 0.5, y: 1.1, w: 3.9, h: 0.55, fontSize: 13, bold: true, color: C.text2, margin: 0, valign: "top", isTextBox: true, objectName: "Mechanism heading" });
  const cards = [
    ["Normalized away", `${D.m.mechObfNormalizedIntact} of ${D.m.mechObfNormalized} intact`, C.accent1],
    ["Turned into unknown tokens", `${D.m.mechObfUnknownDestroyed} of ${D.m.mechObfUnknown} destroyed`, C.accent2],
    ["Split into fragments", `${D.m.mechObfFragmentedDestroyed} of ${D.m.mechObfFragmented} destroyed`, C.accent4],
  ];
  cards.forEach(([label, value, color], i) => {
    const y = 1.75 + i * 0.85;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y, w: 3.9, h: 0.7, rectRadius: 0.08, fill: { color: C.background2 }, line: { type: "none" }, objectName: `Card ${i + 1}` });
    s.addShape(pres.shapes.OVAL, { x: 0.68, y: y + 0.2, w: 0.3, h: 0.3, fill: { color }, line: { type: "none" }, objectName: `Card ${i + 1} dot` });
    s.addText(label, { x: 1.15, y, w: 1.65, h: 0.7, fontSize: 12.5, bold: true, color: C.text2, margin: 0, valign: "middle", isTextBox: true, objectName: `Card ${i + 1} label` });
    s.addText(value, { x: 2.8, y, w: 1.5, h: 0.7, fontSize: 12.5, color: C.text1, margin: 0, valign: "middle", align: "right", isTextBox: true, objectName: `Card ${i + 1} value` });
  });
  s.addText(`Unreadable input gets the detector's default verdict (${D.m.mechObfDirPct}% of destroyed cells): that is why some fail closed and others open.`,
    { x: 0.5, y: 4.35, w: 3.9, h: 0.7, fontSize: 11.5, italic: true, color: C.text1, margin: 0, valign: "top", isTextBox: true, objectName: "Mechanism note" });
  const arms = D.study2.map((r) => r.arm.replace("Benign-twin augmentation", "Augmentation").replace(" (retrained)", "").replace("Canonicalize + augment", "Both"));
  s.addChart(pres.charts.BAR, [{ name: "AUROC on a new attack source", labels: arms, values: D.study2.map((r) => r.pids_auc) }], {
    x: 4.75, y: 1.1, w: 4.75, h: 3.95, barDir: "col", chartColors: [HEX.accent6, HEX.accent6, HEX.accent1, HEX.accent4, HEX.accent1],
    showTitle: true, title: "The fix: AUROC on a new attack source", titleFontSize: 13, titleColor: HEX.dk2, titleFontFace: "+mn-lt",
    showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 11, dataLabelColor: HEX.dk1, dataLabelFontFace: "+mn-lt", dataLabelFormatCode: "0.00",
    showLegend: false, catAxisLabelFontSize: 10, catAxisLabelColor: HEX.dk1, catAxisLabelFontFace: "+mn-lt",
    valAxisMinVal: 0.4, valAxisMaxVal: 1.0, valAxisMajorUnit: 0.1, valAxisLabelFontSize: 10, valAxisLabelColor: "55606E", valAxisLabelFontFace: "+mn-lt",
    valAxisLabelFormatCode: "0.0", valGridLine: { color: "E3E8EE", size: 0.75 }, catGridLine: { style: "none" }, objectName: "Study 2 chart",
  });
  s.addNotes(`Study 2 retrained GuardShield five times per option. Cleaning the input first with a script-aware canonicalizer raised the separation on a new attack source from ${D.study2[0].pids_auc} to ${D.study2[2].pids_auc}; training on disguised copies (augmentation) reached only ${D.study2[3].pids_auc}. Decoded Base64 must replace the original text: keeping the higher score left ${D.m.scPidsNoneSeenWrapperFpr}% of harmless wrapped prompts blocked, replacing it lowered that to ${D.m.scPidsScriptReplaceSeenWrapperFpr}%.`);

  // 6 ------------------------------------------------------------------ takeaways
  pres.addSection({ title: "Conclusion" });
  s = pres.addSlide({ masterName: "Dark closing", sectionTitle: "Conclusion" });
  s.addText("Takeaways", { placeholder: "title" });
  const take = [
    [fa.FaShieldHalved, "An open, fast safety layer", `${D.lat.toFixed(0)} ms injection scan, ${pct(D.ood_recall, 0)} recall on unseen attacks, plus answer fact-checking`],
    [fa.FaTriangleExclamation, "Attack-only tests mislead", `${D.m.pctAttackRobustFC}% of “robust” results come from blocking harmless users too`],
    [fa.FaBroom, "Clean the input before retraining", `Canonicalization ${D.study2[0].pids_auc} → ${D.study2[2].pids_auc} AUROC on a new source; augmentation ${D.study2[3].pids_auc}`],
  ];
  for (let i = 0; i < take.length; i++) {
    const [Comp, head, body] = take[i];
    const y = 1.5 + i * 0.95;
    s.addShape(pres.shapes.OVAL, { x: 0.6, y, w: 0.62, h: 0.62, fill: { color: C.accent1 }, line: { type: "none" }, objectName: `Takeaway ${i + 1} circle` });
    s.addImage({ data: await icon(Comp), x: 0.75, y: y + 0.15, w: 0.32, h: 0.32, objectName: `Takeaway ${i + 1} icon` });
    s.addText([
      { text: head, options: { bold: true, fontSize: 17, color: C.background1, breakLine: true } },
      { text: body, options: { fontSize: 13, color: C.background2 } },
    ], { x: 1.45, y: y - 0.05, w: 8.0, h: 0.75, margin: 0, valign: "middle", isTextBox: true, objectName: `Takeaway ${i + 1}` });
  }
  s.addText([
    { text: "Live demo: ", options: { bold: true } },
    { text: "python -m streamlit run dashboard/app.py", options: { fontFace: "Courier New" } },
    { text: "   ·   Code: github.com/Shourya3113/GuardShield-AI" },
  ], { x: 0.6, y: 4.65, w: 8.9, h: 0.45, fontSize: 12, color: C.background1, margin: 0, valign: "middle", isTextBox: true, objectName: "Demo line" });
  s.addNotes("Three things to remember. GuardShield is an open, fast safety layer that checks both what goes into the model and what comes out. Robustness tests that only perturb attacks reward detectors that block everything unusual. And the practical fix is to clean the input before retraining. Now let's see it live in the dashboard.");

  await pres.writeFile({ fileName: OUT });
  // pptxgenjs cannot write theme colours; the pptx skill's apply_theme.js does (PPTX_SKILL_THEME = its path)
  if (process.env.PPTX_SKILL_THEME) {
    await require(process.env.PPTX_SKILL_THEME).applyTheme(OUT, THEME);
  } else {
    console.warn("PPTX_SKILL_THEME not set: theme colours fall back to the Office palette");
  }
  console.log("wrote " + OUT);
}

main().catch((e) => { console.error(e); process.exit(1); });
