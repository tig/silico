# Brand images

Canonical art for README and GitHub social preview.

## Canonical files

| File | Role | Size notes |
|------|------|------------|
| [`hero.jpg`](hero.jpg) | README hero (approved master) | 16:9 (1280×720) |
| [`social-preview-master.jpg`](social-preview-master.jpg) | Full 2:1 composition before resize | ~2:1 source for GH export |
| [`social-preview.jpg`](social-preview.jpg) | GitHub repo social / Open Graph | **1280×640** (2:1), under 1 MB |

`hero.jpg` is the approved cartoon (coder in bed, the defaced Three Laws plaque, silico-style step bubble). Social uses a matching 2:1 master so export does not crop the 16:9 hero. Keep these three image files, this README, and `src/` (the editable SVG source below).

## GitHub social preview

GitHub docs: [Customizing your repository's social media preview](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview).

- Format: PNG, JPG, or GIF under **1 MB**.
- Recommended: at least **640×320**; best quality **1280×640** (2:1).
- Repo setting is **not** automatic from this path. After changing `social-preview.jpg`, a human uploads it under **Settings → General → Social preview** (public repos only share custom images).

Export from the master hero (or any source art):

```bash
python scripts/export_social_preview.py
# or, from a new 2:1 master:
python scripts/export_social_preview.py docs/images/social-preview-master.jpg -o docs/images/social-preview.jpg
```

Requires Pillow (`pip install Pillow` or use the project env if it has it).

## Art direction (for future agents)

When regenerating or editing brand art:

1. **Scene:** Coder sits up in a normal home bed (wood headboard, ordinary duvet), coding on a laptop. Not a hospital bed. Robot stands on the floor beside the bed, never in it.
2. **Style:** Clean modern cartoon (thick outlines, flat colors, soft cel shading). Not photoreal, not soft “AI slop” mascot mush.
3. **The plaque IS the joke — construct it so the gag is unmissable.** The plaque is titled **"THE THREE LAWS / OF ROBOTICS"** (engraved, official, aged — Asimov I–III abbreviated in spirit). Then, and this is the joke:
   - **"THREE" is struck out in red marker**, with **"FOUR"** scrawled above it in handwriting.
   - **Law IV is a crooked, taped-on yellow sticky note** in the same handwriting — visibly an *amendment* to the canonical three, never a fourth peer entry.
   - **The robot holds the uncapped red marker.** It is the culprit; the amendment is its own polite graffiti.

   Do NOT title the plaque "The Four Laws" or style Law IV like Laws I–III — that erases the joke (people read it as just a list of four). Law IV must read exactly:

   > IV. A robot must have good bedside manners.

4. **Robot speech:** Real operator-step language from silico / Bedside gates, not cute wellness chat. Current approved line:

   > Plug a data USB cable into the board.

   Other good sources: `bedside step` / `bedside ask` prompts in [silico AGENTS.md](https://github.com/tig/silico) and this repo’s surface docs (one human act, plain language).
5. **Title / tagline** on social art: **Bedside** and *Manners for agents who run tools for humans*.
6. **Mug / tiny labels:** Short exact words only (e.g. `DEBUG`). Image models garble small text; verify by reading the image back after generate/edit.
7. **Workflow (SVG source is canonical):** the art is authored as `src/hero.svg` — hand-editable, and text never garbles. To regenerate:

   ```bash
   # hero (1280x720)
   msedge --headless=new --disable-gpu --screenshot=hero.png --window-size=1280,720 file:///.../src/hero.html
   # social master (2560x1280, letterboxed on the art's cream)
   msedge --headless=new --disable-gpu --screenshot=social.png --window-size=2560,1280 file:///.../src/social.html
   # convert to jpg (Pillow), then:
   python scripts/export_social_preview.py docs/images/social-preview-master.jpg -o docs/images/social-preview.jpg
   ```

   Read the rendered images back to verify text; leave the human the GitHub **Settings → Social preview** upload.

## README usage

Root README embeds the hero:

```markdown
![Bedside](docs/images/hero.jpg)
```
