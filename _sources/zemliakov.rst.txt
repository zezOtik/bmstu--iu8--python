.. bmstu_python_iu8 documentation master file, created by
   sphinx-quickstart on Thu Oct  19 08:46:55 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Zemliakov
=========

Земляков Алексей Алексеевич
---------------------------

В лабораторной работе №4 была составлена документация для следующих классов:
::

    class UserSpec(BaseModel):
        user_id: int
        username: str = Field(min_length=1, pattern=russian_regular)
        surname: str = Field(min_length=1, pattern=russian_regular)
        second_name: Optional[str] = Field(pattern=russian_regular, default='')
        email: str = (
            Field(pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'))
        status: Literal['active', 'non-active']
        model_config = ConfigDict(extra='forbid')


    class ProfileSpec(UserSpec):
        bio: str = Field(min_length=1, pattern=russian_regular)
        url: str = Field(pattern=r'://')


    class ItemSpec(BaseModel):
        item_id: int
        name: str = Field(min_length=1, pattern=russian_regular)
        desc: str = Field(min_length=1, pattern=russian_regular)
        price: float = Field(gt=0)
        model_config = ConfigDict(extra='forbid')


    class ServiceSpec(BaseModel):
        service_id: int
        name: str = Field(min_length=1, pattern=russian_regular)
        desc: str = Field(min_length=1, pattern=russian_regular)
        price: float = Field(gt=0)
        model_config = ConfigDict(extra='forbid')


    class OrderLineSpec(BaseModel):
        order_id: int
        order_line_id: int
        item_line: ItemSpec
        quantity: float = Field(gt=0)
        line_price: Optional[float] = Field(gt=0, default=None)
        model_config = ConfigDict(extra='forbid')

        @model_validator(mode="after")
        def calculate_line_prices(self) -> Self:
            self.line_price = self.quantity * self.item_line.price
            return self


    class OrderSpec(BaseModel):
        order_id: int
        user_info: ProfileSpec
        order_lines: List[OrderLineSpec]
        model_config = ConfigDict(extra='forbid')


    class OrdersSpec(BaseModel):
        market_place_orders: List[OrderSpec]
        model_config = ConfigDict(extra='forbid')

Документация составлена при помощи пакета sphinx и экспортирована в html для удобства чтения.
Итоговую html страницу можно найти в docs_srs/build/html/index.html