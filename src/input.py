<<<<<<< HEAD
from __future__ import annotations

=======
>>>>>>> 3819011 (feat(input): adiciona suporte a joystick no multiplayer)
from dataclasses import dataclass
import pygame as pg
import config as C


@dataclass
class PlayerInput:
    rotate_left: bool = False
    rotate_right: bool = False
    thrust: bool = False
    shoot: bool = False
    emp_pressed: bool = False
    usando_joystick: bool = False


class InputManager:
    def __init__(self):
        pg.joystick.init()
        self._joysticks: list[pg.joystick.Joystick] = []
        self._joy_profiles: dict[int, dict[str, int]] = {}
        self._keys = pg.key.get_pressed()
        self._prev_keys = self._keys
        self._cur_joy_btns: dict[int, dict[int, bool]] = {}
        self._prev_joy_btns: dict[int, dict[int, bool]] = {}
        self._refresh_joysticks()
        self._snapshot_joy_buttons()

    def update(self):
        self._refresh_joysticks()
        self._prev_keys = self._keys
        self._keys = pg.key.get_pressed()
        self._prev_joy_btns = {jid: dict(btns) for jid, btns in self._cur_joy_btns.items()}
        self._snapshot_joy_buttons()

    def inputs_por_jogador(self, num_jogadores: int) -> list[PlayerInput]:
        entradas: list[PlayerInput] = []
        for i in range(num_jogadores):
            entradas.append(self._input_jogador(i))
        return entradas

    def joysticks_conectados(self) -> list[str]:
        return [joy.get_name() for joy in self._joysticks]

    def dispositivo_jogador(self, jogador_id: int) -> str:
        if jogador_id < len(self._joysticks):
            joy = self._joysticks[jogador_id]
            return joy.get_name()
        return "Teclado"

    def jogador_por_instance(self, instance_id: int) -> int | None:
        for i, joy in enumerate(self._joysticks):
            if joy.get_instance_id() == instance_id:
                return i
        return None

    def _input_jogador(self, jogador_id: int) -> PlayerInput:
        ctrl = C.CONTROLES[jogador_id]
        joy = self._joysticks[jogador_id] if jogador_id < len(self._joysticks) else None

        kb_left = bool(self._keys[ctrl["esq"]])
        kb_right = bool(self._keys[ctrl["dir"]])
        kb_up = bool(self._keys[ctrl["cima"]])
        kb_shoot = bool(self._keys[ctrl["fogo"]])
        kb_emp_pressed = bool(self._keys[ctrl["hiper"]]) and not bool(self._prev_keys[ctrl["hiper"]])

        joy_left = self._joy_left(joy)
        joy_right = self._joy_right(joy)
        joy_up = self._joy_up(joy)
        joy_shoot = self._joy_shoot(joy)
        joy_emp_pressed = self._joy_emp_just_pressed(joy)

        return PlayerInput(
            rotate_left=kb_left or joy_left,
            rotate_right=kb_right or joy_right,
            thrust=kb_up or joy_up,
            shoot=kb_shoot or joy_shoot,
            emp_pressed=kb_emp_pressed or joy_emp_pressed,
            usando_joystick=joy is not None,
        )

    def _refresh_joysticks(self):
        count = pg.joystick.get_count()
        if count == len(self._joysticks):
            return
        self._joysticks = []
        for i in range(count):
            joy = pg.joystick.Joystick(i)
            joy.init()
            self._joysticks.append(joy)
            jid = joy.get_instance_id()
            self._joy_profiles[jid] = self._resolver_profile(joy.get_name())
        self._cur_joy_btns = {}
        self._prev_joy_btns = {}

    def _snapshot_joy_buttons(self):
        for joy in self._joysticks:
            jid = joy.get_instance_id()
            self._cur_joy_btns[jid] = {
                b: bool(joy.get_button(b))
                for b in range(joy.get_numbuttons())
            }

    def _axis(self, joy: pg.joystick.Joystick | None, axis_id: int, default: float = 0.0) -> float:
        if joy is None:
            return default
        if axis_id >= joy.get_numaxes():
            return default
        return joy.get_axis(axis_id)

    def _btn(self, joy: pg.joystick.Joystick | None, btn_id: int) -> bool:
        if joy is None:
            return False
        if btn_id >= joy.get_numbuttons():
            return False
        return bool(joy.get_button(btn_id))

    def _btn_just_pressed(self, joy: pg.joystick.Joystick | None, btn_id: int) -> bool:
        if joy is None:
            return False
        jid = joy.get_instance_id()
        cur = self._cur_joy_btns.get(jid, {}).get(btn_id, False)
        prev = self._prev_joy_btns.get(jid, {}).get(btn_id, False)
        return cur and not prev

    def _joy_left(self, joy: pg.joystick.Joystick | None) -> bool:
        axis_x = self._profile_value(joy, "axis_left_x", C.JOY_AXIS_LEFT_X)
        return self._axis(joy, axis_x) < -C.JOY_DEADZONE or self._hat(joy, -1, 0)

    def _joy_right(self, joy: pg.joystick.Joystick | None) -> bool:
        axis_x = self._profile_value(joy, "axis_left_x", C.JOY_AXIS_LEFT_X)
        return self._axis(joy, axis_x) > C.JOY_DEADZONE or self._hat(joy, 1, 0)

    def _joy_up(self, joy: pg.joystick.Joystick | None) -> bool:
        axis_y = self._profile_value(joy, "axis_left_y", C.JOY_AXIS_LEFT_Y)
        return self._axis(joy, axis_y) < -C.JOY_DEADZONE or self._hat(joy, 0, 1)

    def _joy_shoot(self, joy: pg.joystick.Joystick | None) -> bool:
        shoot = self._profile_value(joy, "btn_shoot", C.JOY_BTN_SHOOT)
        shoot_alt = self._profile_value(joy, "btn_shoot_alt", C.JOY_BTN_SHOOT_ALT)
        return self._btn(joy, shoot) or self._btn(joy, shoot_alt)

    def _joy_emp_just_pressed(self, joy: pg.joystick.Joystick | None) -> bool:
        emp = self._profile_value(joy, "btn_emp", C.JOY_BTN_EMP)
        return self._btn_just_pressed(joy, emp)

    def _hat(self, joy: pg.joystick.Joystick | None, hat_x: int, hat_y: int) -> bool:
        if joy is None or joy.get_numhats() <= 0:
            return False
        hx, hy = joy.get_hat(0)
        return (hat_x != 0 and hx == hat_x) or (hat_y != 0 and hy == hat_y)

    def _profile_value(self, joy: pg.joystick.Joystick | None, key: str, fallback: int) -> int:
        if joy is None:
            return fallback
        profile = self._joy_profiles.get(joy.get_instance_id(), {})
        return profile.get(key, fallback)

    def _resolver_profile(self, nome: str) -> dict[str, int]:
        n = nome.lower()
        if "xbox" in n:
            return {
                "axis_left_x": 0,
                "axis_left_y": 1,
                "btn_shoot": 7,
                "btn_shoot_alt": 5,
                "btn_emp": 4,
            }
        if "playstation" in n or "ps3" in n or "wireless controller" in n:
            return {
                "axis_left_x": 0,
                "axis_left_y": 1,
                "btn_shoot": 7,
                "btn_shoot_alt": 5,
                "btn_emp": 4,
            }
        return {
            "axis_left_x": C.JOY_AXIS_LEFT_X,
            "axis_left_y": C.JOY_AXIS_LEFT_Y,
            "btn_shoot": C.JOY_BTN_SHOOT,
            "btn_shoot_alt": C.JOY_BTN_SHOOT_ALT,
            "btn_emp": C.JOY_BTN_EMP,
        }
