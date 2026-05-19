from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, cast

import pygame as pg
                                        
import config as C

# Perfil mais comum em controles PS3/genéricos mapeados pelo pygame.
_PS3_PERFIL = {
    "axis_left_x": 0,
    "axis_left_y": 1,
    "btn_shoot": 14,
    "btn_shoot_alt": 13,
    "btn_shoot_more": (5, 9),
    "btn_emp": 10,       # L1/LB
    "btn_emp_more": (8,),
    "btn_fenda": 11,     # R1/RB
    "btn_fenda_more": (),
    "btn_back": 0,
    "btn_start": 3,
}

_AXIS_TRIGGER_THRESHOLD = 0.5
JoyRef = Optional[Any]


@dataclass
class PlayerInput:
    rotate_left: bool = False
    rotate_right: bool = False
    thrust: bool = False
    shoot: bool = False
    emp_pressed: bool = False
    fenda_pressed: bool = False
    usando_joystick: bool = False


class InputManager:
    def __init__(self):
        pg.joystick.init()
        self._joy_rescan_requested = False
        self._joysticks: list[Any] = []
        self._joy_profiles: dict[int, dict[str, Any]] = {}
        self._keys = pg.key.get_pressed()
        self._prev_keys = self._keys
        self._cur_joy_btns: dict[int, dict[int, bool]] = {}
        self._prev_joy_btns: dict[int, dict[int, bool]] = {}
        self._cur_joy_axes: dict[int, dict[int, float]] = {}
        self._prev_joy_axes: dict[int, dict[int, float]] = {}
        self._refresh_joysticks()
        self._snapshot_joy_buttons()
        self._snapshot_joy_axes()

    def update(self):
        self._refresh_joysticks()
        self._prev_keys = self._keys
        self._keys = pg.key.get_pressed()
        self._prev_joy_btns = {jid: dict(btns) for jid, btns in self._cur_joy_btns.items()}
        self._prev_joy_axes = {jid: dict(axes) for jid, axes in self._cur_joy_axes.items()}
        self._snapshot_joy_buttons()
        self._snapshot_joy_axes()

    def inputs_por_jogador(self, num_jogadores: int) -> list[PlayerInput]:
        return [self._input_jogador(i) for i in range(num_jogadores)]

    def joysticks_conectados(self) -> list[str]:
        return [joy.get_name() for joy in self._joysticks]

    def marcar_scan_joystick(self) -> None:
        self._joy_rescan_requested = True

    def dispositivo_jogador(self, jogador_id: int) -> str:
        if jogador_id < len(self._joysticks):
            return self._joysticks[jogador_id].get_name()
        return "Teclado"

    def jogador_por_instance(self, instance_id: int) -> int | None:
        for i, joy in enumerate(self._joysticks):
            if joy.get_instance_id() == instance_id:
                return i
        return None

    def botao_back(self, instance_id: int, button: int) -> bool:
        p = self._joy_profiles.get(instance_id, {})
        return button == p.get("btn_back", C.JOY_BTN_BACK)

    def botao_start(self, instance_id: int, button: int) -> bool:
        p = self._joy_profiles.get(instance_id, {})
        btn_start = p.get("btn_start", C.JOY_BTN_START)
        btn_shoot = p.get("btn_shoot", C.JOY_BTN_SHOOT)
        btn_shoot_alt = p.get("btn_shoot_alt", C.JOY_BTN_SHOOT_ALT)
        return button in (btn_start, btn_shoot, btn_shoot_alt)

    def _input_jogador(self, jogador_id: int) -> PlayerInput:
        ctrl = C.CONTROLES[jogador_id]
        joy = self._joysticks[jogador_id] if jogador_id < len(self._joysticks) else None

        kb_left = bool(self._keys[ctrl["esq"]])
        kb_right = bool(self._keys[ctrl["dir"]])
        kb_up = bool(self._keys[ctrl["cima"]])
        kb_shoot = bool(self._keys[ctrl["fogo"]])
        kb_emp = bool(self._keys[ctrl["hiper"]]) and not bool(self._prev_keys[ctrl["hiper"]])
        kb_fenda = bool(self._keys[ctrl["fenda"]]) and not bool(self._prev_keys[ctrl["fenda"]])

        return PlayerInput(
            rotate_left=kb_left or self._joy_left(joy),
            rotate_right=kb_right or self._joy_right(joy),
            thrust=kb_up or self._joy_up(joy),
            shoot=kb_shoot or self._joy_shoot(joy),
            emp_pressed=kb_emp or self._joy_emp_just_pressed(joy),
            fenda_pressed=kb_fenda or self._joy_fenda_just_pressed(joy),
            usando_joystick=joy is not None,
        )

    def _refresh_joysticks(self):
        count = pg.joystick.get_count()
        if count == len(self._joysticks) and not self._joy_rescan_requested:
            return

        self._joy_rescan_requested = False
        for j in self._joysticks:
            try:
                j.quit()
            except pg.error:
                pass

        self._joysticks = []
        self._joy_profiles.clear()
        self._cur_joy_btns = {}
        self._prev_joy_btns = {}
        self._cur_joy_axes = {}
        self._prev_joy_axes = {}

        for i in range(count):
            try:
                joy = pg.joystick.Joystick(i)
                joy.init()
            except pg.error:
                continue
            self._joysticks.append(joy)
            jid = joy.get_instance_id()
            self._joy_profiles[jid] = self._resolver_profile(joy.get_name())

    def _snapshot_joy_buttons(self):
        for joy in self._joysticks:
            jid = joy.get_instance_id()
            self._cur_joy_btns[jid] = {
                b: bool(joy.get_button(b)) for b in range(joy.get_numbuttons())
            }

    def _snapshot_joy_axes(self):
        for joy in self._joysticks:
            jid = joy.get_instance_id()
            self._cur_joy_axes[jid] = {
                a: joy.get_axis(a) for a in range(joy.get_numaxes())
            }

    def _axis(self, joy: JoyRef, axis_id: int, default: float = 0.0) -> float:
        if joy is None or axis_id >= joy.get_numaxes():
            return default
        return joy.get_axis(axis_id)

    def _btn(self, joy: JoyRef, btn_id: int) -> bool:
        if joy is None or btn_id >= joy.get_numbuttons():
            return False
        return bool(joy.get_button(btn_id))

    def _btn_just_pressed(self, joy: JoyRef, btn_id: int) -> bool:
        if joy is None:
            return False
        jid = joy.get_instance_id()
        cur = self._cur_joy_btns.get(jid, {}).get(btn_id, False)
        prev = self._prev_joy_btns.get(jid, {}).get(btn_id, False)
        return cur and not prev

    def _axis_trigger_active(self, joy: JoyRef, axis_id: int) -> bool:
        if joy is None or axis_id < 0:
            return False
        val = self._cur_joy_axes.get(joy.get_instance_id(), {}).get(axis_id, -1.0)
        return val > _AXIS_TRIGGER_THRESHOLD

    def _axis_trigger_just_pressed(self, joy: JoyRef, axis_id: int) -> bool:
        if joy is None or axis_id < 0:
            return False
        jid = joy.get_instance_id()
        cur = self._cur_joy_axes.get(jid, {}).get(axis_id, -1.0)
        prev = self._prev_joy_axes.get(jid, {}).get(axis_id, -1.0)
        return cur > _AXIS_TRIGGER_THRESHOLD and prev <= _AXIS_TRIGGER_THRESHOLD

    def _hat(self, joy: JoyRef, hat_x: int, hat_y: int) -> bool:
        if joy is None or joy.get_numhats() <= 0:
            return False
        hx, hy = joy.get_hat(0)
        return (hat_x != 0 and hx == hat_x) or (hat_y != 0 and hy == hat_y)

    def _joy_left(self, joy: JoyRef) -> bool:
        ax = self._profile_value(joy, "axis_left_x", C.JOY_AXIS_LEFT_X)
        return self._axis(joy, ax) < -C.JOY_DEADZONE or self._hat(joy, -1, 0)

    def _joy_right(self, joy: JoyRef) -> bool:
        ax = self._profile_value(joy, "axis_left_x", C.JOY_AXIS_LEFT_X)
        return self._axis(joy, ax) > C.JOY_DEADZONE or self._hat(joy, 1, 0)

    def _joy_up(self, joy: JoyRef) -> bool:
        ay = self._profile_value(joy, "axis_left_y", C.JOY_AXIS_LEFT_Y)
        return self._axis(joy, ay) < -C.JOY_DEADZONE or self._hat(joy, 0, 1)

    def _joy_shoot(self, joy: JoyRef) -> bool:
        if joy is None:
            return False
        for bid in self._profile_shoot_buttons(joy):
            if self._btn(joy, bid):
                return True
        axis_r2 = self._profile_value(joy, "axis_r2", -1)
        if axis_r2 >= 0 and self._axis_trigger_active(joy, axis_r2):
            return True
        return False

    def _joy_emp_just_pressed(self, joy: JoyRef) -> bool:
        if joy is None:
            return False
        for bid in self._profile_emp_buttons(joy):
            if self._btn_just_pressed(joy, bid):
                return True
        axis_l2 = self._profile_value(joy, "axis_l2", -1)
        if axis_l2 >= 0 and self._axis_trigger_just_pressed(joy, axis_l2):
            return True
        return False

    def _joy_fenda_just_pressed(self, joy: JoyRef) -> bool:
        if joy is None:
            return False
        for bid in self._profile_fenda_buttons(joy):
            if self._btn_just_pressed(joy, bid):
                return True
        return False

    def _profile_value(self, joy: JoyRef, key: str, fallback: int) -> int:
        if joy is None:
            return fallback
        v = self._joy_profiles.get(joy.get_instance_id(), {}).get(key, fallback)
        return int(v) if isinstance(v, int) else fallback

    def _profile_shoot_buttons(self, joy: Any) -> tuple[int, ...]:
        p = self._joy_profiles.get(joy.get_instance_id(), {})
        out: list[int] = []
        for k in ("btn_shoot", "btn_shoot_alt"):
            v = p.get(k)
            if isinstance(v, int):
                out.append(v)
        extra = p.get("btn_shoot_more")
        if isinstance(extra, tuple):
            out.extend(cast(tuple[int, ...], extra))
        if not out:
            out = [C.JOY_BTN_SHOOT, C.JOY_BTN_SHOOT_ALT]
        return tuple(out)

    def _profile_emp_buttons(self, joy: Any) -> tuple[int, ...]:
        p = self._joy_profiles.get(joy.get_instance_id(), {})
        out: list[int] = []
        v = p.get("btn_emp")
        if isinstance(v, int):
            out.append(v)
        extra = p.get("btn_emp_more")
        if isinstance(extra, tuple):
            out.extend(cast(tuple[int, ...], extra))
        if not out:
            out = [C.JOY_BTN_EMP]
        return tuple(out)

    def _profile_fenda_buttons(self, joy: Any) -> tuple[int, ...]:
        p = self._joy_profiles.get(joy.get_instance_id(), {})
        out: list[int] = []
        v = p.get("btn_fenda")
        if isinstance(v, int):
            out.append(v)
        extra = p.get("btn_fenda_more")
        if isinstance(extra, tuple):
            out.extend(cast(tuple[int, ...], extra))
        if not out:
            out = [C.JOY_BTN_FENDA]
        return tuple(out)

    def _resolver_profile(self, nome: str) -> dict[str, Any]:
        n = nome.lower()

        if "xbox" in n:
            return {
                "axis_left_x": 0,
                "axis_left_y": 1,
                "btn_shoot": 0,
                "btn_shoot_alt": 7,
                "btn_shoot_more": (1, 2, 3),
                "btn_emp": 4,       # LB
                "btn_fenda": 5,     # RB
                "btn_back": 6,
                "btn_start": 7,
                "axis_r2": 5,
                "axis_l2": 4,
            }

        if (
            "ps3" in n
            or "playstation(r)3" in n
            or "playstation 3" in n
            or " p3" in n
            or n.startswith("p3")
            or "shanwan" in n
            or "usb gamepad" in n
            or "usb joystick" in n
            or "vibration joystick" in n
        ):
            return dict(_PS3_PERFIL)

        if (
            "playstation" in n
            or "dualshock" in n
            or "dual shock" in n
            or "dualsense" in n
            or "dual sense" in n
            or "sixaxis" in n
            or "wireless controller" in n
            or "ps4" in n
            or "ps 4" in n
            or "ps5" in n
            or "ps 5" in n
            or "sony interactive" in n
        ):
            return {
                "axis_left_x": 0,
                "axis_left_y": 1,
                "btn_shoot": 0,     # Cross/X
                "btn_shoot_alt": 7, # Options como fallback de selecao
                "btn_shoot_more": (1, 2, 3),
                "btn_emp": 4,       # L1
                "btn_emp_more": (6,),
                "btn_fenda": 5,     # R1
                "btn_back": 8,
                "btn_start": 9,
                "axis_r2": 5,
                "axis_l2": 4,
            }

        return {
            "axis_left_x": C.JOY_AXIS_LEFT_X,
            "axis_left_y": C.JOY_AXIS_LEFT_Y,
            "btn_shoot": C.JOY_BTN_SHOOT,
            "btn_shoot_alt": C.JOY_BTN_SHOOT_ALT,
            "btn_shoot_more": (1, 2, 3),
            "btn_emp": C.JOY_BTN_EMP,
            "btn_emp_more": (6, 10),
            "btn_fenda": C.JOY_BTN_FENDA,
            "btn_fenda_more": (11,),
            "btn_back": C.JOY_BTN_BACK,
            "btn_start": C.JOY_BTN_START,
        }
