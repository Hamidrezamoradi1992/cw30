from django.utils.translation import gettext_lazy as _


class Messages:
    name_missing = _("name is missing")
    # national_id_invalid=_("national id is invalid")

    information_correct = _('The entered information is correct')
    information_fault = _('The information provided is incomplete.')

    image_falt_size = _('The file size must not exceed')

    category_missing = _('Category ID is missing')
    category_invalid = _('Category is invalid')
    category_already_exists = _("Category already exists")

    file_does_not_exists = _("File does not exists")
    file_unsupported_formats = _("Unsupported file format")
    file_allowed_formats = _("Allowed formats are")
    label_missing = _('Label is missing')

    missing_argument = "Enter the complete information."
