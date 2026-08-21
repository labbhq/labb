"""What people searched for, and what they failed to find.

The zero-result list is the point: it names what the docs are missing. Reads
``SearchQueryLog``, which only has rows when ``LABB_DOCS["search"]["log_queries"]``
is on. Also carries the documented retention mechanism — there is no auto-expiry,
because labbdocs should not delete from a consumer's table on a schedule they
never set.
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import Count
from django.utils import timezone

from ...conf import log_queries
from ...models import SearchQueryLog

DEFAULT_DAYS = 30
TOP_N = 10


class Command(BaseCommand):
    help = "Report top and zero-result search queries; optionally purge old rows."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=DEFAULT_DAYS,
            help=f"Window in days (default {DEFAULT_DAYS}).",
        )
        parser.add_argument(
            "--top",
            type=int,
            default=TOP_N,
            help=f"How many queries to list per section (default {TOP_N}).",
        )
        parser.add_argument(
            "--purge-older-than",
            type=int,
            metavar="DAYS",
            help="Delete log rows older than DAYS and exit.",
        )

    def handle(self, *args, **options):
        purge_days = options.get("purge_older_than")
        if purge_days is not None:
            return self._purge(purge_days)

        days = options["days"]
        top = options["top"]
        since = timezone.now() - timedelta(days=days)
        rows = SearchQueryLog.objects.filter(created__gte=since)
        total = rows.count()

        if not total:
            if not log_queries():
                self.stdout.write(
                    'No query log. LABB_DOCS["search"]["log_queries"] is off.'
                )
            else:
                self.stdout.write(f"No searches logged in the last {days} days.")
            return

        self.stdout.write(
            self.style.SUCCESS(f"\nTop queries ({days}d, {total} searches)")
        )
        for row in self._counted(rows)[:top]:
            self.stdout.write(f"  {row['n']:>4}  {row['query']}")

        misses = rows.filter(has_results=False)
        miss_total = misses.count()
        if not miss_total:
            self.stdout.write(self.style.SUCCESS("\nZero results: none"))
            return

        share = round(miss_total / total * 100)
        self.stdout.write(
            self.style.WARNING(f"\nZero results ({miss_total} queries, {share}%)")
        )
        for row in self._counted(misses)[:top]:
            self.stdout.write(f"  {row['n']:>4}  {row['query']}")

    def _counted(self, queryset):
        return list(
            queryset.values("query").annotate(n=Count("id")).order_by("-n", "query")
        )

    def _purge(self, days):
        cutoff = timezone.now() - timedelta(days=days)
        deleted, _ = SearchQueryLog.objects.filter(created__lt=cutoff).delete()
        self.stdout.write(
            self.style.SUCCESS(f"Purged {deleted} log rows older than {days} days.")
        )
