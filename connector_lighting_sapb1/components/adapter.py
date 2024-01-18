# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import json
import logging
from contextlib import contextmanager
from functools import partial

import requests
from requests.exceptions import ConnectionError, HTTPError, RequestException
from requests.packages import urllib3

from odoo import _, exceptions
from odoo.exceptions import ValidationError

from odoo.addons.component.core import AbstractComponent
from odoo.addons.connector.exception import NetworkRetryableError
from odoo.addons.queue_job.exception import RetryableJobError

try:
    from hdbcli import dbapi
except ImportError:
    dbapi = None

_logger = logging.getLogger(__name__)


@contextmanager
def api_handle_errors(message=""):
    """Handle error when calling the API

    It is meant to be used when a model does a direct
    call to a job using the API (not using job.delay()).
    Avoid to have unhandled errors raising on front of the user,
    instead, they are presented as :class:`openerp.exceptions.UserError`.
    """
    if message:
        message = message + "\n\n"
    try:
        yield
    except NetworkRetryableError as err:
        raise exceptions.UserError(_("{}Network Error:\n\n{}").format(message, err))
    except (HTTPError, RequestException, ConnectionError) as err:
        raise exceptions.UserError(
            _("{}API / Network Error:\n\n{}").format(message, err)
        )
    except (dbapi.OperationalError,) as err:
        raise exceptions.UserError(
            _("{}DB operational Error:\n\n{}").format(message, err)
        )
    except (dbapi.IntegrityError,) as err:
        raise exceptions.UserError(
            _("{}DB integrity Error:\n\n{}").format(message, err)
        )
    except (dbapi.InternalError,) as err:
        raise exceptions.UserError(_("{}DB internal Error:\n\n{}").format(message, err))
    except (dbapi.InterfaceError,) as err:
        raise exceptions.UserError(
            _("{}DB interface Error:\n\n{}").format(message, err)
        )


class CRUDAdapter(AbstractComponent):
    """External Records Adapter"""

    _name = "sapb1.lighting.crud.adapter"
    _inherit = ["base.backend.adapter", "base.sapb1.lighting.connector"]

    _usage = "backend.adapter"

    def __init__(self, environment):
        """
        :param environment: current environment (backend, session, ...)
        :type environment: :py:class:`connector.connector.ConnectorEnvironment`
        """
        super().__init__(environment)

        self.schema = self.backend_record.db_schema
        self.conn = partial(
            dbapi.connect,
            self.backend_record.db_host,
            self.backend_record.db_port,
            self.backend_record.db_username,
            self.backend_record.db_password,
        )

    def search(self, model, filters=[]):
        """Search records according to some criterias
        and returns a list of ids"""
        raise NotImplementedError

    def read(self, id, attributes=None):
        """Returns the information of a record"""
        raise NotImplementedError

    def search_read(self, filters=[]):
        """Search records according to some criterias
        and returns their information"""
        raise NotImplementedError

    def create(self, data):
        """Create a record on the external system"""
        raise NotImplementedError

    def write(self, id, data):
        """Update records on the external system"""
        raise NotImplementedError

    def delete(self, id):
        """Delete a record on the external system"""
        raise NotImplementedError

    def get_version(self):
        """Check connection"""
        raise NotImplementedError


