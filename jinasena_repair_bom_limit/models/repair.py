from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class MrpRepair(models.Model):
    _inherit = "mrp.repair"

    allowed_component_ids = fields.Many2many(
        comodel_name="product.product",
        compute="_compute_allowed_component_ids",
        string="Allowed Components",
        help="Products allowed on repair lines based on the BoM of the product to repair.",
    )
    show_no_bom_info = fields.Boolean(
        compute="_compute_allowed_component_ids",
        string="Show No BoM Info",
    )

    @api.depends("product_id", "company_id")
    def _compute_allowed_component_ids(self):
        for repair in self:
            components = repair._get_bom_components(repair.product_id)
            repair.allowed_component_ids = components
            repair.show_no_bom_info = bool(repair.product_id) and not components

    def _get_bom_components(self, product):
        self.ensure_one()
        if not product:
            return self.env["product.product"]
        bom = self.env["mrp.bom"]._bom_find(
            product=product, company_id=self.company_id.id
        )
        if not bom:
            return self.env["product.product"]

        result = self.env["product.product"]
        seen_boms = set()
        repair = self

        def _collect(bom_record):
            nonlocal result
            if not bom_record or bom_record.id in seen_boms:
                return
            seen_boms.add(bom_record.id)
            for line in bom_record.bom_line_ids:
                result_products = repair._get_line_products(line)
                result |= result_products

                child_bom = line.child_bom_id
                if not child_bom:
                    child_bom = self.env["mrp.bom"]._bom_find(
                        product=line.product_id or line.product_tmpl_id.product_variant_id,
                        company_id=self.company_id.id,
                    )
                _collect(child_bom)
        _collect(bom)
        return result

    def _get_line_products(self, line):
        if line.product_id:
            return line.product_id
        if line.product_tmpl_id:
            return line.product_tmpl_id.product_variant_ids
        return self.env["product.product"]

    @api.onchange("product_id")
    def _onchange_product_id_allowed_components(self):
        for repair in self:
            if repair.product_id and not repair.allowed_component_ids:
                return {
                    "warning": {
                        "title": _("No Bill of Materials"),
                        "message": _(
                            "No BoM found for the selected product. Add lines are restricted "
                            "until a BoM is defined."
                        ),
                    }
                }
        return {}


class MrpRepairLine(models.Model):
    _inherit = "mrp.repair.line"

    @api.onchange("repair_id")
    def _onchange_repair_id_product_domain(self):
        if self.repair_id:
            return {
                "domain": {
                    "product_id": [
                        ("id", "in", self.repair_id.allowed_component_ids.ids)
                    ]
                }
            }
        return {"domain": {"product_id": []}}

    @api.constrains("product_id", "repair_id")
    def _check_product_in_bom(self):
        for line in self:
            if not line.product_id or not line.repair_id:
                continue
            allowed = line.repair_id.allowed_component_ids
            if not allowed:
                raise ValidationError(
                    _(
                        "No Bill of Materials found for the product being repaired. "
                        "Repair lines are not allowed until a BoM is defined."
                    )
                )
            if line.product_id not in allowed:
                raise ValidationError(
                    _(
                        "You can only add BoM components of the product being repaired "
                        "to repair lines."
                    )
                )
