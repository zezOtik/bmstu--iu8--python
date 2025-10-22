.. bmstu_python_iu8 documentation master file, created by
   sphinx-quickstart on Mon Oct  20 09:00:55 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Nikulina
=========

Никулина Злата Евгеньевна ИУ8
---------------------------

В лабораторной работе №4 была составлена документация для классов интернет-магазина. Были описаны следующие классы:
::

    class UserSpec(BaseModel):
        uuser_id: int
        username: str = Field(..., pattern=RUS_RE)
        surname: str = Field(..., pattern=RUS_RE)
        second_name: Optional[str] = Field(None, pattern=RUS_RE)
        email: EmailStr
        status: Status

        model_config = ConfigDict(extra='forbid')


    class ProfileSpec(UserSpec):
        bio: str = Field(..., pattern=RUS_RE)
        url: HttpUrl


    class ItemSpec(BaseModel):
        item_id: int
        name: str = Field(..., pattern=RUS_RE)
        desc: str = Field(..., pattern=RUS_RE)
        price: float = Field(..., gt=0)

        model_config = ConfigDict(extra='forbid')


    class ServiceSpec(BaseModel):
        service_id: int
        name: str = Field(..., pattern=RUS_RE)
        desc: str = Field(..., pattern=RUS_RE)
        price: float = Field(..., gt=0)

        model_config = ConfigDict(extra='forbid')


    class OrderLineSpec(BaseModel):
        order_id: int
        order_line_id: int
        item_line: Union[ServiceSpec, ItemSpec]
        quantity: float = Field(..., gt=0)
        line_price: float = Field(..., gt=0)

        model_config = ConfigDict(extra='forbid')

        @model_validator(mode='after')
        def check_line_price(self):
            expected = self.quantity * self.item_line.price
            if self.line_price != expected:
                raise ValueError(
                    f'line_price не равно quantity * item_line.price '
                    f'({self.line_price} != {self.quantity} * '
                    f'{self.item_line.price} = {expected})'
                )
            return self


    class OrderSpec(BaseModel):
        order_id: int
        user_info: ProfileSpec
        items_line: List[OrderLineSpec]

        model_config = ConfigDict(extra='forbid')
        @model_validator(mode='after')
        def check_lines(self):
            if not self.items_line:
                raise ValueError('items_line пустой')

            seen: Set[int] = set()
            for ln in self.items_line:
                if ln.order_id != self.order_id:
                    raise ValueError(
                        'order_line.order_id должен '
                        'совпадать с order.order_id'
                    )
                if ln.order_line_id in seen:
                    raise ValueError(
                        f'повтор order_line_id '
                        f'внутри order {self.order_id}'
                    )
                seen.add(ln.order_line_id)
            return self



    class OrdersSpec(BaseModel):
        market_place_orders: List[OrderSpec]
        model_config = ConfigDict(extra='forbid')

        @model_validator(mode='after')
        def check_global_uniques(self):
            order_ids: Set[int] = set()
            user_ids: Set[int] = set()
            item_ids: Set[int] = set()
            service_ids: Set[int] = set()

            for o in self.market_place_orders:
                if o.order_id in order_ids:
                    raise ValueError(f'повторяющийся order_id: {o.order_id}')
                order_ids.add(o.order_id)

                uid = o.user_info.user_id
                if uid in user_ids:
                    raise ValueError(f'повторяющийся user_id: {uid}')
                user_ids.add(uid)

                for ln in o.items_line:
                    il = ln.item_line
                    if isinstance(il, ItemSpec):
                        if il.item_id in item_ids:
                            raise ValueError(
                                f'повторяющийся '
                                f'item_id: {il.item_id}'
                            )
                        item_ids.add(il.item_id)
                    else:
                        if il.service_id in service_ids:
                            raise ValueError(
                                f'повторяющийся '
                                f'service_id: {il.service_id}'
                            )
                        service_ids.add(il.service_id)
            return self

Документация была собрана с помоью Sphinx. Документация представлена в формате html.
В ней описаны классы путем следующий пунктов:
1. Атрибутов
2. Конфигурации
3. Валидации
4. Примера