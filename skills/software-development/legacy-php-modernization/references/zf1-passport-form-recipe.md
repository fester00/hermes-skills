# Passport Form Recipe — LigaLink ZF1 Cabinet

Complete recipe for adding a passport-data form to `my.ligalink.ru/user/passport`.

## Overview

Page at `/user/passport` that:
- Displays current passport data from UTM5 (masked, e.g. `серия 45** №77****`)
- Lets user input corrected values via form with jQuery input masks
- Sends the update as an email to the operator (since URFA `userEdit()` does not accept passport changes)
- Preserves form values on server-side validation errors

## Files involved

1. `application/modules/billing/forms/Passport.php`
2. `application/modules/billing/views/scripts/index/passport.phtml`
3. `application/modules/billing/controllers/IndexController.php`
4. `application/layouts/_menu.phtml`

## 1. Form class

```php
class Billing_Form_Passport extends Zend_Form
{
    public function __construct()
    {
        $this->setName('passport');
        parent::__construct();

        $this->addElement('text', 'passport_series', array(
            'label' => 'Серия',
            'class' => 'form-control mb-3',
            'required' => true,
            'validators' => array(
                'NotEmpty',
                array('Regex', false, array('pattern' => '/^\d{4}$/'))
            ),
        ));

        $this->addElement('text', 'passport_number', array(
            'label' => 'Номер',
            'class' => 'form-control mb-3',
            'required' => true,
            'validators' => array(
                'NotEmpty',
                array('Regex', false, array('pattern' => '/^\d{6}$/'))
            ),
        ));

        $this->addElement('text', 'passport_issued_by', array(
            'label' => 'Кем выдан',
            'class' => 'form-control mb-3',
            'required' => true,
            'validators' => array('NotEmpty'),
        ));

        $this->addElement('text', 'passport_date', array(
            'label' => 'Дата выдачи',
            'class' => 'form-control mb-3',
            'required' => true,
            'validators' => array(
                'NotEmpty',
                array('Regex', false, array('pattern' => '/^\d{2}\.\d{2}\.\d{4}$/'))
            ),
        ));

        $this->addElement('text', 'passport_code', array(
            'label' => 'Код подразделения',
            'class' => 'form-control mb-3',
            'required' => true,
            'validators' => array(
                'NotEmpty',
                array('Regex', false, array('pattern' => '/^\d{3}-\d{3}$/'))
            ),
        ));

        $this->addElement('text', 'home_telephone', array(
            'label' => 'Контактный телефон',
            'class' => 'form-control mb-3',
            'required' => true,
            'validators' => array(
                'NotEmpty',
            ),
        ));

        $this->addElement('text', 'email', array(
            'label' => 'Email',
            'class' => 'form-control mb-3',
            'required' => true,
            'validators' => array(
                'NotEmpty',
                'EmailAddress',
            ),
        ));

        $this->addElement('button', 'send', array(
            'label' => 'Отправить',
            'class' => 'btn btn-primary btn-block',
            'type' => 'submit',
        ));

        $this->addElement('button', 'edit', array(
            'label' => 'Редактировать',
            'class' => 'btn btn-secondary btn-block',
            'type' => 'button',
        ));
    }
}
```

## 2. Controller action

Insert into `IndexController.php` after an existing action, with correct closing brace balance.

