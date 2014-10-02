try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
from django.conf import settings
from django.db.models import Q
from guardian.shortcuts import get_objects_for_user
from avocado.formatters import registry as formatters
from serrano.formatters import HTMLFormatter


class AlamutFormatter(HTMLFormatter):
    href = settings.ALAMUT_URL + '/show?request={0}'
    request = 'chr{chr}:g.{pos}{ref}>{alt}'

    def to_html(self, values, **context):
        request = self.request.format(**values)
        href = self.href.format(request)
        return '<a target=_blank href="{href}">{label}</a>'.format(
            href=href, label=request)
    to_html.process_multiple = True

    def to_excel(self, values, **context):
        request = self.request.format(**values)
        href = self.href.format(request)

        return '=HYPERLINK("{href}", "{label}")'.format(
            href=href, label=request)
    to_excel.process_multiple = True


class SampleFormatter(HTMLFormatter):
    def to_html(self, values, **kwargs):
        return values['sample__label']

    to_html.process_multiple = True


class ReadDepthFormatter(HTMLFormatter):
    template = '<span class="text-{label_class}">{read_depth}x</span> '\
        '<span class=muted>({coverage_ref}/{coverage_alt})</span>'

    def to_html(self, values, **kwargs):
        label_class = ''
        if values['read_depth'] < 10:
            label_class = 'warning'
        elif values['read_depth'] >= 30:
            label_class = 'success'
        return self.template.format(label_class=label_class, **values)

    to_html.process_multiple = True


class CohortsFormatter(HTMLFormatter):
    # Cache cohort data since cannot and should not change during this
    # formatter's usage
    def _get_cohorts(self, **context):
        if not hasattr(self, '_cohorts'):
            from vdw.samples.models import Cohort
            # Augment resource with cohort-related details
            # (e.g. allele frequencies).
            perms = Q(user=None, published=True)

            # All cohorts this user has permission to.
            projects = None
            if 'request' in context:
                perms |= Q(user=context['request'].user)
                projects = get_objects_for_user(
                    context['request'].user, 'samples.view_project')

            cohorts = Cohort.objects.filter(perms, batch=None)

            if projects is not None:
                cohorts = cohorts.filter(project__in=projects)

            self._cohorts = list(
                cohorts.only('name', 'count').order_by('order', 'name'))

        return self._cohorts

    def _get_cohort_variants(self, value, **context):
        from vdw.samples.models import CohortVariant
        cohorts = self._get_cohorts(**context)

        # All cohort variants for the above cohorts
        variants = dict(
            CohortVariant.objects.filter(
                variant__pk=value, cohort__in=cohorts)
            .values_list('cohort__pk', 'af').distinct())
        output = []
        for c in cohorts:
            output.append((c.name, variants.get(c.pk, 0), c.count))
        return output

    def to_html(self, value, **context):
        variants = self._get_cohort_variants(value, **context)

        html = ['<ul class=unstyled>']
        for name, af, count in variants:
            html.append('<li><small>{0}</small> {1}% <span class=muted>({2})'
                        '</span></li>'.format(name, str(af * 100), count))
        html.append('</ul>')

        return ''.join(html)

    def to_excel(self, value, **context):
        variants = self._get_cohort_variants(value, **context)
        output = OrderedDict()
        for name, af, count in variants:
            key = '{0} Cohort Allele Freq ({1} samples)'.format(name, count)
            output[key] = af
        return output

    to_csv = to_excel


formatters.register(AlamutFormatter, 'Alamut Query Link')
formatters.register(SampleFormatter, 'Sample')
formatters.register(ReadDepthFormatter, 'Read Depth')
formatters.register(CohortsFormatter, 'Cohorts')
