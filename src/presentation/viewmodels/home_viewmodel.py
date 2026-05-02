"""HomeViewModel – manages the state for the home page.

The view model sits between the UI (Flet controls) and the domain use cases.
It holds the current list of users, a loading flag and an error message so
that the view can render the correct state without containing any business
logic.
"""

from __future__ import annotations

from typing import Callable

from src.domain.entities.user import User
from src.domain.usecases.get_users import GetUsersUseCase


class HomeViewModel:
    """Reactive state container for the home page.

    The view model notifies the UI via a *notify* callback whenever its state
    changes.  Pass ``page.update`` (or any other callable) as the notifier.

    Args:
        get_users_use_case: Injected use case that fetches the user list.
        notify:             Callable invoked after every state change so the
                            UI can re-render.  Defaults to a no-op.
    """

    def __init__(
        self,
        get_users_use_case: GetUsersUseCase,
        notify: Callable[[], None] | None = None,
    ) -> None:
        self._get_users = get_users_use_case
        self._notify = notify or (lambda: None)

        self.users: list[User] = []
        self.is_loading: bool = False
        self.error_message: str = ""

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------

    def load_users(self) -> None:
        """Fetch all users and update state, then notify the UI."""
        self.is_loading = True
        self.error_message = ""
        self._notify()

        result = self._get_users.execute()

        if result.is_success:
            self.users = result.value  # type: ignore[assignment]
            self.error_message = ""
        else:
            self.users = []
            self.error_message = str(result.error)

        self.is_loading = False
        self._notify()
