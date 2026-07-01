# Passport Form V2 — LigaLink ZF1 Cabinet (styled, optional email)

Updated recipe incorporating session fixes:
- Email is optional (not required)
- Improved CSS styling for the view template
- Client-side email validation only if field is non-empty

## Files

Same 4 files as v1 recipe:
1. `application/modules/billing/forms/Passport.php`
2. `application/modules/billing/views/scripts/index/passport.phtml`
3. `application/modules/billing/controllers/IndexController.php`
4. `application/layouts/_menu.phtml`

## Form class — email optional

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

        // Серия паспорта
        $this->addElement('text', 'passport_series', array(
            'label' => 'Серия паспорта *',
            'class' => 'form-control mb-3',
            'required' => true,
            'maxlength' => 4,
            'data-mask' => '0000',
            'filters' => array('StringTrim', 'StripTags'),
            'validators' => array(
                array('NotEmpty', true, array('messages' => array('isEmpty' => 'Укажите серию паспорта'))),
                array('Regex', true, array('pattern' => '/^\d{4}$/', 'messages' => array('regexNotMatch' => 'Серия должна содержать ровно 4 цифры'))),
            ),
        ));

        // Номер паспорта
        $this->addElement('text', 'passport_number', array(
            'label' => 'Номер паспорта *',
            'class' => 'form-control mb-3',
            'required' => true,
            'maxlength' => 6,
            'data-mask' => '000000',
            'filters' => array('StringTrim', 'StripTags'),
            'validators' => array(
                array('NotEmpty', true, array('messages' => array('isEmpty' => 'Укажите номер паспорта'))),
                array('Regex', true, array('pattern' => '/^\d{6}$/', 'messages' => array('regexNotMatch' => 'Номер должен содержать ровно 6 цифр'))),
            ),
        ));

        // Кем выдан
        $this->addElement('text', 'passport_issued_by', array(
            'label' => 'Кем выдан *',
            'class' => 'form-control mb-3',
            'required' => true,
            'filters' => array('StringTrim', 'StripTags'),
            'validators' => array(
                array('NotEmpty', true, array('messages' => array('isEmpty' => 'Укажите, кем выдан паспорт'))),
            ),
        ));

        // Дата выдачи
        $this->addElement('text', 'passport_date', array(
            'label' => 'Дата выдачи *',
            'class' => 'form-control mb-3 passport-date',
            'required' => true,
            'placeholder' => 'дд.мм.гггг',
            'data-mask' => '00.00.0000',
            'filters' => array('StringTrim', 'StripTags'),
            'validators' => array(
                array('NotEmpty', true, array('messages' => array('isEmpty' => 'Укажите дату выдачи паспорта'))),
                array('Regex', true, array('pattern' => '/^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.(19|20)\d{2}$/', 'messages' => array('regexNotMatch' => 'Дата должна быть в формате дд.мм.гггг'))),
            ),
        ));

        // Код подразделения
        $this->addElement('text', 'passport_code', array(
            'label' => 'Код подразделения *',
            'class' => 'form-control mb-3',
            'required' => true,
            'maxlength' => 7,
            'placeholder' => '000-000',
            'data-mask' => '000-000',
            'filters' => array('StringTrim', 'StripTags'),
            'validators' => array(
                array('NotEmpty', true, array('messages' => array('isEmpty' => 'Укажите код подразделения'))),
                array('Regex', true, array('pattern' => '/^\d{3}\-\d{3}$/', 'messages' => array('regexNotMatch' => 'Формат: 000-000'))),
            ),
        ));

        // Номер телефона
        $this->addElement('text', 'home_telephone', array(
            'label' => 'Номер телефона *',
            'class' => 'form-control mb-3',
            'required' => true,
            'filters' => array('StringTrim', 'StripTags'),
            'validators' => array(
                array('NotEmpty', true, array('messages' => array('isEmpty' => 'Укажите номер телефона'))),
            ),
        ));

        // Email — optional (was required in v1)
        $this->addElement('text', 'email', array(
            'label' => 'Email',
            'class' => 'form-control mb-3',
            'required' => false,
            'filters' => array('StringTrim', 'StripTags'),
            'validators' => array(
                'EmailAddress'
            ),
        ));

        // Кнопка отправки
        $this->addElement('button', 'send', array(
            'label' => 'Отправить',
            'class' => 'btn btn-primary btn-block',
            'type' => 'submit',
        ));

        // Декораторы для полей
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
            array('HtmlTag', array('tag' => 'div')),
            'Form',
        ));
    }
}
```

## Controller action

```php
private function _parsePassport($passport)
{
    $pattern = '/серия\s+(\d{4})\s+№(\d{6})\s+выдан\s+(.+?)\s+(\d{2}\.\d{2}\.\d{4})\s+(\d{3}-\d{3})/ui';
    if (preg_match($pattern, $passport, $m)) {
        return array(
            'series' => $m[1], 'number' => $m[2],
            'issued_by' => trim($m[3]), 'date' => $m[4], 'code' => $m[5],
        );
    }
    return null;
}

