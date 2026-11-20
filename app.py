"""Gradio study companion with fixed, appendix-verified educational content."""
from __future__ import annotations
import os
os.environ.setdefault('GRADIO_ANALYTICS_ENABLED', 'False')
from html import escape
from pathlib import Path
import argparse
import gradio as gr
from study_logic import load_bank, move, check_answer

BANK = load_bank()
CARDS, QUESTIONS = BANK['flashcards'], BANK['questions']
TITLE = 'ASWB Values & Ethics Study Companion'
CSS = Path(__file__).with_name('styles.css').read_text(encoding='utf-8')
# Gradio scopes component CSS inside .contain. The outer shell needs a global
# head rule to avoid doubling the responsive padding defined in styles.css.
HEAD = '<style>.gradio-container > .main {padding:0 !important;}</style>'

# Gradio 6.32 gives each radio a different native name and rewrites it on
# updates. Restore one native group within our own stable component IDs.
# Observing the tabs also covers the practice panel's lazy first render.
# The browser handles keys; Gradio keeps its existing selection handlers.
RADIO_GROUP_JS = """() => {
    const host = document.getElementById('study-tabs');
    if (!host || host.dataset.nativeRadioGrouping === 'ready') return;
    host.dataset.nativeRadioGrouping = 'ready';
    const normalize = () => {
        for (const input of host.querySelectorAll('#answer-options input[type="radio"]')) {
            if (input.name !== 'aswb-practice-answer') input.name = 'aswb-practice-answer';
        }
    };
    new MutationObserver(normalize).observe(host, {
        subtree: true, childList: true, attributes: true, attributeFilter: ['name']
    });
    normalize();
}"""

# Clear stale inputs immediately and prevent grading during a navigation/reset
# response. The existing view callback restores the Check Answer button.
PRACTICE_TRANSITION_JS = "() => [null, '', {__type__: 'update', interactive: false}]"


def panel(item, text):
    kind = 'question' if item['id'].startswith('MCQ') else 'flashcard'
    return (
        f'<section class="study-panel {kind}-panel" data-topic="{escape(item["code"])}">'
        f'<div class="card-meta"><span class="topic-badge">{escape(item["code"])}</span>'
        f'<span class="topic-name">{escape(item["topic"])}</span>'
        f'<span class="item-id">{escape(item["id"])}</span></div>'
        f'<h2>{escape(text)}</h2></section>'
    )


def source(item):
    return f'<aside class="source-note"><span class="source-label">Source cue</span><p>{escape(item["source"])}</p></aside>'


def position(label, index, total):
    percentage = round(100 * (index + 1) / total, 2)
    return (
        '<div class="position-block">'
        f'<div class="position-line"><span class="position" role="status" aria-live="polite">{label} {index + 1} of {total}</span>'
        f'<span class="position-caption">{("Final " + label.lower()) if index + 1 == total else "Your place in the set"}</span></div>'
        f'<div class="progress-track" role="progressbar" aria-label="{label} position" aria-valuemin="1" aria-valuemax="{total}" aria-valuenow="{index + 1}">'
        f'<span style="width:{percentage}%"></span></div></div>'
    )


def card_view(index):
    item = CARDS[index]
    return (index, position('Card', index, len(CARDS)), panel(item, item['front']),
            gr.update(value='', visible=False), source(item),
            gr.update(interactive=index > 0), gr.update(interactive=index < len(CARDS) - 1))


def card_previous(index): return card_view(move(index, -1, len(CARDS)))
def card_next(index): return card_view(move(index, 1, len(CARDS)))
def card_reset(): return card_view(0)


def reveal(index):
    end_note = ('<div class="end-note"><strong>End of this flashcard set.</strong> Take a moment to explain the principle in your own words. Use Reset Flashcards to review again.</div>'
                if index == len(CARDS) - 1 else '')
    return gr.update(value=(
        '<section class="answer-panel" role="status" aria-live="polite">'
        '<span class="section-kicker">Compare with your recall</span><h3>Answer</h3>'
        f'<p>{escape(CARDS[index]["back"])}</p>{end_note}</section>'
    ), visible=True)


def choices(item):
    return [(f'{key}. {value}', key) for key, value in item['options'].items()]


def question_view(index):
    item = QUESTIONS[index]
    return (index, position('Question', index, len(QUESTIONS)), panel(item, item['prompt']),
            gr.update(choices=choices(item), value=None), '', source(item),
            gr.update(interactive=index > 0), gr.update(interactive=index < len(QUESTIONS) - 1),
            gr.update(interactive=True))


def question_previous(index): return question_view(move(index, -1, len(QUESTIONS)))
def question_next(index): return question_view(move(index, 1, len(QUESTIONS)))
def question_reset(): return question_view(0)


