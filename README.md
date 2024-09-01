# Test Addon
Небольшой тестовый аддон, проверяющий материалы и шейдерные нод-группы на наличие неподключенных нод. Для всех неподключенных нод создаётся нода Attribute с соответствующим именем и типом на каждый сокет без инпута, после чего они смещаются в удалённое место и привязываются к блоку Frame.
Поиск осуществляется от активной ноды Material Output или Group Output для нод-групп. 

## Как установить
1) Скачать архив с аддоном с Github по [ссылке](https://github.com/Wotava/TestAddon/archive/refs/heads/master.zip) или кнопке Code -> Download ZIP
2) Запустить Blender
3) В меню Edit выбрать пункт Preferences
4) Выбрать категорию Add-ons в столбце слева
5) В правом верхнем углу выбрать Install
6) Указать путь к .zip архиву с аддоном и нажать Install Add-on

## Как использовать
![image](https://github.com/user-attachments/assets/a743b64e-a132-4990-a9b9-704a46dcf540)
Blender необходимо запускать из командной строки, в которую будет выводиться информация о найденных проблемных нодах.
На экране View 3D необходимо открыть N-панель нажатием клавиши N, затем выбрать вкладку TEST и нажать кнопку Test Scene Nodes. После нажатия на клавишу в командной строке будет отображаться информация о работе оператора и найденных проблемах.

## Пример данных
Входные данные:

![image](https://github.com/user-attachments/assets/47eb1e51-0acd-4c59-b215-31d6389d6cc7)

Выходные данные:

![image](https://github.com/user-attachments/assets/a9ede5ba-c93b-400c-bc24-5fabdce41516)

```
"Material": Vector Math.001 (type: VECT_MATH)
"Material": Material Output (type: OUTPUT_MATERIAL)
"Material": Vector Math (type: VECT_MATH)
"Material": Gamma.001 (type: GAMMA)
"Material": Gamma (type: GAMMA)
No disconnected Node Groups
No disconnected shader nodes in Node Groups
```
