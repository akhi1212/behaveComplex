from typing import List
from dataclasses import dataclass

"""
    dataclasses library in python is inspired by POJO concept in java
    This library allows us to create customizable json objects with very less lines of code

    In the this file, we are creating a blueprint of payload schemas which is passed in as payloads to our 
    provision-controller REST API calls at test class level

    Consider each class below as an json object, for example ProvisionRecord class would be represented as
    {
        "imei": "{string}",
        "type": "{string}"
    }

    the actual json values are passed as an argument when an object instance of it is created like below within our test framework:
    provision_payload = ProvisionRecord("test-imei", "test-type")

    And later this object is converted into dictionaries to be passed as payload json into POST calls

    For more details please about the library and implementation here https://pypi.org/project/dataclasses/
"""


@dataclass
class ProvisionRecord:
    """
        Generate payload schema to upload single provision record
    """
    imei: str
    type: str


@dataclass
class FetchProvisionRecord:
    """
        Generates payload schema to fetch provision records
    """
    requests: List[ProvisionRecord]


@dataclass
class UploadMultipleProvisionRecords:
    """
        Generate payload schema to upload multiple provision records
    """
    records: List[ProvisionRecord]


@dataclass
class ProvisionPage:
    """
        Generate payload schema to fetch paginated provision records
    """
    maxCount: int
    type: str


@dataclass
class ProvisionPageByImei(ProvisionPage):
    """
        Generate payload schema to fetch paginated provision records with imei
    """
    imei: str


@dataclass
class JobStatusRecord:
    """
        Generate payload schema to POST job status records
    """
    jobId: str
    lastImei: str
