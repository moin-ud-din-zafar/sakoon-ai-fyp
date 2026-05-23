"""Personalization: mood trends, coping library, exercise selection."""

import copy
import random
from typing import Any, Dict, List, Optional

from app.core.constants import MH_SEVERITY_ORDER

# --- Rich coping library: step-by-step, duration, tone, optional Roman Urdu ---


def _st(text: str, text_ur: str = "", **extra) -> Dict[str, Any]:
    s = {"text": text, **extra}
    if text_ur:
        s["textUrdu"] = text_ur
    return s


COPING_LIBRARY: Dict[str, List[Dict[str, Any]]] = {
    "Anxiety": [
        {
            "id": "anxiety-478-breath",
            "type": "breathing",
            "title": "4-7-8 Calm Breath",
            "titleUrdu": "4-7-8 sakoon ki saans",
            "tone": "calm",
            "durationSeconds": 180,
            "description": "A slow pattern to quiet a racing nervous system.",
            "descriptionUrdu": "Aahista pattern jab dimagh tez chal raha ho.",
            "repeatCount": 4,
            "steps": [
                _st(
                    "Sit comfortably. Let your shoulders drop.",
                    "Aaram se baithain. Kandhe narm chor dein.",
                    seconds=10,
                ),
                _st("Breathe in through your nose for 4 counts.", "Naak se 4 ginti tak saans andar.", seconds=4, phase="inhale"),
                _st("Hold gently for 7 counts.", "7 ginti tak halka hold.", seconds=7, phase="hold"),
                _st("Exhale slowly through your mouth for 8 counts.", "8 ginti tak aahista moon se bahar.", seconds=8, phase="exhale"),
            ],
        },
        {
            "id": "anxiety-54321",
            "type": "grounding",
            "title": "5-4-3-2-1 Grounding",
            "titleUrdu": "5-4-3-2-1 zameen se jor",
            "tone": "grounding",
            "durationSeconds": 240,
            "description": "Anchor your attention in the present through your senses.",
            "descriptionUrdu": "Hiss se abhi yahan wapas aain.",
            "steps": [
                _st("Name 5 things you can see around you.", "5 cheezein jo dekh sakte hain, naam lein."),
                _st("Name 4 things you can hear.", "4 awaazen ya sunayi dene wali cheezein."),
                _st("Name 3 things you can feel on your skin or body.", "3 cheezein jo jild ya jism pe mehsoos hon."),
                _st("Name 2 things you can smell (or like the smell of).", "2 mehak ya pasand ki mehak."),
                _st("Name 1 thing you can taste (or a sip of water).", "1 zaiqa ya ghunt paani."),
            ],
        },
    ],
    "Depression": [
        {
            "id": "dep-micro-move",
            "type": "movement",
            "title": "Gentle Movement Reset",
            "titleUrdu": "Halki harkat",
            "tone": "reflective",
            "durationSeconds": 300,
            "description": "Tiny actions to shift stuck energy — no pressure to ‘feel better’.",
            "descriptionUrdu": "Chhoti harkat, zor nahi.",
            "steps": [
                _st("Stand or sit tall. Roll shoulders back once.", "Seedha baithain ya khare hon. Kandhe ek dafa peechay."),
                _st("Stretch arms up for 10 seconds if it feels okay.", "10 sec haath upar agar theek lage."),
                _st("Take 5 slow breaths — in through nose, out through mouth.", "5 aahiste saans — andar naak se, bahar moon se."),
                _st("Name one small thing your body did today (even ‘got out of bed’).", "Aaj jism ne ek chhoti cheez ki — naam lein."),
            ],
        },
        {
            "id": "dep-gratitude-lite",
            "type": "journaling",
            "title": "Three Small Gratitudes",
            "titleUrdu": "Teen chhoti shukr guzari",
            "tone": "reflective",
            "durationSeconds": 180,
            "description": "Three lines — no need for big feelings.",
            "descriptionUrdu": "Teen lines — bara mehsoos zaroori nahi.",
            "prompt": "Write three small things that weren’t terrible today (water, shade, a text).",
            "promptUrdu": "Aaj teen chhoti cheezein likhein jo bilkul buri na thin.",
            "steps": [
                _st("Take one slow breath.", "Ek aahista saans."),
                _st("Write the first small thing you’re glad existed today.", "Pehli chhoti cheez jo aaj theek lagi."),
                _st("Write a second — even ‘tea was warm’ counts.", "Doosri — chaah garam bhi theek hai."),
                _st("Write a third. Fold the page or close the note when done.", "Teesri. Phir band kar dein."),
            ],
        },
    ],
    "Stress": [
        {
            "id": "stress-box",
            "type": "breathing",
            "title": "Box Breathing",
            "titleUrdu": "Box saans",
            "tone": "calm",
            "durationSeconds": 192,
            "description": "Even counts in a square — steadying when everything feels loud.",
            "descriptionUrdu": "Barabar ginti jab sab zor se ho.",
            "repeatCount": 4,
            "steps": [
                _st("Inhale for 4 counts.", "4 ginti andar.", seconds=4, phase="inhale"),
                _st("Hold for 4 counts.", "4 ginti hold.", seconds=4, phase="hold"),
                _st("Exhale for 4 counts.", "4 ginti bahar.", seconds=4, phase="exhale"),
                _st("Hold empty for 4 counts.", "4 ginti khaali.", seconds=4, phase="hold"),
            ],
        },
        {
            "id": "stress-pmr-lite",
            "type": "relaxation",
            "title": "Tension Scan (short)",
            "titleUrdu": "Jism ka halka scan",
            "tone": "grounding",
            "durationSeconds": 240,
            "description": "Notice and release clenched spots — feet to jaw.",
            "descriptionUrdu": "Kasawat chorain — pair se le kar.",
            "steps": [
                _st("Feet: curl toes tight for 3 seconds, then release.", "3 sec pair kas ke, phir chhor dein."),
                _st("Legs: tense thighs 3 seconds, release.", "Raan 3 sec, phir chhor dein."),
                _st("Hands: make fists, release.", "Muthhi, phir kholein."),
                _st("Jaw: let teeth part slightly; shoulders drop.", "Dant halkay, kandhe neeche."),
            ],
        },
    ],
    "Suicidal": [
        {
            "id": "safe-ground-now",
            "type": "safety",
            "title": "Right Now — Safety First",
            "titleUrdu": "Abhi — pehle safety",
            "tone": "calm",
            "durationSeconds": 120,
            "description": "You deserve support beyond this screen.",
            "descriptionUrdu": "Aap support ke haqdar hain.",
            "steps": [
                _st("If you can, move to a safer space away from means of harm.", "Ho sake to mehfooz jagah."),
                _st("Text or call one person you trust — or a helpline.", "Ek bharosa ya helpline."),
                _st("Name five things you see in this room right now.", "Abhi kamre ki 5 cheezein."),
                _st("Slow exhale, longer than your inhale, three times.", "Teen dafa lambi saans bahar."),
            ],
        },
    ],
    "Bipolar": [
        {
            "id": "bio-routine-anchor",
            "type": "routine",
            "title": "Sleep-Wake Anchor",
            "titleUrdu": "Sone-uthne ka seedha waqt",
            "tone": "reflective",
            "durationSeconds": 180,
            "description": "One gentle anchor for your rhythm today.",
            "descriptionUrdu": "Aaj ke liye ek narm routine.",
            "steps": [
                _st("Pick a wake-up window (not exact minute — a 30-min range).", "Uthne ka 30 min ka darja."),
                _st("Pick a wind-down cue tonight (dim lights, same drink).", "Raat ka ek signal — roshni kam ya same drink."),
                _st("Write one line: what helped sleep last time it went okay.", "Ek line: pehle kab theek soye thay."),
            ],
        },
    ],
    "Personality disorder": [
        {
            "id": "pd-observe",
            "type": "mindfulness",
            "title": "Observe the Wave",
            "titleUrdu": "Lehar dekhna",
            "tone": "reflective",
            "durationSeconds": 240,
            "description": "Notice intensity without having to fix it.",
            "descriptionUrdu": "Taiz mehsoos — theek karne ki zaroorat nahi.",
            "steps": [
                _st("Name the feeling in one word (anger, fear, shame, blank).", "Ek lafz mein naam."),
                _st("Where do you feel it in the body? No judgment.", "Jism mein kahan? be-buniyad."),
                _st("Breathe once as if you’re making space around it.", "Ek saans — jagah jaisi."),
                _st("Remind yourself: this wave can move; you don’t have to act this second.", "Lehar chal sakti hai; abhi faisla nahi."),
            ],
        },
    ],
    "Normal": [
        {
            "id": "norm-stay-connected",
            "type": "maintenance",
            "title": "One Connection Check-in",
            "titleUrdu": "Ek rabta",
            "tone": "calm",
            "durationSeconds": 120,
            "description": "A small step toward people or activities that feel steady.",
            "descriptionUrdu": "Seedhay log ya cheez se ek qadam.",
            "steps": [
                _st("Think of one person or place that usually feels neutral or kind.", "Ek shakhs ya jagah jo theek lagti ho."),
                _st("Send a two-word check-in or plan one tiny visit this week.", "Do lafz ka message ya chhoti mulaqat."),
                _st("Notice one thing in your environment that felt okay today.", "Aaj ek cheez jo theek lagi."),
            ],
        },
    ],
}


