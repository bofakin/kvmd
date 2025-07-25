
# ========================================================================== #
#                                                                            #
#    KVMD - The main PiKVM daemon.                                           #
#                                                                            #
#    Copyright (C) 2018-2024  Maxim Devaev <mdevaev@gmail.com>               #
#                                                                            #
#    This program is free software: you can redistribute it and/or modify    #
#    it under the terms of the GNU General Public License as published by    #
#    the Free Software Foundation, either version 3 of the License, or       #
#    (at your option) any later version.                                     #
#                                                                            #
#    This program is distributed in the hope that it will be useful,         #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of          #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           #
#    GNU General Public License for more details.                            #
#                                                                            #
#    You should have received a copy of the GNU General Public License       #
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.  #
#                                                                            #
# ========================================================================== #


import copy

from typing import AsyncGenerator
from typing import Any

from ...logging import get_logger

from ... import aiomulti

from ...yamlconf import Option

from ...validators.basic import valid_bool
from ...validators.basic import valid_int_f1
from ...validators.basic import valid_float_f01
from ...validators.os import valid_abs_path

from . import BaseHid


# =====
class Plugin(BaseHid):  # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        ignore_keys: list[str],
        mouse_x_range: dict[str, Any],
        mouse_y_range: dict[str, Any],
        jiggler: dict[str, Any],
    ) -> None:

        super().__init__(ignore_keys=ignore_keys, **mouse_x_range, **mouse_y_range, **jiggler)

        self.__notifier = aiomulti.AioProcessNotifier()

        common = {"notifier": self.__notifier}

        self.__mouses: dict[str, MouseProcess] = {}

    @classmethod
    def get_plugin_options(cls) -> dict:
        return {
            **cls._get_base_options(),
        }

    def sysprep(self) -> None:
        pass

    async def get_state(self) -> dict:
        return {
            "enabled": False,
            "online": False,
            "busy": False,
            "connected": None,
            "keyboard": {
                "online": False,
                "leds": {
                    "caps": False,
                    "scroll": False,
                    "num": False,
                },
                "outputs": {"available": [], "active": ""},
            },
            "mouse": {
                "absolute": True,
                "online": False,
                "outputs": {
                    "available": list(self.__mouses),
                    "active": "",
                },
            },
            **self._get_jiggler_state(),
        }

    async def trigger_state(self) -> None:
        self.__notifier.notify(1)

    async def poll_state(self) -> AsyncGenerator[dict, None]:
        prev: dict = {}
        while True:
            if (await self.__notifier.wait()) > 0:
                prev = {}
            new = await self.get_state()
            if new != prev:
                prev = copy.deepcopy(new)
                yield new

    async def reset(self) -> None:
        pass

    async def cleanup(self) -> None:
        pass

    # =====

    def set_params(
        self,
        keyboard_output: (str | None)=None,
        mouse_output: (str | None)=None,
        jiggler: (bool | None)=None,
    ) -> None:

        _ = keyboard_output
        _ = mouse_output
        if jiggler is not None:
            self._set_jiggler_active(jiggler)
            self.__notifier.notify()

    def _send_key_event(self, key: int, state: bool) -> None:
        pass

    def _send_mouse_button_event(self, button: int, state: bool) -> None:
        pass

    def _send_mouse_move_event(self, to_x: int, to_y: int) -> None:
        pass

    def _send_mouse_relative_event(self, delta_x: int, delta_y: int) -> None:
        pass

    def _send_mouse_wheel_event(self, delta_x: int, delta_y: int) -> None:
        pass

    def _clear_events(self) -> None:
        pass
