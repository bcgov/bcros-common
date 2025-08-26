import asyncio
import gc
import io
import os
import tempfile
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple

import aiohttp
from flask import current_app, url_for
from jinja2 import Environment, FileSystemLoader
import pikepdf
import requests

from api.services.page_info import get_pdf_page_count
from api.utils.util import TEMPLATE_FOLDER_PATH


class ChunkReportService:  # pylint:disable=too-few-public-methods
    """Service for generating large reports using chunk approach."""

    _TEMPLATE_ENV = Environment(
        loader=FileSystemLoader("."), autoescape=True
    )

    @dataclass
    class ChunkInfo:
        """Chunk info for chunk report."""

        mode: str = "transactions"
        invoice_index: int = 0
        current_chunk: int = 0
        slice_start: int = 0
        slice_end: int = 0
        invoice_chunks: Optional[int] = None

    @staticmethod
    def _cleanup_temp_files(temp_files: List[str]):
        """Clean up temporary files."""
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    @staticmethod
    def _merge_pdf_files(temp_files: List[str]) -> bytes:
        """Merge multiple PDF files into one."""

        # Lazy import to avoid heavy module import in worker processes
        from pikepdf import Pdf # pylint:disable=import-outside-toplevel

        with Pdf.new() as out_pdf:
            for path in temp_files:
                with Pdf.open(path) as src:
                    out_pdf.pages.extend(src.pages)
            buf = io.BytesIO()
            out_pdf.save(buf)
            return buf.getvalue()

    @staticmethod
    def _append_pdf_bytes(pdf_content: bytes, temp_files: List[str]) -> None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(pdf_content)
            temp_files.append(temp_file.name)

    @staticmethod
    async def _render_pdf_bytes_worker_gotenberg_with_session(args: Tuple[str, str], session: aiohttp.ClientSession) -> bytes:
        """Worker used to render HTML string to PDF bytes using Gotenberg with shared session."""
        html_out, base_url = args
        gc.collect()
        
        # Prepare the HTML content for Gotenberg
        html_data = html_out.encode('utf-8')
        
        # Create multipart form data for Gotenberg
        data = aiohttp.FormData()
        data.add_field('index.html', html_data, filename='index.html', content_type='text/html')
        
        # Call Gotenberg using the shared session
        async with session.post(
            'http://localhost:3000/forms/chromium/convert/html',
            data=data,
            timeout=aiohttp.ClientTimeout(total=500)  # 500 second timeout
        ) as response:
            if response.status == 200:
                pdf_content = await response.read()
                gc.collect()
                return pdf_content
            else:
                error_text = await response.text()
                raise Exception(f"Gotenberg conversion failed with status {response.status}: {error_text}")

    @staticmethod
    def _build_chunk_html(
        template_name: str,
        template_vars: Dict[str, Any],
        invoice_copy: Dict[str, Any],
        chunk_info: "ChunkReportService.ChunkInfo",
    ) -> str:
        chunk_vars = template_vars.copy()
        chunk_vars["groupedInvoices"] = [invoice_copy]
        chunk_vars["_chunk_info"] = asdict(chunk_info)
        
        template = ChunkReportService._TEMPLATE_ENV.get_template(
            f"{TEMPLATE_FOLDER_PATH}/{template_name}.html"
        )
        bc_logo_url = url_for("static", filename="images/bcgov-logo-vert.jpg")
        registries_url = url_for("static", filename="images/reg_logo.png")
        return template.render(
            chunk_vars, bclogoUrl=bc_logo_url, registriesurl=registries_url
        )

    @staticmethod
    def _prepare_chunk_tasks(
        template_name: str,
        template_vars: Dict[str, Any],
        grouped_invoices: List[Dict[str, Any]],
        chunk_size: int,
    ) -> List[Tuple[int, str]]:
        """Prepare (order_id, html_out) tasks for all invoice transaction slices."""
        tasks: List[Tuple[int, str]] = []
        order_id = 0
        for invoice_index, original in enumerate(grouped_invoices, start=1):
            txns = original.get("transactions") or []
            if not txns:
                continue
            start = 0
            while start < len(txns):
                end = min(start + chunk_size, len(txns))
                invoice_copy = dict(original)
                invoice_copy["transactions"] = txns[start:end]
                html_out = ChunkReportService._build_chunk_html(
                    template_name,
                    template_vars,
                    invoice_copy,
                    ChunkReportService.ChunkInfo(
                        invoice_index=invoice_index,
                        current_chunk=(start // max(1, chunk_size)) + 1,
                        slice_start=start + 1,
                        slice_end=end,
                    ),
                )
                tasks.append((order_id, html_out))
                order_id += 1
                start = end
        return tasks

    @staticmethod
    async def _render_tasks_parallel_async(
        tasks: List[Tuple[int, str]],
        base_url: str,
    ) -> List[bytes]:
        """Render HTML tasks in parallel using shared session for better performance."""
        results: List[Tuple[int, bytes]] = []
        
        async with aiohttp.ClientSession() as session:
            # Create all tasks with shared session
            async_tasks = []
            order_ids = []
            for oid, html_out in tasks:
                task = ChunkReportService._render_pdf_bytes_worker_gotenberg_with_session(
                    (html_out, base_url), session
                )
                async_tasks.append(task)
                order_ids.append(oid)
            
            # Run all tasks concurrently using gather
            pdf_contents = await asyncio.gather(*async_tasks)
            
            # Combine results with order IDs
            for oid, pdf_content in zip(order_ids, pdf_contents):
                results.append((oid, pdf_content))
                
        return [pdf for _, pdf in sorted(results, key=lambda x: x[0])]

    @staticmethod
    def _prepare_footer_batch_tasks(template_args: dict, total_pages: int, batch_size: int = 200) -> List[Tuple[int, str]]:
        """prepare footer batch tasks"""
        footer_template = ChunkReportService._TEMPLATE_ENV.get_template(f'{TEMPLATE_FOLDER_PATH}/statement_footer.html')
        overlay_style = ChunkReportService._TEMPLATE_ENV.get_template(
            f'{TEMPLATE_FOLDER_PATH}/styles/footer_overlay.html'
        ).render()
        optimized_args = template_args.copy()
        
        tasks: List[Tuple[int, str]] = []
        batch_id = 0
        
        for batch_start in range(1, total_pages + 1, batch_size):
            batch_end = min(batch_start + batch_size, total_pages + 1)

            batch_html_parts = ['<!DOCTYPE html><html><head>']

            batch_html_parts.append(overlay_style)
            batch_html_parts.append('</head><body>')

            for page_num in range(batch_start, batch_end):
                page_args = optimized_args.copy()
                page_args['current_page'] = page_num
                page_args['total_pages'] = total_pages

                footer_html = footer_template.render(page_args)

                batch_html_parts.append(f'<div class="footer-page" id="footer-page-{page_num}"><div class="footer-anchor">{footer_html}</div></div>')
            
            batch_html_parts.append('</body></html>')
            batch_html = ''.join(batch_html_parts)
            
            tasks.append((batch_id, batch_html))
            batch_id += 1
        
        return tasks

    @staticmethod
    def _split_pdf_pages(pdf_bytes: bytes) -> List[bytes]:
        """Split a multi-page PDF into individual page PDFs."""
        individual_pdfs = []
        
        try:
            with pikepdf.Pdf.open(io.BytesIO(pdf_bytes)) as pdf:
                for i, page in enumerate(pdf.pages):
                    # create new PDF for each page
                    single_page_pdf = pikepdf.Pdf.new()
                    single_page_pdf.pages.append(page)
                    
                    # save to bytes
                    output_buffer = io.BytesIO()
                    single_page_pdf.save(output_buffer)
                    individual_pdfs.append(output_buffer.getvalue())
                    
        except Exception as e:
            current_app.logger.error(f"Error splitting PDF pages: {e}")
            raise
            
        return individual_pdfs

    @staticmethod
    def _overlay_footer_pdfs_on_main_pdf(main_pdf_bytes: bytes, footer_pdfs: list) -> bytes:
        """Overlay footer PDFs onto each page of the main PDF."""
        try:
            with pikepdf.Pdf.open(io.BytesIO(main_pdf_bytes)) as main_pdf:
                result_pdf = pikepdf.Pdf.new()

                for i, main_page in enumerate(main_pdf.pages):
                    result_pdf.pages.append(main_page)
                    new_page = result_pdf.pages[-1]  # Get the newly added page
                    
                    # If we have a footer PDF for this page, overlay it
                    if i < len(footer_pdfs):
                        try:
                            with pikepdf.Pdf.open(io.BytesIO(footer_pdfs[i])) as footer_pdf:
                                if len(footer_pdf.pages) > 0:
                                    footer_page = footer_pdf.pages[0]
                                    ChunkReportService._overlay_page_content(new_page, footer_page)
                        except Exception as e:
                            current_app.logger.warning(f"Could not overlay footer on page {i+1}: {e}")

                output_buffer = io.BytesIO()
                result_pdf.save(output_buffer)
                return output_buffer.getvalue()
                
        except Exception as e:
            current_app.logger.error(f"Error overlaying footer PDFs: {e}")
            return main_pdf_bytes

    @staticmethod
    def _overlay_page_content(base_page, overlay_page):
        """Overlay content from overlay_page onto base_page using pikepdf."""
        try:
            if hasattr(base_page, 'add_overlay'):
                base_page.add_overlay(overlay_page)
                return
        except Exception as e:
            current_app.logger.warning(f"Could not overlay page content: {e}")
            pass

    @staticmethod
    def create_chunk_report(
        template_name: str,
        template_vars: Dict[str, Any],
        generate_page_number: bool = False,
        chunk_size: Optional[int] = None,
    ) -> bytes:
        """Create large reports using chunking approach."""
        overall_start_time = time.time()

        if chunk_size is None:
            chunk_size = 500 # the optimal chunk size is 500 after testing

        grouped_invoices = template_vars.get("groupedInvoices", [])
        temp_files: List[str] = []

        # Build all chunk HTMLs ahead of time (keep order id)
        tasks = ChunkReportService._prepare_chunk_tasks(
            template_name, template_vars, grouped_invoices, chunk_size
        )

        base_url = current_app.root_path

        # First pass: render all chunks to PDF bytes in parallel (no footers)
        t0 = time.time()
        pdf_chunks = asyncio.run(ChunkReportService._render_tasks_parallel_async(tasks, base_url))
        t1 = time.time()
        current_app.logger.info(f"_render_tasks_parallel_async: {len(tasks)} tasks, elapsed={t1-t0:.2f}s")

        # Convert PDF bytes to temp files for merging
        for pdf_content in pdf_chunks:
            ChunkReportService._append_pdf_bytes(pdf_content, temp_files)

        merged_pdf_without_footers = ChunkReportService._merge_pdf_files(temp_files)

        ChunkReportService._cleanup_temp_files(temp_files)

        if generate_page_number:
            total_pages = get_pdf_page_count(merged_pdf_without_footers)
            t0 = time.time()
            batch_tasks = ChunkReportService._prepare_footer_batch_tasks(template_vars, total_pages, batch_size=200)
            footer_multi_page_pdfs = asyncio.run(
                ChunkReportService._render_tasks_parallel_async(batch_tasks, current_app.root_path)
            )
            footer_pdfs: List[bytes] = []
            for pdf in footer_multi_page_pdfs:
                footer_pdfs.extend(ChunkReportService._split_pdf_pages(pdf))
            t1 = time.time()
            current_app.logger.info(f"_generate_footer_multi_page_batches: {total_pages} pages, elapsed={t1-t0:.2f}s")
            result = ChunkReportService._overlay_footer_pdfs_on_main_pdf(merged_pdf_without_footers, footer_pdfs)
        else:
            result = merged_pdf_without_footers

        elapsed = time.time() - overall_start_time
        current_app.logger.info(
            "chunk_report done: chunks=%s elapsed=%.1fs", len(tasks), elapsed
        )
        return result
