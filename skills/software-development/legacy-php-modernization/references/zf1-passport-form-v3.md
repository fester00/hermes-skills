# Passport Form V3 — LigaLink ZF1 Cabinet (compact, single-form, UTM5 write)

Updated recipe for the final compact single-form design that writes directly to UTM5 via `rpcf_edit_user_new` (admin API).

## Files

1. `application/modules/billing/forms/Passport.php`
2. `application/modules/billing/views/scripts/index/passport.phtml`
3. `application/modules/billing/controllers/IndexController.php`
4. `library/Urfa/Admin.php`
5. `www/assets/css/passport.css`
6. `www/assets/js/passport.js`

## Key design decisions

- Single form (no separate "current data" view + edit form).
- Series and number are combined into one input `passport_serial_number` and formatted by JS as `0000 000000`.
- Address is split into three inputs: `reg_street`, `reg_city`, `reg_zip`.
- Stored in UTM5 additional parameter `passport_registration_address` as: `индекс, населённый пункт, улица/дом/квартира`.
- Passport string format kept unchanged so existing masked display works: `серия 0000 №000000 выдан ... дд.мм.гггг 000-000`.
- Phone is required; email is optional.

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
        $this->addElement('text', 'passport_serial_number', array(
            'label' => 'Серия и номер паспорта',
            'class' => 'form-control',
            'required' => false,
            'maxlength' => 11,
            'placeholder' => '0000 000000',
            'data-mask' => '0000 000000',
            'filters' => array('StringTrim', 'StripTags'),
            'validators' => array(
                array('Regex', true, array('pattern' => '/^\d{4}\s\d{6}$/', 'messages' => array('regexNotMatch' => 'Формат: 0000 000000'))),
            ),
        ));

        // Кем выдан
        $this->addElement('text', 'passport_issued_by', array(
            'label' => 'Кем выдан',
            'class' => 'form-control',
            'required' => false,
            'placeholder' => 'Отделение МВД России по ...',
            'filters' => array('StringTrim', 'StripTags'),
        ));

        // Дата выдачи
        $this->addElement('text', 'passport_date', array(
            'label' => 'Дата выдачи',
            'class' => 'form-control',
            'required' => false,
            'placeholder' => 'дд.мм.гггг',
            'data-mask' => '00.00.0000',
            'filters' => array('StringTrim', 'StripTags'),
            'validators' => array(
                array('Regex', true, array('pattern' => '/^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.(19|20)\d{2}$/', 'messages' => array('regexNotMatch' => 'Дата должна быть в формате дд.мм.гггг'))),
            ),
        ));

        // Код подразделения
        $this->addElement('text', 'passport_code', array(
            'label' => 'Код подразделения',
            'class' => 'form-control',
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
            'class' => 'form-control',
            'required' => true,
            'placeholder' => 'дд.мм.гггг',
            'data-mask' => '00.00.0000',
            'filters' => array('StringTrim', 'StripTags'),
            'validators' => array(
                array('NotEmpty', true, array('messages' => array('isEmpty' => 'Укажите дату рождения'))),
                array('Regex', true, array('pattern' => '/^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.(19|20)\d{2}$/', 'messages' => array('regexNotMatch' => 'Дата должна быть в формате дд.мм.гггг'))),
            ),
        ));

        // Адрес регистрации
        $this->addElement('text', 'reg_street', array(
            'label' => 'Улица, дом, квартира',
            'class' => 'form-control',
            'required' => false,
            'placeholder' => 'ул. Ленина, д. 10, кв. 5',
            'filters' => array('StringTrim', 'StripTags'),
        ));
        $this->addElement('text', 'reg_city', array(
            'label' => 'Населённый пункт',
            'class' => 'form-control',
            'required' => false,
            'placeholder' => 'г. Москва',
            'filters' => array('StringTrim', 'StripTags'),
        ));
        $this->addElement('text', 'reg_zip', array(
            'label' => 'Почтовый индекс',
            'class' => 'form-control',
            'required' => false,
            'maxlength' => 6,
            'placeholder' => '000000',
            'data-mask' => '000000',
            'filters' => array('StringTrim', 'StripTags'),
            'validators' => array(
                array('Regex', true, array('pattern' => '/^\d{6}$/', 'messages' => array('regexNotMatch' => 'Индекс должен содержать 6 цифр'))),
            ),
        ));

        // Контакты
        $this->addElement('text', 'phone', array(
            'label' => 'Номер телефона',
            'class' => 'form-control',
            'required' => true,
            'placeholder' => '+7 999 999 99 99',
            'data-mask' => '+7 000 000 00 00',
            'filters' => array('StringTrim', 'StripTags'),
            'validators' => array(
                array('NotEmpty', true, array('messages' => array('isEmpty' => 'Укажите номер телефона'))),
                array('Regex', true, array('pattern' => '/^\+7\s\d{3}\s\d{3}\s\d{2}\s\d{2}$/', 'messages' => array('regexNotMatch' => 'Формат: +7 999 999 99 99'))),
            ),
        ));
        $this->addElement('text', 'email', array(
            'label' => 'Email',
            'class' => 'form-control',
            'required' => false,
            'placeholder' => 'email@example.com',
            'filters' => array('StringTrim', 'StripTags'),
            'validators' => array('EmailAddress'),
        ));

        // Кнопка
        $this->addElement('button', 'send', array(
            'label' => 'Сохранить изменения',
            'class' => 'btn btn-primary btn-submit',
            'type' => 'submit',
        ));

        // Decorators with row layout metadata
        $fieldLayout = array(
            'passport_serial_number' => array('row' => false, 'class' => 'field-passport'),
            'passport_issued_by'     => array('row' => false, 'class' => ''),
            'passport_date'          => array('row' => 'date-code-row', 'class' => 'field-short'),
            'passport_code'          => array('row' => 'date-code-row', 'class' => 'field-short'),
            'birthday'               => array('row' => false, 'class' => 'field-short'),
            'reg_street'             => array('row' => false, 'class' => ''),
            'reg_city'               => array('row' => 'city-zip-row', 'class' => 'field-city'),
            'reg_zip'                => array('row' => 'city-zip-row', 'class' => 'field-zip'),
            'phone'                  => array('row' => 'phone-email-row', 'class' => 'field-medium'),
            'email'                  => array('row' => 'phone-email-row', 'class' => ''),
        );

        foreach ($this->getElements() as $element) {
            $name = $element->getName();
            if ($name === 'send') {
                $element->setDecorators(array(
                    'ViewHelper',
                    array('HtmlTag', array('tag' => 'div', 'class' => 'form-group mt-4')),
                ));
                continue;
            }
            $cfg = isset($fieldLayout[$name]) ? $fieldLayout[$name] : array('row' => false, 'class' => '');
            $wrapClass = 'form-group' . ($cfg['class'] ? ' ' . $cfg['class'] : '');
            $element->setDecorators(array(
                'ViewHelper', 'Errors', 'Label',
                array('HtmlTag', array('tag' => 'div', 'class' => $wrapClass)),
            ));
        }

        $this->setDecorators(array('FormElements', array('HtmlTag', array('tag' => 'div')), 'Form'));
    }

    // Override render to wrap multi-field rows in div.form-row
    public function render(Zend_View_Interface $view = null)
    {
        $fieldLayout = array(
            'passport_serial_number' => array('row' => false, 'class' => 'field-passport'),
            'passport_issued_by'     => array('row' => false, 'class' => ''),
            'passport_date'          => array('row' => 'date-code-row', 'class' => 'field-short'),
            'passport_code'          => array('row' => 'date-code-row', 'class' => 'field-short'),
            'birthday'               => array('row' => false, 'class' => 'field-short'),
            'reg_street'             => array('row' => false, 'class' => ''),
            'reg_city'               => array('row' => 'city-zip-row', 'class' => 'field-city'),
            'reg_zip'                => array('row' => 'city-zip-row', 'class' => 'field-zip'),
            'phone'                  => array('row' => 'phone-email-row', 'class' => 'field-medium'),
            'email'                  => array('row' => 'phone-email-row', 'class' => ''),
        );
        $rows = array();
        foreach ($fieldLayout as $name => $cfg) {
            $rowKey = $cfg['row'] === false ? $name . '_row' : $cfg['row'];
            $rows[$rowKey][] = $name;
        }
        $html = '';
        foreach ($rows as $rowId => $names) {
            if (count($names) === 1) {
                $html .= $this->getElement($names[0])->render();
            } else {
                $html .= '<div class="form-row" id="' . $rowId . '">';
                foreach ($names as $name) $html .= $this->getElement($name)->render();
                $html .= '</div>';
            }
        }
        $html .= $this->getElement('send')->render();
        return $html;
    }
}
```

## Inline width fallback (when CSS is overridden)

Legacy cabinets often load global Bootstrap CSS or heavily cached stylesheets. Even if you add `.field-short` to the wrapper, the inner `<input class="form-control">` may still render at 100 % because:
- `.form-control { width: 100%; }` from Bootstrap has higher specificity or appears later.
- The production `passport.css` is stale in browser/CDN cache.
- Another stylesheet is loaded after yours.

**Robust solution:** set `style="width: ...;"` directly on the input element from the form class. Inline styles always win over external CSS (unless `!important` is used elsewhere).

Add this loop after defining all elements (and after setting decorators if you also want the class on the wrapper):

```php
$fieldWidths = array(
    'passport_serial_number' => '160px',
    'passport_date'          => '140px',
    'passport_code'          => '140px',
    'birthday'               => '140px',
    'reg_zip'                => '110px',
    'phone'                  => '180px',
    // full-width fields intentionally omitted
);
foreach ($this->getElements() as $element) {
    $name = $element->getName();
    if ($name === 'send' || empty($fieldWidths[$name])) continue;
    $currentStyle = $element->getAttrib('style');
    $element->setAttrib('style', trim($currentStyle . ' width: ' . $fieldWidths[$name] . ';'));
}
```

Then the rendered `<input>` will look like:

```html
<input name="passport_date" class="form-control field-short" style="width: 140px;" ...>
```

Keep the CSS too — it is the graceful enhancement; inline style is the failsafe.

### Debugging checklist if widths still wrong

1. Confirm the file is uploaded to the production server (`git pull` does NOT trigger VS Code SFTP extension; sync manually).
2. Hard-refresh the page or add cache-buster to the CSS link (`/assets/css/passport.css?v=2`).
3. Open DevTools → Elements and check computed `width` and which stylesheet wins.
4. If `.form-control` from Bootstrap has `width: 100%`, inline `style="width: ..."` on the input will override it.

## Controller action essentials

- Parse existing `$userInfo['passport']` with regex.
- Parse `passport_registration_address` into `reg_zip`, `reg_city`, `reg_street`.
- On POST: strip non-digits from `passport_serial_number`, split first 4 chars as series, next 6 as number.
- Assemble new address string: `$zip . ', ' . $city . ', ' . $street`.
- Save via `rpcf_edit_user_new` (admin API), always GET full profile first to avoid overwriting other fields.
- Merge additional params with new values on the LEFT side: `$addParams + $fullUserInfo['additional_params']`.

## CSS key classes

- `.passport-form .form-row` — flex row for paired fields.
- `.field-passport` (160 px) / `.field-short` (140 px) / `.field-medium` (180 px) / `.field-zip` (110 px) / `.field-city` (flex).
- Mobile breakpoint collapses rows to block layout.

## JS key masks

- Серия/номер: `0000 000000`
- Даты: `00.00.0000`
- Код подразделения: `000-000`
- Индекс: `000000`
- Телефон: `+7 000 000 00 00`

## Pitfalls learned

- `+` operator on arrays: `$new + $existing` keeps LEFT values. Make sure NEW params are on the left.
- Different cache keys for the same additional params will cause stale alerts. Keep keys consistent across index and passport actions.
- `rpcf_user5_edit_user` does NOT save additional params or email — use `rpcf_edit_user_new`.
- Do not put UTM5 credentials or API dump files in skills/memory.
- **CSS classes on wrapper `<div>` may not affect input width in Bootstrap-based templates. Set inline `style` on inputs as a failsafe.**
