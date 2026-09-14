import buttons


def drain(q, now):
    out = []
    while True:
        ev = q.pop(now)
        if ev is None:
            return out
        out.append(ev)


def test_events_come_out_in_order():
    q = buttons.ButtonQueue()
    q.push("a", 0)
    q.push("b", 10)
    q.push("c", 20)
    assert drain(q, 1000) == ["a", "b", "c"]


def test_same_button_is_debounced():
    q = buttons.ButtonQueue()
    q.push("a", 0)
    q.push("a", 30)
    q.push("a", 90)
    assert drain(q, 1000) == ["a", "a"]


def test_debounce_is_per_button():
    q = buttons.ButtonQueue()
    q.push("a", 0)
    q.push("b", 5)
    assert drain(q, 1000) == ["a", "b"]


def test_accept_edge_rejects_right_after_release():
    # Soltar en 90, apretar de nuevo en 100: sólo 10 ms desde la liberación,
    # bien por debajo de RELEASE_MS (30) — es rebote de liberación, no un
    # segundo toque real.
    assert buttons.accept_edge(0, 90, 100) is False


def test_accept_edge_accepts_after_release_and_press_windows_clear():
    # 40 ms desde la liberación (>=30) y 100 ms desde el último press aceptado
    # (>=60): toque real.
    assert buttons.accept_edge(0, 60, 100) is True


def test_accept_edge_rejects_within_press_debounce():
    assert buttons.accept_edge(0, -100000, 50) is False


def test_accept_edge_accepts_at_the_press_debounce_boundary():
    assert buttons.accept_edge(0, -100000, buttons.DEBOUNCE_MS) is True


def test_accept_edge_treats_negative_diffs_as_elapsed():
    # now_ms "antes" que el último press/release (envolvimiento de ticks_ms):
    # tratar como si ya hubiera pasado, no bloquear para siempre.
    assert buttons.accept_edge(1000, 1000, 0) is True


def test_push_raw_skips_debounce():
    q = buttons.ButtonQueue()
    q.push_raw("a", 0)
    q.push_raw("a", 1)
    q.push_raw("a", 2)
    assert drain(q, 1000) == ["a", "a", "a"]


def test_drain_moves_ring_events_into_queue_in_order():
    buttons._ring_idx[0] = buttons.NAMES.index("up")
    buttons._ring_ms[0] = 111
    buttons._ring_idx[1] = buttons.NAMES.index("down")
    buttons._ring_ms[1] = 222
    buttons._pos[0] = 2
    buttons._pos[1] = 0
    try:
        q = buttons.ButtonQueue()
        buttons.drain(q)
        assert drain(q, 1000) == ["up", "down"]
        assert buttons._pos[1] == 2
    finally:
        buttons._pos[0] = 0
        buttons._pos[1] = 0


def test_drain_wraps_around_the_ring():
    last = buttons.RING - 1
    buttons._ring_idx[last] = buttons.NAMES.index("a")
    buttons._ring_ms[last] = 5
    buttons._ring_idx[0] = buttons.NAMES.index("b")
    buttons._ring_ms[0] = 6
    buttons._pos[0] = 1
    buttons._pos[1] = last
    try:
        q = buttons.ButtonQueue()
        buttons.drain(q)
        assert drain(q, 1000) == ["a", "b"]
        assert buttons._pos[1] == 1
    finally:
        buttons._pos[0] = 0
        buttons._pos[1] = 0


def test_drain_stops_at_a_full_ring_without_overwriting_unread_slots():
    # head siempre queda un paso atrás de tail (un slot sacrificado) para
    # poder distinguir "lleno" de "vacío" sin un contador aparte.
    buttons._pos[0] = 5
    buttons._pos[1] = 6
    for i in range(buttons.RING):
        buttons._ring_idx[i] = buttons.NAMES.index("a")
        buttons._ring_ms[i] = i
    try:
        q = buttons.ButtonQueue()
        buttons.drain(q)
        assert len(drain(q, 1000)) == buttons.RING - 1
        assert buttons._pos[1] == buttons._pos[0]
    finally:
        buttons._pos[0] = 0
        buttons._pos[1] = 0


def test_source_hook_is_pulled_before_pending_and_pop():
    calls = []

    def source():
        calls.append(1)

    q = buttons.ButtonQueue(source=source)
    assert q.pending() is False
    assert q.pop(0) is None
    assert calls == [1, 1]


def test_chord_off_by_default_pops_up_and_down_immediately():
    q = buttons.ButtonQueue()
    assert q.chord is False
    q.push("up", 0)
    q.push("down", 50)
    assert q.pop(50) == "up"
    assert q.pop(50) == "down"


def test_up_down_close_together_is_exit_in_both_orders():
    q = buttons.ButtonQueue(chord=True)
    q.push("up", 0)
    q.push("down", 60)
    assert drain(q, 1000) == ["exit"]
    q = buttons.ButtonQueue(chord=True)
    q.push("down", 0)
    q.push("up", 149)
    assert drain(q, 1000) == ["exit"]


def test_up_down_far_apart_are_separate():
    q = buttons.ButtonQueue(chord=True)
    q.push("up", 0)
    q.push("down", 150)
    assert drain(q, 1000) == ["up", "down"]


def test_lone_up_waits_for_chord_window():
    q = buttons.ButtonQueue(chord=True)
    q.push("up", 1000)
    assert q.pop(1050) is None
    assert q.pending()
    assert q.pop(1150) == "up"
    assert not q.pending()


def test_lone_up_then_late_down_within_window_is_exit():
    q = buttons.ButtonQueue(chord=True)
    q.push("up", 1000)
    assert q.pop(1020) is None
    q.push("down", 1080)
    assert q.pop(1090) == "exit"


def test_up_followed_by_other_button_is_not_held():
    q = buttons.ButtonQueue(chord=True)
    q.push("up", 1000)
    q.push("a", 1010)
    assert q.pop(1020) == "up"
    assert q.pop(1020) == "a"


def test_clear_and_empty_pop():
    q = buttons.ButtonQueue()
    assert q.pop(0) is None
    q.push("a", 0)
    q.clear()
    assert not q.pending()
    assert q.pop(10) is None


def test_clear_drains_the_source_before_emptying():
    # Si clear() no drena primero, lo que la IRQ ya había juntado en el ring
    # queda ahí sin leer y el próximo pop() (que sí drena) lo devuelve —
    # justo lo que el quiz necesita evitar al limpiar después de cada refresco.
    calls = []

    def source():
        calls.append(1)
        if len(calls) == 1:
            q.push_raw("a", 0)

    q = buttons.ButtonQueue(source=source)
    q.clear()
    assert q.pop(0) is None


def test_diff_falls_back_to_plain_subtraction_on_cpython():
    assert buttons._diff(10, 3) == 7
