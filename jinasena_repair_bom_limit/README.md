# Jinasena Repair BoM Limit

Restricts Repair Order lines to components defined in the Bill of Materials (BoM) of the product being repaired.

## Features
- Limits selectable repair line products to BoM components (including multi-level BoMs).
- Blocks invalid line items with a friendly `ValidationError` (API/import-safe).
- Shows an info message when the repaired product has no BoM.
- Dynamic refresh when changing the repaired product.
- Includes basic unit tests (positive and negative cases).

## Installation
1. Copy the module into your Odoo add-ons path.
2. Update the app list.
3. Install **Jinasena Repair BoM Limit**.

## Usage
1. Open a Repair Order.
2. Select a **Product to Repair**.
3. Add repair lines — only BoM components are available.
4. If there is no BoM, the list is empty and an info message is displayed.

## Known Limitations
- If multiple BoMs exist for a product, the default BoM returned by Odoo is used.
- The view inheritance targets the standard Odoo 17 Repair form view (`repair.mrp_repair_view_form`).

## Tests
Run the module tests using Odoo test runner:
- `-i jinasena_repair_bom_limit --test-enable`

## License
LGPL-3.0
