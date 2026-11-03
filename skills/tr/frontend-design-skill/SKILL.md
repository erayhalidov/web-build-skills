---
name: frontend-design-skill
description: "Ön yüz düzeni ve CSS tasarlarken veya incelerken kullanın."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [frontend, design, css, layout, typography, color, motion, accessibility]
    related_skills: [design-extraction-and-fidelity, ui-ux-pro-max, tailwind-v4, responsive-mobile-qa]
---

# Ön yüz tasarım becerisi

Çıktının **bir insanın baktığı ekran** olduğu her görev için kullanın: açılış sayfaları, paneller,
formlar, kartlar, navigasyon. Bu kullanıcı **yalnızca özel CSS — Tailwind 2 kez reddedildi**; ona asla
uzanmayın. Tasarım tahmin edilmez, ölçülür: token çıkarımı için `design-extraction-and-fidelity` dosyasına bakın.

## Bu kullanıcı için vazgeçilmezler

- **Değişkenli özel CSS.** Tailwind yok, Bootstrap yok, bileşen kütüphanesi varsayılanları yok.
- **Canlıya çıkmadan önce 2–3 demo varyantı.** Demolar ayrı `.html` dosyalarında yaşar, asla canlı
  alan adında değil.
- **Herhangi bir arayüz değişikliğinde mevcut PHP mantığını ve i18n'i koruyun.** Bir form gönderimini
  ya da çeviri anahtarını bozan yeniden tasarım bir gerilemedir, yeniden tasarım değildir.
- **Bir düzen hatasını gizlemek için `display:none` / `overflow:hidden` yok.** Düzeni düzeltin.
- **"samo mobile" masaüstüne dokunma demektir.**
- **Genel siteler: EN varsayılan + BG değiştirici.**
- Bölümler **ayrı kartlar**dır, tek uzun ayrışmamış sütun değil.
- Butonlar **yüksek kontrast** gerektirir — koyu zeminde asla düşük kontrastlı hayalet buton.

## Düzen

1. **Piksellerden önce ızgaraya karar verin.** İçerik sütunu, boşluklar ve bölüm ritmi
   (bölüm başına `padding`) önce gelir. "Bir şeyler ters" görünümünün çoğu yanlış renk değil yanlış ritimdir.
2. **Dikey ritim bir ölçektir, bölüm başına doğaçlama değerler değil.** Bir taban seçin (4 veya 8 px) ve
   yeniden kullanın. Referansı göz kararı yerine `sectune.py` ile ölçün (fidelity becerisine bakın).
3. **Bir yer tutucu/öne çıkan hücre taşıyorsa her ızgara hücresinin açık bir min-height'u olmalı**, yoksa
   ilk satır diğerlerinden daha yüksek render edilir.
4. **Satır içi çipler/rozetler `width: fit-content` kullanır.** Izgara hücresindeki `display:block` bir çip
   tam genişliğe yayılır ve tabloları renk duvarlarına dönüştürür.
5. **Maksimum genişlikli bir sarmalayıcı içindeki tam kanamalı bölümler**
   `width:100vw; margin-left:calc(50% - 50vw)` gerektirir — ve ardından `html{overflow-x:hidden}` kontrol edin, yoksa
   yatay kaydırma yaratırsınız.

## Tipografi

- Gövde 16 px / satır yüksekliği 24 px varsayılan taban.
- **Adlandırılmış ölçek** (h1/h2/body/body-sm ile boyut + kalınlık + satır yüksekliği), doğaçlama yazı boyutları değil.
- Boyut büyüdükçe harf aralığı daralır: 64 px'te `letter-spacing:-0.5px`, küçük büyük harflerde `+0.5px`.
- Görüntü başlıkları markanın kendi fontu varsa kendi font ailesini alır; gövde sans-serif'te kalır.

## Renk

- **Yalnızca anlamsal tokenlar**: `--bg`, `--bg-raised`, `--fg`, `--muted`, `--primary`, `--accent`.
  Bileşenler asla ham hex referansı vermez.
- Kontrastı gerçek sayılarla doğrulayın — `#0f0914` üzerinde `#fafafa` 18.81:1 (AAA); koyu zemin
  üzerinde pastel bir vurgu genellikle başarısız olan çifttir.
- Koyu yüzeyler **yükseltilmiş varyantlar** (`--bg-raised`) gerektirir, yoksa kartlar sayfaya karışır.

## Hareket

- Süreler bir ölçekten: 120/180/250/350 ms. Asla `transition: all 0.3s ease`.
- Yalnızca `transform` ve `opacity` animasyonu yapın.
- **`prefers-reduced-motion`'a saygı gösterin** — ve herhangi bir ekran görüntüsü karşılaştırmasının
  animasyonları kapatması gerektiğini unutmayın, yoksa aynı sayfanın iki çalıştırması farklı çıkar.

## Erişilebilirlik

- Her etkileşimli öğe gerçek bir `<a>` veya `<button>`'dır; ikonlar `aria-label` alır.
- JS div tıklama işleyicileri yerine `summary` tabanlı akordeonlar.
- Görünür bir yedek odak halkası olmadan asla `outline:none`.

## Kullanıcıya göstermeden önce doğrulama

1. 390 / 834 / 1440 px'te ekran görüntüsü.
2. Her genişlikte `document.documentElement.scrollWidth > clientWidth` kontrol edin — yatay kaydırma,
   mobil'i sessizce mahveden hatadır.
3. Referans varsa `pixdiff.py` çalıştırın ve sayıyı belirtin.
4. Ölçülmüş bir sonuç olmadan asla "tamam" demeyin.
