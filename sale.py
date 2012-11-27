#This file is part sale_discount module for Tryton.
#The COPYRIGHT file at the top level of this repository contains
#the full copyright notices and license terms.
from decimal import Decimal
from trytond.model import fields
from trytond.pyson import Not, Equal, Eval
from trytond.pool import Pool, PoolMeta

__all__ = ['Sale', 'SaleLine']
__metaclass__ = PoolMeta


class Sale:
    'Sale'
    __name__ = 'sale.sale'

    def create_invoice(self, invoice_type):
        InvoiceLine = Pool().get('account.invoice.line')
        invoices = super(Sale, self).create_invoice(invoice_type)
        for line in self.lines:
            if line.discount != 0.0 and line.invoice_lines:
                InvoiceLine.write([line.invoice_lines[0]], {
                        'discount': line.discount,
                        })
        return invoices

    def create_shipment(self, shipment_type):
        Move = Pool().get('stock.move')
        shipments = super(Sale, self).create_shipment(shipment_type)
        for line in self.lines:
            if line.discount != 0.0 and line.moves:
                Move.write([line.moves[0]], {
                        'discount': line.discount,
                        })
        return shipments


class SaleLine:
    'Sale Line'
    __name__ = 'sale.line'

    discount = fields.Numeric('Discount %',
        digits=(16, Eval('currency_digits', 2)),
        states={
        'invisible': Not(Equal(Eval('type'), 'line')),
        }, on_change=['discount', 'product', 'quantity', 'type', 'unit_price'],
        depends=['type', 'unit_price', 'quantity', 'amount'])

    @staticmethod
    def default_discount():
        return Decimal(0.0)

    def on_change_discount(self):
        res = {}
        if self.quantity and self.discount and self.unit_price \
            and self.type == 'line':
            res['unit_price'] = (self.unit_price -
                self.unit_price * self.discount * Decimal('0.01'))
        return res

    def on_change_product(self):
        res = super(SaleLine, self).on_change_product()
        res['discount'] = Decimal(0.0)
        return res

    def on_change_quantity(self):
        res = super(SaleLine, self).on_change_quantity()
        res['discount'] = Decimal(0.0)
        return res
