# Passport Form V4 — LigaLink ZF1 Cabinet (display-group layout, Bootstrap-safe CSS)

Final compact single-form design used in production June 2026. Writes directly to UTM5 via `rpcf_edit_user_new` (admin API).

## Why another version

V3 used a custom `render()` override to group fields into rows. V4 replaces that with native `Zend_Form_DisplayGroup`, which is simpler and survives layout changes. V4 also fixes two production issues discovered during deploy:

1. `$this->headLink()->appendStylesheet()` / `$this->inlineScript()->appendFile()` did not output anything in this cabinet's layout, so CSS/JS never loaded on the live page.
2. Bootstrap 2.x global styles overrode `display: flex` on `.form-row`.

## Files

1. `application/modules/billing/forms/Passport.php`
2. `application/modules/billing/views/scripts/index/passport.phtml`
3. `application/modules/billing/controllers/IndexController.php`
4. `www/assets/css/passport.css`
5. `www/assets/js/passport.js`

## Key design decisions

- Single form, no separate read-only view.
- `passport_serial_number` combines series and number, mask `0000 000000`, backend regex `/^\d{4}\s\d{6}$/`.
- Address split into `reg_index` + `reg_city` (one row) and `reg_address` (street/house/apt, full width).
- Address fields are **conditionally required**: if `passport_registration_address` is missing in UTM5, `reg_address`, `reg_index`, and `reg_city` all become required on both backend and frontend.
- Stored in UTM5 additional param `passport_registration_address` as `индекс, населённый пункт, улица/дом/квартира`.: if `passport_registration_address` is missing in UTM5, `reg_address`, `reg_index`, and `reg_city` all become required on both backend and frontend.
- Stored in UTM5 additional param `passport_registration_address` as `индекс, населённый пункт, улица/дом/квартира`.
- Passport string format unchanged for backward compatibility: `серия 0000 №000000 выдан ... дд.мм.гггг 000-000`.
- Phone required, email optional.
- Placeholders set once in the controller via `$element->setAttrib('placeholder')`; no duplicate JS placeholder logic.

## Form class

