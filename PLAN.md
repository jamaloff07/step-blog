# Dərs 14 — REST, JSON və ilk serializer

> **Canlı kodu yazarkən `ADDIMLAR.pdf`-ə bax** — orada hər addımda hansı faylda hansı sətirləri yazacağın
> yaşıl rənglə göstərilib, terminal çıxışları və xəta mətnləri real yoxlanılıb. Bu fayl isə dərsin qısa xəritəsidir.
> **Bu dərsin xüsusiyyəti:** DRF blokunun ilk günü. Yenilik: **API** (HTML əvəzinə JSON). uv artıq Dərs 7-dən tanışdır —
> bu gün yalnız `uv add djangorestframework` (bir slayd xatırlatma).
> **HTML sayta toxunulmur** — hər şey yeni `api/` app-ına yazılır. Model və migration dəyişmir.
> **Qızıl qayda:** hər API view-u yazanda `blog/views.py`-dakı HTML əkizini göstər — “iki dəfə yaz”.

> **Arxa monitor üçün.** Bu qovluq dərsin SONUNDAKI tam layihədir.
> Kodda nişanlar: `[DƏRS 14]` = sən yazırsan · `[PRAKTİKA 14]` = tələbə yazır · `[EV 14]` = ev tapşırığı.
> I hissədə `[DƏRS 14]`: `rest_framework` + `api` app, `PostSerializer`, `post_list` (GET+POST), `post_detail` (GET/PUT/DELETE).
> **Praktika = 1 tapşırıq:** `CategorySerializer` + `category_list`. **Praktikadan sonra sən yazırsan:** `category_detail` (`[DƏRS 14] praktikadan sonra`).
> Teq API-si + `/api/stats/` → ev tapşırığıdır, dərsdə YAZMA.

**Dərsin sonunda:** `/api/posts/`, `/api/posts/<id>/`, `/api/categories/`, `/api/categories/<id>/` tam CRUD-dur. Postman-da `step-blog` collection-ı var.

Migration tarixçəsi: **dəyişmir** (son: `0013_post_likes`). DRF blokunda yeni migration yoxdur.

## Bu layihəni işə salmaq (uv)
```bash
cd project/django/lesson-14
uv sync                               # .venv + bütün paketlər uv.lock-dan (bir dəfəlik, activate lazım deyil)
./seed.sh                             # TƏK KOMANDA: db.sqlite3 sil → migrate → loaddata demo_full → admin / step12345 hazır
                                      # demo_full = 4 user (parol: step12345) + 9 post + 5 teq + 7 şərh
uv run manage.py runserver            # → http://127.0.0.1:8000/api/posts/
uv run manage.py test                 # yalnız sənin üçün: HTML (15) + API (8) = 23 test
```
Tələbə klonlayanda eyni: `uv sync` → `uv run manage.py migrate` → `loaddata demo` → `runserver`.

---

## Vaxt planı

| Vaxt | Nə | Slayd | ADDIMLAR |
|---|---|---|---|
| 0:00–0:10 | 5 sual + ev tapşırığına baxış. Problem: mobil tətbiq (HTML yox, məlumat). Plan | 1–4 | 2 |
| 0:10–0:22 | API/REST/JSON (restoran, HTML vs JSON, JSON tipləri, REST cədvəli, status kodları). **CANLI:** `JsonResponse` demosu + TypeError | 5–10, 12 | 3 |
| 0:22–0:27 | **Mikro 1:** REST forması + status kodu | 11 | 4 |
| 0:27–0:37 | **CANLI:** `uv add djangorestframework` (xatırlatma), `startapp api`, INSTALLED_APPS, `config/urls.py`, boş `api/urls.py` | 13–15 | 5 |
| 0:37–0:45 | **CANLI:** `PostSerializer` + shell demosu (`.data`, `many=True` xətası) | 16–17 | 6 |
| 0:45–0:50 | **Mikro 2:** `FilmSerializer` | 18 | 7 |
| 0:50–1:02 | **CANLI:** `post_list` GET → Browsable API, `?format=json`; INSTALLED_APPS demosu; `post_detail` GET + 404 | 19–22 | 8–9 |
| 1:02–1:08 | **CANLI:** Postman — GET sorğuları, collection | 27–28 | 10 |
| 1:08–1:24 | **CANLI:** POST (`is_valid` → `save` → 201 / 400), Postman POST; PUT + DELETE; 405 demosu | 23–25, 29 | 11–12 |
| 1:24–1:30 | **Mikro 3:** 3 səhvi tap. Xətalar cədvəli | 26, 30 | 13–14 |
| 1:30–1:40 | **Fasilə** | | |
| 1:40–2:20 | **PRAKTİKA — 1 tapşırıq:** `CategorySerializer` + `category_list`; 20-ci dəqiqədə checkpoint, sonda Postman-da birlikdə | 31–33 | 15 |
| 2:20–2:40 | **“İNDİ MƏN YAZIRAM”:** `category_detail` — sən canlı yazırsan, tələbə baxır / yanaşı yazır | 34 | 16 |
| 2:40–3:00 | Push, yekun, ev tapşırığı vərəqi (3 tapşırıq, ~25 dəq), Dərs 15 anonsu | 35 | 17–18 |

