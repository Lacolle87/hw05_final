from datetime import datetime, timezone


def year(request):
    return {
        'year': datetime.now(timezone.utc).year
    }