```php
class Billing_Form_Passport extends Zend_Form
{
    public function __construct()
    {
        $this->setName('form_passport');
        $this->setMethod('post');
        $this->setAttrib('class', 'passport-form well');
        $this->setAttrib('novalidate', 'novalidate');
        parent::__construct();

        // Серия и номер паспорта
        $this->addElement('text', 'passport_series_number', array(
            'label' => 'Серия и номер паспорта',
            'class' => 'form-control',
            'required' => false,
            'maxlength' => 11,
            'data-mask' => '0000 000000',
            'placeholder' => '1234 123456',
            'filters' => array('StringTrim', 'StripTags'),
            'validators' => array(
                array('Regex', true, array('pattern' => '/^\d{4}\s\d{6}$/', 'messages' => array('regexNotMatch' => 'Формат: 1234 123456'))),
            ),
        ));

        // Дата выдачи
        $this->addElement('text', 'passport_date', array(
            'label' => 'Дата выдачи',
            'class' => 'form-control passport-date',
            'required' => false,
            'placeholder' => 'ДД.ММ.ГГГГ',
            'data-mask' => '00.00.0000',
            'filters' => array('StringTrim', 'StripTags'),
            'validators' => array(
                array('Regex', true, array('pattern' => '/^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.(19|20)\d{2}$/', 'messages' => array('regexNotMatch' => 'Дата должна быть в формате дд.мм.гггг'))),
            ),
        ));

        // Группа: серия/номер + дата выдачи
        $this->addDisplayGroup(array('passport_series_number', 'passport_date'), 'passportMainGroup');
        $this->getDisplayGroup('passportMainGroup')
            ->clearDecorators()
            ->addDecorator('FormElements')
            ->addDecorator('HtmlTag', array('tag' => 'div', 'class' => 'form-row'));

        // Кем выдан
        $this->addElement('text', 'passport_issued_by', array(
            'label' => 'Кем выдан',
            'class' => 'form-control mb-3',
            'required' => false,
            'placeholder' => 'Название подразделения',
            'filters' => array('StringTrim', 'StripTags'),
        ));

        // Код подразделения
        $this->addElement('text', 'passport_code', array(
            'label' => 'Код подразделения',
            'class' => 'form-control mb-3',
            'required' => false,
            'maxlength' => 7,
            'placeholder' => '000-000',
            'data-mask' => '000-000',
            'filters' => array('StringTrim', 'StripTags'),
            'validators' => array(
                array('Regex', true, array('pattern' => '/^\d{3}\-\d{3}$/', 'messages' => array('regexNotMatch' => 'Формат: 000-000'))),
            ),
        ));

        // Дата рождения
        $this->addElement('text', 'birthday', array(
            'label' => 'Дата рождения',
            'class' => 'form-control mb-3 birthday',
            'required' => false,
            'placeholder' => 'ДД.ММ.ГГГГ',
            'data-mask' => '00.00.0000',
            'filters' => array('StringTrim', 'StripTags'),
            'validators' => array(
                array('NotEmpty', true, array('messages' => array('isEmpty' => 'Укажите дату рождения'))),
                array('Regex', true, array('pattern' => '/^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.(19|20)\d{2}$/', 'messages' => array('regexNotMatch' => 'Дата должна быть в формате дд.мм.гггг'))),
            ),
        ));

        // Улица, дом, квартира (метка оставлена общей "Адрес регистрации", placeholder уточняет формат)
        $this->addElement('text', 'reg_address', array(
            'label' => 'Адрес регистрации',
            'class' => 'form-control span12',
            'required' => false,
            'rows' => 1,
            'placeholder' => 'Улица, дом, квартира',
            'filters' => array('StringTrim', 'StripTags'),
        ));

        // Почтовый индекс
        $this->addElement('text', 'reg_index', array(
            'label' => 'Почтовый индекс',
            'class' => 'form-control',
            'required' => false,
            'maxlength' => 6,
            'data-mask' => '000000',
            'placeholder' => '123456',
            'filters' => array('StringTrim', 'StripTags'),
            'validators' => array(
                array('Regex', true, array('pattern' => '/^\d{6}$/', 'messages' => array('regexNotMatch' => 'Индекс должен содержать 6 цифр'))),
            ),
        ));

        // Населённый пункт
        $this->addElement('text', 'reg_city', array(
            'label' => 'Населённый пункт',
            'class' => 'form-control',
            'required' => false,
            'filters' => array('StringTrim', 'StripTags'),
        ));

        // Группа: индекс + город
        $this->addDisplayGroup(array('reg_index', 'reg_city'), 'regLocationGroup');
        $this->getDisplayGroup('regLocationGroup')
            ->clearDecorators()
            ->addDecorator('FormElements')
            ->addDecorator('HtmlTag', array('tag' => 'div', 'class' => 'form-row'));

        // Номер телефона
        $this->addElement('text', 'phone', array(
            'label' => 'Номер телефона',
            'class' => 'form-control mb-3',
            'required' => false,
            'placeholder' => '+7 999 999 99 99',
            'data-mask' => '+7 000 000 00 00',
            'filters' => array('StringTrim', 'StripTags'),
            'validators' => array(
                array('NotEmpty', true, array('messages' => array('isEmpty' => 'Укажите номер телефона'))),
                array('Regex', true, array('pattern' => '/^\+7\s\d{3}\s\d{3}\s\d{2}\s\d{2}$/', 'messages' => array('regexNotMatch' => 'Формат: +7 999 999 99 99'))),
            ),
        ));

        // Email
        $this->addElement('text', 'email', array(
            'label' => 'Email',
            'class' => 'form-control mb-3',
            'required' => false,
            'filters' => array('StringTrim', 'StripTags'),
            'validators' => array('EmailAddress'),
        ));

        // Кнопка отправки
        $this->addElement('button', 'send', array(
            'label' => 'Отправить',
            'class' => 'btn btn-primary btn-block',
            'type' => 'submit',
        ));

        // Декораторы полей
        foreach ($this->getElements() as $element) {
            if ($element->getName() != 'send') {
                $element->setDecorators(array(
                    'ViewHelper',
                    'Errors',
                    'Label',
                    array('HtmlTag', array('tag' => 'div', 'class' => 'form-group')),
                ));
            } else {
                $element->setDecorators(array(
                    'ViewHelper',
                    array('HtmlTag', array('tag' => 'div', 'class' => 'form-group mt-4')),
                ));
            }
        }

        // Декоратор формы
        $this->setDecorators(array(
            'FormElements',
            array('HtmlTag', array('tag' => 'div', 'class' => 'row-fluid')),
            'Form',
        ));
    }
}
```

