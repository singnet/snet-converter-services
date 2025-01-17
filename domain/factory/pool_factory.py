from domain.entities.message_pool import MessagePool


class PoolFactory:

    @staticmethod
    def message_pool(row_id, id, name, message_group_id, is_enabled, created_by, created_at, updated_at):
        return MessagePool(row_id=row_id, id=id, name=name, message_group_id=message_group_id, is_enabled=is_enabled,
                           created_by=created_by, created_at=created_at, updated_at=updated_at)