def grade(index, choice):
    item = QUESTIONS[index]
    result = check_answer(item, choice)
    if result['answer'] is None:
        return ('<div class="feedback feedback-empty" role="status" aria-live="polite">'
                '<h3>Choose an answer</h3><p>Select A, B, or C, then choose Check Answer. '
                'You can take as much time as you need.</p></div>')
    key = item['answer']
    status_class = 'correct' if choice == key else 'incorrect'
    cue = 'Your reasoning is on track.' if choice == key else 'Use the explanation to refine your reasoning.'
    explanations = ''.join(
        f'<li class="rationale-row {"rationale-key" if letter == key else ""}">'
        f'<span class="option-letter">{letter}</span><div><h4>{"Why this is best" if letter == key else "Why this is less appropriate"}</h4>'
        f'<p>{escape(item["rationales"][letter])}</p></div></li>' for letter in 'ABC'
    )
    end_note = ('<div class="end-note"><strong>End of this practice set.</strong> Review the reasoning, then use Reset Practice to work through the questions again.</div>'
                if index == len(QUESTIONS) - 1 else '')
    return (
        f'<section class="feedback feedback-{status_class}" role="status" aria-live="polite">'
        f'<div class="feedback-heading"><span class="result-mark" aria-hidden="true">{"✓" if choice == key else "↗"}</span>'
        f'<div><h3>{result["status"]}</h3><p>{cue} {escape(result["message"])}</p></div></div>'
        f'<div class="correct-choice"><span class="section-kicker">The correct answer is {key}</span><p>{escape(item["options"][key])}</p></div>'
        f'<div class="rationale-section"><h4 class="rationale-title">Understand every option</h4><ul>{explanations}</ul></div>{end_note}</section>'
    )


def build_theme():
    """System fonts keep the interface fast and avoid external font requests."""
    return gr.themes.Base(
        primary_hue='violet', neutral_hue='slate',
        font=['Inter', 'Aptos', 'Segoe UI', 'Arial', 'sans-serif'],
        font_mono=['monospace'],
    ).set(
        body_background_fill='#f8f7fc', body_background_fill_dark='#f8f7fc',
        body_text_color='#1b2547', body_text_color_dark='#1b2547',
        body_text_color_subdued='#505b73', body_text_color_subdued_dark='#505b73',
        block_background_fill='#fffefb', block_background_fill_dark='#fffefb',
        block_border_color='#e0dcec', block_border_color_dark='#e0dcec',
        border_color_primary='#d7d0e8', border_color_primary_dark='#d7d0e8',
        button_primary_background_fill='#4b3bc4', button_primary_background_fill_dark='#4b3bc4',
        button_primary_background_fill_hover='#38299e', button_primary_background_fill_hover_dark='#38299e',
        button_primary_text_color='#ffffff', button_primary_text_color_dark='#ffffff',
        button_primary_border_color='#4b3bc4', button_primary_border_color_dark='#4b3bc4',
        button_secondary_background_fill='#fffefb', button_secondary_background_fill_dark='#fffefb',
        button_secondary_background_fill_hover='#eee9ff', button_secondary_background_fill_hover_dark='#eee9ff',
        button_secondary_text_color='#293658', button_secondary_text_color_dark='#293658',
        input_background_fill='#ffffff', input_background_fill_dark='#ffffff',
        input_border_color='#c8bfdc', input_border_color_dark='#c8bfdc',
    )


