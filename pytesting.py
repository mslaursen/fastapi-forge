import pydantic as p


class TestClass(p.BaseModel):
    name: str

    @p.computed_field
    @property
    def name_upper(self) -> str:
        return self.name.upper()


tc = TestClass(name="test")


print(tc.model_dump(round_trip=True))