## View template

```php
<?php
$this->headLink()->appendStylesheet('/assets/css/passport.css');
$this->inlineScript()->appendFile('/assets/js/passport.js');
?>

<!-- headLink/inlineScript do NOT output in this cabinet layout unless default.phtml
     explicitly echoes $this->inlineScript() / $this->headLink(). Until the layout
     is confirmed to do so, include assets directly in the view as a robust fallback. -->
<link rel="stylesheet" href="/assets/css/passport.css?v=2" type="text/css" media="screen" />
<script type="text/javascript" src="/assets/js/passport.js?v=2"></script>

<?php
$existing = isset($this->userInfo['passport']) ? $this->userInfo['passport'] : '';
$parsed = array('series' => '', 'number' => '', 'issued_by' => '', 'date' => '', 'code' => '');
if (!empty($existing) && preg_match('/серия\s+(\d{4})\s+№(\d{6})\s+выдан\s+(.+?)\s+(\d{2}\.\d{2}\.\d{4})\s+(\d{3}-\d{3})/ui', $existing, $m)) {
    $parsed['series'] = $m[1];
    $parsed['number'] = $m[2];
    $parsed['issued_by'] = $m[3];
    $parsed['date'] = $m[4];
    $parsed['code'] = $m[5];
}
?>

<div class="passport-page">
    <div class="passport-card">
        <?= $this->form ?>
    </div>
</div>

<?= $this->cacheInfo($this->cacheData) ?>

<script type="text/javascript">
    var hasPassportInUtm5 = <?= json_encode(!empty($parsed['series'])) ?>;
    var hasBirthdayInUtm5 = <?= json_encode(!empty($this->additionalParams['user_birthdate'])) ?>;
    var hasRegAddressInUtm5 = <?= json_encode(!empty($this->additionalParams['passport_registration_address'])) ?>;
</script>
```

## Controller essentials

