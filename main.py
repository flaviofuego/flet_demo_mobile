"""Application entry point.

Dependency injection is wired here at the outermost layer so that every inner
layer stays free of concrete dependencies:

    main.py (wires DI)
        └─ presentation layer  (Flet pages + view models)
              └─ domain layer  (entities + use cases)
                    └─ data layer  (repositories + data sources)

To run locally::

    pip install flet
    python main.py

To run as a mobile app, follow the official Flet packaging guide:
https://flet.dev/docs/publish
"""

from __future__ import annotations

import flet as ft

from src.data.datasources.user_local_datasource import UserLocalDataSource
from src.data.repositories.user_repository_impl import UserRepositoryImpl
from src.domain.usecases.get_users import GetUsersUseCase
from src.presentation.pages.home_page import home_page
from src.presentation.viewmodels.home_viewmodel import HomeViewModel


def main(page: ft.Page) -> None:
    """Configure and launch the Flet application.

    Args:
        page: Root :class:`flet.Page` provided by the Flet runtime.
    """
    # ------------------------------------------------------------------ #
    # App-level settings                                                  #
    # ------------------------------------------------------------------ #
    page.title = "Flet Demo Mobile"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0

    # ------------------------------------------------------------------ #
    # Dependency injection (manual DI / poor-man's IoC container)        #
    # ------------------------------------------------------------------ #
    data_source = UserLocalDataSource()
    repository = UserRepositoryImpl(data_source=data_source)
    get_users_use_case = GetUsersUseCase(repository=repository)
    view_model = HomeViewModel(get_users_use_case=get_users_use_case)

    # ------------------------------------------------------------------ #
    # Router                                                              #
    # ------------------------------------------------------------------ #
    def route_change(e: ft.RouteChangeEvent) -> None:  # noqa: ARG001
        page.views.clear()

        if page.route == "/" or page.route == "":
            page.views.append(home_page(page, view_model))

        page.update()

    def view_pop(e: ft.ViewPopEvent) -> None:  # noqa: ARG001
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route or "/")


if __name__ == "__main__":
    ft.app(target=main)
