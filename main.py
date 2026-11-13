from drafter import *
from dataclasses import dataclass
import csv
import io


COLOR_BLUE = "#4255ff"
COLOR_PURPLE = "#8b5cf6"
COLOR_GREEN = "#23b26d"
COLOR_RED = "#ff6b6b"
COLOR_YELLOW = "#ffcd1f" 
COLOR_GRAY = "#8a90a6"
COLOR_DARK = "#282e3e"

SUBJECT_COLORS = {
    "Biology": COLOR_GREEN,
    "Chemistry": COLOR_RED,
    "Math": COLOR_BLUE,
    "History": "#e8890c",
    "English": "#d946ef",
}
DEFAULT_SUBJECT_COLOR = COLOR_PURPLE


set_website_title("Study Site")
add_website_css("body", "background: linear-gradient(135deg, #4255ff 0%, #8b5cf6 100%); "
                        "font-family: 'Segoe UI', sans-serif; color: #ffffff; min-height: 100vh;")
add_website_css("h1, h2, h3", "color: white; text-shadow: 0 2px 4px rgba(0,0,0,0.2);")
add_website_css("button", "background: #ffcd1f; color: #282e3e; border: none; border-radius: 12px; "
                          "padding: 10px 20px; font-weight: 700; font-size: 1rem; cursor: pointer; "
                          "margin: 4px; transition: transform 0.1s;")
add_website_css("button:hover", "transform: translateY(-2px); background: #ffdb5c;")
add_website_css("input, select", "border-radius: 8px; border: 2px solid #d9dde8; padding: 8px; margin: 4px;")


@dataclass
class Flashcard:
    question: str
    answer: str
    subject: str
    topic: str
    correct_count: int
    incorrect_count: int
    needs_review: bool


@dataclass
class StudySession:
    subject: str
    mode: str
    correct_answers: int
    incorrect_answers: int


@dataclass
class State:
    flashcards: list[Flashcard]
    completed_sessions: list[StudySession]
    study_deck_indexes: list[int]
    current_card_position: int
    answer_is_visible: bool
    session_correct_count: int
    session_incorrect_count: int
    selected_subject: str
    selected_mode: str
    status_message: str


SAMPLE_CARDS = [
    ("What is the powerhouse of the cell?", "Mitochondrion", "Biology", "Cell Biology"),
    ("What is the basic unit of life?", "The cell", "Biology", "Cell Biology"),
    ("What is H2O?", "Water", "Chemistry", "Basics"),
    ("What is 7 x 8?", "56", "Math", "Multiplication"),
]


def create_flashcard(question_text: str, answer_text: str,
                     subject_name: str, topic_name: str) -> Flashcard:
    return Flashcard(question_text.strip(), answer_text.strip(),
                     subject_name.strip() or "General",
                     topic_name.strip() or "General",
                     0, 0, False)


def list_subjects(state: State) -> list[str]:
    subject_names = []
    for flashcard in state.flashcards:
        if flashcard.subject not in subject_names:
            subject_names.append(flashcard.subject)
    return subject_names


def get_subject_color(subject_name: str) -> str:
    return SUBJECT_COLORS.get(subject_name, DEFAULT_SUBJECT_COLOR)


def get_mastery_color(flashcard: Flashcard) -> str:
    if flashcard.needs_review:
        return COLOR_RED
    if flashcard.correct_count > 0:
        return COLOR_GREEN
    return COLOR_GRAY


def calculate_percent(correct_total: int, answered_total: int) -> int:
    if answered_total == 0:
        return 0
    return round(100 * correct_total / answered_total)


def build_navigation_bar() -> list:
    return [Button("Home", index),
            Button("Materials", materials_page),
            Button("Study", study_plan_page),
            Button("Progress", progress_page),
            HorizontalRule()]


def build_card_face(display_text: str, background_color: str) -> Div:
    return Div(
        Header(display_text, 2),
        style_background_color=background_color,
        style_color="white",
        style_padding="60px 30px",
        style_border_radius="20px",
        style_text_align="center",
        style_box_shadow="0 8px 24px rgba(0,0,0,0.25)",
        style_margin="20px auto",
        style_max_width="600px",
    )


def build_progress_bar(finished_count: int, total_count: int) -> Div:
    percent_done = calculate_percent(finished_count, total_count)
    return Div(
        Div(style_width=f"{percent_done}%",
            style_height="14px",
            style_background_color=COLOR_YELLOW,
            style_border_radius="8px"),
        style_background_color="rgba(255,255,255,0.3)",
        style_border_radius="8px",
        style_max_width="600px",
        style_margin="10px auto",
    )


def build_mastery_row(flashcard: Flashcard) -> Div:
    return Div(
        f"{flashcard.question}  -  {flashcard.answer}",
        style_background_color="white",
        style_color=COLOR_DARK,
        style_border_left=f"8px solid {get_mastery_color(flashcard)}",
        style_border_radius="8px",
        style_padding="10px 14px",
        style_margin="6px auto",
        style_max_width="600px",
    )


