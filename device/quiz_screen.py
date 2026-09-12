import os

import badger2040
import buttons
import quiz_engine
import state
import ui

QUIZ_PATH = "assets/quiz.json"
BOARD_PATH = "state/leaderboard.json"
ANSWER_BUTTONS = ("a", "b", "c")


def exists(path):
    try:
        os.stat(path)
        return True
    except OSError:
        return False


def header(d, left, right=""):
    d.set_pen(ui.BLACK)
    d.rectangle(0, 0, ui.WIDTH, ui.TAB_H)
    d.set_pen(ui.WHITE)
    d.set_font("bitmap8")
    d.text(left, 3, 2, 200, 1)
    if right:
        d.text(right, ui.WIDTH - 3 - d.measure_text(right, 1), 2, 100, 1)
    d.set_pen(ui.BLACK)


def draw_question(d, jpeg, q, number, total, score):
    ui.clear(d)
    header(d, "QUIZ {}/{}".format(number, total), "pts: {}".format(score))
    if q["type"] == "logo":
        ui.image(d, jpeg, "assets/" + q["image"], 8, 26, 80, 80)
        for i, option in enumerate(q["options"]):
            d.text("ABC"[i] + " " + option, 104, 22 + i * 34, 190, 2)
    else:
        d.text(q["question"], 4, 16, 288, 1)
        for i, option in enumerate(q["options"]):
            d.text("ABC"[i] + ") " + option, 4, 62 + i * 20, 288, 1)
    d.update()


def draw_feedback(d, q, chosen, number, total, score):
    ui.clear(d)
    header(d, "QUIZ {}/{}".format(number, total), "pts: {}".format(score))
    if chosen == q["answer"]:
        d.text("¡Bien!", 4, 18, 288, 3)
        explain_y = 48
    else:
        d.text("Nop...", 4, 18, 288, 3)
        d.text("Era: " + q["options"][q["answer"]], 4, 48, 288, 2)
        explain_y = 90
    d.text(q["explain"], 4, explain_y, 288, 1)
    d.text("Cualquier botón sigue", 4, 116, 288, 1)
    d.update()


def draw_result(d, score, total):
    ui.clear(d)
    header(d, "QUIZ", "fin")
    d.text("{}/{}".format(score, total), 4, 18, 288, 3)
    d.text(quiz_engine.title(score), 4, 50, 288, 2)
    d.text("Cualquier botón sigue", 4, 116, 288, 1)
    d.update()


def draw_initials(d, letters, pos):
    ui.clear(d)
    header(d, "TOP 5")
    d.text("¡Entraste al top 5!", 4, 16, 288, 2)
    for i, index in enumerate(letters):
        x = 100 + i * 34
        d.text(quiz_engine.LETTERS[index], x, 44, 40, 4)
        if i == pos:
            d.rectangle(x, 80, 24, 3)
    d.text("arriba/abajo: letra   B: ok", 4, 116, 288, 1)
    d.update()


def draw_board(d, board, highlight):
    ui.clear(d)
    header(d, "TOP 5")
    if not board:
        d.text("Nadie todavía", 4, 30, 288, 2)
    for i, row in enumerate(board):
        mark = ">" if i == highlight else " "
        d.text("{}{}. {}  {}".format(mark, i + 1, row["i"], row["s"]), 60, 16 + i * 20, 236, 2)
    d.text("Cualquier botón sale", 4, 118, 288, 1)
    d.update()


def _answer(d):
    button = buttons.wait(d)
    while button not in ANSWER_BUTTONS and button != "exit":
        button = buttons.wait(d)
    return button


def run(d, jpeg, rng):
    d.set_update_speed(badger2040.UPDATE_FAST)
    questions = state.load(QUIZ_PATH, [])
    round_ = quiz_engine.build_round(questions, rng, exists=lambda image: exists("assets/" + image))
    questions = None
    if not round_:
        return
    total = len(round_)
    score = 0
    for n, q in enumerate(round_):
        draw_question(d, jpeg, q, n + 1, total, score)
        button = _answer(d)
        if button == "exit":
            return
        chosen = ANSWER_BUTTONS.index(button)
        if chosen == q["answer"]:
            score += 1
        draw_feedback(d, q, chosen, n + 1, total, score)
        if buttons.wait(d) == "exit":
            return
    draw_result(d, score, total)
    if buttons.wait(d) == "exit":
        return
    board = state.load(BOARD_PATH, [])
    highlight = None
    if quiz_engine.qualifies(board, score):
        d.set_update_speed(badger2040.UPDATE_TURBO)
        letters, pos = [0, 0, 0], 0
        while pos < 3:
            draw_initials(d, letters, pos)
            button = buttons.wait(d)
            if button == "exit":
                return
            letters, pos = quiz_engine.step_initials(letters, pos, button)
        d.set_update_speed(badger2040.UPDATE_FAST)
        board, highlight = quiz_engine.insert_score(board, quiz_engine.initials_text(letters), score)
        state.save(BOARD_PATH, board)
    draw_board(d, board, highlight)
    buttons.wait(d)
