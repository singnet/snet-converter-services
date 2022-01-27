from blockfrost import BlockFrostApi, ApiUrls


def get_blockfrost_api_object(project_id, base_url):
    return BlockFrostApi(
        project_id=project_id,
        base_url=base_url,
    )