```php
private function _parsePassport($passport)
{
    $pattern = '/серия\s+(\d{4})\s+№(\d{6})\s+выдан\s+(.+?)\s+(\d{2}\.\d{2}\.\d{4})\s+(\d{3}-\d{3})/ui';
    if (preg_match($pattern, $passport, $matches)) {
        return array(
            'series' => $matches[1],
            'number' => $matches[2],
            'issued_by' => trim($matches[3]),
            'issue_date' => $matches[4],
            'code' => $matches[5],
        );
    }
    return null;
}

public function passportAction()
{
    $this->setTitle('Персональные данные');
    $this->view->headScript()->appendFile('https://code.jquery.com/jquery-3.7.1.min.js');

    $userData = $this->cache->load($this->cache_basic_account);
    if ($userData === false) {
        $urfa = $this->reconnect();
        $userData = $urfa->getUserInfo();
        $this->cache->save($userData, $this->cache_basic_account);
        unset($urfa);
    }
    $this->view->userData = $userData; // needed for _menu.phtml compatibility

    $form = new Billing_Form_Passport();
    $this->view->form = $form;

    if ($this->getRequest()->isPost()) {
        if ($form->isValid($this->getRequest()->getPost())) {
            try {
                $mail = new Zend_Mail('utf-8');
                $mail->setSubject('Паспортные данные абонента (' . $this->view->userData['account'] . ')');
                $body = 'серия ' . $form->getValue('passport_series')
                    . ' №' . $form->getValue('passport_number')
                    . ' выдан ' . $form->getValue('passport_issued_by')
                    . ' ' . $form->getValue('passport_date')
                    . ' ' . $form->getValue('passport_code');
                $mail->setBodyText($body);
                $mail->addTo('info@ligalink.ru');
                $mail->setFrom($form->getValue('email'));
                $mail->send();

                $this->_helper->flashMessenger->addMessage(
                    array('success' => 'Ваши данные отправлены оператору.')
                );
                $this->_redirect('/user/passport');
            } catch (Exception $e) {
                $this->_helper->flashMessenger->addMessage(
                    array('danger' => 'Ошибка при отправке данных: ' . $e->getMessage())
                );
            }
        }
        // On validation failure, fall through to re-render the view.
        // The phtml template reads getValue() to keep inputs filled.
    }
}
```

*Brace-balance verification*: after insertion run `php -l IndexController.php` or count braces (`grep -c '{'` vs `grep -c '}'`).

## 3. View template (passport.phtml)

