"""Use case: retrieve the list of all users.

Use cases (also called *interactors*) orchestrate domain objects and
repository calls.  They receive their dependencies via constructor
injection, which keeps them easy to test in isolation.
"""

from __future__ import annotations

from src.core.error.exceptions import DataException
from src.core.utils.result import Failure, Result, Success
from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository


class GetUsersUseCase:
    """Fetch all users from the repository.

    Args:
        repository: Concrete implementation of :class:`UserRepository`
                    injected at construction time.
    """

    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def execute(self) -> Result[list[User]]:
        """Run the use case and return a :class:`~src.core.utils.result.Result`.

        Returns:
            ``Success(users)`` when the operation succeeds, even if the list
            is empty.  ``Failure(error)`` when the repository raises.
        """
        try:
            users = self._repository.get_all()
            return Success(users)
        except Exception as exc:  # noqa: BLE001
            return Failure(DataException(str(exc)))
