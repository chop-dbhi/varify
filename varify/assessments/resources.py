from django.conf.urls import patterns, url
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from django.utils import simplejson
from preserialize.serialize import serialize
from restlib2.http import codes
from serrano.resources.base import ThrottledResource
from varify import api
from vdw.assessments.models import Assessment
from .forms import AssessmentForm


class AssessmentResourceBase(ThrottledResource):
    model = Assessment
    template = api.templates.Assessment

    def prepare(self, assessment):
        data = {}

        data['id'] = assessment.pk
        data['evidence_details'] = assessment.evidence_details
        data['sanger_requested'] = assessment.sanger_requested
        data['pathogenicity'] = assessment.pathogenicity.pk
        data['assessment_category'] = assessment.assessment_category.pk
        data['mother_result'] = assessment.mother_result.pk
        data['father_result'] = assessment.father_result.pk
        data['sample_result'] = assessment.sample_result.pk

        return simplejson.dumps(data)


class AssessmentsResource(AssessmentResourceBase):
    def get(self, request):
        return HttpResponse(status=codes.no_content)

    def post(self, request):
        data = request.data

        if hasattr(request, 'user'):
            data['user'] = request.user.id
        else:
            response = HttpResponse(status=codes.unprocessable_entity,
                                    content="Request user is not valid.")
            return response

        form = AssessmentForm(data)

        if form.is_valid():
            instance = form.save()

            response = HttpResponse(status=codes.created,
                                    content=self.prepare(instance),
                                    mimetype='application/json')
        else:
            response = HttpResponse(status=codes.unprocessable_entity,
                                    content=dict(form.errors))

        return response


class AssessmentResource(AssessmentResourceBase):
    def is_not_found(self, request, response, pk):
        try:
            instance = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return True

        request.instance = instance
        return False

    def get(self, request, pk):
        data = serialize(request.instance, **self.template)

        return data

    def put(self, request, pk):
        data = request.data

        if hasattr(request, 'user'):
            data['user'] = request.user.id
        else:
            response = HttpResponse(status=codes.unprocessable_entity,
                                    content="Request user is not valid.")
            return response

        form = AssessmentForm(data, instance=request.instance)

        if form.is_valid():
            form.save()
            response = HttpResponse(status=codes.ok,
                                    content=self.prepare(request.instance),
                                    mimetype='application/json')
        else:
            response = HttpResponse(status=codes.unprocessable_entity,
                                    content=dict(form.errors))

        return response


assessments_resource = never_cache(AssessmentsResource())
assessment_resource = never_cache(AssessmentResource())

urlpatterns = patterns(
    '',
    url(r'^$', assessments_resource, name='assessments'),
    url(r'^(?P<pk>\d+)/$', assessment_resource, name='assessment'),
)
