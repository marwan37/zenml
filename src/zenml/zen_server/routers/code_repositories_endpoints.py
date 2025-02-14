#  Copyright (c) ZenML GmbH 2023. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at:
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
#  or implied. See the License for the specific language governing
#  permissions and limitations under the License.
"""Endpoint definitions for code repositories."""

from typing import Optional, Union
from uuid import UUID

from fastapi import APIRouter, Depends, Security

from zenml.constants import API, CODE_REPOSITORIES, VERSION_1
from zenml.models import (
    CodeRepositoryFilter,
    CodeRepositoryRequest,
    CodeRepositoryResponse,
    CodeRepositoryUpdate,
    Page,
)
from zenml.zen_server.auth import AuthContext, authorize
from zenml.zen_server.exceptions import error_response
from zenml.zen_server.rbac.endpoint_utils import (
    verify_permissions_and_create_entity,
    verify_permissions_and_delete_entity,
    verify_permissions_and_get_entity,
    verify_permissions_and_list_entities,
    verify_permissions_and_update_entity,
)
from zenml.zen_server.rbac.models import ResourceType
from zenml.zen_server.routers.workspaces_endpoints import (
    router as workspace_router,
)
from zenml.zen_server.utils import (
    handle_exceptions,
    make_dependable,
    zen_store,
)

router = APIRouter(
    prefix=API + VERSION_1 + CODE_REPOSITORIES,
    tags=["code_repositories"],
    responses={401: error_response, 403: error_response},
)


@router.post(
    "",
    response_model=CodeRepositoryResponse,
    responses={401: error_response, 409: error_response, 422: error_response},
)
@workspace_router.post(
    "/{workspace_name_or_id}" + CODE_REPOSITORIES,
    response_model=CodeRepositoryResponse,
    responses={401: error_response, 409: error_response, 422: error_response},
)
@handle_exceptions
def create_code_repository(
    code_repository: CodeRepositoryRequest,
    workspace_name_or_id: Optional[Union[str, UUID]] = None,
    _: AuthContext = Security(authorize),
) -> CodeRepositoryResponse:
    """Creates a code repository.

    Args:
        code_repository: Code repository to create.
        workspace_name_or_id: Optional name or ID of the workspace.

    Returns:
        The created code repository.

    Raises:
        IllegalOperationError: If the workspace specified in the code repository
            does not match the current workspace.
    """
    if workspace_name_or_id:
        workspace = zen_store().get_workspace(workspace_name_or_id)
        code_repository.workspace = workspace.id

    return verify_permissions_and_create_entity(
        request_model=code_repository,
        resource_type=ResourceType.CODE_REPOSITORY,
        create_method=zen_store().create_code_repository,
    )


@router.get(
    "",
    response_model=Page[CodeRepositoryResponse],
    responses={401: error_response, 404: error_response, 422: error_response},
)
@workspace_router.get(
    "/{workspace_name_or_id}" + CODE_REPOSITORIES,
    response_model=Page[CodeRepositoryResponse],
    responses={401: error_response, 404: error_response, 422: error_response},
)
@handle_exceptions
def list_code_repositories(
    filter_model: CodeRepositoryFilter = Depends(
        make_dependable(CodeRepositoryFilter)
    ),
    workspace_name_or_id: Optional[Union[str, UUID]] = None,
    hydrate: bool = False,
    _: AuthContext = Security(authorize),
) -> Page[CodeRepositoryResponse]:
    """Gets a page of code repositories.

    Args:
        filter_model: Filter model used for pagination, sorting,
            filtering.
        workspace_name_or_id: Optional name or ID of the workspace.
        hydrate: Flag deciding whether to hydrate the output model(s)
            by including metadata fields in the response.

    Returns:
        Page of code repository objects.
    """
    if workspace_name_or_id:
        workspace = zen_store().get_workspace(workspace_name_or_id)
        filter_model.set_scope_workspace(workspace.id)

    return verify_permissions_and_list_entities(
        filter_model=filter_model,
        resource_type=ResourceType.CODE_REPOSITORY,
        list_method=zen_store().list_code_repositories,
        hydrate=hydrate,
    )


@router.get(
    "/{code_repository_id}",
    response_model=CodeRepositoryResponse,
    responses={401: error_response, 404: error_response, 422: error_response},
)
@handle_exceptions
def get_code_repository(
    code_repository_id: UUID,
    hydrate: bool = True,
    _: AuthContext = Security(authorize),
) -> CodeRepositoryResponse:
    """Gets a specific code repository using its unique ID.

    Args:
        code_repository_id: The ID of the code repository to get.
        hydrate: Flag deciding whether to hydrate the output model(s)
            by including metadata fields in the response.

    Returns:
        A specific code repository object.
    """
    return verify_permissions_and_get_entity(
        id=code_repository_id,
        get_method=zen_store().get_code_repository,
        hydrate=hydrate,
    )


@router.put(
    "/{code_repository_id}",
    response_model=CodeRepositoryResponse,
    responses={401: error_response, 404: error_response, 422: error_response},
)
@handle_exceptions
def update_code_repository(
    code_repository_id: UUID,
    update: CodeRepositoryUpdate,
    _: AuthContext = Security(authorize),
) -> CodeRepositoryResponse:
    """Updates a code repository.

    Args:
        code_repository_id: The ID of the code repository to update.
        update: The model containing the attributes to update.

    Returns:
        The updated code repository object.
    """
    return verify_permissions_and_update_entity(
        id=code_repository_id,
        update_model=update,
        get_method=zen_store().get_code_repository,
        update_method=zen_store().update_code_repository,
    )


@router.delete(
    "/{code_repository_id}",
    responses={401: error_response, 404: error_response, 422: error_response},
)
@handle_exceptions
def delete_code_repository(
    code_repository_id: UUID,
    _: AuthContext = Security(authorize),
) -> None:
    """Deletes a specific code repository.

    Args:
        code_repository_id: The ID of the code repository to delete.
    """
    verify_permissions_and_delete_entity(
        id=code_repository_id,
        get_method=zen_store().get_code_repository,
        delete_method=zen_store().delete_code_repository,
    )