def parse_csv_text(csv_text: str) -> list[Flashcard]:
    all_rows = list(csv.reader(io.StringIO(csv_text)))
    imported_cards = []
    if not all_rows:
        return imported_cards

    header_names = [name.strip().lower() for name in all_rows[0]]
    if "question" in header_names and "answer" in header_names:
        question_column = header_names.index("question")
        answer_column = header_names.index("answer")
        subject_column = header_names.index("subject") if "subject" in header_names else -1
        topic_column = header_names.index("topic") if "topic" in header_names else -1
        all_rows = all_rows[1:]
    else:
        question_column, answer_column, subject_column, topic_column = 0, 1, 2, 3

    def read_cell(row: list, column_number: int) -> str:
        if 0 <= column_number < len(row):
            return row[column_number]
        return ""

    for row in all_rows:
        question_text = read_cell(row, question_column)
        answer_text = read_cell(row, answer_column)
        if question_text.strip() and answer_text.strip():
            imported_cards.append(create_flashcard(
                question_text, answer_text,
                read_cell(row, subject_column), read_cell(row, topic_column)))
    return imported_cards


@route
def index(state: State) -> Page:
    review_count = len([card for card in state.flashcards if card.needs_review])
    return Page(state, [
        Div(Header("Study Site", 1),
            "Import your own flashcards and turn them into study games.",
            style_text_align="center", style_margin="30px auto"),
        build_card_face(f"{len(state.flashcards)} cards loaded", COLOR_BLUE),
        build_card_face(f"{review_count} need review", COLOR_RED),
        build_card_face(f"{len(state.completed_sessions)} sessions done", COLOR_GREEN),
        Div(Button("My Materials", materials_page),
            Button("Start Studying", study_plan_page),
            Button("Progress", progress_page),
            style_text_align="center"),
    ])


@route
def materials_page(state: State) -> Page:
    page_content = build_navigation_bar() + [Header("My Materials", 2)]
    if state.status_message:
        page_content += [state.status_message, HorizontalRule()]

    page_content += [
        Header("Import a CSV", 3),
        "Columns: question, answer, subject, topic (subject and topic are optional).",
        LineBreak(),
        FileUpload("csv_file"),
        Button("Import CSV", import_csv_file),
        HorizontalRule(),
        Header("Add a card by hand", 3),
        "Question:", TextBox("question_text", ""), LineBreak(),
        "Answer:", TextBox("answer_text", ""), LineBreak(),
        "Subject:", TextBox("subject_name", ""), LineBreak(),
        "Topic:", TextBox("topic_name", ""), LineBreak(),
        Button("Add Card", add_manual_card),
        Button("Load Sample Cards", load_sample_cards),
        Button("Clear All Cards", clear_all_cards),
        HorizontalRule(),
        Header(f"Preview ({len(state.flashcards)} cards)", 3),
        "Gray = new, red = needs review, green = known",
    ]
    for flashcard in state.flashcards:
        page_content.append(build_mastery_row(flashcard))
    return Page(state, page_content)


@route
def import_csv_file(state: State, csv_file: bytes) -> Page:
    try:
        if isinstance(csv_file, bytes):
            csv_text = csv_file.decode("utf-8-sig")
        else:
            csv_text = str(csv_file)
        imported_cards = parse_csv_text(csv_text)
    except Exception:
        state.status_message = "Sorry, that file could not be read. Is it a UTF-8 CSV?"
        return materials_page(state)
    state.flashcards.extend(imported_cards)
    state.status_message = f"Imported {len(imported_cards)} cards."
    return materials_page(state)


@route
def add_manual_card(state: State, question_text: str, answer_text: str,
                    subject_name: str, topic_name: str) -> Page:
    if question_text.strip() and answer_text.strip():
        state.flashcards.append(
            create_flashcard(question_text, answer_text, subject_name, topic_name))
        state.status_message = "Card added."
    else:
        state.status_message = "Please fill in both a question and an answer."
    return materials_page(state)


@route
def load_sample_cards(state: State) -> Page:
    for question_text, answer_text, subject_name, topic_name in SAMPLE_CARDS:
        state.flashcards.append(
            create_flashcard(question_text, answer_text, subject_name, topic_name))
    state.status_message = "Sample cards loaded."
    return materials_page(state)


@route
def clear_all_cards(state: State) -> Page:
    state.flashcards = []
    state.status_message = "All cards cleared."
    return materials_page(state)


@route
def study_plan_page(state: State) -> Page:
    page_content = build_navigation_bar() + [Header("Study Plan", 2)]
    if not state.flashcards:
        page_content += ["You need some flashcards first.",
                         Button("Go to Materials", materials_page)]
        return Page(state, page_content)
    if state.status_message:
        page_content += [state.status_message, HorizontalRule()]
    page_content += [
        "Subject:",
        SelectBox("subject_choice", ["All"] + list_subjects(state), "All"),
        LineBreak(),
        "Which cards?",
        SelectBox("mode_choice", ["All cards", "Missed cards only"], "All cards"),
        LineBreak(),
        Button("Start Flashcards", start_study_session),
    ]
    return Page(state, page_content)


