from config import get_settings
from general.services.utils_services import read_json_file
from pydantic import BaseModel, validator
from pydantic.typing import List


class DistinctionResponse(BaseModel):
    name: str


class DistinctionNumber(DistinctionResponse):
    number: int


class DistinctionNumberList(BaseModel):
    data: List[DistinctionNumber]


class DistinctionPayload(DistinctionResponse):

    @validator('name')
    def name_validator(cls, name):
        link = get_settings().base_dir + '/initial_data/distinction_feedback.json'
        distinction_lst = read_json_file(link)
        if not distinction_lst:
            raise EnvironmentError('the file could not be opened')

        if name not in distinction_lst:
            raise ValueError('value is not a valid distinction')
        return name
