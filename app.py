import json, re, uuid, random import streamlit as st

BUZZWORDS = re.compile(r"\b(photorealistic|4k|8k|ultra[- ]?detailed|hdr)\b", re.I)

def sanitize(text: str) -> str: t = BUZZWORDS.sub("", text or "") t = re.sub(r"\s{2,}", " ", t).strip() return t

def detect_undertone(text: str) -> str: t = (text or "").lower() if "olive" in t: return "olive" if any(k in t for k in ["warm","golden","sunlit","tan"]): return "warm" if any(k in t for k in ["cool","pale","porcelain","fair"]): return "cool" return "neutral"

def framing_from_idea(text: str) -> str: t = (text or "").lower() if any(k in t for k in ["headshot","close-up","closeup","tight portrait"]): return "headshot" if any(k in t for k in ["full body","full-body","standing","street","runway"]): return "full" if any(k in t for k in ["half body","half-body","waist","mid","three-quarter","3/4"]): return "half" return "half"

def scene_from_idea(text: str) -> str: t = (text or "").lower() if any(k in t for k in ["studio","seamless","strobe","flash"]): return "studio" if any(k in t for k in ["window","cafe","indoor","apartment","interior","loft"]): return "window_indoor" if any(k in t for k in ["overcast","cloudy","soft daylight"]): return "overcast_day" if any(k in t for k in ["noon","hard sun","midday","harsh sun"]): return "hard_noon" if any(k in t for k in ["night","neon","sodium","streetlight","blue hour","dusk","twilight"]): return "night_street" if any(k in t for k in ["office","fluoro","fluorescent","warehouse"]): return "fluoro_office" return "overcast_day"

def choose_aspect(mode: str, framing: str, custom: str) -> str: if mode == "Fixed 9:16": return "9:16" if mode == "Custom": return (custom or "9:16").strip() return "4:5" if framing in ("headshot","half") else "2:3"

def keyword_hooks(text: str) -> dict: t = (text or "").lower() hooks = {} if "telephoto" in t: hooks["lens"] = ("135mm","f/2") if "macro" in t or "beauty" in t: hooks["lens"] = ("100mm","f/4") if "wide" in t: hooks["lens"] = ("35mm","f/4") if any(k in t for k in ["action","stride","walking","run-and-gun","handheld"]): hooks["handheld"] = True if "cinematic" in t: hooks["cinematic"] = True if any(k in t for k in ["film 400","grainy","analog"]): hooks["grain"] = "film" return hooks

def choose_camera(scene: str, framing: str, hooks: dict, camera_bias: str, lens_pref: str) -> dict: body = camera_bias if camera_bias != "Auto" else None if lens_pref != "Auto": lens, fnum = (lens_pref, "f/2.8") if lens_pref == "135mm": fnum = "f/2" if lens_pref == "85mm": fnum = "f/2" if lens_pref == "50mm": fnum = "f/2.8" if lens_pref == "35mm": fnum = "f/4" if lens_pref == "100mm Macro": fnum = "f/4" if not body: body = "Sony A7S III (full-frame, low-light)" if scene=="night_street" else "Canon 5D Mark IV (full-frame)" return {"body": body, "lens": lens_pref, "aperture": fnum} if "lens" in hooks: lens, fnum = hooks["lens"] if not body: body = "Sony A7S III (full-frame, low-light)" if scene=="night_street" else "Canon 5D Mark IV (full-frame)" return {"body": body, "lens": lens, "aperture": fnum} if not body: if scene == "night_street": body = "Sony A7S III (full-frame, low-light)" elif scene in ("window_indoor","fluoro_office"): body = "Nikon D850 (full-frame)" elif scene in ("studio","hard_noon"): body = "Canon 5D Mark IV (full-frame)" else: body = "Sony A7R IV (full-frame)" if scene == "night_street": if framing == "headshot": lens, fnum = "85mm", "f/1.8" elif framing == "full": lens, fnum = "35mm", "f/1.8" else: lens, fnum = "50mm", "f/1.8" elif scene == "studio": lens, fnum = ("85mm","f/2.8") if framing != "full" else ("50mm","f/4") elif scene == "hard_noon": lens, fnum = ("50mm","f/2.8") if framing != "full" else ("35mm","f/4") elif scene == "window_indoor": lens, fnum = ("85mm","f/2") if framing == "headshot" else ("50mm","f/2.8") elif scene == "fluoro_office": lens, fnum = ("85mm","f/2") if framing != "full" else ("50mm","f/2.8") else: lens, fnum = ("50mm","f/2.8") if framing != "full" else ("35mm","f/4") return {"body": body, "lens": lens, "aperture": fnum}

