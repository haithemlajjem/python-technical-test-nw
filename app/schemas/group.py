from infrastructure.models.group import GroupTypeEnum
from pydantic import BaseModel, ConfigDict, Field


class GroupBase(BaseModel):
    name: str = Field(..., example="Main Group")
    type: GroupTypeEnum = Field(..., example="group1")


class GroupCreate(GroupBase):
    """
    Schema for creating a group.
    """

    pass


class GroupUpdate(BaseModel):
    """
    Schema for updating a group.
    """

    name: str | None = Field(None, example="Updated Group Name")
    type: GroupTypeEnum | None = Field(None, example="group2")


class GroupResponse(GroupBase):
    """
    Response schema for a group.
    """

    id: int
    sites: list[int] = []  # List of site IDs
    child_groups: list[int] = []  # List of child group IDs

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm(cls, obj):
        data = obj.__dict__.copy()
        data["sites"] = [s.id for s in obj.sites] if obj.sites else []
        data["child_groups"] = (
            [c.id for c in obj.child_groups] if obj.child_groups else []
        )
        return cls.model_validate(data)
