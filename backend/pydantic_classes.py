from datetime import datetime, date, time
from typing import List, Optional, Union, Set
from enum import Enum
from pydantic import BaseModel, field_validator


############################################
# Enumerations are defined here
############################################

############################################
# Classes are defined here
############################################
class RecordCreate(BaseModel):
    numberOfPushups: int
    date: date
    user: int  # N:1 Relationship (mandatory)


class UserCreate(BaseModel):
    email: str
    name: str
    hasRecords: Optional[List[int]] = None  # 1:N Relationship


