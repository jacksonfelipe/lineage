import json
from .models import Event

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from apps.main.home.decorator import conditional_otp_required

from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime


@conditional_otp_required
def calendar(request):
    context = {
        'segment': 'calendar',
    }
    return render(request, 'pages/calendar.html', context)


@conditional_otp_required
def get_events(request):
    events = Event.objects.filter(user=request.user)
    data = []
    for event in events:
        data.append({
            "id": event.id,
            "title": event.title,
            "start": event.start_date.strftime('%Y-%m-%d'),
            "end": event.end_date.strftime('%Y-%m-%d'),
            "className": event.className
        })
    return JsonResponse(data, safe=False)


@csrf_exempt
@conditional_otp_required
@require_http_methods(["POST"])
def create_event(request):
    try:
        data = json.loads(request.body)
        title = data.get("title")
        start = parse_datetime(data.get("start"))
        end = parse_datetime(data.get("end"))
        className = data.get("className", "bg-red")

        if not title or not start or not end:
            return HttpResponseBadRequest("Dados incompletos")

        event = Event.objects.create(
            user=request.user,
            title=title,
            start_date=start,
            end_date=end,
            className=className
        )
        return JsonResponse({
            "id": event.id,
            "title": event.title,
            "start": event.start_date.strftime('%Y-%m-%d'),
            "end": event.end_date.strftime('%Y-%m-%d'),
            "className": event.className
        })
    except Exception as e:
        return HttpResponseBadRequest(str(e))


@csrf_exempt
@conditional_otp_required
@require_http_methods(["POST"])
def update_event(request, event_id):
    try:
        data = json.loads(request.body)
        event = Event.objects.get(id=event_id, user=request.user)

        event.title = data.get("title", event.title)
        event.start_date = parse_datetime(data.get("start")) or event.start_date
        event.end_date = parse_datetime(data.get("end")) or event.end_date
        event.className = data.get("className", event.className)
        event.save()

        return JsonResponse({
            "id": event.id,
            "title": event.title,
            "start": event.start_date.strftime('%Y-%m-%d'),
            "end": event.end_date.strftime('%Y-%m-%d'),
            "className": event.className
        })
    except Event.DoesNotExist:
        return HttpResponseForbidden("Evento não encontrado ou sem permissão")
    except Exception as e:
        return HttpResponseBadRequest(str(e))


@csrf_exempt
@conditional_otp_required
@require_http_methods(["POST"])
def delete_event(request, event_id):
    try:
        event = Event.objects.get(id=event_id, user=request.user)
        event.delete()
        return JsonResponse({"status": "deleted"})
    except Event.DoesNotExist:
        return HttpResponseForbidden("Evento não encontrado ou sem permissão")
    except Exception as e:
        return HttpResponseBadRequest(str(e))