---

## Dərsdən əvvəl (5 dəq)
Bir gün əvvəl tələbələrə: **Postman yükləyin**. Dərsin əvvəlində:
```bash
git clone <repo> && cd step-blog        # və ya git pull
uv sync
uv run manage.py runserver              # Dərs 13-ün saytı açılır
```
De: “Bu gün saytın ikinci üzünü yazırıq — JSON. Sayta toxunmuruq.”

---

## CANLI KOD — addım-addım

### Addım 1 — motivasiya (0:00)
`/post/1/` aç → Ctrl+U → HTML. **De:** “Telefon tətbiqinə bu lazımdırmı? Yox — məlumat lazımdır. Eyni blog, ikinci üz: JSON.”

### Addım 2 — API/REST/JSON + JsonResponse demosu (0:10)
Slaydlar 6–10 tez. Slayd 12: `blog/views.py`-a müvəqqəti `post_json` (4 sahə əl ilə) + URL → `/post/1/json/` işləyir.
⚠ `JsonResponse({"post": post})` → `TypeError: Object of type Post is not JSON serializable`. **De:** “Tərcüməçi lazımdır — serializer.” Demo bitəndə **sil**.

**Mikro 1 (5 dəq, slayd 11):** `GET /api/films/` 200 · `DELETE /api/films/3/` 204 · 201 · 400 (`year`) · 404.

### Addım 3 — DRF + api app (0:27)
`uv add djangorestframework` (slayd 14 — “Dərs 7: paket lazımdır → uv add”, 30 saniyə) → `uv run manage.py startapp api` →
settings `'rest_framework'`, `'api'` → `config/urls.py` `path('api/', include('api.urls'))` → boş `api/urls.py` (`app_name = "api"`, `urlpatterns = []`).
**De:** “Niyə ayrı app? HTML sayt `blog`-da qalır, toxunmuruq. Modellər bir yerdə — `from blog.models import Post`.”

### Addım 4 — PostSerializer (0:37)
`api/serializers.py`: `class Meta: model, fields, read_only_fields`. `blog/forms.py` → `PostForm` ilə yan-yana göstər: eyni qəlib.
Shell: `PostSerializer(post).data` → dict; `many=True` → list. ⚠ many-siz → `'QuerySet' object has no attribute 'title'`.
Diqqət: `author: 1`, `tags: [1]` — id-lər (Dərs 15-də adlar), `created_at` string.

**Mikro 2 (5 dəq, slayd 18):** `FilmSerializer`, `read_only_fields = ["rating", "created_at"]`; 5 film → `many=True`; `"iki min"` → 400 `year`.

### Addım 5 — post_list GET + post_detail GET (0:50)
`@api_view(["GET"])` + `Response(serializer.data)` → `api/urls.py`. Brauzerdə `/api/posts/` → Browsable API, `?format=json`.
⚠ **Demo:** settings-dən `'rest_framework'`-ü şərhə al → `TemplateDoesNotExist: rest_framework/api.html`. Geri qaytar.
`post_detail` + `get_object_or_404` → `/api/posts/999/` → `{"detail":"No Post matches the given query."}`.
**De:** “`PostListView`: obyektləri götür — eynidir. Orada template + context, burada serializer + Response.”

### Addım 6 — Postman GET (1:02)
New → HTTP → GET `http://127.0.0.1:8000/api/posts/` → Send. Status, vaxt, body. Save → collection `step-blog`.
⚠ `Could not get response` → runserver işləmir.

