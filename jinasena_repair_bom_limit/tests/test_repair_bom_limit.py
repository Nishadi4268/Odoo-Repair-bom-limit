from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestRepairBomLimit(TransactionCase):
    def setUp(self):
        super().setUp()
        self.company = self.env.company
        self.partner = self.env["res.partner"].create({"name": "Test Partner"})
        self.location_stock = self.env.ref("stock.stock_location_stock")
        self.location_customer = self.env.ref("stock.stock_location_customers")

        self.product_repair = self.env["product.product"].create(
            {
                "name": "Repair Product",
                "type": "product",
            }
        )
        self.component_ok = self.env["product.product"].create(
            {
                "name": "Component OK",
                "type": "product",
            }
        )
        self.component_bad = self.env["product.product"].create(
            {
                "name": "Component BAD",
                "type": "product",
            }
        )

        self.bom = self.env["mrp.bom"].create(
            {
                "product_tmpl_id": self.product_repair.product_tmpl_id.id,
                "product_qty": 1.0,
                "type": "normal",
            }
        )
        self.env["mrp.bom.line"].create(
            {
                "bom_id": self.bom.id,
                "product_id": self.component_ok.id,
                "product_qty": 1.0,
                "product_uom_id": self.component_ok.uom_id.id,
            }
        )

    def _create_repair(self):
        return self.env["mrp.repair"].create(
            {
                "product_id": self.product_repair.id,
                "product_qty": 1.0,
                "product_uom": self.product_repair.uom_id.id,
                "company_id": self.company.id,
                "partner_id": self.partner.id,
                "location_id": self.location_stock.id,
                "location_dest_id": self.location_customer.id,
            }
        )

    def _create_line_vals(self, repair, product):
        line_vals = {
            "repair_id": repair.id,
            "product_id": product.id,
            "product_uom_qty": 1.0,
            "product_uom": product.uom_id.id,
        }
        if "type" in self.env["mrp.repair.line"]._fields:
            line_vals["type"] = "add"
        return line_vals

    def test_allowed_component_can_be_added(self):
        repair = self._create_repair()
        line_vals = self._create_line_vals(repair, self.component_ok)
        line = self.env["mrp.repair.line"].create(line_vals)
        self.assertEqual(line.product_id, self.component_ok)

    def test_non_bom_component_is_blocked(self):
        repair = self._create_repair()
        line_vals = self._create_line_vals(repair, self.component_bad)
        with self.assertRaises(ValidationError):
            self.env["mrp.repair.line"].create(line_vals)
