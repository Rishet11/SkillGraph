const pptxgen = require("pptxgenjs");

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "OpenAI Codex";
pptx.company = "SkillGraph";
pptx.subject = "Hackathon deck";
pptx.title = "SkillGraph - 5 Slide Deck";
pptx.lang = "en-US";
pptx.theme = {
  headFontFace: "Aptos Display",
  bodyFontFace: "Aptos",
  lang: "en-US",
};

const colors = {
  ink: "1D1F33",
  blue: "2F78A8",
  orange: "C84B1E",
  green: "1B7A48",
  sand: "FFF6EA",
  line: "D7D7DB",
  muted: "676B83",
};

function addHeader(slide, title, kicker) {
  slide.addText(kicker, {
    x: 0.6, y: 0.35, w: 5, h: 0.3,
    fontFace: "Aptos", fontSize: 10, color: colors.blue, bold: true,
    charSpace: 1.2, uppercase: true,
  });
  slide.addText(title, {
    x: 0.6, y: 0.7, w: 8.6, h: 0.7,
    fontFace: "Aptos Display", fontSize: 25, color: colors.ink, bold: true,
  });
  slide.addShape(pptx.ShapeType.line, {
    x: 0.6, y: 1.45, w: 11.7, h: 0,
    line: { color: colors.line, pt: 1.1 },
  });
}

function addBulletList(slide, items, x, y, w) {
  const runs = [];
  items.forEach((item) => {
    runs.push({
      text: item,
      options: {
        breakLine: true,
        bullet: { indent: 14 },
      },
    });
  });
  slide.addText(runs, {
    x, y, w, h: 4.8,
    fontFace: "Aptos", fontSize: 18, color: colors.ink,
    margin: 0.05, paraSpaceAfterPt: 9, breakLine: false,
  });
}

function addCallout(slide, text, x, y, w, h, fill, color = colors.ink) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x, y, w, h,
    rectRadius: 0.08,
    line: { color: fill, pt: 1 },
    fill: { color: fill },
  });
  slide.addText(text, {
    x: x + 0.15, y: y + 0.12, w: w - 0.3, h: h - 0.24,
    fontFace: "Aptos", fontSize: 16, color, bold: true, valign: "mid",
  });
}

function finalize(slide) {
  void slide;
}

// Slide 1
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.sand };
  addHeader(slide, "Solution Overview", "SkillGraph");
  slide.addText("AI-Adaptive Onboarding Engine", {
    x: 0.6, y: 1.75, w: 4.8, h: 0.55,
    fontFace: "Aptos Display", fontSize: 28, bold: true, color: colors.blue,
  });
  addBulletList(slide, [
    "Static onboarding wastes expert time and overwhelms junior hires.",
    "SkillGraph parses a resume and JD, measures real gaps, and builds a dependency-aware path.",
    "Every recommendation is grounded to a fixed course catalog with deterministic reasoning trace.",
  ], 0.6, 2.45, 6.2);
  addCallout(slide, "3-panel UX\nSkills • Graph • Path + Trace", 8.0, 2.0, 3.8, 1.2, "E9F3FB");
  addCallout(slide, "Demo proof\nMark Learned -> Recompute", 8.0, 3.45, 3.8, 1.0, "FFF0E8");
  addCallout(slide, "Domains\nSWE + Data", 8.0, 4.75, 3.8, 0.95, "EDF8F1");
  finalize(slide);
}

// Slide 2
{
  const slide = pptx.addSlide();
  slide.background = { color: "FFFFFF" };
  addHeader(slide, "Architecture & Workflow", "Pipeline");
  const steps = [
    ["Resume + JD", colors.blue],
    ["Classifier", colors.green],
    ["Mastery Scorer", colors.orange],
    ["Gap Subgraph", colors.blue],
    ["Priority Traversal", colors.green],
    ["Course Mapper + Trace", colors.orange],
  ];
  let x = 0.65;
  steps.forEach(([label, fill], index) => {
    addCallout(slide, label, x, 2.35, 1.75, 0.9, fill, "FFFFFF");
    if (index < steps.length - 1) {
      slide.addShape(pptx.ShapeType.chevron, {
        x: x + 1.85, y: 2.58, w: 0.4, h: 0.38,
        line: { color: colors.line, pt: 1 },
        fill: { color: "DADFE8" },
      });
    }
    x += 1.95;
  });
  addBulletList(slide, [
    "Domain-specific skill taxonomies and prerequisite DAGs drive the adaptive engine.",
    "The backend owns scoring, graph construction, traversal, and deterministic reasoning.",
    "The frontend renders the 3-panel result view and can recompute after Mark Learned.",
  ], 0.8, 4.0, 11.0);
  finalize(slide);
}

