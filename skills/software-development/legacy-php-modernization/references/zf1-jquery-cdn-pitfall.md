# ZF1 cabinet: jQuery CDN pitfall and local-only fix

## Symptom

Browser console error:

```
Uncaught TypeError: $(...).on is not a function
    bindRequiredToggle https://my.ligalink.ru/assets/js/passport.js?v=3:41
    <anonymous> https://my.ligalink.ru/assets/js/passport.js?v=3:57
```

`jQuery.fn.jquery` reports a version, but `$('.passport-form').on` is missing.

## Root cause

`application/layouts/default.phtml` may enable ZendX JQuery with an SSL CDN:

```php
<?php echo $this->jQuery()->setCdnSsl(true)->uiEnable(); ?>
```

This causes ZendX to inject a second `<script>` tag pointing at `https://ajax.googleapis.com/ajax/libs/jquery/...`. The CDN copy loads after the local copy and overwrites `$`, replacing the local jQuery 1.11.0 (which has `.on()`) with an older CDN build that did not.

## Business constraint

The subscriber cabinet at `my.ligalink.ru` must work for users who have no general internet access. Resources under `ligalink.ru` and `liga-link.net` are considered local; everything else must be avoided.

## Fix

1. In `application/layouts/default.phtml`, replace the ZendX call with local paths:

```php
<?php echo $this->headScript()
    ->appendFile('/assets/js/jquery/jquery.min.js')
    ->appendFile('/assets/js/jquery/jquery.timeago.js')
    ->appendFile('/assets/js/jquery/jquery.timeago.ru.js')
?->

<?php echo $this->jQuery()
    ->setLocalPath('/assets/js/jquery/jquery.min.js')
    ->setUiLocalPath('/assets/js/jquery/jquery-ui.custom.min.js')
    ->uiEnable(); ?>
```

2. Remove the duplicate jQuery UI include from the bottom `headScript()` block:

```php
<?= $this->headScript()
    ->appendFile('/assets/bootstrap/js/bootstrap.min.js')
    ->appendFile('/assets/js/jquery/jquery.ui.datepicker-ru.js'); ?>
```

3. Bump the asset query string in any affected view template to defeat browser cache:

```html
<link rel="stylesheet" href="/assets/css/passport.css?v=3" />
<script src="/assets/js/passport.js?v=3"></script>
```

## Verification

- DevTools Network tab: no requests to `ajax.googleapis.com` after reload.
- Console: `jQuery.fn.jquery` matches the local version, and `typeof jQuery.fn.on === 'function'` is `true`.
- Re-test the page that previously threw the error.

## Related files in LigaLink ZF1 cabinet

- `application/layouts/default.phtml`
- `application/layouts/default.backup`
- `library/ZendX/JQuery.php` (defines CDN constants — do not edit; override in layout)
