def analyze_channel(channel_info: dict) -> str:
    """
    Accepts channel info dict, returns a summary string.
    For now: returns a mock response.
    """

    return (
        f"Mock analysis: '{channel_info.get('title')}' has "
        f"{channel_info.get('subscriber_count', 0)} subscribers. "
        f"Looks like a great channel!"
    )