import re
from typing import Optional

from fastapi import Depends, HTTPException, status


class FilterParams:

    def __init__(self, display_type: Optional[list[str]] = None, fields: Optional[list[str]] = None):
        self.display_type: str = display_type
        self.fields: list(str) = fields

    def validate(self,
                 possible_fields: Optional[list] = None,
                 display_types: Optional[dict] = None) -> list[str]:
        if not self.fields and not self.display_type:
            self.fields = possible_fields

        if self.display_type:
            if self.display_type not in list(display_types.keys()):
                raise HTTPException(404, detail="inmvalid display type")  # todo Exception
            self.fields = display_types[self.display_type]

        for field in self.fields:
            if field not in possible_fields:
                raise HTTPException(
                    404, detail=f"inmvalid fiels name: {field}.  Possibilies are: {possible_fields}")  # todo Exception
        return self.fields


def filter_fields(fields: Optional[str] = None) -> list[str]:
    """Create filter fields list

    Args:
        fields (str): a comma-separated string with all the fields

    Returns:
        list[str]: The list of fields
    """
    if fields:
        pattern = re.compile(r'^[a-zA-Z_]+$')

        # Remove the last ',' if needed
        if fields[-1] == ',':
            fields = fields[:-1]
        # todo: re-ecrire les exceptions propre (DRY)
        if ' ' in fields:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=[
                {
                    "loc": [
                        "url",
                        "filter_fields",
                        "fields"
                    ],
                    "msg": 'Must not contain spaces',
                    "type": "value_error"
                }
            ])

        fields_list = fields.split(',')
        for field in fields_list:
            if not pattern.match(field):
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=[
                    {
                        "loc": [
                            "url",
                            "filter_fields",
                            field
                        ],
                        "msg": 'Not a valid value',
                        "type": "value_error"
                    }
                ])
            if len(field) > 16:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=[
                    {
                        "loc": [
                            "url",
                            "filter_fields",
                            field
                        ],
                        "msg": 'string is too long',
                        "type": "value_error"
                    }
                ])
        return fields_list
    return None


def filter_fields_with_display(display_type: Optional[str] = None,
                               fields: Optional[str] = Depends(filter_fields)):
    return FilterParams(display_type, fields)
