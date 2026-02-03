# Translations

This project uses gettext catalogs stored under `openastro2/locale/`.
There are two scripts involved:

- `scripts/extract_translations.sh`: builds the `.pot` template from source code and settings.
- `scripts/update_translations.sh`: compiles `.po` files into `.mo` files.

## Extract `.pot`

Run:

```bash
openastro2/scripts/extract_translations.sh
```

What it does:

1. Extracts strings from Python sources using `_()` and `_t()`.
2. Extracts strings from the following settings files:
   - `openastro2/openastro2/settings/settings2.json`
   - `openastro2/openastro2/settings/settings2-tno.json`
3. Updates `openastro2/openastro2/locale/templates/openastro.pot`.

The settings extraction works by staging `_t("...")` calls in `.tmp/` and
then rewriting source paths in the `.pot` so they point back to the original
JSON files.

## Compile `.mo`

After updating translations, compile the catalogs:

```bash
openastro2/scripts/update_translations.sh
```

This will create or update `.mo` files under `openastro2/locale/<lang>/LC_MESSAGES/`.