// Slide 3
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.sand };
  addHeader(slide, "Tech Stack & Models", "Implementation");
  addCallout(slide, "Backend\nFastAPI\nDAG engine\nClassifier hooks", 0.7, 2.0, 2.8, 1.9, "E9F3FB");
  addCallout(slide, "Frontend\nNext.js 14\nTypeScript\nSingle-page UX", 3.9, 2.0, 2.8, 1.9, "EDF8F1");
  addCallout(slide, "Data\nSWE + Data skills\nEdges\nFixed course catalog", 7.1, 2.0, 2.8, 1.9, "FFF0E8");
  addCallout(slide, "Models\nDeterministic by default\nGemini classifier-only optional", 10.3, 2.0, 2.4, 1.9, "F3EDFB");
  addBulletList(slide, [
    "No embeddings, vector DBs, or free-form course generation in the live submission path.",
    "Grounding is enforced by a fixed catalog and taxonomy-only skill outputs.",
    "Gemini is optional and restricted to classification into predefined skills.",
  ], 0.8, 4.45, 11.2);
  finalize(slide);
}

// Slide 4
{
  const slide = pptx.addSlide();
  slide.background = { color: "FFFFFF" };
  addHeader(slide, "Algorithms & Training", "Core Logic");
  slide.addText("mastery = 0.35 * frequency + 0.35 * recency + 0.30 * jd_match", {
    x: 0.8, y: 1.9, w: 11.4, h: 0.45,
    fontFace: "Courier New", fontSize: 18, color: colors.ink, bold: true,
  });
  slide.addText("priority = 0.4 * jd_importance + 0.4 * downstream_depth - 0.2 * mastery", {
    x: 0.8, y: 2.45, w: 11.4, h: 0.45,
    fontFace: "Courier New", fontSize: 18, color: colors.ink, bold: true,
  });
  addBulletList(slide, [
    "Gap if JD-required or preferred and mastery < 0.6.",
    "Build the gap subgraph including prerequisite ancestors.",
    "Traverse the valid frontier greedily by highest priority; never violate dependencies.",
    "Reasoning trace explains JD alignment, downstream depth, mastery, and unlocked skills.",
  ], 0.8, 3.2, 6.6);
  addCallout(slide, "Training note\nNo custom model training required.\nOriginality is in adaptive logic.", 8.0, 3.45, 4.0, 1.4, "E9F3FB");
  addCallout(slide, "Trace example\nrequired_by_jd: true\npriority_score: 1.18\ndownstream_depth: 3", 8.0, 5.1, 4.0, 1.5, "FFF0E8");
  finalize(slide);
}

// Slide 5
{
  const slide = pptx.addSlide();
  slide.background = { color: colors.sand };
  addHeader(slide, "Datasets & Metrics", "Evaluation");
  addBulletList(slide, [
    "Skill taxonomies are curated from the PRD's O*NET-grounded SWE and Data domains.",
    "Course catalog is fixed JSON; no hallucinated courses can enter the path.",
    "Two fixed demo personas prove cross-domain behavior and stable judging flow.",
  ], 0.7, 1.95, 6.2);
  addCallout(slide, "Metrics\nRedundant modules eliminated\nNaive vs recommended path length\nReasoning trace coverage = 100%", 7.6, 2.0, 4.6, 1.7, "EDF8F1");
  addCallout(slide, "Submission proof\nREADME\nDocker\nDemo video runbook\n5-slide deck", 7.6, 4.0, 4.6, 1.4, "E9F3FB");
  slide.addText("Prototype scope: 2 domains (SWE and Data) with deterministic adaptive onboarding.", {
    x: 0.8, y: 5.75, w: 11.2, h: 0.45,
    fontFace: "Aptos", fontSize: 18, color: colors.orange, bold: true,
  });
  finalize(slide);
}

pptx.writeFile({ fileName: "SkillGraph_Hackathon_Deck.pptx" });
