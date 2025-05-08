import random
from apps.lineage.games.models import *


def populate_box_with_items(box):
    box_type = box.box_type
    all_items = Item.objects.all()

    for _ in range(box_type.boosters_amount):
        rarity = box_type.get_rarity_by_chance()
        candidates = all_items.filter(rarity=rarity)

        if not candidates.exists():
            continue  # Pula se não tiver item daquela raridade

        selected_item = random.choice(list(candidates))

        BoxItem.objects.create(
            box=box,
            item=selected_item,
            probability=1.0
        )