def choose_lighting(scene: str, bias: str) -> str: if bias != "Auto": return { "Studio": "Single strobe into white bounce; near-shadowless key; controlled speculars; soft edge fall-off", "Window indoor": "North-facing window key ~45°, negative fill camera-right; subtle warm practical as fill; gentle highlight roll-off", "Overcast": "Soft overcast daylight; flat shadows; rich midtones; true color without cast", "Hard noon": "Noon hard sun from above with subtle on-camera flash fill; honest, punchy textures", "Night street": "Ambient streetlights + neon as key; cooler sky bounce; believable shadow density; light rim from signage", "Fluoro office": "Overhead fluorescent strips as top light; green cast corrected with white card bounce; negative fill both sides", }[bias] if scene == "studio": return "Single strobe into white bounce; near-shadowless key; controlled speculars; soft edge fall-off" if scene == "window_indoor": return "North-facing window key ~45°, negative fill camera-right; subtle warm practical as fill; gentle highlight roll-off" if scene == "overcast_day": return "Soft overcast daylight; flat shadows; rich midtones; true color without cast" if scene == "hard_noon": return "Noon hard sun from above with subtle on-camera flash fill; honest, punchy textures" if scene == "night_street": return "Ambient streetlights + neon as key; cooler sky bounce; believable shadow density; light rim from signage" if scene == "fluoro_office": return "Overhead fluorescent strips as top light; green cast corrected with white card bounce; negative fill both sides" return "Soft daylight with mild negative fill; highlight roll-off preserved"

POSE_TEMPLATES = { "Neutral (default)": "Pose: relaxed but intentional; hips angled ~10°, chin slightly down, shoulders soft; hands with gentle tension and natural finger splay; micro‑gesture around eyes or mouth to carry mood.", "Seated portrait": "Pose: seated, back straight, shoulders open; chin slightly down; hands relaxed on lap or cup; micro‑gesture in eyes.", "Standing editorial": "Pose: weight on one leg, slight S‑curve; shoulders relaxed; chin level; one hand engaged with wardrobe or prop.", "Walking stride": "Pose: natural stride toward camera; arms swing lightly; chin level; eyes engaged; minimal blur implied.", "Crossed arms": "Pose: arms crossed without tension; shoulders soft; chin slightly down; gaze confident." }

SKIN_LINE_TMPL = ( "Skin realism: visible pores on nose/temples, soft vellus hair along jaw/forearm, " "{undertone} undertone with natural specular roll‑off; faint freckles and fine lines preserved; no plastic smoothing." ) MATERIALS_LINE = ( "Materials behave: fabric weave and micro‑pilling in cotton/knit, silk with directional specular, leather edge wear with stitching shadows, " "glass reflections with believable falloff." ) COMPOSITION_LINE = ( "Composition: intentional crop with graphic lines/diagonals and usable negative space; " "balance centered or rule‑of‑thirds as scene dictates; camera motion locked unless stated." ) POST_LINE_BASE = "Post: fine film grain, gentle S‑curve; no heavy filters."

def tone_line(tone: str) -> str: return { "neutral": "", "gritty but luxe": "Vibe: gritty but luxe.", "editorial calm": "Vibe: editorial calm.", "documentary intimacy": "Vibe: documentary intimacy.", "high‑fashion irony": "Vibe: high‑fashion irony." }.get(tone, "")

def photographer_line(name: str) -> str: return { "None": "", "Juergen Teller": "Reference: blunt flash realism (Juergen Teller) adapted to this scene.", "Peter Lindbergh": "Reference: cinematic minimalism and human texture (Peter Lindbergh).", "Richard Avedon": "Reference: crisp, honest portraiture with graphic simplicity (Richard Avedon).", "Inez & Vinoodh": "Reference: polished editorial focus with bold shape language (Inez & Vinoodh).", "Wolfgang Tillmans": "Reference: intimate documentary edge with natural light (Wolfgang Tillmans)." }.get(name, "")