class GenericAdapter(AbstractComponent):
    _name = "sapb1.lighting.adapter"
    _inherit = "sapb1.lighting.crud.adapter"

    ## private methods

    def _escape(self, s):
        return s.replace("'", "").replace('"', "")

    def _check_schema(self):
        sql = """select 1
                 from sys.schemas
                 WHERE schema_owner = 'SYSTEM' and
                       schema_name = ?"""

        schema_exists = self._exec_sql(sql, (self.schema,))
        if not schema_exists:
            raise dbapi.InternalError("The schema %s does not exist" % self.schema)

    def _exec_sql(self, sql, params, commit=False):
        conn = self.conn()
        cr = conn.cursor()
        cr.execute(sql, params)

        headers = [desc[0] for desc in cr.description]
        res = []
        for row in cr:
            res.append(dict(zip(headers, row)))

        if commit:
            conn.commit()
        cr.close()
        conn.close()

        return res

    def _exec_query(self, filters=[], fields=None):
        fields_l = fields or ["*"]
        if fields:
            if self._id:
                for f in self._id:
                    if f not in fields_l:
                        fields_l.append(f)

        fields_str = ", ".join(fields_l)

        where_l, values_l = [], []
        if filters:
            for k, operator, v in filters:
                if v is None:
                    if operator == "=":
                        operator = "is"
                    elif operator == "!=":
                        operator = "is not"
                    else:
                        raise Exception(
                            "Operator '%s' is not implemented on NULL values" % operator
                        )

                value_placeholder = "?"
                if operator in ("in", "not in"):
                    value_placeholder = "%s" % (tuple(v),)
                else:
                    values_l.append(v)

                where_l.append('"%s" %s %s' % (k, operator, value_placeholder))

        where_str = where_l and "where %s" % (" and ".join(where_l),) or ""

        # check if schema exists to avoid injection
        self._check_schema()

        # prepare the sql
        sql = self._sql_read % dict(
            schema=self.schema, fields=fields_str, where=where_str
        )

        # execute
        res = self._exec_sql(sql, tuple(values_l))

        filter_keys_s = {e[0] for e in filters}
        if self._id and set(self._id).issubset(filter_keys_s):
            self._check_uniq(res)

        return res

    def _check_uniq(self, data):
        uniq = set()
        for rec in data:
            id_t = tuple([rec[f] for f in self._id])
            if id_t in uniq:
                raise dbapi.IntegrityError(
                    "Unexpected error: ID duplicated: %s - %s" % (self._id, id_t)
                )
            uniq.add(id_t)

    def id2dict(self, id):
        return dict(zip(self._id, id))

    def _check_response_error(self, r):
        if not r.ok:
            err_msg = _("Error trying to connect to %s: %s") % (r.url, r.text)
            if r.status_code in (500, 502, 503, 504):
                raise RetryableJobError(
                    "%s\n%s" % (err_msg, _("The job will be retried later"))
                )
            try:
                # if it's a json response
                # TODO: maybe use response 'Content-Type' instead??
                err_json = r.json()
                err = err_json["error"]
                if err["code"] == 305:
                    if err["message"]["lang"] != "en-us":
                        raise ValidationError(
                            _(
                                "Only supported english (en-us) dealing with error messages from the server\n%s"
                            )
                            % err_json
                        )
                    if err["message"]["value"] == "Switch company error: -1102":
                        raise RetryableJobError(
                            _(
                                "Temporarily connection error:\n%s\n"
                                "It will be retried later."
                            )
                            % err_json
                        )
            except json.decoder.JSONDecodeError:
                pass
            raise ConnectionError(err_msg)

    def _login(self):
        # TODO: convert this login/logout to the contextmanager call
        if hasattr(self, "session") and self.session:
            raise ConnectionError(
                "The session should have been empty on  new transaction"
            )
        self.session = requests.session()

        payload = {
            "CompanyDB": self.backend_record.db_schema,
            "UserName": self.backend_record.sl_username,
            "Password": self.backend_record.sl_password,
        }
        r = self.session.post(
            self.backend_record.sl_url + "/Login", json=payload, verify=False
        )
        self._check_response_error(r)
        return True

    def _logout(self):
        # TODO: convert this login/logout to the contextmanager call
        if not self.session:
            raise ConnectionError(
                "The session is not set, you cannot make a logout without being logged in"
            )
        r = self.session.post(self.backend_record.sl_url + "/Logout")  # , verify=False)
        self._check_response_error(r)
        return True

    ########## exposed methods

    def search_read(self, filters=[]):
        """Search records according to some criterias
        and returns a list of ids

        :rtype: list
        """
        _logger.debug("method search_read, sql %s, filters %s", self._sql_read, filters)

        res = self._exec_query(filters=filters)

        return res

    def search(self, filters=[]):
        """Search records according to some criterias
        and returns a list of ids

        :rtype: list
        """
        _logger.debug("method search, sql %s, filters %s", self._sql_read, filters)

        res = self.search_read(filters=filters)

        res = [tuple([x[f] for f in self._id]) for x in res]

        return res

    def read(self, id, attributes=None):
        """Returns the information of a record

        :rtype: dict
        """
        _logger.debug(
            "method read, sql %s id %s, attributes %s", self._sql_read, id, attributes
        )

        filters = list(zip(self._id, ["="] * len(self._id), id))

        res = self._exec_query(filters=filters)

        if len(res) > 1:
            raise dbapi.IntegrityError(
                "Unexpected error: Returned more the one rows:\n%s" % ("\n".join(res),)
            )

        return res and res[0] or []

    def write(self, id, values):
        """Update records on the external system"""
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        _logger.debug("method write, id %s, values %s", id, values)

        self._login()

        _id = self.id2dict(id)["ItemCode"]

        sap_main_lang_id = self.backend_record.language_map.filtered(
            lambda x: x.sap_main_lang
        ).sap_lang_id
        root_url = self.backend_record.sl_url

        translate_fields = (
            hasattr(self, "_translatable_fields") and self._translatable_fields or []
        )
        if not isinstance(translate_fields, (list, tuple)):
            translate_fields = [translate_fields]

        payload = {}
        add_lang = {}
        for k, v in values.items():
            if k not in translate_fields or not isinstance(v, dict):
                payload[k] = v
            else:
                for lang, value in v.items():
                    if lang == sap_main_lang_id:
                        payload[k] = value
                    else:
                        add_lang.setdefault(k, {})
                        add_lang[k][lang] = value

        if payload:
            r = self.session.patch(root_url + f"/Items(ItemCode='{_id}')", json=payload)
            self._check_response_error(r)

        if add_lang:
            # update/create data
            for field, trls in add_lang.items():
                qry = [
                    f"$filter=TableName eq '{self._base_table}' and FieldAlias eq '{field}' and PrimaryKeyofobject eq '"
                    f"{_id}'",
                    "$select=TranslationsInUserLanguages,Numerator",
                ]
                r = self.session.get(
                    root_url + "/MultiLanguageTranslations?" + "&".join(qry)
                )
                self._check_response_error(r)
                res = r.json()["value"]
                if len(res) > 1:
                    raise ValidationError(
                        "Unexpected more than one language register found"
                    )
                elif len(res) == 1:
                    res = res[0]
                    numerator = res["Numerator"]
                    new_trls = res["TranslationsInUserLanguages"]
                    for tr in new_trls:
                        lang_code = tr["LanguageCodeOfUserLanguage"]
                        if lang_code in trls:
                            trl_text = trls.pop(lang_code)
                            if tr["Translationscontent"] != trl_text:
                                tr["Translationscontent"] = trl_text

                    for lang_code, tr_text in trls.items():
                        new_trls.append(
                            {
                                "KeyFromHeaderTable": numerator,
                                "LanguageCodeOfUserLanguage": lang_code,
                                "Translationscontent": tr_text,
                            }
                        )
                    payload = {
                        "TranslationsInUserLanguages": new_trls,
                    }
                    r = self.session.patch(
                        root_url + f"/MultiLanguageTranslations(Numerator={numerator})",
                        json=payload,
                    )
                    self._check_response_error(r)
                else:
                    payload = {
                        "TableName": self._base_table,
                        "FieldAlias": field,
                        "PrimaryKeyofobject": f"{_id}",
                    }
                    new_trls = []
                    for lang_code, tr_text in trls.items():
                        new_trls.append(
                            {
                                "LanguageCodeOfUserLanguage": lang_code,
                                "Translationscontent": tr_text,
                            }
                        )
                    payload["TranslationsInUserLanguages"] = new_trls
                    r = self.session.post(
                        root_url + "/MultiLanguageTranslations", json=payload
                    )
                    self._check_response_error(r)

        self._logout()

        return True

    def get_version(self):
        res = self._exec_query()

        return res[0][0]


class SAPB1LightingNoModelAdapter(AbstractComponent):
    """Used to test the connection"""

    _name = "sapb1.lighting.adapter.test"
    _inherit = "sapb1.lighting.adapter"
    _apply_on = "sapb1connector_sapb1.lighting.backend"

    _sql_read = "select @@version"
    _id = None
