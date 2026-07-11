from django.core.management.base import BaseCommand

from shop.models import Product

PRODUCTS = [
    # Clothing
    dict(sku="p01", name="Everyday Crewneck Tee", subtitle="100% combed cotton", category="clothing", price=499, stock="in", icon="shirt"),
    dict(sku="p02", name="Waxed Field Jacket", subtitle="Cotton canvas, water-resistant", category="clothing", price=2999, stock="low", icon="jacket"),
    dict(sku="p03", name="Tapered Chino Trousers", subtitle="Stretch cotton twill", category="clothing", price=1499, stock="in", icon="trousers"),
    dict(sku="p04", name="Wrap Midi Dress", subtitle="Viscose blend", category="clothing", price=2199, stock="in", icon="dress"),
    # Shoes
    dict(sku="p05", name="Court Classic Sneaker", subtitle="Leather upper, rubber sole", category="shoes", price=2499, stock="in", icon="sneaker"),
    dict(sku="p06", name="Block Heel Sandal", subtitle="Vegan leather", category="shoes", price=1799, stock="low", icon="heel"),
    dict(sku="p07", name="Chelsea Boot", subtitle="Suede, elastic gusset", category="shoes", price=3499, stock="in", icon="boot"),
    dict(sku="p08", name="Trail Running Shoe", subtitle="Breathable mesh", category="shoes", price=2799, stock="in", icon="sneaker"),
    # Grocery
    dict(sku="p09", name="Orchard Apples, 1kg", subtitle="Locally sourced", category="grocery", price=180, stock="in", icon="apple"),
    dict(sku="p10", name="Sourdough Loaf", subtitle="Baked fresh daily", category="grocery", price=90, stock="in", icon="bread"),
    dict(sku="p11", name="Cold-Pressed Olive Oil", subtitle="500ml, first press", category="grocery", price=899, stock="low", icon="bottle"),
    dict(sku="p12", name="Farmstand Veg Basket", subtitle="Seasonal mix", category="grocery", price=399, stock="in", icon="basket"),
    # Electronics
    dict(sku="p13", name="Wireless Over-Ear Headphones", subtitle="30hr battery life", category="electronics", price=3499, stock="in", icon="headphones"),
    dict(sku="p14", name="Everyday Smartwatch", subtitle="Heart rate + GPS", category="electronics", price=4999, stock="low", icon="watch"),
    dict(sku="p15", name="Portable Bluetooth Speaker", subtitle="IPX6 water resistant", category="electronics", price=2299, stock="in", icon="speaker"),
    dict(sku="p16", name="Studio Desk Lamp", subtitle="Dimmable LED", category="electronics", price=1499, stock="in", icon="lamp"),
    # Home
    dict(sku="p17", name="Rattan Accent Chair", subtitle="Solid oak frame", category="home", price=8999, stock="low", icon="chair"),
    dict(sku="p18", name="Ceramic Table Lamp", subtitle="Linen shade", category="home", price=1799, stock="in", icon="lamp"),
    dict(sku="p19", name="Stoneware Mug Set of 4", subtitle="Dishwasher safe", category="home", price=899, stock="in", icon="mug"),
    dict(sku="p20", name="Woven Lounge Chair", subtitle="Indoor/outdoor", category="home", price=6999, stock="in", icon="chair"),
    # Beauty
    dict(sku="p21", name="Signature Eau de Parfum", subtitle="50ml, citrus & cedar", category="beauty", price=2499, stock="in", icon="perfume"),
    dict(sku="p22", name="Matte Lipstick", subtitle="Long-wear formula", category="beauty", price=699, stock="in", icon="lipstick"),
    dict(sku="p23", name="Kabuki Makeup Brush", subtitle="Vegan bristles", category="beauty", price=399, stock="low", icon="brush"),
    dict(sku="p24", name="Rosewater Face Mist", subtitle="Alcohol-free, 100ml", category="beauty", price=599, stock="in", icon="bottle"),
]


class Command(BaseCommand):
    help = "Seeds the database with the Bazarify demo catalog."

    def handle(self, *args, **options):
        created, updated = 0, 0
        for entry in PRODUCTS:
            _, was_created = Product.objects.update_or_create(sku=entry["sku"], defaults=entry)
            if was_created:
                created += 1
            else:
                updated += 1
        self.stdout.write(self.style.SUCCESS(f"Seeded products: {created} created, {updated} updated."))