def build_variant(idea: str, force_scene: str | None, aspect_mode: str, custom_ar: str, lighting_bias: str, camera_bias: str, lens_pref: str, tone: str, pose_template: str, include_skin: bool, include_materials: bool, include_composition: bool, must_include: str, avoid: str, chaos: int, verbosity: str, photoref: str) -> dict:

text

concept = sanitize(idea)
base_scene = scene_from_idea(concept)
scene = force_scene or base_scene
framing = framing_from_idea(concept)
hooks = keyword_hooks(concept)
cam = choose_camera(scene, framing, hooks, camera_bias, lens_pref)
lighting = choose_lighting(scene, lighting_bias)
undertone = detect_undertone(concept)
ar = choose_aspect(aspect_mode, framing, custom_ar)
seed = uuid.uuid4().hex[:8]

perspective = "head‑level" if framing != "full" else "waist‑level"
framing_label = "tight portrait" if framing == "headshot" else ("half‑body" if framing == "half" else "full‑body")
motion = "handheld micro‑shake" if hooks.get("handheld") else "locked tripod"

parts = []
parts.append(f"Shot on a {cam['body']} with a {cam['lens']} lens at {cam['aperture']}, {perspective} perspective, {framing_label} framing, {motion}.")
parts.append(f"Lighting: {lighting}.")
if include_skin: parts.append(SKIN_LINE_TMPL.format(undertone=undertone))
if include_materials: parts.append(MATERIALS_LINE)
if include_composition: parts.append(COMPOSITION_LINE)
parts.append(POSE_TEMPLATES.get(pose_template, POSE_TEMPLATES["Neutral (default)"]))
if must_include.strip(): parts.append(f"Must include: {sanitize(must_include)}.")
if avoid.strip(): parts.append(f"Avoid: {sanitize(avoid)}.")
tone_txt = tone_line(tone)
if tone_txt: parts.append(tone_txt)
photoline = photographer_line(photoref)
if photoline: parts.append(photoline)
parts.append(f"Subject/scene from idea: {concept}. {POST_LINE_BASE}")

prose = " ".join(parts)
if verbosity == "concise":
    prose = re.sub(r"\b(balance centered or rule‑of‑thirds as scene dictates; )", "", prose)
elif verbosity == "detailed":
    prose += " Edge fidelity: tiny vellus hairs along hairline and forearm; fine knuckle lines; lip texture with nonuniform sheen."

NEG_CORE = "plastic skin, waxy, ai-glow, over‑airbrushed, cgi, doll-like, deformed hands, extra fingers, bad anatomy, disfigured, blurry, watermark, text artifacts"
neg = f"{NEG_CORE}, {sanitize(avoid)}" if avoid.strip() else NEG_CORE

params = {"chaos": chaos, "ar": ar, "style":"raw", "v":7, "stylize":150, "p":seed}
title = f"{scene.replace('_',' ').title()} • {cam['lens']} • {ar}"
return {"title": title, "prose": prose, "negative": neg, "params": params}
def generate_variants(idea: str, n: int, aspect_mode: str, custom_ar: str, lighting_bias: str, camera_bias: str, lens_pref: str, tone: str, pose_template: str, include_skin: bool, include_materials: bool, include_composition: bool, must_include: str, avoid: str, chaos: int, verbosity: str, photoref: str) -> dict:

text