```php
// Parse existing passport
$existing = array();
if (!empty($userInfo['passport'])) {
    $existing = $this->_parsePassport($userInfo['passport']);
}

if ($this->getRequest()->isPost()) {
    $post = $this->getRequest()->getPost();
    $hasPassport = !empty($existing['series']);

    if (!$hasPassport) {
        $form->getElement('passport_series_number')->addValidator('NotEmpty', true, array('messages' => array('isEmpty' => 'Укажите серию и номер паспорта')));
        $form->getElement('passport_issued_by')->addValidator('NotEmpty', true, array('messages' => array('isEmpty' => 'Укажите, кем выдан паспорт')));
        $form->getElement('passport_date')->addValidator('NotEmpty', true, array('messages' => array('isEmpty' => 'Укажите дату выдачи паспорта')));
        $form->getElement('passport_code')->addValidator('NotEmpty', true, array('messages' => array('isEmpty' => 'Укажите код подразделения')));
    }

    $hasRegAddress = !empty($additionalParams['passport_registration_address']);
    if (!$hasRegAddress) {
        $form->getElement('reg_address')->addValidator('NotEmpty', true, array('messages' => array('isEmpty' => 'Укажите улицу, дом и квартиру')));
        $form->getElement('reg_index')->addValidator('NotEmpty', true, array('messages' => array('isEmpty' => 'Укажите почтовый индекс')));
        $form->getElement('reg_city')->addValidator('NotEmpty', true, array('messages' => array('isEmpty' => 'Укажите населённый пункт')));
    }

    if ($form->isValid($post)) {
        // Split combined field
        $seriesNumber = $form->getValue('passport_series_number');
        $series = $number = '';
        if (preg_match('/^(\d{4})\s(\d{6})$/', $seriesNumber, $m)) {
            $series = $m[1];
            $number = $m[2];
        }

        // Fallback to existing passport data if already present and left empty
        $issued = $form->getValue('passport_issued_by') ?: $existing['issued_by'];
        $date   = $form->getValue('passport_date')       ?: $existing['date'];
        $code   = $form->getValue('passport_code')       ?: $existing['code'];
        if ($hasPassport && empty($series)) $series = $existing['series'];
        if ($hasPassport && empty($number)) $number = $existing['number'];

        $passport = 'серия ' . $series . ' №' . $number
            . ' выдан ' . $issued . ' ' . $date . ' ' . $code;

        // Assemble address
        $regAddressParts = array();
        $regIndex  = trim($form->getValue('reg_index'));
        $regCity   = trim($form->getValue('reg_city'));
        $regStreet = trim($form->getValue('reg_address'));
        if ($regIndex)  $regAddressParts[] = $regIndex;
        if ($regCity)   $regAddressParts[] = $regCity;
        if ($regStreet) $regAddressParts[] = $regStreet;
        $regAddress = implode(', ', $regAddressParts);

        // Keep old address if nothing entered and one exists
        if (!empty($additionalParams['passport_registration_address']) && empty($regAddress)) {
            $regAddress = $additionalParams['passport_registration_address'];
        }

        $saveResult = $this->_savePassportData(
            $userInfo,
            array(
                'series'    => $series,
                'number'    => $number,
                'issued_by' => $issued,
                'date'      => $date,
                'code'      => $code,
                'passport_str' => $passport,
            ),
            array(
                'phone'       => $form->getValue('phone'),
                'email'       => $form->getValue('email'),
                'birthday'    => $form->getValue('birthday'),
                'reg_address' => $regAddress,
            )
        );

        if ($saveResult) {
            $this->cache->remove($userInfoCacheKey);
            $this->cache->remove($additionalParamsCacheKey);
            $this->_helper->flashMessenger->addMessage(array('success' => 'Данные успешно сохранены.'));
        } else {
            $this->_helper->flashMessenger->addMessage(array('error' => 'Не удалось сохранить данные. Попробуйте позже.'));
        }

        $this->redirect('/user/passport');
    }
} else {
    // Placeholders only — values are not pre-filled for security
    $defaults = array();
    if (!empty($existing['series']) && !empty($existing['number'])) {
        $form->getElement('passport_series_number')
            ->setAttrib('placeholder', $this->_helper->masker->maskFromBegin($existing['series'], 2) . ' ' . $this->_helper->masker->maskFromEnd($existing['number'], 2));
    }
    if (!empty($existing['issued_by'])) {
        $form->getElement('passport_issued_by')
            ->setAttrib('placeholder', $this->_helper->masker->maskInbetween($existing['issued_by'], 4, 4));
    }
    if (!empty($existing['date'])) {
        $form->getElement('passport_date')
            ->setAttrib('placeholder', $this->_helper->masker->maskFromEnd($existing['date'], 4));
    }
    if (!empty($existing['code'])) {
        $form->getElement('passport_code')
            ->setAttrib('placeholder', $this->_helper->masker->maskFromEnd($existing['code'], 3));
    }
    if (!empty($additionalParams['user_birthdate'])) {
        $form->getElement('birthday')
            ->setAttrib('placeholder', $this->_helper->masker->maskFromEnd($additionalParams['user_birthdate'], 4));
    }
    if (!empty($additionalParams['passport_registration_address'])) {
        $regAddress = $additionalParams['passport_registration_address'];
        if (preg_match('/^(\d{6})[,\s]+([^,]+)[,\s]+(.+)$/u', $regAddress, $m)) {
            $form->getElement('reg_index')->setAttrib('placeholder', $this->_helper->masker->maskFromBegin($m[1], 2));
            $form->getElement('reg_city')->setAttrib('placeholder', $this->_helper->masker->maskInbetween($m[2], 3, 3));
            $form->getElement('reg_address')->setAttrib('placeholder', $this->_helper->masker->maskInbetween($m[3], 4, 4));
        } else {
            $form->getElement('reg_address')->setAttrib('placeholder', $this->_helper->masker->maskInbetween($regAddress, 4, 4));
        }
    }
    if (!empty($userInfo['mobile_telephone'])) {
        $defaults['phone'] = $userInfo['mobile_telephone'];
    } elseif (!empty($userInfo['home_telephone'])) {
        $defaults['phone'] = $userInfo['home_telephone'];
    }
    if (!empty($userInfo['email'])) {
        $defaults['email'] = $userInfo['email'];
    }
    $form->setDefaults($defaults);
}
```

