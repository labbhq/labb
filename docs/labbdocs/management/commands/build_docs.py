from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from ...doc_parser import CONTENT_BASE_PATH, DocParser


class Command(BaseCommand):
    help = "Parse and build documentation from a markdown folder"

    def add_arguments(self, parser):
        parser.add_argument(
            "doc_name",
            type=str,
            help="Name of the documentation to build (must be configured in LABB_DOCS)",
        )
        parser.add_argument(
            "--quiet", action="store_true", help="Suppress output messages"
        )

    def handle(self, *args, **options):
        doc_name = options["doc_name"]
        quiet = options["quiet"]

        # Get LABB_DOCS configuration from Django settings
        labb_docs = getattr(settings, "LABB_DOCS", {})
        doc_types = labb_docs.get("types", {})

        if doc_name not in doc_types:
            raise CommandError(
                f"Documentation '{doc_name}' not found in LABB_DOCS configuration"
            )

        doc_config = doc_types[doc_name]

        # Get configuration values
        yaml_output_path = doc_config.get("config")
        if not yaml_output_path:
            raise CommandError(
                f"No config path specified for documentation '{doc_name}'"
            )

        url_prefix = doc_config.get("url_prefix", f"/docs/{doc_name}")
        template_dir = doc_config["template_dir"]
        # Get build path from configuration
        build_path = doc_config["build_path"]

        content_path = CONTENT_BASE_PATH / doc_name
        content_path = str(content_path)

        # Check if the content path exists
        content_path_obj = Path(content_path)
        if not content_path_obj.exists():
            raise CommandError(f"Content path '{content_path}' does not exist")

        if not content_path_obj.is_dir():
            raise CommandError(f"Content path '{content_path}' is not a directory")

        # Initialize the DocParser
        if not quiet:
            self.stdout.write(
                f"Parsing documentation '{doc_name}' from: {content_path}"
            )
            self.stdout.write(f"Using URL prefix: {url_prefix}")
            self.stdout.write(f"Build path: {build_path}")
            self.stdout.write(f"YAML output: {yaml_output_path}")

        try:
            seo_config = labb_docs.get("seo", {})

            parser = DocParser(
                name=doc_name,
                content_path=content_path,
                build_path=build_path,
                template_dir=template_dir,
                url_prefix=url_prefix,
                yaml_output_path=yaml_output_path,
                seo_config=seo_config,
            )

            # Parse and save the documentation
            parser.save_to_yaml()

            if not quiet:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully built documentation '{doc_name}' to: {parser.docs_yaml_path}"
                    )
                )

        except Exception as e:
            raise CommandError(f"Error building documentation: {str(e)}")
