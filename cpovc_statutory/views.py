from django.shortcuts import render

from cpovc_forms.forms import OVCSearchForm
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
import json
import random
import uuid
# from itertools import chain #
from datetime import datetime
from dateutil.relativedelta import relativedelta
from cpovc_forms.forms import (
    OVCSearchForm,)
from cpovc_forms.models import (
   OVCCaseRecord,
)
from cpovc_main.functions import (
     get_dict, get_list_of_persons, translate_geo,)
from cpovc_forms.functions import (save_audit_trail)
from cpovc_main.country import (COUNTRIES)
from cpovc_registry.models import (
RegPerson,RegPersonsGeo)
import uuid
from datetime import datetime, timedelta
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib import messages
from cpovc_auth.models import AppUser
from cpovc_registry.models import (
    RegOrgUnit, RegOrgUnitContact, RegPerson, RegPersonsOrgUnits,
    RegPersonsTypes, RegPersonsGuardians, RegPersonsGeo, RegPersonsExternalIds,
    RegPersonsSiblings)
from cpovc_registry.forms import (
    RegistrationForm, RegistrationSearchForm, NewUser)
from cpovc_main.functions import (
    workforce_id_generator, beneficiary_id_generator, get_org_units_dict)
from cpovc_main.models import SetupGeography
from cpovc_auth.decorators import is_allowed_groups

from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control

from cpovc_main.country import COUNTRIES
from cpovc_ovc.models import OVCRegistration
from cpovc_ovc.functions import get_ovcdetails
from cpovc_ovc.views import ovc_register
from cpovc_forms.views import new_case_record_sheet
from cpovc_forms.models import OVCCaseGeo, OVCCaseEvents

from cpovc_reports.forms import CaseLoad

now = timezone.now()


# For CTiP
from cpovc_ctip.settings import CATS
from cpovc_ctip.forms import CTIPForm
from cpovc_ctip.functions import handle_ctip, get_ctip

# Create your views here.

def stat_home(request):
    try:
        form = OVCSearchForm(data=request.GET)
        # form = SearchForm(data=request.POST)
        # person_type = 'TBVC'
        return render(request, 'statutory/home.html',
                      {'status': 200, 'form': form})
    except Exception as e:
        raise e

def remand(request):
    try:
        return render(request, 'statutory/remand_preadmission.html'
                      )
    except Exception as e:
        raise e
def rescue(request):
    try:
        return render(request, 'statutory/rescue_preadmission.html'
                      )
    except Exception as e:
        raise e
    
def rehab(request):
    try:
        return render(request, 'statutory/rescue_preadmission.html'
                      )
    except Exception as e:
        raise e

def case_record_sheet(request):
    form = OVCSearchForm(data=request.POST, initial={'person_type': 'TBVC'})
    check_fields = ['sex_id', 'person_type_id', 'identifier_type_id']
    vals = get_dict(field_name=check_fields)
    if request.method == 'POST':
        resultsets = None
        person_type = None

        try:
            person_type = 'TBVC'
            search_string = request.POST.get('search_name')
            search_criteria = request.POST.get('search_criteria')
            number_of_results = 1000
            type_of_person = [person_type] if person_type else []
            include_died = False

            resultsets = get_list_of_persons(
                search_string=search_string,
                number_of_results=number_of_results,
                in_person_types=type_of_person,
                include_died=include_died,
                search_criteria=search_criteria)

            if resultsets:
                for result in resultsets:

                    # Add case_count to result <object>
                    case_count = OVCCaseRecord.objects.filter(
                        person=int(result.id), is_void=False).count()
                    setattr(result, 'case_count', case_count)

                    # Add child_geo to result <object>
                    ovc_persongeos = RegPersonsGeo.objects.filter(
                        person=int(result.id)).values_list(
                        'area_id', flat=True).order_by('area_id')
                    geo_locs = []
                    for ovc_persongeo in ovc_persongeos:
                        area_id = str(ovc_persongeo)
                        geo_locs.append(translate_geo(int(area_id)))

                    persongeos = ', '.join(geo_locs)

                    setattr(result, 'ovc_persongeos', persongeos)

                msg = 'Showing results for (%s)' % search_string
                messages.add_message(request, messages.INFO, msg)
                return render(request, 'statutory/home.html',
                              {'form': form,
                               'resultsets': resultsets,
                               'vals': vals,
                               'person_type': person_type})
            else:
                msg = 'No results for (%s).' % (search_string)
                msg += 'Name does not exist in database.'
                messages.add_message(request, messages.ERROR, msg)
        except Exception as e:
            msg = 'OVC search error - %s' % (str(e))
            messages.add_message(request, messages.INFO, msg)
        return HttpResponseRedirect(reverse(case_record_sheet))
    else:
        cpims_id = request.GET.get('cpims_id', False)
        form = OVCSearchForm(initial={'search_criteria': 'NAME'})
        if cpims_id:
            resultsets = RegPerson.objects.filter(id=cpims_id)
            return render(
                request, 'statutory/home.html',
                {'form': form, 'resultsets': resultsets,
                 'vals': vals, 'person_type': person_type})
        form = OVCSearchForm(initial={'search_criteria': 'NAME'})
        return render(request, 'statutory/home.html',
                      {'form': form})