## CSS

```css
.passport-page h2 {
    margin-bottom: 24px;
    font-size: 22px;
    color: #2c3e50;
    border-bottom: 2px solid #3498db;
    padding-bottom: 10px;
}

.passport-card {
    background: #fff;
    border: 1px solid #e1e8ed;
    border-radius: 6px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.passport-form .form-group {
    margin-bottom: 20px;
}

/* Must beat Bootstrap 2.x overrides */
.passport-form .form-row,
.passport-form .row-fluid .form-row {
    display: flex !important;
    gap: 16px;
    flex-wrap: wrap;
    margin-bottom: 20px;
}

.passport-form .form-row .form-group,
.passport-form .row-fluid .form-row .form-group {
    flex: 1 1 0 !important;
    min-width: 160px;
    margin-bottom: 0 !important;
}

.passport-form .form-row .form-group .form-control,
.passport-form .row-fluid .form-row .form-group .form-control {
    width: 100% !important;
    box-sizing: border-box;
}

.passport-form label {
    display: block;
    font-weight: 600;
    font-size: 13px;
    margin-bottom: 7px;
    color: #34495e;
}

.passport-form .form-control {
    border: 1px solid #ccd6de;
    border-radius: 4px;
    padding: 10px 12px;
    font-size: 14px;
    width: 100%;
    box-sizing: border-box;
}

.passport-form .form-control:focus {
    border-color: #3498db;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.12);
    outline: none;
}

.passport-form .form-control::placeholder {
    color: #aab7c4;
}

.passport-form .btn-submit {
    background: #3498db;
    color: #fff;
    border: none;
    padding: 12px 28px;
    font-size: 15px;
    border-radius: 4px;
    cursor: pointer;
    transition: background 0.15s;
}

.passport-form .btn-submit:hover,
.passport-form .btn-submit:focus {
    background: #2980b9;
}

.alert-custom {
    padding: 14px 18px;
    border-radius: 4px;
    margin-bottom: 20px;
    font-size: 14px;
}

.alert-custom.warning {
    background: #fdf6e3;
    border-left: 4px solid #f39c12;
    color: #7d5c0a;
}

@media (max-width: 600px) {
    .passport-form .form-row {
        display: block;
    }
    .passport-form .form-row .form-group {
        margin-bottom: 20px;
    }
}
```

## JS