def compute_trend(emotion_history: List[Dict[str, Any]]) -> str:
    """Mood trend: improving | stable | declining."""
    if len(emotion_history) < 2:
        return "stable"

    def severity_score(label: str) -> int:
        try:
            return MH_SEVERITY_ORDER.index(label)
        except ValueError:
            return len(MH_SEVERITY_ORDER)

    scores = [severity_score(h.get("dominantEmotion", "Normal")) for h in emotion_history]
    recent = scores[-3:]
    older = scores[:-3] if len(scores) > 3 else scores[:-1]
    if not older:
        return "stable"

    recent_avg = sum(recent) / len(recent)
    older_avg = sum(older) / len(older)
    diff = recent_avg - older_avg

    if diff < -0.5:
        return "improving"
    if diff > 0.5:
        return "declining"
    return "stable"


def _pool_for_class(mh_classification: str) -> List[Dict[str, Any]]:
    return list(COPING_LIBRARY.get(mh_classification, COPING_LIBRARY["Normal"]))


def choose_library_exercise(
    mh_classification: str,
    recent_types: Optional[List[str]] = None,
    recent_titles: Optional[List[str]] = None,
    mood_trend: str = "stable",
) -> Dict[str, Any]:
    """
    Pick one library exercise: avoid recent types/titles; bias by mood trend.
    Returns a deep copy–safe dict (caller should copy if mutating).
    """
    recent_types = recent_types or []
    recent_titles = set((recent_titles or [])[-5:])
    pool = _pool_for_class(mh_classification)

    filtered = [e for e in pool if e.get("type") not in recent_types]
    if not filtered:
        filtered = [e for e in pool if e.get("title") not in recent_titles]
    if not filtered:
        filtered = pool

    grounding_first = {"grounding", "breathing", "safety", "relaxation"}
    if mood_trend == "declining":
        filtered.sort(
            key=lambda x: (0 if x.get("type") in grounding_first else 1, random.random())
        )
    elif mood_trend == "improving":
        random.shuffle(filtered)

    chosen = filtered[0]
    return copy.deepcopy(chosen)


