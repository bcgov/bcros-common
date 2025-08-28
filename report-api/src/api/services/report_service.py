# Copyright © 2019 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Service to  manage report-templates."""

import asyncio
import base64

from dateutil import parser
from flask import current_app, url_for
from jinja2 import Environment, FileSystemLoader
from jinja2.sandbox import SandboxedEnvironment
import requests

from api.services.chunk_report_service import ChunkReportService
from api.services.page_info import get_pdf_page_count
from api.utils.util import TEMPLATE_FOLDER_PATH


def format_datetime(value, format='short'):  # pylint: disable=redefined-builtin
    """Filter to format datetime globally."""
    dt_format = '%m-%d-%Y'
    if format == 'full':
        dt_format = '%m-%d-%Y %I:%M %p'
    elif format == 'short':
        dt_format = '%m-%d-%Y'
    elif format == 'month':
        dt_format = '%B'
    elif format == 'yyyy-mm-dd':
        dt_format = '%Y-%m-%d'
    elif format == 'mmm dd,yyyy':
        dt_format = '%B %e, %Y'
    elif format == 'detail':
        dt_format = '%B %d, %Y at %I:%M %p Pacific Time'
    elif format == 'unix':
        return int(parser.parse(value).timestamp())

    return parser.parse(value).strftime(dt_format)


ENV = Environment(loader=FileSystemLoader('.'), autoescape=True)
ENV.filters['format_datetime'] = format_datetime


class ReportService:
    """Service for all template related operations."""

    @staticmethod
    def _finalize_pdf(
        template_name: str,
        template_args: object,
        html_out: str,
        generate_page_number: bool,
    ) -> bytes:
        """Route to chunk only when statement_report has groupedInvoices; else render directly."""
        is_statement = 'statement_report' in (template_name or '')
        has_grouped_invoices = bool((template_args or {}).get('groupedInvoices'))

        if is_statement and has_grouped_invoices:
            return ChunkReportService.create_chunk_report(
                template_name,
                template_args,
                generate_page_number,
            )
        return ReportService.generate_pdf(template_name,html_out, generate_page_number, template_args)

    @staticmethod
    def generate_pdf(template_name, html_out, generate_page_number: bool = False, template_args: dict = None): # pylint:disable=too-many-locals
        """Generate pdf out of the html using Gotenberg."""
        gotenberg_url = current_app.config.get('GOTENBERG_URL', 'http://localhost:3000')
        endpoint = f"{gotenberg_url}/forms/chromium/convert/html"

        files = [("files", ("index.html", html_out, "text/html"))]
        data = {}

        resp = requests.post(
            endpoint,
            files=files,
            data=data,
            timeout=120
        )
        resp.raise_for_status()
        main_pdf_bytes = resp.content


        template_requires_page_numbers = any(name in template_name for name in ['routing_slip_report', 'payment_receipt'])
        if template_requires_page_numbers:
            generate_page_number = True
        if generate_page_number:
            total_pages = get_pdf_page_count(main_pdf_bytes)

            # Build footer batches using the same footer template and overlay CSS as chunk service
            footer_args = dict(template_args or {})
            footer_args['current_template'] = template_name
            batch_tasks = ChunkReportService._prepare_footer_batch_tasks(footer_args, total_pages, batch_size=200)

            # Render footer batches to PDFs in parallel (reuse chunk service async worker)
            footer_multi_page_pdfs = asyncio.run(
                ChunkReportService._render_tasks_parallel_async(batch_tasks, current_app.root_path)
            )

            footer_pdfs = []
            for pdf in footer_multi_page_pdfs:
                footer_pdfs.extend(ChunkReportService._split_pdf_pages(pdf))

            return ChunkReportService._overlay_footer_pdfs_on_main_pdf(main_pdf_bytes, footer_pdfs)

        return main_pdf_bytes

    @classmethod
    def create_report_from_stored_template(
        cls,
        template_name: str,
        template_args: object,
        generate_page_number: bool = False,
    ):
        """Create a report from a stored template."""
        template = ENV.get_template(f'{TEMPLATE_FOLDER_PATH}/{template_name}.html')
        bc_logo_url = url_for('static', filename='images/bcgov-logo-vert.jpg')
        registries_url = url_for('static', filename='images/reg_logo.png')
        html_out = template.render(
            template_args, bclogoUrl=bc_logo_url, registriesurl=registries_url
        )

        # Finalize via shared helper (chunk when name contains 'statement_report')
        return ReportService._finalize_pdf(
            template_name,
            template_args,
            html_out,
            generate_page_number,
        )

    @classmethod
    def create_report_from_template(cls, template_string: str, template_args: object,
                                    generate_page_number: bool = False):
        """Create a report from a json template."""
        template_decoded = base64.b64decode(template_string).decode('utf-8')
        # Use a sandboxed environment for user-supplied templates
        sandbox_env = SandboxedEnvironment(autoescape=True)
        sandbox_env.filters['format_datetime'] = format_datetime
        template_ = sandbox_env.from_string(template_decoded)
        html_out = template_.render(template_args)

        report_name = (template_args or {}).get('reportName', '')
        return ReportService._finalize_pdf(
            template_name=report_name,
            template_args=template_args,
            html_out=html_out,
            generate_page_number=generate_page_number,
        )
