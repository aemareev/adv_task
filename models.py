from dataclasses import dataclass
from datetime import datetime


@dataclass
class IndexDataPoint:
    timestamp: datetime
    value: float


if __name__ == '__main__':
    point = IndexDataPoint(datetime.fromisoformat('2023-09-09T23:59:59.843845+03:00'), 267.59)
    print(point)
