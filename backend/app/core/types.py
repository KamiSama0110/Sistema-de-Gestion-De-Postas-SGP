from typing import Annotated

from fastapi import Path, Query
from pydantic import Field

MAX_INT32 = 2_147_483_647

IdPath = Annotated[int, Path(ge=1, le=MAX_INT32)]
IdQuery = Annotated[int | None, Query(ge=1, le=MAX_INT32)]
IdQueryReq = Annotated[int, Query(ge=1, le=MAX_INT32)]
Id = Annotated[int, Field(ge=1, le=MAX_INT32)]
IdOpcional = Annotated[int | None, Field(ge=1, le=MAX_INT32)]