def build_app():
    with gr.Blocks(title=TITLE, analytics_enabled=False) as demo:
        gr.HTML(
            '<header class="landing">'
            '<div class="brand-line"><span class="brand-mark" aria-hidden="true">VE</span>'
            '<span>THE ETHICS STUDY ROOM</span><span class="edition-label">Clinical exam preparation</span></div>'
            '<div class="hero-grid"><div class="hero-copy"><p class="eyebrow">Small sessions. Stronger reasoning.</p>'
            '<h1>ASWB Values &amp; Ethics<br><em>Study Companion.</em></h1>'
            '<p class="hero-subtitle">Review ethical concepts. Practice applying them to real-world scenarios. '
            'Build confidence in the reasoning behind each answer.</p></div>'
            '<div class="content-stats" aria-label="Available study content">'
            '<div class="stat"><strong>06</strong><span>Selected topics</span></div>'
            '<div class="stat"><strong>12</strong><span>Flashcards</span></div>'
            '<div class="stat"><strong>10</strong><span>Practice questions</span></div>'
            '<p>Pick a card. Try a scenario.<br>One thoughtful step at a time.</p></div></div>'
            '<div class="getting-started"><span class="small-step">YOUR NEXT MOVE</span>'
            '<span>Choose an activity below. Recall a concept, or put your judgment into practice.</span></div>'
            '</header>'
        )
        with gr.Tabs(elem_id='study-tabs'):
            with gr.Tab('Flashcards', elem_id='flashcards-tab'):
                card_index = gr.State(0)
                gr.HTML('<div class="activity-intro"><div><span class="section-kicker">01 · Recall &amp; reveal</span><h2>Make the principles stick.</h2></div>'
                        '<p>Form your answer first. Reveal it when you are ready, then compare the reasoning.</p></div>')
                card_progress = gr.HTML(position('Card', 0, len(CARDS)))
                card_prompt = gr.HTML(panel(CARDS[0], CARDS[0]['front']))
                show = gr.Button('Show Answer', variant='primary', elem_classes=['main-action'])
                card_answer = gr.HTML('', visible=False)
                with gr.Row(elem_classes=['navigation-row']):
                    card_prev = gr.Button('Previous', interactive=False, elem_classes=['nav-button'])
                    card_forward = gr.Button('Next', elem_classes=['nav-button'])
                    card_restart = gr.Button('Reset Flashcards', elem_classes=['reset-button'])
                card_source = gr.HTML(source(CARDS[0]))
                card_outputs = [card_index, card_progress, card_prompt, card_answer, card_source, card_prev, card_forward]
                show.click(reveal, card_index, card_answer, api_name='reveal_card')
                card_prev.click(card_previous, card_index, card_outputs, api_name='previous_card')
                card_forward.click(card_next, card_index, card_outputs, api_name='next_card')
                card_restart.click(card_reset, None, card_outputs, api_name='reset_cards')
            with gr.Tab('Practice Questions', elem_id='questions-tab'):
                question_index = gr.State(0)
                gr.HTML('<div class="activity-intro"><div><span class="section-kicker">02 · Scenario challenge</span><h2>Think through the next step.</h2></div>'
                        '<p>Choose the best response for the facts given. Every option offers a chance to learn.</p></div>')
                question_progress = gr.HTML(position('Question', 0, len(QUESTIONS)))
                question_prompt = gr.HTML(panel(QUESTIONS[0], QUESTIONS[0]['prompt']))
                selection = gr.Radio(choices(QUESTIONS[0]), value=None, label='Your answer', interactive=True, elem_id='answer-options')
                check = gr.Button('Check Answer', variant='primary', elem_classes=['main-action'])
                feedback = gr.HTML('')
                with gr.Row(elem_classes=['navigation-row']):
                    question_prev = gr.Button('Previous', interactive=False, elem_classes=['nav-button'])
                    question_forward = gr.Button('Next', elem_classes=['nav-button'])
                    question_restart = gr.Button('Reset Practice', elem_classes=['reset-button'])
                question_source = gr.HTML(source(QUESTIONS[0]))
                question_outputs = [question_index, question_progress, question_prompt, selection, feedback, question_source, question_prev, question_forward, check]
                check.click(grade, [question_index, selection], feedback, api_name='check_answer', concurrency_id='practice')
                # Clear immediately in the browser; a queued clear can erase a
                # newer Check Answer result when the learner acts quickly.
                selection.input(None, None, feedback, js="() => ['']", queue=False, api_name=False)
                for button, handler, inputs, api_name in (
                    (question_prev, question_previous, question_index, 'previous_question'),
                    (question_forward, question_next, question_index, 'next_question'),
                    (question_restart, question_reset, None, 'reset_questions'),
                ):
                    button.click(None, None, [selection, feedback, check],
                                 js=PRACTICE_TRANSITION_JS, queue=False, api_name=False).then(
                        handler, inputs, question_outputs, api_name=api_name, concurrency_id='practice')
        gr.HTML(
            '<footer class="study-footer"><div class="footer-grid">'
            '<section><span class="section-kicker">Your study scope</span><h2>Six connected areas of ethics.</h2>'
            '<div class="scope-chips"><span>IA-1 · Confidentiality</span><span>IA-3 · Ethical dilemmas</span><span>IA-4 · Informed consent</span>'
            '<span>IB-1 · Self-determination</span><span>IB-2 · Boundaries</span><span>IC-4 · Accessibility</span></div>'
            '<p>This is selected-topic practice, not full exam coverage.</p></section>'
            '<section class="notice"><span class="section-kicker">Study responsibly</span><h2>Original, unofficial practice.</h2>'
            '<p>Educational material using fictional scenarios, not actual, recalled, or secure ASWB exam questions. '
            'Not legal or client-specific advice. Do not enter or use real client information. '
            'Laws vary by jurisdiction and change over time. Practice performance cannot predict an ASWB exam score.</p></section></div>'
            '<div class="footer-details"><p><strong>Source transparency.</strong> Content checked against the supplied ASWB Clinical Values and Ethics Knowledge Base 2026. '
            'Primary-source anchors are those named in the appendix; they have not been independently checked.</p>'
            '<p><strong>Keyboard.</strong> Use Tab / Shift+Tab between controls. Use arrow keys within answer choices; Space selects the focused answer. Enter or Space activates a tab or button. '
            'Your place is kept only for this session. Refreshing or resetting starts over.</p></div></footer>'
        )
        demo.load(None, None, None, js=RADIO_GROUP_JS, queue=False, api_name=False)
    return demo


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=int(os.environ.get('PORT', '7860')))
    parser.add_argument('--host', default=os.environ.get('GRADIO_SERVER_NAME', '0.0.0.0' if os.environ.get('SPACE_ID') else '127.0.0.1'))
    parser.add_argument('--share', action='store_true', help='Create a temporary public Gradio link.')
    args = parser.parse_args()
    build_app().queue(default_concurrency_limit=1).launch(
        server_name=args.host, server_port=args.port, share=args.share, inbrowser=False,
        theme=build_theme(), css=CSS, head=HEAD, show_error=False, footer_links=[], ssr_mode=False, run_history=False)
