# Как выпустить релиз на GitHub с EXE (Python 3.8)

## Вариант A — локально на Windows

1. Установите Python 3.8.x.
2. (Опционально) Установите Inno Setup 6 для setup-файла.
3. В корне проекта запустите:

```bat
build\build_windows_release.bat
```

4. Готовые файлы появятся в папке `release`:
   - `PictureConverter\PictureConverter.exe` (портативный)
   - `PictureConverter-Setup.exe` (если установлен Inno Setup)

5. На GitHub создайте Release и загрузите эти файлы как Assets.

## Вариант B — через GitHub Actions

1. Запушьте код в GitHub.
2. Создайте тег:

```bash
git tag v1.0.0
git push origin v1.0.0
```

3. Workflow `.github/workflows/release.yml` автоматически соберёт `PictureConverter-portable.zip` и прикрепит к релизу.

## Важно для Windows 7

Если нужна максимальная совместимость с Windows 7, лучше собирать EXE на Windows 7 (или в Win7 VM) с Python 3.8.

## Вариант C — вообще без git и терминала (через кнопку)

1. Откройте вкладку **Actions** в GitHub.
2. Выберите workflow **Build and Release Windows App**.
3. Нажмите **Run workflow**.
4. Введите версию, например `1.0.1`.
5. Workflow сам создаст тег `v1.0.1`, соберёт приложение и опубликует Release с `PictureConverter-portable.zip`.