public function passportAction()
{
    $this->setTitle('Персональные данные');

    $userData = $this->cache->load($this->cache_basic_account);
    if ($userData === false) {
        $urfa = $this->reconnect();
        $userData = $urfa->getUserInfo();
        $this->cache->save($userData, $this->cache_basic_account);
        unset($urfa);
    }
    $this->view->userData = $userData; // required for _menu.phtml
    $this->view->user = $userData;

    $form = new Billing_Form_Passport();
    $this->view->form = $form;

    if ($this->getRequest()->isPost()) {
        $data = $this->getRequest()->getPost();
        if ($form->isValid($data)) {
            try {
                $series = $form->getValue('passport_series');
                $number = $form->getValue('passport_number');
                $issued = $form->getValue('passport_issued_by');
                $date = $form->getValue('passport_date');
                $code = $form->getValue('passport_code');

                $account = $userData['basic_account'];
                $body = "серия $series №$number выдан $issued $date $code";

                $mail = new Zend_Mail('utf-8');
                $mail->setSubject("Паспортные данные абонента ($account)")
                     ->setBodyText($body)
                     ->addTo('info@ligalink.ru')
                     ->send();

                $this->cache->remove($this->cache_basic_account);
                $this->_helper->flashMessenger->addMessage(array('success' => 'Ваши паспортные данные отправлены оператору.'));
                $this->_redirect('/user/passport');
            } catch (Exception $e) {
                $this->view->error = 'Ошибка при отправке данных: ' . $e->getMessage();
            }
        } else {
            $this->view->error = 'Пожалуйста, исправьте ошибки в форме.';
        }
    }
}
```

## View template (styled, with inline CSS and JS masks)

```php
<?php
$existing = isset($this->user['passport']) ? $this->user['passport'] : '';
$parsed = array('series'=>'', 'number'=>'', 'issued_by'=>'', 'date'=>'', 'code'=>'');
if (!empty($existing) && preg_match('/серия\s+(\d{4})\s+№(\d{6})\s+выдан\s+(.+?)\s+(\d{2}\.\d{2}\.\d{4})\s+(\d{3}-\d{3})/ui', $existing, $m)) {
    $parsed['series'] = $m[1]; $parsed['number'] = $m[2];
    $parsed['issued_by'] = $m[3]; $parsed['date'] = $m[4]; $parsed['code'] = $m[5];
}

