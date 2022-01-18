from domain.entities.conversion_fee import ConversionFee


class ConversionFactory:
    @staticmethod
    def conversion_fee(id, percentage_from_source, created_by, created_at, updated_at):
        return ConversionFee(id=id, percentage_from_source=percentage_from_source, created_by=created_by,
                             created_at=created_at, updated_at=updated_at)

    @staticmethod
    def convert_conversion_fee_db_object_to_object(conversion_fee):
        if conversion_fee is None:
            return None

        return ConversionFactory.conversion_fee(id=conversion_fee.id,
                                                percentage_from_source=conversion_fee.percentage_from_source,
                                                created_by=conversion_fee.created_by,
                                                created_at=conversion_fee.created_at,
                                                updated_at=conversion_fee.updated_at
                                                )
