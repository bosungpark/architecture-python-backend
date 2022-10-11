from datetime import date
from typing import List, Optional

from allocation.domain import model
from allocation.domain.model import SKU, Batch, OrderLine, Reference
from allocation.service_layer.unit_of_work import AbstractUnitOfWork


class InvalidSku(Exception):
    pass

def is_valid_sku(sku: SKU, batches: List[Batch]):
    return sku in {b.sku for b in batches}

def allocate(orderid:str, sku:str, qty: int,
             uow: AbstractUnitOfWork)-> str:
    line: OrderLine = OrderLine(orderid=orderid, sku=sku, qty=qty)
    with uow:
        product= uow.products.get(sku=line.sku)
        if product is None:
            raise InvalidSku(f"Invalid sku {sku}")
        batchref: Reference = product.allocate(line)
        uow.commit()
    return batchref

def add_batch(
        ref: str, sku:str, qty: int, eta: Optional[date],
        uow: AbstractUnitOfWork
):
    with uow:
        product = uow.products.get(sku=sku)
        if product is None:
            product=model.Product(sku, batches=[])
            uow.products.add(product)
        product.batches.append(Batch(ref, sku, qty, eta))
        uow.commit()