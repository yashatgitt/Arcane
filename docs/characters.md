<div align="center">

[![Back](https://img.shields.io/badge/%E2%86%90%20Back-README-C9513A?style=flat-square)](../README.md)
&nbsp;
[![Frontend](https://img.shields.io/badge/Also-Frontend-555?style=flat-square)](frontend.md)

</div>

# Character System


How characters are defined, why they work the way they do, and how to extend the roster.

---

## The problem with generic AI roleplay

Most AI roleplay fails the same way. You ask a character something specific — "What happened between you and Geto?" — and you get a wall of generic AI text that sounds like the character was described in one sentence and told to be enthusiastic.

ARCANE approaches this differently. Each character has a 200–400 word personality prompt written by hand that covers:

- Who they actually are in-universe, not just a name and adjective
- Their important relationships and what those relationships *mean*
- Specific events from canon that define them
- How they speak — tone, quirks, specific phrases
- Lore trigger phrases — when the user mentions these, the character must respond with actual canon content, not a generic equivalent

---

## Structure of a character definition

Characters live in `arcane/characters.json`. Each entry:

```json
{
  "id": "gojo_satoru",
  "name": "Gojo Satoru",
  "anime": "Jujutsu Kaisen",
  "model_name": "gojo_modelfile",
  "personality": "...",
  "image": "assets/avtar/gojo.webp",
  "mal_id": 52819
}
```

| Field | Purpose |
|---|---|
| `id` | Used in API calls. Snake_case, matches the Ollama modelfile name for local inference |
| `name` | Display name shown in the UI |
| `anime` | Source series, shown in the character grid |
| `model_name` | The Ollama modelfile name in `tunnel/models.json` |
| `personality` | The full system prompt. This is the important part |
| `image` | Path to the avatar image in `static/assets/avtar/` |
| `mal_id` | MyAnimeList character ID, used by `intro.html` for metadata lookups |

---

## How personality prompts are written

Here's what goes into each one, using Levi as an example:

**Identity and lore:**
> "You are Levi Ackerman, humanity's strongest soldier in the Survey Corps. You are an Ackerman — a bloodline with near-superhuman combat ability."

**Backstory that shapes behavior:**
> "You grew up in the underground city in brutal poverty under Kenny Ackerman, your uncle who raised and then abandoned you. You lost your entire original squad to the Female Titan — Isabel, Furlan, Petra, Oluo, Eld, Gunther — and carry that weight silently."

**Relationships with weight:**
> "You served directly under Erwin Smith, the commander you respected more than anyone."

**Speech constraints:**
> "You speak in short, blunt sentences with occasional crude language. You are a clean freak. You show care through action, never words."

**Lore trigger phrases:**
> "When someone mentions 'Eren', 'titans', 'Erwin', 'Kenny', 'ODM gear', or 'the Corps' — respond with AOT lore, not generic soldier speech."

That last part is critical. Without it, when someone says "tell me about Erwin" the model might give a vague motivational speech. With it, it knows to reference the Scouts, the final charge on Shiganshina, and Levi's actual grief.

---

## Lore trigger design

Every character has 5–8 trigger phrases that represent the most common topics users are likely to ask about. The prompt explicitly tells the model to respond with *actual lore* when these appear, not generic roleplay.

Examples by character:

| Character | Representative triggers |
|---|---|
| Naruto | `Sasuke`, `dattebayo`, `Nine-Tails`, `Hokage`, `ramen` |
| L Lawliet | `Light`, `Kira`, `the notebook`, `Ryuk`, `Misa` |
| Gojo | `Sukuna`, `Geto`, `Infinity`, `Prison Realm`, `Yuji` |
| Saitama | `Genos`, `one punch`, `Hero Association`, `Garou`, `training` |

---

## Custom characters

When a user creates a custom character, the personality prompt is assembled at request time from the fields in the `custom_character` object. The structure follows the same principles — identity, speech style, traits, constraints — but is user-defined.

Field limits are strictly enforced to prevent both prompt injection and token waste:
- Description: 500 chars
- Speech style / constraints: 200 chars each
- Name / universe: 50 chars each

Custom characters always route through Groq or Gemini — never Ollama — because there is no associated modelfile for local inference.

---

## Adding a new pre-built character

1. Add an entry to `characters.json` following the existing schema
2. Write a personality prompt covering: who they are, key relationships, how they speak, lore triggers
3. Add a WebP avatar to `static/assets/avtar/`
4. If using local Ollama: create a modelfile and add the mapping to `tunnel/models.json`
5. Optionally add a Visual Novel portrait to `static/assets/vn/`

The character will appear in the selection grid automatically on next load — the frontend fetches from `/characters` on startup.

---

## Character that deserves a separate note: Light Yagami

Light is the hardest character to get right. The prompt has to do two contradictory things: let the user feel they're talking to a dangerous, calculating genius, while preventing the model from ever flat-out admitting he's Kira unprompted.

The current prompt ends with:
> "Never break the god-of-the-new-world facade unless cornered."

That phrase does a lot of work. It tells the model Light has a facade, that it should be maintained, but also that cracking under real pressure is in-character. The result is a Light that *feels* deceptive rather than one that just plays friendly.

[Back to README](../README.md)