```javascript
jQuery(document).ready(function ($) {
    function bindMask(selector, maxLen, fmtFunc) {
        $(document).on('input', selector, function () {
            var raw = this.value.replace(/\D/g, '').slice(0, maxLen);
            this.value = fmtFunc ? fmtFunc(raw) : raw;
        });
    }

    bindMask('input[data-mask="0000 000000"]', 10, function (v) {
        var s = v.slice(0, 4);
        var n = v.slice(4);
        return s + (n ? ' ' + n : '');
    });

    bindMask('input[data-mask="000000"]', 6);
    bindMask('input[data-mask="00.00.0000"]', 8, function (v) {
        var f = '';
        for (var i = 0; i < v.length; i++) {
            if (i === 2 || i === 4) f += '.';
            f += v[i];
        }
        return f;
    });
    bindMask('input[data-mask="000-000"]', 6, function (v) {
        var f = '';
        for (var i = 0; i < v.length; i++) {
            if (i === 3) f += '-';
            f += v[i];
        }
        return f;
    });

    $(document).on('input', 'input[data-mask="+7 000 000 00 00"]', function () {
        var raw = this.value.replace(/\D/g, '').replace(/^7/, '').slice(0, 10);
        var f = '+7';
        if (raw.length > 0) f += ' ' + raw.substr(0, 3);
        if (raw.length > 3) f += ' ' + raw.substr(3, 3);
        if (raw.length > 6) f += ' ' + raw.substr(6, 2);
        if (raw.length > 8) f += ' ' + raw.substr(8, 2);
        this.value = f;
    });

    $('.passport-form').on('submit', function (e) {
        var ok = true;
        var errs = [];
        var seriesNumber = $('[name="passport_series_number"]').val().replace(/\D/g, '');
        var date = $('[name="passport_date"]').val().trim();
        var code = $('[name="passport_code"]').val().replace(/\D/g, '');
        var phone = $('[name="phone"]').val().trim();
        var birthday = $('[name="birthday"]').val().trim();
        var email = $('[name="email"]').val().trim();
        var regIndex = $('[name="reg_index"]').val().replace(/\D/g, '');

        if (!hasPassportInUtm5) {
            if (seriesNumber.length !== 10) { ok = false; errs.push('серия и номер паспорта (10 цифр)'); }
            if (!/^\d{2}\.\d{2}\.\d{4}$/.test(date)) { ok = false; errs.push('дата выдачи'); }
            if (code.length !== 6) { ok = false; errs.push('код подразделения'); }
        }

        if (!hasBirthdayInUtm5) {
            if (!/^\d{2}\.\d{2}\.\d{4}$/.test(birthday)) { ok = false; errs.push('дата рождения'); }
        }

        if (!/^\+7\s\d{3}\s\d{3}\s\d{2}\s\d{2}$/.test(phone)) {
            ok = false; errs.push('номер телефона (формат +7 999 999 99 99)');
        }
        if (email.length > 0 && email.indexOf('@') === -1) {
            ok = false; errs.push('email (или оставьте пустым)');
        }
        if (regIndex.length > 0 && regIndex.length !== 6) {
            ok = false; errs.push('почтовый индекс (6 цифр)');
        if (regIndex.length > 0 && regIndex.length !== 6) { ok = false; errs.push('почтовый индекс (6 цифр)'); }

        if (!hasRegAddressInUtm5) {
            var regCity = $('[name="reg_city"]').val().trim();
            var regAddress = $('[name="reg_address"]').val().trim();
            if (regAddress.length < 3) { ok = false; errs.push('адрес регистрации (улица, дом, квартира)'); }
            if (regCity.length < 2) { ok = false; errs.push('населённый пункт'); }
            if (regIndex.length !== 6) { ok = false; errs.push('почтовый индекс (6 цифр)'); }
        }

        if (!ok) {
            e.preventDefault();
            alert('Пожалуйста, проверьте поля: ' + errs.join(', ') + '. Форма не очищена — продолжайте редактирование.');
            return false;
        }
    });
});
```

## Git workflow for this project

