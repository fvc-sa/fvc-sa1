import io

import qrcode
import base64
from qrcode.image import pil, svg

from odoo import api, models


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    @api.model
    def get_qr_code(self, data):
        if data != "":
            factories = {
                "png": pil.PilImage,
                "svg": svg.SvgImage,
                "svg-fragment": svg.SvgFragmentImage,
                "svg-path": svg.SvgPathImage,
            }
            kwargs={}
            back_color = kwargs.pop("back_color", "white")
            fill_color = kwargs.pop("fill_color", "black")
            try:
                # Defaults to png if the argument is unknown
                image_factory = factories.get('png', pil.PilImage)
                qr = qrcode.QRCode(
                    box_size=4, border=5, image_factory=image_factory, **kwargs
                )
                qr.add_data(data)
                qr.make()
                img = qr.make_image(fill_color=fill_color, back_color=back_color)
                arr = io.BytesIO()
                img.save(arr)
                arr.seek(0)
                img_bytes = arr.read()
                base64_encoded_result_bytes = base64.b64encode(img_bytes)
                base64_encoded_result_str = base64_encoded_result_bytes.decode('ascii')
                return base64_encoded_result_str
            except Exception:
                raise ValueError("Cannot convert into barcode.")

    @api.model
    def qr_generate(self, value, box_size=4, border=5, factory="png", **kwargs):
        factories = {
            "png": pil.PilImage,
            "svg": svg.SvgImage,
            "svg-fragment": svg.SvgFragmentImage,
            "svg-path": svg.SvgPathImage,
        }

        back_color = kwargs.pop("back_color", "white")
        fill_color = kwargs.pop("fill_color", "black")
        try:
            # Defaults to png if the argument is unknown
            image_factory = factories.get(factory, pil.PilImage)
            qr = qrcode.QRCode(
                box_size=box_size, border=border, image_factory=image_factory, **kwargs
            )
            qr.add_data(value)
            qr.make()
            img = qr.make_image(fill_color=fill_color, back_color=back_color)
            arr = io.BytesIO()
            img.save(arr)
            return arr.getvalue()
        except Exception:
            raise ValueError("Cannot convert into barcode.")
