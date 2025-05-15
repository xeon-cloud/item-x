# ITEM-X - площадка для продажи и покупки цифровых товаров и услуг пользователями

*Основной функционал*:
- Авторизация через Яндекс ID
- Покупка и продажа товаров
- Поиск по ключевым словам
- Фильтр товаров по цене и дате
- Система уведомлений
- Удобный мессенджер

***
#### У каждого юзера есть свой кабинет

*Возможности*:
- Пополнение денежных средств
- Вывод денежный средств
- Просмотр истории покупок
- Управление своими товарами
- Генерация ключа для доступа к API

***

## Документация к API

*В заголовке запроса необходимо указать параметр авторизации*
```Authorization: Bearer {ваш токен)```

### Получение информации о себе - ```/api/users/me``` ```[GET]```
Пример ответа сервера:
```
{
  "success": True,
  "data": {
    "id": 1,
    "username":
    "Xeonvsd",
    "wallet": {
      "total": 0,
      "hold": 0
    }
  }
}
```

### Загрузка товара - ```/api/items/create``` ```[POST]```
Тело запроса JSON (пример)
```
{
    'name': '<name>',
    'about': '<about>',
    'amount': 100,
    'content': '<some content>',
    'categoryName': 'services',
    'subCategoryId': 1,
    'image': '<image in base64>',
    'contentFile': '<file in base64> (no required)',
    'extension': 'ex. txt (only with contentFile)'
}
```
Пример ответа сервера:
```
{
  'success': True,
  'message': 'Item created',
  'data': {
      'id': 1,
      'url': '/category/services/1/1'
}
```

### Редактирование товара - ```/api/items/update/<item_id>``` ```[POST, PUT]```
Тело запроса JSON (пример) - передаем желаемые параметры для едита
```
{
    'name': '<name>',
    'about': '<about>',
    'amount': 100,
    'content': '<some content>',
    'categoryName': 'services',
    'subCategoryId': 1,
    'image': '<image in base64>',
    'contentFile': '<file in base64> (no required)',
    'extension': 'ex. txt (only with contentFile)'
}
```
Пример ответа сервера:
```
{
  'success': True,
  'message': 'Item updated'
}
```

### Удаление товара - ```/api/items/delete/<item_id>``` ```[POST, DELETE]```
Пример ответа сервера:
```
{
  'success': True,
  'message': 'Item deleted'
}
```