@route
def start_study_session(state: State, subject_choice: str, mode_choice: str) -> Page:
    chosen_indexes = []
    for card_index, flashcard in enumerate(state.flashcards):
        if subject_choice != "All" and flashcard.subject != subject_choice:
            continue
        if mode_choice == "Missed cards only" and not flashcard.needs_review:
            continue
        chosen_indexes.append(card_index)

    if not chosen_indexes:
        state.status_message = "No cards match those choices."
        return study_plan_page(state)

    state.study_deck_indexes = chosen_indexes
    state.current_card_position = 0
    state.answer_is_visible = False
    state.session_correct_count = 0
    state.session_incorrect_count = 0
    state.selected_subject = subject_choice
    state.selected_mode = mode_choice
    state.status_message = ""
    return flashcard_game_page(state)


@route
def flashcard_game_page(state: State) -> Page:
    current_card = state.flashcards[state.study_deck_indexes[state.current_card_position]]
    subject_color = get_subject_color(current_card.subject)
    cards_finished = state.current_card_position
    deck_size = len(state.study_deck_indexes)

    page_content = [
        Div(f"{current_card.subject} - {current_card.topic}",
            style_text_align="center", style_margin="16px"),
        build_progress_bar(cards_finished, deck_size),
        Div(f"Card {cards_finished + 1} of {deck_size}   "
            f"Correct: {state.session_correct_count}   Missed: {state.session_incorrect_count}",
            style_text_align="center"),
        build_card_face(current_card.question, subject_color),
    ]

    if state.answer_is_visible:
        page_content += [
            build_card_face(current_card.answer, COLOR_GREEN),
            Div("Did you know it?",
                Button("I knew it", mark_card_known,
                       style_background_color=COLOR_GREEN, style_color="white"),
                Button("I missed it", mark_card_missed,
                       style_background_color=COLOR_RED, style_color="white"),
                style_text_align="center"),
        ]
    else:
        page_content.append(
            Div(Button("Show Answer", show_answer), style_text_align="center"))

    page_content.append(
        Div(Button("Quit Session", results_page), style_text_align="center"))
    return Page(state, page_content)


@route
def show_answer(state: State) -> Page:
    state.answer_is_visible = True
    return flashcard_game_page(state)


def go_to_next_card(state: State) -> Page:
    state.answer_is_visible = False
    state.current_card_position += 1
    if state.current_card_position >= len(state.study_deck_indexes):
        return results_page(state)
    return flashcard_game_page(state)


@route
def mark_card_known(state: State) -> Page:
    current_card = state.flashcards[state.study_deck_indexes[state.current_card_position]]
    current_card.correct_count += 1
    current_card.needs_review = False
    state.session_correct_count += 1
    return go_to_next_card(state)


@route
def mark_card_missed(state: State) -> Page:
    current_card = state.flashcards[state.study_deck_indexes[state.current_card_position]]
    current_card.incorrect_count += 1
    current_card.needs_review = True
    state.session_incorrect_count += 1
    return go_to_next_card(state)


@route
def results_page(state: State) -> Page:
    answered_total = state.session_correct_count + state.session_incorrect_count
    if answered_total > 0:
        state.completed_sessions.append(StudySession(
            state.selected_subject, state.selected_mode,
            state.session_correct_count, state.session_incorrect_count))
    score_percent = calculate_percent(state.session_correct_count, answered_total)

    if answered_total == 0:
        summary_text = "No cards answered this time."
    elif score_percent >= 80:
        summary_text = f"Amazing! You scored {score_percent}%."
    elif score_percent >= 50:
        summary_text = f"Nice work! You scored {score_percent}%."
    else:
        summary_text = f"Keep going! You scored {score_percent}%."

    state.study_deck_indexes = []
    state.current_card_position = 0
    state.answer_is_visible = False

    return Page(state, [
        build_card_face(summary_text,
                        COLOR_GREEN if score_percent >= 50 else COLOR_PURPLE),
        Div(f"Correct: {state.session_correct_count}   Missed: {state.session_incorrect_count}",
            style_text_align="center"),
        Div(Button("Review Missed Cards", study_plan_page),
            Button("Progress", progress_page),
            Button("Home", index),
            style_text_align="center"),
    ])


@route
def progress_page(state: State) -> Page:
    page_content = build_navigation_bar() + [Header("Progress", 2)]
    if not state.completed_sessions:
        page_content.append("No sessions yet. Finish a study round to see results here.")
        return Page(state, page_content)

    for session_number, session in enumerate(state.completed_sessions, start=1):
        answered_total = session.correct_answers + session.incorrect_answers
        score_percent = calculate_percent(session.correct_answers, answered_total)
        page_content.append(Div(
            f"Session {session_number}: {session.subject} ({session.mode}) - "
            f"{score_percent}%  [{session.correct_answers}/{answered_total}]"))
        page_content.append(build_progress_bar(session.correct_answers, answered_total))
    return Page(state, page_content)


start_server(State([], [], [], 0, False, 0, 0, "All", "All cards", ""))
