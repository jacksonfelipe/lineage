from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import reverse
from apps.lineage.games.models import *
from apps.lineage.games.forms import *


@staff_member_required
def dashboard(request):
    context = {
        'box_type_count': BoxType.objects.count(),
        'box_count': Box.objects.count(),
    }
    return render(request, 'box/manager/dashboard.html', context)


# VIEWS DA SESSAO BOX (user)
@staff_member_required
def box_list_view(request):
    boxes = Box.objects.select_related('user', 'box_type').all()
    return render(request, 'box/manager/box/list.html', {'boxes': boxes})


@staff_member_required
def box_create_view(request):
    if request.method == 'POST':
        form = BoxForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('games:box_list'))
    else:
        form = BoxForm()
    return render(request, 'box/manager/box/create.html', {'form': form})


@staff_member_required
def box_edit_view(request, pk):
    box = get_object_or_404(Box, pk=pk)
    if request.method == 'POST':
        form = BoxForm(request.POST, instance=box)
        if form.is_valid():
            form.save()
            return redirect(reverse('games:box_list'))
    else:
        form = BoxForm(instance=box)
    return render(request, 'box/manager/box/edit.html', {'form': form, 'box': box})


@staff_member_required
def box_delete_view(request, pk):
    box = get_object_or_404(Box, pk=pk)
    print(box.box_type.name)
    if request.method == 'POST':
        box.delete()
        return redirect(reverse('games:box_list'))
    return render(request, 'box/manager/box/delete.html', {'box': box})


# VIEWS DA SESSAO BOX ITEM (user)
@staff_member_required
def box_item_list_view(request, box_id):
    box = get_object_or_404(Box, pk=box_id)
    box_items = box.items.select_related('item').all()
    return render(request, 'box/manager/box_item/list.html', {'box': box, 'box_items': box_items})


@staff_member_required
def box_item_create_view(request, box_type_id):
    box_type = get_object_or_404(BoxType, pk=box_type_id)
    if request.method == 'POST':
        form = BoxItemForm(request.POST)
        if form.is_valid():
            box_item = form.save(commit=False)
            box_item.box_type = box_type
            box_item.save()
            return redirect('games:box_item_list', box_type_id=box_type.id)
    else:
        form = BoxItemForm()
    return render(request, 'box/manager/box_item/form.html', {'form': form, 'box_type': box_type})


@staff_member_required
def box_item_edit_view(request, pk):
    box_item = get_object_or_404(BoxItem, pk=pk)
    if request.method == 'POST':
        form = BoxItemForm(request.POST, instance=box_item)
        if form.is_valid():
            form.save()
            return redirect(reverse('games:box_item_list', args=[box_item.box.id]))
    else:
        form = BoxItemForm(instance=box_item)
    return render(request, 'box/manager/box_item/edit.html', {'form': form, 'box_item': box_item, 'box': box_item.box})


@staff_member_required
def box_item_delete_view(request, pk):
    box_item = get_object_or_404(BoxItem, pk=pk)
    box = box_item.box
    if request.method == 'POST':
        box_item.delete()
        return redirect(reverse('games:box_item_list', args=[box.id]))
    return render(request, 'box/manager/box_item/delete.html', {'box_item': box_item, 'box': box})


# VIEWS DA SESSAO BOX TPE (user)
@staff_member_required
def box_type_list_view(request):
    box_types = BoxType.objects.all()
    return render(request, 'box/manager/box_type/list.html', {'box_types': box_types})


@staff_member_required
def box_type_create_view(request):
    if request.method == 'POST':
        form = BoxTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('games:box_type_list')
    else:
        form = BoxTypeForm()
    return render(request, 'box/manager/box_type/form.html', {'form': form})


@staff_member_required
def box_type_edit_view(request, pk):
    box_type = get_object_or_404(BoxType, pk=pk)
    if request.method == 'POST':
        form = BoxTypeForm(request.POST, instance=box_type)
        if form.is_valid():
            form.save()
            return redirect('games:box_type_list')
    else:
        form = BoxTypeForm(instance=box_type)
    return render(request, 'box/manager/box_type/form.html', {'form': form, 'box_type': box_type})


@staff_member_required
def box_type_delete_view(request, pk):
    box_type = get_object_or_404(BoxType, pk=pk)
    if request.method == 'POST':
        box_type.delete()
        return redirect('games:box_type_list')
    return render(request, 'box/manager/box_type/delete_confirm.html', {'box_type': box_type})
