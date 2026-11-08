"""A tiny Azure Table Storage adapter for each Discord user's virtual credits."""
import os
from azure.core.exceptions import ResourceNotFoundError
from azure.data.tables import TableServiceClient
from game import STARTING_BALANCE

TABLE_NAME = "PlayerBalances"


def _table():
    connection = os.environ.get("GAME_STORAGE_CONNECTION_STRING")
    if not connection:
        raise RuntimeError("Missing GAME_STORAGE_CONNECTION_STRING app setting")
    service = TableServiceClient.from_connection_string(connection)
    return service.get_table_client(TABLE_NAME)


def get_balance(user_id: str) -> int:
    """New users have 100 credits until they first play."""
    try:
        entity = _table().get_entity(partition_key="players", row_key=user_id)
        return int(entity["balance"])
    except ResourceNotFoundError:
        return STARTING_BALANCE


def set_balance(user_id: str, new_balance: int) -> None:
    """Demo-only write. See README: concurrent updates need ETags/idempotency."""
    _table().upsert_entity({
        "PartitionKey": "players",
        "RowKey": user_id,
        "balance": new_balance,
    })