function maskField($val, $visibleLen) {
    $vis = substr($val, 0, min($visibleLen, strlen($val)));
    $masked = str_repeat('*', max(0, strlen($val) - $visibleLen));
    return $vis . $masked;
}
?>
<style>
.passport-page h2 { margin-bottom: 24px; font-size: 22px; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
.passport-card { background: #fff; border: 1px solid #e1e8ed; border-radius: 6px; padding: 24px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.passport-card h4 { margin-top: 0; margin-bottom: 18px; font-size: 16px; color: #34495e; font-weight: 600; }
.passport-info { background: #f4f8fb; border-left: 4px solid #3498db; padding: 16px 18px; margin-bottom: 24px; border-radius: 0 4px 4px 0; }
.passport-info p { margin: 6px 0; font-size: 14px; color: #2c3e50; }
.passport-info strong { display: inline-block; width: 170px; color: #555; font-weight: 500; }
.passport-form .form-group { margin-bottom: 20px; }
.passport-form label { display: block; font-weight: 600; font-size: 13px; margin-bottom: 7px; color: #34495e; }
.passport-form .req { color: #e74c3c; }
.passport-form .form-control { border: 1px solid #ccd6de; border-radius: 4px; padding: 10px 12px; font-size: 14px; transition: border-color 0.15s, box-shadow 0.15s; }
.passport-form .form-control:focus { border-color: #3498db; box-shadow: 0 0 0 3px rgba(52,152,219,0.12); outline: none; }
.passport-form .form-control::placeholder { color: #aab7c4; }
.passport-form .form-row { display: flex; gap: 16px; flex-wrap: wrap; }
.passport-form .form-row .form-group { flex: 1 1 220px; margin-bottom: 0; }
.passport-form .btn-submit { background: #3498db; color: #fff; border: none; padding: 12px 28px; font-size: 15px; border-radius: 4px; cursor: pointer; transition: background 0.15s; }
.passport-form .btn-submit:hover, .passport-form .btn-submit:focus { background: #2980b9; }
.passport-form .field-hint { font-size: 12px; color: #95a5a6; margin-top: 5px; }
.alert-custom { padding: 14px 18px; border-radius: 4px; margin-bottom: 20px; font-size: 14px; }
.alert-custom.warning { background: #fdf6e3; border-left: 4px solid #f39c12; color: #7d5c0a; }
@media (max-width: 600px) {
  .passport-form .form-row { display: block; }
  .passport-info strong { width: auto; display: block; margin-bottom: 2px; }
}
</style>

<div class="passport-page">
  <h2>Персональные данные</h2>

  <div class="passport-info">
    <p><strong>Абонент:</strong> <?= htmlspecialchars($this->user['full_name'] ?? '') ?></p>
    <p><strong>Лицевой счёт:</strong> <?= htmlspecialchars($this->user['basic_account'] ?? '') ?></p>
  </div>

  <?php if (!empty($parsed['series'])): ?>
  <div class="passport-card">
    <h4>Текущие паспортные данные (маскированные)</h4>
    <div class="passport-info" style="margin-bottom:0;">
      <p><strong>Серия:</strong> <?= maskField($parsed['series'], 2) ?></p>
      <p><strong>Номер:</strong> <?= maskField($parsed['number'], 2) ?></p>
      <p><strong>Кем выдан:</strong> <?= htmlspecialchars($parsed['issued_by']) ?></p>
      <p><strong>Дата выдачи:</strong> <?= maskField(substr($parsed['date'], 0, 2), 0) .'.'. maskField(substr($parsed['date'], 3, 2), 0) .'.'. substr($parsed['date'], 6, 4) ?></p>
      <p><strong>Код подразделения:</strong> <?= maskField($parsed['code'], 0) ?></p>
    </div>
  </div>
  <?php else: ?>
  <div class="alert-custom warning">
    <strong>Внимание!</strong> Паспортные данные отсутствуют. Заполните форму ниже.
  </div>
  <?php endif; ?>

  <?php if (isset($this->error)): ?>
    <?= $this->bootAlert(array('error'=>$this->error)); ?>
  <?php endif; ?>

  <div class="passport-card">
    <h4>Укажите или актуализируйте данные</h4>
    <?= $this->form; ?>
  </div>
</div>

<script type="text/javascript">
jQuery(document).ready(function($) {
    function bindMask(selector, maxLen, fmtFunc) {
        $(document).on('input', selector, function() {
            var raw = this.value.replace(/\D/g, '').slice(0, maxLen);
            this.value = fmtFunc ? fmtFunc(raw) : raw;
        });
    }
    bindMask('input[data-mask="0000"]', 4);
    bindMask('input[data-mask="000000"]', 6);
    bindMask('input[data-mask="00.00.0000"]', 8, function(v) {
        var f = ''; for (var i = 0; i < v.length; i++) { if (i === 2 || i === 4) f += '.'; f += v[i]; }
        return f;
    });
    bindMask('input[data-mask="000-000"]', 6, function(v) {
        var f = ''; for (var i = 0; i < v.length; i++) { if (i === 3) f += '-'; f += v[i]; }
        return f;
    });

    $('.passport-form').on('submit', function(e) {
        var ok = true; var errs = [];
        var s = $('[name="passport_series"]').val().replace(/\D/g,'');
        var n = $('[name="passport_number"]').val().replace(/\D/g,'');
        var d = $('[name="passport_date"]').val().trim();
        var c = $('[name="passport_code"]').val().replace(/\D/g,'');
        var p = $('[name="home_telephone"]').val().trim();
        var em = $('[name="email"]').val().trim();

        if (s.length !== 4) { ok = false; errs.push('серия (4 цифры)'); }
        if (n.length !== 6) { ok = false; errs.push('номер (6 цифр)'); }
        if (!/^\d{2}\.\d{2}\.\d{4}$/.test(d)) { ok = false; errs.push('дата выдачи'); }
        if (c.length !== 6) { ok = false; errs.push('код подразделения'); }
        if (p.length < 3) { ok = false; errs.push('телефон'); }
        if (em.length > 0 && em.indexOf('@') === -1) { ok = false; errs.push('email (или оставьте пустым)'); }

        if (!ok) {
            e.preventDefault();
            alert('Проверьте поля: ' + errs.join(', ') + '. Форма не очищена — продолжайте редактирование.');
            return false;
        }
    });
});
</script>
```

## Menu link

```html
<li><a href="/user/passport">Персональные данные</a></li>
```

## Key changes from v1

1. Email `required => false`, no `NotEmpty` validator. Label has no `*`.
2. Client validation skips email check when empty; only validates format if provided.
3. View includes inline `<style>` for cards, form-row layouts, focus effects, and mobile adaptability.
4. JS masks are pure inline jQuery (no external CDN dependency).
5. Errors collected into an array and shown in a single alert (prevents alert fatigue).

## Verified against production source (2026-06-10)

Checked against the live `my.ligalink.ru` codebase. Key differences from earlier recipe assumptions:

| Detail | Recipe assumption | Actual code |
|---|---|---|
| **Phone field name** | `home_telephone` | `phone` (form), populated from `home_telephone` or `mobile_telephone` from billing |
| **Birthday field** | Missing | Present in form and view (required, `дд.мм.гггг` format) |
| **Controller cache** | Loads `userData` from cache | Calls `reconnect()` + `getUserInfo()` directly every request |
| **Default population** | N/A | Passport fields (series/number/issued_by/date/code) are **commented out** — only phone and email are pre-filled |
| **View masking** | `maskField(val, visibleLen)` only | `maskField(val, visibleLen, direction)` with `'begin'` (default) or `'end'` |
| **Form decorators** | Simple loop over all elements | Per-element decorators: `ViewHelper`, `Errors`, `Label`, `HtmlTag('div', 'form-group')` for inputs; `ViewHelper` + `HtmlTag('div', 'form-group mt-4')` for submit button |
| **mail->setFrom()** | Missing or from user email | `setFrom('cabinet@ligalink.ru', 'LigaLink Cabinet')` |
| **mail->addTo()** | `'info@ligalink.ru'` | `'info@ligalink.ru', 'Info LigaLink'` |

### Production `maskField()` implementation
```php
function maskField($val, $visibleLen, $direction = 'begin') {
    $len = strlen($val);
    if ($visibleLen <= 0) return str_repeat('*', $len);
    if ($visibleLen >= $len) return $val;
    $masked = str_repeat('*', $len - $visibleLen);
    if ($direction === 'end') return $masked . substr($val, -$visibleLen);
    return substr($val, 0, $visibleLen) . $masked;
}
```
Usage in view:
- Series: `maskField($parsed['series'], 2)` → `45****`
- Number: `maskField($parsed['number'], 2, 'end')` → `****78`
- Date: individual day/month masked, year shown
- Code: fully masked `maskField($parsed['code'], 0)` → `******`

### Production decorator pattern
```php
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
```

### Production email pattern
```php
$mail = new Zend_Mail('utf-8');
$mail->setBodyText($messageBody);
$mail->setFrom('cabinet@ligalink.ru', 'LigaLink Cabinet');
$mail->addTo('info@ligalink.ru', 'Info LigaLink');
$mail->setSubject('Паспортные данные абонента ' . $account);
$mail->send();
```
