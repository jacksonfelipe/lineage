import random
from apps.lineage.games.models import *


def populate_box_with_items(box):
    box_type = box.box_type
    all_items = Item.objects.all()

    # Definindo as probabilidades para cada raridade, baseadas nas chances do box_type
    rarities = {
        'common': box_type.chance_common,
        'rare': box_type.chance_rare,
        'epic': box_type.chance_epic,
        'legendary': box_type.chance_legendary,
    }

    total_chance = sum(rarities.values())  # Soma das probabilidades para normalizar

    # Verificando se a soma das chances é 100% ou algo próximo (validação simples)
    if total_chance != 100:
        raise ValueError(f"A soma das chances não é 100%. Soma atual: {total_chance}")

    # Definindo a quantidade de boosters para cada raridade com base nas probabilidades
    boosters_count = box_type.boosters_amount
    boosters_by_rarity = {
        rarity: int((boosters_count * chance) / 100)
        for rarity, chance in rarities.items()
    }

    # Corrige a distribuição caso o arredondamento tenha gerado uma diferença de contagem
    difference = boosters_count - sum(boosters_by_rarity.values())
    for rarity in sorted(rarities, key=lambda x: rarities[x], reverse=True):  # Atribui os restantes para as raridades com maior chance
        if difference > 0:
            boosters_by_rarity[rarity] += 1
            difference -= 1

    # Adiciona os itens ao box
    for rarity, count in boosters_by_rarity.items():
        if count > 0:
            candidates = all_items.filter(rarity=rarity)
            if not candidates.exists():
                continue  # Pula se não houver itens da raridade

            for _ in range(count):
                selected_item = random.choice(list(candidates))
                BoxItem.objects.create(
                    box=box,
                    item=selected_item,
                    probability=1.0
                )
