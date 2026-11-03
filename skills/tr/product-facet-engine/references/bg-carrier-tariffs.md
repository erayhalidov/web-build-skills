# Bulgar taşıyıcı tarifeleri (Speedy / DPD) — katalog mağazaları için yayınlanmış fiyatlar

"Her Avrupa ülkesi için gerçek teslimat fiyatları ekle" istekleri için bilgi bankası. Buradaki her sayı
taşıyıcının yayınlanmış fiyat listesinden — asla listede olmayan bir varış noktasına dış değer biçme.

## Keşif gerçekleri (bir dahaki sefere bir saat kazandırır)

| Gerçek | Ayrıntı |
| --- | --- |
| `www.dpd.bg` | **Speedy**'nin uluslararası sayfalarına yönlendirir — Bulgaristan'da DPD ağını Speedy işletir, dolayısıyla "Speedy - DPD" iki teklif değil tek bir hizmettir. |
| `https://www.dpd.bg` (443) | Sunucudan bağlantı reddedildi. Düz `http://www.dpd.bg/` 200 döner ve speedy.bg'ye yönlendirme verir. |
| `https://www.speedy.bg/...` | Cloudflare "Just a moment…" JS meydan okuması — düz bir getirme meydan okuma sayfasını alır, headless Chromium da orada takılır. |
| `https://services.speedy.bg/priceList/?lang=en` | **Asıl fiyat listesi.** Normal tarayıcı UA'sıyla düz curl'e 200, meydan okuma yok. `<title>` sürüm tarihini taşır (`Speedy Price List 13.09.2026`) — müşterilere o tarihi belirtin. |

```bash
curl -sSL -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36" \
  -o /tmp/sp_pl.html "https://services.speedy.bg/priceList/?lang=en"
```

Sayfayı ayrıştırma (~200 KB satır içi tablo):
```python
import re, html as H
s = open('/tmp/sp_pl.html', encoding='utf-8', errors='replace').read()
flat = H.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '|', s))).replace('\xa0', ' ')  # prices use &nbsp;
flat = re.sub(r'\|+', '|', flat)
```
* Tutar ile € işareti arasındaki `\xa0` her fiyat regex'ini bozar — önce normalleştirin.
* Başlık satırı genellikle kendi `<table>` öğesinde yaşar, ülke satırları ise dışında kalır, dolayısıyla `<table>…</table>`
  sınırları arasında dilimlemek gövdeyi kaybeder. Bunun yerine **düzleştirilmiş metni** hizmet başlığı ile
  izleyen şablon paragraf arasında dilimleyin.
* Ülke adları parantez taşıyabilir (`CROATIA (LOCAL NAME: HRVATSKA)`) — `[A-Z][A-Z \.\-\(\)']{3,60}`
  ile eşleştirin ve yine de kaybedersiniz; satır sayısını bölge listesine karşı doğrulayın.

## Bulgaristan'dan giden hizmetler

| Kod | Hizmet | Ağırlık bantları | Notlar |
| --- | --- | --- | --- |
| 202 | Speedy CEE Economy | 1, 2, 3, 4, 5, 7, 10, 20, 31.5 kg | RO/GR son bant `21.72 € + her ek kg için 1.09 €`. |
| 306 | DPD Economy — kapıdan kapıya | 0.5, 5, 10, 31.5, 40 kg | Batı / Kuzey Avrupa karayolu hizmeti. |
| 308 | DPD Economy **Toplama talebi** | 0.5, 5, 10, 31.5, 40 kg | Bulgaristan'a **gelen** toplamalar — giden siparişler için asla bu fiyatı vermeyin. |
| 302 | Speedy Air Express | 0.5 kg adım, 10 kg'a kadar 20 bant | Bölge 1 (karayolu ağı dışındaki AB), Bölge 2 (AB dışı Avrupa), 3/4 (dünya). 10 kg üzeri → talep üzerine. |

Yayınlanan tüm tutarlar **KDV'yi ve yakıt ek ücretini zaten içerir**.

## Ülke → hizmet eşlemesi

* **202 CEE Economy** — RO, GR, HU, CZ, PL, SK, SI, HR, CY
* **306 DPD Economy** — AT, DE, BE, FR, IT, NL, DK, LU, ES, EE, FI, LV, LT, PT, SE
* **302 Air Bölge 1** — IE, MT (bölge-1 listesi ayrıca AT, BE, HR, CY, CZ, DK, EE, FI, FR, DE, GR, HU, IE, IT, LV, LT, LU, MT, NL, PL, PT, SK, SI, ES, SE adlarını da verir)
* **302 Air Bölge 2** — AL, AD, BA, FO, GI, GL, VA, IS, LI, MC, ME, NO, SM, RS, CH, TR, GB, GG, JE, Kanarya Adaları
* **Hiçbir yerde listelenmemiş** (UA, US, …) → "talep üzerine fiyat". Ara değer uydurmayın.

