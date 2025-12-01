топик: appletv
приложения: appletv/apps
appletv/availability
appletv/state

для упровления используется appletv/set.
возможные команды:

  Навигация

  {"action": "up"}
  {"action": "down"}
  {"action": "left"}
  {"action": "right"}
  {"action": "select"}
  {"action": "menu"}
  {"action": "home"}

  Медиа

  {"action": "play"}
  {"action": "pause"}
  {"action": "play_pause"}
  {"action": "stop"}
  {"action": "next"}
  {"action": "previous"}

  Питание

  {"action": "turn_on"}
  {"action": "turn_off"}

  Запуск приложений

  {"action": "launch_app", "app_id": "com.netflix.Netflix"}
  {"action": "launch_app", "app_id": "com.google.ios.youtube"}
  {"action": "launch_app", "app_id": "ru.kinopoisk"}
  {"action": "launch_app", "app_id": "org.jellyfin.swiftfin"}
  {"action": "launch_app", "app_id": "com.plexapp.plex"}

  Воспроизведение URL

  {"action": "play_url", "url": "https://example.com/video.mp4"}

  Множественные команды (макрос)

  {"action": "multi", "commands": ["up", "up", "select"]}

  Принудительное обновление (топик appletv/get)

  {"type": "state"}
  {"type": "apps"}
  {"type": "all"}

  Все app_id можно взять из appletv/apps — там полный список приложений.
