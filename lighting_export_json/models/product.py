# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import json

from odoo import _, api, fields, models


def _values2range(values, _range, magnitude=None):
    ranges = []
    for w in values:
        for r in _range:
            _min, _max = r
            if _min <= w and w < _max:
                if r not in ranges:
                    ranges.append(r)
                    break

    ranges_str = []
    for _min, _max in sorted(ranges):
        if _min != float("-inf") and _max != float("inf"):
            _range = "%i - %i" % (_min, _max)
        elif _min != float("-inf") and _max == float("inf"):
            _range = "> %i" % _min
        elif _min == float("-inf") and _max != float("inf"):
            _range = "< %i" % _max
        else:
            _range = "-\u221E - \u221E"

        if magnitude:
            _range = "%s%s" % (_range, magnitude)

        ranges_str.append(_range)

    return ranges_str


def get_group_type(group, typ):
    if typ in group.mapped("type_ids.code"):
        return group
    else:
        if group.parent_id:
            return get_group_type(group.parent_id, typ)

    return None


class LightingProduct(models.Model):
    _inherit = "lighting.product"

    # auxiliary function to get non db translations
    def _(self, string):
        return _(string)

    # Auxiliar fields
    finish_group_name = fields.Char(
        compute="_compute_finish_group_name",
    )

    def _compute_finish_group_name(self):
        for rec in self:
            if "FINISH" in rec.product_group_id.type_ids.mapped("code"):
                rec.finish_group_name = rec.product_group_id.name
            else:
                rec.finish_group_name = rec.reference

    photo_group_id = fields.Many2one(
        comodel_name="lighting.product.group",
        compute="_compute_foto_group",
    )

    def _compute_foto_group(self):
        for rec in self:
            if rec.product_group_id:
                rec.photo_group_id = get_group_type(rec.product_group_id, "PHOTO")
            else:
                rec.photo_group_id = False

    group_description = fields.Char(
        compute="_compute_group_description",
    )

    def _compute_group_description(self):
        for rec in self:
            if rec.configurator:
                rec.group_description = rec.description
            else:
                description_l = filter(
                    lambda x: x,
                    [
                        rec.category_id
                        and rec.category_id.description_text
                        or rec.category_id.name,
                        rec.photo_group_id
                        and rec.photo_group_id.alt_name
                        or rec.photo_group_id.name,
                    ],
                )

                description = " ".join(description_l)
                if description:
                    rec.group_description = description
                else:
                    rec.group_description = False

    category_complete_ids = fields.Many2many(
        string="Export Category Complete",
        comodel_name="lighting.product.category",
        compute="_compute_category_complete_ids",
    )

    def _compute_category_complete_ids(self):
        for rec in self:
            rec.category_complete_ids = rec.category_id.complete_chain_ids

    # Display fields

    json_display_finish_group_name = fields.Char(
        string="Finish group name JSON Display",
        compute="_compute_json_display_finish_group_name",
    )

    def _compute_json_display_finish_group_name(self):
        for rec in self:
            if rec.finish_group_name != rec.reference:
                rec.json_display_finish_group_name = rec.finish_group_name
            else:
                rec.json_display_finish_group_name = False

    # Display finishes
    def _get_finish_json(self, template_id, finish):
        finish_d = {}
        finish_lang_d = {}
        for lang in template_id.lang_ids.mapped("code"):
            finish_lang_d[lang] = finish.with_context(lang=lang).name
        if finish_lang_d:
            finish_d.update({"description": finish_lang_d})
        if finish.html_color:
            finish_d.update({"html_color": finish.html_color})
        if finish_d:
            return json.dumps(finish_d)

    # Display Finish
    json_display_finish = fields.Serialized(
        string="Finish JSON Display",
        compute="_compute_json_display_finish",
    )

    @api.depends(
        "finish_id", "finish_id.code", "finish_id.name", "finish_id.html_color"
    )
    def _compute_json_display_finish(self):
        template_id = self.env.context.get("template_id")
        if template_id:
            for rec in self:
                if rec.finish_id:
                    finish_d = self._get_finish_json(template_id, rec.finish_id)
                    if finish_d:
                        rec.json_display_finish = finish_d
                    else:
                        rec.json_display_finish = False
                else:
                    rec.json_display_finish = False
        else:
            self.json_display_finish = False

    # Display Finish2
    json_display_finish2 = fields.Serialized(
        string="Finish2 JSON Display",
        compute="_compute_json_display_finish2",
    )

    @api.depends(
        "finish2_id", "finish2_id.code", "finish2_id.name", "finish2_id.html_color"
    )
    def _compute_json_display_finish2(self):
        template_id = self.env.context.get("template_id")
        if template_id:
            for rec in self:
                if rec.finish2_id:
                    finish_d = self._get_finish_json(template_id, rec.finish2_id)
                    if finish_d:
                        rec.json_display_finish2 = finish_d
                    else:
                        rec.json_display_finish2 = False
                else:
                    rec.json_display_finish2 = False
        else:
            self.json_display_finish2 = False

    # Display Attachments
    json_display_attachment = fields.Serialized(
        string="Attachments JSON Display",
        compute="_compute_json_display_attachment",
    )

    @api.depends(
        "attachment_ids.datas_fname",
        "attachment_ids.sequence",
        "attachment_ids.attachment_id.store_fname",
        "attachment_ids.type_id.code",
        "attachment_ids.type_id.name",
    )
    def _compute_json_display_attachment(self):
        template_id = self.env.context.get("template_id")
        if template_id:
            for rec in self:
                # map attach type with order
                attachment_order_d = {
                    x.type_id: (x.sequence, x.id) for x in template_id.attachment_ids
                }
                attachment_max_d = {
                    x.type_id: x.max_count for x in template_id.attachment_ids
                }

                # classify
                attachment_type_d = {}
                for a in rec.attachment_ids.filtered(
                    lambda x: x.datas_location == "file"
                ):
                    attach_type = a.type_id
                    if attach_type in attachment_order_d:
                        if attach_type not in attachment_type_d:
                            attachment_type_d[attach_type] = self.env[
                                "lighting.attachment"
                            ]
                        attachment_type_d[attach_type] |= a

                # final attachment sort and formatting
                if attachment_type_d:
                    attachment_l = []
                    for attach_type, attachs in sorted(
                        attachment_type_d.items(),
                        key=lambda x: attachment_order_d[x[0]],
                    ):
                        attachs_date = attachs.sorted(
                            lambda x: (fields.Date.from_string(x.write_date), x.id),
                            reverse=True,
                        )
                        max_idx = attachment_max_d[attach_type]
                        if max_idx < 0:
                            max_idx = len(attachs_date)
                        for a in attachs_date[:max_idx]:
                            attachment_d = {
                                "datas_fname": a.datas_fname,
                                "store_fname": a.attachment_id.store_fname,
                                "type": a.type_id.code,
                            }

                            type_lang_d = {}
                            for lang in template_id.lang_ids.mapped("code"):
                                type_lang_d[lang] = a.type_id.with_context(
                                    lang=lang
                                ).name
                            if type_lang_d:
                                attachment_d.update(
                                    {
                                        "label": type_lang_d,
                                    }
                                )

                            attachment_l.append(attachment_d)

                    if attachment_l:
                        rec.json_display_attachment = json.dumps(attachment_l)
                    else:
                        rec.json_display_attachment = False
                else:
                    rec.json_display_attachment = False
        else:
            self.json_display_attachment = False

    # Export Url Attachments
    export_url_attachments = fields.Serialized(
        compute="_compute_export_url_attachments",
    )

    @api.depends(
        "attachment_ids.datas_fname",
        "attachment_ids.sequence",
        "attachment_ids.attachment_id.store_fname",
        "attachment_ids.type_id.code",
        "attachment_ids.type_id.name",
    )
    def _compute_export_url_attachments(self):
        template_id = self.env.context.get("template_id")
        if template_id:
            for rec in self:
                # map attach type with order
                attachment_order_d = {
                    x.type_id: (x.sequence, x.id) for x in template_id.attachment_ids
                }
                attachment_resolution_d = {
                    x.type_id: x.resolution for x in template_id.attachment_ids
                }
                attachment_max_d = {
                    x.type_id: x.max_count for x in template_id.attachment_ids
                }
                attachment_prefix_d = {
                    x.type_id: x.prefix or "" for x in template_id.attachment_ids
                }

                # classify
                attachment_type_d = {}
                for a in rec.attachment_ids:
                    attach_type = a.type_id
                    if attach_type in attachment_order_d:
                        if attach_type not in attachment_type_d:
                            attachment_type_d[attach_type] = self.env[
                                "lighting.attachment"
                            ]
                        attachment_type_d[attach_type] |= a

                # final attachment sort and formatting
                if attachment_type_d:
                    attachment_d = {}
                    for attach_type, attachs in sorted(
                        attachment_type_d.items(),
                        key=lambda x: attachment_order_d[x[0]],
                    ):
                        attachs_date = attachs.sorted(
                            lambda x: (fields.Date.from_string(x.write_date), x.id),
                            reverse=True,
                        )
                        max_idx = attachment_max_d[attach_type]
                        if max_idx < 0:
                            max_idx = len(attachs_date)
                        for a in attachs_date[:max_idx]:
                            if a.datas_location == "file":
                                if not a.public:
                                    a.sudo().public = True
                            prefix = attachment_prefix_d[attach_type]
                            attachment_d.setdefault(prefix, []).append(
                                a.url_get(
                                    resolution=attachment_resolution_d.get(attach_type)
                                )
                            )

                    if attachment_d:
                        rec.export_url_attachments = json.dumps(attachment_d)
                    else:
                        rec.export_url_attachments = False
                else:
                    rec.export_url_attachments = False
        else:
            self.export_url_attachments = False

    # Display Model
    json_display_model = fields.Serialized(
        string="Model JSON Display",
        compute="_compute_json_display_model",
    )

    @api.depends("model_id", "model_id.name")
    def _compute_json_display_model(self):
        template_id = self.env.context.get("template_id")
        if template_id:
            for rec in self:
                if rec.model_id:
                    rec.json_display_model = json.dumps(rec.model_id.mapped("name"))
                else:
                    rec.json_display_model = False
        else:
            self.json_display_model = False

    # Display Sources
    json_display_source_type = fields.Serialized(
        string="Source type JSON Display",
        compute="_compute_json_display_source_type",
    )

    @api.depends(
        "source_ids.lampholder_id",
        "source_ids.line_ids",
        "source_ids.line_ids.type_id",
        "source_ids.line_ids.type_id.name",
        "source_ids.sequence",
    )
    def _compute_json_display_source_type(self):
        template_id = self.env.context.get("template_id")
        if template_id:
            for rec in self:
                rec.json_display_source_type = json.dumps(
                    rec.source_ids.get_source_type()
                )
        else:
            self.json_display_source_type = False

    # Display Color temperature
    json_display_color_temperature = fields.Serialized(
        string="Color temperature JSON Display",
        compute="_compute_json_display_color_temperature",
    )

    @api.depends(
        "source_ids",
        "source_ids.line_ids",
        "source_ids.line_ids.color_temperature_flux_ids",
        "source_ids.line_ids.color_temperature_flux_ids.color_temperature_id",
        "source_ids.line_ids.color_temperature_flux_ids.color_temperature_id.value",
        "source_ids.sequence",
    )
    def _compute_json_display_color_temperature(self):
        template_id = self.env.context.get("template_id")
        if template_id:
            for rec in self:
                rec.json_display_color_temperature = json.dumps(
                    rec.source_ids.get_color_temperature()
                )
        else:
            self.json_display_color_temperature = False

    # Display Luminous flux
    json_display_luminous_flux = fields.Serialized(
        string="Luminous flux JSON Display",
        compute="_compute_json_display_luminous_flux",
    )

    @api.depends(
        "source_ids",
        "source_ids.line_ids",
        "source_ids.line_ids.color_temperature_flux_ids",
        "source_ids.line_ids.color_temperature_flux_ids.color_temperature_id",
        "source_ids.line_ids.color_temperature_flux_ids.color_temperature_id.value",
        "source_ids.line_ids.color_temperature_flux_ids.nominal_flux",
        "source_ids.sequence",
    )
    def _compute_json_display_luminous_flux(self):
        template_id = self.env.context.get("template_id")
        if template_id:
            for rec in self:
                rec.json_display_luminous_flux = json.dumps(
                    rec.source_ids.get_luminous_flux()
                )
        else:
            self.json_display_luminous_flux = False

    # Display Wattage
    json_display_wattage = fields.Serialized(
        string="Wattage JSON Display",
        compute="_compute_json_display_wattage",
    )

    @api.depends(
        "source_ids",
        "source_ids.line_ids",
        "source_ids.line_ids.wattage",
        "source_ids.line_ids.wattage_magnitude",
        "source_ids.sequence",
    )
    def _compute_json_display_wattage(self):
        template_id = self.env.context.get("template_id")
        if template_id:
            for rec in self:
                rec.json_display_wattage = json.dumps(rec.source_ids.get_wattage())
        else:
            self.json_display_wattage = False

    # Display Beams
    json_display_beam = fields.Serialized(
        string="Beam JSON Display", compute="_compute_json_display_beam"
    )

    @api.depends(
        "beam_ids.dimension_ids",
        "beam_ids.dimension_ids.value",
        "beam_ids.dimension_ids.type_id",
        "beam_ids.dimension_ids.type_id.uom",
        "beam_ids.photometric_distribution_ids",
        "beam_ids.photometric_distribution_ids.name",
        "beam_ids.sequence",
    )
    def _compute_json_display_beam(self):
        template_id = self.env.context.get("template_id")
        if template_id:
            for rec in self:
                rec.json_display_beam = json.dumps(rec.beam_ids.get_beam())
        else:
            self.json_display_beam = False

    # Display Beam Angle
    json_display_beam_angle = fields.Serialized(
        string="Beam angle JSON Display",
        compute="_compute_json_display_beam_angle",
    )

    @api.depends(
        "beam_ids.dimension_ids",
        "beam_ids.dimension_ids.value",
        "beam_ids.dimension_ids.type_id",
        "beam_ids.dimension_ids.type_id.uom",
        "beam_ids.sequence",
    )
    def _compute_json_display_beam_angle(self):
        template_id = self.env.context.get("template_id")
        if template_id:
            for rec in self:
                rec.json_display_beam_angle = json.dumps(rec.beam_ids.get_beam_angle())
        else:
            self.json_display_beam_angle = False

    # Display Cut hole dimension
    json_display_cut_hole_dimension = fields.Char(
        string="Cut hole dimension JSON Display",
        compute="_compute_json_display_cut_hole_dimension",
    )

    @api.depends(
        "recess_dimension_ids",
        "recess_dimension_ids.type_id",
        "recess_dimension_ids.value",
        "recess_dimension_ids.sequence",
    )
    def _compute_json_display_cut_hole_dimension(self):
        template_id = self.env.context.get("template_id")
        if template_id:
            for rec in self:
                rec.json_display_cut_hole_dimension = (
                    rec.recess_dimension_ids.get_display()
                )
        else:
            self.json_display_cut_hole_dimension = False

    # Display Dimension
    json_display_dimension = fields.Char(
        string="Dimension JSON Display",
        compute="_compute_json_display_dimension",
    )

    @api.depends(
        "dimension_ids",
        "dimension_ids.type_id",
        "dimension_ids.value",
        "dimension_ids.sequence",
    )
    def _compute_json_display_dimension(self):
        template_id = self.env.context.get("template_id")
        if template_id:
            for rec in self:
                rec.json_display_dimension = rec.dimension_ids.get_display()
        else:
            self.json_display_dimension = False

    # Display Dimmable
    json_display_dimmable = fields.Serialized(
        string="Dimmable JSON Display",
        compute="_compute_json_display_dimmable",
    )

    @api.depends("dimmable_ids", "dimmable_ids.name")
    def _compute_json_display_dimmable(self):
        template_id = self.env.context.get("template_id")
        if template_id:
            for rec in self:
                dimmables = None
                if rec.dimmable_ids:
                    dimmables = rec.dimmable_ids.mapped("display_name")
                else:
                    if rec.configurator:
                        dimmables = ["ON-OFF"]
                if dimmables:
                    rec.json_display_dimmable = json.dumps(dimmables)
                else:
                    rec.json_display_dimmable = False
        else:
            self.json_display_dimmable = False

    # Display Optional products
    json_display_optional = fields.Serialized(
        string="Optional JSON Display",
        compute="_compute_json_display_optional",
    )

    @api.depends("optional_ids")
    def _compute_json_display_optional(self):
        template_id = self.env.context.get("template_id")
        if template_id:
            for rec in self:
                if rec.optional_ids:
                    template_optional_published = rec.optional_ids.filtered(
                        lambda x: x.state == "published"
                    )
                    template_optional_l = list(
                        set(template_optional_published.mapped("finish_group_name"))
                    )
                    if template_optional_l:
                        rec.json_display_optional = json.dumps(
                            sorted(template_optional_l)
                        )
                    else:
                        rec.json_display_optional = False
                else:
                    rec.json_display_optional = False
        else:
            self.json_display_optional = False

    # Display Subtitutes
    json_display_substitute = fields.Serialized(
        string="Substitute JSON Display",
        compute="_compute_json_display_substitute",
    )

    @api.depends("substitute_ids")
    def _compute_json_display_substitute(self):
        template_id = self.env.context.get("template_id")
        if template_id:
            for rec in self:
                if rec.substitute_ids:
                    template_substitute_published = rec.substitute_ids.filtered(
                        lambda x: x.state == "published"
                    )
                    template_substitute_l = list(
                        set(template_substitute_published.mapped("finish_group_name"))
                    )
                    rec.json_display_substitute = json.dumps(
                        sorted(template_substitute_l)
                    )
                else:
                    rec.json_display_substitute = False
        else:
            self.json_display_substitute = False

    # Display First Product Photo
    json_display_photo = fields.Serialized(
        string="Photo JSON Display",
        compute="_compute_json_display_photo",
    )

    def _compute_json_display_photo(self):
        template_id = self.env.context.get("template_id")
        if template_id:
            attachment_order_d = {
                x.type_id.id: x.sequence for x in template_id.attachment_ids
            }
            for rec in self:
                if rec.product_group_id:
                    attachment_ids = rec.product_group_id.flat_product_ids.mapped(
                        "attachment_ids"
                    )
                else:
                    attachment_ids = rec.attachment_ids

                images = attachment_ids.filtered(
                    lambda x: x.datas_location == "file"
                    and x.datas_fname
                    and x.type_id.is_image
                    and x.image_known
                    and x.type_id.id in attachment_order_d.keys()
                )
                if images:
                    images = images.sorted(
                        lambda x: (
                            attachment_order_d[x.type_id.id],
                            x.product_id.sequence,
                            x.sequence,
                            x.id,
                        )
                    )
                    attachment_d = {
                        "datas_fname": images[0].datas_fname,
                        "store_fname": images[0].attachment_id.store_fname,
                    }
                    rec.json_display_photo = json.dumps(attachment_d)
                else:
                    rec.json_display_photo = False
        else:
            self.json_display_photo = False

    # Display Product Video url
    json_display_video = fields.Char(
        string="Video JSON Display",
        compute="_compute_json_display_video",
    )

    def _compute_json_display_video(self):
        template_id = self.env.context.get("template_id")
        if template_id:
            attachment_order_d = {
                x.type_id.id: x.sequence for x in template_id.attachment_url_ids
            }
            for rec in self:
                urls = rec.attachment_ids.filtered(
                    lambda x: x.datas_location == "url"
                    and x.datas_url
                    and x.type_id.id in attachment_order_d.keys()
                )
                if urls:
                    urls = urls.sorted(
                        lambda x: (
                            attachment_order_d[x.type_id.id],
                            x.product_id.sequence,
                            x.sequence,
                            x.id,
                        )
                    )
                    rec.json_display_video = urls[0].datas_url
                else:
                    rec.json_display_video = False
        else:
            self.json_display_video = False

    # Search fields
    # Search Materials
    json_search_material_ids = fields.Many2many(
        string="Material JSON Search",
        comodel_name="lighting.product.material",
        compute="_compute_json_search_material_ids",
    )

    @api.depends("body_material_ids")
    def _compute_json_search_material_ids(self):
        fields = ["body_material_ids"]
        for rec in self:
            materials_s = set()
            for field in fields:
                objs = getattr(rec, field)
                if objs:
                    materials_s |= {x.id for x in objs}

            if materials_s:
                objs = self.env["lighting.product.material"].browse(list(materials_s))
                rec.json_search_material_ids = [
                    (4, x.id, False) for x in objs.sorted(lambda x: x.display_name)
                ]
            else:
                rec.json_search_material_ids = False

    # Search CRI
    json_search_cri = fields.Serialized(
        string="CRI JSON Search",
        compute="_compute_json_search_cri",
    )

    @api.depends("source_ids.line_ids.cri_min")
    def _compute_json_search_cri(self):
        for rec in self:
            cris = (
                rec.source_ids.mapped("line_ids")
                .filtered(
                    lambda x: x.cri_min != 0
                    and x.is_led
                    and (x.is_integrated or x.is_lamp_included)
                )
                .mapped("cri_min")
            )

            rec.json_search_cri = json.dumps(sorted(list(set(cris))))

    # Search CRI - Temp
    json_search_cri_color_temperature = fields.Serialized(
        string="CRI - Color Temperature JSON Search",
        compute="_compute_json_search_cri_color_temperature",
    )

    @api.depends(
        "source_ids.line_ids",
        "source_ids.line_ids.cri_min",
        "source_ids.line_ids.special_spectrum_id",
        "source_ids.line_ids.special_spectrum_id.name",
        "source_ids.line_ids.special_spectrum_id.use_as_cct",
        "source_ids.line_ids.color_temperature_flux_ids",
        "source_ids.line_ids.color_temperature_flux_ids.color_temperature_id",
        "source_ids.line_ids.color_temperature_flux_ids.color_temperature_id.value",
    )
    def _compute_json_search_cri_color_temperature(self):
        for rec in self:
            critemps = []
            critemps_dup = set()
            lines = rec.source_ids.mapped("line_ids")
            for line in lines.sorted("cri_min"):
                if line.special_spectrum_id and line.special_spectrum_id.use_as_cct:
                    critemps.append(line.special_spectrum_id.name)
                else:
                    ctemps = line.color_temperature_flux_ids.mapped(
                        "color_temperature_id"
                    ).sorted(lambda x: x.value)
                    if line.cri_min and ctemps:
                        for ctemp in ctemps:
                            if ctemp.display_name:
                                critemp = (line.cri_min, ctemp.display_name)
                                if critemp not in critemps_dup:
                                    critemps_dup.add(critemp)
                                    critemps.append("CRI%i - %s" % critemp)
            if critemps:
                rec.json_search_cri_color_temperature = json.dumps(critemps)
            else:
                rec.json_search_cri_color_temperature = False

    # Search Input Voltage
    json_search_input_voltage = fields.Serialized(
        string="Input Voltage JSON Search",
        compute="_compute_json_search_input_voltage",
    )

    @api.depends("input_voltage_id")
    def _compute_json_search_input_voltage(self):
        for rec in self:
            if rec.input_voltage_id:
                rec.json_search_input_voltage = json.dumps(
                    rec.input_voltage_id.mapped("name")
                )
            else:
                rec.json_search_input_voltage = False

    # Search Beam
    json_search_beam_angle = fields.Serialized(
        string="Beam angle JSON Search",
        compute="_compute_json_search_beam_angle",
    )

    @api.depends(
        "beam_ids.dimension_ids.value",
        "beam_ids.dimension_ids.type_id",
        "beam_ids.dimension_ids.type_id.name",
        "beam_ids.dimension_ids.type_id.uom",
    )
    def _compute_json_search_beam_angle(self):
        for rec in self:
            angles = rec.beam_ids.mapped("dimension_ids.value")
            if angles:
                if rec.configurator:
                    a_ranges = ["%i\u00B0" % x for x in angles]
                else:
                    arange = [
                        (0, 20),
                        (20, 40),
                        (40, 60),
                        (60, 80),
                        (80, 100),
                        (100, float("inf")),
                    ]
                    a_ranges = _values2range(angles, arange, magnitude="\u00B0")
                if a_ranges:
                    rec.json_search_beam_angle = json.dumps(a_ranges)
                else:
                    rec.json_search_beam_angle = False
            else:
                rec.json_search_beam_angle = False

    # Search Wattage
    json_search_wattage = fields.Serialized(
        string="Wattage JSON Search",
        compute="_compute_json_search_wattage",
    )

    @api.depends("source_ids.line_ids.wattage")
    def _compute_json_search_wattage(self):
        for rec in self:
            wattages_s = set()
            for line in rec.source_ids.mapped("line_ids"):
                if line.wattage:
                    wattages_s.add(line.wattage * line.source_id.num)
            wattages_s2 = set()
            for w in wattages_s:
                wattages_s2.add(w)
            if wattages_s2:
                wrange = [
                    (0, 10),
                    (10, 20),
                    (20, 30),
                    (30, 40),
                    (40, 50),
                    (50, float("inf")),
                ]
                wattage_ranges = _values2range(wattages_s2, wrange, magnitude="W")
                if wattage_ranges:
                    rec.json_search_wattage = json.dumps(wattage_ranges)
                else:
                    rec.json_search_wattage = False
            else:
                rec.json_search_wattage = False

    # Search Wattage 2
    json_search_wattage2 = fields.Serialized(
        string="Wattage2 JSON Search",
        compute="_compute_json_search_wattage2",
    )

    @api.depends(
        "source_ids",
        "source_ids.line_ids",
        "source_ids.line_ids.wattage",
        "source_ids.line_ids.wattage_magnitude",
        "source_ids.sequence",
    )
    def _compute_json_search_wattage2(self):
        template_id = self.env.context.get("template_id")
        if template_id:
            for rec in self:
                rec.json_search_wattage2 = json.dumps(rec.source_ids.get_wattage())
        else:
            self.json_search_wattage2 = False

    # Search Color temperature
    json_search_color_temperature = fields.Serialized(
        string="Color temperature JSON Search",
        compute="_compute_json_search_color_temperature",
    )

    @api.depends(
        "source_ids.line_ids.color_temperature_flux_ids",
        "source_ids.line_ids.color_temperature_flux_ids.color_temperature_id",
        "source_ids.line_ids.color_temperature_flux_ids.color_temperature_id.value",
    )
    def _compute_json_search_color_temperature(self):
        for rec in self:
            colork_s = set()
            for line in rec.source_ids.mapped("line_ids"):
                if line.is_integrated:
                    if line.color_temperature_flux_ids:
                        if (
                            line.is_color_temperature_flux_tunable
                            and len(line.color_temperature_flux_ids) > 1
                        ):
                            tunable_range = line.color_temperature_flux_ids.sorted(
                                lambda x: x.color_temperature_id.value
                            ).mapped("color_temperature_id.value")
                            values = (
                                self.env["lighting.product.color.temperature"]
                                .search(
                                    [
                                        ("value", ">=", tunable_range[0]),
                                        ("value", "<=", tunable_range[-1]),
                                    ]
                                )
                                .mapped("value")
                            )
                        else:
                            values = line.color_temperature_flux_ids.mapped(
                                "color_temperature_id.value"
                            )
                        colork_s |= set(values)

            if colork_s:
                krange = [
                    (0, 3000),
                    (3000, 3500),
                    (3500, 4000),
                    (4000, 5000),
                    (5000, float("inf")),
                ]
                k_ranges = _values2range(colork_s, krange, magnitude="K")
                if k_ranges:
                    rec.json_search_color_temperature = json.dumps(k_ranges)
                else:
                    rec.json_search_color_temperature = False
            else:
                rec.json_search_color_temperature = False

    # Search Luminoux flux
    json_search_luminous_flux = fields.Serialized(
        string="Luminous flux JSON Search",
        compute="_compute_json_search_luminous_flux",
    )

    @api.depends(
        "source_ids.line_ids.color_temperature_flux_ids",
        "source_ids.line_ids.color_temperature_flux_ids.color_temperature_id",
        "source_ids.line_ids.color_temperature_flux_ids.color_temperature_id.value",
        "source_ids.line_ids.color_temperature_flux_ids.nominal_flux",
    )
    def _compute_json_search_luminous_flux(self):
        for rec in self:
            fluxes_s = set()
            for line in rec.source_ids.mapped("line_ids"):
                if line.is_integrated:
                    if line.color_temperature_flux_ids:
                        if (
                            line.is_color_temperature_flux_tunable
                            and len(line.color_temperature_flux_ids) > 1
                        ):
                            tunable_range = line.color_temperature_flux_ids.sorted(
                                lambda x: x.nominal_flux
                            ).mapped("nominal_flux")
                            values = (
                                self.env[
                                    "lighting.product.source.line.color.temperature.flux"
                                ]
                                .search(
                                    [
                                        ("nominal_flux", ">=", tunable_range[0]),
                                        ("nominal_flux", "<=", tunable_range[-1]),
                                    ]
                                )
                                .mapped("nominal_flux")
                            )
                        else:
                            values = line.color_temperature_flux_ids.mapped(
                                "nominal_flux"
                            )
                        fluxes_s |= set(map(lambda x: x * line.source_id.num, values))

            if fluxes_s:
                fxrange = [
                    (0, 400),
                    (400, 800),
                    (800, 1200),
                    (1200, 1600),
                    (1600, 2000),
                    (2000, float("inf")),
                ]
                flux_ranges = _values2range(fluxes_s, fxrange, magnitude="Lm")
                if flux_ranges:
                    rec.json_search_luminous_flux = json.dumps(flux_ranges)
                else:
                    rec.json_search_luminous_flux = False
            else:
                rec.json_search_luminous_flux = False

    # Search Source type flux
    json_search_source_type = fields.Serialized(
        string="Source type JSON Search",
        compute="_compute_json_search_source_type",
    )

    @api.depends(
        "source_ids.line_ids.is_integrated",
        "source_ids.line_ids.is_led",
    )
    def _compute_json_search_source_type(self):
        template_id = self.env.context.get("template_id")
        if template_id:
            for rec in self:
                leds_integrated = rec.source_ids.mapped("line_ids").filtered(
                    lambda x: x.is_led and x.is_integrated
                )
                type_str = "LED" if leds_integrated else "Other"

                source_type_d = {}
                for lang in template_id.lang_ids.mapped("code"):
                    source_type_d[lang] = rec.with_context(lang=lang)._(type_str)

                if source_type_d:
                    rec.json_search_source_type = json.dumps(source_type_d)
                else:
                    rec.json_search_source_type = False

    marketplace_description_html = fields.Html(
        string="Marketplace description html",
        store=False,
        readonly=True,
        compute="_compute_marketplace_description_html",
    )

    @api.depends("marketplace_description")
    def _compute_marketplace_description_html(self):
        for rec in self:
            if rec.marketplace_description:
                rec.marketplace_description_html = rec.marketplace_description.replace(
                    "\n", "<br>"
                )
            else:
                rec.marketplace_description_html = False