Basıldığı şekliyle geçiş süreleri: DE/AT/CZ/PL 3-4 · HU/SK 2-3 · SI 3-4 · HR/BE/FR/IT/NL/DK/LU/LV/LT 4-5 · ES 5-6 ·
SE 5-6 · EE 5-6 · FI/PT 5-7 · Air Bölge 1 1-2 · Air Bölge 2 1-3. RO/GR/CY **basılmamıştır** — tahmin etmek yerine
sütunu atlayın.

## Fiyat matrisi (sürüm 13.09.2026)

202 CEE Economy, bantlar 1 → 31.5 kg:
```
RO        5.27  5.71  6.13 10.96 10.96 13.63 16.76 21.72 21.72 (+1.09 €/kg over 31.5)
GR        6.44  7.36  7.36 10.96 10.96 13.63 16.76 21.72 21.72 (+1.09 €/kg over 31.5)
HU        8.84  9.70 10.57 23.17 23.17 27.68 27.68 27.68 27.68
CZ        8.84  9.70 10.57 32.21 32.21 38.22 38.22 38.22 38.22
PL/SK/SI/HR 8.84 9.70 10.57 45.76 45.76 51.04 51.04 53.14 53.14
CY       17.03 19.21 21.36 23.72 25.87   —     —     —     —   (only to 5 kg)
```

306 DPD Economy, bantlar 0.5 / 5 / 10 / 31.5 / 40 kg:
```
AT, DE                     23.78 23.78 28.32 28.32  65.14
BE, FR, IT, NL             32.82 32.82 38.83 38.83  75.67
DK, LU                     44.26 46.38 51.64 53.77  90.58
ES                         42.59 42.59 50.11 50.11  86.94
EE, FI, LV, LT, PT, SE     63.28 65.38 71.71 74.89 111.72
```

302 Air Express: bölge 1 68.41 €'dan başlar (≤0.5 kg) ve 0.5 kg adımı başına ~10-15 € artar; bölge 2 84.08 €'dan.
Yaklaşık değer vermek yerine yayınlanan 20 satırı aktarın.

Mevcut ek ücretler (SSS'te belirtin, teklife sessizce eklemeyin): ada/uzak posta kodu
28.06 € (202) / 26.54 € (308) KDV dahil · 50 kg üzeri ağır koli 12.77 € · bir kenarı >100 cm ise elleçleme
1.94 € · kapıda ödeme %2.4 (uluslararası min 1.23 €). Son kontrol edildiğinde yürürlükte olan kampanya: **DE ve IT için 306 tarife
fiyatlarında -%25, 01.09.2024 – 30.09.2026**.

## Siteye bağlama

`inc/shipping.php`:
* `shipping_services()` — hizmet anahtarı başına etiket, taşıyıcı, bant listesi, not
* `shipping_rates()` — hizmet → varış grubu → bant başına fiyat (diziler bantlarla aynı sırada)
* `shipping_map()` — ISO2 → `['service' =>, 'group' =>, 'days' =>]`
* `shipping_quote($cc, $kg)` — ağırlığın sığdığı ilk bant; **yayınlanan bantların ötesinde `price = null`**
  ki arayüz tahmin etmek yerine "talep üzerine" diyebilsin
* `shipping_pickup()` (ücretsiz, 0.00) ve `shipping_options()`
* `shipping_updated()` — müşterilere gösterilen sürüm dizesi

Ağırlık katalogdan gelir (`products.weight`; paylaşılan SELECT'lerde `AS weight_kg` takma adı verin), adet üzerinden
toplanır. Ağırlığı olmayan öğeler belgelenmiş 0.5 kg tahmini katkı yapar ve sayfa ağırlığın kısmen tahmini
olduğunu söyler. Her şeyi **POST'ta sunucu tarafında** ürün slug'ından yeniden hesaplayın — tarayıcı sepetine
fiyat veya ağırlık için güvenilmez.

Render: teslimat sayfasında (`Delivery prices to every European country`) aynı dizilerden kurulan bir fiyat
tablosu, böylece ödeme akışından asla kopamaz. Oranlar değişirse → üç diziyi değiştir, `shipping_updated()`
sürümünü artır, rota taramasını yeniden çalıştır.
