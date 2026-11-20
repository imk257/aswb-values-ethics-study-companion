# ASWB Values and Ethics Study Companion

A Gradio study companion with 12 flashcards and 10 original fictional multiple-choice questions across six selected Values and Ethics topics. The reviewed content bank, explanations, source cues, visual design, and keyboard corrections are fixed in this version. No AI model or API key is used during study.

## Study scope and safeguards

The selected topics are IA-1 confidentiality, IA-3 ethical dilemmas, IA-4 informed consent, IB-1 self-determination, IB-2 professional boundaries, and IC-4 accessibility and language access. This is selected-topic practice, not complete ASWB Clinical preparation or a predictor of exam scores.

Original, unofficial educational practice; not actual, recalled, or secure ASWB exam questions. Not legal or client-specific advice. Do not enter or use real client information. Laws vary by jurisdiction and change over time.

Content was checked against the supplied ASWB Clinical Values and Ethics Knowledge Base 2026. Each item identifies its appendix topic/page and named source anchors. Primary-source originals have not been independently checked. The source course documents are not redistributed in this repository. No text or upload inputs solicit client information; progress is session-only. The hosting provider may maintain technical logs.

## Render deployment

This repository defines one Python web service on Render's **Free** instance plan. It does not request a database, persistent disk, or paid add-on.

- Python: 3.12.14, pinned in `.python-version`.
- Build command: `pip install -r requirements.txt`.
- Start command: `python -B app.py --host 0.0.0.0 --port $PORT`.
- Health-check path: `/`.
- The app listens on all interfaces at Render's supplied `PORT`. It does not create a Gradio share tunnel.

Connect this repository in Render and select **Free** when creating the web service, or apply the included `render.yaml` Blueprint and verify its Free plan before creation. If creating the service manually, use the build/start commands above. The public URL is assigned by Render after service creation; repository upload alone does not establish a successful deployment.

Free Render services can sleep after 15 minutes without traffic, so the first request after inactivity may wait while the service starts. Free workspace usage limits apply. The URL should be checked before use; free hosting does not guarantee immediate or continuous availability. See [Render's free-service limits](https://render.com/docs/free).

## Local alternative

Use Python 3.12, install the requirements, and run `python app.py`. Open the address printed by Gradio, normally `http://127.0.0.1:7860`, and keep the terminal running during study.

The separately preserved [runnable ZIP backup](https://drive.google.com/file/d/1ryY2CPuTC3T81QDUSj9TgMmhzePJGqwy/view) includes full macOS/Linux and Windows launch instructions. Downloading files is optional when a verified public Render deployment is available.

## Controls and accessibility

- Flashcards: recall an answer, choose Show Answer, and navigate with Previous/Next. Navigation hides the answer; Reset Flashcards returns to the beginning.
- Practice: choose A, B, or C, then Check Answer. Read the correct-answer and both distractor explanations. Reset Practice clears the session position and answer state. Checking without a selection gives guidance.
- Keyboard: Tab/Shift+Tab moves between controls; arrow keys move through answers; Space selects; Enter or Space activates tabs and buttons. Activity-tab arrow switching remains limited; use Tab/Shift+Tab and Enter/Space instead.
- Correctness appears in text as well as color. Progress is item position, not mastery. Screen-reader behavior and comprehensive accessibility conformance have not been independently audited.

## Repository contents

The five app/support files are `app.py`, `study_logic.py`, `content.json`, `styles.css`, and `requirements.txt`. The remaining files provide deployment configuration, exclusion rules, and these instructions. Private notes, assignment documents, screenshots, test records, credentials, and local environments are excluded.
