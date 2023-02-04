import functools
import inspect
from typing import Union, TypeVar

import interactions
from interactions import BaseComponent, ComponentType, ActionRow, Listener, BaseCommand, InteractiveComponent
from interactions.ext.ui import UIComponent, Button, StringSelectMenu, UserSelectMenu
from interactions.ext.ui.base_ui import BaseUI
from interactions.ext.ui.components import (
    ChannelSelectMenu,
    RoleSelectMenu,
    MentionableSelectMenu,
    get_component_weight,
)

T = TypeVar("T", bound="UI")


class UI(BaseUI):
    """
    A class to create discord UI components.
    """

    _components: dict[str, Union[InteractiveComponent, UIComponent]]

    def __new__(cls, client: interactions.Client, *, timeout: float = 120, skip_gather: bool = False) -> T:
        instance = super().__new__(cls, client, timeout=timeout)

        instance._components = {}

        if not skip_gather:
            instance._gather_callbacks()

        instance.__event_hook.callback = functools.partial(instance.__event_hook.callback, instance)
        instance._client.add_command(instance.__event_hook)  # noqa
        return instance

    @classmethod
    def from_message(cls, message: interactions.Message, *, timeout: float = 120) -> T:
        ui = cls(message.client, timeout=timeout, skip_gather=True)
        for i, row in enumerate(message.components):
            for component in row.components:
                match component.type:
                    case ComponentType.BUTTON:
                        component = Button.from_dict(component.to_dict())
                    case ComponentType.STRING_SELECT:
                        component = StringSelectMenu.from_dict(component.to_dict())
                    case ComponentType.USER_SELECT:
                        component = UserSelectMenu.from_dict(component.to_dict())
                    case ComponentType.CHANNEL_SELECT:
                        component = ChannelSelectMenu.from_dict(component.to_dict())
                    case ComponentType.ROLE_SELECT:
                        component = RoleSelectMenu.from_dict(component.to_dict())
                    case ComponentType.MENTIONABLE_SELECT:
                        component = MentionableSelectMenu.from_dict(component.to_dict())
                    case _:
                        raise TypeError(f"Unknown component type {component.type}")
                component.row = i
                ui.add_component(component)
        return ui

    def _gather_callbacks(self) -> None:
        self.__invalidate_caches__()
        objects: list[str, list[InteractiveComponent | BaseCommand | Listener]] = inspect.getmembers(self, lambda x: isinstance(x, (BaseComponent, Listener, BaseCommand)))  # type: ignore
        for name, obj in objects:
            if isinstance(obj, (Listener, BaseCommand)):
                if obj is not self.__event_hook:
                    obj.callback = functools.partial(obj.callback, self)
                    self._client.add_command(obj)
            else:
                if getattr(obj, "type", ComponentType.ACTION_ROW) == ComponentType.ACTION_ROW:
                    self._logger.warning(f"ActionRow {name} is not a valid component, skipping")
                    continue
                if custom_id := getattr(obj, "custom_id", None):
                    self._components[custom_id] = obj
                else:
                    self._components[name] = obj
                    if hasattr(obj, "custom_id"):
                        obj.custom_id = name

    @interactions.listen()
    async def __event_hook(self, event: interactions.events.Component) -> None:
        """
        Called when a component is triggered.
        """
        if self._components.get(event.ctx.custom_id):
            self._logger.debug(f"Component {event.ctx.custom_id} triggered")

    @functools.cached_property
    def _ordered_(self) -> list[str]:
        # depending on how the class was defined, components may be in self.__dict__ or __class__.__dict__ or both
        return [key for key, val in (self.__dict__ | self.__class__.__dict__).items() if isinstance(val, BaseComponent)]

    def __invalidate_caches__(self) -> None:
        self.__dict__.pop("_ordered_", None)

    @property
    def components(self) -> list[Union[BaseComponent, UIComponent]]:
        """A list of all components in this UI."""
        return [getattr(self, name) for name in self._ordered_]

    @property
    def components_by_id(self) -> dict[str, Union[BaseComponent, UIComponent]]:
        """A dict of all components in this UI, keyed by their custom_id."""
        return {key: getattr(self, key) for key in self._ordered_}

    def add_component(self, component: Union[InteractiveComponent, UIComponent]) -> None:
        """Add a component to this UI."""
        if not hasattr(component, "custom_id"):
            raise TypeError("Component must support custom_id")

        if component.custom_id in self._components:
            raise ValueError(f"Component with custom_id {component.custom_id} already exists")
        self._components[component.custom_id] = component
        setattr(self, component.custom_id, component)
        self.__invalidate_caches__()

    def remove_component(self, component: Union[InteractiveComponent, UIComponent]) -> None:
        """Remove a component from this UI."""
        if not hasattr(component, "custom_id"):
            raise TypeError("Component must support custom_id")

        if component.custom_id not in self._components:
            raise ValueError(f"Component with custom_id {component.custom_id} does not exist")
        del self._components[component.custom_id]
        delattr(self, component.custom_id)
        self.__invalidate_caches__()

    def to_dict(self) -> list[dict]:
        """
        Convert this UI to a dict.
        """
        max_rows = 5
        max_weight = 5
        weights = [0] * max_rows
        rows = {i: [] for i in range(max_rows)}

        # determine if its even possible to fit all components
        total_weight = sum(get_component_weight(component) for component in self.components)
        if total_weight > max_weight * max_rows:
            raise ValueError(
                f"UI has no space to fit all components - Total weight: {total_weight}/{max_weight * max_rows}"
            )

        for component in [component for component in self.components if component.row is not None] + [
            component for component in self.components if component.row is None
        ]:
            weight = get_component_weight(component)
            if component.row is not None:
                if weights[component.row] + weight > max_weight:
                    raise ValueError(f"Row {component.row} has no space to fit {component}")
                rows[component.row].append(component)
                weights[component.row] += weight
            else:
                for i, row in enumerate(rows.values()):
                    if weights[i] + weight <= max_weight:
                        rows[i].append(component)
                        weights[i] += weight
                        break
                else:
                    raise ValueError(
                        f"UI can not fit all components due to specified rows, however, it is possible to fit all components if no rows are specified. Total weight: {total_weight}/{max_weight * max_rows}"
                    )
        return [ActionRow(*row).to_dict() for row in rows.values() if row]

    async def on_trigger(self, event: interactions.events.Component) -> None:
        """
        Called when a component is triggered.
        """
        ...
