# Martin 3D Character

Отдельный проект настоящей 3D-модели Мартина. Не изменяет Martin-AI-Host.

**Статус: процедурный прототип. Не финальная модель и не сходство 1:1.**

## Состав

Геометрия кота, одежды, наушников и микрофона. Серо-полосатый окрас через
запечённую текстуру 1024×1024. Скелет с простыми жёсткими весами и клипы Idle, Talk, Wave, DJ.

Сборка создаёт BLEND, GLB, настоящий рендер сцены, рендер повторно импортированного GLB
и машинный отчёт о структуре экспортированного файла.

## Скачать результат

Actions → Build and validate Martin prototype → успешный запуск → Artifacts → martin-3d-prototype.
Артефакт появляется только после успешной сборки, хранится 30 дней и может требовать входа в GitHub.
Внутри: martin-prototype.blend, martin-prototype.glb, source-render.png,
exported-glb-render.png и martin-prototype.report.json.

## Локальная сборка

Нужен Blender с glTF exporter и Python 3. В Actions используется пакет Ubuntu 24.04.

```sh
blender --background --factory-startup --python-exit-code 1 --python scripts/build_character.py
python3 scripts/validate_glb.py build/martin-prototype.glb
blender --background --factory-startup --python-exit-code 1 --python scripts/verify_export.py
```

Без API-ключей, платных моделей или облачной генерации. Обычный GitHub-hosted runner,
без платных larger runners.

## Ограничения

Лицо и силуэт пока приближённые. Геометрическая шерсть убрана: выбран облегчённый мультяшный стиль.
Нет моргания и фонемных morph targets. Talk двигает челюсть, но не синхронизирован с голосом.
Веса частей жёсткие; это не финальный deformation rig. Модель не проверена на Android.
Структурная проверка не является полным Khronos glTF Validator.

Сравнивать с референсом нужно настоящие рендеры из build, а не иллюстрации.
План приёмки: [ART_DIRECTION.md](docs/ART_DIRECTION.md).
Личные фотографии в публичный репозиторий не загружаются.

Основа экспорта: [официальное руководство Blender glTF](https://docs.blender.org/manual/en/latest/addons/scene_gltf2.html).

Мобильные лимиты сборки: до 40 000 треугольников, 16 мешей и 8 МиБ GLB. Проверяется сборкой; это не гарантия FPS.
