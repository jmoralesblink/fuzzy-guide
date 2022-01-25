import dataclasses
import uuid
from datetime import datetime, date, time
from decimal import Decimal
from json import JSONEncoder


class EnhancedJSONEncoder(JSONEncoder):
    """Extends the base JSONEncoder to support additional types"""

    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        # See "Date Time String Format" in the ECMA-262 specification (YYYY-MM-DDTHH:mm:ss.sssZ)
        if isinstance(o, datetime):
            iso = o.isoformat()  # ex: 2021-06-03T18:55:26.914391 or 2021-06-03T18:55:26.914391+00:00
            if o.microsecond:  # ensure the microseconds are only 3 digits
                iso = iso[:23] + iso[26:]
            if iso.endswith("+00:00"):  # use Z to represent UTC, instead of a 0 offset
                iso = iso[:-6] + "Z"
            return iso
        if isinstance(o, date):
            return o.isoformat()
        if isinstance(o, time):
            if o.utcoffset() is not None:
                raise ValueError("JSON can't represent timezone-aware times.")
            iso = o.isoformat()  # ex: 19:08:09.892751
            if o.microsecond:  # ensure the microseconds are only 3 digits
                iso = iso[:12]
            return iso
        if isinstance(o, Decimal):
            return float(str(o))
        elif isinstance(o, uuid.UUID):
            return str(o)

        return super().default(o)