The canonical remote is **`git.liga-link.net/git/lk.git`**. A local commit is **not** the end of the task.

Required sequence:

1. `git pull origin master` before editing.
2. `git add -A && git commit -m "..."`
3. **`git push origin master`** — mandatory. The user may then deploy to the production host themselves.

**Common mistake:** stopping after `git commit`. Always push, then confirm the push succeeded.

## Production deploy notes

- `git push` is not enough. The server does not auto-pull. The user deploys PHP files and static assets to the production host themselves (e.g., VS Code SFTP `Sync Local to Remote` or a server-side `git pull`).
- If only CSS/JS are deployed but PHP files are not, the page renders a confusing mixed form (new static assets, old template/fields).
- If the layout is later updated to echo `$this->headLink()` / `$this->inlineScript()` in `<head>`, the direct `<link>/<script>` tags in the view can be removed; until then, keep them as a fallback.

## Pitfalls learned
## Pitfalls learned

1. `$this->headLink()` / `$this->inlineScript()` may not render in a custom ZF1 layout. Include `<link>` and `<script>` directly in the phtml.
2. Bootstrap 2.x can override `display: flex`. Use `!important` and parent-qualified selectors.
3. Do not duplicate placeholder logic in JS when the controller already sets them via `setAttrib('placeholder')`.
4. `rpcf_edit_user_new` needs the full profile first to avoid overwriting unrelated additional params.
5. Array merge order matters: `$newParams + $existingParams` keeps left-side values.
6. Cache keys for additional params must be consistent across `indexAction` and `passportAction`.
7. **Never load jQuery from CDN in the cabinet.** If `.on()` or other jQuery methods disappear after deploy, check whether `setCdnSsl(true)` loaded an older jQuery from Google. See `references/zf1-jquery-cdn-pitfall.md`.

## Optional: consent checkbox for PDn

Add before the submit button:

```php
$this->addElement('checkbox', 'pd_consent', array(
    'label' => 'Я согласен на обработку персональных данных и ознакомлен с политикой конфиденциальности',
    'class' => 'form-check-input',
    'required' => false,
    'value' => '1',
    'uncheckedValue' => '',
    'validators' => array(
        array('NotEmpty', true, array('messages' => array('isEmpty' => 'Необходимо согласие на обработку персональных данных'))),
    ),
));

$this->addElement('button', 'send', array(
    'label' => 'Отправить',
    'class' => 'btn btn-primary btn-block',
    'type' => 'submit',
    'disabled' => 'disabled',
));
```

Decorator:

```php
$element->setDecorators(array(
    'ViewHelper',
    'Errors',
    array('Label', array('placement' => 'APPEND', 'class' => 'form-check-label')),
    array('HtmlTag', array('tag' => 'div', 'class' => 'form-group form-check pd-consent-group')),
));
```

JS (enable submit only when checked):

```javascript
var $consent = $('[name="pd_consent"]');
var $submitBtn = $('.passport-form button[type="submit"]');

function updateConsentState() {
    var checked = $consent.is(':checked');
    var $group = $consent.closest('.pd-consent-group');
    if (checked) {
        $consent.removeClass('is-required');
        $group.find('.required-hint').remove();
        $submitBtn.prop('disabled', false);
    } else {
        $consent.addClass('is-required');
        if (!$group.find('.required-hint').length) {
            $group.append('<div class="field-hint required-hint">Обязательно к заполнению</div>');
        }
        $submitBtn.prop('disabled', true);
    }
}

$consent.on('change', updateConsentState);
updateConsentState();
```

Server-side:

```php
$pdConsent = $form->getValue('pd_consent');
if (empty($pdConsent)) {
    $form->getElement('pd_consent')->markAsError();
    $form->getElement('pd_consent')->addError('Необходимо согласие на обработку персональных данных');
    $this->view->error = 'Для сохранения данных необходимо согласие на обработку персональных данных.';
} else {
    // ... save to UTM5 ...
}
```
