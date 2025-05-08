import random
from apps.lineage.games.models import *


def open_box(user, box_id):
    try:
        box = Box.objects.get(id=box_id)
    except Box.DoesNotExist:
        return None, "Caixa não encontrada."

    items = list(box.items.all())
    if not items:
        return None, "Caixa vazia."

    selected_item = random.choices(
        items,
        weights=[item.probability for item in items],
        k=1
    )[0]

    # Garante que o usuário tem uma bag
    bag, _ = Bag.objects.get_or_create(user=user)

    # Tenta atualizar item existente ou criar novo
    bag_item, created = BagItem.objects.get_or_create(
        bag=bag,
        item_id=selected_item.item.item_id,
        enchant=selected_item.item.enchant,  # Acesse o enchant do Item, não de BoxItem
        defaults={
            'item_name': selected_item.item.name,  # Acesse o nome do Item corretamente
            'quantity': 1,
        }
    )

    if not created:
        bag_item.quantity += 1
        bag_item.save()

    return selected_item.item, None