```php
<?php $user = $this->userData; $form = $this->form; ?>

<div class="row">
    <div class="col-md-8 col-md-offset-2">
        <h3 class="text-center">Персональные данные</h3>

        <?php if (isset($user['passport']) && !empty($user['passport'])): ?>
            <?php $p = $user['passport']; 
                  $pattern = '/серия\s+(\d{4})\s+№(\d{6})\s+выдан\s+(.+?)\s+(\d{2}\.\d{2}\.\d{4})\s+(\d{3}-\d{3})/ui';
                  if (preg_match($pattern, $p, $m)): ?>
                <div class="alert alert-info" id="currentData"><strong>Текущие паспортные данные:</strong><br>
                серия <?= substr($m[1], 0, 2) . '**' ?> №<?= substr($m[2], 0, 2) . '****' ?> выдан <?= $m[3] ?> **.**.
                <?= substr($m[4], 6, 4) ?> ***-***</div>
            <?php else: ?>
                <div class="alert alert-warning" id="currentData">Паспортные данные отсутствуют или имеют неизвестный формат.</div>
            <?php endif; ?>
        <?php else: ?>
            <div class="alert alert-warning" id="currentData">Паспортные данные отсутствуют.</div>
        <?php endif; ?>

        <form method="post" action="/user/passport" id="passportForm">
            <table border="0" width="40%">
                <tr>
                    <td>&emsp;</td>
                    <td><h3>Контактные данные</h3></td>
                </tr>
                <tr>
                    <td>&emsp;</td>
                    <td><?= $form->getElement('home_telephone')->renderLabel() ?></td>
                </tr>
                <tr>
                    <td>&emsp;</td>
                    <td><input type="text" class="form-control mb-3" name="home_telephone" value="<?= htmlspecialchars($form->getValue('home_telephone')) ?>" data-mask="__/__/____" data-mask-placeholder="_" placeholder="Введите ваш телефон" /></td>
                </tr>
                <tr>
                    <td>&emsp;</td>
                    <td><?= $form->getElement('email')->renderLabel() ?></td>
                </tr>
                <tr>
                    <td>&emsp;</td>
                    <td><input type="text" class="form-control mb-3" name="email" value="<?= htmlspecialchars($form->getValue('email')) ?>" placeholder="Введите ваш email" required /></td>
                </tr>
                <tr>
                    <td>&emsp;</td>
                    <td><h3>Паспорт</h3></td>
                </tr>
                <tr>
                    <td>&emsp;</td>
                    <td><?= $form->getElement('passport_series')->renderLabel() ?></td>
                </tr>
                <tr>
                    <td>&emsp;</td>
                    <td><input type="text" class="form-control mb-3" name="passport_series" value="<?= htmlspecialchars($form->getValue('passport_series')) ?>" data-mask="0000" data-mask-placeholder="0" required /></td>
                </tr>
                <tr>
                    <td>&emsp;</td>
                    <td><?= $form->getElement('passport_number')->renderLabel() ?></td>
                </tr>
                <tr>
                    <td>&emsp;</td>
                    <td><input type="text" class="form-control mb-3" name="passport_number" value="<?= htmlspecialchars($form->getValue('passport_number')) ?>" data-mask="000000" data-mask-placeholder="0" required /></td>
                </tr>
                <tr>
                    <td>&emsp;</td>
                    <td><?= $form->getElement('passport_issued_by')->renderLabel() ?></td>
                </tr>
                <tr>
                    <td>&emsp;</td>
                    <td><input type="text" class="form-control mb-3" name="passport_issued_by" value="<?= htmlspecialchars($form->getValue('passport_issued_by')) ?>" required /></td>
                </tr>
                <tr>
                    <td>&emsp;</td>
                    <td><?= $form->getElement('passport_date')->renderLabel() ?></td>
                </tr>
                <tr>
                    <td>&emsp;</td>
                    <td><input type="text" class="form-control mb-3" name="passport_date" value="<?= htmlspecialchars($form->getValue('passport_date')) ?>" data-mask="00.00.0000" data-mask-placeholder="0" required /></td>
                </tr>
                <tr>
                    <td>&emsp;</td>
                    <td><?= $form->getElement('passport_code')->renderLabel() ?></td>
                </tr>
                <tr>
                    <td>&emsp;</td>
                    <td><input type="text" class="form-control mb-3" name="passport_code" value="<?= htmlspecialchars($form->getValue('passport_code')) ?>" data-mask="000-000" data-mask-placeholder="0" required /></td>
                </tr>
                <tr>
                    <td>&emsp;</td>
                    <td>
                        <button type="submit" class="btn btn-primary btn-block mb-3" id="sendButton">Отправить</button>
                        <button type="button" class="btn btn-secondary btn-block" id="editButton">Редактировать</button>
                    </td>
                </tr>
            </table>
        </form>
    </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery.maskedinput/1.4.1/jquery.maskedinput.min.js"></script>
<script>
$(function() {
    $('[data-mask]').each(function() {
        var mask = $(this).data('mask');
        $(this).inputmask(mask, { placeholder: $(this).data('mask-placeholder') });
    });

    $('#passportForm').on('submit', function(e) {
        e.preventDefault();
        var valid = true;
        $('#passportForm [required]').each(function() {
            if (!$(this).val() || $(this).val().length < $(this).attr('data-mask').replace(/[^0A]/g, '').length) {
                $(this).addClass('is-invalid');
                valid = false;
            } else {
                $(this).removeClass('is-invalid');
            }
        });
        if (!valid) {
            alert('Заполните все обязательные поля.');
            return false;
        }
        this.submit();
    });

    $('#editButton').on('click', function() {
        var form = $('#passportForm');
        var btn = $(this);
        if (form.find(':input:not(button)').first().prop('disabled')) {
            form.find(':input:not(button)').prop('disabled', false).not('[data-mask]').each(function() {
                if ($(this).data('mask')) {
                    $(this).inputmask('remove');
                    $(this).inputmask($(this).data('mask'), { placeholder: $(this).data('mask-placeholder') });
                }
            });
            btn.text('Отменить редактирование');
        } else {
            form.find(':input:not(button)').prop('disabled', true);
            btn.text('Редактировать');
        }
    });
});
</script>
```

## 4. Menu link

In `application/layouts/_menu.phtml` add inside the `<ul>`:

```html
<li><a href="/user/passport">Персональные данные</a></li>
```

## Known pitfalls

- **userEdit() does NOT update passport** — `userEdit()` in `library/Urfa/Client.php` sends `$user['passport']` from cached `getUserInfo()`, not the new value. Use email as the only viable user-side option.
- **brace balance** — after pasting into `IndexController.php`, always verify `{` and `}` counts match (`grep -c '{'` / `grep -c '}'`).
- **userData compatibility** — `_menu.phtml` uses `$this->userData`. Always set `$this->view->userData = $userData` in every action, or menu/nav renders empty.
- **jQuery availability** — input-mask CDN link used as external dependency; if server blocks external CDN, inline-mask snippet or local file preferred.
- **mail transport** — `Zend_Mail` defaults to sendmail. If email silently fails, check `application.ini` for a configured SMTP transport.

## Mask reference

| Field | mask | placeholder |
|-------|------|-------------|
| Серия | `0000` | `0` |
| Номер | `000000` | `0` |
| Дата | `00.00.0000` | `0` |
| Код | `000-000` | `0` |
| Телефон | `__/__/____` or `+7 (___) ___-__-__` | `_` |
