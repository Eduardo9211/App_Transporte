const CACHE_NAME = 'transporte-v2';
const urlsToCache = [
  './',
  './index.html',
  './manifest.json'
];

// Instalación del Service Worker y almacenamiento de archivos base
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      // Usamos addAll solo con los archivos locales seguros
      return cache.addAll(urlsToCache);
    }).then(() => self.skipWaiting())
  );
});

// Activación y limpieza de cachés antiguas
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Interceptación de peticiones para funcionamiento offline y con CDNs externos
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      // Si está en caché, lo devuelve; si no, lo busca en la red y opcionalmente lo cachea
      return response || fetch(event.request).then(fetchResponse => {
        // Opcional: si la petición es externa (CDNs), podemos dejar que pase directo por la red
        return fetchResponse;
      }).catch(() => {
        // Fallback en caso de que no haya red ni caché (opcionalmente podrías retornar una vista offline)
        if (event.request.mode === 'navigate') {
          return caches.match('./index.html');
        }
      });
    })
  );
});