### Addım 7 — POST, PUT, DELETE (1:08)
`@api_view(["GET", "POST"])`, `PostSerializer(data=request.data)` → `is_valid()` → `save()` → `201`; errors → `400`.
**De:** “Dərs 11: form(request.POST) → is_valid → save → redirect. Eyni 4 addım. `request.data` = `request.POST`-un API variantı.”
Postman: Body → raw → JSON → 201; `{"title": "x"}` → 400 `Bu sahə tələb edilir`. Brauzerdə `/post/10/` — sayt da görür.
⚠ **Demo:** `is_valid()`-siz `save()` → `AssertionError: You must call .is_valid() before calling .save().`
`post_detail` → `["GET", "PUT", "DELETE"]`: `PostSerializer(post, data=request.data)` (instance + data), `post.delete()` → 204.
⚠ **Göstər:** PATCH → 405 `"PATCH" yöntəminə icazə verilmir.` — “kod yazmadıq, `@api_view` siyahıya baxır.”
**De:** “`author: 1` — tətbiq kimin adından istəsə yaza bilər. Dərs 11-dəki vəziyyət. Dərs 16-da token gələcək.”

**Mikro 3 (5 dəq, slayd 26):** many=True yoxdur · is_valid-dən əvvəl save · `@api_view(["GET"])` → POST 405 · gizli: 201 yox, 200.

---

## PRAKTİKA — 1 tapşırıq (1:40–2:20)

| Nə | Tapşırıq | Checkpoint (Postman-da yoxla) |
|---|---|---|
| Praktika (~40 dəq) | `CategorySerializer` (id, name, slug, description) · `category_list` GET+POST · `path("categories/", ...)` · collection · commit | 20-ci dəq: `GET /api/categories/` kimdə açılır? Sonda: POST `{"name":"İdman","slug":"idman"}` → 201 · POST `{"name":"x"}` → 400 slug |

**Qaydan:** yeni heç nə izah etmə. “`post_list`-i kopyala, `Post` → `Category`, importları yenilə.”
Tez bitirənə: Postman-da POST-u `description` ilə göndər; ev tapşırığının 1-ci bəndi (Tag). `category_detail`-i **özü yazmasın** — birlikdə yazacaqsınız.

## “İNDİ MƏN YAZIRAM” — category_detail (2:20–2:40)
Hamı ekrana baxır. `post_detail`-in əkizini canlı yaz (`[DƏRS 14] praktikadan sonra`): `@api_view(["GET", "PUT", "DELETE"])`, `get_object_or_404`,
PUT → `CategorySerializer(category, data=request.data)`, DELETE → 204. URL: `path("categories/<int:category_id>/", ...)`.
Postman-da birlikdə: `/api/categories/1/` 200 · `/99/` 404 · PUT → 200 · DELETE boş (praktikada yaradılan “İdman”) → 204.
⚠ **Göstər:** `DELETE /api/categories/1/` (postları var) → 500 `ProtectedError` — “Dərs 10, `on_delete=PROTECT`, baza özünü qoruyur — düzgündür.”
**De:** “Eyni qəlibi bu gün 3 dəfə gördünüz. Evdə teq üçün 4-cü dəfə özünüz — kopyala, adı dəyiş, 25 dəqiqə.”

### Tez-tez çıxan xətalar (praktikada)
| Xəta | Səbəb |
|---|---|
| `NameError: name 'Category' is not defined` | `from blog.models import Post, Category` yenilənməyib |
| `NameError: name 'CategorySerializer' is not defined` | `views.py`-da serializer importu |
| `'QuerySet' object has no attribute 'name'` | `many=True` unudulub |
| POST → 405 | `@api_view(["GET"])` — POST siyahıda yoxdur |
| POST → 400 slug, amma göndərilib | Postman-da Body form-data/Text — raw → JSON seç |
| `AssertionError: You must call .is_valid()` | sıra səhvdir |
| `ModuleNotFoundError: No module named 'rest_framework'` | `python manage.py` ilə işlədilir — `uv run manage.py` |

---

## Növbəti dərsə körpü
**De:** “Bu gün postlar üçün 2 funksiya — 35 sətir. Kateqoriya üçün yenə 35. Evdə teq üçün yenə 35.”
Soruş: “Dərs 13-də eyni problemi necə həll etmişdik?” → hazır class, yalnız fərqi yaz.
→ Dərs 15: **ViewSet + Router** — 35 sətir → 3 sətir, URL-ləri Router özü düzəldir. Post JSON-unun içində şərhlər — **nested serializer**.