def exercise_to_api_payload(
    exercise: Dict[str, Any],
    source: str,
    assignment_id: Optional[int] = None,
    prefer_urdu: bool = False,
) -> Dict[str, Any]:
    """Normalize exercise for JSON API (camelCase where needed for frontend)."""
    out = {
        "assignmentId": assignment_id,
        "source": source,
        "id": exercise.get("id"),
        "type": exercise.get("type"),
        "title": exercise.get("title"),
        "tone": exercise.get("tone", "calm"),
        "durationSeconds": exercise.get("durationSeconds", 120),
        "description": exercise.get("description", ""),
        "repeatCount": exercise.get("repeatCount", 1),
        "prompt": exercise.get("prompt"),
        "steps": exercise.get("steps") or [],
    }
    if prefer_urdu:
        if exercise.get("titleUrdu"):
            out["title"] = exercise["titleUrdu"]
        if exercise.get("descriptionUrdu"):
            out["description"] = exercise["descriptionUrdu"]
        if exercise.get("promptUrdu"):
            out["prompt"] = exercise["promptUrdu"]
        steps = []
        for s in out["steps"]:
            ns = dict(s)
            if ns.get("textUrdu"):
                ns["text"] = ns["textUrdu"]
            steps.append(ns)
        out["steps"] = steps
    # Strip internal Urdu keys for minimal payload if not prefer_urdu
    if not prefer_urdu:
        for s in out["steps"]:
            s.pop("textUrdu", None)
    return out


def merge_llm_exercise(raw: Dict[str, Any], source: str = "llm") -> Dict[str, Any]:
    """Validate / pad LLM JSON into internal exercise shape."""
    steps_in = raw.get("steps") or []
    steps = []
    for s in steps_in[:5]:
        if isinstance(s, dict) and s.get("text"):
            step = {"text": str(s["text"])[:500]}
            if s.get("seconds") is not None:
                try:
                    step["seconds"] = max(1, min(120, int(s["seconds"])))
                except (TypeError, ValueError):
                    pass
            ph = s.get("phase")
            if ph in ("inhale", "hold", "exhale"):
                step["phase"] = ph
            steps.append(step)
    try:
        dur = int(raw.get("durationSeconds") or 0)
    except (TypeError, ValueError):
        dur = 0
    if dur <= 0:
        dur = max(60, len(steps) * 30)

    try:
        rc = max(1, min(6, int(raw.get("repeatCount") or 1)))
    except (TypeError, ValueError):
        rc = 1

    ex = {
        "id": raw.get("id") or "llm-generated",
        "type": raw.get("type") or "grounding",
        "title": (raw.get("title") or "Your exercise")[:120],
        "tone": raw.get("tone") or "calm",
        "durationSeconds": min(600, max(30, dur)),
        "description": (raw.get("description") or "")[:400],
        "repeatCount": rc,
        "steps": steps,
    }
    if ex["type"] == "journaling":
        ex["prompt"] = raw.get("prompt") or (steps[0]["text"] if steps else "Write a few honest lines.")
        if len(ex["steps"]) < 2:
            ex["steps"] = [
                {"text": "Take one slow breath before you write."},
                {"text": ex["prompt"]},
                {"text": "Write without editing. Stop when you've said enough for now."},
            ]
    if not ex["steps"]:
        ex["steps"] = [
            {"text": "Pause for a moment.", "seconds": 5},
            {"text": "Name one thing you can see near you right now."},
            {"text": "Place both feet flat on the floor if you can.", "seconds": 10},
        ]
    ex["source"] = source
    return ex
