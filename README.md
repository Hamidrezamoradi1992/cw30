````md
# CW - پیاده‌سازی Serializerهای ماژول Archive

## هدف

در این تمرین باید Repository پروژه را دریافت کرده، پروژه را اجرا کنید و سپس تمامی Serializerهای مورد نیاز ماژول Archive را بر اساس Modelها و ViewSetهای موجود پیاده‌سازی نمایید.

---

## راه‌اندازی پروژه

1. Repository را Clone کنید.
2. محیط مجازی (Virtual Environment) ایجاد و فعال کنید.
3. وابستگی‌ها را نصب کنید.
4. Database را تنظیم کنید.
5. Migrationها را اجرا کنید:

```bash
python manage.py makemigrations
python manage.py migrate
```

6. یک SuperUser ایجاد کنید:

```bash
python manage.py createsuperuser
```

7. سرور را اجرا کنید:

```bash
python manage.py runserver
```

---

## توضیح پروژه

سیستم Archive برای مدیریت فایل‌های سازمانی طراحی شده است.

### فرمت‌های مجاز فایل

- PDF
- DOC / DOCX
- XLS / XLSX
- PPT / PPTX
- TXT
- JPG / JPEG / PNG
- ZIP / RAR / 7Z

### حداکثر فضای ذخیره‌سازی

- 100GB

### حداکثر حجم هر فایل

مطابق محدودیت‌های تعریف‌شده در تنظیمات پروژه.

---

## Modelهای موجود

در پروژه Modelهای زیر از قبل پیاده‌سازی شده‌اند.

### Category

#### فیلدها

- owner_user
- name

### File

#### فیلدها

- owner_user
- category
- owner
- name
- label
- file
- size
- uploaded_at
- file_format

#### قابلیت‌های موجود

- اعتبارسنجی فرمت فایل
- محاسبه حجم فایل
- کنترل فضای ذخیره‌سازی
- گزارش مصرف Storage

### FileDownloadLog

#### فیلدها

- owner_user
- file
- user_id
- downloaded_at
- action

#### عملیات‌های قابل ثبت

- download
- delete

---

## Serializerهای مورد نیاز

باید Serializerهای زیر را پیاده‌سازی کنید.

### Category

- CategorySetSerializers
- CategorySetResponseSerializer
- CategoryListResponseSerializers
- CategoryDestroySerializer
- CategoryDestroyResponseSerializer

#### نیازمندی‌ها

- جلوگیری از ثبت دسته‌بندی تکراری
- اعتبارسنجی نام دسته‌بندی
- امکان حذف دسته‌بندی
- خروجی مناسب برای لیست دسته‌بندی‌ها

### File

- FileCreateSerializer
- FileResponseSerializers
- FileDownloadSerializer
- FileDownloadResponseSerializer
- FileDestroySerializer
- FileDestroyResponseSerializer

#### نیازمندی‌ها

- اعتبارسنجی Category
- اعتبارسنجی Label
- ثبت Owner
- ثبت Owner User
- ثبت فرمت فایل
- ثبت حجم فایل
- ثبت عملیات Download
- ثبت عملیات Delete

### User

- BaseUserInfoSerializer

#### نیازمندی‌ها

- نمایش fullname کاربر
- از User پایه Django استفاده شده است.

### Storage

- WordSerializers
- ExcelSerializers
- PdfSerializers
- OtherTypeSerializers
- FileDietaileResponseSerializer

#### نیازمندی‌ها

- نمایش حجم کل Storage
- نمایش فضای آزاد
- نمایش حجم فایل‌های Word
- نمایش حجم فایل‌های Excel
- نمایش حجم فایل‌های PDF
- نمایش سایر فایل‌ها
- نمایش رنگ هر بخش برای نمودار مصرف

---

## نکات مهم

### 1. بررسی و اصلاح Modelها

علاوه بر پیاده‌سازی Serializerها، در صورتی که هنگام بررسی پروژه متوجه هرگونه ایراد منطقی، ساختاری، Type Error، Validation Error، Query Error یا مشکل در Modelها شدید، موظف هستید آن‌ها را اصلاح کنید.

مواردی که باید بررسی شوند:

- ForeignKeyها و Related Nameها
- نوع فیلدها
- Validationها
- متدهای Save
- متدهای محاسباتی
- Queryهای مربوط به Storage
- لاگ‌های Download و Delete
- ناسازگاری بین Model و Serializer
- ناسازگاری بین View و Serializer

> هدف این تسک صرفاً پیاده‌سازی Serializerها نیست؛ خروجی نهایی باید بدون خطا اجرا شود.

---

### 2. استفاده از ساختار مدیریت خطای پروژه

در تمامی Serializerها و Validationها باید از ساختار مدیریت خطای تعریف‌شده در پروژه استفاده شود.

برای مدیریت خطاها حتماً از موارد زیر استفاده کنید:

- `CustomValidationException`
- فایل `messages.py`

نمونه:

```python
raise CustomValidationException(
    {"detail": Messages.category_invalid}
)
```

یا:

```python
raise CustomValidationException(
    {"detail": Messages.file_does_not_exists}
)
```

---

### 3. عدم Hard Code کردن پیام‌ها

استفاده مستقیم از متن خطا یا پیام موفقیت در Serializerها مجاز نیست.

تمامی پیام‌ها باید از فایل `messages.py` خوانده شوند.

❌ نمونه غیرمجاز:

```python
raise CustomValidationException(
    {"detail": "Category Not Found"}
)
```

```python
raise serializers.ValidationError(
    "File is invalid"
)
```

✅ نمونه صحیح:

```python
raise CustomValidationException(
    {"detail": Messages.category_invalid}
)
```

---

### 4. سازگاری کامل با ViewSetها

Serializerهای پیاده‌سازی‌شده باید کاملاً با ViewSetهای موجود سازگار باشند.

در صورت نیاز به تغییرات جزئی در Model یا View جهت رفع خطاهای موجود پروژه، اعمال تغییرات مجاز است؛ اما ساختار و Contract خروجی APIها نباید تغییر کند.

---

## APIهای قابل تست

پس از پیاده‌سازی Serializerها باید APIهای زیر بدون خطا کار کنند:

- add_category_archive
- list_category_archive
- destroy_category_archive
- add_file_archive
- download_file_archive
- destroy_file_archive
- detail_storage

---

## خروجی مورد انتظار

- تمامی Serializerها پیاده‌سازی شوند.
- Validationها مطابق نیازمندی‌ها انجام شوند.
- تمامی Errorها از طریق `CustomValidationException` مدیریت شوند.
- تمامی پیام‌ها از فایل `messages.py` خوانده شوند.
- Response Structure با ViewSetهای موجود سازگار باشد.
- کدها مطابق استاندارد Django REST Framework نوشته شوند.
- در صورت وجود ایراد در Modelها، اصلاح شوند.
- پروژه بدون خطا اجرا شود.
- تمامی APIهای تعریف‌شده به‌درستی پاسخ دهند.
````
