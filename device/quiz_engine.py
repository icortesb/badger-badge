ROUND_LEVELS = (1, 1, 1, 2, 2, 2, 2, 3, 3, 3)
TITLES = (
    (10, "10x dev (o googleaste)"),
    (7, "Senior que deploya los viernes"),
    (4, "En mi máquina anda"),
    (0, "Junior de Stack Overflow"),
)
BOARD_SIZE = 5
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def shuffled(items, rng):
    out = list(items)
    for i in range(len(out) - 1, 0, -1):
        j = rng.randint(0, i)
        out[i], out[j] = out[j], out[i]
    return out


def _pick(questions, used, level, qtype, rng):
    candidates = [
        i for i, q in enumerate(questions)
        if i not in used
        and (level is None or q["level"] == level)
        and (qtype is None or q["type"] == qtype)
    ]
    if not candidates:
        return None
    return candidates[rng.randint(0, len(candidates) - 1)]


def _prepare(question, rng):
    correct = question["options"][question["answer"]]
    prepared = dict(question)
    prepared["options"] = shuffled(question["options"], rng)
    prepared["answer"] = prepared["options"].index(correct)
    return prepared


def build_round(questions, rng, exists=None):
    usable = [
        q for q in questions
        if q["type"] != "logo" or exists is None or exists(q["image"])
    ]
    used = set()
    result = []
    for slot, level in enumerate(ROUND_LEVELS):
        wanted = "logo" if slot % 2 == 0 else "trivia"
        index = _pick(usable, used, level, wanted, rng)
        if index is None:
            index = _pick(usable, used, level, None, rng)
        if index is None:
            index = _pick(usable, used, None, None, rng)
        if index is None:
            break
        used.add(index)
        result.append(_prepare(usable[index], rng))
    return result


def title(score):
    for minimum, name in TITLES:
        if score >= minimum:
            return name
    return TITLES[-1][1]


def qualifies(board, score):
    return len(board) < BOARD_SIZE or score > board[-1]["s"]


def insert_score(board, initials, score):
    pos = len(board)
    for i, row in enumerate(board):
        if score > row["s"]:
            pos = i
            break
    if pos >= BOARD_SIZE:
        return list(board), None
    new = list(board[:pos]) + [{"i": initials, "s": score}] + list(board[pos:])
    return new[:BOARD_SIZE], pos


def step_initials(letters, pos, button):
    letters = list(letters)
    if pos >= 3:
        return letters, pos
    if button == "up":
        letters[pos] = (letters[pos] + 1) % len(LETTERS)
    elif button == "down":
        letters[pos] = (letters[pos] - 1) % len(LETTERS)
    elif button == "b":
        pos += 1
    return letters, pos


def initials_text(letters):
    return "".join(LETTERS[i] for i in letters)


def bump_rounds(stats):
    rounds = stats.get("rounds", 0)
    if not isinstance(rounds, int) or isinstance(rounds, bool) or rounds < 0:
        rounds = 0
    new_stats = dict(stats)
    new_stats["rounds"] = rounds + 1
    return new_stats
