# CakePHP CRM Controllers Audit Reference

Quick-reference for common CakePHP 2.x CRM controller patterns found in ISP/billing systems.

## Auth checks in beforeFilter()

```php
// Full restriction — only admins (limited_privileges = 0)
if ($this->Session->read('Auth.User.Group.limited_privileges') != 0) {
  throw new UnauthorizedException('Доступ запрещен');
}

// Partial restriction — excludes limited_privileges = 1
if ($this->Session->read('Auth.User.Group.limited_privileges') == 1) {
  throw new UnauthorizedException('Доступ запрещен');
}
```

## JSON response pattern

```php
public function beforeRender() {
  parent::beforeRender();
  if ($this->request->is('ajax')) {
    if (!empty($this->result)) {
      $this->viewClass = 'Json';
      foreach ($this->result as $key => $value):
        $this->set($key, $value);
        $serialize[] = $key;
      endforeach;
      $this->set('_serialize', $serialize);
    }
  }
}
```

## Paginator pattern

```php
public $paginate = array(
  'contain' => false,
  'fields' => array('Model.id', 'Model.name'),
  'conditions' => array('Model.deleted' => NULL),
  'order' => array('Model.id' => 'asc'),
  'limit' => 25
);
```

## Search session persistence

```php
// POST saves to session
if ($this->request->is('post')) {
  $this->Session->write($this->modelClass, $this->request->data);
}
// GET restores from session
if ($this->Session->check($this->modelClass . '.Search')) {
  $this->request->data = $this->Session->read($this->modelClass);
}
```

## Key controller categories

| Category | Controllers | Data source |
|----------|-------------|-------------|
| Auth/users | Users, Groups | CRM DB |
| Customers | Customers, Ajax (getCustomerDetails) | UTM5 DB |
| Orders | Orders, RepairOrders, ScheduleOrders | CRM DB |
| Equipment | AccessSwitches, SwitchPorts, SwitchHouseLinks, Wireless, WirelessPorts | CRM DB |
| Billing refs | Tariffs, TariffDetails, Accounting | UTM5 DB |
| Network | Ipv4Nets, Hives, Houses | UTM5 + CRM |
| Settings | Settings, ConstantsComponent | CRM DB |