base_scene = scene_from_idea(idea)
neighbors = {
    "overcast_day":["window_indoor","hard_noon"],
    "window_indoor":["overcast_day","fluoro_office"],
    "hard_noon":["overcast_day","studio"],
    "night_street":["overcast_day","window_indoor"],
    "fluoro_office":["window_indoor","studio"],
    "studio":["window_indoor","overcast_day"]
}
scenes = [base_scene]
if base_scene in neighbors:
    k = min(2 + chaos//5, len(neighbors[base_scene]))
    scenes += random.sample(neighbors[base_scene], k=k)
while len(scenes) < n: scenes.append(base_scene)
scenes = scenes[:n]

variants = [
    build_variant(idea, s, aspect_mode, custom_ar, lighting_bias, camera_bias, lens_pref,
                  tone, pose_template, include_skin, include_materials, include_composition,
                  must_include, avoid, chaos, verbosity, photoref)
    for s in scenes
]

brief = {
    "concept": sanitize(idea),
    "subject": {"age":"", "gender_expression":"", "skin_undertone": detect_undertone(idea)},
    "controls": {
        "variants": n, "aspect_mode": aspect_mode, "custom_ar": custom_ar,
        "lighting_bias": lighting_bias, "camera_bias": camera_bias, "lens_pref": lens_pref,
        "tone": tone, "pose_template": pose_template,
        "include_skin": include_skin, "include_materials": include_materials, "include_composition": include_composition,
        "must_include": sanitize(must_include), "avoid": sanitize(avoid),
        "chaos": chaos, "verbosity": verbosity, "photographer_reference": photoref
    }
}
return {"brief": brief, "prompts": variants}
st.set_page_config(page_title="Ultra‑Real Human Prompt Bot (Pro)", page_icon="📸", layout="centered") st.title("Ultra‑Real Human Prompt Bot (Pro)") st.caption("Messy idea → professional, ultra‑real prompts + JSON. Camera/lighting, skin/materials/pose/composition, negatives, seeds, aspect modes, photographer styles.")

with st.sidebar: st.header("Settings") variants = st.slider("Variants", 1, 5, 3, 1) aspect_mode = st.radio("Aspect Ratio Mode", ["Fixed 9:16","Auto by framing","Custom"], index=0) custom_ar = st.text_input("Custom AR (e.g., 3:2 or 1:1)", value="9:16") lighting_bias = st.selectbox("Lighting bias", ["Auto","Studio","Window indoor","Overcast","Hard noon","Night street","Fluoro office"]) camera_bias = st.selectbox("Camera body bias", ["Auto","Canon 5D Mark IV (full-frame)","Nikon D850 (full-frame)","Sony A7R IV (full-frame)","Sony A7S III (full-frame, low-light)"]) lens_pref = st.selectbox("Lens preference", ["Auto","35mm","50mm","85mm","100mm Macro","135mm"]) tone = st.selectbox("Vibe / tone", ["neutral","gritty but luxe","editorial calm","documentary intimacy","high‑fashion irony"]) pose_template = st.selectbox("Pose template", list(POSE_TEMPLATES.keys()), index=0) include_skin = st.checkbox("Include skin micro‑texture module", True) include_materials = st.checkbox("Include materials/texture module", True) include_composition = st.checkbox("Include composition module", True) photoref = st.selectbox("Photographer style reference (optional)", ["None","Juergen Teller","Peter Lindbergh","Richard Avedon","Inez & Vinoodh","Wolfgang Tillmans"]) must_include = st.text_area("Must include (comma‑separated)", placeholder="e.g., lip texture, collarbone shadow, scarf knot symmetry") avoid = st.text_area("Avoid / negatives (comma‑separated)", placeholder="e.g., plastic skin, heavy blur, over‑airbrushed") chaos = st.slider("Chaos (variety)", 0, 10, 5, 1) verbosity = st.selectbox("Verbosity", ["concise","standard","detailed"], index=1)

idea = st.text_area("Your messy idea", height=140, placeholder="e.g., dusk street, man with olive undertone, linen shirt, relaxed stance, soft wind, reflective mood …")

if st.button("Generate"): if not idea.strip(): st.error("Please enter an idea.") else: data = generate_variants( idea=idea, n=variants, aspect_mode=aspect_mode, custom_ar=custom_ar, lighting_bias=lighting_bias, camera_bias=camera_bias, lens_pref=lens_pref, tone=tone, pose_template=pose_template, include_skin=include_skin, include_materials=include_materials, include_composition=include_composition, must_include=must_include, avoid=avoid, chaos=chaos, verbosity=verbosity, photoref=photoref )

text

    st.subheader("Copy‑ready ultra‑real prompts")
    all_text = []
    for p in data["prompts"]:
        pr = p["params"]
        tail = f"--chaos {pr['chaos']} --ar {pr['ar']} --style {pr['style']} --v {pr['v']} --stylize {pr['stylize']} --p {pr['p']}"
        block = f"- {p['title']}\n{p['prose']}\nNegative: {p['negative']}\n{tail}\n"
        all_text.append(block)
        st.code(block, language=None)

    st.subheader("Structured JSON")
    js = json.dumps(data, indent=2, ensure_ascii=False)
    st.code(js, language="json")

    st.download_button("Download prompts (.txt)", "\n\n".join(all_text).encode("utf-8"),
                       file_name="ultra_real_prompts.txt", mime="text/plain")
    st.download_button("Download JSON (.json)", js.encode("utf-8"),
                       file_name="ultra_real_prompts.json", mime="application/json")
if name == "main": pass
