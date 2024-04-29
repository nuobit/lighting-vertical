# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import models


class QueueJob(models.Model):
    _inherit = "queue.job"

    def requeue_sudo(self):
        self.sudo().requeue()
